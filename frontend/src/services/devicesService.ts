import { apiClient } from '@/lib/api';
import type {
  Device,
  DeviceCreateRequest,
  DeviceCreateResponse,
  DeviceUpdateRequest,
} from '@/types/coreData';

export const devicesService = {
  async list(): Promise<Device[]> {
    const response = await apiClient.get('/api/v1/devices');
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

  async get(id: string): Promise<Device> {
    const response = await apiClient.get(`/api/v1/devices/${id}`);
    return response.data;
  },

  async create(data: DeviceCreateRequest): Promise<DeviceCreateResponse> {
    const response = await apiClient.post('/api/v1/devices', data);
    return response.data;
  },

  async update(id: string, data: DeviceUpdateRequest): Promise<Device> {
    const response = await apiClient.patch(`/api/v1/devices/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/devices/${id}`);
  },
};
