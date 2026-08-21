import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { platformGroupsService } from '@/services/platformGroupsService'
import { queryKeys } from './queryKeys'
import type {
  SecurityGroupCreateRequest,
  SecurityGroupSaveRequest,
} from '@/types/coreData'

export function usePlatformGroups() {
  return useQuery({
    queryKey: queryKeys.platformGroups.list(),
    queryFn: () => platformGroupsService.list(),
  })
}

export function useCreatePlatformGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SecurityGroupCreateRequest) => platformGroupsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platformGroups.all })
    },
  })
}

export function useSavePlatformGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SecurityGroupSaveRequest }) =>
      platformGroupsService.save(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platformGroups.all })
    },
  })
}

export function useReplacePlatformGroupUsers() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, userIds }: { id: string; userIds: string[] }) =>
      platformGroupsService.replaceUsers(id, userIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platformGroups.all })
    },
  })
}

export function useDeletePlatformGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => platformGroupsService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platformGroups.all })
    },
  })
}
