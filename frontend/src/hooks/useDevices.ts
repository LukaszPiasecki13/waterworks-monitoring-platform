import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesService } from '@/services/devicesService';
import { queryKeys } from './queryKeys';
import { useActiveOrganizationStore } from '@/stores/activeOrganizationStore';
import type { DeviceCreateRequest, DeviceUpdateRequest } from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  organization_id?: string
  water_object_id?: string
}

export function useDevices(params?: ListParams) {
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)

  const queryParams = {
    ...params,
    organization_id: activeOrgId ?? undefined,
  }

  return useQuery({
    queryKey: queryKeys.devices.list(queryParams),
    queryFn: () => devicesService.list(queryParams),
    enabled: !!activeOrgId,
  });
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: queryKeys.devices.detail(id),
    queryFn: () => devicesService.get(id),
    enabled: !!id,
  });
}

export function useCreateDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DeviceCreateRequest) => devicesService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.waterObjects.all });
    },
  });
}

export function useUpdateDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DeviceUpdateRequest }) =>
      devicesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}

export function useDeleteDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => devicesService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}
