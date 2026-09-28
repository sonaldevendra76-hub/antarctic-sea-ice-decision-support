from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Coordinates(BaseModel):
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")


class Bounds(BaseModel):
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)


class VesselCapabilities(BaseModel):
    ice_class: str = Field(..., description="Polar ice class (PC1-PC7)")
    max_ice_thickness: float = Field(..., gt=0, description="Maximum ice thickness in meters")
    speed_knots: float = Field(..., gt=0, description="Maximum speed in knots")


class IcebergSize(BaseModel):
    length_m: float = Field(..., gt=0)
    width_m: float = Field(..., gt=0)
    height_m: float = Field(..., gt=0)


class DriftVelocity(BaseModel):
    east_knots: float
    north_knots: float


class RouteObjectives(BaseModel):
    minimize_time: float = Field(default=0.4, ge=0, le=1)
    minimize_risk: float = Field(default=0.4, ge=0, le=1)
    minimize_fuel: float = Field(default=0.2, ge=0, le=1)


class Waypoint(BaseModel):
    lon: float
    lat: float
    estimated_arrival: datetime
    risk_score: float = Field(..., ge=0, le=1)


class RouteSummary(BaseModel):
    total_distance_nm: float
    estimated_duration_hours: float
    total_risk_score: float = Field(..., ge=0, le=1)
    fuel_consumption_liters: float
