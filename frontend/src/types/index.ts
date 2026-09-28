export interface Coordinates {
  lon: number
  lat: number
}

export interface VesselCapabilities {
  ice_class: string
  max_ice_thickness: number
  speed_knots: number
}

export interface VesselData {
  id: string
  name: string
  position: Coordinates
  capabilities: VesselCapabilities
  status: string
}

export interface RouteObjectives {
  minimize_time: number
  minimize_risk: number
  minimize_fuel: number
}

export interface Waypoint {
  lon: number
  lat: number
  estimated_arrival: string
  risk_score: number
}

export interface RouteSummary {
  total_distance_nm: number
  estimated_duration_hours: number
  total_risk_score: number
  fuel_consumption_liters: number
}

export interface RouteData {
  route_id: string
  waypoints: Waypoint[]
  summary: RouteSummary
  algorithm: string
  cost_function: string
  metadata: {
    forecast_timestep: number
    data_source: string
    note?: string
    dataset?: string
  }
}

export interface IcebergSize {
  length_m: number
  width_m: number
  height_m: number
}

export interface DriftVelocity {
  east_knots: number
  north_knots: number
}

export interface Iceberg {
  id: string
  position: Coordinates
  size: IcebergSize
  drift_velocity: DriftVelocity
}

export interface IcebergData {
  timestamp: string
  icebergs: Iceberg[]
  metadata: {
    source: string
    note?: string
  }
}

export interface GridBounds {
  min_lon: number
  min_lat: number
  max_lon: number
  max_lat: number
}

export interface ForecastGrid {
  bounds: GridBounds
  resolution: number
  ice_concentration: number[][]
  ice_thickness: number[][]
}

export interface ForecastMetadata {
  source: string
  dataset?: string
  doi?: string
  resolution?: string
  date?: string
  ice_thickness_source?: string
  ice_thickness_note?: string
}

export interface ForecastData {
  timestep: number
  timestamp: string
  grid: ForecastGrid
  metadata: ForecastMetadata
}

export interface AlertData {
  alert_id: string
  severity: string
  position: Coordinates
  message: string
  vessel_in_range?: boolean
  [key: string]: any
}

export interface Alert {
  type: string
  timestamp: string
  data: AlertData
}

export interface RouteRequest {
  start: Coordinates
  end: Coordinates
  vessel_config: VesselCapabilities
  objectives: RouteObjectives
  forecast_timestep: number
}
