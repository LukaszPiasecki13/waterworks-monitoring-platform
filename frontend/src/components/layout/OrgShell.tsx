import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { Topbar } from './Topbar'
import { OrgSidebar } from './OrgSidebar'

interface OrgShellProps {
  children: React.ReactNode
}

export function OrgShell({ children }: OrgShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const environment = useActiveEnvironmentStore((s) => s.environment)
  const userContext = useAuthStore((s) => s.userContext)

  // Guard: Only redirect if environment is null (not set)
  // or if org exists but is stale (F5 after removal from organization)
  // DO NOT redirect just because environment.type !== 'organization' - that's a transient state
  // during normal switching and React Router will handle route matching correctly

  if (!environment) {
    return <Navigate to="/environment-picker" replace />
  }

  // If environment is org type, check if org still exists (F5 edge case)
  if (environment.type === 'organization' && userContext && !userContext.organizations.some((o) => o.organization_id === environment.organizationId)) {
    useActiveEnvironmentStore.getState().clear()
    return <Navigate to="/environment-picker" replace />
  }

  return (
    <div className="flex h-screen bg-neutral-50">
      <OrgSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="flex flex-1 flex-col">
        <Topbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  )
}
