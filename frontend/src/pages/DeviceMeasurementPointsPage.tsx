import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
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
import { toast } from '@/components/ui/Toast'
import { ChevronLeft, Plus, Pencil, Trash2 } from 'lucide-react'
import type { MeasurementPoint, MeasurementPointCreateRequest, MeasurementPointUpdateRequest } from '@/types/coreData'
import { DeviceMeasurementPointFormDialog } from '@/components/dialogs/DeviceMeasurementPointFormDialog'

export function DeviceMeasurementPointsPage() {
  const { deviceId } = useParams<{ deviceId: string }>()
  const navigate = useNavigate()
  const { data: allPoints = [], isLoading } = useMeasurementPoints()
  const createMutation = useCreateMeasurementPoint()
  const updateMutation = useUpdateMeasurementPoint()
  const deleteMutation = useDeleteMeasurementPoint()

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  if (!deviceId) {
    return (
      <div className="px-6 py-8">
        <div className="text-red-600">Brakuje ID urządzenia</div>
      </div>
    )
  }

  const devicePoints = useMemo(
    () => allPoints.filter((p) => p.device_id === deviceId),
    [allPoints, deviceId]
  )
  const editingPoint = editingId ? devicePoints.find((p) => p.id === editingId) : undefined

  const handleCreate = (data: MeasurementPointCreateRequest | MeasurementPointUpdateRequest) => {
    createMutation.mutate(data as MeasurementPointCreateRequest, {
      onSuccess: () => {
        setIsFormOpen(false)
        toast.success('Punkt pomiarowy utworzony')
      },
      onError: (error: any) => {
        toast.error(error.message || 'Błąd przy tworzeniu')
      },
    })
  }

  const handleUpdate = (data: MeasurementPointCreateRequest | MeasurementPointUpdateRequest) => {
    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data: data as MeasurementPointUpdateRequest },
        {
          onSuccess: () => {
            setIsFormOpen(false)
            setEditingId(null)
            toast.success('Punkt pomiarowy zaktualizowany')
          },
          onError: (error: any) => {
            toast.error(error.message || 'Błąd przy aktualizacji')
          },
        }
      )
    }
  }

  const handleDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId, {
        onSuccess: () => {
          setDeleteId(null)
          toast.success('Punkt pomiarowy usunięty')
        },
        onError: (error: any) => {
          toast.error(error.message || 'Błąd przy usuwaniu')
        },
      })
    }
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
        <span className={row.is_active ? 'text-green-600 font-medium' : 'text-gray-400'}>
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
            onClick={() => {
              setEditingId(row.id)
              setIsFormOpen(true)
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDeleteId(row.id)}
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
            <h1 className="text-3xl font-bold text-gray-900">Punkty pomiarowe urządzenia</h1>
            <p className="text-gray-600 mt-2">
              Urządzenie: <span className="font-mono text-sm">{deviceId}</span>
            </p>
          </div>
          <Button onClick={() => setIsFormOpen(true)}>
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
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setEditingId(null)
        }}
        onSubmit={editingId ? handleUpdate : handleCreate}
        device_id={deviceId}
        initialData={editingPoint}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń punkt pomiarowy?"
        message="Ta operacja nie może być cofnięta."
        onConfirm={handleDelete}
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
