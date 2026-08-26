import { lazy, Suspense } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createBrowserRouter, createRoutesFromElements, Route, Navigate, Outlet } from 'react-router-dom'
import { queryClient } from '@/lib/queryClient'
import '@/lib/api'
import { BackendWakeupPopup } from '@/components/BackendWakeupPopup'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequirePermission } from '@/components/RequirePermission'
import { OrgShell } from '@/components/layout/OrgShell'
import { PlatformShell } from '@/components/layout/PlatformShell'
import { LoginPage } from '@/pages/LoginPage'
import { EnvironmentPickerPage } from '@/pages/EnvironmentPickerPage'
import { NoAccessPage } from '@/pages/NoAccessPage'
import { ObjectsPage } from '@/pages/ObjectsPage'
import { ObjectDetailPage } from '@/pages/ObjectDetailPage'
import { AccountPage } from '@/pages/AccountPage'
import { DevicesPage } from '@/pages/DevicesPage'
import { DeviceMeasurementPointsPage } from '@/pages/DeviceMeasurementPointsPage'
import { ForbiddenPage } from '@/pages/ForbiddenPage'
import { NotFoundPage } from '@/pages/NotFoundPage'

// Lazy-loaded platform pages (code split)
const PlatformOrganizationsPage = lazy(() =>
  import('@/pages/PlatformOrganizationsPage').then((m) => ({ default: m.PlatformOrganizationsPage }))
)
const PlatformActivationCodesPage = lazy(() =>
  import('@/pages/PlatformActivationCodesPage').then((m) => ({ default: m.PlatformActivationCodesPage }))
)
const PlatformDevicesPage = lazy(() =>
  import('@/pages/PlatformDevicesPage').then((m) => ({ default: m.PlatformDevicesPage }))
)
const PlatformAuditPage = lazy(() =>
  import('@/pages/PlatformAuditPage').then((m) => ({ default: m.PlatformAuditPage }))
)

function LoadingFallback() {
  return (
    <div className="flex h-screen items-center justify-center bg-neutral-50">
      <div className="text-center">
        <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-neutral-300 border-t-blue-600"></div>
        <p className="text-neutral-600">Ładowanie...</p>
      </div>
    </div>
  )
}

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/environment-picker" element={<EnvironmentPickerPage />} />
      <Route path="/no-access" element={<NoAccessPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />

      <Route element={<ProtectedRoute />}>
        {/* Organization-plane routes */}
        <Route element={<OrgShell><Outlet /></OrgShell>}>
          <Route path="/" element={<Navigate to="/objects" replace />} />
          <Route path="/dashboard" element={<Navigate to="/objects" replace />} />
          <Route path="/objects" element={<ObjectsPage />} />
          <Route path="/objects/:objectId" element={<ObjectDetailPage />} />
          <Route path="/account" element={<AccountPage />} />
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
          <Route path="/admin/members" element={<Navigate to="/" replace />} />
          <Route path="/admin/groups" element={<Navigate to="/" replace />} />
        </Route>

        {/* Platform-plane routes */}
        <Route element={<PlatformShell><Outlet /></PlatformShell>}>
          <Route path="/platform" element={<Navigate to="/platform/organizations" replace />} />
          <Route
            path="/platform/organizations"
            element={
              <RequirePermission permission="PLATFORM_VIEW_ORGANIZATIONS">
                <Suspense fallback={<LoadingFallback />}>
                  <PlatformOrganizationsPage />
                </Suspense>
              </RequirePermission>
            }
          />
          <Route path="/platform/users" element={<Navigate to="/platform/organizations" replace />} />
          <Route path="/platform/groups" element={<Navigate to="/platform/organizations" replace />} />
          <Route
            path="/platform/activation-codes"
            element={
              <RequirePermission permission="PLATFORM_MANAGE_DEVICE_PROVISIONING">
                <Suspense fallback={<LoadingFallback />}>
                  <PlatformActivationCodesPage />
                </Suspense>
              </RequirePermission>
            }
          />
          <Route
            path="/platform/devices"
            element={
              <RequirePermission permission="PLATFORM_MANAGE_DEVICE_PROVISIONING">
                <Suspense fallback={<LoadingFallback />}>
                  <PlatformDevicesPage />
                </Suspense>
              </RequirePermission>
            }
          />
          <Route
            path="/platform/audit"
            element={
              <RequirePermission permission="PLATFORM_VIEW_AUDIT">
                <Suspense fallback={<LoadingFallback />}>
                  <PlatformAuditPage />
                </Suspense>
              </RequirePermission>
            }
          />
          <Route path="/platform/account" element={<AccountPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </>
  )
)

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <BackendWakeupPopup />
    </QueryClientProvider>
  )
}

export default App
