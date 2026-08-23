import { usePlatformDevices, useDeletePlatformDevice } from '@/hooks/useDevices';
import { useActivePermissions } from '@/hooks/useActivePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Trash2, Cpu } from 'lucide-react';
import type { Device } from '@/types/coreData';
import { useState } from 'react';

export function PlatformDevicesPage() {
  const { data: devices = [], isLoading } = usePlatformDevices();
  const deleteDeviceMutation = useDeletePlatformDevice();
  const { hasPermission } = useActivePermissions();
  const canManage = hasPermission('PLATFORM_MANAGE_DEVICE_PROVISIONING');

  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    try {
      await deleteDeviceMutation.mutateAsync(deleteId);
      setDeleteId(null);
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  const columns = [
    {
      key: 'external_id',
      label: 'Numer seryjny (SN)',
      render: (row: Device) => row.external_id,
    },
    {
      key: 'water_object_id',
      label: 'Przypisany',
      render: (row: Device) => (row.water_object_id ? '✓ Tak' : '✗ Nie'),
    },
    {
      key: 'firmware_version',
      label: 'Wersja firmware',
      render: (row: Device) => row.firmware_version || '—',
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (row: Device) => (row.is_active ? 'Aktywne' : 'Nieaktywne'),
    },
    {
      key: 'last_seen_at',
      label: 'Ostatnio widziane',
      render: (row: Device) => (
        row.last_seen_at ? new Date(row.last_seen_at).toLocaleString('pl-PL') : '—'
      ),
    },
    ...(canManage
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: Device) => (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setDeleteId(row.id)}
                aria-label={`Usuń urządzenie ${row.external_id}`}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            ),
          },
        ]
      : []),
  ];

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Wszystkie urządzenia</h1>
          <p className="text-neutral-600">Zarządzanie urządzeniami na platformie</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={devices}
            isLoading={isLoading}
            emptyState={
              canManage
                ? {
                    icon: <Cpu className="h-12 w-12" />,
                    title: 'Brak urządzeń',
                    subtitle: 'Nie ma zarejestrowanych urządzeń na platformie',
                  }
                : undefined
            }
          />
        </CardContent>
      </Card>

      {canManage && (
        <ConfirmDialog
          open={!!deleteId}
          onOpenChange={(open) => !open && setDeleteId(null)}
          title="Usuń urządzenie"
          description="Ta akcja nie może być cofnięta."
          message="Czy na pewno chcesz usunąć to urządzenie? Wszystkie dane związane z tym urządzeniem będą usunięte."
          confirmText="Usuń"
          cancelText="Anuluj"
          isDestructive
          isLoading={deleteDeviceMutation.isPending}
          onConfirm={handleDeleteConfirm}
        />
      )}
    </div>
  );
}
