import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { waterObjectsService } from '@/services/waterObjectsService';
import { queryKeys } from './queryKeys';
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore';
import type { WaterObjectCreateRequest, WaterObjectUpdateRequest } from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
}

export function useWaterObjects(params?: ListParams) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.waterObjects.list(params),
    queryFn: () => waterObjectsService.list(activeOrgId!, params),
    enabled: !!activeOrgId,
  });
}

export function useWaterObject(id: string) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.waterObjects.detail(id),
    queryFn: () => waterObjectsService.get(activeOrgId!, id),
    enabled: !!id && !!activeOrgId,
  });
}

export function useCreateWaterObject() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (data: WaterObjectCreateRequest) => waterObjectsService.create(activeOrgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
    },
  });
}

export function useUpdateWaterObject() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WaterObjectUpdateRequest }) =>
      waterObjectsService.update(activeOrgId!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}

export function useDeleteWaterObject() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (id: string) => waterObjectsService.delete(activeOrgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}
