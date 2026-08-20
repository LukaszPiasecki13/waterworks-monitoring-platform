import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersService } from '@/services/usersService'
import { queryKeys } from './queryKeys'

export function useUserOrganizations(userId: string | null) {
  return useQuery({
    queryKey: queryKeys.users.organizations(userId || ''),
    queryFn: () => usersService.getOrganizations(userId as string),
    enabled: !!userId,
  })
}

export function useAssignUserOrganization(userId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (orgId: string) => usersService.assignOrganization(userId, orgId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.organizations(userId) })
    },
  })
}

export function useRemoveUserOrganization(userId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (orgId: string) => usersService.removeOrganization(userId, orgId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.organizations(userId) })
    },
  })
}
