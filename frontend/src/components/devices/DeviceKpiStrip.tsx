import { usePlatformDeviceStats } from '@/hooks/useDevices';
import { Card, CardContent } from '@/components/ui/Card';

export function DeviceKpiStrip() {
  const { data: stats, isLoading } = usePlatformDeviceStats();

  const cards = [
    { label: 'Łącznie urządzeń', value: stats?.total ?? 0 },
    { label: 'Aktywne', value: stats?.active ?? 0 },
    { label: 'Nieprzypisane', value: stats?.unassigned ?? 0 },
  ];

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardContent className="p-6">
            {isLoading ? (
              <div className="h-8 bg-neutral-200 rounded animate-pulse mb-2" />
            ) : (
              <div className="text-3xl font-bold text-brand-600">{card.value}</div>
            )}
            <div className="text-sm text-neutral-600 mt-2">{card.label}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
