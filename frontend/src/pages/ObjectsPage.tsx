import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelemetryObjects } from '@/hooks/useTelemetryApi'
import { useWaterObjects, useCreateWaterObject, useUpdateWaterObject, useDeleteWaterObject } from '@/hooks/useWaterObjects'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { useGridLayout } from '@/hooks/useGridLayout'
import { useOrgId } from '@/hooks/useOrgId'
import { Button } from '@/components/ui/Button'
import { ObjectsGrid } from '@/components/objects/ObjectsGrid'
import { ObjectsTable } from '@/components/objects/ObjectsTable'
import { WaterObjectFormDialog, type WaterObjectFormData } from '@/components/dialogs/WaterObjectFormDialog'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'

import type { WaterObject, WaterObjectCreateRequest, WaterObjectUpdateRequest } from '@/types/coreData'
import type { ObjectSummary } from '@/types/telemetry'

export function ObjectsPage() {
  const orgId = useOrgId()
  const navigate = useNavigate()
  const { hasPermission } = useActivePermissions()
  const canManage = hasPermission('CAN_MANAGE_ASSETS')

  // API hooks (must be called unconditionally)
  const { data: telemetryData, isError: telemetryError, isLoading: telemetryLoading } = useTelemetryObjects()
  const { data: waterObjects, isError: waterError, isLoading: waterLoading } = useWaterObjects()
  const createMutation = useCreateWaterObject()
  const updateMutation = useUpdateWaterObject()
  const deleteMutation = useDeleteWaterObject()

  // CRUD state
  const crud = useCrudPageState<string, WaterObjectFormData, WaterObjectCreateRequest, WaterObjectUpdateRequest>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Obiekt wodny utworzony',
      updateSuccess: 'Obiekt wodny zaktualizowany',
      deleteSuccess: 'Obiekt wodny usunięty',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
  })

  // Local state
  const [gridMode, setGridMode] = useState(true)
  const [gridState, setGridState] = useState<{ pinnedIds: string[]; order: string[] }>({
    pinnedIds: [],
    order: [],
  })

  // localStorage hook (must be called unconditionally)
  const gridLayout = useGridLayout(orgId)

  useEffect(() => {
    const newState = {
      pinnedIds: gridLayout.getPinnedIds(),
      order: gridLayout.getOrder(),
    }
    if (
      newState.pinnedIds !== gridState.pinnedIds ||
      newState.order !== gridState.order
    ) {
      setGridState(newState)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orgId])

  // Join telemetry + water objects by object_id (must be called unconditionally)
  const mergedObjects = useMemo(() => {
    if (!waterObjects || !telemetryData?.items) return []

    const telemetryMap: Record<string, ObjectSummary> = {}
    telemetryData.items.forEach((item) => {
      telemetryMap[item.object_id] = item
    })

    return waterObjects.map((waterObj: WaterObject) => ({
      ...waterObj,
      telemetry: telemetryMap[waterObj.id] || null,
    }))
  }, [waterObjects, telemetryData])

  // Error handling
  if (telemetryError || waterError) {
    return (
      <div className="px-6 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold">Błąd ładowania danych</h2>
          <p className="text-red-700 mt-1">Nie udało się pobrać danych obiektów. Spróbuj przeładować stronę.</p>
        </div>
      </div>
    )
  }

  // Loading state
  if (telemetryLoading || waterLoading) {
    return (
      <div className="px-6 py-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-neutral-600 mt-4">Ładowanie obiektów...</p>
        </div>
      </div>
    )
  }

  const handleTogglePin = (objectId: string) => {
    const newPinned = gridState.pinnedIds.includes(objectId)
      ? gridState.pinnedIds.filter((id) => id !== objectId)
      : [...gridState.pinnedIds, objectId]
    gridLayout.setPinned(newPinned)
    setGridState((prev) => ({ ...prev, pinnedIds: newPinned }))
  }

  const handleSetOrder = (newOrder: string[]) => {
    gridLayout.setOrder(newOrder)
    setGridState((prev) => ({ ...prev, order: newOrder }))
  }

  const handleNavigate = (objectId: string) => {
    navigate(`/objects/${objectId}`)
  }

  return (
    <div className="px-6 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Obiekty wodne</h1>
          <p className="text-neutral-600 mt-2">
            Pulpit zarządzania obiektami i monitorowaniem w czasie rzeczywistym
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={gridMode ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setGridMode(true)}
          >
            Siatka
          </Button>
          <Button
            variant={!gridMode ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setGridMode(false)}
          >
            Lista
          </Button>
        </div>
      </div>

      {gridMode ? (
        <ObjectsGrid
          objects={mergedObjects}
          pinnedIds={gridState.pinnedIds}
          order={gridState.order}
          onSetOrder={handleSetOrder}
          onTogglePin={handleTogglePin}
          onNavigate={handleNavigate}
          canManage={canManage}
          onEdit={crud.openEdit}
          onDelete={crud.requestDelete}
        />
      ) : (
        <ObjectsTable
          objects={mergedObjects}
          pinnedIds={gridState.pinnedIds}
          onTogglePin={handleTogglePin}
          canManage={canManage}
          onEdit={crud.openEdit}
          onDelete={crud.requestDelete}
        />
      )}

      {canManage && (
        <>
          <WaterObjectFormDialog
            open={crud.isFormOpen}
            onOpenChange={crud.setIsFormOpen}
            waterObjectId={crud.editingId}
            onSubmit={crud.handleSubmit}
            isLoading={crud.isSubmitting}
            serverFieldErrors={crud.serverFieldErrors}
          />

          <ConfirmDialog
            open={!!crud.deleteId}
            onOpenChange={(open) => !open && crud.cancelDelete()}
            title="Usuń obiekt wodny"
            description="Ta akcja nie może być cofnięta."
            message="Czy na pewno chcesz usunąć ten obiekt?"
            confirmText="Usuń"
            cancelText="Anuluj"
            isDestructive
            isLoading={crud.isDeleting}
            onConfirm={crud.confirmDelete}
          />
        </>
      )}
    </div>
  )
}
