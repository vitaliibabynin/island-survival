'use client'

import { Suspense, useRef, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, useGLTF, PerspectiveCamera, Sky, Environment } from '@react-three/drei'
import * as THREE from 'three'

interface WorldModelProps {
  url: string
}

function WorldModel({ url }: WorldModelProps) {
  const gltf = useGLTF(url)
  const modelRef = useRef<THREE.Group>(null)

  useEffect(() => {
    if (modelRef.current) {
      // Center and scale the model
      const box = new THREE.Box3().setFromObject(modelRef.current)
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())

      // Center the model
      modelRef.current.position.sub(center)

      // Scale to reasonable size (optional)
      const maxDim = Math.max(size.x, size.y, size.z)
      if (maxDim > 50) {
        const scale = 50 / maxDim
        modelRef.current.scale.setScalar(scale)
      }
    }
  }, [gltf])

  return <primitive ref={modelRef} object={gltf.scene} />
}

function LoadingBox() {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.3
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.4
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#4299e1" wireframe />
    </mesh>
  )
}

interface WorldViewer3DProps {
  worldUrl: string
  className?: string
}

export default function WorldViewer3D({ worldUrl, className = '' }: WorldViewer3DProps) {
  return (
    <div className={`relative ${className}`} style={{ minHeight: '500px' }}>
      <Canvas
        shadows
        camera={{ position: [0, 2, 10], fov: 60 }}
        style={{ background: '#1e293b' }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, 10, -10]} intensity={0.5} />

        {/* Environment and Sky */}
        <Sky sunPosition={[100, 20, 100]} />
        <Environment preset="sunset" />

        {/* 3D World Model */}
        <Suspense fallback={<LoadingBox />}>
          <WorldModel url={worldUrl} />
        </Suspense>

        {/* Ground plane for reference */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#2d3748" />
        </mesh>

        {/* Camera Controls */}
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={2}
          maxDistance={100}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>

      {/* Instructions overlay */}
      <div className="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur-sm text-white px-4 py-3 rounded-lg text-sm">
        <div className="font-semibold mb-2">Controls</div>
        <div className="space-y-1 text-xs text-gray-300">
          <div>🖱️ Left Click + Drag: Rotate view</div>
          <div>🖱️ Right Click + Drag: Pan camera</div>
          <div>🖱️ Scroll: Zoom in/out</div>
        </div>
      </div>
    </div>
  )
}

// Preload the GLTF model
useGLTF.preload = (url: string) => {
  useGLTF(url)
}
