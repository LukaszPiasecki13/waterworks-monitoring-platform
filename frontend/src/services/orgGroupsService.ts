import { apiClient } from '@/lib/api';
import type {
  SecurityGroupSummary,
  SecurityGroupCreateRequest,
  SecurityGroupSaveRequest,
} from '@/types/coreData';

export const orgGroupsService = {
  async list(orgId: string): Promise<SecurityGroupSummary[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/groups`);
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

  async create(
    orgId: string,
    data: SecurityGroupCreateRequest
  ): Promise<SecurityGroupSummary> {
    const response = await apiClient.post(`/api/v1/orgs/${orgId}/groups`, data);
    return response.data;
  },

  async save(
    orgId: string,
    id: string,
    data: SecurityGroupSaveRequest
  ): Promise<SecurityGroupSummary> {
    const response = await apiClient.put(`/api/v1/orgs/${orgId}/groups/${id}`, data);
    return response.data;
  },

  async replaceUsers(
    orgId: string,
    id: string,
    userIds: string[]
  ): Promise<SecurityGroupSummary> {
    const response = await apiClient.put(
      `/api/v1/orgs/${orgId}/groups/${id}/users`,
      { user_ids: userIds }
    );
    return response.data;
  },

  async remove(orgId: string, id: string): Promise<void> {
    await apiClient.delete(`/api/v1/orgs/${orgId}/groups/${id}`);
  },
};
