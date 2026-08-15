import axios, { type InternalAxiosRequestConfig, type AxiosProgressEvent } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import { queryClient } from '@/lib/queryClient'
import { resetBackendWakeupNotice, startBackendRequest } from '@/lib/backendWakeup'
import { markSessionChanged, captureSessionRevision, assertSessionUnchanged } from '@/lib/sessionLifecycle'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const authClient = axios.create({
  baseURL: API_URL,
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

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const store = useAuthStore.getState()
      const refreshToken = store.refreshToken

      if (refreshToken) {
        const sessionRevision = captureSessionRevision()

        try {
          const response = await authClient.post('/auth/token/refresh', {
            refresh: refreshToken,
          })

          assertSessionUnchanged(sessionRevision)

          const { access, refresh } = response.data
          store.setTokens(access, refresh)

          const headers = originalRequest.headers as Record<string, string>
          headers.Authorization = `Bearer ${access}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          clearSessionAndRedirect()
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

export async function refreshSession() {
  const store = useAuthStore.getState()
  const refreshToken = store.refreshToken

  if (!refreshToken) {
    throw new Error('No refresh token available')
  }

  const sessionRevision = captureSessionRevision()

  try {
    const response = await authClient.post('/auth/token/refresh', {
      refresh: refreshToken,
    })

    assertSessionUnchanged(sessionRevision)

    const { access, refresh } = response.data
    store.setTokens(access, refresh)

    return response.data
  } catch (error) {
    clearSessionAndRedirect()
    throw error
  }
}
