import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export interface LatestPointValue {
  point_id: string
  type: string
  unit: string
  value: number
  quality: string
  measured_at: string
  device_id: string
}

export interface ObjectSummary {
  org_id: string
  object_id: string
  name: string
  device_id: string
  status: 'ok' | 'warning' | 'no_comm' | 'no_data'
  last_contact_at: string | null
  last_measurement_at: string | null
  points: LatestPointValue[]
}

export interface ObjectDetail extends ObjectSummary {
  last_seq: number
  available_points: string[]
}

export interface MeasurementSeriesItem {
  point_id: string
  type: string
  unit: string
  measured_at: string
  value: number
  avg: number
  min: number
  max: number
  quality: string
  device_id: string
}

export interface MeasurementsResponse {
  object_id: string
  from: string
  to: string
  count: number
  items: MeasurementSeriesItem[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export function useTelemetryObjects(limit = 50) {
  return useQuery<PaginatedResponse<ObjectSummary>>({
    queryKey: ['telemetry', 'objects'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/api/v1/telemetry/objects', {
          params: { limit },
        })
        console.log('Telemetry API response:', response.data)

        if (!response.data || typeof response.data !== 'object') {
          console.error('Invalid response format:', response.data)
          throw new Error(`Invalid response format: ${typeof response.data}`)
        }

        if (!Array.isArray(response.data.items)) {
          console.error('Response.items is not an array:', response.data.items)
          throw new Error('Response.items is not an array')
        }

        return response.data
      } catch (error) {
        console.error('Error fetching telemetry objects:', error)
        throw error
      }
    },
  })
}

export function useTelemetryObjectDetail(objectId: string) {
  return useQuery<ObjectDetail>({
    queryKey: ['telemetry', 'object', objectId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/telemetry/objects/${objectId}`)
      return data
    },
    enabled: !!objectId,
  })
}

export function useTelemetryMeasurements(
  objectId: string,
  pointId?: string,
  hoursBack = 24,
) {
  return useQuery<MeasurementsResponse>({
    queryKey: ['telemetry', 'measurements', objectId, pointId, hoursBack],
    queryFn: async () => {
      const now = new Date()
      const startTime = new Date(now.getTime() - hoursBack * 60 * 60 * 1000)

      const { data } = await apiClient.get(
        `/api/v1/telemetry/objects/${objectId}/measurements`,
        {
          params: {
            point_id: pointId,
            start: startTime.toISOString(),
            end: now.toISOString(),
            limit: 5000,
          },
        },
      )
      return data
    },
    enabled: !!objectId,
  })
}
