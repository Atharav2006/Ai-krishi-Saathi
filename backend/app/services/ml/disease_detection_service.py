import logging
import threading
import time
import json
from pathlib import Path
from io import BytesIO
import hashlib

import numpy as np
from PIL import Image
from fastapi import UploadFile

from app.schemas.ml import DiseaseDetectionResponse
from app.core.config import settings
from app.services.monitoring.prediction_writer import log_prediction_async
from app.db.session import SessionLocal

logger = logging.getLogger("krishi_saathi.ml.disease_detection")

MODEL_DIR = Path(__file__).parents[4] / "ml_pipeline" / "models"
IMG_SIZE = (224, 224)

# Advisory texts per disease — extending with PlantVillage dataset classes
ADVISORY_TEXTS = {
    "Tomato___healthy": "Crop appears healthy. Continue current irrigation and nutrient regimen.",
    "Tomato___Bacterial_spot": "Bacterial Spot detected. Apply copper-based bactericides early. Avoid overhead watering.",
    "Tomato___Early_blight": "Early Blight detected. Remove infected lower leaves. Spray Mancozeb or Chlorothalonil.",
    "Tomato___Late_blight": "Late Blight detected. Apply Mancozeb (75% WP) @ 2.5 g/L or Copper Oxychloride early morning. Remove infected leaves.",
    "Tomato___Leaf_Mold": "Leaf Mold detected. Improve air circulation. Apply fungicides like Chlorothalonil.",
    "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot detected. Remove infected leaves. Use fungicidal sprays.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spider mites detected. Spray Neem oil or Miticides like Abamectin. Increase humidity.",
    "Tomato___Target_Spot": "Target Spot detected. Ensure good ventilation. Apply appropriate fungicides.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Leaf Curl Virus detected. Control whitefly vectors using sticky traps or Imidacloprid.",
    "Tomato___Tomato_mosaic_virus": "Mosaic Virus detected. Remove infected plants immediately. Sanitize tools to prevent spread.",
    "Squash___Powdery_mildew": "Powdery Mildew detected. Improve airflow; apply Sulphur 80% WP @ 3g/L. Avoid overhead irrigation."
}


class DiseaseDetectionService:
    """
    Thread-safe singleton loading TFLite or ONNX disease detection model.
    Gracefully degrades to a deterministic fallback if model files are absent.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._tflite_interpreter = None
                cls._instance._ort_session = None
                cls._instance._class_map: dict = {}
                cls._instance._model_version = "none"
                cls._instance._initialized = False
        return cls._instance

    def _load_model(self):
        with self._lock:
            if self._initialized:
                return

            tflite_path = MODEL_DIR / "disease_model_v2.tflite"
            onnx_path = MODEL_DIR / "disease_model.onnx"
            class_map_path = MODEL_DIR / "disease_class_map.json"

            # Load class map
            if class_map_path.exists():
                with open(class_map_path) as f:
                    self._class_map = json.load(f)
            else:
                self._class_map = {str(i): k for i, k in enumerate(ADVISORY_TEXTS.keys())}
                logger.warning("No class map found. Using built-in advisory classes.")

            if tflite_path.exists():
                try:
                    import tensorflow as tf
                    self._tflite_interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
                    self._tflite_interpreter.allocate_tensors()
                    self._model_version = settings.MODEL_VERSION_TAG
                    logger.info(f"Loaded TFLite disease model (version: {self._model_version})")
                except Exception as e:
                    logger.error(f"TFLite load failed: {e}. Trying ONNX.")

            if self._tflite_interpreter is None and onnx_path.exists():
                try:
                    import onnxruntime as ort
                    self._ort_session = ort.InferenceSession(str(onnx_path))
                    self._model_version = settings.MODEL_VERSION_TAG
                    logger.info(f"Loaded ONNX disease model (version: {self._model_version})")
                except Exception as e:
                    logger.error(f"ONNX disease load failed: {e}. Using fallback.")

            if self._tflite_interpreter is None and self._ort_session is None:
                logger.warning("No trained disease model found. Run ml_pipeline/src/train_cnn.py first. Using fallback.")

            self._initialized = True

    def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Resize and normalize image into model input format."""
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image = image.resize(IMG_SIZE, Image.LANCZOS)
        arr = np.array(image, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)  # (1, 224, 224, 3)

    def _run_tflite(self, input_data: np.ndarray) -> np.ndarray:
        input_details = self._tflite_interpreter.get_input_details()
        output_details = self._tflite_interpreter.get_output_details()
        self._tflite_interpreter.set_tensor(input_details[0]['index'], input_data)
        self._tflite_interpreter.invoke()
        return self._tflite_interpreter.get_tensor(output_details[0]['index'])[0]

    def _run_onnx(self, input_data: np.ndarray) -> np.ndarray:
        input_name = self._ort_session.get_inputs()[0].name
        return self._ort_session.run(None, {input_name: input_data})[0][0]

    async def predict_from_image(self, file: UploadFile) -> DiseaseDetectionResponse:
        if not self._initialized:
            self._load_model()

        start = time.time()
        image_bytes = await file.read()
        input_data = self._preprocess_image(image_bytes)

        probs: np.ndarray

        if self._tflite_interpreter is not None:
            probs = self._run_tflite(input_data)
        elif self._ort_session is not None:
            probs = self._run_onnx(input_data)
        else:
            # Deterministic fallback
            disease_class = "Healthy"
            confidence = 0.35
            advisory = ADVISORY_TEXTS.get(disease_class, "Please consult your local Krishi Kendram.")
            latency_ms = round((time.time() - start) * 1000, 2)
            logger.info(
                f"Disease fallback | class={disease_class} | confidence={confidence:.3f} "
                f"| model_version={self._model_version} | latency={latency_ms}ms"
            )
            log_prediction_async(
                session_factory=SessionLocal,
                user_id=None,
                model_type="disease_detection",
                model_version=self._model_version,
                input_payload={"image_size": len(image_bytes), "content_type": file.content_type},
                predicted_value=disease_class,
                confidence_score=confidence,
                latency_ms=latency_ms,
            )
            return DiseaseDetectionResponse(
                disease_class=disease_class,
                confidence=confidence,
                advisory_text=advisory,
                model_version=self._model_version,
            )

        class_idx = int(np.argmax(probs))
        confidence = float(round(probs[class_idx], 4))
        raw_disease_class = self._class_map.get(str(class_idx), "Unknown")
        
        # MLOps: Reject low-confidence predictions (out-of-distribution images)
        if confidence < 0.35:
            disease_class = "Unrecognized Leaf"
            advisory = "The AI is unsure (Low Confidence). Please ensure the image is a clear, close-up photo of a supported crop leaf (Tomato, Corn, Potato, Apple, etc.)."
        else:
            # Format the raw dataset name (e.g. "Tomato___healthy" -> "Tomato - healthy")
            disease_class = raw_disease_class.replace("___", " - ").replace("_", " ")
            advisory = ADVISORY_TEXTS.get(raw_disease_class, "Consult your local Krishi Kendram for treatment advice.")


        latency_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            f"Disease inference | class={disease_class} | confidence={confidence:.3f} "
            f"| model_version={self._model_version} | latency={latency_ms}ms"
        )

        log_prediction_async(
            session_factory=SessionLocal,
            user_id=None,
            model_type="disease_detection",
            model_version=self._model_version,
            input_payload={"image_size": len(image_bytes), "content_type": file.content_type},
            predicted_value=disease_class,
            confidence_score=confidence,
            latency_ms=latency_ms,
        )

        return DiseaseDetectionResponse(
            disease_class=disease_class,
            confidence=confidence,
            advisory_text=advisory,
            model_version=self._model_version,
        )


disease_detection_service = DiseaseDetectionService()
