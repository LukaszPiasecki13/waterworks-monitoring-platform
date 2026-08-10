import type { User } from '@/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { markSessionChanged } from '@/lib/sessionLifecycle'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice } from '@/lib/backendWakeup'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string, user: User) => void
  logout: () => void
  updateUser: (user: User) => void
  setTokens: (accessToken: string, refreshToken: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (accessToken, refreshToken, user) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
      },

      logout: () => {
        markSessionChanged()
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        queryClient.clear()
        resetBackendWakeupNotice()
      },

      updateUser: (user) => {
        set({ user })
      },

      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken })
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
      },
    }),
    {
      name: 'auth-user',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated = !!state.accessToken
        }
      },
    }
  )
)
