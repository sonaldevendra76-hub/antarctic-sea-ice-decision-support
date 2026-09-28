import React from 'react'
import { RouteData } from '../types'

interface RouteSummaryProps {
  routeData: RouteData
}

const RouteSummary: React.FC<RouteSummaryProps> = ({ routeData }) => {
  const { summary, algorithm, metadata, waypoints } = routeData

  return (
    <div className="glass-panel rounded-lg p-4">
      <h3 className="text-sm font-semibold text-green-400 mb-3 flex items-center">
        <span className="mr-2">✓</span> ROUTE SUMMARY
      </h3>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-slate-800/50 p-2 rounded">
            <p className="text-slate-400 text-xs">Distance</p>
            <p className="font-medium">{summary.total_distance_nm.toFixed(1)} nm</p>
          </div>
          <div className="bg-slate-800/50 p-2 rounded">
            <p className="text-slate-400 text-xs">Duration</p>
            <p className="font-medium">{summary.estimated_duration_hours.toFixed(1)} hrs</p>
          </div>
          <div className="bg-slate-800/50 p-2 rounded">
            <p className="text-slate-400 text-xs">Fuel</p>
            <p className="font-medium">{summary.fuel_consumption_liters.toFixed(0)} L</p>
          </div>
          <div className="bg-slate-800/50 p-2 rounded">
            <p className="text-slate-400 text-xs">Risk</p>
            <p className="font-medium">{(summary.total_risk_score * 100).toFixed(0)}%</p>
          </div>
        </div>

        <div className="text-sm space-y-1">
          <div className="flex justify-between">
            <span className="text-slate-400">Waypoints:</span>
            <span>{waypoints.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Algorithm:</span>
            <span className="text-blue-400">{algorithm}</span>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-700/50">
          <p className="text-xs font-medium mb-1 text-slate-300">Data Source</p>
          <p className={`text-xs ${metadata.data_source === 'real' ? 'text-green-400' : 'text-yellow-500'}`}>
            {metadata.data_source === 'real' ? '✓ Real NOAA/NSIDC G02202' : 'Demo/Simulated'}
          </p>
          {metadata.data_source === 'real' && metadata.dataset && (
            <p className="text-xs text-slate-500 mt-1">{metadata.dataset}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default RouteSummary
