import { useSyncExternalStore } from 'react'
import { subscribeToBackendWakeup, getBackendWakeupState } from '@/lib/backendWakeup'

export function BackendWakeupPopup() {
  const state = useSyncExternalStore(subscribeToBackendWakeup, getBackendWakeupState, () => ({
    isWakingUp: false,
  }))

  if (!state.isWakingUp) {
    return null
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div
        className="bg-white rounded-lg p-8 shadow-lg max-w-md text-center"
        role="status"
        aria-live="polite"
      >
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 border-4 border-neutral-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <h2 className="text-xl font-semibold mb-2 text-neutral-900">Trwa uruchamianie serwera</h2>
        <p className="text-neutral-600">Proszę czekać. Może to potrwać do minuty...</p>
      </div>
    </div>
  )
}
