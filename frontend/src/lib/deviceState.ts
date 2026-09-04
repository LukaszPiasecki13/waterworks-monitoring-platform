/* Formatting helpers for the device state read channel (B-08).
   Kept apart from the drawer so the "never show a value without its age"
   rule has one implementation instead of one per view. */

export function formatUptime(seconds: number | null | undefined): string {
  if (seconds == null) return '—'

  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

export function formatAge(ageSeconds: number): string {
  if (ageSeconds < 60) return 'przed chwilą'
  const minutes = Math.floor(ageSeconds / 60)
  if (minutes < 60) return `sprzed ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `sprzed ${hours} h`
  return `sprzed ${Math.floor(hours / 24)} dni`
}

export function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} kB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export type RssiLevel = 'good' | 'fair' | 'poor' | 'unknown'

/* Thresholds follow the usual LTE rule of thumb: better than -80 dBm is
   comfortable, worse than -95 dBm is where retransmissions start. */
export function rssiLevel(rssiDbm: number | null | undefined): RssiLevel {
  if (rssiDbm == null) return 'unknown'
  if (rssiDbm >= -80) return 'good'
  if (rssiDbm >= -95) return 'fair'
  return 'poor'
}

const RESTART_REASON_LABELS: Record<string, string> = {
  unknown: 'nieznana',
  power_on: 'włączenie zasilania',
  external: 'reset zewnętrzny',
  software: 'restart programowy',
  panic: 'panic (błąd krytyczny)',
  int_watchdog: 'watchdog przerwań',
  task_watchdog: 'watchdog zadania',
  other_watchdog: 'watchdog',
  deep_sleep: 'wybudzenie z deep sleep',
  brownout: 'zanik zasilania (brownout)',
  sdio: 'reset SDIO',
}

export function formatRestartReason(reason: string | null | undefined): string {
  if (!reason) return '—'
  return RESTART_REASON_LABELS[reason] ?? reason
}

/* Buffer fill matters because the device holds roughly 12 minutes in RAM
   while the platform promises 72 h of offline retention — a filling buffer
   is the early warning that windows are about to be dropped. */
export function bufferFillPercent(
  used: number | null | undefined,
  capacity: number | null | undefined
): number | undefined {
  if (!capacity || used == null) return undefined
  return Math.round((used / capacity) * 100)
}
