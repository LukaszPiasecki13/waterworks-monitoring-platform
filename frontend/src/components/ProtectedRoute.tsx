import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'

export function ProtectedRoute() {
  const { isAuthenticated } = useAuthStore()
  const { environment } = useActiveEnvironmentStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!environment) {
    return <Navigate to="/environment-picker" replace />
  }

  return <Outlet />
}
