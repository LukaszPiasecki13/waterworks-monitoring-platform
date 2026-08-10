import { useQuery } from '@tanstack/react-query';
import { objectStatusService } from '@/services/objectStatusService';
import { queryKeys } from './queryKeys';

export function useObjectsStatus() {
  return useQuery({
    queryKey: queryKeys.objectStatus.list(),
    queryFn: () => objectStatusService.listObjectsStatus(),
  });
}

export function useObjectStatusDetail(objectId: string) {
  return useQuery({
    queryKey: queryKeys.objectStatus.detail(objectId),
    queryFn: () => objectStatusService.getObjectDetail(objectId),
  });
}

export function useObjectMeasurements(
  objectId: string,
  params?: { start?: string; end?: string }
) {
  return useQuery({
    queryKey: queryKeys.objectStatus.measurements(objectId, params),
    queryFn: () => objectStatusService.getObjectMeasurements(objectId, params),
  });
}
