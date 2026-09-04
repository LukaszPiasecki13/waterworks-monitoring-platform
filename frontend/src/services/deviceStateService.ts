import { apiClient } from '@/lib/api'
import type { DeviceState } from '@/types/telemetry'

/* Device state read channel (B-08).
   The device answers reads on its next contact, so these endpoints serve the
   last state it reported — never a live query. Every section carries its own
   age, which the UI is expected to show alongside the value. */
export const deviceStateService = {
  async get(orgId: string, deviceId: string): Promise<DeviceState> {
    const { data } = await apiClient.get(
      `/api/v1/orgs/${orgId}/telemetry/devices/${deviceId}/state`
    )
    return data
  },

  async getPlatform(deviceId: string): Promise<DeviceState> {
    const { data } = await apiClient.get(
      `/api/v1/platform/telemetry/devices/${deviceId}/state`
    )
    return data
  },
}
