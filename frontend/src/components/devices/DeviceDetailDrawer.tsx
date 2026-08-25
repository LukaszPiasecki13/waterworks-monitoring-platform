import { usePlatformDevice, useWaterObject, useOrganization } from '@/hooks/useDevices';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerClose, DrawerBody } from '@/components/ui/Drawer';
import { formatRelativeTime } from '@/lib/deviceFreshness';

interface DeviceDetailDrawerProps {
  deviceId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeviceDetailDrawer({ deviceId, open, onOpenChange }: DeviceDetailDrawerProps) {
  const { data: device, isLoading: deviceLoading } = usePlatformDevice(deviceId || '');
  const { data: waterObject } = useWaterObject(device?.water_object_id ?? null);
  const { data: organization } = useOrganization(waterObject?.organization_id ?? null);

  const isLoading = deviceLoading;

  if (!device) return null;

  const formatDateTime = (iso: string | null) => {
    if (!iso) return '—';
    const date = new Date(iso);
    return `${date.toLocaleDateString('pl-PL')} · ${date.toLocaleTimeString('pl-PL')}`;
  };

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>
            <div>
              <div className="font-mono text-sm">{device.external_id}</div>
              <div className="text-xs text-neutral-600 font-normal mt-1">
                {organization?.name || '—'}
              </div>
            </div>
          </DrawerTitle>
          <DrawerClose />
        </DrawerHeader>

        {isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-neutral-200 rounded animate-pulse" />
            ))}
          </div>
        ) : (
          <DrawerBody>
            {/* Łączność & Zdrowie */}
            <div>
              <h5 className="font-semibold text-neutral-900 mb-4">Łączność & Zdrowie</h5>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-neutral-600">Ostatni kontakt</dt>
                  <dd className="text-neutral-900">
                    {formatRelativeTime(device.last_seen_at)} · {formatDateTime(device.last_seen_at)}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Sygnał modemu (RSSI)</dt>
                  <dd className="text-neutral-600">— <em className="text-xs">(wymaga firmware)</em></dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Ostatni reset</dt>
                  <dd className="text-neutral-600">— <em className="text-xs">(wymaga firmware)</em></dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Uptime</dt>
                  <dd className="text-neutral-600">— <em className="text-xs">(wymaga firmware)</em></dd>
                </div>
              </dl>
            </div>

            {/* Konfiguracja */}
            <div>
              <h5 className="font-semibold text-neutral-900 mb-4">Konfiguracja urządzenia</h5>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-neutral-600">Firmware</dt>
                  <dd className="text-neutral-900 font-mono">{device.firmware_version || '—'}</dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Aktywne</dt>
                  <dd className="text-neutral-900">{device.is_active ? 'Tak' : 'Nie'}</dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Organizacja</dt>
                  <dd className="text-neutral-900">{organization?.name || '—'}</dd>
                </div>
              </dl>
            </div>
          </DrawerBody>
        )}
      </DrawerContent>
    </Drawer>
  );
}
