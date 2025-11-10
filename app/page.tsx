'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import PanoramaViewer from '@/components/PanoramaViewer'
import WorldViewer3D from '@/components/WorldViewer3D'
import GenerationControls from '@/components/GenerationControls'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface GeneratedImage {
  id: string
  prompt: string
  image_url: string
  created_at: string
  scenario: string
}

interface World3D {
  id: string
  image_id: string
  world_url: string
  created_at: string
  scenario: string
}

export default function Home() {
  const [images, setImages] = useState<GeneratedImage[]>([])
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null)
  const [worlds, setWorlds] = useState<World3D[]>([])
  const [currentWorld, setCurrentWorld] = useState<World3D | null>(null)
  const [viewMode, setViewMode] = useState<'panorama' | '3d'>('panorama')
  const [loading, setLoading] = useState(false)
  const [loading3D, setLoading3D] = useState(false)
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

  const pollJobStatus = async (jobId: string): Promise<any> => {
    const maxAttempts = 180 // 3 minutes max (180 * 1s)
    let attempts = 0

    while (attempts < maxAttempts) {
      try {
        const response = await axios.get(`${API_URL}/api/jobs/${jobId}`, { timeout: 5000 })
        const job = response.data

        if (job.status === 'completed') {
          return job.result
        } else if (job.status === 'failed') {
          throw new Error(job.error || 'Generation failed')
        }

        // Still processing, wait and try again
        await new Promise(resolve => setTimeout(resolve, 1000))
        attempts++
      } catch (err: any) {
        if (err.response?.status === 404) {
          throw new Error('Job not found')
        }
        throw err
      }
    }

    throw new Error('Generation timed out after 3 minutes')
  }

  const generateImage = async (scenario?: string) => {
    setLoading(true)
    setError(null)

    try {
      // Start generation (returns immediately with job ID)
      const response = await axios.post(`${API_URL}/api/generate`, {
        scenario: scenario || 'random'
      }, {
        timeout: 10000 // 10 seconds for job creation
      })

      const job = response.data
      console.log('Generation started, job ID:', job.job_id)

      // Poll for completion
      const newImage = await pollJobStatus(job.job_id)

      setImages([newImage, ...images])
      setCurrentImage(newImage)
      setApiStatus('online')
    } catch (err: any) {
      console.error('Error generating image:', err)

      let errorMessage = 'Failed to generate image. '

      if (err.code === 'ECONNABORTED') {
        errorMessage += 'Request timed out.'
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

  const generate3DWorld = async () => {
    if (!currentImage) {
      setError('Please generate a panorama first')
      return
    }

    setLoading3D(true)
    setError(null)

    try {
      // Start 3D generation (returns immediately with job ID)
      const response = await axios.post(`${API_URL}/api/generate-3d`, {
        image_id: currentImage.id
      }, {
        timeout: 10000
      })

      const job = response.data
      console.log('3D generation started, job ID:', job.job_id)

      // Poll for completion
      const newWorld = await pollJobStatus(job.job_id)

      setWorlds([newWorld, ...worlds])
      setCurrentWorld(newWorld)
      setViewMode('3d')
      setApiStatus('online')
    } catch (err: any) {
      console.error('Error generating 3D world:', err)

      let errorMessage = 'Failed to generate 3D world. '

      if (err.code === 'ECONNABORTED') {
        errorMessage += 'Request timed out.'
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        errorMessage += `Cannot reach API at ${API_URL}. Check connection.`
        setApiStatus('offline')
      } else if (err.response) {
        errorMessage += `Server error (${err.response.status}): ${err.response.data?.detail || err.response.statusText}`
      } else {
        errorMessage += err.message
      }

      setError(errorMessage)
      checkApiHealth()
    } finally {
      setLoading3D(false)
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
            {/* View Mode Toggle */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setViewMode('panorama')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === 'panorama'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                }`}
              >
                360° Panorama
              </button>
              <button
                onClick={() => setViewMode('3d')}
                disabled={!currentWorld}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === '3d'
                    ? 'bg-blue-600 text-white'
                    : currentWorld
                    ? 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    : 'bg-slate-700 text-gray-500 cursor-not-allowed'
                }`}
              >
                3D World
              </button>
              {viewMode === 'panorama' && currentImage && (
                <button
                  onClick={generate3DWorld}
                  disabled={loading3D}
                  className="ml-auto px-4 py-2 rounded-lg font-medium bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition"
                >
                  {loading3D ? 'Generating 3D World...' : '🌍 Generate 3D World'}
                </button>
              )}
            </div>

            <div className="bg-slate-800 rounded-lg overflow-hidden shadow-2xl">
              {viewMode === 'panorama' ? (
                <>
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
                </>
              ) : (
                <>
                  {currentWorld ? (
                    <WorldViewer3D worldUrl={currentWorld.world_url} className="aspect-[2/1]" />
                  ) : (
                    <div className="aspect-[2/1] flex items-center justify-center bg-slate-700">
                      <p className="text-gray-400">No 3D worlds generated yet</p>
                    </div>
                  )}

                  {currentWorld && (
                    <div className="p-4 bg-slate-900">
                      <h3 className="text-lg font-semibold text-white mb-2">
                        {currentWorld.scenario} - 3D World
                      </h3>
                      <p className="text-sm text-gray-400">
                        Explore the 3D environment using mouse controls
                      </p>
                    </div>
                  )}
                </>
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
