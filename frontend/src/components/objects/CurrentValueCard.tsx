import { StatusPill } from '@/components/ui/StatusPill'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover'
import { HelpCircle } from 'lucide-react'
import type { LatestPointValue } from '@/hooks/useTelemetryApi'
import type { DataQuality } from '@/lib/statusConfig'
import { formatDistanceToNow } from 'date-fns'
import { pl } from 'date-fns/locale'

interface CurrentValueCardProps {
  point: LatestPointValue
}

export function CurrentValueCard({ point }: CurrentValueCardProps) {
  const measuredTime = formatDistanceToNow(new Date(point.measured_at), {
    addSuffix: true,
    locale: pl,
  })

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-sm font-semibold text-gray-900">{point.type}</h4>
          <p className="text-xs text-gray-500 mt-0.5">
            ID: <span className="font-mono">{point.point_id}</span>
          </p>
        </div>
        <Popover>
          <PopoverTrigger asChild>
            <button className="text-gray-400 hover:text-gray-600">
              <HelpCircle className="h-4 w-4" />
            </button>
          </PopoverTrigger>
          <PopoverContent className="w-64 text-sm">
            <p className="text-gray-700">
              Wartość z <span className="font-mono text-xs bg-gray-100 px-1 py-0.5 rounded">{point.device_id}</span>
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Zmierzono {measuredTime}
            </p>
          </PopoverContent>
        </Popover>
      </div>

      <div className="mb-3">
        <p className="text-2xl font-bold text-gray-900 font-mono">
          {point.value.toFixed(2)}
        </p>
        <p className="text-xs text-gray-600 mt-1">{point.unit}</p>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-500">Jakość danych:</span>
        <StatusPill kind="quality" value={point.quality as DataQuality} />
      </div>

      <p className="text-xs text-gray-400 mt-2">
        Zmierzono {measuredTime}
      </p>
    </div>
  )
}
