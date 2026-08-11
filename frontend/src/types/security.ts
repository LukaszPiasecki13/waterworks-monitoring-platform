import type { PermissionCode } from './permissions'

export interface Permission {
  id: string
  code: PermissionCode
  name: string
  category: string
}

export interface UserGroup {
  id: string
  name: string
  description: string
  is_system: boolean
  system_key: string | null
  permissions: Permission[]
  user_ids: string[]
  created_at: string
  updated_at: string
}

export interface UserGroupCreateRequest {
  name: string
  description: string
  permission_codes: PermissionCode[]
}

export interface UserGroupSaveRequest extends UserGroupCreateRequest {
  user_ids: string[]
}
