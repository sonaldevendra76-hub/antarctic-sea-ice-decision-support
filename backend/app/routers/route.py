from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.routing_service import RoutingService
from app.services.forecast_service import ForecastService
from app.services.iceberg_service import IcebergService
from app.models import Coordinates, VesselCapabilities, RouteObjectives

router = APIRouter()
routing_service = RoutingService()
forecast_service = ForecastService()
iceberg_service = IcebergService()


class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates
    vessel_config: VesselCapabilities
    objectives: RouteObjectives
    forecast_timestep: int = 0


@router.post("/route")
async def calculate_route(request: RouteRequest):
    """
    Calculate optimal route using A* pathfinding algorithm with risk-aware cost function.
    Incorporates sea-ice risk and iceberg trajectory risk.
    """
    # Get forecast data for the route calculation
    forecast_data = forecast_service.get_forecast(
        timestep=request.forecast_timestep,
        bounds=None
    )
    
    # Get iceberg data with trajectory predictions
    iceberg_data = iceberg_service.get_icebergs()
    
    return routing_service.calculate_route(
        start=request.start,
        end=request.end,
        vessel_config=request.vessel_config,
        objectives=request.objectives,
        forecast_timestep=request.forecast_timestep,
        forecast_data=forecast_data,
        iceberg_data=iceberg_data
    )
