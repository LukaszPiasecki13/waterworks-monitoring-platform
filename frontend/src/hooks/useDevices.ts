import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesService } from '@/services/devicesService';
import { queryKeys } from './queryKeys';
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore';
import type {
  DeviceAssignRequest,
  DeviceUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  water_object_id?: string
  search?: string
  is_active?: boolean
  credential_status?: 'unclaimed' | 'claimed' | 'revoked'
  organization_id?: string
  assigned?: 'assigned' | 'unassigned'
  sort_by?: 'last_seen_at' | 'created_at' | 'external_id'
  sort_dir?: 'asc' | 'desc'
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
export function usePlatformDevices(params?: ListParams) {
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
  return useQuery({
    queryKey: queryKeys.platformDevices.stats(),
    queryFn: () => devicesService.getStats(),
  });
}
