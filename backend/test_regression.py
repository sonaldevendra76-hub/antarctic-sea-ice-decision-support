import requests
import json

print("=" * 60)
print("REGRESSION VERIFICATION TEST")
print("=" * 60)

# Test 1: Health
print("\n1. Testing GET /api/health...")
try:
    r = requests.get('http://localhost:8000/api/health')
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Forecast
print("\n2. Testing GET /api/forecast...")
try:
    r = requests.get('http://localhost:8000/api/forecast')
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Source: {data['metadata']['source']}")
    print(f"   Dataset: {data['metadata'].get('dataset', 'N/A')}")
    print(f"   Grid shape: {len(data['grid']['ice_concentration'])} x {len(data['grid']['ice_concentration'][0])}")
    print(f"   DOI: {data['metadata'].get('doi', 'N/A')}")
    print(f"   Resolution: {data['metadata'].get('resolution', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Icebergs
print("\n3. Testing GET /api/icebergs...")
try:
    r = requests.get('http://localhost:8000/api/icebergs')
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Icebergs count: {len(data.get('icebergs', []))}")
    print(f"   Source: {data['metadata']['source']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Bathymetry
print("\n4. Testing GET /api/bathymetry/bounds...")
try:
    r = requests.get('http://localhost:8000/api/bathymetry/bounds?min_lon=-50&min_lat=-75&max_lon=-40&max_lat=-65&resolution=0.1')
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Grid shape: {len(data['depth_grid'])} x {len(data['depth_grid'][0])}")
    print(f"   Source: {data['metadata']['source']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Route (balanced weights)
print("\n5. Testing POST /api/route (balanced weights)...")
try:
    r = requests.post('http://localhost:8000/api/route', json={
        'start': {'lon': -45.0, 'lat': -70.0},
        'end': {'lon': -40.0, 'lat': -65.0},
        'vessel_config': {'ice_class': 'PC5', 'max_ice_thickness': 1.5, 'speed_knots': 12.0},
        'objectives': {'minimize_time': 0.4, 'minimize_risk': 0.4, 'minimize_fuel': 0.2},
        'forecast_timestep': 0
    })
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Route ID: {data['route_id']}")
    print(f"   Waypoints: {len(data['waypoints'])}")
    print(f"   Algorithm: {data['algorithm']}")
    print(f"   Data source: {data['metadata']['data_source']}")
    print(f"   Distance: {data['summary']['total_distance_nm']} nm")
    print(f"   Risk score: {data['summary']['total_risk_score']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 6: Route (high risk weight)
print("\n6. Testing POST /api/route (high risk weight)...")
try:
    r = requests.post('http://localhost:8000/api/route', json={
        'start': {'lon': -45.0, 'lat': -70.0},
        'end': {'lon': -40.0, 'lat': -65.0},
        'vessel_config': {'ice_class': 'PC5', 'max_ice_thickness': 1.5, 'speed_knots': 12.0},
        'objectives': {'minimize_time': 0.1, 'minimize_risk': 0.8, 'minimize_fuel': 0.1},
        'forecast_timestep': 0
    })
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Waypoints: {len(data['waypoints'])}")
    print(f"   Risk score: {data['summary']['total_risk_score']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 7: Route (PC1 vessel)
print("\n7. Testing POST /api/route (PC1 vessel)...")
try:
    r = requests.post('http://localhost:8000/api/route', json={
        'start': {'lon': -45.0, 'lat': -70.0},
        'end': {'lon': -40.0, 'lat': -65.0},
        'vessel_config': {'ice_class': 'PC1', 'max_ice_thickness': 3.0, 'speed_knots': 15.0},
        'objectives': {'minimize_time': 0.4, 'minimize_risk': 0.4, 'minimize_fuel': 0.2},
        'forecast_timestep': 0
    })
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Risk score: {data['summary']['total_risk_score']}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("REGRESSION VERIFICATION COMPLETE")
print("=" * 60)
