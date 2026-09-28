# Antarctic Sea-Ice Decision Support System - API Contract

## Overview
This document defines the API contract between the frontend (React/Vite) and backend (FastAPI) for the Antarctic Sea-Ice Decision Support System.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET /health**

Check if the backend service is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "0.1.0"
}
```

### 2. Get Forecast Data
**GET /forecast**

Retrieve sea-ice forecast data for Antarctic waters.

**Query Parameters:**
- `timestep` (optional): Integer, forecast timestep (default: 0)
- `bounds` (optional): String, bbox format "min_lon,min_lat,max_lon,max_lat"

**Response:**
```json
{
  "timestep": 0,
  "timestamp": "2024-01-01T00:00:00Z",
  "grid": {
    "bounds": {
      "min_lon": -180.0,
      "min_lat": -90.0,
      "max_lon": 180.0,
      "max_lat": -60.0
    },
    "resolution": 0.5,
    "ice_concentration": [[0.1, 0.2, ...], ...],
    "ice_thickness": [[0.5, 0.6, ...], ...]
  }
}
```

### 3. Get Vessel Data
**GET /vessel**

Retrieve current vessel status and configuration.

**Response:**
```json
{
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
```

### 4. Get Bathymetry Bounds
**GET /bathymetry/bounds**

Retrieve bathymetry (seafloor depth) data for a specified bounding box.

**Query Parameters:**
- `min_lon`: Float, minimum longitude
- `min_lat`: Float, minimum latitude
- `max_lon`: Float, maximum longitude
- `max_lat`: Float, maximum latitude
- `resolution` (optional): Float, grid resolution in degrees (default: 0.1)

**Response:**
```json
{
  "bounds": {
    "min_lon": -50.0,
    "min_lat": -75.0,
    "max_lon": -40.0,
    "max_lat": -65.0
  },
  "resolution": 0.1,
  "depth_grid": [[100, 150, ...], ...],
  "metadata": {
    "source": "demo",
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

### 5. Get Icebergs
**GET /icebergs**

Retrieve detected iceberg positions and characteristics.

**Query Parameters:**
- `bounds` (optional): String, bbox format "min_lon,min_lat,max_lon,max_lat"
- `min_size` (optional): Float, minimum iceberg size in meters (default: 0)

**Response:**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "icebergs": [
    {
      "id": "iceberg-001",
      "position": {
        "lon": -45.5,
        "lat": -70.5
      },
      "size": {
        "length_m": 200,
        "width_m": 150,
        "height_m": 30
      },
      "drift_velocity": {
        "east_knots": 0.1,
        "north_knots": -0.05
      }
    }
  ]
}
```

### 6. Calculate Route
**POST /route**

Calculate optimal route using A* pathfinding algorithm with risk-aware cost function.

**Request Body:**
```json
{
  "start": {
    "lon": -45.0,
    "lat": -70.0
  },
  "end": {
    "lon": -40.0,
    "lat": -65.0
  },
  "vessel_config": {
    "ice_class": "PC5",
    "max_ice_thickness": 1.5,
    "speed_knots": 12.0
  },
  "objectives": {
    "minimize_time": 0.4,
    "minimize_risk": 0.4,
    "minimize_fuel": 0.2
  },
  "forecast_timestep": 0
}
```

**Response:**
```json
{
  "route_id": "route-001",
  "waypoints": [
    {
      "lon": -45.0,
      "lat": -70.0,
      "estimated_arrival": "2024-01-01T00:00:00Z",
      "risk_score": 0.1
    },
    {
      "lon": -44.5,
      "lat": -69.5,
      "estimated_arrival": "2024-01-01T01:30:00Z",
      "risk_score": 0.2
    }
  ],
  "summary": {
    "total_distance_nm": 150.5,
    "estimated_duration_hours": 12.5,
    "total_risk_score": 0.15,
    "fuel_consumption_liters": 2500
  },
  "algorithm": "A*",
  "cost_function": "risk_aware"
}
```

### 7. WebSocket Alerts
**WebSocket /ws/alerts**

Real-time alert notifications for SAR events, ice hazards, and route deviations.

**Connection:**
```
ws://localhost:8000/ws/alerts
```

**Message Format (Server -> Client):**
```json
{
  "type": "sar_alert",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "alert_id": "sar-001",
    "severity": "critical",
    "position": {
      "lon": -42.0,
      "lat": -67.0
    },
    "message": "SAR operation requested at coordinates",
    "vessel_in_range": true
  }
}
```

**Alert Types:**
- `sar_alert`: Search and Rescue emergency
- `ice_hazard`: Dangerous ice concentration detected
- `route_deviation`: Vessel deviating from planned route
- `weather_warning`: Severe weather conditions

## Data Types

### Coordinates
All coordinates use WGS84 decimal degrees:
- Longitude: -180 to 180
- Latitude: -90 to 90 (Antarctic region: -90 to -60)

### Risk Scores
Risk scores are normalized 0.0 to 1.0:
- 0.0: No risk
- 0.5: Moderate risk
- 1.0: Extreme risk

### Ice Classes
Polar ice classifications:
- `PC1`: Year-round operation in all polar waters
- `PC2`: Year-round operation in medium first-year ice
- `PC3`: Year-round operation in second-year ice
- `PC4`: Year-round operation in thick first-year ice
- `PC5`: Summer/autumn operation in medium first-year ice
- `PC6`: Summer/autumn operation in thin first-year ice
- `PC7`: Summer/autumn operation in old ice

## Error Responses

All endpoints may return error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid coordinate bounds",
    "details": {}
  }
}
```

## Version
Current API version: 0.1.0
