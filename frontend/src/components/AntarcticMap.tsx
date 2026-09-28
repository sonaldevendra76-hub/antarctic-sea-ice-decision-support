import React, { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import {
  ForecastData,
  VesselData,
  IcebergData,
  RouteData,
  Coordinates
} from '../types'

interface AntarcticMapProps {
  forecastData: ForecastData | null
  vesselData: VesselData | null
  icebergData: IcebergData | null
  routeData: RouteData | null
  startPoint: Coordinates | null
  endPoint: Coordinates | null
  onMapClick: (coords: Coordinates) => void
}

const AntarcticMap: React.FC<AntarcticMapProps> = ({
  forecastData,
  vesselData,
  icebergData,
  routeData,
  startPoint,
  endPoint,
  onMapClick
}) => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)

  // Wait until MapLibre style is completely ready
  const runWhenStyleLoaded = (
    callback: (mapInstance: maplibregl.Map) => void
  ) => {
    const mapInstance = map.current

    if (!mapInstance) return

    if (mapInstance.isStyleLoaded()) {
      callback(mapInstance)
      return
    }

    const handleStyleLoad = () => {
      if (map.current) {
        callback(map.current)
      }
    }

    mapInstance.once('style.load', handleStyleLoad)
  }

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: [0, -75],
      zoom: 3,
      attributionControl: false
    })

    // Custom dark navigation control
    const nav = new maplibregl.NavigationControl({
      showCompass: true,
      showZoom: true,
      visualizePitch: true
    })
    map.current.addControl(nav, 'top-right')

    // Add attribution at bottom right
    map.current.addControl(new maplibregl.AttributionControl({
      compact: true
    }), 'bottom-right')

    return () => {
      map.current?.remove()
      map.current = null
    }
  }, [])

  // Map click handler - properly managed with cleanup
  useEffect(() => {
    const mapInstance = map.current
    if (!mapInstance) return

    const handleClick = (e: maplibregl.MapMouseEvent) => {
      const point = {
        lon: e.lngLat.lng,
        lat: e.lngLat.lat
      }
      onMapClick(point)
    }

    mapInstance.on('click', handleClick)

    return () => {
      mapInstance.off('click', handleClick)
    }
  }, [onMapClick])

  // Render sea-ice concentration
  useEffect(() => {
    if (!forecastData) return

    runWhenStyleLoaded((mapInstance) => {
      const { grid } = forecastData
      const { bounds, ice_concentration } = grid

      if (mapInstance.getLayer('ice-concentration')) {
        mapInstance.removeLayer('ice-concentration')
      }

      if (mapInstance.getSource('ice-concentration')) {
        mapInstance.removeSource('ice-concentration')
      }

      const features: GeoJSON.Feature[] = []

      for (let y = 0; y < ice_concentration.length; y++) {
        for (let x = 0; x < ice_concentration[y].length; x++) {
          const concentration = ice_concentration[y][x]

          if (concentration > 0.1) {
            const lon =
              bounds.min_lon +
              (x / ice_concentration[y].length) *
                (bounds.max_lon - bounds.min_lon)

            const lat =
              bounds.min_lat +
              (y / ice_concentration.length) *
                (bounds.max_lat - bounds.min_lat)

            features.push({
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [lon, lat]
              },
              properties: {
                concentration
              }
            })
          }
        }
      }

      if (features.length === 0) return

      mapInstance.addSource('ice-concentration', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features
        }
      })

      mapInstance.addLayer({
        id: 'ice-concentration',
        type: 'circle',
        source: 'ice-concentration',
        paint: {
          'circle-radius': 2,
          'circle-color': [
            'interpolate',
            ['linear'],
            ['get', 'concentration'],
            0.1, '#3b82f6',
            0.5, '#8b5cf6',
            0.8, '#ef4444',
            1.0, '#ffffff'
          ],
          'circle-opacity': 0.6
        }
      })
    })
  }, [forecastData])

  // Render vessel
  useEffect(() => {
    if (!vesselData) return

    runWhenStyleLoaded((mapInstance) => {
      if (mapInstance.getLayer('vessel')) {
        mapInstance.removeLayer('vessel')
      }

      if (mapInstance.getSource('vessel')) {
        mapInstance.removeSource('vessel')
      }

      mapInstance.addSource('vessel', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [
              vesselData.position.lon,
              vesselData.position.lat
            ]
          },
          properties: {}
        }
      })

      mapInstance.addLayer({
        id: 'vessel',
        type: 'circle',
        source: 'vessel',
        paint: {
          'circle-radius': 8,
          'circle-color': '#f59e0b',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff'
        }
      })
    })
  }, [vesselData])

  // Render icebergs
  useEffect(() => {
    if (!icebergData) return

    runWhenStyleLoaded((mapInstance) => {
      if (mapInstance.getLayer('icebergs')) {
        mapInstance.removeLayer('icebergs')
      }

      if (mapInstance.getSource('icebergs')) {
        mapInstance.removeSource('icebergs')
      }

      const features: GeoJSON.Feature[] =
        icebergData.icebergs.map((iceberg) => ({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [
              iceberg.position.lon,
              iceberg.position.lat
            ]
          },
          properties: {
            id: iceberg.id,
            size: iceberg.size.length_m
          }
        }))

      mapInstance.addSource('icebergs', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features
        }
      })

      mapInstance.addLayer({
        id: 'icebergs',
        type: 'circle',
        source: 'icebergs',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['get', 'size'],
            0, 4,
            500, 8,
            1000, 14,
            2000, 20
          ],
          'circle-color': '#06b6d4',
          'circle-opacity': 0.8,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        }
      })
    })
  }, [icebergData])

  // Render route and markers
  useEffect(() => {
    runWhenStyleLoaded((mapInstance) => {
      // Remove old route
      if (mapInstance.getLayer('route')) {
        mapInstance.removeLayer('route')
      }

      if (mapInstance.getSource('route')) {
        mapInstance.removeSource('route')
      }

      // Remove old start marker
      if (mapInstance.getLayer('start-marker-label')) {
        mapInstance.removeLayer('start-marker-label')
      }
      if (mapInstance.getLayer('start-marker')) {
        mapInstance.removeLayer('start-marker')
      }
      if (mapInstance.getSource('start-marker')) {
        mapInstance.removeSource('start-marker')
      }

      // Remove old end marker
      if (mapInstance.getLayer('end-marker-label')) {
        mapInstance.removeLayer('end-marker-label')
      }
      if (mapInstance.getLayer('end-marker')) {
        mapInstance.removeLayer('end-marker')
      }
      if (mapInstance.getSource('end-marker')) {
        mapInstance.removeSource('end-marker')
      }

      // Start marker
      if (startPoint) {
        const startCoords = [startPoint.lon, startPoint.lat]

        mapInstance.addSource('start-marker', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: startCoords
            },
            properties: {
              label: 'START'
            }
          }
        })

        mapInstance.addLayer({
          id: 'start-marker',
          type: 'circle',
          source: 'start-marker',
          paint: {
            'circle-radius': 15,
            'circle-color': '#22c55e',
            'circle-stroke-width': 4,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 1,
            'circle-stroke-opacity': 1
          }
        })

        // Add text label for START
        mapInstance.addLayer({
          id: 'start-marker-label',
          type: 'symbol',
          source: 'start-marker',
          layout: {
            'text-field': 'START',
            'text-size': 14,
            'text-anchor': 'top',
            'text-offset': [0, 1]
          },
          paint: {
            'text-color': '#ffffff',
            'text-halo-color': '#000000',
            'text-halo-width': 2
          }
        })
      }

      // End marker
      if (endPoint) {
        const endCoords = [endPoint.lon, endPoint.lat]

        mapInstance.addSource('end-marker', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: endCoords
            },
            properties: {
              label: 'DESTINATION'
            }
          }
        })

        mapInstance.addLayer({
          id: 'end-marker',
          type: 'circle',
          source: 'end-marker',
          paint: {
            'circle-radius': 15,
            'circle-color': '#ef4444',
            'circle-stroke-width': 4,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 1,
            'circle-stroke-opacity': 1
          }
        })

        // Add text label for DESTINATION
        mapInstance.addLayer({
          id: 'end-marker-label',
          type: 'symbol',
          source: 'end-marker',
          layout: {
            'text-field': 'DESTINATION',
            'text-size': 14,
            'text-anchor': 'top',
            'text-offset': [0, 1]
          },
          paint: {
            'text-color': '#ffffff',
            'text-halo-color': '#000000',
            'text-halo-width': 2
          }
        })
      }

      // Route
      if (routeData?.waypoints?.length) {
        const coordinates = routeData.waypoints.map(
          (wp) => [wp.lon, wp.lat] as [number, number]
        )

        mapInstance.addSource('route', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: {
              type: 'LineString',
              coordinates
            },
            properties: {}
          }
        })

        mapInstance.addLayer({
          id: 'route',
          type: 'line',
          source: 'route',
          paint: {
            'line-color': '#3b82f6',
            'line-width': 4
          }
        })
      }
    })
  }, [startPoint, endPoint, routeData])

  return (
    <div
      ref={mapContainer}
      className="w-full h-full min-h-[500px]"
    />
  )
}

export default AntarcticMap