import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { activationCodesService } from '@/services/activationCodesService';
import { queryKeys } from './queryKeys';
import { useEffect, useRef } from 'react';
import type { ActivationCode } from '@/types/coreData';

interface ListParams {
  skip?: number;
  limit?: number;
}

export function useActivationCodes(params?: ListParams) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const query = useQuery({
    queryKey: queryKeys.activationCodes.list(params),
    queryFn: () => activationCodesService.list(params),
  });

  const data = query.data || { items: [], total: 0, skip: 0, limit: 100 };
  const hasUnused = Array.isArray(data.items) ? data.items.some((code: ActivationCode) => code.status === 'unused') : false;

  useEffect(() => {
    if (hasUnused) {
      if (!intervalRef.current) {
        intervalRef.current = setInterval(() => {
          query.refetch();
        }, 2000);
      }
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [hasUnused, query]);

  return query;
}

export function useActivationCodeDetail(id: string) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const query = useQuery({
    queryKey: queryKeys.activationCodes.detail(id),
    queryFn: () => activationCodesService.get(id),
    enabled: !!id,
  });

  const data = query.data || { status: 'unused', used_at: null, serial_number: null };
  const hasUnused = data.status === 'unused';

  useEffect(() => {
    if (hasUnused && id) {
      if (!intervalRef.current) {
        intervalRef.current = setInterval(() => {
          query.refetch();
        }, 2000);
      }
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [hasUnused, id, query]);

  return query;
}

export function useCreateActivationCode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => activationCodesService.create(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activationCodes.all });
    },
  });
}

export function useCancelActivationCode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => activationCodesService.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activationCodes.all });
    },
  });
}
