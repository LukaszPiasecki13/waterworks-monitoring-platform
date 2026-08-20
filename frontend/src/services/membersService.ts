import { apiClient } from '@/lib/api';
import type { OrganizationMember } from '@/types/coreData';

export const membersService = {
  async list(orgId: string): Promise<OrganizationMember[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/members`);
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

  async add(orgId: string, userId: string): Promise<OrganizationMember> {
    const response = await apiClient.post(`/api/v1/orgs/${orgId}/members/${userId}`);
    return response.data;
  },

  async remove(orgId: string, userId: string): Promise<void> {
    await apiClient.delete(`/api/v1/orgs/${orgId}/members/${userId}`);
  },
};
