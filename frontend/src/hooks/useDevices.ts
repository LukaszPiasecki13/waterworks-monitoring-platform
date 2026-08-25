import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesService } from '@/services/devicesService';
import { organizationsService } from '@/services/organizationsService';
import { waterObjectsService } from '@/services/waterObjectsService';
import { queryKeys } from './queryKeys';
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore';
import type {
  DeviceAssignRequest,
  DeviceUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  water_object_id?: string
  search?: string
  organization_id?: string
}

interface PlatformListParams {
  search?: string
  organization_id?: string
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

export function useAssignDevice() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (data: DeviceAssignRequest) => devicesService.assign(activeOrgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
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

// Platform-level device hooks (no org scoping)
export function usePlatformDevices(params?: PlatformListParams) {
  return useQuery({
    queryKey: queryKeys.platformDevices.list(params),
    queryFn: () => devicesService.listAll(params),
  });
}

export function usePlatformDevice(id: string) {
  return useQuery({
    queryKey: queryKeys.platformDevices.detail(id),
    queryFn: () => devicesService.getDetail(id),
    enabled: !!id,
  });
}

export function useDeletePlatformDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => devicesService.deletePlatform(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platformDevices.all });
    },
  });
}

export function usePlatformDeviceStats() {
  const { data: devices, isLoading } = usePlatformDevices();
  const devicesArray = Array.isArray(devices) ? devices : [];

  return {
    data: devicesArray.length > 0 ? {
      total: devicesArray.length,
      active: devicesArray.filter((d) => d.is_active).length,
      unassigned: devicesArray.filter((d) => !d.water_object_id).length,
    } : undefined,
    isLoading,
  };
}


export function useOrganization(id: string | null) {
  return useQuery({
    queryKey: queryKeys.organizations.detail(id ?? ''),
    queryFn: () => organizationsService.get(id!),
    enabled: !!id,
  });
}


export function useWaterObject(id: string | null) {
  return useQuery({
    queryKey: queryKeys.waterObjects.detail(id ?? ''),
    queryFn: () => waterObjectsService.getPlatformDetail(id!),
    enabled: !!id,
  });
}


