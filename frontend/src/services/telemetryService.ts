import { apiClient } from '@/lib/api'
import type { ObjectSummary, ObjectDetail, MeasurementsResponse, PaginatedResponse } from '@/types/telemetry'

interface ListObjectsParams {
  limit?: number
  org_id?: string
}

interface GetMeasurementsParams {
  point_id?: string
  start: string
  end: string
  limit?: number
}

export const telemetryService = {
  async listObjects(params: ListObjectsParams): Promise<PaginatedResponse<ObjectSummary>> {
    const { data } = await apiClient.get('/api/v1/telemetry/objects', { params })
    if (!data || typeof data !== 'object' || !Array.isArray(data.items)) {
      throw new Error('Invalid response format')
    }
    return data
  },

  async getObject(objectId: string): Promise<ObjectDetail> {
    const { data } = await apiClient.get(`/api/v1/telemetry/objects/${objectId}`)
    return data
  },

  async getMeasurements(objectId: string, params: GetMeasurementsParams): Promise<MeasurementsResponse> {
    const { data } = await apiClient.get(`/api/v1/telemetry/objects/${objectId}/measurements`, { params })
    return data
  },
}
