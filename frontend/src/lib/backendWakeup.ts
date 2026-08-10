const BACKEND_WAKEUP_DELAY_MS = 5000

interface BackendWakeupState {
  isWakingUp: boolean
}

const state: BackendWakeupState = {
  isWakingUp: false,
}

type Listener = () => void
const listeners = new Set<Listener>()

export function subscribeToBackendWakeup(listener: Listener) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

function notifyListeners() {
  listeners.forEach((listener) => listener())
}

let currentTimer: ReturnType<typeof setTimeout> | null = null

export function startBackendRequest() {
  currentTimer = setTimeout(() => {
    state.isWakingUp = true
    notifyListeners()
  }, BACKEND_WAKEUP_DELAY_MS)

  return () => {
    if (currentTimer !== null) {
      clearTimeout(currentTimer)
      currentTimer = null
    }
    state.isWakingUp = false
    notifyListeners()
  }
}

export function resetBackendWakeupNotice() {
  if (currentTimer !== null) {
    clearTimeout(currentTimer)
    currentTimer = null
  }
  state.isWakingUp = false
  notifyListeners()
}

export function getBackendWakeupState() {
  return state
}
