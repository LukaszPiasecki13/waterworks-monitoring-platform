import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { DashboardPage } from './DashboardPage'

// Mock the telemetry hook
vi.mock('@/hooks/useTelemetryApi', () => ({
  useTelemetryObjects: () => ({
    data: {
      items: [
        {
          object_id: 'obj-1',
          status: 'ok',
          device_id: 'device-1',
          last_contact_at: new Date().toISOString(),
          points: [{ id: 'p1', value: 100 }],
        },
      ],
    },
    isLoading: false,
    error: null,
  }),
}))

describe('DashboardPage', () => {
  it('renders dashboard title', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    )
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText(/Monitorowanie sieci wodociągów/i)).toBeInTheDocument()
  })

  it('renders objects table', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    )
    expect(screen.getByText('Obiekty monitorowania')).toBeInTheDocument()
  })

  it('displays loaded objects', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    )
    expect(screen.getByText('obj-1')).toBeInTheDocument()
  })

  it('shows filter button', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    )
    expect(screen.getByText('Filtry')).toBeInTheDocument()
  })
})
