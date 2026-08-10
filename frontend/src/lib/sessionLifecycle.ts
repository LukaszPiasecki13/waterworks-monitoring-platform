import { SessionChangedError } from './errors'

let sessionRevision = 0

export function markSessionChanged() {
  sessionRevision++
}

export function captureSessionRevision() {
  return sessionRevision
}

export function assertSessionUnchanged(capturedRevision: number) {
  if (sessionRevision !== capturedRevision) {
    throw new SessionChangedError()
  }
}
