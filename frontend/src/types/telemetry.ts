export interface LatestPointValue {
  point_id: string
  point_name: string
  type: string
  unit: string
  value: number
  quality: string
  measured_at: string
  device_id: string
  device_name: string
}

export interface ObjectSummary {
  org_id: string
  org_name: string
  object_id: string
  name: string
  device_id: string
  device_name: string
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
  point_name: string
  type: string
  unit: string
  measured_at: string
  value: number
  avg: number
  min: number
  max: number
  quality: string
  device_id: string
  device_name: string
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
