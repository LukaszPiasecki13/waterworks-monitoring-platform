import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { membersService } from '@/services/membersService'
import { queryKeys } from './queryKeys'

export function useMembers() {
  const orgId = useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.members.list(orgId || ''),
    queryFn: () => (orgId ? membersService.list(orgId) : Promise.resolve([])),
    enabled: !!orgId,
  })
}

export function useAddMember() {
  const queryClient = useQueryClient()
  const orgId = useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (userId: string) => {
      if (!orgId) throw new Error('No organization selected')
      return membersService.add(orgId, userId)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      }
    },
  })
}

export function useRemoveMember() {
  const queryClient = useQueryClient()
  const orgId = useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (userId: string) => {
      if (!orgId) throw new Error('No organization selected')
      return membersService.remove(orgId, userId)
    },
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      }
    },
  })
}
