import { useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import {
  useMeasurementPoints,
  useCreateMeasurementPoint,
  useUpdateMeasurementPoint,
  useDeleteMeasurementPoint,
} from '@/hooks/useMeasurementPoints'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { ChevronLeft, Plus, Pencil, Trash2 } from 'lucide-react'
import type { MeasurementPoint, MeasurementPointCreateRequest, MeasurementPointUpdateRequest } from '@/types/coreData'
import { DeviceMeasurementPointFormDialog } from '@/components/dialogs/DeviceMeasurementPointFormDialog'

type PointFormData = MeasurementPointCreateRequest | MeasurementPointUpdateRequest

export function DeviceMeasurementPointsPage() {
  const { deviceId } = useParams<{ deviceId: string }>()
  const navigate = useNavigate()
  const { data: allPoints = [], isLoading } = useMeasurementPoints()
  const createMutation = useCreateMeasurementPoint()
  const updateMutation = useUpdateMeasurementPoint()
  const deleteMutation = useDeleteMeasurementPoint()

  const devicePoints = useMemo(
    () => allPoints.filter((p) => p.device_id === deviceId),
    [allPoints, deviceId]
  )

  const crud = useCrudPageState<string, PointFormData, MeasurementPointCreateRequest, MeasurementPointUpdateRequest>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Punkt pomiarowy utworzony',
      updateSuccess: 'Punkt pomiarowy zaktualizowany',
      deleteSuccess: 'Punkt pomiarowy usunięty',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
    toCreateInput: (data) => data as MeasurementPointCreateRequest,
    toUpdateInput: (data) => data as MeasurementPointUpdateRequest,
  })

  const editingPoint = crud.editingId ? devicePoints.find((p) => p.id === crud.editingId) : undefined

  if (!deviceId) {
    return (
      <div className="px-6 py-8">
        <div className="text-red-600">Brakuje ID urządzenia</div>
      </div>
    )
  }

  const columns = [
    {
      key: 'external_id',
      label: 'ID Zewnętrzne',
      render: (row: MeasurementPoint) => row.external_id,
    },
    {
      key: 'point_type',
      label: 'Typ',
      render: (row: MeasurementPoint) => row.point_type,
    },
    {
      key: 'unit',
      label: 'Jednostka',
      render: (row: MeasurementPoint) => row.unit,
    },
    {
      key: 'min_technical',
      label: 'Min',
      render: (row: MeasurementPoint) =>
        row.min_technical !== null ? row.min_technical.toFixed(2) : '—',
    },
    {
      key: 'max_technical',
      label: 'Max',
      render: (row: MeasurementPoint) =>
        row.max_technical !== null ? row.max_technical.toFixed(2) : '—',
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (row: MeasurementPoint) => (
        <span className={row.is_active ? 'text-green-600 font-medium' : 'text-neutral-400'}>
          {row.is_active ? 'Aktywny' : 'Nieaktywny'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: MeasurementPoint) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => crud.openEdit(row.id)}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => crud.requestDelete(row.id)}
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="px-6 py-8">
      <div className="mb-8">
        <Button variant="ghost" onClick={() => navigate('/admin/devices')} className="mb-4">
          <ChevronLeft className="mr-2 h-4 w-4" />
          Wróć do urządzeń
        </Button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900">Punkty pomiarowe urządzenia</h1>
            <p className="text-neutral-600 mt-2">
              Urządzenie: <span className="font-mono text-sm">{deviceId}</span>
            </p>
          </div>
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Dodaj punkt
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Punkty pomiarowe ({devicePoints.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={devicePoints} isLoading={isLoading} />
        </CardContent>
      </Card>

      <DeviceMeasurementPointFormDialog
        isOpen={crud.isFormOpen}
        onClose={() => crud.setIsFormOpen(false)}
        onSubmit={crud.handleSubmit}
        device_id={deviceId}
        initialData={editingPoint}
        isLoading={crud.isSubmitting}
        serverFieldErrors={crud.serverFieldErrors}
      />

      <ConfirmDialog
        open={crud.deleteId !== null}
        onOpenChange={(open) => !open && crud.cancelDelete()}
        title="Usuń punkt pomiarowy?"
        message="Ta operacja nie może być cofnięta."
        onConfirm={crud.confirmDelete}
        isLoading={crud.isDeleting}
      />
    </div>
  )
}
