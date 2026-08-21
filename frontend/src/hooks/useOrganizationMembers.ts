import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { membersService } from '@/services/membersService'
import { authService } from '@/services/authService'
import { queryKeys } from './queryKeys'

export function useOrganizationMembers(orgId: string | null) {
  return useQuery({
    queryKey: queryKeys.members.list(orgId || ''),
    queryFn: () => (orgId ? membersService.list(orgId) : Promise.resolve([])),
    enabled: !!orgId,
  })
}

export function useAddOrganizationMember(orgId: string) {
  const queryClient = useQueryClient()
  const { setUserContext } = useAuthStore()

  return useMutation({
    mutationFn: (userId: string) => membersService.add(orgId, userId),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      // Force fetch and sync user context to Zustand store
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

export function useRemoveOrganizationMember(orgId: string) {
  const queryClient = useQueryClient()
  const { setUserContext } = useAuthStore()

  return useMutation({
    mutationFn: (userId: string) => membersService.remove(orgId, userId),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.members.list(orgId) })
      // Force fetch and sync user context to Zustand store
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
