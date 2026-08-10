import { useState } from 'react'
import { useTelemetryObjects } from '@/hooks/useTelemetryApi'
import { DataTable } from '@/components/ui/DataTable'
import { StatusPill } from '@/components/ui/StatusPill'
import { Button } from '@/components/ui/Button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover'
import type { ObjectSummary } from '@/hooks/useTelemetryApi'
import { formatDistanceToNow } from 'date-fns'
import { pl } from 'date-fns/locale'
import { Filter, X } from 'lucide-react'

interface ObjectsStatusTableProps {
  onSelectObject: (objectId: string) => void
}

export function ObjectsStatusTable({ onSelectObject }: ObjectsStatusTableProps) {
  const { data, isLoading, error } = useTelemetryObjects(50)
  const [skip, setSkip] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const limit = 20

  if (error) {
    return (
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Obiekty monitorowania</h3>
          <p className="text-sm text-gray-600">Błąd ładowania danych</p>
        </div>
        <div className="text-red-600">{String(error)}</div>
      </div>
    )
  }

  if (!data || typeof data !== 'object') {
    return (
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Obiekty monitorowania</h3>
          <p className="text-sm text-gray-600">Błąd struktury danych</p>
        </div>
        <div className="text-red-600">Nieoczekiwany format odpowiedzi: {typeof data}</div>
      </div>
    )
  }

  const objects = Array.isArray(data?.items) ? data.items : []

  // Apply filters
  const filteredObjects = objects.filter((obj) => {
    if (statusFilter && obj.status !== statusFilter) return false
    return true
  })

  const paginatedObjects = filteredObjects.slice(skip, skip + limit)

  // Get unique statuses for filter
  const uniqueStatuses = Array.from(new Set(objects.map((obj) => obj.status)))

  const statusLabels: Record<string, string> = {
    ok: 'OK',
    warning: 'Ostrzeżenie',
    alarm: 'Alarm',
    no_comm: 'Brak komunikacji',
    no_data: 'Brak danych',
  }

  const columns = [
    {
      key: 'name',
      label: 'Nazwa Obiektu',
      render: (row: ObjectSummary) => (
        <button
          onClick={() => onSelectObject(row.object_id)}
          className="text-brand-600 hover:text-brand-700 hover:underline font-medium"
        >
          {row.name}
        </button>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row: ObjectSummary) => (
        <StatusPill kind="objectStatus" value={row.status} />
      ),
    },
    {
      key: 'last_contact_at',
      label: 'Ostatni Kontakt',
      render: (row: ObjectSummary) =>
        row.last_contact_at ? (
          <span className="text-sm text-gray-600">
            {formatDistanceToNow(new Date(row.last_contact_at), {
              addSuffix: true,
              locale: pl,
            })}
          </span>
        ) : (
          <span className="text-sm text-gray-400">—</span>
        ),
    },
    {
      key: 'points_count',
      label: 'Pomiary',
      render: (row: ObjectSummary) => (
        <span className="text-sm text-gray-600">{row.points.length}</span>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Obiekty monitorowania</h3>
          <p className="text-sm text-gray-600">
            {filteredObjects.length > 0
              ? `Wyświetlanie ${filteredObjects.length} z ${objects.length} obiektów`
              : 'Brak obiektów'}
          </p>
        </div>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2">
              <Filter className="h-4 w-4" />
              Filtry
              {statusFilter && <span className="text-xs bg-brand-100 text-brand-700 px-2 py-0.5 rounded">1</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-56">
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-900 mb-2">Status</p>
                <div className="space-y-2">
                  {uniqueStatuses.map((status) => (
                    <label key={status} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={statusFilter === status}
                        onChange={(e) => {
                          setStatusFilter(e.target.checked ? status : null)
                          setSkip(0)
                        }}
                        className="rounded"
                      />
                      <span className="text-sm text-gray-700">{statusLabels[status] || status}</span>
                    </label>
                  ))}
                </div>
              </div>
              {statusFilter && (
                <button
                  onClick={() => {
                    setStatusFilter(null)
                    setSkip(0)
                  }}
                  className="w-full text-sm text-brand-600 hover:text-brand-700 font-medium flex items-center justify-center gap-1 py-1"
                >
                  <X className="h-4 w-4" />
                  Wyczyść filtry
                </button>
              )}
            </div>
          </PopoverContent>
        </Popover>
      </div>

      <DataTable
        columns={columns}
        data={paginatedObjects}
        isLoading={isLoading}
        onRowClick={(row) => onSelectObject(row.object_id)}
      />

      {filteredObjects.length > limit && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Wyświetlanie {Math.min(skip + 1, filteredObjects.length)}–{Math.min(skip + limit, filteredObjects.length)} z {filteredObjects.length}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
            >
              Poprzednia
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= filteredObjects.length}
            >
              Następna
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
