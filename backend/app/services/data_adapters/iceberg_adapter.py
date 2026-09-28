"""
Iceberg Data Adapter

Loads and normalizes real USNIC (U.S. National Ice Center) Antarctic iceberg data.
Implements prototype drift-based trajectory prediction using observed positions.

Source: NOAA / U.S. National Ice Center (USNIC)
Dataset: Antarctic Iceberg Locations, 2014 to Present, Weekly
Documentation: https://usicecenter.gov/Catalog/AntarcIceberg
"""

import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IcebergAdapter:
    """
    Adapter for USNIC Antarctic iceberg observations.
    
    Provides:
    - Real observed iceberg positions
    - Prototype drift-based trajectory prediction
    - Normalized internal representation
    """
    
    DATASET_ID = "USNIC Antarctic Iceberg Locations"
    SOURCE = "U.S. National Ice Center (USNIC)"
    DATA_TYPE = "real"
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the iceberg adapter.
        
        Args:
            data_dir: Path to data directory. If None, uses default.
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(__file__),
                "../../../data/icebergs/usnic"
            )
        
        self.data_file = os.path.join(data_dir, "icebergs_locations_usi.csv")
        self._cache: Optional[List[Dict]] = None
        self._trajectory_cache: Dict[str, List[Dict]] = {}
        
    def load_icebergs(self) -> List[Dict]:
        """
        Load iceberg observations from cached USNIC CSV file.
        
        Returns:
            List of normalized iceberg observation dictionaries.
        """
        if self._cache is not None:
            return self._cache
        
        if not os.path.exists(self.data_file):
            logger.warning(f"USNIC data file not found: {self.data_file}")
            return []
        
        icebergs = []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        iceberg = self._normalize_row(row)
                        if iceberg:
                            icebergs.append(iceberg)
                    except Exception as e:
                        logger.warning(f"Failed to parse iceberg row: {e}")
                        continue
            
            self._cache = icebergs
            logger.info(f"Loaded {len(icebergs)} iceberg observations from USNIC")
            
        except Exception as e:
            logger.error(f"Failed to load USNIC iceberg data: {e}")
            return []
        
        return icebergs
    
    def _normalize_row(self, row: Dict) -> Optional[Dict]:
        """
        Normalize a USNIC CSV row to internal representation.
        
        Args:
            row: Raw CSV row from USNIC dataset.
            
        Returns:
            Normalized iceberg dictionary or None if invalid.
        """
        try:
            # Parse coordinates
            lat = float(row.get('latitude', 0))
            lon = float(row.get('longitude', 0))
            
            # Parse dimensions (nautical miles)
            length_nm = float(row.get('length_nm', 0))
            width_nm = float(row.get('width_nm', 0))
            
            # Parse timestamp (Unix timestamp)
            timestamp = int(row.get('time', 0))
            observed_at = datetime.fromtimestamp(timestamp)
            
            # Get iceberg ID
            iceberg_id = row.get('Iceberg', '').strip()
            if not iceberg_id:
                iceberg_id = f"UNKNOWN_{hash(row)}"
            
            return {
                'id': iceberg_id,
                'position': {
                    'lat': lat,
                    'lon': lon
                },
                'observed_at': observed_at.isoformat(),
                'timestamp': timestamp,
                'length_nm': length_nm,
                'width_nm': width_nm,
                'remarks': row.get('remarks', ''),
                'source': self.SOURCE,
                'source_type': self.DATA_TYPE
            }
            
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to normalize iceberg row: {e}")
            return None
    
    def calculate_trajectory(
        self,
        iceberg_id: str,
        current_position: Dict,
        historical_observations: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Calculate prototype drift-based trajectory prediction.
        
        Uses observed displacement between consecutive observations to estimate
        drift velocity, then extrapolates to future positions.
        
        Args:
            iceberg_id: Iceberg identifier.
            current_position: Current position {'lat': ..., 'lon': ...}.
            historical_observations: Historical observations for this iceberg.
                If None, uses constant-velocity fallback.
                
        Returns:
            List of predicted positions at 6h, 12h, 24h, 48h horizons.
        """
        # Check cache
        cache_key = f"{iceberg_id}_{current_position['lat']}_{current_position['lon']}"
        if cache_key in self._trajectory_cache:
            return self._trajectory_cache[cache_key]
        
        # Estimate drift velocity from historical observations
        drift_velocity = self._estimate_drift_velocity(
            current_position,
            historical_observations
        )
        
        # Generate predictions at different horizons
        horizons = [6, 12, 24, 48]  # hours
        predictions = []
        
        for hours in horizons:
            pred = self._extrapolate_position(
                current_position,
                drift_velocity,
                hours
            )
            
            # Prototype uncertainty estimate (increases with horizon)
            uncertainty_nm = self._estimate_uncertainty(hours)
            
            predictions.append({
                'hours_ahead': hours,
                'lon': pred['lon'],
                'lat': pred['lat'],
                'uncertainty_nm': uncertainty_nm
            })
        
        self._trajectory_cache[cache_key] = predictions
        return predictions
    
    def _estimate_drift_velocity(
        self,
        current_position: Dict,
        historical_observations: Optional[List[Dict]]
    ) -> Tuple[float, float]:
        """
        Estimate drift velocity from historical observations.
        
        Args:
            current_position: Current position.
            historical_observations: Historical positions for this iceberg.
            
        Returns:
            Tuple of (velocity_lat_deg_per_hour, velocity_lon_deg_per_hour).
        """
        if not historical_observations or len(historical_observations) < 2:
            # Fallback: use small constant drift (prototype assumption)
            # Typical Antarctic iceberg drift: 0.1-0.5 km/h
            # Convert to degrees (approx 111 km per degree)
            return (0.0005, 0.0005)  # ~0.05 km/h drift
        
        # Use most recent two observations to estimate velocity
        sorted_obs = sorted(historical_observations, key=lambda x: x['timestamp'])
        recent = sorted_obs[-1]
        previous = sorted_obs[-2]
        
        # Calculate time difference in hours
        time_diff_hours = (recent['timestamp'] - previous['timestamp']) / 3600
        
        if time_diff_hours <= 0:
            return (0.0005, 0.0005)  # Fallback
        
        # Calculate displacement
        lat_diff = recent['position']['lat'] - previous['position']['lat']
        lon_diff = recent['position']['lon'] - previous['position']['lon']
        
        # Velocity in degrees per hour
        vel_lat = lat_diff / time_diff_hours
        vel_lon = lon_diff / time_diff_hours
        
        return (vel_lat, vel_lon)
    
    def _extrapolate_position(
        self,
        current_position: Dict,
        velocity: Tuple[float, float],
        hours_ahead: int
    ) -> Dict:
        """
        Extrapolate position using constant velocity.
        
        Args:
            current_position: Current position.
            velocity: (vel_lat, vel_lon) in degrees per hour.
            hours_ahead: Hours to extrapolate.
            
        Returns:
            Predicted position.
        """
        vel_lat, vel_lon = velocity
        
        pred_lat = current_position['lat'] + vel_lat * hours_ahead
        pred_lon = current_position['lon'] + vel_lon * hours_ahead
        
        # Clamp to valid latitude range
        pred_lat = max(-90, min(90, pred_lat))
        
        # Normalize longitude to [-180, 180]
        pred_lon = ((pred_lon + 180) % 360) - 180
        
        return {
            'lat': pred_lat,
            'lon': pred_lon
        }
    
    def _estimate_uncertainty(self, hours_ahead: int) -> float:
        """
        Estimate prototype uncertainty radius.
        
        Uncertainty increases with forecast horizon.
        This is NOT statistically validated - it's a prototype estimate.
        
        Args:
            hours_ahead: Forecast horizon in hours.
            
        Returns:
            Uncertainty radius in nautical miles.
        """
        # Linear increase: ~5 NM at 6h, ~40 NM at 48h
        # This is a rough prototype estimate
        base_uncertainty = 5.0  # NM
        growth_rate = 0.8  # NM per hour
        
        return base_uncertainty + growth_rate * hours_ahead
