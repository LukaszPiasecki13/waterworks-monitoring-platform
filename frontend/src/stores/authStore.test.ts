import { describe, it, expect, beforeEach, vi } from 'vitest'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice } from '@/lib/backendWakeup'

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
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  status: 'active',
}

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('logout clears queryClient and backendWakeup', async () => {
    const { useAuthStore } = await import('./authStore')
    const store = useAuthStore.getState()

    store.login('access_token', 'refresh_token', mockUser)
    store.logout()

    expect(queryClient.clear).toHaveBeenCalled()
    expect(resetBackendWakeupNotice).toHaveBeenCalled()
    expect(store.user).toBeNull()
  })

  it('setTokens updates localStorage', async () => {
    const { useAuthStore } = await import('./authStore')
    const store = useAuthStore.getState()

    store.setTokens('new_access', 'new_refresh')

    expect(localStorage.getItem('access_token')).toBe('new_access')
    expect(localStorage.getItem('refresh_token')).toBe('new_refresh')
  })
})
