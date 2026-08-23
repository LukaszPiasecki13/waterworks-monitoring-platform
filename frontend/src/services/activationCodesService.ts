import { apiClient } from '@/lib/api';
import type { ActivationCode, ActivationCodeCreateResponse } from '@/types/coreData';

interface ListParams {
  skip?: number;
  limit?: number;
}

export const activationCodesService = {
  async list(params?: ListParams) {
    const response = await apiClient.get('/api/v1/platform/device-activation-codes', { params });
    if (response.data && Array.isArray(response.data.items)) {
      return response.data;
    }
    return { items: [], total: 0, skip: 0, limit: 100 };
  },

  async get(id: string): Promise<ActivationCode> {
    const response = await apiClient.get(`/api/v1/platform/device-activation-codes/${id}`);
    return response.data;
  },

  async create(): Promise<ActivationCodeCreateResponse> {
    const response = await apiClient.post('/api/v1/platform/device-activation-codes');
    return response.data;
  },

  async cancel(id: string): Promise<{ id: string; status: string }> {
    const response = await apiClient.post(
      `/api/v1/platform/device-activation-codes/${id}/cancel`
    );
    return response.data;
  },
};
