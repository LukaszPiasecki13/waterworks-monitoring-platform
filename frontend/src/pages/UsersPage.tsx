import { useState } from 'react';
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '@/hooks/useUsers';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { toast } from '@/components/ui/Toast';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import type { ManagedUser } from '@/types/coreData';
import { UserFormDialog } from '@/components/dialogs/UserFormDialog';

export function UsersPage() {
  const { data: users = [], isLoading } = useUsers();
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();
  const deleteMutation = useDeleteUser();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const handleCreate = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setIsFormOpen(false);
        toast.success('Użytkownik utworzony');
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
            toast.success('Użytkownik zaktualizowany');
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
          toast.success('Użytkownik usunięty');
        },
        onError: (error: any) => {
          toast.error(error.message || 'Błąd przy usuwaniu');
        },
      });
    }
  };

  const columns = [
    {
      key: 'username',
      label: 'Nazwa użytkownika',
      render: (row: ManagedUser) => row.username,
    },
    {
      key: 'email',
      label: 'Email',
      render: (row: ManagedUser) => row.email,
    },
    {
      key: 'status',
      label: 'Status',
      render: (row: ManagedUser) => row.status || '—',
    },
    {
      key: 'is_active',
      label: 'Aktywny',
      render: (row: ManagedUser) => row.is_active ? '✓' : '✗',
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: ManagedUser) => (
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
          <h1 className="text-3xl font-bold text-neutral-900">Użytkownicy</h1>
          <p className="text-neutral-600">Zarządzanie użytkownikami systemu</p>
        </div>
        <Button onClick={() => { setEditingId(null); setIsFormOpen(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Nowy użytkownik
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={users}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <UserFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        userId={editingId}
        onSubmit={editingId ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń użytkownika"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć tego użytkownika?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  );
}
