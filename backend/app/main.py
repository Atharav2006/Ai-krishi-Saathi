from contextlib import asynccontextmanager
from datetime import datetime
import time
import logging
import traceback

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.api.v1.forecasts import get_forecasts as get_forecasts_handler
from app.core.config import settings
from app.services.monitoring.scheduler import start_scheduler, shutdown_scheduler
from app.services.monitoring.registry_init import auto_register_models
from app.db.session import SessionLocal
from app.api import deps
from sqlalchemy.orm import Session

logger = logging.getLogger("krishi_saathi.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: start scheduler, auto-register models on boot, shut down on teardown."""
    logger.info("Starting AI Krishi Saathi API...")
    start_scheduler()
    _db = SessionLocal()
    try:
        auto_register_models(_db)
    except Exception as exc:
        logger.error(f"Model auto-registration failed (non-fatal): {exc}")
    finally:
        _db.close()
    yield
    shutdown_scheduler()
    logger.info("AI Krishi Saathi API shut down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Industry scale REST APIs for AI Krishi Saathi (Offline-first syncing, RBAC, ML Monitoring)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def fix_malformed_paths_middleware(request, call_next):
    # Fix for legacy/malformed paths
    path = request.url.path
    if path == f"{settings.API_V1_STR}forecasts" or path == "/forecasts":
        request.scope["path"] = f"{settings.API_V1_STR}/forecasts"
        logger.warning(f"Fixed malformed path: {path} -> {request.scope['path']}")
    elif path == "/auth/register":
        request.scope["path"] = f"{settings.API_V1_STR}/auth/register"
        logger.warning(f"Fixed malformed path: {path} -> {request.scope['path']}")
    elif path == "/auth/login/access-token":
        request.scope["path"] = f"{settings.API_V1_STR}/auth/login/access-token"
        logger.warning(f"Fixed malformed path: {path} -> {request.scope['path']}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for audio
import os
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get(f"{settings.API_V1_STR}forecasts", include_in_schema=False)
def forecasts_compat(
    district: str,
    crops: str,
    days: int = 7,
    db: Session = Depends(deps.get_db),
):
    """
    Backward-compatible endpoint for clients mistakenly calling `/api/v1forecasts`.
    Forwards the request to the canonical `/api/v1/forecasts` handler.
    """
    return get_forecasts_handler(district=district, crops=crops, days=days, db=db)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    with open("crash.log", "a") as f:
        f.write(f"\n--- {datetime.now()} ---\n")
        f.write(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "version": settings.VERSION}
