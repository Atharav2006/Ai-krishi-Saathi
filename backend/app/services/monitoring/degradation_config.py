"""
services/monitoring/degradation_config.py
------------------------------------------
Configurable threshold constants for automatic performance degradation detection.

Each entry maps:  (model_type, metric_name) → (threshold_value, comparison_direction)

comparison_direction:
  "above"  → degraded when metric_value > threshold  (e.g. error metrics: MAE, RMSE, MAPE)
  "below"  → degraded when metric_value < threshold  (e.g. quality metrics: Accuracy, F1)
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DegradationThreshold:
    model_type: str
    metric_name: str
    threshold: float
    direction: Literal["above", "below"]  # 'above' = bad when high, 'below' = bad when low

    def is_breached(self, metric_value: float) -> bool:
        if self.direction == "above":
            return metric_value > self.threshold
        return metric_value < self.threshold


# ─── Price Forecast Thresholds ────────────────────────────────────────────────
# MAPE > 18% signals the model is materially mispricing mandi rates
PRICE_THRESHOLDS: list[DegradationThreshold] = [
    DegradationThreshold("price_forecast", "MAPE", threshold=18.0, direction="above"),
    DegradationThreshold("price_forecast", "MAE",  threshold=500.0, direction="above"),  # ₹500 MAE limit
]

# ─── Disease Detection Thresholds ────────────────────────────────────────────
# Accuracy < 75% or weighted F1 < 70% risks missed/wrong disease diagnoses
DISEASE_THRESHOLDS: list[DegradationThreshold] = [
    DegradationThreshold("disease_detection", "Accuracy", threshold=0.75, direction="below"),
    DegradationThreshold("disease_detection", "F1",       threshold=0.70, direction="below"),
]

# ─── Combined Lookup ──────────────────────────────────────────────────────────
ALL_THRESHOLDS: dict[tuple[str, str], DegradationThreshold] = {
    (t.model_type, t.metric_name): t
    for t in PRICE_THRESHOLDS + DISEASE_THRESHOLDS
}


def get_threshold(model_type: str, metric_name: str) -> DegradationThreshold | None:
    """Return the threshold config for a given (model_type, metric_name) pair, or None."""
    return ALL_THRESHOLDS.get((model_type, metric_name))
