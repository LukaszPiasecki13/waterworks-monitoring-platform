import { usePlatformDevice, useWaterObject, useOrganization } from '@/hooks/useDevices';
import { deviceSectionData, findSection, usePlatformDeviceState } from '@/hooks/useDeviceState';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerClose, DrawerBody } from '@/components/ui/Drawer';
import { Badge } from '@/components/ui/Badge';
import { formatRelativeTime } from '@/lib/deviceFreshness';
import {
  bufferFillPercent,
  formatAge,
  formatBytes,
  formatRestartReason,
  formatUptime,
  rssiLevel,
} from '@/lib/deviceState';

interface DeviceDetailDrawerProps {
  deviceId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeviceDetailDrawer({ deviceId, open, onOpenChange }: DeviceDetailDrawerProps) {
  const { data: device, isLoading: deviceLoading } = usePlatformDevice(deviceId || '');
  const { data: waterObject } = useWaterObject(device?.water_object_id ?? null);
  const { data: organization } = useOrganization(waterObject?.organization_id ?? null);
  /* Gated on `open`: this is the only polling query in the app, and a closed
     drawer that still remembers a deviceId would keep it running forever. */
  const {
    data: deviceState,
    isLoading: stateLoading,
    isError: stateError,
  } = usePlatformDeviceState(
    open ? deviceId : null
  );

  const isLoading = deviceLoading;

  if (!device) return null;

  const formatDateTime = (iso: string | null) => {
    if (!iso) return '—';
    const date = new Date(iso);
    return `${date.toLocaleDateString('pl-PL')} · ${date.toLocaleTimeString('pl-PL')}`;
  };

  const stateSection = findSection(deviceState, 'device');
  const state = deviceSectionData(deviceState);

  /* The device answers reads on its next contact, so every field below is
     "as of capture", not "now". The header states that once, in one place,
     rather than repeating a timestamp on each row. */
  const freshness = stateSection ? (
    <Badge variant={stateSection.is_stale ? 'warning' : 'success'}>
      {formatAge(stateSection.age_seconds)}
    </Badge>
  ) : null;

  const bufferFill = bufferFillPercent(state?.buffer_windows_used, state?.buffer_windows_capacity);
  const droppedWindows = state?.buffer_windows_dropped;
  const stateFailed = !!stateError;
  const rssi = rssiLevel(state?.rssi_dbm);
  const rssiVariant = rssi === 'good' ? 'success' : rssi === 'fair' ? 'warning' : 'danger';

  const missing = <span className="text-neutral-600">—</span>;

  /* "Never reported" and "we could not ask" are opposite diagnoses; showing
     the first when the second happened is exactly the misreading this whole
     channel exists to prevent. */
  const noStateYet = !stateLoading && !stateFailed && !stateSection;

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
              <div className="flex items-center justify-between mb-4">
                <h5 className="font-semibold text-neutral-900">Łączność &amp; Zdrowie</h5>
                {freshness}
              </div>

              {stateFailed && (
                <p className="text-xs text-red-700 mb-3">
                  Nie udało się pobrać stanu urządzenia. To awaria odczytu po stronie
                  platformy, a nie informacja o samym urządzeniu — poniższe pola mogą
                  być nieaktualne.
                </p>
              )}

              {noStateYet && (
                <p className="text-xs text-neutral-600 mb-3">
                  Urządzenie nie przysłało jeszcze raportu stanu. Stan dołącza do pakietu
                  telemetrycznego co ~15 min — pojawi się przy najbliższym kontakcie.
                </p>
              )}

              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-neutral-600">Ostatni kontakt</dt>
                  <dd className="text-neutral-900">
                    {formatRelativeTime(device.last_seen_at)} · {formatDateTime(device.last_seen_at)}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Ostatni raport stanu</dt>
                  <dd className="text-neutral-900">
                    {stateSection
                      ? `${formatAge(stateSection.age_seconds)} · ${formatDateTime(stateSection.captured_at)}`
                      : missing}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Sygnał modemu (RSSI)</dt>
                  <dd className="text-neutral-900">
                    {state?.rssi_dbm != null ? (
                      <span className="inline-flex items-center gap-2">
                        {state.rssi_dbm} dBm
                        <Badge variant={rssiVariant}>
                          {rssi === 'good' ? 'dobry' : rssi === 'fair' ? 'słaby' : 'krytyczny'}
                        </Badge>
                      </span>
                    ) : (
                      missing
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Uptime</dt>
                  <dd className="text-neutral-900">{formatUptime(state?.uptime_seconds)}</dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Ostatni restart</dt>
                  <dd className="text-neutral-900">
                    {state?.restart_reason ? (
                      <>
                        {formatRestartReason(state.restart_reason)}
                        {state.restart_count != null && (
                          <span className="text-neutral-600">
                            {' '}
                            · restartów od ostatniego zdrowego startu: {state.restart_count}
                          </span>
                        )}
                      </>
                    ) : (
                      missing
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Wolna pamięć</dt>
                  <dd className="text-neutral-900">
                    {state?.free_heap_bytes != null ? (
                      <>
                        {formatBytes(state.free_heap_bytes)}
                        <span className="text-neutral-600">
                          {' '}
                          · minimum od startu: {formatBytes(state.min_free_heap_bytes)}
                        </span>
                      </>
                    ) : (
                      missing
                    )}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Bufor lokalny — jedyny sygnał, że urządzenie po cichu gubi dane */}
            <div>
              <h5 className="font-semibold text-neutral-900 mb-4">Bufor lokalny</h5>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-neutral-600">Zapełnienie</dt>
                  <dd className="text-neutral-900">
                    {bufferFill !== undefined ? (
                      <span className="inline-flex items-center gap-2">
                        {state?.buffer_windows_used}/{state?.buffer_windows_capacity} okien ({bufferFill}%)
                        {bufferFill >= 80 && <Badge variant="warning">bliski przepełnienia</Badge>}
                      </span>
                    ) : (
                      missing
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-600">Porzucone okna (od startu)</dt>
                  <dd className="text-neutral-900">
                    {droppedWindows != null ? (
                      <span className="inline-flex items-center gap-2">
                        {droppedWindows}
                        {droppedWindows > 0 && <Badge variant="danger">utrata danych</Badge>}
                      </span>
                    ) : (
                      missing
                    )}
                  </dd>
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
                  <dt className="text-neutral-600">Wersja schematu rejestru</dt>
                  <dd className="text-neutral-900 font-mono">
                    {state?.registry_schema_version ?? '—'}
                  </dd>
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
