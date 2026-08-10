import { authClient } from '@/lib/api';
import type { PermissionCode } from '@/types/permissions';

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
};
