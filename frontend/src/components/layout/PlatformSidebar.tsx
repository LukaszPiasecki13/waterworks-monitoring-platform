import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { cn } from '@/lib/cn'
import { Building2, Users, Lock, FileText, ChevronLeft } from 'lucide-react'
import type { PermissionCode } from '@/types/permissions'

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
  permissions?: PermissionCode[]
  requireAll?: boolean
}

interface PlatformSidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export function PlatformSidebar({ isOpen = true, onClose }: PlatformSidebarProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const userContext = useAuthStore((s) => s.userContext)
  const { hasPermission, hasAnyPermission } = useActivePermissions()
  const { setOrganization } = useActiveEnvironmentStore()

  const handleBackToOrganization = () => {
    if (userContext?.organizations.length && userContext.organizations.length > 0) {
      const firstOrg = userContext.organizations[0]
      setOrganization({ id: firstOrg.organization_id, name: firstOrg.organization_name })
      navigate('/dashboard', { replace: true })
      if (onClose) onClose()
    }
  }

  const navItems: NavItem[] = [
    {
      label: 'Organizacje',
      path: '/platform/organizations',
      icon: <Building2 className="h-5 w-5" />,
      permissions: ['PLATFORM_VIEW_ORGANIZATIONS'],
    },
    {
      label: 'Użytkownicy',
      path: '/platform/users',
      icon: <Users className="h-5 w-5" />,
      permissions: ['PLATFORM_VIEW_USERS'],
    },
    {
      label: 'Grupy',
      path: '/platform/groups',
      icon: <Lock className="h-5 w-5" />,
      permissions: ['PLATFORM_VIEW_ORGANIZATIONS'],
    },
    {
      label: 'Audyt',
      path: '/platform/audit',
      icon: <FileText className="h-5 w-5" />,
      permissions: ['PLATFORM_VIEW_AUDIT'],
    },
  ]

  const canAccessItem = (item: NavItem): boolean => {
    if (!item.permissions || item.permissions.length === 0) {
      return true
    }
    if (item.requireAll) {
      return item.permissions.every((p) => hasPermission(p as PermissionCode))
    }
    return hasAnyPermission(item.permissions as PermissionCode[])
  }

  const visibleItems = navItems.filter((i) => canAccessItem(i))

  const handleLinkClick = () => {
    if (onClose) {
      onClose()
    }
  }

  if (visibleItems.length === 0) {
    return null
  }

  return (
    <aside
      className={cn(
        'fixed inset-y-16 left-0 z-40 w-64 bg-surface border-r border-neutral-200 overflow-y-auto transition-transform duration-300 lg:static lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}
    >
      <nav className="space-y-6 px-2 py-4 flex-1">
        <div>
          <div className="px-3 py-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Platforma
            </p>
          </div>
          <div className="space-y-1">
            {visibleItems.map((item) => {
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-brand-50 text-brand-700 font-semibold'
                      : 'text-neutral-700 hover:bg-neutral-100'
                  )}
                >
                  <div
                    className={cn(
                      'flex-shrink-0',
                      isActive ? 'text-brand-600' : 'text-neutral-400'
                    )}
                  >
                    {item.icon}
                  </div>
                  {item.label}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {userContext?.organizations && userContext.organizations.length > 0 && (
        <div className="border-t border-neutral-200 px-2 py-4">
          <button
            onClick={handleBackToOrganization}
            className={cn(
              'flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              'text-neutral-700 hover:bg-neutral-100'
            )}
          >
            <ChevronLeft className="h-5 w-5 text-neutral-400 flex-shrink-0" />
            Wróć do organizacji
          </button>
        </div>
      )}
    </aside>
  )
}
