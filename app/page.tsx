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

  // Fetch existing images on load
  useEffect(() => {
    fetchImages()
  }, [])

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
      })

      const newImage = response.data
      setImages([newImage, ...images])
      setCurrentImage(newImage)
    } catch (err) {
      console.error('Error generating image:', err)
      setError('Failed to generate image. Make sure the RunPod API is running.')
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
        </header>

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-6">
            {error}
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
