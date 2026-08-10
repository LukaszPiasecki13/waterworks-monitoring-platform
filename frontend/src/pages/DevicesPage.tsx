import { useState } from 'react';
import { useDevices, useCreateDevice, useUpdateDevice, useDeleteDevice } from '@/hooks/useDevices';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { toast } from '@/components/ui/Toast';
import { Plus, Pencil, Trash2, Key } from 'lucide-react';
import type { Device } from '@/types/coreData';
import { DeviceFormDialog } from '@/components/dialogs/DeviceFormDialog';
import { DeviceSecretRevealDialog } from '@/components/dialogs/DeviceSecretRevealDialog';

export function DevicesPage() {
  const { data: devices = [], isLoading } = useDevices();
  const createMutation = useCreateDevice();
  const updateMutation = useUpdateDevice();
  const deleteMutation = useDeleteDevice();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [revealSecretId, setRevealSecretId] = useState<string | null>(null);
  const [revealSecret, setRevealSecret] = useState<string | null>(null);

  const handleCreate = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: (response) => {
        setIsFormOpen(false);
        toast.success('Urządzenie utworzone');
        if (response.plain_secret) {
          setRevealSecretId(response.id.toString());
          setRevealSecret(response.plain_secret);
        }
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
            toast.success('Urządzenie zaktualizowane');
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
          toast.success('Urządzenie usunięte');
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
      render: (row: Device) => row.name,
    },
    {
      key: 'device_type',
      label: 'Typ',
      render: (row: Device) => row.device_type || '—',
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: Device) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setRevealSecretId(row.id)}
            title="Pokaż sekret"
          >
            <Key className="h-4 w-4" />
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
          <h1 className="text-3xl font-bold text-neutral-900">Urządzenia</h1>
          <p className="text-neutral-600">Zarządzanie urządzeniami pomiarowymi</p>
        </div>
        <Button onClick={() => { setEditingId(null); setIsFormOpen(true); }}>
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
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        deviceId={editingId}
        onSubmit={editingId ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <DeviceSecretRevealDialog
        open={!!revealSecretId}
        onOpenChange={(open) => {
          if (!open) {
            setRevealSecretId(null);
            setRevealSecret(null);
          }
        }}
        deviceId={revealSecretId}
        secret={revealSecret}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń urządzenie"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć to urządzenie?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  );
}
