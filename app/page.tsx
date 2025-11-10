'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import PanoramaViewer from '@/components/PanoramaViewer'
import GenerationControls from '@/components/GenerationControls'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface GeneratedImage {
  id: string
  prompt: string
  image_url: string
  created_at: string
  scenario: string
}

export default function Home() {
  const [images, setImages] = useState<GeneratedImage[]>([])
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [showDebug, setShowDebug] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>('')

  // Check API status on load
  useEffect(() => {
    checkApiHealth()
    fetchImages()
  }, [])

  const checkApiHealth = async () => {
    setApiStatus('checking')
    try {
      const response = await axios.get(`${API_URL}/api/health`, { timeout: 5000 })
      setApiStatus('online')
      setDebugInfo(`✅ API Connected\nURL: ${API_URL}\nStatus: ${JSON.stringify(response.data, null, 2)}`)
    } catch (err: any) {
      setApiStatus('offline')
      let errorDetails = `❌ API Connection Failed\nURL: ${API_URL}\n\n`

      if (err.code === 'ECONNABORTED') {
        errorDetails += 'Error: Request timeout (5s)\n'
      } else if (err.code === 'ERR_NETWORK') {
        errorDetails += 'Error: Network error - Cannot reach API\n'
      } else if (err.response) {
        errorDetails += `Error: Server responded with ${err.response.status}\n`
        errorDetails += `Response: ${JSON.stringify(err.response.data, null, 2)}\n`
      } else if (err.request) {
        errorDetails += 'Error: No response from server\n'
        errorDetails += 'Possible causes:\n'
        errorDetails += '- RunPod API not running\n'
        errorDetails += '- Wrong API URL in Vercel env\n'
        errorDetails += '- CORS issues\n'
      } else {
        errorDetails += `Error: ${err.message}\n`
      }

      setDebugInfo(errorDetails)
    }
  }

  const fetchImages = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/images`)
      setImages(response.data)
      if (response.data.length > 0 && !currentImage) {
        setCurrentImage(response.data[0])
      }
    } catch (err) {
      console.error('Error fetching images:', err)
      setError('Failed to fetch images')
    }
  }

  const generateImage = async (scenario?: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/api/generate`, {
        scenario: scenario || 'random'
      }, {
        timeout: 300000 // 5 minutes for image generation
      })

      const newImage = response.data
      setImages([newImage, ...images])
      setCurrentImage(newImage)
      setApiStatus('online')
    } catch (err: any) {
      console.error('Error generating image:', err)

      let errorMessage = 'Failed to generate image. '

      if (err.code === 'ECONNABORTED') {
        errorMessage += 'Request timed out after 5 minutes.'
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        errorMessage += `Cannot reach API at ${API_URL}. Check connection.`
        setApiStatus('offline')
      } else if (err.response) {
        errorMessage += `Server error (${err.response.status}): ${err.response.data?.detail || err.response.statusText}`
      } else {
        errorMessage += err.message
      }

      setError(errorMessage)
      checkApiHealth() // Recheck connection
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            Island Survival
          </h1>
          <p className="text-xl text-gray-300">
            Immersive 360° Panoramic Survival Scenarios
          </p>

          {/* API Status Indicator */}
          <div className="mt-4 flex items-center justify-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                apiStatus === 'online' ? 'bg-green-500 animate-pulse' :
                apiStatus === 'offline' ? 'bg-red-500' :
                'bg-yellow-500 animate-pulse'
              }`} />
              <span className="text-sm text-gray-400">
                API: {apiStatus === 'online' ? 'Connected' : apiStatus === 'offline' ? 'Disconnected' : 'Checking...'}
              </span>
            </div>

            <button
              onClick={checkApiHealth}
              className="text-xs text-blue-400 hover:text-blue-300 underline"
            >
              Test Connection
            </button>

            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-xs text-gray-500 hover:text-gray-400 underline"
            >
              {showDebug ? 'Hide' : 'Show'} Debug Info
            </button>
          </div>
        </header>

        {/* Debug Panel */}
        {showDebug && (
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 mb-6 font-mono text-xs">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-white font-semibold">Debug Information</h3>
              <button
                onClick={() => navigator.clipboard.writeText(debugInfo)}
                className="text-blue-400 hover:text-blue-300 text-xs"
              >
                Copy
              </button>
            </div>
            <pre className="text-gray-300 whitespace-pre-wrap">{debugInfo}</pre>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-6">
            <div className="flex justify-between items-start">
              <div>{error}</div>
              <button
                onClick={() => setShowDebug(true)}
                className="text-xs underline ml-4"
              >
                Debug
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main viewer */}
          <div className="lg:col-span-3">
            <div className="bg-slate-800 rounded-lg overflow-hidden shadow-2xl">
              {currentImage ? (
                <PanoramaViewer imageUrl={currentImage.image_url} />
              ) : (
                <div className="aspect-[2/1] flex items-center justify-center bg-slate-700">
                  <p className="text-gray-400">No panoramas generated yet</p>
                </div>
              )}

              {currentImage && (
                <div className="p-4 bg-slate-900">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {currentImage.scenario}
                  </h3>
                  <p className="text-sm text-gray-400">{currentImage.prompt}</p>
                </div>
              )}
            </div>
          </div>

          {/* Controls and gallery */}
          <div className="lg:col-span-1">
            <GenerationControls
              onGenerate={generateImage}
              loading={loading}
              apiStatus={apiStatus}
            />

            {/* Gallery */}
            <div className="mt-6 bg-slate-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Gallery</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {images.map((img) => (
                  <button
                    key={img.id}
                    onClick={() => setCurrentImage(img)}
                    className={`w-full text-left p-3 rounded transition ${
                      currentImage?.id === img.id
                        ? 'bg-blue-600'
                        : 'bg-slate-700 hover:bg-slate-600'
                    }`}
                  >
                    <p className="text-sm font-medium text-white truncate">
                      {img.scenario}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(img.created_at).toLocaleDateString()}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
