export function formatTimeAgo(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} sec temu`
  if (seconds < 3600) return `${Math.round(seconds / 60)} min temu`
  if (seconds < 86400) return `${Math.round(seconds / 3600)} h temu`
  return `${Math.round(seconds / 86400)} dni temu`
}
