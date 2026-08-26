import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import { DataTable } from '@/components/ui/DataTable'
import { StatusPill } from '@/components/ui/StatusPill'
import { FreshnessBar } from '@/components/ui/FreshnessBar'
import { formatTimeAgo } from '@/components/ui/freshnessUtils'
import { Button } from '@/components/ui/Button'
import { Star, MoreVertical, Edit, Trash2, Plus } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/DropdownMenu'

import type { WaterObject } from '@/types/coreData'
import type { ObjectSummary } from '@/types/telemetry'
import type { ObjectStatus } from '@/lib/statusConfig'

interface ColumnDef<T> {
  key: keyof T | string
  label: string
  width?: string
  render?: (row: T, index: number) => React.ReactNode
  sortable?: boolean
}

type ObjectRow = WaterObject & { telemetry: ObjectSummary | null }

export interface ObjectsTableProps {
  objects: ObjectRow[]
  pinnedIds: string[]
  onTogglePin: (objectId: string) => void
  canManage?: boolean
  onEdit?: (objectId: string) => void
  onDelete?: (objectId: string) => void
}

export function ObjectsTable({ objects, pinnedIds, onTogglePin, canManage = false, onEdit, onDelete }: ObjectsTableProps) {
  const navigate = useNavigate()

  const columns: ColumnDef<ObjectRow>[] = [
    {
      key: 'name',
      label: 'Nazwa',
      width: '200px',
      render: (row: ObjectRow) => (
        <div className="flex items-center gap-2">
          <button
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation()
              onTogglePin(row.id)
            }}
            className="p-1 text-neutral-400 hover:text-brand-500 transition-colors"
            title={pinnedIds.includes(row.id) ? 'Odepnij' : 'Przypnij'}
          >
            <Star
              size={16}
              fill={pinnedIds.includes(row.id) ? 'currentColor' : 'none'}
              className={pinnedIds.includes(row.id) ? 'text-brand-500' : ''}
            />
          </button>
          <span>{row.name}</span>
        </div>
      ),
    },
    {
      key: 'object_type',
      label: 'Typ',
      width: '120px',
    },
    {
      key: 'status',
      label: 'Status',
      width: '120px',
      render: (row: ObjectRow) => {
        const status = (row.telemetry?.status || 'no_data') as ObjectStatus
        return <StatusPill kind="objectStatus" value={status} />
      },
    },
    {
      key: 'pressure',
      label: 'Ciśnienie',
      width: '120px',
      render: (row: ObjectRow) => {
        const pressure = row.telemetry?.points?.find(
          (p: typeof row.telemetry.points[0]) => p.type === 'pressure'
        )
        return pressure ? `${pressure.value} ${pressure.unit}` : '—'
      },
    },
    {
      key: 'temperature',
      label: 'Temperatura',
      width: '120px',
      render: (row: ObjectRow) => {
        const temp = row.telemetry?.points?.find(
          (p: typeof row.telemetry.points[0]) => p.type === 'temperature'
        )
        return temp ? `${temp.value} ${temp.unit}` : '—'
      },
    },
    {
      key: 'freshness',
      label: 'Świeżość',
      width: '150px',
      render: (row: ObjectRow) =>
        row.telemetry?.last_contact_at ? (
          <FreshnessBar lastContactAt={new Date(row.telemetry.last_contact_at)} />
        ) : (
          <span className="text-neutral-400">—</span>
        ),
    },
    {
      key: 'last_contact_at',
      label: 'Ostatni kontakt',
      width: '120px',
      render: (row: ObjectRow) =>
        row.telemetry?.last_contact_at
          ? formatTimeAgo((Date.now() - new Date(row.telemetry.last_contact_at).getTime()) / 1000)
          : '—',
    },
    ...(canManage
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            width: '80px',
            render: (row: ObjectRow) => (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="px-2 py-1 rounded-md border border-neutral-200 hover:bg-neutral-50 text-neutral-600"
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                    aria-label={`Menu zarządzania obiektem ${row.name}`}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation()
                      onEdit?.(row.id)
                    }}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edytuj
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation()
                      onDelete?.(row.id)
                    }}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Usuń
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ),
          },
        ]
      : []),
  ]

  const handleRowClick = (row: ObjectRow) => {
    navigate(`/objects/${row.id}`)
  }

  return (
    <div className="space-y-4">
      {canManage && (
        <Button onClick={() => onEdit?.('')} className="w-full sm:w-auto">
          <Plus className="mr-2 h-4 w-4" />
          Nowy obiekt
        </Button>
      )}
      <DataTable
        columns={columns}
        data={objects}
        onRowClick={handleRowClick}
        emptyMessage="Brak obiektów do wyświetlenia"
      />
    </div>
  )
}
