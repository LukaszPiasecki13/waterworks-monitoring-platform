import { useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createBrowserRouter, createRoutesFromElements, Route, Navigate } from 'react-router-dom'
import { queryClient } from '@/lib/queryClient'
import { attachBackendWakeupInterceptors } from '@/lib/api'
import { BackendWakeupPopup } from '@/components/BackendWakeupPopup'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequirePermission } from '@/components/RequirePermission'
import { AppLayout } from '@/components/layout/AppLayout'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ObjectDetailPage } from '@/pages/ObjectDetailPage'
import { AccountPage } from '@/pages/AccountPage'
import { OrganizationsPage } from '@/pages/OrganizationsPage'
import { WaterObjectsPage } from '@/pages/WaterObjectsPage'
import { DevicesPage } from '@/pages/DevicesPage'
import { DeviceMeasurementPointsPage } from '@/pages/DeviceMeasurementPointsPage'
import { UsersPage } from '@/pages/UsersPage'
import { ForbiddenPage } from '@/pages/ForbiddenPage'
import { NotFoundPage } from '@/pages/NotFoundPage'

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/objects/:objectId" element={<ObjectDetailPage />} />
          <Route path="/account" element={<AccountPage />} />
          <Route
            path="/admin/organizations"
            element={
              <RequirePermission permission="CAN_VIEW_ORGANIZATIONS">
                <OrganizationsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/admin/objects"
            element={
              <RequirePermission permission="CAN_VIEW_ASSETS">
                <WaterObjectsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/admin/devices"
            element={
              <RequirePermission permission="CAN_VIEW_ASSETS">
                <DevicesPage />
              </RequirePermission>
            }
          />
          <Route
            path="/admin/devices/:deviceId"
            element={
              <RequirePermission permission="CAN_VIEW_ASSETS">
                <DeviceMeasurementPointsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/admin/users"
            element={
              <RequirePermission
                permissions={['CAN_VIEW_USERS', 'CAN_MANAGE_USERS', 'CAN_VIEW_SECURITY']}
              >
                <UsersPage />
              </RequirePermission>
            }
          />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </>
  )
)

function App() {
  useEffect(() => {
    attachBackendWakeupInterceptors()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <BackendWakeupPopup />
    </QueryClientProvider>
  )
}

export default App
