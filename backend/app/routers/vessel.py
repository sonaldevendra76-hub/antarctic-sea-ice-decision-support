from fastapi import APIRouter
from app.services.vessel_service import VesselService

router = APIRouter()
vessel_service = VesselService()


@router.get("/vessel")
async def get_vessel():
    """
    Retrieve vessel configuration and capabilities.
    """
    return vessel_service.get_vessel_data()
