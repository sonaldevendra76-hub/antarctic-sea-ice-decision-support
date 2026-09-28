import React from 'react'
import { RouteData } from '../types'

interface RiskPanelProps {
  routeData: RouteData | null
}

const RiskPanel: React.FC<RiskPanelProps> = ({ routeData }) => {
  if (!routeData) {
    return (
      <div className="glass-panel rounded-lg p-4">
        <h3 className="text-sm font-semibold text-purple-400 mb-3 flex items-center">
          <span className="mr-2">📊</span> A* ROUTE ANALYSIS
        </h3>
        <p className="text-sm text-slate-400">Calculate a route to see analysis</p>
      </div>
    )
  }

  const { summary, metadata } = routeData

  return (
    <div className="glass-panel rounded-lg p-4">
      <h3 className="text-sm font-semibold text-purple-400 mb-3 flex items-center">
        <span className="mr-2">📊</span> A* ROUTE ANALYSIS
      </h3>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Total Risk Score</span>
            <span className={summary.total_risk_score > 0.5 ? 'text-red-400' : 'text-green-400'}>
              {(summary.total_risk_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                summary.total_risk_score > 0.5 ? 'bg-red-500' : 'bg-green-500'
              }`}
              style={{ width: `${summary.total_risk_score * 100}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="bg-slate-800/50 p-2 rounded text-center">
            <p className="text-slate-400 text-xs">Distance</p>
            <p className="font-medium">{summary.total_distance_nm.toFixed(0)} nm</p>
          </div>
          <div className="bg-slate-800/50 p-2 rounded text-center">
            <p className="text-slate-400 text-xs">Duration</p>
            <p className="font-medium">{summary.estimated_duration_hours.toFixed(1)}h</p>
          </div>
          <div className="bg-slate-800/50 p-2 rounded text-center">
            <p className="text-slate-400 text-xs">Fuel</p>
            <p className="font-medium">{summary.fuel_consumption_liters.toFixed(0)}L</p>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-700/50 space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Algorithm:</span>
            <span className="text-blue-400">{routeData.algorithm}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Data Basis:</span>
            <span className={metadata.data_source === 'real' ? 'text-green-400' : 'text-yellow-500'}>
              {metadata.data_source === 'real' ? 'Real Sea-Ice' : 'Demo'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskPanel
