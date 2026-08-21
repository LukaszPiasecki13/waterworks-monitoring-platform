import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { useAuthStore } from '@/stores/authStore'
import { membersService } from '@/services/membersService'
import { authService } from '@/services/authService'
import { queryKeys } from './queryKeys'

function useActiveOrgId(): string | null {
  return useActiveEnvironmentStore((s) => {
    if (s.environment?.type === 'organization') {
      return s.environment.organizationId
    }
    return null
  })
}

export function useMembers() {
  const orgId = useActiveOrgId()

  return useQuery({
    queryKey: queryKeys.members.list(orgId || ''),
    queryFn: () => (orgId ? membersService.list(orgId) : Promise.resolve([])),
    enabled: !!orgId,
  })
}

export function useAddMember() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()
  const { setUserContext } = useAuthStore()

  return useMutation({
    mutationFn: (userId: string) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return membersService.add(orgId, userId)
    },
    onSuccess: async () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      }
      try {
        const userContextData = await queryClient.fetchQuery({
          queryKey: queryKeys.auth.userContext(),
          queryFn: () => authService.getMyContext(),
        })
        setUserContext(userContextData)
      } catch (error) {
        console.error('Failed to update user context:', error)
      }
    },
  })
}

export function useRemoveMember() {
  const orgId = useActiveOrgId()
  const queryClient = useQueryClient()
  const { setUserContext } = useAuthStore()

  return useMutation({
    mutationFn: (userId: string) => {
      if (!orgId) throw new Error('Brak aktywnej organizacji')
      return membersService.remove(orgId, userId)
    },
    onSuccess: async () => {
      if (orgId) {
        queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      }
      try {
        const userContextData = await queryClient.fetchQuery({
          queryKey: queryKeys.auth.userContext(),
          queryFn: () => authService.getMyContext(),
        })
        setUserContext(userContextData)
      } catch (error) {
        console.error('Failed to update user context:', error)
      }
    },
  })
}
