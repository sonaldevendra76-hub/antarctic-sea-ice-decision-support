import os
import numpy as np
import xarray as xr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .base_adapter import BaseDataAdapter


class SeaIceDataAdapter(BaseDataAdapter):
    """Adapter for NOAA/NSIDC Sea Ice Concentration data (G02202)"""
    
    DATASET_ID = "NOAA/NSIDC G02202 Version 6"
    DOI = "10.7265/b18j-z797"
    DATA_DIR = "data/sea_ice/g02202"
    
    def __init__(self, mode: str = "demo"):
        super().__init__(mode)
        self.data_file = None
        self._find_data_file()
    
    def _find_data_file(self):
        """Find the NetCDF file in the data directory"""
        data_path = os.path.join(os.getcwd(), self.DATA_DIR)
        if os.path.exists(data_path):
            # Look for .nc files
            for file in os.listdir(data_path):
                if file.endswith('.nc'):
                    self.data_file = os.path.join(data_path, file)
                    print(f"Found NetCDF file: {self.data_file}")
                    break
        else:
            print(f"Data directory not found: {data_path}")
    
    def get_forecast(self, timestep: int = 0, bounds: Optional[str] = None) -> Dict[str, Any]:
        """
        Get sea-ice forecast data.
        
        Args:
            timestep: Forecast timestep (not used for single file mode)
            bounds: Bounding box as "min_lon,min_lat,max_lon,max_lat"
        
        Returns:
            Dictionary with grid data and metadata
        """
        if self.mode == "real" and self.data_file:
            return self._get_real_forecast(bounds)
        else:
            return self._get_demo_forecast(timestep, bounds)
    
    def _get_real_forecast(self, bounds: Optional[str]) -> Dict[str, Any]:
        """Load and process real NOAA/NSIDC NetCDF data"""
        try:
            # Open NetCDF file with xarray
            ds = xr.open_dataset(self.data_file)
            
            # Inspect the dataset
            print(f"NetCDF variables: {list(ds.data_vars.keys())}")
            print(f"NetCDF dimensions: {list(ds.dims.keys())}")
            print(f"NetCDF coordinates: {list(ds.coords.keys())}")
            
            # Find sea ice concentration variable
            # NOAA/NSIDC G02202 uses 'cdr_seaice_conc'
            ice_conc_var = None
            possible_names = ['cdr_seaice_conc', 'seaice_conc', 'goddard_merged_seaice_conc', 
                            'ice_conc', 'concentration', 'sic']
            
            for name in possible_names:
                if name in ds.data_vars:
                    ice_conc_var = name
                    print(f"Found ice concentration variable: {name}")
                    break
            
            if ice_conc_var is None:
                # Use the first variable as fallback
                ice_conc_var = list(ds.data_vars.keys())[0]
                print(f"Using fallback variable: {ice_conc_var}")
            
            # Extract the data
            ice_conc_data = ds[ice_conc_var]
            
            # Get valid range from attributes if available
            valid_range = ice_conc_data.attrs.get('valid_range', [0, 100])
            print(f"Valid range: {valid_range}")
            
            # Get dimensions
            dims = ice_conc_data.dims
            print(f"Variable dimensions: {dims}")
            
            # Handle different coordinate systems
            # NSIDC data typically uses (y, x) or (latitude, longitude)
            # We need to identify which dimension is latitude/longitude
            
            # Try to extract Antarctic region (southern hemisphere)
            # NSIDC data is typically global, we need to filter for Antarctic
            
            # Get the data as numpy array
            ice_conc_array = ice_conc_data.values
            
            # Handle 3D data (time, y, x) - take first time slice
            if len(ice_conc_array.shape) == 3:
                ice_conc_array = ice_conc_array[0]
                print(f"Taking first time slice, shape: {ice_conc_array.shape}")
            
            # Handle fill values and missing data
            # NSIDC uses specific fill values (251, 252, 253, 254, 255 for different conditions)
            fill_values = [251, 252, 253, 254, 255, -9999, -1]
            
            # Replace fill values with NaN
            for fv in fill_values:
                ice_conc_array = np.where(ice_conc_array == fv, np.nan, ice_conc_array)
            
            # Also handle NaN values - set to 0 (open water)
            ice_conc_array = np.where(np.isnan(ice_conc_array), 0, ice_conc_array)
            
            # Normalize concentration to 0-1 range
            # NSIDC data is 0-100 (percentage)
            max_val = np.nanmax(ice_conc_array)
            if max_val > 1:
                ice_conc_array = ice_conc_array / 100.0
                print(f"Normalized from 0-100 to 0-1 range")
            
            # Clip to valid range
            ice_conc_array = np.clip(ice_conc_array, 0, 1)
            print(f"Final shape: {ice_conc_array.shape}")
            print(f"Min/Max concentration: {np.nanmin(ice_conc_array):.3f} / {np.nanmax(ice_conc_array):.3f}")
            print(f"Non-zero pixels: {np.count_nonzero(ice_conc_array > 0)}")
            
            # Get the date from the file
            file_date = self._extract_date_from_dataset(ds)
            
            # Parse bounds if provided
            if bounds:
                parts = bounds.split(",")
                bounds_dict = {
                    "min_lon": float(parts[0]),
                    "min_lat": float(parts[1]),
                    "max_lon": float(parts[2]),
                    "max_lat": float(parts[3])
                }
            else:
                # Default Antarctic bounds
                bounds_dict = {
                    "min_lon": -180.0,
                    "min_lat": -90.0,
                    "max_lon": 180.0,
                    "max_lat": -60.0
                }
            
            # Resolution (NSIDC is typically 25km)
            resolution = 0.25  # Approximate 25km in degrees
            
            # Close the dataset
            ds.close()
            
            # Generate synthetic ice thickness (marked as demo)
            ice_thickness = np.random.uniform(0, 2, ice_conc_array.shape)
            
            return {
                "timestep": 0,
                "timestamp": file_date.isoformat() + "Z",
                "grid": {
                    "bounds": bounds_dict,
                    "resolution": resolution,
                    "ice_concentration": ice_conc_array.tolist(),
                    "ice_thickness": ice_thickness.tolist()
                },
                "metadata": {
                    "source": "real",
                    "dataset": self.DATASET_ID,
                    "doi": self.DOI,
                    "resolution": "25 km",
                    "date": file_date.isoformat() + "Z",
                    "ice_thickness_source": "demo_derived",
                    "ice_thickness_note": "Ice thickness is synthetic - only concentration is from real dataset"
                }
            }
            
        except Exception as e:
            print(f"Error loading real data: {e}")
            print(f"Falling back to demo mode")
            return self._get_demo_forecast(0, bounds)
    
    def _extract_date_from_dataset(self, ds) -> datetime:
        """Extract date from NetCDF dataset"""
        # Try common date variable names
        date_vars = ['time', 'date', 'time_counter', 't']
        
        for var in date_vars:
            if var in ds.coords or var in ds.data_vars:
                try:
                    time_val = ds[var].values
                    if hasattr(time_val, '__len__'):
                        time_val = time_val[0]
                    
                    # Convert to datetime
                    if isinstance(time_val, np.datetime64):
                        return time_val.astype('datetime64[s]').astype(datetime)
                    elif hasattr(time_val, 'to_datetime'):
                        return time_val.to_datetime()
                    else:
                        # Try to parse as numeric
                        return datetime.fromtimestamp(float(time_val))
                except:
                    continue
        
        # Fallback to file modification time
        if self.data_file:
            return datetime.fromtimestamp(os.path.getmtime(self.data_file))
        
        return datetime.utcnow()
    
    def _get_demo_forecast(self, timestep: int, bounds: Optional[str]) -> Dict[str, Any]:
        """Generate demo forecast data (original implementation)"""
        base_bounds = {
            "min_lon": -180.0,
            "min_lat": -90.0,
            "max_lon": 180.0,
            "max_lat": -60.0
        }
        resolution = 0.5
        
        # Parse bounds if provided
        if bounds is None:
            bounds_dict = base_bounds
        else:
            parts = bounds.split(",")
            bounds_dict = {
                "min_lon": float(parts[0]),
                "min_lat": float(parts[1]),
                "max_lon": float(parts[2]),
                "max_lat": float(parts[3])
            }
        
        # Calculate grid dimensions
        lon_steps = int((bounds_dict["max_lon"] - bounds_dict["min_lon"]) / resolution)
        lat_steps = int((bounds_dict["max_lat"] - bounds_dict["min_lat"]) / resolution)
        
        # Generate deterministic demo data based on timestep
        np.random.seed(42 + timestep)
        ice_concentration = np.random.uniform(0, 1, (lat_steps, lon_steps))
        ice_thickness = np.random.uniform(0, 2, (lat_steps, lon_steps))
        
        # Calculate timestamp
        base_time = datetime(2024, 1, 1)
        forecast_time = base_time + timedelta(hours=6 * timestep)
        
        return {
            "timestep": timestep,
            "timestamp": forecast_time.isoformat() + "Z",
            "grid": {
                "bounds": bounds_dict,
                "resolution": resolution,
                "ice_concentration": ice_concentration.tolist(),
                "ice_thickness": ice_thickness.tolist()
            },
            "metadata": {
                "source": "demo",
                "note": "Deterministic seeded demo data - replace with real forecast API"
            }
        }
