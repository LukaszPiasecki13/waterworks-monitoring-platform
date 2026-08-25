import { apiClient } from '@/lib/api';

export interface CredentialStatus {
  device_id: string;
  status: string;
  claimed_at: string | null;
}

export const deviceCredentialsService = {
  async getBatch(deviceIds: string[]): Promise<CredentialStatus[]> {
    if (!deviceIds.length) {
      return [];
    }
    const params = new URLSearchParams();
    deviceIds.forEach(id => params.append('device_ids', id));
    const response = await apiClient.get('/api/v1/platform/devices/credentials', { params });
    return response.data;
  },
};
