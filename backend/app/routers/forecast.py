from fastapi import APIRouter, Query
from typing import Optional
import numpy as np

from app.services.forecast_service import ForecastService

router = APIRouter()
forecast_service = ForecastService()


@router.get("/forecast")
async def get_forecast(
    timestep: int = Query(0, ge=0, description="Forecast timestep"),
    bounds: Optional[str] = Query(None, description="bbox format: min_lon,min_lat,max_lon,max_lat")
):
    """
    Retrieve sea-ice forecast data.
    Supports both real NOAA/NSIDC data and demo fallback.
    """
    return forecast_service.get_forecast(timestep=timestep, bounds=bounds)
