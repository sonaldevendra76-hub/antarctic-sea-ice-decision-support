import numpy as np
from typing import Optional, List, Dict
from datetime import datetime
import logging

from app.services.data_adapters.iceberg_adapter import IcebergAdapter
from app.config.settings import settings

logger = logging.getLogger(__name__)


class IcebergService:
    """
    Service for iceberg detection and tracking.
    
    Uses real USNIC (U.S. National Ice Center) data when available,
    with prototype drift-based trajectory prediction.
    Falls back to demo data if real data is unavailable.
    """
    
    def __init__(self):
        self.adapter = IcebergAdapter()
        np.random.seed(44)
    
    def get_icebergs(self, bounds: Optional[str] = None, min_size: float = 0):
        """
        Get iceberg data with trajectory predictions.
        
        Uses real USNIC data if available, otherwise falls back to demo data.
        """
        # Try to load real USNIC data
        real_icebergs = self.adapter.load_icebergs()
        
        if real_icebergs:
            return self._format_real_icebergs(real_icebergs, min_size)
        else:
            logger.warning("Falling back to demo iceberg data")
            return self._generate_demo_icebergs(min_size)
    
    def _format_real_icebergs(self, raw_icebergs: List[Dict], min_size: float) -> Dict:
        """
        Format real USNIC iceberg data with trajectory predictions.
        
        Args:
            raw_icebergs: Raw iceberg observations from adapter.
            min_size: Minimum size filter in nautical miles.
            
        Returns:
            Formatted iceberg response with trajectories.
        """
        icebergs = []
        
        for iceberg in raw_icebergs:
            # Filter by size
            if iceberg['length_nm'] < min_size:
                continue
            
            # Calculate trajectory prediction
            trajectory = self.adapter.calculate_trajectory(
                iceberg_id=iceberg['id'],
                current_position=iceberg['position'],
                historical_observations=None  # Would need historical data
            )
            
            # Convert dimensions to meters (1 NM = 1852 m)
            length_m = iceberg['length_nm'] * 1852
            width_m = iceberg['width_nm'] * 1852
            
            icebergs.append({
                "id": iceberg['id'],
                "position": iceberg['position'],
                "observed_at": iceberg['observed_at'],
                "size": {
                    "length_m": round(length_m, 1),
                    "width_m": round(width_m, 1)
                },
                "trajectory": trajectory,
                "prediction_method": "prototype drift-based extrapolation",
                "source": iceberg['source']
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "icebergs": icebergs,
            "metadata": {
                "source": "real",
                "dataset": IcebergAdapter.DATASET_ID,
                "prediction_method": "prototype drift-based extrapolation",
                "forecast_horizon": "48 hours",
                "note": "Real USNIC observations with prototype trajectory prediction"
            }
        }
    
    def _generate_demo_icebergs(self, min_size: float) -> Dict:
        """
        Generate deterministic demo iceberg data as fallback.
        """
        # Generate deterministic icebergs
        np.random.seed(44)
        num_icebergs = 10
        
        icebergs = []
        for i in range(num_icebergs):
            # Random position in Antarctic region
            lon = np.random.uniform(-180, 180)
            lat = np.random.uniform(-90, -60)
            
            # Random size
            length_nm = np.random.uniform(10, 30)  # nautical miles
            width_nm = length_nm * np.random.uniform(0.5, 0.8)
            
            # Convert to meters
            length_m = length_nm * 1852
            width_m = width_nm * 1852
            
            # Skip if below minimum size
            if length_nm < min_size:
                continue
            
            # Generate simple trajectory (constant drift)
            trajectory = []
            for hours in [6, 12, 24, 48]:
                # Simple drift: ~0.05 km/h
                drift_km = 0.05 * hours
                drift_deg = drift_km / 111  # approx km per degree
                
                trajectory.append({
                    "hours_ahead": hours,
                    "lon": round(lon + drift_deg, 4),
                    "lat": round(lat + drift_deg * 0.5, 4),
                    "uncertainty_nm": round(5.0 + 0.8 * hours, 1)
                })
            
            icebergs.append({
                "id": f"iceberg-{i:03d}",
                "position": {
                    "lon": round(lon, 2),
                    "lat": round(lat, 2)
                },
                "observed_at": datetime.utcnow().isoformat() + "Z",
                "size": {
                    "length_m": round(length_m, 1),
                    "width_m": round(width_m, 1)
                },
                "trajectory": trajectory,
                "prediction_method": "prototype drift-based extrapolation",
                "source": "demo"
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "icebergs": icebergs,
            "metadata": {
                "source": "demo",
                "prediction_method": "prototype drift-based extrapolation",
                "forecast_horizon": "48 hours",
                "note": "Deterministic seeded demo data - real USNIC data unavailable"
            }
        }
