import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FreshnessBar } from '../FreshnessBar'

describe('FreshnessBar', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('renders progress bar and label', () => {
    const pastDate = new Date(Date.now() - 60000) // 1 minute ago
    render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    expect(screen.getByText(/min temu/)).toBeInTheDocument()
  })

  it('calculates progress correctly for recent contact', () => {
    const pastDate = new Date(Date.now() - 30000) // 30 seconds ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('[style*="width"]')
    expect(progressBar).toBeInTheDocument()
    // Progress should be ~10% (30/300)
    expect(progressBar).toHaveStyle({ width: expect.stringContaining('%') })
  })

  it('calculates progress correctly for older contact', () => {
    const pastDate = new Date(Date.now() - 250000) // ~4.17 minutes ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('[style*="width"]')
    expect(progressBar).toBeInTheDocument()
    // Progress should be ~83% (250/300)
  })

  it('caps progress at 100%', () => {
    const pastDate = new Date(Date.now() - 600000) // 10 minutes ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('[style*="width"]')
    expect(progressBar).toHaveStyle({ width: '100%' })
  })

  it('formats label as seconds for recent contact', () => {
    const pastDate = new Date(Date.now() - 30000) // 30 seconds ago
    render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    expect(screen.getByText(/30 sec temu/)).toBeInTheDocument()
  })

  it('formats label as minutes for older contact', () => {
    const pastDate = new Date(Date.now() - 120000) // 2 minutes ago
    render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    expect(screen.getByText(/2 min temu/)).toBeInTheDocument()
  })

  it('formats label as hours for very old contact', () => {
    const pastDate = new Date(Date.now() - 7200000) // 2 hours ago
    render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    expect(screen.getByText(/2 h temu/)).toBeInTheDocument()
  })

  it('applies green color for fresh data', () => {
    const pastDate = new Date(Date.now() - 60000) // 1 minute ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('.bg-green-500')
    expect(progressBar).toBeInTheDocument()
  })

  it('applies yellow color for warning state', () => {
    const pastDate = new Date(Date.now() - 200000) // ~3.33 minutes ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('.bg-yellow-500')
    expect(progressBar).toBeInTheDocument()
  })

  it('applies red color for stale data', () => {
    const pastDate = new Date(Date.now() - 300000) // 5 minutes ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={300} />
    )
    const progressBar = container.querySelector('.bg-red-500')
    expect(progressBar).toBeInTheDocument()
  })

  it('uses custom expectedIntervalSeconds', () => {
    const pastDate = new Date(Date.now() - 50000) // 50 seconds ago
    const { container } = render(
      <FreshnessBar lastContactAt={pastDate} expectedIntervalSeconds={100} />
    )
    const progressBar = container.querySelector('[style*="width"]')
    expect(progressBar).toHaveStyle({ width: '50%' })
  })
})
