import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWaterObjects, useCreateWaterObject, useUpdateWaterObject, useDeleteWaterObject } from '@/hooks/useWaterObjects';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { toast } from '@/components/ui/Toast';
import { Plus, Pencil, Trash2, Eye } from 'lucide-react';
import type { WaterObject } from '@/types/coreData';
import { WaterObjectFormDialog } from '@/components/dialogs/WaterObjectFormDialog';

export function WaterObjectsPage() {
  const navigate = useNavigate();
  const { data: objects = [], isLoading } = useWaterObjects();
  const createMutation = useCreateWaterObject();
  const updateMutation = useUpdateWaterObject();
  const deleteMutation = useDeleteWaterObject();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleCreate = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setIsFormOpen(false);
        toast.success('Obiekt wodny utworzony');
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
            toast.success('Obiekt wodny zaktualizowany');
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
          toast.success('Obiekt wodny usunięty');
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
      render: (row: WaterObject) => row.name,
    },
    {
      key: 'object_type',
      label: 'Typ',
      render: (row: WaterObject) => row.object_type || '—',
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: WaterObject) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/objects/${row.id}`)}
            title="Wyświetl szczegóły"
          >
            <Eye className="h-4 w-4" />
          </Button>
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
          <h1 className="text-3xl font-bold text-neutral-900">Obiekty wodne</h1>
          <p className="text-neutral-600">Zarządzanie obiektami monitorowania sieci wodociągów</p>
        </div>
        <Button onClick={() => { setEditingId(null); setIsFormOpen(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Nowy obiekt
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={objects}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <WaterObjectFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        waterObjectId={editingId}
        onSubmit={editingId ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń obiekt wodny"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć ten obiekt?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  );
}
