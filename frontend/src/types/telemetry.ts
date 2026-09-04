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

/* Device state read channel (B-08) — one entry per reported section */
export interface DeviceStateSection {
  section: string
  schema_version: number
  captured_at: string
  received_at: string
  age_seconds: number
  is_stale: boolean
  data: Record<string, unknown>
}

export interface DeviceState {
  device_id: string
  external_id: string
  last_seen_at: string | null
  last_diagnostics_at: string | null
  sections: DeviceStateSection[]
}

/* Fields of the `device` section. All optional: an older firmware reports a
   subset, and a newer one may report more than this backend types.
   `| null` is not decoration — the backend types every field as nullable, so a
   device may send an explicit null where firmware today simply omits the key.
   Readers must treat the two the same. */
export interface DeviceStateDeviceSection {
  serial_number?: string | null
  firmware_version?: string | null
  registry_schema_version?: number | null
  uptime_seconds?: number | null
  restart_count?: number | null
  restart_reason?: string | null
  rssi_dbm?: number | null
  free_heap_bytes?: number | null
  min_free_heap_bytes?: number | null
  buffer_windows_used?: number | null
  buffer_windows_capacity?: number | null
  buffer_windows_dropped?: number | null
}
