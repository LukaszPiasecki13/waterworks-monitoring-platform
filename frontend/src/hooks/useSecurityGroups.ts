import axios from 'axios'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { securityService } from '@/services/securityService'
import { queryKeys } from './queryKeys'
import { toast } from '@/components/ui/Toast'
import type {
  UserGroupCreateRequest,
  UserGroupSaveRequest,
} from '@/types/security'

function extractErrorDetail(error: unknown): string | undefined {
  return axios.isAxiosError(error) ? error.response?.data?.detail : undefined
}

export function useSecurityGroups() {
  const queryClient = useQueryClient()

  const permissionsQuery = useQuery({
    queryKey: queryKeys.security.permissions.list(),
    queryFn: () => securityService.listPermissions(),
  })

  const groupsQuery = useQuery({
    queryKey: queryKeys.security.groups.list(),
    queryFn: () => securityService.listGroups(),
  })

  const createMutation = useMutation({
    mutationFn: (data: UserGroupCreateRequest) => securityService.createGroup(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.security.groups.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.security.myPermissions() })
      toast.success('Grupa utworzona')
    },
    onError: (error: unknown) => {
      toast.error(extractErrorDetail(error) || 'Błąd przy tworzeniu grupy')
    },
  })

  const saveMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserGroupSaveRequest }) =>
      securityService.saveGroup(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.security.groups.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.security.myPermissions() })
      toast.success('Grupa zapisana')
    },
    onError: (error: unknown) => {
      toast.error(extractErrorDetail(error) || 'Błąd przy zapisywaniu grupy')
    },
  })

  const removeMutation = useMutation({
    mutationFn: (id: string) => securityService.deleteGroup(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.security.groups.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.security.myPermissions() })
      toast.success('Grupa usunięta')
    },
    onError: (error: unknown) => {
      toast.error(extractErrorDetail(error) || 'Błąd przy usuwaniu grupy')
    },
  })

  return {
    permissions: permissionsQuery.data || [],
    groups: groupsQuery.data || [],
    isLoadingPermissions: permissionsQuery.isLoading,
    isLoadingGroups: groupsQuery.isLoading,
    create: createMutation,
    save: saveMutation,
    remove: removeMutation,
  }
}

export function useUserGroups(userId: string) {
  return useQuery({
    queryKey: queryKeys.security.userGroups(userId),
    queryFn: () => securityService.getUserGroups(userId),
    enabled: !!userId,
  })
}

export function useReplaceUserGroups() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, groupIds }: { userId: string; groupIds: string[] }) =>
      securityService.setUserGroups(userId, groupIds),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.security.groups.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.security.userGroups(userId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.security.myPermissions() })
      toast.success('Grupy użytkownika zaktualizowane')
    },
    onError: (error: unknown) => {
      toast.error(extractErrorDetail(error) || 'Błąd przy aktualizacji grup')
    },
  })
}
