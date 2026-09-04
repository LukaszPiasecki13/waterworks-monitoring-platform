import { useQuery } from '@tanstack/react-query'
import { deviceStateService } from '@/services/deviceStateService'
import { queryKeys } from './queryKeys'
import type { DeviceState, DeviceStateDeviceSection, DeviceStateSection } from '@/types/telemetry'

/* Last state a device reported, read through the platform plane.
   Refetched on an interval because the answer only changes when the device
   next calls in — polling here is what turns "stale" into "fresh" without
   the operator reloading the page. */
export function usePlatformDeviceState(deviceId: string | null) {
  return useQuery({
    queryKey: queryKeys.telemetry.deviceState(deviceId ?? '', null),
    queryFn: () => deviceStateService.getPlatform(deviceId!),
    enabled: !!deviceId,
    refetchInterval: 60_000,
  })
}

export function useOrgDeviceState(orgId: string | null, deviceId: string | null) {
  return useQuery({
    queryKey: queryKeys.telemetry.deviceState(deviceId ?? '', orgId),
    queryFn: () => deviceStateService.get(orgId!, deviceId!),
    enabled: !!orgId && !!deviceId,
    refetchInterval: 60_000,
  })
}

export function findSection(
  state: DeviceState | undefined,
  section: string
): DeviceStateSection | undefined {
  return state?.sections.find((entry) => entry.section === section)
}

/* The `device` section's payload is stored as free-form JSON so a newer
   firmware is never truncated on the way in. Reading it back therefore means
   narrowing, not casting blindly. */
export function deviceSectionData(
  state: DeviceState | undefined
): DeviceStateDeviceSection | undefined {
  const section = findSection(state, 'device')
  return section ? (section.data as DeviceStateDeviceSection) : undefined
}
