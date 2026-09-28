from fastapi import APIRouter, Query
from typing import Optional

from app.services.bathymetry_service import BathymetryService

router = APIRouter()
bathymetry_service = BathymetryService()


@router.get("/bathymetry/bounds")
async def get_bathymetry(
    min_lon: float = Query(..., ge=-180, le=180),
    min_lat: float = Query(..., ge=-90, le=90),
    max_lon: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),
    resolution: float = Query(0.1, gt=0, description="Grid resolution in degrees")
):
    """
    Retrieve bathymetry (seafloor depth) data for specified bounds.
    Currently uses demo grid data.
    """
    return bathymetry_service.get_bathymetry(
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        resolution=resolution
    )
