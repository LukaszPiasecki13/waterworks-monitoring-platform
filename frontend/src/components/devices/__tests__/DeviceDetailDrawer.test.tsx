import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

import type { Device } from '@/types/coreData'
import type { DeviceState } from '@/types/telemetry'

/* The drawer pulls four independent queries. Mocking the hooks rather than
   the network keeps these tests about what an operator sees — which is the
   part B-08 changed and the part no backend test can cover. */
const usePlatformDevice = vi.fn()
const useWaterObject = vi.fn()
const useOrganization = vi.fn()
const usePlatformDeviceState = vi.fn()

vi.mock('@/hooks/useDevices', () => ({
  usePlatformDevice: (...args: unknown[]) => usePlatformDevice(...args),
  useWaterObject: (...args: unknown[]) => useWaterObject(...args),
  useOrganization: (...args: unknown[]) => useOrganization(...args),
}))

vi.mock('@/hooks/useDeviceState', async () => {
  const actual = await vi.importActual<typeof import('@/hooks/useDeviceState')>(
    '@/hooks/useDeviceState'
  )
  return {
    ...actual,
    usePlatformDeviceState: (...args: unknown[]) => usePlatformDeviceState(...args),
  }
})

const { DeviceDetailDrawer } = await import('../DeviceDetailDrawer')

const device: Device = {
  id: 'dev-1',
  water_object_id: 'obj-1',
  external_id: 'WW-2026-000123',
  firmware_version: '0.4.0',
  last_seen_at: new Date().toISOString(),
  last_diagnostics_at: new Date().toISOString(),
  is_active: true,
  created_at: new Date().toISOString(),
  device_credential_id: 'cred-1',
}

function stateWith(
  data: Record<string, unknown>,
  overrides: Partial<DeviceState['sections'][number]> = {}
): DeviceState {
  return {
    device_id: 'dev-1',
    external_id: 'WW-2026-000123',
    last_seen_at: new Date().toISOString(),
    last_diagnostics_at: new Date().toISOString(),
    sections: [
      {
        section: 'device',
        schema_version: 1,
        captured_at: new Date().toISOString(),
        received_at: new Date().toISOString(),
        age_seconds: 45,
        is_stale: false,
        data,
        ...overrides,
      },
    ],
  }
}

const fullSection = {
  serial_number: 'WW-2026-000123',
  firmware_version: '0.4.0',
  registry_schema_version: 2,
  uptime_seconds: 10 * 86400 + 5 * 3600,
  restart_count: 12,
  restart_reason: 'task_watchdog',
  rssi_dbm: -67,
  free_heap_bytes: 184320,
  min_free_heap_bytes: 151000,
  buffer_windows_used: 8,
  buffer_windows_capacity: 48,
  buffer_windows_dropped: 0,
}

function renderDrawer(
  state: DeviceState | undefined,
  { isLoading = false, isError = false } = {}
) {
  usePlatformDevice.mockReturnValue({ data: device, isLoading: false })
  useWaterObject.mockReturnValue({ data: { id: 'obj-1', organization_id: 'org-1' } })
  useOrganization.mockReturnValue({ data: { id: 'org-1', name: 'Gmina Testowa' } })
  usePlatformDeviceState.mockReturnValue({ data: state, isLoading, isError })

  return render(
    <DeviceDetailDrawer deviceId="dev-1" open onOpenChange={() => {}} />
  )
}

describe('DeviceDetailDrawer — device state (B-08)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the reported state instead of the old "wymaga firmware" placeholders', () => {
    renderDrawer(stateWith(fullSection))

    expect(screen.queryByText(/wymaga firmware/i)).not.toBeInTheDocument()
    expect(screen.getByText(/-67 dBm/)).toBeInTheDocument()
    expect(screen.getByText('10d 5h')).toBeInTheDocument()
    expect(screen.getByText(/watchdog zadania/)).toBeInTheDocument()
  })

  it('states how old the reading is, never presenting it as live', () => {
    renderDrawer(stateWith(fullSection, { age_seconds: 20 * 60, is_stale: true }))

    expect(screen.getAllByText(/sprzed 20 min/).length).toBeGreaterThan(0)
  })

  it('shows buffer fill and flags dropped windows as data loss', () => {
    renderDrawer(
      stateWith({
        ...fullSection,
        buffer_windows_used: 44,
        buffer_windows_capacity: 48,
        buffer_windows_dropped: 17,
      })
    )

    expect(screen.getByText(/44\/48 okien \(92%\)/)).toBeInTheDocument()
    expect(screen.getByText('bliski przepełnienia')).toBeInTheDocument()
    expect(screen.getByText('utrata danych')).toBeInTheDocument()
  })

  it('does not flag a healthy buffer', () => {
    renderDrawer(stateWith(fullSection))

    expect(screen.queryByText('utrata danych')).not.toBeInTheDocument()
    expect(screen.queryByText('bliski przepełnienia')).not.toBeInTheDocument()
  })

  it('explains the empty state rather than showing a wall of dashes', () => {
    renderDrawer({
      device_id: 'dev-1',
      external_id: 'WW-2026-000123',
      last_seen_at: new Date().toISOString(),
      last_diagnostics_at: null,
      sections: [],
    })

    expect(screen.getByText(/nie przysłało jeszcze raportu stanu/i)).toBeInTheDocument()
  })

  it('survives a section that omits every optional field', () => {
    /* Firmware older than this backend reports a subset; the drawer must
       degrade to dashes, not crash on undefined. */
    expect(() => renderDrawer(stateWith({}))).not.toThrow()

    expect(screen.getByText('Sygnał modemu (RSSI)')).toBeInTheDocument()
  })

  it('omits RSSI rather than inventing one when the modem had no reading', () => {
    const withoutRssi = { ...fullSection } as Partial<typeof fullSection>
    delete withoutRssi.rssi_dbm
    renderDrawer(stateWith(withoutRssi))

    expect(screen.queryByText(/dBm/)).not.toBeInTheDocument()
    expect(screen.queryByText('dobry')).not.toBeInTheDocument()
  })

  it('treats an explicit null the same as an omitted field', () => {
    /* The backend types every field as nullable, so a device may send null
       where firmware today omits the key. Rendering " dBm" next to a red
       "krytyczny" badge for a device that simply had no reading would invent
       a fault that does not exist. */
    renderDrawer(stateWith({ ...fullSection, rssi_dbm: null, uptime_seconds: null }))

    expect(screen.queryByText(/dBm/)).not.toBeInTheDocument()
    expect(screen.queryByText('krytyczny')).not.toBeInTheDocument()
  })

  it('says the read failed instead of blaming the device', () => {
    /* "Never reported" and "we could not ask" are opposite diagnoses. */
    renderDrawer(undefined, { isError: true })

    expect(screen.getByText(/nie udało się pobrać stanu/i)).toBeInTheDocument()
    expect(screen.queryByText(/nie przysłało jeszcze raportu stanu/i)).not.toBeInTheDocument()
  })
})
