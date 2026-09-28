import numpy as np
from typing import Optional
from datetime import datetime, timedelta
from .data_adapters.sea_ice_adapter import SeaIceDataAdapter
from ..config.settings import settings


class ForecastService:
    """
    Service for sea-ice forecast data.
    Supports both real data (NOAA/NSIDC) and demo fallback mode.
    """
    
    def __init__(self):
        self.base_bounds = {
            "min_lon": -180.0,
            "min_lat": -90.0,
            "max_lon": 180.0,
            "max_lat": -60.0
        }
        self.resolution = 0.5
        np.random.seed(42)  # Deterministic seed for demo data
        
        # Initialize adapter based on settings
        self.adapter = SeaIceDataAdapter(mode=settings.DATA_MODE)
    
    def get_forecast(self, timestep: int = 0, bounds: Optional[str] = None):
        """
        Get forecast data from appropriate source (real or demo).
        """
        return self.adapter.get_forecast(timestep=timestep, bounds=bounds)
