import { apiClient } from '@/lib/api';
import type { ObjectStatus, DataQuality } from '@/lib/statusConfig';

/* Tymczasowe typy dla telemetrii — dopóki backend nie wprowadzi prawdziwych endpointów w Etapie 3/4 */

export interface ObjectStatusDetail {
  id: string;
  name: string;
  status: ObjectStatus;
  last_update: string;
}

export interface MeasurementData {
  id: string;
  external_id: string;
  point_type: string;
  unit: string;
  value: number | null;
  quality: DataQuality;
  timestamp: string;
  min_technical?: number;
  max_technical?: number;
}

export interface ObjectDetail {
  id: string;
  name: string;
  status: ObjectStatus;
  last_update: string;
  measurements: MeasurementData[];
}

export const objectStatusService = {
  async listObjectsStatus(): Promise<ObjectStatusDetail[]> {
    const response = await apiClient.get('/api/telemetry/objects');
    return response.data;
  },

  async getObjectDetail(objectId: string): Promise<ObjectDetail> {
    const response = await apiClient.get(`/api/telemetry/objects/${objectId}`);
    return response.data;
  },

  async getObjectMeasurements(
    objectId: string,
    params?: { start?: string; end?: string }
  ): Promise<MeasurementData[]> {
    const response = await apiClient.get(`/api/telemetry/objects/${objectId}/measurements`, {
      params,
    });
    return response.data;
  },
};
