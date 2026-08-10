import { useState } from 'react'
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
import {
  useTelemetryObjectDetail,
  useTelemetryMeasurements,
} from '@/hooks/useTelemetryApi'

interface TelemetryDetailChartProps {
  objectId: string
  onClose: () => void
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'ok':
      return 'text-green-600'
    case 'warning':
      return 'text-yellow-600'
    case 'no_comm':
      return 'text-red-600'
    case 'no_data':
      return 'text-gray-600'
    default:
      return 'text-gray-600'
  }
}

function getStatusBg(status: string): string {
  switch (status) {
    case 'ok':
      return 'bg-green-50 border-green-200'
    case 'warning':
      return 'bg-yellow-50 border-yellow-200'
    case 'no_comm':
      return 'bg-red-50 border-red-200'
    case 'no_data':
      return 'bg-gray-50 border-gray-200'
    default:
      return 'bg-gray-50 border-gray-200'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'ok':
      return 'OK ✓'
    case 'warning':
      return 'Ostrzeżenie ⚠'
    case 'no_comm':
      return 'Brak komunikacji ✗'
    case 'no_data':
      return 'Brak danych'
    default:
      return status
  }
}

const CHART_COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4']

const HOUR_MS = 60 * 60 * 1000
const DAY_MS = 24 * HOUR_MS

// Adapts tick labels to how wide the visible time range is
function formatAxisTick(timestamp: number, spanMs: number): string {
  const date = new Date(timestamp)
  if (spanMs <= 26 * HOUR_MS) {
    return date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
  }
  if (spanMs <= 8 * DAY_MS) {
    return date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit' })
      + ' ' + date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
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

export function TelemetryDetailChart({
  objectId,
  onClose,
}: TelemetryDetailChartProps) {
  const { data: detail, isLoading: detailLoading } = useTelemetryObjectDetail(objectId)
  const { data: measurements, isLoading: measurementsLoading } = useTelemetryMeasurements(
    objectId,
    undefined,
    24,
  )
  const [selectedPointIds, setSelectedPointIds] = useState<string[]>([])

  const isLoading = detailLoading || measurementsLoading

  // Merge measurements into one row per timestamp so lines share the X axis
  const chartDataByTimestamp = new Map<number, Record<string, number>>()
  for (const m of measurements?.items || []) {
    const timestamp = new Date(m.measured_at).getTime()
    const row = chartDataByTimestamp.get(timestamp) ?? { timestamp }
    row[`${m.point_id}_value`] = m.value
    chartDataByTimestamp.set(timestamp, row)
  }
  const chartData = [...chartDataByTimestamp.values()].sort(
    (a, b) => a.timestamp - b.timestamp,
  )
  const chartSpanMs =
    chartData.length > 1
      ? chartData[chartData.length - 1].timestamp - chartData[0].timestamp
      : DAY_MS

  // Get unique point IDs
  const uniquePoints = [...new Set((measurements?.items || []).map((i) => i.point_id))]

  // Auto-select first point if none selected
  if (selectedPointIds.length === 0 && uniquePoints.length > 0) {
    setSelectedPointIds([uniquePoints[0]])
  }

  const togglePoint = (pointId: string) => {
    setSelectedPointIds((prev) =>
      prev.includes(pointId)
        ? prev.filter((id) => id !== pointId)
        : [...prev, pointId].slice(-3), // Max 3 lines
    )
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <p className="text-gray-600">Ładowanie danych...</p>
        </div>
      </div>
    )
  }

  if (!detail) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <p className="text-red-600">Nie udało się załadować szczegółów obiektu</p>
          <button
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
          >
            Zamknij
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`border-b ${getStatusBg(detail.status)} p-6`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{detail.object_id}</h2>
              <p className="text-gray-600 mt-1">
                Urządzenie: <span className="font-mono text-sm">{detail.device_id}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ✕
            </button>
          </div>

          {/* Status Badge */}
          <div className={`inline-block px-4 py-2 rounded-full font-medium ${getStatusColor(
            detail.status,
          )}`}>
            {getStatusLabel(detail.status)}
          </div>

          {/* Info */}
          <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
            <div>
              <span className="text-gray-600">Ostatni kontakt:</span>
              <p className="font-medium">
                {detail.last_contact_at
                  ? new Date(detail.last_contact_at).toLocaleString('pl-PL')
                  : 'Brak danych'}
              </p>
            </div>
            <div>
              <span className="text-gray-600">Ostatnia sekwencja:</span>
              <p className="font-medium">{detail.last_seq}</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Point Selector */}
          {uniquePoints.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Pomiary (wybierz do 3):
              </h3>
              <div className="flex flex-wrap gap-2">
                {uniquePoints.map((pointId, idx) => (
                  <button
                    key={pointId}
                    onClick={() => togglePoint(pointId)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      selectedPointIds.includes(pointId)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                    style={
                      selectedPointIds.includes(pointId)
                        ? { backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }
                        : undefined
                    }
                  >
                    {pointId}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Chart */}
          {chartData.length > 0 && selectedPointIds.length > 0 ? (
            <div className="bg-gray-50 p-4 rounded-lg mb-6 h-96">
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
                  <Legend
                    wrapperStyle={{ paddingTop: '1rem' }}
                    iconType="line"
                  />
                  {selectedPointIds.map((pointId, idx) => (
                    <Line
                      key={pointId}
                      type="monotone"
                      dataKey={`${pointId}_value`}
                      stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                      dot={false}
                      strokeWidth={2}
                      isAnimationActive={false}
                      name={pointId}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="bg-gray-50 p-6 rounded-lg text-center text-gray-500 mb-6">
              {measurements?.items.length === 0
                ? 'Brak danych pomiarów dla tego obiektu'
                : 'Wybierz pomiar aby wyświetlić wykres'}
            </div>
          )}

          {/* Latest Values Table */}
          {detail.points.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Ostatnie wartości:</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {detail.points.map((point) => (
                  <div key={point.point_id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <p className="text-xs text-gray-600 mb-1">{point.type}</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {point.value.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {point.unit}
                      {point.quality !== 'good' && (
                        <span className="ml-1 text-yellow-600">• {point.quality}</span>
                      )}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Zamknij
          </button>
        </div>
      </div>
    </div>
  )
}
