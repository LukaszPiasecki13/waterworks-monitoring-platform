import { useNavigate } from 'react-router-dom';
import { useCrudPageState } from '@/hooks/useCrudPageState';
import { useWaterObjects, useCreateWaterObject, useUpdateWaterObject, useDeleteWaterObject } from '@/hooks/useWaterObjects';
import { useActivePermissions } from '@/hooks/useActivePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Plus, Pencil, Trash2, Eye, Droplet } from 'lucide-react';
import type { WaterObject, WaterObjectCreateRequest, WaterObjectUpdateRequest } from '@/types/coreData';
import { WaterObjectFormDialog, type WaterObjectFormData } from '@/components/dialogs/WaterObjectFormDialog';

export function WaterObjectsPage() {
  const navigate = useNavigate();
  const { data: objects = [], isLoading } = useWaterObjects();
  const createMutation = useCreateWaterObject();
  const updateMutation = useUpdateWaterObject();
  const deleteMutation = useDeleteWaterObject();
  const { hasPermission } = useActivePermissions();
  const canManage = hasPermission('CAN_MANAGE_ASSETS');

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
  });

  const columns = [
    {
      key: 'name',
      label: 'Nazwa',
      render: (row: WaterObject) => row.name,
    },
    {
      key: 'object_type',
      label: 'Typ',
      render: (row: WaterObject) => row.object_type || '—',
    },
    ...(canManage
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: WaterObject) => (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/objects/${row.id}`)}
                  aria-label={`Wyświetl szczegóły obiektu ${row.name}`}
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => crud.openEdit(row.id)}
                  aria-label={`Edytuj obiekt ${row.name}`}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => crud.requestDelete(row.id)}
                  aria-label={`Usuń obiekt ${row.name}`}
                >
                  <Trash2 className="h-4 w-4" />
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
          <h1 className="text-3xl font-bold text-neutral-900">Obiekty wodne</h1>
          <p className="text-neutral-600">Zarządzanie obiektami monitorowania sieci wodociągów</p>
        </div>
        {canManage && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Nowy obiekt
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={objects}
            isLoading={isLoading}
            emptyState={canManage ? {
              icon: <Droplet className="h-12 w-12" />,
              title: 'Brak obiektów wodnych',
              subtitle: 'Utwórz pierwszą infrastrukturę do monitorowania',
              ctaLabel: 'Dodaj obiekt',
              onCta: () => crud.openCreate(),
            } : undefined}
          />
        </CardContent>
      </Card>

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
  );
}
