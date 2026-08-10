import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatusPill } from './StatusPill'

describe('StatusPill', () => {
  it('renders object status pills', () => {
    render(<StatusPill kind="objectStatus" value="ok" />)
    expect(screen.getByText(/OK|Aktywne/i)).toBeInTheDocument()
  })

  it('renders quality data pills', () => {
    render(<StatusPill kind="quality" value="good" />)
    expect(screen.getByText(/Dobra|Good/i)).toBeInTheDocument()
  })

  it('applies correct styling for different statuses', () => {
    const { container: container1 } = render(<StatusPill kind="objectStatus" value="ok" />)
    const okPill = container1.querySelector('[class*="status-ok"]')
    expect(okPill).toBeInTheDocument()

    const { container: container2 } = render(<StatusPill kind="objectStatus" value="warning" />)
    const warningPill = container2.querySelector('[class*="status-warning"]')
    expect(warningPill).toBeInTheDocument()
  })

  it('renders with class when status is unknown', () => {
    const { container } = render(<StatusPill kind="objectStatus" value="unknown" />)
    expect(container.querySelector('[class*="bg-"]')).toBeInTheDocument()
  })
})
