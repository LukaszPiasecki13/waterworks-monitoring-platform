import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { waterObjectsService } from '@/services/waterObjectsService';
import { queryKeys } from './queryKeys';
import type { WaterObjectCreateRequest, WaterObjectUpdateRequest } from '@/types/coreData';

export function useWaterObjects() {
  return useQuery({
    queryKey: queryKeys.waterObjects.list(),
    queryFn: () => waterObjectsService.list(),
  });
}

export function useWaterObject(id: string) {
  return useQuery({
    queryKey: queryKeys.waterObjects.detail(id),
    queryFn: () => waterObjectsService.get(id),
  });
}

export function useCreateWaterObject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WaterObjectCreateRequest) => waterObjectsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
    },
  });
}

export function useUpdateWaterObject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WaterObjectUpdateRequest }) =>
      waterObjectsService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}

export function useDeleteWaterObject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => waterObjectsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}
