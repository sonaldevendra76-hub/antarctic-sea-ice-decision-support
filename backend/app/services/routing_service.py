import heapq
import numpy as np
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import uuid

from app.models import Coordinates, VesselCapabilities, RouteObjectives, Waypoint, RouteSummary


class RoutingService:
    """
    Service for route calculation using A* pathfinding with risk-aware cost function.
    """
    
    def __init__(self):
        self.grid_resolution = 0.1  # degrees
        # Cache for bathymetry and iceberg data (in production, fetch from services)
        self._bathymetry_cache: Optional[dict] = None
        self._iceberg_cache: Optional[dict] = None
        # Cache for forecast ice concentration data
        self._ice_concentration_cache: Optional[Dict] = None
        # Iceberg risk parameters
        self.iceberg_safety_radius_nm = 20.0  # Safety radius in nautical miles
        self.iceberg_risk_weight = 0.5  # Weight for iceberg risk in total cost
    
    def calculate_route(
        self,
        start: Coordinates,
        end: Coordinates,
        vessel_config: VesselCapabilities,
        objectives: RouteObjectives,
        forecast_timestep: int,
        forecast_data: Optional[Dict] = None,
        iceberg_data: Optional[Dict] = None
    ):
        """
        Calculate optimal route using A* algorithm with risk-aware cost function.
        
        Args:
            forecast_data: Optional forecast data with ice concentration grid
            iceberg_data: Optional iceberg data with trajectory predictions
        """
        # Cache forecast data if provided
        if forecast_data:
            self._ice_concentration_cache = forecast_data
        
        # Cache iceberg data if provided
        if iceberg_data:
            self._iceberg_cache = iceberg_data
        
        # For initial implementation, use a simplified A* on a grid
        waypoints = self._astar_search(start, end, vessel_config, objectives)
        
        # Calculate route summary
        summary = self._calculate_summary(waypoints, vessel_config, objectives)
        
        # Include data source in metadata
        data_source = "demo"
        if self._ice_concentration_cache and self._ice_concentration_cache.get("metadata"):
            data_source = self._ice_concentration_cache["metadata"].get("source", "demo")
        
        return {
            "route_id": f"route-{uuid.uuid4().hex[:8]}",
            "waypoints": waypoints,
            "summary": summary,
            "algorithm": "A*",
            "cost_function": "risk_aware",
            "metadata": {
                "forecast_timestep": forecast_timestep,
                "data_source": data_source,
                "note": "A* implementation with risk-aware cost function"
            }
        }
    
    def _astar_search(
        self,
        start: Coordinates,
        end: Coordinates,
        vessel_config: VesselCapabilities,
        objectives: RouteObjectives
    ) -> List[dict]:
        """
        A* pathfinding algorithm with risk-aware cost function.
        """
        # Get grid bounds from forecast data if available
        if self._ice_concentration_cache and "grid" in self._ice_concentration_cache:
            bounds = self._ice_concentration_cache["grid"]["bounds"]
            grid_data = self._ice_concentration_cache["grid"]["ice_concentration"]
            grid_height = len(grid_data)
            grid_width = len(grid_data[0]) if grid_height > 0 else 0
            grid_resolution = self._ice_concentration_cache["grid"]["resolution"]
        else:
            # Fallback to default global bounds
            bounds = {"min_lon": -180.0, "min_lat": -90.0, "max_lon": 180.0, "max_lat": -60.0}
            grid_height = 300
            grid_width = 360
            grid_resolution = 0.5
        
        # Validate coordinates are within forecast coverage
        if not (bounds["min_lon"] <= start.lon <= bounds["max_lon"] and
                bounds["min_lat"] <= start.lat <= bounds["max_lat"]):
            raise ValueError(
                f"Start coordinate ({start.lon}, {start.lat}) is outside forecast coverage. "
                f"Valid bounds: lon [{bounds['min_lon']}, {bounds['max_lon']}], lat [{bounds['min_lat']}, {bounds['max_lat']}]"
            )
        
        if not (bounds["min_lon"] <= end.lon <= bounds["max_lon"] and
                bounds["min_lat"] <= end.lat <= bounds["max_lat"]):
            raise ValueError(
                f"End coordinate ({end.lon}, {end.lat}) is outside forecast coverage. "
                f"Valid bounds: lon [{bounds['min_lon']}, {bounds['max_lon']}], lat [{bounds['min_lat']}, {bounds['max_lat']}]"
            )
        
        # Convert to grid coordinates using actual forecast bounds
        start_grid = self._to_grid(start.lon, start.lat, bounds, grid_width, grid_height)
        end_grid = self._to_grid(end.lon, end.lat, bounds, grid_width, grid_height)
        
        print(f"Start: ({start.lon}, {start.lat}) -> grid: {start_grid}")
        print(f"End: ({end.lon}, {end.lat}) -> grid: {end_grid}")
        print(f"Grid dimensions: {grid_width} x {grid_height}")
        
        # Priority queue: (f_score, g_score, grid_x, grid_y, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, start_grid[0], start_grid[1], []))
        
        # Track visited
        visited = set()
        g_scores = {}
        
        max_iterations = 10000  # Prevent infinite loops
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            f_score, g_score, x, y, path = heapq.heappop(open_set)
            
            if (x, y) == end_grid:
                # Convert path to waypoints
                waypoints = []
                current_time = datetime.utcnow()
                
                # Add start
                waypoints.append({
                    "lon": start.lon,
                    "lat": start.lat,
                    "estimated_arrival": current_time.isoformat() + "Z",
                    "risk_score": 0.1
                })
                
                # Add intermediate waypoints (sample every 5th point to reduce output size)
                for i, (px, py) in enumerate(path):
                    if i % 5 == 0 or i == len(path) - 1:
                        lon, lat = self._from_grid(px, py, bounds, grid_width, grid_height)
                        current_time += timedelta(hours=0.5)
                        risk = self._calculate_risk_at_point(px, py, vessel_config)
                        waypoints.append({
                            "lon": round(lon, 4),
                            "lat": round(lat, 4),
                            "estimated_arrival": current_time.isoformat() + "Z",
                            "risk_score": round(risk, 3)
                        })
                
                # Add end
                current_time += timedelta(hours=0.5)
                waypoints.append({
                    "lon": end.lon,
                    "lat": end.lat,
                    "estimated_arrival": current_time.isoformat() + "Z",
                    "risk_score": 0.1
                })
                
                print(f"A* found path with {len(waypoints)} waypoints after {iterations} iterations")
                return waypoints
            
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            # Explore neighbors (8-directional)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if nx < 0 or nx >= grid_width or ny < 0 or ny >= grid_height:
                    continue
                
                if (nx, ny) in visited:
                    continue
                
                # Calculate cost
                move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                risk_cost = self._calculate_risk_at_point(nx, ny, vessel_config)
                
                # Weighted cost based on objectives
                total_cost = (
                    move_cost * objectives.minimize_time +
                    risk_cost * objectives.minimize_risk * 10
                )
                
                new_g = g_score + total_cost
                h_score = self._heuristic((nx, ny), end_grid)
                f_score = new_g + h_score
                
                if (nx, ny) not in g_scores or new_g < g_scores[(nx, ny)]:
                    g_scores[(nx, ny)] = new_g
                    new_path = path + [(x, y)]
                    heapq.heappush(open_set, (f_score, new_g, nx, ny, new_path))
        
        print(f"A* failed to find path after {iterations} iterations, using fallback")
        # Fallback: direct path if no route found
        return [
            {
                "lon": start.lon,
                "lat": start.lat,
                "estimated_arrival": datetime.utcnow().isoformat() + "Z",
                "risk_score": 0.5
            },
            {
                "lon": end.lon,
                "lat": end.lat,
                "estimated_arrival": (datetime.utcnow() + timedelta(hours=10)).isoformat() + "Z",
                "risk_score": 0.5
            }
        ]
    
    def _to_grid(self, lon: float, lat: float, bounds: dict, grid_width: int, grid_height: int) -> Tuple[int, int]:
        """Convert coordinates to grid indices using actual forecast bounds."""
        lon_range = bounds["max_lon"] - bounds["min_lon"]
        lat_range = bounds["max_lat"] - bounds["min_lat"]
        
        x = int(((lon - bounds["min_lon"]) / lon_range) * grid_width)
        y = int(((lat - bounds["min_lat"]) / lat_range) * grid_height)
        
        # Clamp to grid bounds
        x = max(0, min(x, grid_width - 1))
        y = max(0, min(y, grid_height - 1))
        
        return (x, y)
    
    def _from_grid(self, x: int, y: int, bounds: dict, grid_width: int, grid_height: int) -> Tuple[float, float]:
        """Convert grid indices to coordinates using actual forecast bounds."""
        lon_range = bounds["max_lon"] - bounds["min_lon"]
        lat_range = bounds["max_lat"] - bounds["min_lat"]
        
        lon = bounds["min_lon"] + (x / grid_width) * lon_range
        lat = bounds["min_lat"] + (y / grid_height) * lat_range
        
        return (lon, lat)
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic."""
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    
    def _calculate_risk_at_point(self, x: int, y: int, vessel_config: VesselCapabilities) -> float:
        """
        Calculate risk score at a grid point.
        Uses real ice concentration data and iceberg trajectory predictions if available.
        
        Risk = sea-ice risk + iceberg risk
        """
        # Get coordinates for this grid point
        if self._ice_concentration_cache and "grid" in self._ice_concentration_cache:
            bounds = self._ice_concentration_cache["grid"]["bounds"]
            grid_width = len(self._ice_concentration_cache["grid"]["ice_concentration"][0])
            grid_height = len(self._ice_concentration_cache["grid"]["ice_concentration"])
            lon, lat = self._from_grid(x, y, bounds, grid_width, grid_height)
        else:
            # Fallback coordinates
            lon, lat = x * 0.5 - 180, y * 0.1 - 90
        
        # Sea-ice risk
        sea_ice_risk = self._calculate_sea_ice_risk(x, y, vessel_config)
        
        # Iceberg risk
        iceberg_risk = self._calculate_iceberg_risk(lon, lat)
        
        # Combined risk (weighted sum)
        total_risk = sea_ice_risk + (iceberg_risk * self.iceberg_risk_weight)
        
        return min(max(total_risk, 0.0), 1.0)
    
    def _calculate_sea_ice_risk(self, x: int, y: int, vessel_config: VesselCapabilities) -> float:
        """
        Calculate sea-ice risk at a grid point.
        Uses real NOAA/NSIDC ice concentration data if available.
        """
        # Try to get real ice concentration from cached forecast
        ice_concentration = 0.0
        if self._ice_concentration_cache and "grid" in self._ice_concentration_cache:
            grid_data = self._ice_concentration_cache["grid"]["ice_concentration"]
            grid_height = len(grid_data)
            grid_width = len(grid_data[0]) if grid_height > 0 else 0
            
            # Check bounds
            if 0 <= x < grid_width and 0 <= y < grid_height:
                ice_concentration = grid_data[y][x]
        
        # Base risk from ice concentration
        base_risk = ice_concentration
        
        # Adjust for vessel ice class
        ice_class_factor = {
            "PC1": 0.2, "PC2": 0.3, "PC3": 0.4, "PC4": 0.5,
            "PC5": 0.6, "PC6": 0.8, "PC7": 1.0
        }.get(vessel_config.ice_class, 0.5)
        
        risk = base_risk * ice_class_factor
        return min(max(risk, 0.0), 1.0)
    
    def _calculate_iceberg_risk(self, lon: float, lat: float) -> float:
        """
        Calculate iceberg risk at a coordinate based on predicted trajectory positions.
        
        Risk increases as distance to predicted iceberg positions decreases.
        Uses safety radius to define high-risk zone.
        """
        if not self._iceberg_cache or "icebergs" not in self._iceberg_cache:
            return 0.0
        
        icebergs = self._iceberg_cache["icebergs"]
        max_risk = 0.0
        
        for iceberg in icebergs:
            # Check both current position and predicted trajectory points
            positions_to_check = [iceberg["position"]]
            
            # Add predicted trajectory positions
            if "trajectory" in iceberg:
                for pred in iceberg["trajectory"]:
                    positions_to_check.append({
                        "lon": pred["lon"],
                        "lat": pred["lat"]
                    })
            
            # Calculate minimum distance to any iceberg position
            min_distance_nm = float('inf')
            for pos in positions_to_check:
                dist = self._haversine_distance_nm(lon, lat, pos["lon"], pos["lat"])
                min_distance_nm = min(min_distance_nm, dist)
            
            # Calculate risk based on distance (inverse relationship)
            if min_distance_nm < self.iceberg_safety_radius_nm:
                # Inside safety radius: high risk
                risk = 1.0 - (min_distance_nm / self.iceberg_safety_radius_nm)
                max_risk = max(max_risk, risk)
        
        return max_risk
    
    def _haversine_distance_nm(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """
        Calculate great-circle distance between two points in nautical miles.
        """
        from math import radians, sin, cos, sqrt, asin
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth radius in nautical miles (6371 km / 1.852 km per NM)
        r = 6371 / 1.852
        
        return c * r
    
    def _calculate_summary(
        self,
        waypoints: List[dict],
        vessel_config: VesselCapabilities,
        objectives: RouteObjectives
    ) -> dict:
        """Calculate route summary statistics."""
        if len(waypoints) < 2:
            return {
                "total_distance_nm": 0,
                "estimated_duration_hours": 0,
                "total_risk_score": 0,
                "fuel_consumption_liters": 0
            }
        
        # Calculate total distance (simplified)
        total_distance = 0
        total_risk = 0
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            dist = ((p1["lon"] - p2["lon"]) ** 2 + (p1["lat"] - p2["lat"]) ** 2) ** 0.5
            total_distance += dist * 60  # Rough conversion to nautical miles
            total_risk += p2["risk_score"]
        
        avg_risk = total_risk / (len(waypoints) - 1)
        duration = total_distance / vessel_config.speed_knots
        fuel = duration * 200  # Simplified fuel consumption: 200L/hour
        
        return RouteSummary(
            total_distance_nm=round(total_distance, 1),
            estimated_duration_hours=round(duration, 1),
            total_risk_score=round(avg_risk, 2),
            fuel_consumption_liters=round(fuel, 0)
        ).dict()
