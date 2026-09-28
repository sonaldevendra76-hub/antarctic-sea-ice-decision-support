from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.routers import health, bathymetry, icebergs, route
from app.routers import forecast as forecast_router
from app.routers import vessel as vessel_router
from app.routers.ws_alerts import alerts_router
from app.config.settings import settings
from app.services.data_adapters.sea_ice_adapter import SeaIceDataAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Antarctic Sea-Ice Decision Support System")
    
    # Log active data mode
    logger.info("=" * 60)
    logger.info(f"DATA MODE: {settings.DATA_MODE.upper()}")
    if settings.DATA_MODE == "real":
        logger.info(f"Sea-ice source: {SeaIceDataAdapter.DATASET_ID}")
        logger.info(f"DOI: {SeaIceDataAdapter.DOI}")
    else:
        logger.info("Sea-ice source: Demo synthetic data")
    logger.info("=" * 60)
    
    yield
    logger.info("Shutting down Antarctic Sea-Ice Decision Support System")


app = FastAPI(
    title="Antarctic Sea-Ice Decision Support System",
    description="Maritime route decision support for Antarctic waters",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(forecast_router.router, prefix="/api", tags=["forecast"])
app.include_router(vessel_router.router, prefix="/api", tags=["vessel"])
app.include_router(bathymetry.router, prefix="/api", tags=["bathymetry"])
app.include_router(icebergs.router, prefix="/api", tags=["icebergs"])
app.include_router(route.router, prefix="/api", tags=["route"])
app.include_router(alerts_router, prefix="/api", tags=["alerts"])


@app.get("/")
async def root():
    return {
        "message": "Antarctic Sea-Ice Decision Support System API",
        "version": "0.1.0",
        "docs": "/docs"
    }
