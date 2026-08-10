import type { User, LoginResponse } from '@/types'
import { authClient } from '@/lib/api'

export const authService = {
  async login(credentials: { username: string; password: string }): Promise<LoginResponse> {
    const response = await authClient.post('/auth/token', credentials)
    return response.data
  },

  async getUserProfile(accessToken: string): Promise<User> {
    const response = await authClient.get('/auth/user', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await authClient.patch('/auth/user', data)
    return response.data
  },
}
