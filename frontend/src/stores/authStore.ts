import type { AuthUser } from '@/types'
import type { PermissionCode } from '@/types/permissions'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { markSessionChanged } from '@/lib/sessionLifecycle'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice } from '@/lib/backendWakeup'
import { useActiveOrganizationStore } from './activeOrganizationStore'

interface AuthState {
  user: AuthUser | null
  permissions: PermissionCode[]
  groupIds: number[]
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string, user: AuthUser, permissions?: PermissionCode[], groupIds?: number[]) => void
  logout: () => void
  updateUser: (user: AuthUser) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  hasPermission: (permission: PermissionCode) => boolean
  hasAnyPermission: (permissions: PermissionCode[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      permissions: [],
      groupIds: [],
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (accessToken, refreshToken, user, permissions = [], groupIds = []) => {
        set({
          user,
          permissions,
          groupIds,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      logout: () => {
        markSessionChanged()
        set({
          user: null,
          permissions: [],
          groupIds: [],
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        queryClient.clear()
        resetBackendWakeupNotice()
        useActiveOrganizationStore.getState().clear()
      },

      updateUser: (user) => {
        set({ user })
      },

      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken })
      },

      hasPermission: (permission: PermissionCode) => {
        return get().permissions.includes(permission)
      },

      hasAnyPermission: (permissions: PermissionCode[]) => {
        return permissions.some((p) => get().permissions.includes(p))
      },
    }),
    {
      name: 'auth-user',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        permissions: state.permissions,
        groupIds: state.groupIds,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated = !!state.accessToken
        }
      },
    }
  )
)
