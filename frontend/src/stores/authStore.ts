import type { AuthUser } from '@/types'
import type { UserContextResponse } from '@/types/context'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { markSessionChanged } from '@/lib/sessionLifecycle'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice } from '@/lib/backendWakeup'
import { useActiveEnvironmentStore } from './activeEnvironmentStore'

interface AuthState {
  user: AuthUser | null
  userContext: UserContextResponse | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string, user: AuthUser, userContext: UserContextResponse) => void
  logout: () => void
  updateUser: (user: AuthUser) => void
  setUserContext: (userContext: UserContextResponse) => void
  setTokens: (accessToken: string, refreshToken: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      userContext: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (accessToken, refreshToken, user, userContext) => {
        set({
          user,
          userContext,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      logout: () => {
        markSessionChanged()
        set({
          user: null,
          userContext: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        queryClient.clear()
        resetBackendWakeupNotice()
        useActiveEnvironmentStore.getState().clear()
      },

      updateUser: (user) => {
        set({ user })
      },

      setUserContext: (userContext) => {
        set({ userContext })
      },

      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken })
      },
    }),
    {
      name: 'auth-user',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        userContext: state.userContext,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated = !!state.accessToken
        }
      },
    }
  )
)
