import React from 'react'

interface ForecastSliderProps {
  value: number
  onChange: (value: number) => void
}

const ForecastSlider: React.FC<ForecastSliderProps> = ({ value, onChange }) => {
  return (
    <div className="glass-panel rounded-lg p-4">
      <h3 className="text-sm font-semibold text-blue-400 mb-3 flex items-center">
        <span className="mr-2">📅</span> FORECAST TIMESTEP
      </h3>
      <div className="flex items-center space-x-4">
        <input
          type="range"
          min="0"
          max="10"
          step="1"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="flex-1 accent-blue-500"
        />
        <span className="text-sm text-white w-12 text-right font-medium">T-{value}</span>
      </div>
      <p className="text-xs text-slate-500 mt-2">
        Current dataset: Single timestep available
      </p>
    </div>
  )
}

export default ForecastSlider
