import { apiClient } from '@/lib/api';
import type {
  MeasurementPoint,
  MeasurementPointCreateRequest,
  MeasurementPointUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  organization_id?: string
  device_id?: string
}

export const measurementPointsService = {
  async list(params?: ListParams): Promise<MeasurementPoint[]> {
    const response = await apiClient.get('/api/v1/measurement-points', { params });
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

  async get(id: string): Promise<MeasurementPoint> {
    const response = await apiClient.get(`/api/v1/measurement-points/${id}`);
    return response.data;
  },

  async create(data: MeasurementPointCreateRequest): Promise<MeasurementPoint> {
    const response = await apiClient.post('/api/v1/measurement-points', data);
    return response.data;
  },

  async update(id: string, data: MeasurementPointUpdateRequest): Promise<MeasurementPoint> {
    const response = await apiClient.patch(`/api/v1/measurement-points/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/measurement-points/${id}`);
  },
};
