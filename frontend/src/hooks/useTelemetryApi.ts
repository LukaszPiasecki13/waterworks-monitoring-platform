import { useQuery } from '@tanstack/react-query'
import { telemetryService } from '@/services/telemetryService'
import { queryKeys } from './queryKeys'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'

export function useTelemetryObjects(limit = 50) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.telemetry.objects(activeOrgId, limit),
    queryFn: () => telemetryService.listObjects(activeOrgId!, { limit }),
    enabled: !!activeOrgId,
  })
}

export function useTelemetryObjectDetail(objectId: string) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.telemetry.object(objectId, activeOrgId),
    queryFn: () => telemetryService.getObject(activeOrgId!, objectId),
    enabled: !!objectId && !!activeOrgId,
    refetchInterval: 15000,
  })
}

export function useTelemetryMeasurements(
  objectId: string,
  pointId?: string,
  hoursBack = 24,
) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.telemetry.measurements(objectId, pointId, hoursBack, activeOrgId),
    queryFn: () => {
      const now = new Date()
      const startTime = new Date(now.getTime() - hoursBack * 60 * 60 * 1000)

      return telemetryService.getMeasurements(activeOrgId!, objectId, {
        point_id: pointId,
        start: startTime.toISOString(),
        end: now.toISOString(),
        limit: 5000,
      })
    },
    enabled: !!objectId && !!activeOrgId,
    refetchInterval: 15000,
  })
}
