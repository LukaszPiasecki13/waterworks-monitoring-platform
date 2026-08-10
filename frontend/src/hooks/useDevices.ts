import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesService } from '@/services/devicesService';
import { queryKeys } from './queryKeys';
import type { DeviceCreateRequest, DeviceUpdateRequest } from '@/types/coreData';

export function useDevices() {
  return useQuery({
    queryKey: queryKeys.devices.list(),
    queryFn: () => devicesService.list(),
  });
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: queryKeys.devices.detail(id),
    queryFn: () => devicesService.get(id),
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
