import { Star, MoreVertical, Edit, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { StatusPill } from '@/components/ui/StatusPill'
import { FreshnessBar } from '@/components/ui/FreshnessBar'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/DropdownMenu'

import type { WaterObject } from '@/types/coreData'
import type { ObjectSummary } from '@/types/telemetry'
import type { ObjectStatus } from '@/lib/statusConfig'

export interface ObjectCardProps {
  object: WaterObject
  telemetry: ObjectSummary | null
  isPinned: boolean
  onTogglePin: (objectId: string) => void
  onNavigate: (objectId: string) => void
  canManage?: boolean
  onEdit?: (objectId: string) => void
  onDelete?: (objectId: string) => void
}

export function ObjectCard({
  object,
  telemetry,
  isPinned,
  onTogglePin,
  onNavigate,
  canManage = false,
  onEdit,
  onDelete,
}: ObjectCardProps) {
  const handleStarClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onTogglePin(object.id)
  }

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit?.(object.id)
  }

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.(object.id)
  }

  const handleCardClick = () => {
    onNavigate(object.id)
  }

  const status = (telemetry?.status || 'no_data') as ObjectStatus

  return (
    <Card
      className="cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-[1.02] group"
      onClick={handleCardClick}
    >
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex-1 min-w-0">
          <CardTitle className="text-base truncate">{object.name}</CardTitle>
        </div>
        <div className="flex-shrink-0 ml-2 flex gap-1">
          <button
            type="button"
            onClick={handleStarClick}
            className="p-1 text-neutral-400 hover:text-brand-500 transition-colors"
            title={isPinned ? 'Odepnij' : 'Przypnij'}
          >
            <Star
              size={20}
              fill={isPinned ? 'currentColor' : 'none'}
              className={isPinned ? 'text-brand-500' : ''}
            />
          </button>
          {canManage && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="px-2 py-1 rounded-md border border-neutral-200 hover:bg-neutral-50 text-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                  aria-label={`Menu zarządzania obiektem ${object.name}`}
                >
                  <MoreVertical className="h-4 w-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleEditClick}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edytuj
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDeleteClick}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Usuń
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <div>
          <div className="text-xs text-neutral-500 mb-1">Status</div>
          <StatusPill kind="objectStatus" value={status} />
        </div>

        <div>
          <div className="text-xs text-neutral-500 mb-1">Typ obiektu</div>
          <p className="text-sm font-medium text-neutral-700">{object.object_type}</p>
        </div>

        {telemetry && telemetry.points && telemetry.points.length > 0 && (
          <div>
            <div className="text-xs text-neutral-500 mb-2">Metryki</div>
            <div className="space-y-1">
              {telemetry.points.slice(0, 2).map((point) => (
                <div key={point.point_id} className="flex justify-between text-sm">
                  <span className="text-neutral-600">{point.point_name}:</span>
                  <span className="font-medium text-neutral-900">
                    {point.value} {point.unit}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {telemetry && telemetry.last_contact_at && (
          <div>
            <div className="text-xs text-neutral-500 mb-1">Świeżość danych</div>
            <FreshnessBar lastContactAt={new Date(telemetry.last_contact_at)} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
