import { describe, expect, it } from 'vitest'
import {
  bufferFillPercent,
  formatAge,
  formatBytes,
  formatRestartReason,
  formatUptime,
  rssiLevel,
} from './deviceState'

describe('formatUptime', () => {
  it('renders days and hours for a long-running device', () => {
    expect(formatUptime(10 * 86400 + 5 * 3600)).toBe('10d 5h')
  })

  it('renders hours and minutes below a day', () => {
    expect(formatUptime(3 * 3600 + 25 * 60)).toBe('3h 25m')
  })

  it('renders minutes for a device that just restarted', () => {
    expect(formatUptime(90)).toBe('1m')
  })

  it('shows a dash rather than a zero when firmware reports nothing', () => {
    expect(formatUptime(undefined)).toBe('—')
  })
})

describe('formatAge', () => {
  it('names the age instead of implying the value is live', () => {
    expect(formatAge(20)).toBe('przed chwilą')
    expect(formatAge(20 * 60)).toBe('sprzed 20 min')
    expect(formatAge(3 * 3600)).toBe('sprzed 3 h')
    expect(formatAge(50 * 3600)).toBe('sprzed 2 dni')
  })
})

describe('rssiLevel', () => {
  it('separates a comfortable link from one that is about to retransmit', () => {
    expect(rssiLevel(-67)).toBe('good')
    expect(rssiLevel(-88)).toBe('fair')
    expect(rssiLevel(-105)).toBe('poor')
  })

  it('treats a missing reading as unknown, not as a weak signal', () => {
    expect(rssiLevel(undefined)).toBe('unknown')
  })
})

describe('bufferFillPercent', () => {
  it('reports fill against the reported capacity', () => {
    expect(bufferFillPercent(12, 48)).toBe(25)
    expect(bufferFillPercent(48, 48)).toBe(100)
  })

  it('returns undefined rather than dividing by a missing capacity', () => {
    expect(bufferFillPercent(12, undefined)).toBeUndefined()
    expect(bufferFillPercent(12, 0)).toBeUndefined()
    expect(bufferFillPercent(undefined, 48)).toBeUndefined()
  })
})

describe('formatBytes', () => {
  it('scales to the unit an operator can read', () => {
    expect(formatBytes(512)).toBe('512 B')
    expect(formatBytes(184320)).toBe('180.0 kB')
    expect(formatBytes(4 * 1024 * 1024)).toBe('4.0 MB')
  })
})

describe('formatRestartReason', () => {
  it('translates the firmware vocabulary', () => {
    expect(formatRestartReason('task_watchdog')).toBe('watchdog zadania')
    expect(formatRestartReason('brownout')).toBe('zanik zasilania (brownout)')
  })

  it('passes an unrecognised reason through instead of hiding it', () => {
    expect(formatRestartReason('future_reason')).toBe('future_reason')
  })
})
