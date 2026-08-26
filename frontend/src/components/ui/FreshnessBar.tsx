import { useState, useEffect } from 'react'
import { formatTimeAgo } from './freshnessUtils'

export interface FreshnessBarProps {
  lastContactAt: Date
  expectedIntervalSeconds?: number
}

function calculateFreshness(lastContactAt: Date, expectedIntervalSeconds: number) {
  const now = Date.now()
  const contactTime = lastContactAt.getTime()
  const elapsedMs = now - contactTime
  const elapsedSec = elapsedMs / 1000

  const prog = Math.min(elapsedSec / expectedIntervalSeconds, 1) * 100
  const lbl = formatTimeAgo(elapsedSec)

  return {
    progress: prog,
    label: lbl,
  }
}

export function FreshnessBar({
  lastContactAt,
  expectedIntervalSeconds = 300,
}: FreshnessBarProps) {
  const [freshness, setFreshness] = useState(() =>
    calculateFreshness(lastContactAt, expectedIntervalSeconds)
  )

  useEffect(() => {
    setFreshness(calculateFreshness(lastContactAt, expectedIntervalSeconds))
  }, [lastContactAt, expectedIntervalSeconds])

  useEffect(() => {
    const interval = setInterval(() => {
      setFreshness(() =>
        calculateFreshness(lastContactAt, expectedIntervalSeconds)
      )
    }, 1000)
    return () => clearInterval(interval)
  }, [lastContactAt, expectedIntervalSeconds])

  const getColorClass = () => {
    if (freshness.progress < 50) return 'bg-green-500'
    if (freshness.progress < 80) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-neutral-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColorClass()} transition-all duration-300`}
          style={{ width: `${freshness.progress}%` }}
        />
      </div>
      <span className="text-xs text-neutral-500 whitespace-nowrap" title={freshness.label}>
        {freshness.label}
      </span>
    </div>
  )
}
