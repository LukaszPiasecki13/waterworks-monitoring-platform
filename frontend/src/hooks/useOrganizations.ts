import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { organizationsService } from '@/services/organizationsService';
import { authService } from '@/services/authService';
import { queryKeys } from './queryKeys';
import type { OrganizationCreateRequest, OrganizationUpdateRequest } from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  name?: string
}

interface QueryOptions {
  enabled?: boolean
}

export function useOrganizations(params?: ListParams, options?: QueryOptions) {
  return useQuery({
    queryKey: queryKeys.organizations.list(params),
    queryFn: () => organizationsService.list(params),
    enabled: options?.enabled !== false,
  });
}

export function useOrganization(id: string) {
  return useQuery({
    queryKey: queryKeys.organizations.detail(id),
    queryFn: () => organizationsService.get(id),
    enabled: !!id,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  const { setUserContext } = useAuthStore();

  return useMutation({
    mutationFn: (data: OrganizationCreateRequest) => organizationsService.create(data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
      try {
        const userContextData = await queryClient.fetchQuery({
          queryKey: queryKeys.auth.userContext(),
          queryFn: () => authService.getMyContext(),
        });
        setUserContext(userContextData);
      } catch (error) {
        console.error('Failed to update user context:', error);
      }
    },
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();
  const { setUserContext } = useAuthStore();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: OrganizationUpdateRequest }) =>
      organizationsService.update(id, data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
      try {
        const userContextData = await queryClient.fetchQuery({
          queryKey: queryKeys.auth.userContext(),
          queryFn: () => authService.getMyContext(),
        });
        setUserContext(userContextData);
      } catch (error) {
        console.error('Failed to update user context:', error);
      }
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();
  const { setUserContext } = useAuthStore();

  return useMutation({
    mutationFn: (id: string) => organizationsService.delete(id),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
      try {
        const userContextData = await queryClient.fetchQuery({
          queryKey: queryKeys.auth.userContext(),
          queryFn: () => authService.getMyContext(),
        });
        setUserContext(userContextData);
      } catch (error) {
        console.error('Failed to update user context:', error);
      }
    },
  });
}
