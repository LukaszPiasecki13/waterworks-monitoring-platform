/* Status mapping — spójna semantyka między statusem obiektu i jakością danych */

export type SemanticStatus = 'success' | 'warning' | 'danger' | 'danger-strong' | 'neutral' | 'info';

export type ObjectStatus = 'ok' | 'warning' | 'alarm' | 'no_comm' | 'no_data';
export type DataQuality =
  | 'good'
  | 'stale'
  | 'out_of_range'
  | 'sensor_error'
  | 'communication_error'
  | 'delayed'
  | 'unknown';

export const OBJECT_STATUS_COLOR_MAP: Record<ObjectStatus, SemanticStatus> = {
  ok: 'success',
  warning: 'warning',
  alarm: 'danger-strong',
  no_comm: 'danger',
  no_data: 'neutral',
};

export const OBJECT_STATUS_LABEL_MAP: Record<ObjectStatus, string> = {
  ok: 'OK — Aktywne',
  warning: 'Ostrzeżenie',
  alarm: 'Alarm',
  no_comm: 'Brak komunikacji',
  no_data: 'Brak danych',
};

export const DATA_QUALITY_COLOR_MAP: Record<DataQuality, SemanticStatus> = {
  good: 'success',
  stale: 'warning',
  out_of_range: 'warning',
  sensor_error: 'danger',
  communication_error: 'danger',
  delayed: 'warning',
  unknown: 'neutral',
};

export const DATA_QUALITY_LABEL_MAP: Record<DataQuality, string> = {
  good: 'Dobra jakość',
  stale: 'Dane nieświeże',
  out_of_range: 'Poza zakresem',
  sensor_error: 'Błąd sensora',
  communication_error: 'Błąd komunikacji',
  delayed: 'Opóźnione',
  unknown: 'Nieznane',
};

export const SEMANTIC_STATUS_TO_TAILWIND: Record<SemanticStatus, string> = {
  success: 'bg-status-ok-50 text-status-ok-700 border-status-ok-200',
  warning: 'bg-status-warning-50 text-status-warning-700 border-status-warning-200',
  danger: 'bg-status-no-comm-50 text-status-no-comm-700 border-status-no-comm-200',
  'danger-strong': 'bg-status-alarm-50 text-status-alarm-700 border-status-alarm-200',
  neutral: 'bg-status-no-data-50 text-status-no-data-700 border-status-no-data-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
};

export const SEMANTIC_STATUS_TO_DOT_COLOR: Record<SemanticStatus, string> = {
  success: 'text-status-ok-500',
  warning: 'text-status-warning-500',
  danger: 'text-status-no-comm-500',
  'danger-strong': 'text-status-alarm-500',
  neutral: 'text-status-no-data-500',
  info: 'text-blue-500',
};

export function getObjectStatusColor(status: ObjectStatus): SemanticStatus {
  return OBJECT_STATUS_COLOR_MAP[status];
}

export function getObjectStatusLabel(status: ObjectStatus): string {
  return OBJECT_STATUS_LABEL_MAP[status];
}

export function getDataQualityColor(quality: DataQuality): SemanticStatus {
  return DATA_QUALITY_COLOR_MAP[quality];
}

export function getDataQualityLabel(quality: DataQuality): string {
  return DATA_QUALITY_LABEL_MAP[quality];
}
