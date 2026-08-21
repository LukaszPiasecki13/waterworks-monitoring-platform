import axios, { type InternalAxiosRequestConfig, type AxiosProgressEvent } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice, startBackendRequest } from '@/lib/backendWakeup'
import { markSessionChanged, captureSessionRevision, assertSessionUnchanged } from '@/lib/sessionLifecycle'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const authClient = axios.create({
  baseURL: API_URL,
})

authClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (!config.headers.Authorization) {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export const apiClient = axios.create({
  baseURL: API_URL,
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const cleanup = startBackendRequest()
  config.signal?.addEventListener?.('abort', () => cleanup())
  const originalProgress = config.onDownloadProgress
  if (originalProgress) {
    config.onDownloadProgress = (progressEvent: AxiosProgressEvent) => {
      cleanup()
      originalProgress(progressEvent)
    }
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    resetBackendWakeupNotice()
    return response
  },
  (error) => {
    resetBackendWakeupNotice()
    return Promise.reject(error)
  }
)

apiClient.interceptors.request.use((config) => {
  const store = useAuthStore.getState()
  const token = store.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as Record<string, unknown>

    if (error.response?.status === 404 && /\/api\/v1\/orgs\//.test(originalRequest.url as string)) {
      useActiveEnvironmentStore.getState().clear()
      window.location.href = '/not-found'
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const store = useAuthStore.getState()
      const refreshToken = store.refreshToken

      if (refreshToken) {
        try {
          const access = await refreshTokenAndContext(refreshToken)
          const headers = originalRequest.headers as Record<string, string>
          headers.Authorization = `Bearer ${access}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          return Promise.reject(refreshError)
        }
      } else {
        clearSessionAndRedirect()
      }
    }

    return Promise.reject(error)
  }
)

export async function clearSessionAndRedirect() {
  const store = useAuthStore.getState()
  markSessionChanged()
  store.logout()
  queryClient.clear()
  resetBackendWakeupNotice()
  window.location.href = '/login'
}

async function refreshTokenAndContext(refreshToken: string) {
  const sessionRevision = captureSessionRevision()

  try {
    const response = await authClient.post('/auth/token/refresh', {
      refresh: refreshToken,
    })

    assertSessionUnchanged(sessionRevision)

    const { access, refresh } = response.data
    const store = useAuthStore.getState()
    store.setTokens(access, refresh)

    const contextResponse = await authClient.get('/auth/me/context', {
      headers: {
        Authorization: `Bearer ${access}`,
      },
    })

    store.setUserContext(contextResponse.data)

    if (store.userContext && store.userContext.organizations.length + (store.userContext.platform ? 1 : 0) === 0) {
      window.location.href = '/no-access'
      return Promise.reject(new Error('No access'))
    }

    return access
  } catch (error) {
    clearSessionAndRedirect()
    throw error
  }
}

export async function refreshSession() {
  const store = useAuthStore.getState()
  const refreshToken = store.refreshToken

  if (!refreshToken) {
    throw new Error('No refresh token available')
  }

  return await refreshTokenAndContext(refreshToken)
}
