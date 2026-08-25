import { apiClient } from '@/lib/api';
import type {
  Device,
  DeviceAssignRequest,
  DeviceAssignResponse,
  DeviceClaimStatusResponse,
  DeviceUpdateRequest,
} from '@/types/coreData';

interface ListParams {
  water_object_id?: string
  search?: string
  organization_id?: string
}

interface PlatformListParams {
  search?: string
  organization_id?: string
}

export const devicesService = {
  async list(orgId: string, params?: ListParams): Promise<Device[]> {
    const response = await apiClient.get(`/api/v1/orgs/${orgId}/devices`, { params });
    return response.data;
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
  async listAll(params?: PlatformListParams): Promise<Device[]> {
    const response = await apiClient.get('/api/v1/platform/devices', { params });
    return response.data;
  },

  async getDetail(id: string): Promise<Device> {
    const response = await apiClient.get(`/api/v1/platform/devices/${id}`);
    return response.data;
  },

  async deletePlatform(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/platform/devices/${id}`);
  },

};
