# Antarctic Sea-Ice Decision Support System

## 1. Project Overview

The **Antarctic Sea-Ice Decision Support System** is a prototype designed to help research vessels plan safer and more fuel-conscious routes through Antarctic waters.

The SIH problem focuses on three major objectives:

1. Forecast Antarctic sea-ice concentration.
2. Predict iceberg trajectories.
3. Identify safe and fuel-efficient navigation routes for research vessels.

Our current prototype focuses on building the **complete working decision-support pipeline** using real environmental datasets and a risk-aware routing algorithm.

The current system can combine:

**Sea-ice conditions + iceberg observations + vessel parameters → environmental risk → A* routing → route information**

---

# 2. Current Prototype at a Glance

The current implementation contains:

* Real NOAA/NSIDC sea-ice concentration data
* Real USNIC Antarctic iceberg observations
* Prototype iceberg trajectory extrapolation
* Sea-ice risk calculation
* Iceberg proximity risk calculation
* Risk-aware A* route planning
* Vessel configuration
* Distance and travel-time estimation
* Prototype fuel estimation
* Interactive Antarctic map
* Start and destination selection
* FastAPI backend
* React/TypeScript frontend

The prototype is designed as the foundation for the complete SIH solution.

---

# 3. Overall System Architecture

```text
                    ENVIRONMENTAL DATA
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     NOAA/NSIDC         USNIC           Future Data
      Sea Ice          Icebergs       SAR / Weather /
                                      Oceanographic Data
          │                │                │
          ▼                ▼                │
      Sea-Ice Risk    Iceberg Risk            │
          │                │                  │
          └────────────────┼──────────────────┘
                           ▼
                    Risk Assessment
                           │
                           ▼
                    A* Route Planner
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                Safe Route    Fuel/Time
                    │             │
                    └──────┬──────┘
                           ▼
                   React Dashboard
                           │
                           ▼
                         User
```

---

# 4. Sea-Ice Dataset

## NOAA/NSIDC G02202 Version 6

The current prototype uses real Antarctic sea-ice concentration data from the **NOAA/NSIDC Sea Ice Concentration Climate Data Record, Version 6 (G02202)**.

Local file:

```text
backend/data/sea_ice/g02202/
sic_pss25_20260101_am2_v06r00.nc
```

The dataset is stored in **NetCDF** format.

Important variable:

```text
cdr_seaice_conc
```

The current dataset has a grid of approximately:

```text
332 × 316
```

and a spatial resolution of approximately:

```text
25 km
```

The current local file represents sea-ice concentration for:

```text
2026-01-01
```

### How it is used

The backend reads the sea-ice concentration grid and converts it into an environmental risk value.

Conceptually:

```text
Sea-Ice Concentration
          ↓
     Risk Calculation
          ↓
   Risk of Grid Cell
          ↓
      A* Routing
```

Areas with higher sea-ice conditions can receive higher navigation costs.

### Important clarification

The current prototype uses **real sea-ice concentration data**, but it does **not yet contain a trained ML model that forecasts future sea-ice concentration**.

The ML forecasting component is planned as a future enhancement.

---

# 5. Iceberg Dataset

## USNIC Antarctic Iceberg Observations

The prototype also uses real Antarctic iceberg observations from the:

**U.S. National Ice Center (USNIC)**

Local file:

```text
backend/data/icebergs/usnic/
icebergs_locations_usi.csv
```

The dataset contains:

```text
Iceberg
length_nm
width_nm
latitude
longitude
remarks
time
```

Example observations include iceberg IDs such as:

```text
A76C
A81
```

along with their observed:

* Length
* Width
* Latitude
* Longitude
* Date
* Timestamp

For example:

```text
A76C
Length: 16 NM
Width: 7 NM
Latitude: -52.078
Longitude: -31.634
```

These are real observations from the USNIC dataset.

---

# 6. Iceberg Trajectory Prediction

The USNIC dataset primarily provides **observed iceberg positions**.

It does not directly provide the future position of every iceberg.

Therefore, the current prototype creates future positions using a simple **prototype drift-based extrapolation**.

The current flow is:

```text
Real USNIC Observation
          ↓
Current Iceberg Position
          ↓
Prototype Drift Calculation
          ↓
Future Position Estimate
          ↓
6h / 12h / 24h / 48h
```

### Important limitation

The current trajectory prediction is **not a trained ML model and has not been scientifically validated as a forecasting system**.

It is currently a prototype mechanism that demonstrates how predicted iceberg positions can be connected to the navigation risk engine.

A future version can improve this using:

* Historical iceberg tracks
* Ocean currents
* Wind
* Sea-ice movement
* Other oceanographic variables
* Machine learning or physics-informed models

---

# 7. Iceberg Risk

Iceberg information is not only displayed on the dashboard.

It is also connected to the routing engine.

The routing system calculates the distance between potential route locations and current/predicted iceberg positions.

The current prototype uses an iceberg safety radius.

Conceptually:

```text
                 ICEBERG
                    ●
              ┌───────────┐
              │ Risk Area │
              │           │
              └───────────┘

       Route ───────────────→

Far from iceberg:
Lower risk

Close to iceberg:
Higher risk
```

The maximum iceberg risk around a potential route point is incorporated into the total environmental risk.

---

# 8. A* Risk-Aware Routing

The main route-planning algorithm is **A***.

Traditional shortest-path routing would mainly try to minimize distance.

Our implementation adds environmental risk.

Conceptually:

```text
Total Route Cost
      =
Travel/Movement Cost
      +
Environmental Risk Cost
```

Environmental risk currently includes:

```text
Sea-Ice Risk
+
Iceberg Proximity Risk
```

The A* algorithm evaluates possible grid locations and searches for a lower-cost path from the start location to the destination.

Therefore, the system does not simply ask:

> "What is the shortest path?"

It instead asks:

> "What is a lower-cost path considering navigation and environmental risk?"

---

# 9. Vessel Configuration

The route planner accepts vessel-specific parameters.

The current routing configuration includes parameters such as:

```text
Ice Class
Maximum Ice Thickness
Speed
```

The system can also receive different navigation objectives.

For example:

```text
Safety Weight = 0.7
Fuel Weight   = 0.3
```

This allows the routing system to be adapted to different vessel requirements.

---

# 10. Fuel and Travel Estimation

After calculating the route, the system estimates:

* Total route distance
* Estimated travel duration
* Fuel consumption

A tested route produced approximately:

```text
Distance:       1417.8 nautical miles
Duration:       118.2 hours
Fuel estimate:  23,630 liters
```

These values demonstrate the routing concept.

### Important limitation

The current fuel calculation is a **prototype estimation**.

It is not a certified maritime fuel-consumption model.

A production implementation could use:

* Vessel-specific engine characteristics
* Speed-power curves
* Hull resistance
* Ice resistance
* Weather
* Sea state
* Engine efficiency
* Actual fuel curves

---

# 11. SAR Data

## Why SAR is part of the proposed system

SAR means **Synthetic Aperture Radar**.

SAR is important for Antarctic monitoring because it can provide useful information about sea ice and iceberg conditions even when optical satellite imagery has limitations.

Our original proposed architecture includes SAR because it can potentially help with:

* Sea-ice detection
* Sea-ice classification
* Ice-edge detection
* Iceberg detection
* Monitoring changing ice conditions

## Is SAR integrated right now?

**No.**

SAR is **not yet integrated into the current working prototype**.

We first implemented and validated the core pipeline using real NOAA/NSIDC sea-ice data and real USNIC iceberg observations.

The current working system is:

```text
Real Sea-Ice Data
       +
Real Iceberg Data
       ↓
Risk Assessment
       ↓
A* Routing
       ↓
Route
```

The planned SAR pipeline is:

```text
SAR Satellite Data
       ↓
Preprocessing
       ↓
Sea-Ice / Iceberg Feature Extraction
       ↓
Risk Information
       ↓
A* Routing
```

SAR requires additional preprocessing, georeferencing and extraction of useful environmental features before it can be connected reliably to the routing engine.

Therefore, SAR is part of our **proposed methodology and future data-fusion layer**, but it should not be represented as an already completed component of the current prototype.

---

# 12. Bathymetry

Bathymetry represents the underwater depth of the Antarctic region.

Bathymetry support exists in the current system architecture.

However, the current prototype does not yet have a fully integrated high-resolution real Antarctic bathymetric dataset comparable to the real sea-ice and iceberg datasets.

Real bathymetry integration is therefore a future improvement.

A future route-planning system can use bathymetry to prevent vessels from entering areas that are unsuitable because of water depth or vessel draft.

The future pipeline would be:

```text
Bathymetry
    +
Vessel Draft
    ↓
Depth Constraint
    ↓
Safe Navigation Area
    ↓
A* Routing
```

---

# 13. Backend

The backend is built using:

```text
Python
FastAPI
NumPy
Pydantic
```

Important API endpoints currently include:

```text
GET  /api/health
GET  /api/forecast
GET  /api/icebergs
GET  /api/bathymetry/bounds
POST /api/route
WS   /api/ws/alerts
```

### `/api/forecast`

Provides the sea-ice data and related metadata.

### `/api/icebergs`

Provides iceberg observations and prototype trajectory information.

### `/api/route`

Receives:

```text
Start location
Destination
Vessel configuration
Navigation objectives
```

and returns route information.

---

# 14. Frontend

The frontend uses:

```text
React
TypeScript
Vite
Tailwind CSS
MapLibre GL JS
Recharts
Lucide
```

The dashboard provides:

* Antarctic map
* Start location selection
* Destination selection
* Vessel configuration
* Route calculation
* Route visualization
* Risk information
* Route summary
* Environmental information

### Map Interaction

The current interaction is:

```text
First map click
       ↓
Start Point

Second map click
       ↓
Destination

Route calculation
       ↓
A* Route
```

The map interaction bug that previously prevented the second point from being correctly registered has been fixed.

---

# 15. Complete Data Flow

The current system can be understood as:

```text
                REAL DATA
                    │
       ┌────────────┴─────────────┐
       │                          │
       ▼                          ▼
NOAA/NSIDC Sea Ice          USNIC Icebergs
       │                          │
       ▼                          ▼
Sea-Ice Risk             Iceberg Observation
                                  │
                                  ▼
                         Prototype Trajectory
                                  │
                                  ▼
                         Iceberg Risk
       │                          │
       └────────────┬─────────────┘
                    ▼
             Environmental Risk
                    │
                    ▼
              A* Route Engine
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Distance    Time      Fuel
                    │
                    ▼
             React Dashboard
                    │
                    ▼
                   User
```

---

# 16. What Is Completed?

### Completed

* [x] React/Vite frontend
* [x] FastAPI backend
* [x] Interactive Antarctic map
* [x] Start/destination selection
* [x] Real NOAA/NSIDC sea-ice dataset
* [x] Sea-ice risk calculation
* [x] Real USNIC iceberg dataset
* [x] Iceberg API
* [x] Prototype iceberg trajectory
* [x] Iceberg proximity risk
* [x] Iceberg risk integrated into A*
* [x] Risk-aware A* routing
* [x] Vessel parameters
* [x] Route distance calculation
* [x] Travel-time estimation
* [x] Prototype fuel estimation
* [x] Frontend/backend integration

---

# 17. What Is Still Remaining?

### Planned improvements

* [ ] ML-based sea-ice forecasting
* [ ] Improved/validated iceberg trajectory prediction
* [ ] Historical iceberg movement modelling
* [ ] Real Antarctic bathymetry integration
* [ ] SAR data integration
* [ ] Oceanographic and meteorological data integration
* [ ] More advanced vessel-specific fuel modelling
* [ ] Cloud deployment / production hosting

---

# 18. Real vs Prototype Components

| Component                  | Current Status                           |
| -------------------------- | ---------------------------------------- |
| NOAA/NSIDC sea-ice data    | **Real**                                 |
| USNIC iceberg observations | **Real**                                 |
| Sea-ice risk               | **Implemented**                          |
| Iceberg risk               | **Implemented**                          |
| Iceberg future trajectory  | **Prototype extrapolation**              |
| A* routing                 | **Implemented**                          |
| Vessel constraints         | **Implemented**                          |
| Fuel estimation            | **Prototype**                            |
| Bathymetry                 | **Prototype / pending real integration** |
| SAR                        | **Not yet integrated**                   |
| ML sea-ice forecasting     | **Not yet implemented**                  |
| ML iceberg prediction      | **Not yet implemented**                  |

---

# 19. Current Achievement

The most important achievement of the current prototype is that the project now demonstrates an **end-to-end environmental decision-support pipeline**.

```text
Real Antarctic Data
       ↓
Environmental Risk
       ↓
Risk-Aware Route Planning
       ↓
Vessel Route
       ↓
Distance / Time / Risk / Fuel
       ↓
Interactive Dashboard
```

This provides the foundation for adding the more advanced ML, SAR, bathymetry, oceanographic and meteorological components.

---


