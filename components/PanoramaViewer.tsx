'use client'

import { useEffect, useRef } from 'react'

interface PanoramaViewerProps {
  imageUrl: string
}

export default function PanoramaViewer({ imageUrl }: PanoramaViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const isDraggingRef = useRef(false)
  const lastXRef = useRef(0)
  const rotationRef = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const updateSize = () => {
      const rect = container.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
    }
    updateSize()
    window.addEventListener('resize', updateSize)

    // Load image
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = imageUrl

    img.onload = () => {
      renderPanorama()
    }

    const renderPanorama = () => {
      if (!ctx || !canvas) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Simple panorama rendering with horizontal scrolling
      const imgWidth = img.width
      const imgHeight = img.height

      // Calculate dimensions to maintain aspect ratio
      const scale = canvas.height / imgHeight
      const scaledWidth = imgWidth * scale

      // Draw the image with rotation offset
      const offsetX = (rotationRef.current % scaledWidth)

      // Draw twice for seamless looping
      ctx.drawImage(img, -offsetX, 0, scaledWidth, canvas.height)
      ctx.drawImage(img, scaledWidth - offsetX, 0, scaledWidth, canvas.height)
    }

    // Mouse/touch controls
    const handleStart = (x: number) => {
      isDraggingRef.current = true
      lastXRef.current = x
    }

    const handleMove = (x: number) => {
      if (!isDraggingRef.current) return

      const deltaX = x - lastXRef.current
      rotationRef.current += deltaX
      lastXRef.current = x

      renderPanorama()
    }

    const handleEnd = () => {
      isDraggingRef.current = false
    }

    // Mouse events
    canvas.addEventListener('mousedown', (e) => handleStart(e.clientX))
    canvas.addEventListener('mousemove', (e) => handleMove(e.clientX))
    canvas.addEventListener('mouseup', handleEnd)
    canvas.addEventListener('mouseleave', handleEnd)

    // Touch events
    canvas.addEventListener('touchstart', (e) => {
      e.preventDefault()
      handleStart(e.touches[0].clientX)
    })
    canvas.addEventListener('touchmove', (e) => {
      e.preventDefault()
      handleMove(e.touches[0].clientX)
    })
    canvas.addEventListener('touchend', handleEnd)

    // Auto-rotate (optional)
    let autoRotate: number
    const startAutoRotate = () => {
      autoRotate = window.setInterval(() => {
        if (!isDraggingRef.current) {
          rotationRef.current += 0.5
          renderPanorama()
        }
      }, 16)
    }
    startAutoRotate()

    return () => {
      window.removeEventListener('resize', updateSize)
      clearInterval(autoRotate)
    }
  }, [imageUrl])

  return (
    <div ref={containerRef} className="relative w-full aspect-[2/1] bg-black">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-grab active:cursor-grabbing"
      />
      <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded text-sm">
        Drag to look around
      </div>
    </div>
  )
}
