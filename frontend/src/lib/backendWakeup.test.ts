import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import {
  startBackendRequest,
  subscribeToBackendWakeup,
  resetBackendWakeupNotice,
  getBackendWakeupState,
} from './backendWakeup'

describe('backendWakeup', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    resetBackendWakeupNotice()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('timer starts, popup appears after 5s', () => {
    const states: boolean[] = []
    subscribeToBackendWakeup(() => {
      states.push(getBackendWakeupState().isWakingUp)
    })

    startBackendRequest()

    expect(getBackendWakeupState().isWakingUp).toBe(false)

    vi.advanceTimersByTime(4999)
    expect(getBackendWakeupState().isWakingUp).toBe(false)

    vi.advanceTimersByTime(1)
    expect(getBackendWakeupState().isWakingUp).toBe(true)
  })

  it('cleanup cancels timer early', () => {
    const states: boolean[] = []
    subscribeToBackendWakeup(() => {
      states.push(getBackendWakeupState().isWakingUp)
    })

    const cleanup = startBackendRequest()

    vi.advanceTimersByTime(2500)
    cleanup()

    vi.advanceTimersByTime(10000)
    expect(getBackendWakeupState().isWakingUp).toBe(false)
  })

  it('resetBackendWakeupNotice hides popup', () => {
    startBackendRequest()
    vi.advanceTimersByTime(5000)

    expect(getBackendWakeupState().isWakingUp).toBe(true)

    resetBackendWakeupNotice()
    expect(getBackendWakeupState().isWakingUp).toBe(false)
  })

  it('multiple subscribers are notified', () => {
    const calls1: boolean[] = []
    const calls2: boolean[] = []

    subscribeToBackendWakeup(() => calls1.push(getBackendWakeupState().isWakingUp))
    subscribeToBackendWakeup(() => calls2.push(getBackendWakeupState().isWakingUp))

    startBackendRequest()
    vi.advanceTimersByTime(5000)

    expect(calls1.length).toBeGreaterThan(0)
    expect(calls2.length).toBeGreaterThan(0)
    expect(getBackendWakeupState().isWakingUp).toBe(true)
  })
})
