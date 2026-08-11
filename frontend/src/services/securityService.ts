import { authClient, apiClient } from '@/lib/api';
import type { PermissionCode } from '@/types/permissions';
import type {
  Permission,
  UserGroup,
  UserGroupCreateRequest,
  UserGroupSaveRequest,
} from '@/types/security';

interface PermissionsResponse {
  permissions: PermissionCode[];
  group_ids: string[];
}

export const securityService = {
  async getMyPermissions(accessToken: string): Promise<PermissionsResponse> {
    /* Ręczne przekazanie tokenu na wypadek że store jeszcze nie ma go */
    const response = await authClient.get('/api/v1/security/me/permissions', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  },

  async listPermissions(): Promise<Permission[]> {
    const response = await apiClient.get('/api/v1/security/permissions');
    return Array.isArray(response.data) ? response.data : response.data.items || [];
  },

  async listGroups(): Promise<UserGroup[]> {
    const response = await apiClient.get('/api/v1/security/groups');
    return Array.isArray(response.data) ? response.data : response.data.items || [];
  },

  async createGroup(data: UserGroupCreateRequest): Promise<UserGroup> {
    const response = await apiClient.post('/api/v1/security/groups', data);
    return response.data;
  },

  async saveGroup(id: string, data: UserGroupSaveRequest): Promise<UserGroup> {
    const response = await apiClient.put(`/api/v1/security/groups/${id}`, data);
    return response.data;
  },

  async deleteGroup(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/security/groups/${id}`);
  },

  async getUserGroups(userId: string): Promise<string[]> {
    const response = await apiClient.get(`/api/v1/security/users/${userId}/groups`);
    return Array.isArray(response.data) ? response.data : response.data.group_ids || [];
  },

  async setUserGroups(userId: string, groupIds: string[]): Promise<string[]> {
    const response = await apiClient.put(`/api/v1/security/users/${userId}/groups`, {
      group_ids: groupIds,
    });
    return Array.isArray(response.data) ? response.data : response.data.group_ids || [];
  },
};
