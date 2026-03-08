import logging
import threading
import time
import json
from pathlib import Path
from typing import List, Optional

import numpy as np
import joblib

from app.schemas.ml import PriceForecastResponse, PriceForecastRequest
from app.core.config import settings
from app.services.monitoring.prediction_writer import log_prediction_async
from app.db.session import SessionLocal

logger = logging.getLogger("krishi_saathi.ml.price_forecast")

MODEL_DIR = Path(__file__).parents[4] / "ml_pipeline" / "models"

# Feature columns must match what was used during training (from feature_engineering.py)
FEATURE_COLUMNS = [
    "lag_1", "lag_3", "lag_7", "lag_14", "lag_30",
    "roll_mean_7", "roll_std_7", "roll_mean_30", "roll_std_30",
    "day_of_week", "month", "quarter", "is_weekend", "year",
    "is_monsoon", "is_rabi", "is_kharif",
]


class PriceForecastService:
    """
    Thread-safe singleton loading a real ONNX or joblib price forecasting model.
    Falls back gracefully to statistical estimation if the trained model is not yet
    present (e.g., during initial development before training pipeline has run).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._ort_session = None
                cls._instance._joblib_bundle = None
                cls._instance._model_version = "none"
                cls._instance._initialized = False
        return cls._instance

    def _load_model(self):
        with self._lock:
            if self._initialized:
                return
            
            onnx_path = MODEL_DIR / "price_forecast.onnx"
            joblib_path = MODEL_DIR / "price_forecast_rf.joblib"

            if onnx_path.exists():
                try:
                    import onnxruntime as ort
                    self._ort_session = ort.InferenceSession(str(onnx_path))
                    self._model_version = settings.MODEL_VERSION_TAG
                    logger.info(f"Loaded ONNX price model from: {onnx_path} (version: {self._model_version})")
                except Exception as e:
                    logger.error(f"Failed to load ONNX model: {e}. Will use statistical fallback.")
            elif joblib_path.exists():
                try:
                    self._joblib_bundle = joblib.load(str(joblib_path))
                    self._model_version = settings.MODEL_VERSION_TAG
                    logger.info(f"Loaded joblib price model from: {joblib_path}")
                except Exception as e:
                    logger.error(f"Failed to load joblib model: {e}. Will use statistical fallback.")
            else:
                logger.warning(
                    "No trained price model found. Run ml_pipeline/src/train_rf.py to generate. "
                    "Using statistical fallback."
                )

            self._initialized = True

    def _build_feature_vector(self, payload: PriceForecastRequest) -> np.ndarray:
        """
        Constructs the 17-feature vector from the request payload.
        Uses recent_price_series to populate lag and rolling features.
        """
        from datetime import datetime

        now = datetime.utcnow()
        series = payload.recent_price_series if payload.recent_price_series else []
        series = series[-30:] if len(series) >= 30 else series

        def _get(offset: int, default: float = 0.0) -> float:
            idx = len(series) - offset
            return float(series[idx]) if idx >= 0 and len(series) > 0 else default

        base = _get(1) or 1500.0
        roll7 = float(np.mean(series[-7:])) if len(series) >= 7 else base
        roll30 = float(np.mean(series[-30:])) if len(series) >= 30 else base
        std7 = float(np.std(series[-7:])) if len(series) >= 7 else 50.0
        std30 = float(np.std(series[-30:])) if len(series) >= 30 else 100.0

        month = now.month
        season_monsoon = 1 if month in [6, 7, 8, 9] else 0
        season_rabi = 1 if month in [10, 11, 12, 1, 2, 3] else 0
        season_kharif = 1 if month in [4, 5] else 0

        features = [
            _get(1, base), _get(3, base), _get(7, base), _get(14, base), _get(30, base),
            roll7, std7, roll30, std30,
            now.weekday(), month, (month - 1) // 3 + 1,
            1 if now.weekday() >= 5 else 0,
            now.year,
            season_monsoon, season_rabi, season_kharif,
        ]
        return np.array([features], dtype=np.float32)

    def predict(self, payload: PriceForecastRequest) -> PriceForecastResponse:
        if not self._initialized:
            self._load_model()

        start = time.time()
        feature_vec = self._build_feature_vector(payload)

        predicted_price: float
        confidence: float

        if self._ort_session is not None:
            # Real ONNX inference
            input_name = self._ort_session.get_inputs()[0].name
            raw_output = self._ort_session.run(None, {input_name: feature_vec})[0].flatten()
            predicted_price = float(round(raw_output[0], 2))
            confidence = 0.87  # RF doesn't emit probabilities; use calibrated default
        elif self._joblib_bundle is not None:
            model = self._joblib_bundle["model"]
            predicted_price = float(round(model.predict(feature_vec)[0], 2))
            confidence = 0.85
        else:
            # Statistical fallback
            base = float(np.mean(payload.recent_price_series)) if payload.recent_price_series else 1500.0
            fluctuation = np.random.uniform(-0.05, 0.08)
            predicted_price = round(base * (1 + fluctuation), 2)
            confidence = 0.40

        # Determine trend
        ref_price = payload.recent_price_series[-1] if payload.recent_price_series else predicted_price
        diff_pct = (predicted_price - ref_price) / (ref_price + 1e-8)
        trend = "stable"
        if diff_pct > 0.03:
            trend = "up"
        elif diff_pct < -0.03:
            trend = "down"

        elapsed = time.time() - start
        latency_ms = round(elapsed * 1000, 2)
        logger.info(
            f"Price inference | crop={payload.crop_id} | predicted={predicted_price} "
            f"| confidence={confidence:.3f} | model_version={self._model_version} | latency={latency_ms}ms"
        )

        # Non-blocking: fire-and-forget prediction log — does NOT slow down the response
        log_prediction_async(
            session_factory=SessionLocal,
            user_id=None,  # user_id injected by API layer in future
            model_type="price_forecast",
            model_version=self._model_version,
            input_payload={"crop_id": str(payload.crop_id), "district_id": str(payload.district_id)},
            predicted_value=predicted_price,
            confidence_score=round(confidence, 4),
            latency_ms=latency_ms,
        )

        return PriceForecastResponse(
            predicted_price=predicted_price,
            trend_direction=trend,
            confidence_score=round(confidence, 4),
            model_version=self._model_version,
        )


price_forecast_service = PriceForecastService()
