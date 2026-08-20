import { describe, it, expect, beforeEach, vi } from 'vitest'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice } from '@/lib/backendWakeup'
import type { UserContextResponse } from '@/types/context'

vi.mock('@/lib/queryClient')
vi.mock('@/lib/backendWakeup')

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

const mockUser = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  is_active: true,
}

const mockUserContext: UserContextResponse = {
  organizations: [],
  platform: null,
}

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('logout clears queryClient and backendWakeup', async () => {
    const { useAuthStore } = await import('./authStore')
    const store = useAuthStore.getState()

    store.login('access_token', 'refresh_token', mockUser, mockUserContext)
    store.logout()

    expect(queryClient.clear).toHaveBeenCalled()
    expect(resetBackendWakeupNotice).toHaveBeenCalled()
    expect(store.user).toBeNull()
  })

  it('setTokens updates store state', async () => {
    const { useAuthStore } = await import('./authStore')
    const store = useAuthStore.getState()

    store.setTokens('new_access', 'new_refresh')

    expect(useAuthStore.getState().accessToken).toBe('new_access')
    expect(useAuthStore.getState().refreshToken).toBe('new_refresh')
  })
})
