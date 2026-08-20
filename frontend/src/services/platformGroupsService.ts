import { apiClient } from '@/lib/api';
import type { SecurityGroupSummary } from '@/types/coreData';

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
};
