import { apiClient } from '@/lib/api';
import type {
  MeasurementPoint,
  MeasurementPointCreateRequest,
  MeasurementPointUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  device_id?: string
}

export const measurementPointsService = {
  async list(orgId: string, params?: ListParams): Promise<MeasurementPoint[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/measurement-points`, { params });
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

  async get(orgId: string, id: string): Promise<MeasurementPoint> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/measurement-points/${id}`);
    return response.data;
  },

  async create(orgId: string, data: MeasurementPointCreateRequest): Promise<MeasurementPoint> {
    const response = await apiClient.post(`/api/v1/orgs/${orgId}/measurement-points`, data);
    return response.data;
  },

  async update(orgId: string, id: string, data: MeasurementPointUpdateRequest): Promise<MeasurementPoint> {
    const response = await apiClient.patch(`/api/v1/orgs/${orgId}/measurement-points/${id}`, data);
    return response.data;
  },

  async delete(orgId: string, id: string): Promise<void> {
    await apiClient.delete(`/api/v1/orgs/${orgId}/measurement-points/${id}`);
  },
};
