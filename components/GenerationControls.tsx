'use client'

import { useState } from 'react'

interface GenerationControlsProps {
  onGenerate: (scenario?: string) => void
  loading: boolean
}

const SCENARIOS = [
  { id: 'random', name: 'Random', icon: '🎲' },
  { id: 'beach', name: 'Beach Landing', icon: '🏖️' },
  { id: 'jungle', name: 'Dense Jungle', icon: '🌴' },
  { id: 'mountain', name: 'Mountain Peak', icon: '⛰️' },
  { id: 'cave', name: 'Dark Cave', icon: '🕳️' },
  { id: 'ruins', name: 'Ancient Ruins', icon: '🏛️' },
  { id: 'storm', name: 'Stormy Weather', icon: '⛈️' },
  { id: 'sunset', name: 'Sunset View', icon: '🌅' },
  { id: 'night', name: 'Night Sky', icon: '🌙' },
]

export default function GenerationControls({
  onGenerate,
  loading,
}: GenerationControlsProps) {
  const [selectedScenario, setSelectedScenario] = useState('random')

  const handleGenerate = () => {
    onGenerate(selectedScenario)
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-white mb-4">
        Generate Panorama
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Scenario
          </label>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="w-full bg-slate-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            {SCENARIOS.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.icon} {scenario.name}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold py-3 px-4 rounded transition"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin h-5 w-5 mr-2"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating...
            </span>
          ) : (
            'Generate'
          )}
        </button>

        <div className="text-xs text-gray-400 mt-2">
          {loading ? (
            <p>This may take 1-2 minutes depending on GPU...</p>
          ) : (
            <p>Click to generate a new 360° panoramic scene</p>
          )}
        </div>
      </div>
    </div>
  )
}
