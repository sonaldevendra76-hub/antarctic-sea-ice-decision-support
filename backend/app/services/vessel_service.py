class VesselService:
    """
    Service for vessel data and configuration.
    """
    
    def __init__(self):
        self.vessel_data = {
            "id": "vessel-001",
            "name": "RV Polar Star",
            "position": {
                "lon": -45.0,
                "lat": -70.0
            },
            "capabilities": {
                "ice_class": "PC5",
                "max_ice_thickness": 1.5,
                "speed_knots": 12.0
            },
            "status": "active"
        }
    
    def get_vessel_data(self):
        """
        Return current vessel configuration.
        """
        return self.vessel_data
