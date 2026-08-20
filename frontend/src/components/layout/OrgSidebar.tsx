import { Link, useLocation } from 'react-router-dom'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { cn } from '@/lib/cn'
import { BarChart3, Droplets, GaugeCircle, Users } from 'lucide-react'
import { UserMenu } from './UserMenu'
import type { PermissionCode } from '@/types/permissions'

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
  permissions?: PermissionCode[]
  requireAll?: boolean
  section?: 'monitoring' | 'config' | 'admin'
}

interface OrgSidebarProps {
  isOpen?: boolean
  onClose?: () => void
  collapsed?: boolean
}

export function OrgSidebar({ isOpen = true, onClose, collapsed = false }: OrgSidebarProps) {
  const location = useLocation()
  const { hasPermission, hasAnyPermission } = useActivePermissions()

  const navItems: NavItem[] = [
    {
      label: 'Pulpit',
      path: '/dashboard',
      icon: <BarChart3 className="h-5 w-5" />,
      section: 'monitoring',
    },
    {
      label: 'Obiekty wodne',
      path: '/admin/objects',
      icon: <Droplets className="h-5 w-5" />,
      permissions: ['CAN_VIEW_ASSETS'],
      section: 'config',
    },
    {
      label: 'Urządzenia',
      path: '/admin/devices',
      icon: <GaugeCircle className="h-5 w-5" />,
      permissions: ['CAN_VIEW_ASSETS'],
      section: 'config',
    },
    {
      label: 'Członkowie',
      path: '/admin/members',
      icon: <Users className="h-5 w-5" />,
      permissions: ['CAN_MANAGE_USERS'],
      section: 'admin',
    },
    {
      label: 'Grupy organizacji',
      path: '/admin/groups',
      icon: <Users className="h-5 w-5" />,
      permissions: ['CAN_VIEW_SECURITY'],
      section: 'admin',
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

  const groupedItems = {
    monitoring: navItems.filter((i) => i.section === 'monitoring' && canAccessItem(i)),
    config: navItems.filter((i) => i.section === 'config' && canAccessItem(i)),
    admin: navItems.filter((i) => i.section === 'admin' && canAccessItem(i)),
  }

  const handleLinkClick = () => {
    if (onClose) {
      onClose()
    }
  }

  const sections = [
    { key: 'monitoring', label: 'Monitorowanie', items: groupedItems.monitoring },
    { key: 'config', label: 'Konfiguracja', items: groupedItems.config },
    { key: 'admin', label: 'Administracja', items: groupedItems.admin },
  ]

  return (
    <aside
      className={cn(
        'fixed inset-y-16 left-0 z-40 w-64 bg-surface border-r border-neutral-200 overflow-y-auto transition-all duration-300 lg:static lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        collapsed ? 'lg:w-16' : 'lg:w-64'
      )}
    >
      <nav className={cn('space-y-6 py-4 flex-1', collapsed ? 'px-1' : 'px-2')}>
        {sections.map((section) => {
          if (section.items.length === 0) return null

          return (
            <div key={section.key}>
              <div className="px-3 py-2">
                {!collapsed && (
                  <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                    {section.label}
                  </p>
                )}
              </div>
              <div className="space-y-1">
                {section.items.map((item) => {
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
          )
        })}
      </nav>

      <UserMenu accountPath="/account" onNavigate={handleLinkClick} collapsed={collapsed} />
    </aside>
  )
}
