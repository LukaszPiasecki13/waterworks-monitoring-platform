import { usePlatformDevice } from '@/hooks/useDevices';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerClose, DrawerBody } from '@/components/ui/Drawer';
import { Badge } from '@/components/ui/Badge';
import { formatRelativeTime } from '@/lib/deviceFreshness';

interface DeviceDetailDrawerProps {
  deviceId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeviceDetailDrawer({ deviceId, open, onOpenChange }: DeviceDetailDrawerProps) {
  const { data: device, isLoading } = usePlatformDevice(deviceId || '');

  if (!device) return null;

  const credentialBadgeVariant = () => {
    switch (device.credential_status) {
      case 'claimed':
        return 'success';
      case 'unclaimed':
        return 'neutral';
      case 'revoked':
        return 'danger';
      default:
        return 'neutral';
    }
  };

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
                {device.organization_name} · {device.water_object_name}
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
            {/* Tożsamość & Provisioning */}
            <div>
              <h5 className="font-semibold text-neutral-900 mb-4">Tożsamość & Provisioning</h5>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-neutral-600">Status poświadczenia</dt>
                  <dd className="mt-1">
                    <Badge variant={credentialBadgeVariant()}>
                      {device.credential_status || 'unknown'}
                    </Badge>
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Aktywowano</dt>
                  <dd className="text-neutral-900">{formatDateTime(device.claimed_at)}</dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Dodano do systemu</dt>
                  <dd className="text-neutral-900">{formatDateTime(device.created_at)}</dd>
                </div>
              </dl>
            </div>

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
                  <dd className="text-neutral-900">{device.organization_name || '—'}</dd>
                </div>
              </dl>
            </div>

            {/* Punkty pomiarowe */}
            {device.measurement_points && device.measurement_points.length > 0 && (
              <div>
                <h5 className="font-semibold text-neutral-900 mb-4">Punkty pomiarowe</h5>
                <ul className="space-y-2 text-sm">
                  {device.measurement_points.map((point) => (
                    <li key={point.id} className="text-neutral-900 border-l-2 border-neutral-300 pl-3">
                      <strong>{point.point_type}</strong> — {point.unit} · zakres{' '}
                      {point.min_technical}–{point.max_technical} ·{' '}
                      {point.is_active ? 'aktywny' : 'nieaktywny'}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Lokalizacja */}
            {(device.location_description || device.latitude || device.longitude) && (
              <div>
                <h5 className="font-semibold text-neutral-900 mb-4">Lokalizacja obiektu</h5>
                <dl className="space-y-3 text-sm">
                  <div>
                    <dt className="text-neutral-600">Adres</dt>
                    <dd className="text-neutral-900">{device.location_description || '—'}</dd>
                  </div>
                  {(device.latitude || device.longitude) && (
                    <div>
                      <dt className="text-neutral-600">Koordynaty</dt>
                      <dd className="text-neutral-900">
                        {device.latitude}°N {device.longitude}°E{' '}
                        {device.latitude && device.longitude && (
                          <a
                            href={`https://www.google.com/maps?q=${device.latitude},${device.longitude}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-500 hover:underline"
                          >
                            mapy
                          </a>
                        )}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            )}
          </DrawerBody>
        )}
      </DrawerContent>
    </Drawer>
  );
}
