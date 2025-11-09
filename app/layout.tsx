import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Island Survival - 360° Panoramic Experience',
  description: 'Explore survival scenarios in immersive 360° panoramic environments',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
