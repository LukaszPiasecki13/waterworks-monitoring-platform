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
  | 'CAN_MANAGE_ASSETS';

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
};
