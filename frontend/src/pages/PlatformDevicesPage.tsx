import { useState } from 'react';
import { usePlatformDevices, useDeletePlatformDevice } from '@/hooks/useDevices';
import { useActivePermissions } from '@/hooks/useActivePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Badge } from '@/components/ui/Badge';
import { Trash2, Cpu } from 'lucide-react';
import { toast } from '@/components/ui/Toast';
import { parseApiError } from '@/lib/errors';
import type { Device } from '@/types/coreData';
import { DeviceKpiStrip } from '@/components/devices/DeviceKpiStrip';
import { DeviceFilterBar } from '@/components/devices/DeviceFilterBar';
import { DeviceDetailDrawer } from '@/components/devices/DeviceDetailDrawer';
import { getFreshness, formatRelativeTime } from '@/lib/deviceFreshness';

const PAGE_SIZE = 20;

export function PlatformDevicesPage() {
  const { hasPermission } = useActivePermissions();
  const canManage = hasPermission('PLATFORM_MANAGE_DEVICE_PROVISIONING');
  const deleteDeviceMutation = useDeletePlatformDevice();

  // Filter state
  const [search, setSearch] = useState('');
  const [isActive, setIsActive] = useState<boolean | null>(null);
  const [credentialStatus, setCredentialStatus] = useState<string | null>(null);
  const [assigned, setAssigned] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState('external_id');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);

  // Detail drawer state
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);

  // Delete state
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data: paginatedDevices, isLoading } = usePlatformDevices({
    skip: (page - 1) * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: search || undefined,
    is_active: isActive === null ? undefined : isActive,
    credential_status: credentialStatus ? (credentialStatus as 'unclaimed' | 'claimed' | 'revoked') : undefined,
    assigned: assigned ? (assigned as 'assigned' | 'unassigned') : undefined,
    sort_by: sortBy as 'last_seen_at' | 'created_at' | 'external_id',
    sort_dir: sortDir,
  });

  const devices = paginatedDevices?.items || [];
  const total = paginatedDevices?.total || 0;

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    try {
      await deleteDeviceMutation.mutateAsync(deleteId);
      setDeleteId(null);
      toast.success('Urządzenie usunięte');
    } catch (error) {
      toast.error(parseApiError(error).message);
    }
  };

  const freshnessColors = {
    fresh: 'text-green-600 bg-green-50',
    warn: 'text-yellow-600 bg-yellow-50',
    stale: 'text-red-600 bg-red-50',
    unknown: 'text-neutral-600 bg-neutral-50',
  };

  const columns = [
    {
      key: 'external_id',
      label: 'Urządzenie (SN)',
      sortable: true,
      render: (row: Device) => <span className="text-sm text-neutral-900">{row.external_id}</span>,
    },
    {
      key: 'organization_name',
      label: 'Organizacja / Obiekt',
      render: (row: Device) => (
        <div className="text-sm text-neutral-900">
          {row.organization_name || row.water_object_name ? (
            <>
              <div>{row.organization_name || '—'}</div>
              <div className="text-neutral-600 text-xs">{row.water_object_name || '—'}</div>
            </>
          ) : (
            <span className="text-neutral-600">— nie przypisane —</span>
          )}
        </div>
      ),
    },
    {
      key: 'last_seen_at',
      label: 'Ostatni kontakt',
      sortable: true,
      render: (row: Device) => {
        const freshness = getFreshness(row.last_seen_at);
        const colors = freshnessColors[freshness];
        return (
          <div className={`text-sm font-normal inline-flex items-center gap-2 px-2 py-1 rounded ${colors}`}>
            <span
              className={`w-2 h-2 rounded-full ${
                freshness === 'fresh'
                  ? 'bg-green-600'
                  : freshness === 'warn'
                    ? 'bg-yellow-600'
                    : freshness === 'stale'
                      ? 'bg-red-600'
                      : 'bg-neutral-400'
              }`}
            />
            {formatRelativeTime(row.last_seen_at)}
          </div>
        );
      },
    },
    {
      key: 'firmware_version',
      label: 'Firmware',
      render: (row: Device) => <span className="text-sm text-neutral-900">{row.firmware_version || '—'}</span>,
    },
    {
      key: 'credential_status',
      label: 'Poświadczenie',
      render: (row: Device) => {
        const variant =
          row.credential_status === 'claimed'
            ? 'success'
            : row.credential_status === 'unclaimed'
              ? 'neutral'
              : row.credential_status === 'revoked'
                ? 'danger'
                : 'neutral';
        return <Badge variant={variant}>{row.credential_status || 'unknown'}</Badge>;
      },
    },
    {
      key: 'created_at',
      label: 'Dodane',
      sortable: true,
      render: (row: Device) => (
        <span className="text-sm font-normal text-neutral-900">
          {row.created_at ? new Date(row.created_at).toLocaleDateString('pl-PL') : '—'}
        </span>
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
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteId(row.id);
                }}
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

      <DeviceKpiStrip />

      <Card>
        <DeviceFilterBar
          search={search}
          onSearchChange={setSearch}
          isActive={isActive}
          onIsActiveChange={setIsActive}
          credentialStatus={credentialStatus}
          onCredentialStatusChange={setCredentialStatus}
          assigned={assigned}
          onAssignedChange={setAssigned}
        />

        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={devices}
            isLoading={isLoading}
            currentPage={page}
            totalCount={total}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
            onRowClick={(row) => setSelectedDeviceId(row.id)}
            sortBy={sortBy}
            sortDir={sortDir}
            onSort={(key, dir) => {
              setSortBy(key);
              setSortDir(dir);
              setPage(1);
            }}
            emptyState={
              canManage
                ? {
                    icon: <Cpu className="h-12 w-12" />,
                    title: 'Brak urządzeń',
                    subtitle: 'Nie ma zarejestrowanych urządzeń spełniających kryteria',
                  }
                : undefined
            }
          />
        </CardContent>
      </Card>

      <DeviceDetailDrawer
        deviceId={selectedDeviceId}
        open={!!selectedDeviceId}
        onOpenChange={(open) => !open && setSelectedDeviceId(null)}
      />

      {canManage && (
        <ConfirmDialog
          open={!!deleteId}
          onOpenChange={(open) => !open && setDeleteId(null)}
          title="Usuń urządzenie"
          description="Ta akcja nie może być cofnięta."
          message="Czy na pewno chcesz usunąć to urządzenie? Ta operacja spowoduje: usunięcie wszystkich danych pomiarowych, usunięcie całej historii telemetrii, usunięcie danych logowania urządzenia i zwolnienie numeru seryjnego do ponownej rejestracji."
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
