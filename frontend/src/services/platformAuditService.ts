import { apiClient } from '@/lib/api';
import type { AuditEvent } from '@/types/coreData';

interface AuditListParams {
  skip?: number;
  limit?: number;
}

export const platformAuditService = {
  async list(params?: AuditListParams): Promise<AuditEvent[]> {
    const response = await apiClient.get('/api/v1/platform/audit', { params });
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
