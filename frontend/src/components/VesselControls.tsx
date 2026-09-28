import React from 'react'
import { VesselData } from '../types'

interface VesselControlsProps {
  vesselData: VesselData | null
}

const VesselControls: React.FC<VesselControlsProps> = ({ vesselData }) => {
  if (!vesselData) {
    return (
      <div className="glass-panel rounded-lg p-4">
        <h3 className="text-sm font-semibold text-orange-400 mb-3 flex items-center">
          <span className="mr-2">🚢</span> VESSEL STATUS
        </h3>
        <p className="text-sm text-slate-400">Loading vessel data...</p>
      </div>
    )
  }

  return (
    <div className="glass-panel rounded-lg p-4">
      <h3 className="text-sm font-semibold text-orange-400 mb-3 flex items-center">
        <span className="mr-2">🚢</span> VESSEL STATUS
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
  )
}

export default VesselControls
