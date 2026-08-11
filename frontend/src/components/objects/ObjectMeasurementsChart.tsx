import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useTelemetryMeasurements } from '@/hooks/useTelemetryApi'

interface ObjectMeasurementsChartProps {
  objectId: string
  hoursBack?: number
}

const CHART_COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4']
const HOUR_MS = 60 * 60 * 1000
const DAY_MS = 24 * HOUR_MS

function formatAxisTick(timestamp: number, spanMs: number): string {
  const date = new Date(timestamp)
  if (spanMs <= 26 * HOUR_MS) {
    return date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
  }
  if (spanMs <= 8 * DAY_MS) {
    return (
      date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit' }) +
      ' ' +
      date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
    )
  }
  return date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function formatTooltipLabel(timestamp: number): string {
  return new Date(timestamp).toLocaleString('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function ObjectMeasurementsChart({
  objectId,
  hoursBack = 24,
}: ObjectMeasurementsChartProps) {
  const { data: measurements, isLoading } = useTelemetryMeasurements(
    objectId,
    undefined,
    hoursBack,
  )
  const [selectedPointIds, setSelectedPointIds] = useState<string[]>([])

  // Merge measurements into one row per timestamp
  const chartDataByTimestamp = new Map<number, Record<string, number>>()
  const pointNameMap = new Map<string, string>()
  for (const m of measurements?.items || []) {
    const timestamp = new Date(m.measured_at).getTime()
    const row = chartDataByTimestamp.get(timestamp) ?? { timestamp }
    row[`${m.point_id}_value`] = m.value
    chartDataByTimestamp.set(timestamp, row)
    pointNameMap.set(m.point_id, m.point_name)
  }
  const chartData = [...chartDataByTimestamp.values()].sort(
    (a, b) => a.timestamp - b.timestamp,
  )
  const chartSpanMs =
    chartData.length > 1 ? chartData[chartData.length - 1].timestamp - chartData[0].timestamp : DAY_MS

  // Get unique point IDs
  const uniquePoints = [...new Set((measurements?.items || []).map((i) => i.point_id))]

  // Auto-select first point if none selected
  useEffect(() => {
    if (selectedPointIds.length === 0 && uniquePoints.length > 0) {
      setSelectedPointIds([uniquePoints[0]])
    }
  }, [uniquePoints, selectedPointIds.length])

  const togglePoint = (pointId: string) => {
    setSelectedPointIds((prev) =>
      prev.includes(pointId)
        ? prev.filter((id) => id !== pointId)
        : [...prev, pointId].slice(-3), // Max 3 lines
    )
  }

  if (isLoading) {
    return (
      <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-8 text-center text-neutral-500">
        Ładowanie danych wykresu...
      </div>
    )
  }

  if (!measurements || measurements.items.length === 0) {
    return (
      <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-8 text-center text-neutral-500">
        Brak danych pomiarów dla tego okresu
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {uniquePoints.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-neutral-900 mb-2">
            Pomiary do wykreślenia (max 3):
          </h4>
          <div className="flex flex-wrap gap-2">
            {uniquePoints.map((pointId, idx) => (
              <button
                key={pointId}
                onClick={() => togglePoint(pointId)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors border ${
                  selectedPointIds.includes(pointId)
                    ? 'border-transparent text-white'
                    : 'border-neutral-300 text-neutral-700 bg-white hover:bg-neutral-50'
                }`}
                style={
                  selectedPointIds.includes(pointId)
                    ? { backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }
                    : undefined
                }
              >
                {pointNameMap.get(pointId) || pointId}
              </button>
            ))}
          </div>
        </div>
      )}

      {chartData.length > 0 && selectedPointIds.length > 0 ? (
        <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timestamp"
                type="number"
                scale="time"
                domain={['dataMin', 'dataMax']}
                tickFormatter={(value) => formatAxisTick(value, chartSpanMs)}
                minTickGap={40}
                stroke="#9ca3af"
                style={{ fontSize: '0.875rem' }}
              />
              <YAxis stroke="#9ca3af" style={{ fontSize: '0.875rem' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                }}
                formatter={(value) => [
                  typeof value === 'number' ? value.toFixed(2) : value,
                  '',
                ]}
                labelFormatter={(value) => formatTooltipLabel(value)}
                labelStyle={{ color: '#000' }}
              />
              <Legend wrapperStyle={{ paddingTop: '1rem' }} iconType="line" />
              {selectedPointIds.map((pointId) => {
                const colorIdx = uniquePoints.indexOf(pointId)
                return (
                  <Line
                    key={pointId}
                    type="monotone"
                    dataKey={`${pointId}_value`}
                    stroke={CHART_COLORS[colorIdx % CHART_COLORS.length]}
                    dot={false}
                    strokeWidth={2}
                    isAnimationActive={false}
                    name={pointNameMap.get(pointId) || pointId}
                  />
                )
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-6 text-center text-neutral-500">
          Wybierz pomiar aby wyświetlić wykres
        </div>
      )}
    </div>
  )
}
