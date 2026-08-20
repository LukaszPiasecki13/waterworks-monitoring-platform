import { apiClient } from '@/lib/api';
import type {
  ManagedUser,
  ManagedUserCreateRequest,
  ManagedUserUpdateRequest,
  AuditLogEntry,
  UserOrganizationsResponse,
} from '@/types/coreData';

export const usersService = {
  async list(): Promise<ManagedUser[]> {
    const response = await apiClient.get('/api/v1/platform/users');
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

  async get(id: string): Promise<ManagedUser> {
    const response = await apiClient.get(`/api/v1/platform/users/${id}`);
    return response.data;
  },

  async create(data: ManagedUserCreateRequest): Promise<ManagedUser> {
    const response = await apiClient.post('/api/v1/platform/users', data);
    return response.data;
  },

  async update(id: string, data: ManagedUserUpdateRequest): Promise<ManagedUser> {
    const response = await apiClient.patch(`/api/v1/platform/users/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/platform/users/${id}`);
  },

  async getAudit(id: string): Promise<AuditLogEntry[]> {
    const response = await apiClient.get(`/api/v1/platform/users/${id}/audit`);
    return response.data;
  },

  async getOrganizations(userId: string): Promise<UserOrganizationsResponse> {
    const response = await apiClient.get(`/api/v1/platform/users/${userId}/organizations`);
    return response.data;
  },

  async assignOrganization(userId: string, orgId: string): Promise<void> {
    await apiClient.post(`/api/v1/platform/users/${userId}/organizations/${orgId}`);
  },

  async removeOrganization(userId: string, orgId: string): Promise<void> {
    await apiClient.delete(`/api/v1/platform/users/${userId}/organizations/${orgId}`);
  },
};
