import { apiClient } from '@/lib/api';
import type {
  ManagedUser,
  ManagedUserCreateRequest,
  ManagedUserUpdateRequest,
  AuditLogEntry,
} from '@/types/coreData';

export const usersService = {
  async list(): Promise<ManagedUser[]> {
    const response = await apiClient.get('/api/v1/users');
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

  async get(id: number): Promise<ManagedUser> {
    const response = await apiClient.get(`/api/v1/users/${id}`);
    return response.data;
  },

  async create(data: ManagedUserCreateRequest): Promise<ManagedUser> {
    const response = await apiClient.post('/api/v1/users', data);
    return response.data;
  },

  async update(id: number, data: ManagedUserUpdateRequest): Promise<ManagedUser> {
    const response = await apiClient.patch(`/api/v1/users/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/users/${id}`);
  },

  async getAudit(id: number): Promise<AuditLogEntry[]> {
    const response = await apiClient.get(`/api/v1/users/${id}/audit`);
    return response.data;
  },
};
