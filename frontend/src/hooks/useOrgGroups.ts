import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { orgGroupsService } from '@/services/orgGroupsService'
import { queryKeys } from './queryKeys'
import type {
  SecurityGroupCreateRequest,
  SecurityGroupSaveRequest,
} from '@/types/coreData'

function useActiveOrgId(): string | null {
  return useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })
}

export function useOrgGroups() {
  const orgId = useActiveOrgId()

  return useQuery({
    queryKey: queryKeys.orgGroups.list(orgId || ''),
    queryFn: () => (orgId ? orgGroupsService.list(orgId) : Promise.resolve([])),
    enabled: !!orgId,
  })
}

export function useCreateOrgGroup() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SecurityGroupCreateRequest) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return orgGroupsService.create(orgId, data)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.orgGroups.list(orgId) })
      }
    },
  })
}

export function useSaveOrgGroup() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SecurityGroupSaveRequest }) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return orgGroupsService.save(orgId, id, data)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.orgGroups.list(orgId) })
      }
    },
  })
}

export function useReplaceOrgGroupUsers() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, userIds }: { id: string; userIds: string[] }) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return orgGroupsService.replaceUsers(orgId, id, userIds)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.orgGroups.list(orgId) })
      }
    },
  })
}

export function useDeleteOrgGroup() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return orgGroupsService.remove(orgId, id)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.orgGroups.list(orgId) })
      }
    },
  })
}
