import { apiClient } from '@/lib/api'
import type { ObjectSummary, ObjectDetail, MeasurementsResponse, PaginatedResponse } from '@/types/telemetry'

interface ListObjectsParams {
  limit?: number
}

interface GetMeasurementsParams {
  point_id?: string
  start: string
  end: string
  limit?: number
}

export const telemetryService = {
  async listObjects(orgId: string, params?: ListObjectsParams): Promise<PaginatedResponse<ObjectSummary>> {
    const { data } = await apiClient.get(`/api/v1/orgs/${orgId}/telemetry/objects`, { params })
    if (!data || typeof data !== 'object' || !Array.isArray(data.items)) {
      throw new Error('Invalid response format')
    }
    return data
  },

  async getObject(orgId: string, objectId: string): Promise<ObjectDetail> {
    const { data } = await apiClient.get(`/api/v1/orgs/${orgId}/telemetry/objects/${objectId}`)
    return data
  },

  async getMeasurements(orgId: string, objectId: string, params: GetMeasurementsParams): Promise<MeasurementsResponse> {
    const { data } = await apiClient.get(`/api/v1/orgs/${orgId}/telemetry/objects/${objectId}/measurements`, { params })
    return data
  },
}
