import { apiClient } from '@/lib/api';
import type { Organization, OrganizationCreateRequest, OrganizationUpdateRequest } from '@/types/coreData';

export const organizationsService = {
  async list(): Promise<Organization[]> {
    const response = await apiClient.get('/api/v1/organizations');
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

  async get(id: string): Promise<Organization> {
    const response = await apiClient.get(`/api/v1/organizations/${id}`);
    return response.data;
  },

  async create(data: OrganizationCreateRequest): Promise<Organization> {
    const response = await apiClient.post('/api/v1/organizations', data);
    return response.data;
  },

  async update(id: string, data: OrganizationUpdateRequest): Promise<Organization> {
    const response = await apiClient.patch(`/api/v1/organizations/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/organizations/${id}`);
  },
};
