import { apiClient } from '@/lib/api';
import type {
  Device,
  DeviceAssignRequest,
  DeviceAssignResponse,
  DeviceClaimStatusResponse,
  DeviceDetail,
  DeviceStats,
  DeviceUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  skip?: number
  limit?: number
  water_object_id?: string
  search?: string
  is_active?: boolean
  credential_status?: 'unclaimed' | 'claimed' | 'revoked'
  organization_id?: string
  assigned?: 'assigned' | 'unassigned'
  sort_by?: 'last_seen_at' | 'created_at' | 'external_id'
  sort_dir?: 'asc' | 'desc'
}

export interface PaginatedDevices {
  items: Device[];
  total: number;
  skip: number;
  limit: number;
}

export const devicesService = {
  async list(orgId: string, params?: ListParams): Promise<Device[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/devices`, { params });
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

  async get(orgId: string, id: string): Promise<Device> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/devices/${id}`);
    return response.data;
  },

  async assign(orgId: string, data: DeviceAssignRequest): Promise<DeviceAssignResponse> {
    const response = await apiClient.post(`/api/v1/orgs/${orgId}/devices`, data);
    return response.data;
  },

  async getClaimStatus(orgId: string, serialNumber: string): Promise<DeviceClaimStatusResponse> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/devices/claims/${serialNumber}`);
    return response.data;
  },

  async update(orgId: string, id: string, data: DeviceUpdateRequest): Promise<Device> {
    const response = await apiClient.patch(`/api/v1/orgs/${orgId}/devices/${id}`, data);
    return response.data;
  },

  async delete(orgId: string, id: string): Promise<void> {
    await apiClient.delete(`/api/v1/orgs/${orgId}/devices/${id}`);
  },

  // Platform-level methods (no org scoping)
  async listAll(params?: ListParams): Promise<PaginatedDevices> {
    const response = await apiClient.get('/api/v1/platform/devices', { params });
    return response.data;
  },

  async getDetail(id: string): Promise<DeviceDetail> {
    const response = await apiClient.get(`/api/v1/platform/devices/${id}`);
    return response.data;
  },

  async getStats(): Promise<DeviceStats> {
    const response = await apiClient.get('/api/v1/platform/devices/stats');
    return response.data;
  },

  async deletePlatform(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/platform/devices/${id}`);
  },
};
