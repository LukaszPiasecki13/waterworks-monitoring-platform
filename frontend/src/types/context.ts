import type { PermissionCode } from './permissions';

export interface OrganizationEnvironment {
  type: 'organization';
  organizationId: string;
  organizationName: string;
}

export interface PlatformEnvironment {
  type: 'platform';
}

export type ActiveEnvironment = OrganizationEnvironment | PlatformEnvironment | null;

export interface OrganizationContext {
  organization_id: string;
  organization_name: string;
  permissions: PermissionCode[];
}

export interface PlatformContext {
  permissions: PermissionCode[];
}

export interface UserContextResponse {
  organizations: OrganizationContext[];
  platform: PlatformContext | null;
}
