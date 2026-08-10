import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { measurementPointsService } from '@/services/measurementPointsService';
import { queryKeys } from './queryKeys';
import type {
  MeasurementPointCreateRequest,
  MeasurementPointUpdateRequest,
} from '@/types/coreData';

export function useMeasurementPoints() {
  return useQuery({
    queryKey: queryKeys.measurementPoints.list(),
    queryFn: () => measurementPointsService.list(),
  });
}

export function useMeasurementPoint(id: string) {
  return useQuery({
    queryKey: queryKeys.measurementPoints.detail(id),
    queryFn: () => measurementPointsService.get(id),
  });
}

export function useCreateMeasurementPoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: MeasurementPointCreateRequest) =>
      measurementPointsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
    },
  });
}

export function useUpdateMeasurementPoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: MeasurementPointUpdateRequest }) =>
      measurementPointsService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
    },
  });
}

export function useDeleteMeasurementPoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => measurementPointsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.measurementPoints.all });
    },
  });
}
