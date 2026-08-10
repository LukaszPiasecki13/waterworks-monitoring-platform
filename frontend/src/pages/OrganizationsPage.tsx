import { useState } from 'react';
import { useOrganizations, useCreateOrganization, useUpdateOrganization, useDeleteOrganization } from '@/hooks/useOrganizations';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { toast } from '@/components/ui/Toast';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { Organization } from '@/types/coreData';
import { OrganizationFormDialog } from '@/components/dialogs/OrganizationFormDialog';

export function OrganizationsPage() {
  const { data: organizations = [], isLoading } = useOrganizations();
  const createMutation = useCreateOrganization();
  const updateMutation = useUpdateOrganization();
  const deleteMutation = useDeleteOrganization();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleCreate = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setIsFormOpen(false);
        toast.success('Organizacja utworzona');
      },
      onError: (error: any) => {
        toast.error(error.message || 'Błąd przy tworzeniu');
      },
    });
  };

  const handleUpdate = (data: any) => {
    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data },
        {
          onSuccess: () => {
            setIsFormOpen(false);
            setEditingId(null);
            toast.success('Organizacja zaktualizowana');
          },
          onError: (error: any) => {
            toast.error(error.message || 'Błąd przy aktualizacji');
          },
        }
      );
    }
  };

  const handleDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId, {
        onSuccess: () => {
          setDeleteId(null);
          toast.success('Organizacja usunięta');
        },
        onError: (error: any) => {
          toast.error(error.message || 'Błąd przy usuwaniu');
        },
      });
    }
  };

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
            onClick={() => {
              setEditingId(row.id);
              setIsFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setDeleteId(row.id)}
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
        <Button onClick={() => { setEditingId(null); setIsFormOpen(true); }}>
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
            onRowClick={(row) => {
              setEditingId(row.id.toString());
              setIsFormOpen(true);
            }}
          />
        </CardContent>
      </Card>

      <OrganizationFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        organizationId={editingId}
        onSubmit={editingId ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń organizację"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć tę organizację?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  );
}
