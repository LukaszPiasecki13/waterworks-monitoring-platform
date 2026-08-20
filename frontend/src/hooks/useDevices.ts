import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesService } from '@/services/devicesService';
import { queryKeys } from './queryKeys';
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore';
import type { DeviceCreateRequest, DeviceUpdateRequest } from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  water_object_id?: string
}

export function useDevices(params?: ListParams) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.devices.list(params),
    queryFn: () => devicesService.list(activeOrgId!, params),
    enabled: !!activeOrgId,
  });
}

export function useDevice(id: string) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.devices.detail(id),
    queryFn: () => devicesService.get(activeOrgId!, id),
    enabled: !!id && !!activeOrgId,
  });
}

export function useCreateDevice() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (data: DeviceCreateRequest) => devicesService.create(activeOrgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}

export function useUpdateDevice() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DeviceUpdateRequest }) =>
      devicesService.update(activeOrgId!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}

export function useDeleteDevice() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (id: string) => devicesService.delete(activeOrgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}
