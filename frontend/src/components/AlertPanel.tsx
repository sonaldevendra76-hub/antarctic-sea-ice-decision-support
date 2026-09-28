import React from 'react'
import { Alert } from '../types'

interface AlertPanelProps {
  alerts: Alert[]
  onTriggerDemoAlert: (type: string) => void
}

const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, onTriggerDemoAlert }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'warning':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'moderate':
        return 'text-orange-400 bg-orange-400/10 border-orange-400/20'
      default:
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20'
    }
  }

  return (
    <div>
      <div className="space-y-2 mb-4">
        <button
          onClick={() => onTriggerDemoAlert('sar_alert')}
          className="w-full px-3 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-sm transition-colors border border-slate-600/50"
        >
          Trigger Demo SAR Alert
        </button>
        <button
          onClick={() => onTriggerDemoAlert('ice_hazard')}
          className="w-full px-3 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-sm transition-colors border border-slate-600/50"
        >
          Trigger Demo Ice Hazard
        </button>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {alerts.length === 0 ? (
          <p className="text-sm text-slate-400">No alerts</p>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={index}
              className={`p-3 rounded border ${getSeverityColor(alert.data.severity)}`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-xs font-medium uppercase">
                  {alert.type.replace('_', ' ')}
                </span>
                <span className="text-xs text-slate-500">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm mb-2">{alert.data.message}</p>
              {alert.data.position && (
                <p className="text-xs text-slate-500">
                  Position: {alert.data.position.lon.toFixed(2)}, {alert.data.position.lat.toFixed(2)}
                </p>
              )}
              <p className="text-xs text-yellow-500 mt-1">
                ⚠ DEMO/SIMULATED DATA
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AlertPanel
