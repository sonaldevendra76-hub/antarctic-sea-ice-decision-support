import {
  VesselData,
  ForecastData,
  IcebergData,
  RouteData,
  RouteRequest
} from '../types'

const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000'

class Api {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}/api${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      }
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  async getVessel(): Promise<VesselData> {
    return this.request<VesselData>('/vessel')
  }

  async getForecast(timestep: number = 0, bounds?: string): Promise<ForecastData> {
    const params = new URLSearchParams({ timestep: timestep.toString() })
    if (bounds) {
      params.append('bounds', bounds)
    }
    return this.request<ForecastData>(`/forecast?${params.toString()}`)
  }

  async getIcebergs(bounds?: string, minSize?: number): Promise<IcebergData> {
    const params = new URLSearchParams()
    if (bounds) {
      params.append('bounds', bounds)
    }
    if (minSize !== undefined) {
      params.append('min_size', minSize.toString())
    }
    return this.request<IcebergData>(`/icebergs?${params.toString()}`)
  }

  async calculateRoute(request: RouteRequest): Promise<RouteData> {
    return this.request<RouteData>('/route', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  connectAlerts(): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/api/ws/alerts'
    return new WebSocket(wsUrl)
  }

  async triggerDemoAlert(type: string): Promise<void> {
    const ws = this.connectAlerts()
    ws.onopen = () => {
      ws.send(JSON.stringify({ action: 'trigger_demo_alert', alert_type: type }))
      ws.close()
    }
  }
}

export const api = new Api(API_BASE_URL)
