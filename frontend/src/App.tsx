import { useState, useEffect, useCallback } from 'react'
import AntarcticMap from './components/AntarcticMap'
import ForecastSlider from './components/ForecastSlider'
import VesselControls from './components/VesselControls'
import RiskPanel from './components/RiskPanel'
import AlertPanel from './components/AlertPanel'
import RouteSummary from './components/RouteSummary'
import ObjectiveSliders from './components/ObjectiveSliders'
import { api } from './services/api'
import {
  VesselData,
  ForecastData,
  IcebergData,
  RouteData,
  RouteObjectives,
  Alert,
  Coordinates
} from './types'

function App() {
  const [forecastTimestep, setForecastTimestep] = useState(0)
  const [vesselData, setVesselData] = useState<VesselData | null>(null)
  const [forecastData, setForecastData] = useState<ForecastData | null>(null)
  const [icebergData, setIcebergData] = useState<IcebergData | null>(null)
  const [routeData, setRouteData] = useState<RouteData | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [objectives, setObjectives] = useState<RouteObjectives>({
    minimize_time: 0.4,
    minimize_risk: 0.4,
    minimize_fuel: 0.2
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [startPoint, setStartPoint] = useState<Coordinates | null>(null)
  const [endPoint, setEndPoint] = useState<Coordinates | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Load vessel data
        const vessel = await api.getVessel()
        setVesselData(vessel)
        
        // Load forecast data
        const forecast = await api.getForecast(forecastTimestep)
        setForecastData(forecast)
        
        // Load iceberg data
        const icebergs = await api.getIcebergs()
        setIcebergData(icebergs)
        
        // Setup WebSocket connection for alerts
        const ws = api.connectAlerts()
        ws.onopen = () => {
          setWsConnected(true)
        }
        ws.onmessage = (event: MessageEvent) => {
          const alert = JSON.parse(event.data)
          setAlerts(prev => [...prev, alert])
        }
        ws.onerror = (err: Event) => {
          console.error('WebSocket error:', err)
          setWsConnected(false)
        }
        ws.onclose = () => {
          setWsConnected(false)
        }
        
        return () => ws.close()
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
        console.error('Failed to load data:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [forecastTimestep])

  useEffect(() => {
    console.log("STATE CHANGED:", {
      startPoint,
      endPoint,
    })
  }, [startPoint, endPoint])

  const handleMapClick = useCallback((point: Coordinates) => {
    console.log("========== MAP CLICK ==========")
    console.log("CLICKED POINT:", point)
    console.log("CURRENT startPoint:", startPoint)
    console.log("CURRENT endPoint:", endPoint)

    if (startPoint === null) {
      console.log(">>> ACTION: SETTING START")
      setStartPoint(point)
      return
    }

    if (endPoint === null) {
      console.log(">>> ACTION: SETTING DESTINATION")
      setEndPoint(point)
      return
    }

    console.log(">>> ACTION: IGNORING THIRD CLICK")
  }, [startPoint, endPoint])

  const handleCalculateRoute = async () => {
    if (!vesselData || !startPoint || !endPoint) return
    
    try {
      const route = await api.calculateRoute({
        start: startPoint,
        end: endPoint,
        vessel_config: vesselData.capabilities,
        objectives,
        forecast_timestep: forecastTimestep
      })
      setRouteData(route)
    } catch (err) {
      console.error('Failed to calculate route:', err)
      setError(err instanceof Error ? err.message : 'Failed to calculate route')
    }
  }

  const handleClearRoute = () => {
    setStartPoint(null)
    setEndPoint(null)
    setRouteData(null)
  }

  const handleTriggerDemoAlert = async (type: string) => {
    try {
      await api.triggerDemoAlert(type)
    } catch (err) {
      console.error('Failed to trigger alert:', err)
    }
  }

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#0a0e1a] text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-xl mb-2">Loading Antarctic Environmental Data...</div>
          <div className="text-slate-400 text-sm">Connecting to backend services</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#0a0e1a] text-white">
        <div className="text-center text-red-400 max-w-md">
          <div className="text-2xl mb-4">Backend Connection Unavailable</div>
          <div className="text-slate-400 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0e1a] text-white">
      {/* Header */}
      <header className="bg-slate-900/95 backdrop-blur border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="text-blue-400">ANTARCTIC</span> SEA-ICE DECISION SUPPORT SYSTEM
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              AI/ML-Enabled Research Vessel Navigation Prototype
            </p>
          </div>
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${!error ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-slate-400">Backend: {!error ? 'CONNECTED' : 'DISCONNECTED'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${forecastData?.metadata.source === 'real' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span className="text-slate-400">
                Sea-Ice: {forecastData?.metadata.source === 'real' ? 'REAL' : 'DEMO'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span className="text-slate-400">Routing: A*</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              <span className="text-slate-400">Iceberg: DEMO</span>
            </div>
          </div>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Main Map Area */}
        <div className="flex-1 relative">
          {/* Map Instructions */}
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-black/80 text-white px-4 py-2 rounded text-sm">
            {!startPoint && !endPoint && "Click once to set START • Click again to set DESTINATION"}
            {startPoint && !endPoint && "START selected • Click to set DESTINATION"}
            {startPoint && endPoint && "START and DESTINATION selected • Press Reset to choose new points"}
          </div>

          <AntarcticMap
            forecastData={forecastData}
            vesselData={vesselData}
            icebergData={icebergData}
            routeData={routeData}
            startPoint={startPoint}
            endPoint={endPoint}
            onMapClick={handleMapClick}
          />
          
          {/* Floating Controls */}
          <div className="absolute top-4 left-4 space-y-2">
            <ForecastSlider
              value={forecastTimestep}
              onChange={setForecastTimestep}
            />
          </div>
          
          <div className="absolute top-4 right-4 space-y-2">
            <VesselControls vesselData={vesselData} />
          </div>
        </div>
        
        {/* Side Panel */}
        <div className="w-96 bg-slate-900/95 backdrop-blur border-l border-slate-700/50 overflow-y-auto">
          <div className="p-4 space-y-4">
            {/* Sea-Ice Conditions Card */}
            {forecastData && (
              <div className="glass-panel rounded-lg p-4">
                <h3 className="text-sm font-semibold text-blue-400 mb-3 flex items-center">
                  <span className="mr-2">❄️</span> SEA-ICE CONDITIONS
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Dataset:</span>
                    <span className="text-white">NOAA/NSIDC G02202 V6</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Resolution:</span>
                    <span className="text-white">25 km</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status:</span>
                    <span className="text-green-400">REAL DATA</span>
                  </div>
                  <div className="pt-2 border-t border-slate-700/50">
                    <p className="text-xs text-slate-500">DOI: 10.7265/b18j-z797</p>
                  </div>
                </div>
              </div>
            )}

            {/* Vessel Card */}
            {vesselData && (
              <div className="glass-panel rounded-lg p-4">
                <h3 className="text-sm font-semibold text-orange-400 mb-3 flex items-center">
                  <span className="mr-2">🚢</span> RESEARCH VESSEL
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Name:</span>
                    <span className="text-white">{vesselData.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status:</span>
                    <span className="text-green-400">{vesselData.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Ice Class:</span>
                    <span className="text-white">{vesselData.capabilities.ice_class}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Speed:</span>
                    <span className="text-white">{vesselData.capabilities.speed_knots} kts</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Position:</span>
                    <span className="text-white">{vesselData.position.lon.toFixed(2)}, {vesselData.position.lat.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Iceberg Monitoring Card */}
            {icebergData && (
              <div className="glass-panel rounded-lg p-4">
                <h3 className="text-sm font-semibold text-cyan-400 mb-3 flex items-center">
                  <span className="mr-2">◆</span> ICEBERG MONITORING
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Detected:</span>
                    <span className="text-white">{icebergData.icebergs.length}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-700/50">
                    <p className="text-xs text-yellow-500">⚠ DEMO / SIMULATED DATA</p>
                    <p className="text-xs text-slate-500 mt-1">Trajectory Prediction: NEXT DEVELOPMENT</p>
                  </div>
                </div>
              </div>
            )}

            {/* Route Objectives */}
            <div className="glass-panel rounded-lg p-4">
              <h3 className="text-sm font-semibold text-purple-400 mb-3 flex items-center">
                <span className="mr-2">⚖️</span> ROUTE OBJECTIVES
              </h3>
              <ObjectiveSliders
                objectives={objectives}
                onChange={setObjectives}
              />
            </div>

            {/* Route Control */}
            <div className="glass-panel rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-400 mb-3 flex items-center">
                <span className="mr-2">🗺️</span> ROUTE CONTROL
              </h3>
              
              <div className="space-y-3">
                {/* Start Point */}
                <div>
                  <p className="text-xs text-slate-400 mb-1">START</p>
                  {startPoint ? (
                    <p className="text-sm text-white font-mono">
                      {startPoint.lon.toFixed(2)}°, {startPoint.lat.toFixed(2)}°
                    </p>
                  ) : (
                    <p className="text-sm text-slate-500">Click map to select</p>
                  )}
                </div>

                {/* Destination Point */}
                <div>
                  <p className="text-xs text-slate-400 mb-1">DESTINATION</p>
                  {endPoint ? (
                    <p className="text-sm text-white font-mono">
                      {endPoint.lon.toFixed(2)}°, {endPoint.lat.toFixed(2)}°
                    </p>
                  ) : (
                    <p className="text-sm text-slate-500">
                      {startPoint ? 'Click map to select' : 'Select start first'}
                    </p>
                  )}
                </div>

                {/* Buttons */}
                <div className="space-y-2 pt-2">
                  <button
                    onClick={handleCalculateRoute}
                    disabled={!startPoint || !endPoint}
                    className="w-full py-2 px-4 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-blue-600 hover:bg-blue-500 text-white"
                  >
                    CALCULATE A* ROUTE
                  </button>
                  <button
                    onClick={handleClearRoute}
                    className="w-full py-2 px-4 rounded font-medium transition-colors bg-slate-700 hover:bg-slate-600 text-white"
                  >
                    RESET
                  </button>
                </div>
              </div>
            </div>

            {/* Route Analysis */}
            <RiskPanel routeData={routeData} />
            
            {routeData && (
              <RouteSummary routeData={routeData} />
            )}

            {/* Alerts */}
            <div className="glass-panel rounded-lg p-4">
              <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center">
                <span className="mr-2">🚨</span> ALERTS
              </h3>
              <div className="flex items-center space-x-2 mb-3">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-xs text-slate-400">
                  {wsConnected ? 'ALERT STREAM CONNECTED' : 'ALERT STREAM DISCONNECTED'}
                </span>
              </div>
              <AlertPanel
                alerts={alerts}
                onTriggerDemoAlert={handleTriggerDemoAlert}
              />
            </div>

            {/* Data Status Footer */}
            <div className="glass-panel rounded-lg p-4 text-xs">
              <h4 className="font-semibold text-slate-300 mb-2">DATA & PROTOTYPE STATUS</h4>
              <div className="space-y-1">
                <div className="flex items-center text-green-400">
                  <span className="mr-2">✓</span>
                  <span>NOAA/NSIDC G02202 V6 Sea-Ice Concentration</span>
                </div>
                <div className="flex items-center text-yellow-500">
                  <span className="mr-2">•</span>
                  <span>Iceberg records (Demo)</span>
                </div>
                <div className="flex items-center text-yellow-500">
                  <span className="mr-2">•</span>
                  <span>Bathymetry (Demo)</span>
                </div>
                <div className="flex items-center text-yellow-500">
                  <span className="mr-2">•</span>
                  <span>SAR alert (Demo)</span>
                </div>
                <div className="pt-2 border-t border-slate-700/50 mt-2 text-slate-500">
                  <div className="flex items-center">
                    <span className="mr-2">→</span>
                    <span>Iceberg trajectory prediction (Next Development)</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">→</span>
                    <span>Advanced sea-ice forecasting (Next Development)</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">→</span>
                    <span>Real SAR/Sentinel-1 integration (Next Development)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
