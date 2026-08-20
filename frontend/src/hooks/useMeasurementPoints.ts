import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { measurementPointsService } from '@/services/measurementPointsService';
import { queryKeys } from './queryKeys';
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore';
import type {
  MeasurementPointCreateRequest,
  MeasurementPointUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  device_id?: string
}

export function useMeasurementPoints(params?: ListParams) {
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useQuery({
    queryKey: queryKeys.measurementPoints.list(params),
    queryFn: () => measurementPointsService.list(activeOrgId!, params),
    enabled: !!activeOrgId,
  });
}

export function useCreateMeasurementPoint() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (data: MeasurementPointCreateRequest) =>
      measurementPointsService.create(activeOrgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}

export function useUpdateMeasurementPoint() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: MeasurementPointUpdateRequest }) =>
      measurementPointsService.update(activeOrgId!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
    },
  });
}

export function useDeleteMeasurementPoint() {
  const queryClient = useQueryClient();
  const activeOrgId = useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })

  return useMutation({
    mutationFn: (id: string) => measurementPointsService.delete(activeOrgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
    },
  });
}
