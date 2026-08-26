import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { ObjectCard } from '../ObjectCard'

import type { WaterObject } from '@/types/coreData'
import type { ObjectSummary } from '@/types/telemetry'

const mockObject: WaterObject = {
  id: 'obj-1',
  organization_id: 'org-1',
  name: 'Test Object',
  object_type: 'pump',
  location_description: 'Test Location',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockTelemetry: ObjectSummary = {
  org_id: 'org-1',
  org_name: 'Test Org',
  object_id: 'obj-1',
  name: 'Test Object',
  device_id: 'dev-1',
  device_name: 'Device 1',
  status: 'ok' as const,
  last_contact_at: new Date().toISOString(),
  last_measurement_at: new Date().toISOString(),
  points: [
    {
      point_id: 'p1',
      point_name: 'Pressure',
      type: 'pressure',
      unit: 'bar',
      value: 2.5,
      quality: 'good',
      measured_at: new Date().toISOString(),
      device_id: 'dev-1',
      device_name: 'Device 1',
    },
  ],
}

describe('ObjectCard', () => {
  const mockOnTogglePin = vi.fn()
  const mockOnNavigate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders card with object name', () => {
    render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    expect(screen.getByText('Test Object')).toBeInTheDocument()
  })

  it('renders object type', () => {
    render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    expect(screen.getByText('pump')).toBeInTheDocument()
  })

  it('renders star icon filled when pinned', () => {
    const { container } = render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={true}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    const starButton = container.querySelector('button[title="Odepnij"]')
    expect(starButton).toBeInTheDocument()
  })

  it('renders star icon outline when not pinned', () => {
    const { container } = render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    const starButton = container.querySelector('button[title="Przypnij"]')
    expect(starButton).toBeInTheDocument()
  })

  it('calls onTogglePin when star icon is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    const starButton = container.querySelector('button[title="Przypnij"]')!
    await user.click(starButton)
    expect(mockOnTogglePin).toHaveBeenCalledWith('obj-1')
  })

  it('calls onNavigate when card is clicked', async () => {
    const user = userEvent.setup()
    render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    const card = screen.getByText('Test Object').closest('div[class*="rounded-lg"]')!
    await user.click(card)
    expect(mockOnNavigate).toHaveBeenCalledWith('obj-1')
  })

  it('renders hover effect class', () => {
    const { container } = render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    const card = container.querySelector('[class*="hover:shadow-md"]')
    expect(card).toBeInTheDocument()
  })

  it('renders metrics when telemetry data is available', () => {
    render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    expect(screen.getByText('Pressure')).toBeInTheDocument()
    expect(screen.getByText('2.5 bar')).toBeInTheDocument()
  })

  it('renders status pill', () => {
    const { container } = render(
      <ObjectCard
        object={mockObject}
        telemetry={mockTelemetry}
        isPinned={false}
        onTogglePin={mockOnTogglePin}
        onNavigate={mockOnNavigate}
      />
    )
    // StatusPill should be rendered with status indicator
    expect(container.querySelector('[class*="inline-flex"]')).toBeInTheDocument()
  })
})
