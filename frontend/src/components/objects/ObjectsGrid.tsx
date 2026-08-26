import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import { SortableContext, useSortable, rectSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Card, CardContent } from '@/components/ui/Card'
import { Plus } from 'lucide-react'
import { ObjectCard } from './ObjectCard'

import type { WaterObject } from '@/types/coreData'
import type { ObjectSummary } from '@/types/telemetry'

export interface ObjectsGridProps {
  objects: Array<WaterObject & { telemetry: ObjectSummary | null }>
  pinnedIds: string[]
  order?: string[]
  onSetOrder: (newOrder: string[]) => void
  onTogglePin: (objectId: string) => void
  onNavigate: (objectId: string) => void
  canManage?: boolean
  onEdit?: (objectId: string) => void
  onDelete?: (objectId: string) => void
}

interface SortableItemProps {
  id: string
  children: React.ReactNode
}

function SortableItem({ id, children }: SortableItemProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
    >
      {children}
    </div>
  )
}

export function ObjectsGrid({
  objects,
  pinnedIds,
  order = [],
  onSetOrder,
  onTogglePin,
  onNavigate,
  canManage = false,
  onEdit,
  onDelete,
}: ObjectsGridProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  // Sort objects: pinned first, then by persisted drag order, then rest
  const sortedObjects = [...objects].sort((a, b) => {
    const aIsPinned = pinnedIds.includes(a.id)
    const bIsPinned = pinnedIds.includes(b.id)
    if (aIsPinned !== bIsPinned) return aIsPinned ? -1 : 1

    const aIndex = order.indexOf(a.id)
    const bIndex = order.indexOf(b.id)
    if (aIndex === -1 && bIndex === -1) return 0
    if (aIndex === -1) return 1
    if (bIndex === -1) return -1
    return aIndex - bIndex
  })

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    const activeIndex = sortedObjects.findIndex((obj) => obj.id === active.id)
    const overIndex = sortedObjects.findIndex((obj) => obj.id === over.id)

    if (activeIndex === -1 || overIndex === -1) return

    const newSorted = [...sortedObjects]
    const [movedItem] = newSorted.splice(activeIndex, 1)
    newSorted.splice(overIndex, 0, movedItem)

    const newOrder = newSorted.map((obj) => obj.id)
    onSetOrder(newOrder)
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext
        items={sortedObjects.map((obj) => obj.id)}
        strategy={rectSortingStrategy}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {sortedObjects.map((obj) => (
            <SortableItem key={obj.id} id={obj.id}>
              <ObjectCard
                object={obj}
                telemetry={obj.telemetry}
                isPinned={pinnedIds.includes(obj.id)}
                onTogglePin={onTogglePin}
                onNavigate={onNavigate}
                canManage={canManage}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            </SortableItem>
          ))}
          {canManage && (
            <Card className="cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-[1.02] flex items-center justify-center min-h-[200px] opacity-0 hover:opacity-100 bg-neutral-50 border-2 border-dashed border-neutral-300" onClick={() => onEdit?.('')}>
              <CardContent className="flex flex-col items-center justify-center gap-2 p-6">
                <div className="rounded-full bg-brand-50 p-3">
                  <Plus className="h-6 w-6 text-brand-600" />
                </div>
                <span className="text-sm font-medium text-neutral-700">Dodaj nowy obiekt</span>
              </CardContent>
            </Card>
          )}
        </div>
      </SortableContext>
    </DndContext>
  )
}
