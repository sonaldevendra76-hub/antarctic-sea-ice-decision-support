import os
from typing import Literal
from pathlib import Path


class Settings:
    """Application settings for data source configuration"""
    
    def __init__(self):
        # Data mode: "demo" for synthetic data, "real" for actual datasets
        # Priority: 1. Environment variable DATA_MODE, 2. Check for NetCDF file, 3. Default to demo
        self.DATA_MODE: Literal["demo", "real"] = self._detect_data_mode()
    
    def _detect_data_mode(self) -> str:
        """Auto-detect data mode based on available data files"""
        # If environment variable is set, use it
        env_mode = os.getenv("DATA_MODE")
        if env_mode in ["demo", "real"]:
            print(f"DATA_MODE from environment: {env_mode}")
            return env_mode
        
        # Check if NetCDF file exists
        data_dir = Path("data/sea_ice/g02202")
        if data_dir.exists():
            nc_files = list(data_dir.glob("*.nc"))
            if nc_files:
                print(f"Found {len(nc_files)} NetCDF file(s) in {data_dir}")
                print("Auto-setting DATA_MODE to 'real'")
                return "real"
        
        print("No NetCDF files found, using demo mode")
        return "demo"
    
    def is_real_mode(self) -> bool:
        """Check if running in real data mode"""
        return self.DATA_MODE == "real"
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.DATA_MODE == "demo"


settings = Settings()
