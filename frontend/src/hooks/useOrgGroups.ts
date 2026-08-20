import { useQuery } from '@tanstack/react-query'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { orgGroupsService } from '@/services/orgGroupsService'
import { queryKeys } from './queryKeys'

export function useOrgGroups() {
  const orgId = useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.orgGroups.list(orgId || ''),
    queryFn: () => (orgId ? orgGroupsService.list(orgId) : Promise.resolve([])),
    enabled: !!orgId,
  })
}
