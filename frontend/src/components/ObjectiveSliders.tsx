import React from 'react'
import { RouteObjectives } from '../types'

interface ObjectiveSlidersProps {
  objectives: RouteObjectives
  onChange: (objectives: RouteObjectives) => void
}

const ObjectiveSliders: React.FC<ObjectiveSlidersProps> = ({ objectives, onChange }) => {
  const handleChange = (key: keyof RouteObjectives, value: number) => {
    const newObjectives = { ...objectives, [key]: value }
    // Normalize to sum to 1
    const total = Object.values(newObjectives).reduce((a: number, b: number) => a + b, 0)
    const normalized: RouteObjectives = {
      minimize_time: newObjectives.minimize_time / total,
      minimize_risk: newObjectives.minimize_risk / total,
      minimize_fuel: newObjectives.minimize_fuel / total
    }
    onChange(normalized)
  }

  return (
    <div className="bg-slate-800 p-4 rounded-lg shadow-lg">
      <h3 className="font-medium mb-3">Route Objectives</h3>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Minimize Time</span>
            <span>{(objectives.minimize_time * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={objectives.minimize_time}
            onChange={(e) => handleChange('minimize_time', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Minimize Risk</span>
            <span>{(objectives.minimize_risk * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={objectives.minimize_risk}
            onChange={(e) => handleChange('minimize_risk', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Minimize Fuel</span>
            <span>{(objectives.minimize_fuel * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={objectives.minimize_fuel}
            onChange={(e) => handleChange('minimize_fuel', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
      <p className="text-xs text-slate-500 mt-3">
        Adjusting objectives will affect new route calculations
      </p>
    </div>
  )
}

export default ObjectiveSliders
