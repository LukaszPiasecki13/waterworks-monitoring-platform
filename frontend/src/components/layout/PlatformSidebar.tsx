import { Link, useLocation } from 'react-router-dom'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { cn } from '@/lib/cn'
import { Building2, Users, Lock, FileText, KeyRound, Cpu } from 'lucide-react'
import { UserMenu } from './UserMenu'
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
  collapsed?: boolean
}

export function PlatformSidebar({ isOpen = true, onClose, collapsed = false }: PlatformSidebarProps) {
  const location = useLocation()
  const { hasPermission, hasAnyPermission } = useActivePermissions()

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
      label: 'Kody aktywacyjne',
      path: '/platform/activation-codes',
      icon: <KeyRound className="h-5 w-5" />,
      permissions: ['PLATFORM_MANAGE_DEVICE_PROVISIONING'],
    },
    {
      label: 'Wszystkie urządzenia',
      path: '/platform/devices',
      icon: <Cpu className="h-5 w-5" />,
      permissions: ['PLATFORM_MANAGE_DEVICE_PROVISIONING'],
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
        'fixed inset-y-16 left-0 z-40 w-64 bg-surface border-r border-neutral-200 overflow-y-auto transition-all duration-300 lg:static lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        collapsed ? 'lg:w-16' : 'lg:w-64'
      )}
    >
      <nav className={cn('space-y-6 py-4 flex-1', collapsed ? 'px-1' : 'px-2')}>
        <div>
          <div className="px-3 py-2">
            {!collapsed && (
              <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Platforma
              </p>
            )}
          </div>
          <div className="space-y-1">
            {visibleItems.map((item) => {
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  title={collapsed ? item.label : undefined}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    collapsed && 'lg:justify-center',
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
                  {!collapsed && item.label}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      <UserMenu accountPath="/platform/account" onNavigate={onClose} collapsed={collapsed} />
    </aside>
  )
}
