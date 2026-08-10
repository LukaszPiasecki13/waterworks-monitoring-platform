import type { AuthUser, LoginResponse } from '@/types'
import type { PermissionCode } from '@/types/permissions'
import { authClient } from '@/lib/api'

interface UserPermissions {
  permissions: PermissionCode[]
  group_ids: number[]
}

export const authService = {
  async login(credentials: { username: string; password: string }): Promise<LoginResponse> {
    const response = await authClient.post('/auth/token', credentials)
    return response.data
  },

  async getUserProfile(accessToken: string): Promise<AuthUser> {
    const response = await authClient.get('/auth/user', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
    return response.data
  },

  async getUserPermissions(accessToken: string): Promise<UserPermissions> {
    const response = await authClient.get('/api/v1/security/me/permissions', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
    return response.data
  },

  async updateProfile(data: Partial<AuthUser>): Promise<AuthUser> {
    const response = await authClient.patch('/auth/user', data)
    return response.data
  },
}
