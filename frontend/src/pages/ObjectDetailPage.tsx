import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTelemetryObjectDetail } from '@/hooks/useTelemetryApi'
import { CurrentValueCard } from '@/components/objects/CurrentValueCard'
import { ObjectMeasurementsChart } from '@/components/objects/ObjectMeasurementsChart'
import { StatusPill } from '@/components/ui/StatusPill'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ChevronLeft } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { pl } from 'date-fns/locale'

export function ObjectDetailPage() {
  const { objectId } = useParams<{ objectId: string }>()
  const navigate = useNavigate()
  const { data: detail, isLoading } = useTelemetryObjectDetail(objectId || '')
  const [hoursBack, setHoursBack] = useState(24)

  if (!objectId) {
    return (
      <div className="px-6 py-8">
        <div className="text-red-600">Brakuje ID obiektu</div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="px-6 py-8">
        <div className="text-gray-500">Ładowanie szczegółów obiektu...</div>
      </div>
    )
  }

  if (!detail) {
    return (
      <div className="px-6 py-8">
        <Button variant="outline" onClick={() => navigate('/dashboard')}>
          <ChevronLeft className="mr-2 h-4 w-4" />
          Wróć do dashboardu
        </Button>
        <div className="mt-4 text-red-600">Nie udało się załadować szczegółów obiektu</div>
      </div>
    )
  }

  return (
    <div className="px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-4">
          <ChevronLeft className="mr-2 h-4 w-4" />
          Wróć do dashboardu
        </Button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{detail.object_id}</h1>
            <p className="text-gray-600 mt-2">
              Urządzenie: <span className="font-mono text-sm">{detail.device_id}</span>
            </p>
          </div>
          <StatusPill kind="objectStatus" value={detail.status} />
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-600 uppercase font-semibold">Organizacja</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">{detail.org_id}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-600 uppercase font-semibold">Ostatni kontakt</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {detail.last_contact_at
                ? formatDistanceToNow(new Date(detail.last_contact_at), {
                    addSuffix: true,
                    locale: pl,
                  })
                : 'Brak danych'}
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-600 uppercase font-semibold">Sekwencja</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">{detail.last_seq}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-600 uppercase font-semibold">Pomiary</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">{detail.points.length}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="values" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="values">Aktualne wartości</TabsTrigger>
          <TabsTrigger value="chart">Wykresy pomiarów</TabsTrigger>
        </TabsList>

        {/* Aktualne wartości */}
        <TabsContent value="values">
          {detail.points.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {detail.points.map((point) => (
                <CurrentValueCard key={point.point_id} point={point} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-gray-500">Brak danych pomiarów</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Wykresy */}
        <TabsContent value="chart">
          <Card>
            <CardContent className="pt-6">
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 block mb-2">
                  Okres czasu:
                </label>
                <div className="flex gap-2">
                  {[
                    { label: '24h', value: 24 },
                    { label: '7d', value: 168 },
                    { label: '30d', value: 720 },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setHoursBack(opt.value)}
                      className={`px-3 py-2 text-sm font-medium rounded-md border transition-colors ${
                        hoursBack === opt.value
                          ? 'bg-teal-50 border-teal-300 text-teal-700'
                          : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <ObjectMeasurementsChart objectId={objectId} hoursBack={hoursBack} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
