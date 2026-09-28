# Antarctic Sea-Ice Decision Support System

A prototype decision-support platform for Antarctic research vessels.

## How to Run

##Backend

Open PowerShell in the project root and run:

cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Backend: http://localhost:8000

### Frontend

Open a second terminal:

cd frontend
npm install
npm run dev

Open the URL shown by Vite.

## Current Features

- Real NOAA/NSIDC G02202 Version 6 sea-ice concentration data
- Real USNIC iceberg observations
- Prototype iceberg trajectory extrapolation
- Iceberg proximity risk
- Risk-aware A* route planning
- Vessel constraints
- Interactive React/MapLibre dashboard
- FastAPI backend

## Current Limitations

- No trained ML sea-ice forecasting model yet
- Iceberg trajectory prediction is currently prototype drift-based extrapolation
- Bathymetry is currently prototype/demo data
- SAR imagery is not yet integrated
- Fuel consumption is a prototype estimate
- Not validated for real-world navigation

## Main Technologies

React, TypeScript, Vite, Tailwind CSS, MapLibre GL JS, Python, FastAPI, NumPy, Pydantic, WebSockets and A* routing.

## Data

Sea ice:
NOAA/NSIDC G02202 Version 6
DOI: 10.7265/b18j-z797

Icebergs:
U.S. National Ice Center (USNIC)
