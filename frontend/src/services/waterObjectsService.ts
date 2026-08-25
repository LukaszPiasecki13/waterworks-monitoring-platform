import { apiClient } from '@/lib/api';
import type {
  WaterObject,
  WaterObjectCreateRequest,
  WaterObjectUpdateRequest,
} from '@/types/coreData';

export const waterObjectsService = {
  async list(orgId: string): Promise<WaterObject[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/objects`);
    return Array.isArray(response.data) ? response.data : [];
  },

  async get(orgId: string, id: string): Promise<WaterObject> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/objects/${id}`);
    return response.data;
  },

  async create(orgId: string, data: WaterObjectCreateRequest): Promise<WaterObject> {
    const response = await apiClient.post(`/api/v1/orgs/${orgId}/objects`, data);
    return response.data;
  },

  async update(orgId: string, id: string, data: WaterObjectUpdateRequest): Promise<WaterObject> {
    const response = await apiClient.patch(`/api/v1/orgs/${orgId}/objects/${id}`, data);
    return response.data;
  },

  async delete(orgId: string, id: string): Promise<void> {
    await apiClient.delete(`/api/v1/orgs/${orgId}/objects/${id}`);
  },

  // Platform-level methods (no org scoping)
  async getPlatformDetail(id: string): Promise<WaterObject> {
    const response = await apiClient.get(`/api/v1/platform/objects/${id}`);
    return response.data;
  },
};
