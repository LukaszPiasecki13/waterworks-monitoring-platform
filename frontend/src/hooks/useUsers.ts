import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersService } from '@/services/usersService';
import { queryKeys } from './queryKeys';
import type { ManagedUserCreateRequest, ManagedUserUpdateRequest } from '@/types/coreData';

export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users.list(),
    queryFn: () => usersService.list(),
  });
}

export function useUser(id: number) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => usersService.get(id),
    enabled: !!id,
  });
}

export function useUserAudit(id: number) {
  return useQuery({
    queryKey: queryKeys.users.audit(id),
    queryFn: () => usersService.getAudit(id),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ManagedUserCreateRequest) => usersService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManagedUserUpdateRequest }) =>
      usersService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });
}
