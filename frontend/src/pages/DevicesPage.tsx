import { useCrudPageState } from '@/hooks/useCrudPageState';
import { useDevices, useCreateDevice, useUpdateDevice, useDeleteDevice } from '@/hooks/useDevices';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { Device, DeviceCreateRequest, DeviceUpdateRequest } from '@/types/coreData';
import { DeviceFormDialog, type DeviceFormData } from '@/components/dialogs/DeviceFormDialog';

export function DevicesPage() {
  const { data: devices = [], isLoading } = useDevices();
  const createMutation = useCreateDevice();
  const updateMutation = useUpdateDevice();
  const deleteMutation = useDeleteDevice();

  const crud = useCrudPageState<string, DeviceFormData, DeviceCreateRequest, DeviceUpdateRequest, Device>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Urządzenie utworzone',
      updateSuccess: 'Urządzenie zaktualizowane',
      deleteSuccess: 'Urządzenie usunięte',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
    toCreateInput: (data) => ({
      external_id: data.external_id ?? '',
      water_object_id: data.water_object_id ?? '',
      firmware_version: data.firmware_version || undefined,
    }),
    toUpdateInput: (data) => {
      const updateData: DeviceUpdateRequest = {};
      if (data.firmware_version) updateData.firmware_version = data.firmware_version;
      if (data.is_active !== undefined) updateData.is_active = data.is_active;
      return updateData;
    },
  });

  const columns = [
    {
      key: 'external_id',
      label: 'Nazwa',
      render: (row: Device) => row.external_id,
    },
    {
      key: 'firmware_version',
      label: 'Wersja',
      render: (row: Device) => row.firmware_version || '—',
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: Device) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => crud.openEdit(row.id)}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => crud.requestDelete(row.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Urządzenia</h1>
          <p className="text-neutral-600">Zarządzanie urządzeniami pomiarowymi</p>
        </div>
        <Button onClick={crud.openCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Nowe urządzenie
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={devices}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <DeviceFormDialog
        open={crud.isFormOpen}
        onOpenChange={crud.setIsFormOpen}
        deviceId={crud.editingId}
        onSubmit={crud.handleSubmit}
        isLoading={crud.isSubmitting}
        serverFieldErrors={crud.serverFieldErrors}
      />

      <ConfirmDialog
        open={!!crud.deleteId}
        onOpenChange={(open) => !open && crud.cancelDelete()}
        title="Usuń urządzenie"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć to urządzenie?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={crud.isDeleting}
        onConfirm={crud.confirmDelete}
      />
    </div>
  );
}
