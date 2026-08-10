import { AxiosError } from 'axios'

export class SessionChangedError extends Error {
  constructor(message = 'Session changed during operation') {
    super(message)
    this.name = 'SessionChangedError'
  }
}

export function parseApiError(err: unknown): string {
  if (err instanceof AxiosError && err.response?.data) {
    const data = err.response.data as Record<string, unknown>
    if (typeof data.detail === 'string') {
      return data.detail
    }
  }
  return 'Unknown error occurred'
}
