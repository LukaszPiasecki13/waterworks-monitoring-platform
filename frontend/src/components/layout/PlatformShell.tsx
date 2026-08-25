import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { Topbar } from './Topbar'
import { PlatformSidebar } from './PlatformSidebar'
import { SettingsDialog } from '@/components/settings/SettingsDialog'

interface PlatformShellProps {
  children: React.ReactNode
}

export function PlatformShell({ children }: PlatformShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const environment = useActiveEnvironmentStore((s) => s.environment)

  // Guard: Only redirect if environment is null (not set)
  // DO NOT redirect just because environment.type !== 'platform' - that's a transient state
  // during normal switching and React Router will handle route matching correctly
  if (!environment) {
    return <Navigate to="/environment-picker" replace />
  }

  return (
    <div className="flex h-screen bg-neutral-50">
      <PlatformSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} collapsed={collapsed} onOpenSettings={() => setSettingsOpen(true)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="flex flex-1 flex-col">
        <Topbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} collapsed={collapsed} onToggleSidebar={() => setCollapsed((c) => !c)} />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>

      <SettingsDialog scope="platform" open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  )
}
