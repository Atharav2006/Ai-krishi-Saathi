from fastapi import APIRouter

from app.api.v1 import (
    auth, users, locations, agtech, ml, feedback, model_registry, forecasts,
    admin_summary, metrics_history, degradation_history, retraining_jobs,
    voice
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(locations.router, prefix="/locations", tags=["Locations / Geography"])
api_router.include_router(agtech.router, prefix="/agtech", tags=["Agriculture & Analytics"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning Inference"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["Price Forecasting"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Model Monitoring & Feedback"])
api_router.include_router(model_registry.router, prefix="/registry", tags=["Model Registry"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice Advisor"])

# Admin Dashboard Endpoints (Secured via auth dependencies checking role)
api_router.include_router(admin_summary.router, prefix="/admin", tags=["Admin Summary"])
api_router.include_router(metrics_history.router, prefix="/metrics", tags=["Metrics History"])
api_router.include_router(degradation_history.router, prefix="/degradation", tags=["Degradation History"])
api_router.include_router(retraining_jobs.router, prefix="/retraining", tags=["Retraining Jobs"])
