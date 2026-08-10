import { useTelemetryObjects } from '@/hooks/useTelemetryApi'

interface TelemetryObjectsListProps {
  onSelectObject: (objectId: string) => void
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'ok':
      return 'bg-green-100 text-green-800 border-green-300'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    case 'no_comm':
      return 'bg-red-100 text-red-800 border-red-300'
    case 'no_data':
      return 'bg-gray-100 text-gray-800 border-gray-300'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'ok':
      return '✓ OK'
    case 'warning':
      return '⚠ Ostrzeżenie'
    case 'no_comm':
      return '✗ Brak komunikacji'
    case 'no_data':
      return '— Brak danych'
    default:
      return status
  }
}

export function TelemetryObjectsList({ onSelectObject }: TelemetryObjectsListProps) {
  const { data, isLoading, error } = useTelemetryObjects()

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Błąd ładowania obiektów: {error instanceof Error ? error.message : 'Nieznany błąd'}
      </div>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center text-gray-500">
        Brak danych telemetrii
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {data.items.map((obj) => (
        <button
          key={obj.object_id}
          onClick={() => onSelectObject(obj.object_id)}
          className="w-full text-left p-4 bg-white border border-gray-200 rounded-lg hover:border-blue-400 hover:shadow-md transition-all"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{obj.object_id}</h3>
              <p className="text-sm text-gray-500">
                Urządzenie: {obj.device_id} • Org: {obj.org_id}
              </p>
              {obj.last_contact_at && (
                <p className="text-xs text-gray-400 mt-1">
                  Ostatni kontakt:{' '}
                  {new Date(obj.last_contact_at).toLocaleString('pl-PL')}
                </p>
              )}
            </div>
            <div
              className={`ml-4 px-3 py-1 rounded-full text-sm font-medium border whitespace-nowrap ${getStatusColor(
                obj.status,
              )}`}
            >
              {getStatusLabel(obj.status)}
            </div>
          </div>

          {obj.points.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2">
              {obj.points.map((point) => (
                <div key={point.point_id} className="text-sm">
                  <span className="text-gray-600">{point.type}:</span>{' '}
                  <span className="font-medium text-gray-900">
                    {point.value.toFixed(2)} {point.unit}
                  </span>
                  {point.quality !== 'good' && (
                    <span className="ml-1 text-xs text-yellow-600">({point.quality})</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </button>
      ))}
    </div>
  )
}
