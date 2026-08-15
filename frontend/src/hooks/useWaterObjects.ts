import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { waterObjectsService } from '@/services/waterObjectsService';
import { queryKeys } from './queryKeys';
import { useActiveOrganizationStore } from '@/stores/activeOrganizationStore';
import type { WaterObjectCreateRequest, WaterObjectUpdateRequest } from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  organization_id?: string
}

export function useWaterObjects(params?: ListParams) {
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)

  const queryParams = {
    ...params,
    organization_id: activeOrgId ?? undefined,
  }

  return useQuery({
    queryKey: queryKeys.waterObjects.list(queryParams),
    queryFn: () => waterObjectsService.list(queryParams),
    enabled: !!activeOrgId,
  });
}

export function useWaterObject(id: string) {
  return useQuery({
    queryKey: queryKeys.waterObjects.detail(id),
    queryFn: () => waterObjectsService.get(id),
    enabled: !!id,
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
