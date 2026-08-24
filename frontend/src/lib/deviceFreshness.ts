export type FreshnessLevel = 'fresh' | 'warn' | 'stale' | 'unknown';

export function getFreshness(lastSeenAt: string | null): FreshnessLevel {
  if (!lastSeenAt) return 'unknown';

  const now = new Date();
  const lastSeen = new Date(lastSeenAt);
  const diffMs = now.getTime() - lastSeen.getTime();

  const oneHourMs = 60 * 60 * 1000;
  const threeDaysMs = 3 * 24 * 60 * 60 * 1000;

  if (diffMs < oneHourMs) return 'fresh';
  if (diffMs < threeDaysMs) return 'warn';
  return 'stale';
}

export function formatRelativeTime(iso: string | null): string {
  if (!iso) return '—';

  const now = new Date();
  const date = new Date(iso);
  const diffMs = now.getTime() - date.getTime();

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d temu`;
  if (hours > 0) return `${hours}h temu`;
  if (minutes > 0) return `${minutes}m temu`;
  return 'teraz';
}
