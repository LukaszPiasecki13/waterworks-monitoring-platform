import { apiClient } from '@/lib/api';
import type {
  SecurityGroupSummary,
  SecurityGroupCreateRequest,
  SecurityGroupSaveRequest,
} from '@/types/coreData';

export const platformGroupsService = {
  async list(): Promise<SecurityGroupSummary[]> {
    const response = await apiClient.get('/api/v1/platform/groups');
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

  async create(data: SecurityGroupCreateRequest): Promise<SecurityGroupSummary> {
    const response = await apiClient.post('/api/v1/platform/groups', data);
    return response.data;
  },

  async save(id: string, data: SecurityGroupSaveRequest): Promise<SecurityGroupSummary> {
    const response = await apiClient.put(`/api/v1/platform/groups/${id}`, data);
    return response.data;
  },

  async replaceUsers(id: string, userIds: string[]): Promise<SecurityGroupSummary> {
    const response = await apiClient.put(`/api/v1/platform/groups/${id}/users`, {
      user_ids: userIds,
    });
    return response.data;
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/platform/groups/${id}`);
  },
};
