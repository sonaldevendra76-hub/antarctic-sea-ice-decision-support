from fastapi import APIRouter, Query
from typing import Optional

from app.services.iceberg_service import IcebergService

router = APIRouter()
iceberg_service = IcebergService()


@router.get("/icebergs")
async def get_icebergs(
    bounds: Optional[str] = Query(None, description="bbox format: min_lon,min_lat,max_lon,max_lat"),
    min_size: float = Query(0, ge=0, description="Minimum iceberg size in meters")
):
    """
    Retrieve detected iceberg positions and characteristics.
    Currently uses deterministic seeded demo data.
    """
    return iceberg_service.get_icebergs(bounds=bounds, min_size=min_size)
