"""
api/v1/metrics_history.py
--------------------------
Detailed rolling metrics history for Recharts line charts.
"""
from typing import List, Any
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.monitoring import ModelMetric, ModelType

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.metrics")


class MetricPoint(BaseModel):
    window_end: datetime
    metric_value: float


class MetricSeriesResponse(BaseModel):
    metric_name: str
    data_points: List[MetricPoint]


@router.get(
    "/{model_type}/rolling",
    response_model=List[MetricSeriesResponse],
    summary="Get rolling metrics timeseries for charts (Admin Only)",
)
def get_rolling_metrics(
    model_type: str,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    # Requires standard valid user token
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(ModelMetric)
        .filter(
            ModelMetric.model_type == ModelType(model_type),
            ModelMetric.window_end >= cutoff,
        )
        .order_by(ModelMetric.window_end.asc())
        .all()
    )

    # Group by metric_name
    grouped: dict[str, List[MetricPoint]] = {}
    for r in rows:
        if r.metric_name not in grouped:
            grouped[r.metric_name] = []
        grouped[r.metric_name].append(
            MetricPoint(window_end=r.window_end, metric_value=r.metric_value)
        )

    # Format for easy Recharts consumption
    return [
        MetricSeriesResponse(metric_name=name, data_points=points)
        for name, points in grouped.items()
    ]
