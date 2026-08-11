/* Core Data types — odpowiadające API Etap 1 */

/* Organization */
export interface Organization {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface OrganizationCreateRequest {
  name: string;
}

export interface OrganizationUpdateRequest {
  name: string;
}

/* Water Object */
export interface WaterObject {
  id: string;
  organization_id: string;
  name: string;
  object_type: string;
  location_description?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at: string;
}

export interface WaterObjectCreateRequest {
  name: string;
  object_type: string;
  location_description?: string;
  latitude?: number;
  longitude?: number;
  organization_id?: string; /* tylko dla admina platformy */
}

export interface WaterObjectUpdateRequest {
  name?: string;
  object_type?: string;
  location_description?: string;
  latitude?: number;
  longitude?: number;
}

/* Device */
export interface Device {
  id: string;
  water_object_id: string;
  external_id: string;
  firmware_version: string | null;
  last_seen_at: string | null;
  last_diagnostics_at: string | null;
  is_active: boolean;
}

export interface DeviceCreateRequest {
  water_object_id: string;
  external_id: string;
  firmware_version?: string;
}

export interface DeviceCreateResponse {
  id: string;
  water_object_id: string;
  external_id: string;
  firmware_version: string | null;
  last_seen_at: string | null;
  last_diagnostics_at: string | null;
  is_active: boolean;
  plain_secret: string;
}

export interface DeviceUpdateRequest {
  firmware_version?: string;
  is_active?: boolean;
}

/* Measurement Point */
export interface MeasurementPoint {
  id: string;
  device_id: string;
  external_id: string;
  point_type: string;
  unit: string;
  min_technical?: number;
  max_technical?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MeasurementPointCreateRequest {
  device_id: string;
  external_id: string;
  point_type: string;
  unit: string;
  min_technical?: number;
  max_technical?: number;
}

export interface MeasurementPointUpdateRequest {
  external_id?: string;
  point_type?: string;
  unit?: string;
  min_technical?: number;
  max_technical?: number;
}

/* Managed User (z /api/v1/users, inny od AuthUser z /auth/user) */
export interface ManagedUser {
  id: number;
  organization_id: string | null;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  status: 'regular' | 'admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ManagedUserCreateRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  status: 'regular' | 'admin';
  organization_id?: string;
}

export interface ManagedUserUpdateRequest {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  status?: 'regular' | 'admin';
  is_active?: boolean;
}

/* Audit log entry */
export interface AuditLogEntry {
  id: string;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, any>;
  created_at: string;
}
