/* Permissions lustrzane wobec backend/app/modules/security/permission_catalog.py */

export type PermissionCode =
  | 'CAN_VIEW_USERS'
  | 'CAN_MANAGE_USERS'
  | 'CAN_VIEW_SECURITY'
  | 'CAN_MANAGE_SECURITY'
  | 'CAN_VIEW_ATTACHMENTS'
  | 'CAN_MANAGE_ATTACHMENTS'
  | 'CAN_VIEW_ORGANIZATIONS'
  | 'CAN_MANAGE_ORGANIZATIONS'
  | 'CAN_VIEW_ASSETS'
  | 'CAN_MANAGE_ASSETS'
  | 'PLATFORM_VIEW_ORGANIZATIONS'
  | 'PLATFORM_MANAGE_ORGANIZATIONS'
  | 'PLATFORM_VIEW_USERS'
  | 'PLATFORM_MANAGE_USERS'
  | 'PLATFORM_MANAGE_MEMBERSHIPS'
  | 'PLATFORM_VIEW_AUDIT';

export const PERMISSIONS: Record<PermissionCode, string> = {
  CAN_VIEW_USERS: 'View users',
  CAN_MANAGE_USERS: 'Manage users',
  CAN_VIEW_SECURITY: 'View security',
  CAN_MANAGE_SECURITY: 'Manage security',
  CAN_VIEW_ATTACHMENTS: 'View attachments',
  CAN_MANAGE_ATTACHMENTS: 'Manage attachments',
  CAN_VIEW_ORGANIZATIONS: 'View organizations',
  CAN_MANAGE_ORGANIZATIONS: 'Manage organizations',
  CAN_VIEW_ASSETS: 'View assets',
  CAN_MANAGE_ASSETS: 'Manage assets',
  PLATFORM_VIEW_ORGANIZATIONS: 'View organizations (platform)',
  PLATFORM_MANAGE_ORGANIZATIONS: 'Manage organizations (platform)',
  PLATFORM_VIEW_USERS: 'View users (platform)',
  PLATFORM_MANAGE_USERS: 'Manage users (platform)',
  PLATFORM_MANAGE_MEMBERSHIPS: 'Manage memberships (platform)',
  PLATFORM_VIEW_AUDIT: 'View audit log (platform)',
};

export interface PermissionCatalogEntry {
  code: PermissionCode;
  name: string;
  category: string;
  plane: 'organization' | 'platform';
}

/* Mirrors PERMISSION_CATALOG in backend/app/modules/security/permission_catalog.py —
   keep category/plane in sync manually when the backend catalog changes. */
export const PERMISSION_CATALOG: PermissionCatalogEntry[] = [
  { code: 'CAN_VIEW_USERS', name: 'Podgląd członków organizacji', category: 'Użytkownicy', plane: 'organization' },
  { code: 'CAN_MANAGE_USERS', name: 'Zarządzanie członkami organizacji', category: 'Użytkownicy', plane: 'organization' },
  { code: 'CAN_VIEW_SECURITY', name: 'Podgląd grup bezpieczeństwa organizacji', category: 'Bezpieczeństwo', plane: 'organization' },
  { code: 'CAN_MANAGE_SECURITY', name: 'Zarządzanie grupami bezpieczeństwa organizacji', category: 'Bezpieczeństwo', plane: 'organization' },
  { code: 'CAN_VIEW_ATTACHMENTS', name: 'Podgląd załączników organizacji', category: 'Załączniki', plane: 'organization' },
  { code: 'CAN_MANAGE_ATTACHMENTS', name: 'Zarządzanie załącznikami organizacji', category: 'Załączniki', plane: 'organization' },
  { code: 'CAN_VIEW_ORGANIZATIONS', name: 'Podgląd własnej organizacji', category: 'Rejestr obiektów', plane: 'organization' },
  { code: 'CAN_MANAGE_ORGANIZATIONS', name: 'Zarządzanie własną organizacją', category: 'Rejestr obiektów', plane: 'organization' },
  { code: 'CAN_VIEW_ASSETS', name: 'Podgląd obiektów, urządzeń i punktów pomiarowych', category: 'Rejestr obiektów', plane: 'organization' },
  { code: 'CAN_MANAGE_ASSETS', name: 'Zarządzanie obiektami, urządzeniami i punktami pomiarowymi', category: 'Rejestr obiektów', plane: 'organization' },
  { code: 'PLATFORM_VIEW_ORGANIZATIONS', name: 'Podgląd rejestru organizacji', category: 'Platforma', plane: 'platform' },
  { code: 'PLATFORM_MANAGE_ORGANIZATIONS', name: 'Zarządzanie organizacjami', category: 'Platforma', plane: 'platform' },
  { code: 'PLATFORM_VIEW_USERS', name: 'Podgląd globalnego rejestru kont', category: 'Platforma', plane: 'platform' },
  { code: 'PLATFORM_MANAGE_USERS', name: 'Zarządzanie kontami', category: 'Platforma', plane: 'platform' },
  { code: 'PLATFORM_MANAGE_MEMBERSHIPS', name: 'Zarządzanie członkostwami', category: 'Platforma', plane: 'platform' },
  { code: 'PLATFORM_VIEW_AUDIT', name: 'Podgląd audytu globalnego', category: 'Platforma', plane: 'platform' },
];
