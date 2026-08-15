import { useQuery } from '@tanstack/react-query'
import { telemetryService } from '@/services/telemetryService'
import { queryKeys } from './queryKeys'
import { useActiveOrganizationStore } from '@/stores/activeOrganizationStore'

export function useTelemetryObjects(limit = 50) {
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)

  return useQuery({
    queryKey: queryKeys.telemetry.objects(activeOrgId, limit),
    queryFn: () => telemetryService.listObjects({ limit, org_id: activeOrgId ?? undefined }),
    enabled: !!activeOrgId,
  })
}

export function useTelemetryObjectDetail(objectId: string) {
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)

  return useQuery({
    queryKey: queryKeys.telemetry.object(objectId, activeOrgId),
    queryFn: () => telemetryService.getObject(objectId),
    enabled: !!objectId && !!activeOrgId,
    refetchInterval: 15000,
  })
}

export function useTelemetryMeasurements(
  objectId: string,
  pointId?: string,
  hoursBack = 24,
) {
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)

  return useQuery({
    queryKey: queryKeys.telemetry.measurements(objectId, pointId, hoursBack, activeOrgId),
    queryFn: () => {
      const now = new Date()
      const startTime = new Date(now.getTime() - hoursBack * 60 * 60 * 1000)

      return telemetryService.getMeasurements(objectId, {
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
