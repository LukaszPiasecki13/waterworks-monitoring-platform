import { useCrudPageState } from '@/hooks/useCrudPageState';
import { useOrganizations, useCreateOrganization, useUpdateOrganization, useDeleteOrganization } from '@/hooks/useOrganizations';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { Organization } from '@/types/coreData';
import { OrganizationFormDialog, type OrganizationFormData } from '@/components/dialogs/OrganizationFormDialog';

export function OrganizationsPage() {
  const { data: organizations = [], isLoading } = useOrganizations();
  const createMutation = useCreateOrganization();
  const updateMutation = useUpdateOrganization();
  const deleteMutation = useDeleteOrganization();

  const crud = useCrudPageState<string, OrganizationFormData>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Organizacja utworzona',
      updateSuccess: 'Organizacja zaktualizowana',
      deleteSuccess: 'Organizacja usunięta',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
  });

  const columns = [
    {
      key: 'name',
      label: 'Nazwa',
      render: (row: Organization) => row.name,
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: Organization) => (
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
          <h1 className="text-3xl font-bold text-neutral-900">Organizacje</h1>
          <p className="text-neutral-600">Zarządzanie organizacjami i ich użytkownikami</p>
        </div>
        <Button onClick={crud.openCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Nowa organizacja
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={organizations}
            isLoading={isLoading}
            onRowClick={(row) => crud.openEdit(row.id)}
          />
        </CardContent>
      </Card>

      <OrganizationFormDialog
        open={crud.isFormOpen}
        onOpenChange={crud.setIsFormOpen}
        organizationId={crud.editingId}
        onSubmit={crud.handleSubmit}
        isLoading={crud.isSubmitting}
        serverFieldErrors={crud.serverFieldErrors}
      />

      <ConfirmDialog
        open={!!crud.deleteId}
        onOpenChange={(open) => !open && crud.cancelDelete()}
        title="Usuń organizację"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć tę organizację?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={crud.isDeleting}
        onConfirm={crud.confirmDelete}
      />
    </div>
  );
}
