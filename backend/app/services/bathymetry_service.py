import numpy as np


class BathymetryService:
    """
    Service for bathymetry (seafloor depth) data.
    Currently uses demo grid data.
    """
    
    def __init__(self):
        np.random.seed(43)  # Different seed for bathymetry
    
    def get_bathymetry(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float, resolution: float):
        """
        Generate demo bathymetry data for specified bounds.
        """
        # Calculate grid dimensions
        lon_steps = int((max_lon - min_lon) / resolution)
        lat_steps = int((max_lat - min_lat) / resolution)
        
        # Generate deterministic depth data (100m to 4000m)
        np.random.seed(43)
        depth_grid = np.random.uniform(100, 4000, (lat_steps, lon_steps))
        
        return {
            "bounds": {
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat
            },
            "resolution": resolution,
            "depth_grid": depth_grid.tolist(),
            "metadata": {
                "source": "demo",
                "note": "Demo grid data - replace with real bathymetry database"
            }
        }
