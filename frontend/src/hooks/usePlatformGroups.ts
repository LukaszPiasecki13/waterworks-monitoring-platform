import { useQuery } from '@tanstack/react-query'
import { platformGroupsService } from '@/services/platformGroupsService'
import { queryKeys } from './queryKeys'

export function usePlatformGroups() {
  return useQuery({
    queryKey: queryKeys.platformGroups.list(),
    queryFn: () => platformGroupsService.list(),
  })
}
