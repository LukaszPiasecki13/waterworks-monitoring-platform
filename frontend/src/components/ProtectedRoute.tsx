import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { useUserContext } from '@/hooks/useUserContext'

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const { environment } = useActiveEnvironmentStore()
  useUserContext()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!environment) {
    return <Navigate to="/environment-picker" replace />
  }

  return <Outlet />
}
