import { useCrudPageState } from '@/hooks/useCrudPageState';
import { useDevices, useAssignDevice, useUpdateDevice, useDeleteDevice } from '@/hooks/useDevices';
import { useActivePermissions } from '@/hooks/useActivePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Plus, Pencil, Unlink, Cpu } from 'lucide-react';
import type { Device, DeviceAssignRequest, DeviceUpdateRequest } from '@/types/coreData';
import { DeviceFormDialog, type DeviceFormData } from '@/components/dialogs/DeviceFormDialog';

export function DevicesPage() {
  const { data: devices = [], isLoading } = useDevices();
  const assignMutation = useAssignDevice();
  const updateMutation = useUpdateDevice();
  const deleteMutation = useDeleteDevice();
  const { hasPermission } = useActivePermissions();
  const canManage = hasPermission('CAN_MANAGE_ASSETS');

  const crud = useCrudPageState<string, DeviceFormData, DeviceAssignRequest, DeviceUpdateRequest>({
    createMutation: assignMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Urządzenie przypisane',
      updateSuccess: 'Urządzenie zaktualizowane',
      deleteSuccess: 'Urządzenie odłączone od organizacji',
      createErrorFallback: 'Błąd przy przypisywaniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy odłączaniu',
    },
    toCreateInput: (data) => ({
      serial_number: data.external_id ?? '',
      water_object_id: data.water_object_id ?? '',
    }),
    toUpdateInput: (data) => {
      const updateData: DeviceUpdateRequest = {};
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
    ...(canManage
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: Device) => (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => crud.openEdit(row.id)}
                  aria-label={`Edytuj urządzenie ${row.external_id}`}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => crud.requestDelete(row.id)}
                  aria-label={`Odłącz urządzenie ${row.external_id}`}
                >
                  <Unlink className="h-4 w-4" />
                </Button>
              </div>
            ),
          },
        ]
      : []),
  ];

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Urządzenia</h1>
          <p className="text-neutral-600">Zarządzanie urządzeniami pomiarowymi</p>
        </div>
        {canManage && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Przypisz urządzenie
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={devices}
            isLoading={isLoading}
            emptyState={canManage ? {
              icon: <Cpu className="h-12 w-12" />,
              title: 'Brak urządzeń',
              subtitle: 'Zacznij od przypisania pierwszego urządzenia',
              ctaLabel: 'Przypisz urządzenie',
              onCta: () => crud.openCreate(),
            } : undefined}
          />
        </CardContent>
      </Card>

      {canManage && (
        <>
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
            title="Odłącz urządzenie"
            description="Urządzenie powróci do puli nieprzypisanych"
            message="Czy chcesz odłączyć to urządzenie od organizacji? Będzie dostępne do przypisania innym organizacjom."
            confirmText="Odłącz"
            cancelText="Anuluj"
            isLoading={crud.isDeleting}
            onConfirm={crud.confirmDelete}
          />
        </>
      )}
    </div>
  );
}
