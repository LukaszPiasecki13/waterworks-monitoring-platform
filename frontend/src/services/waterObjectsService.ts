import { apiClient } from '@/lib/api';
import type {
  WaterObject,
  WaterObjectCreateRequest,
  WaterObjectUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  organization_id?: string
}

export const waterObjectsService = {
  async list(params?: ListParams): Promise<WaterObject[]> {
    const response = await apiClient.get('/api/v1/objects', { params });
    // Backend returns PaginatedResponse, extract items
    if (response.data && Array.isArray(response.data.items)) {
      return response.data.items;
    }
    // Fallback if response is already an array
    if (Array.isArray(response.data)) {
      return response.data;
    }
    return [];
  },

  async get(id: string): Promise<WaterObject> {
    const response = await apiClient.get(`/api/v1/objects/${id}`);
    return response.data;
  },

  async create(data: WaterObjectCreateRequest): Promise<WaterObject> {
    const response = await apiClient.post('/api/v1/objects', data);
    return response.data;
  },

  async update(id: string, data: WaterObjectUpdateRequest): Promise<WaterObject> {
    const response = await apiClient.patch(`/api/v1/objects/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/objects/${id}`);
  },
};
