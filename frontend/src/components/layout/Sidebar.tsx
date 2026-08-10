import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/cn';
import { BarChart3, Settings, Users, Droplets, GaugeCircle } from 'lucide-react';
import type { PermissionCode } from '@/types/permissions';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  permissions?: PermissionCode[];
  requireAll?: boolean;
  section?: 'monitoring' | 'config';
}

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const location = useLocation();
  const { hasPermission, hasAnyPermission } = useAuthStore();

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
      label: 'Organizacje',
      path: '/admin/organizations',
      icon: <Settings className="h-5 w-5" />,
      permissions: ['CAN_VIEW_ORGANIZATIONS'],
      section: 'config',
    },
    {
      label: 'Użytkownicy',
      path: '/admin/users',
      icon: <Users className="h-5 w-5" />,
      permissions: ['CAN_MANAGE_USERS'],
      section: 'config',
    },
  ];

  const canAccessItem = (item: NavItem): boolean => {
    if (!item.permissions || item.permissions.length === 0) {
      return true;
    }
    if (item.requireAll) {
      return item.permissions.every((p) => hasPermission(p as PermissionCode));
    }
    return hasAnyPermission(item.permissions as PermissionCode[]);
  };

  const groupedItems = {
    monitoring: navItems.filter((i) => i.section === 'monitoring' && canAccessItem(i)),
    config: navItems.filter((i) => i.section === 'config' && canAccessItem(i)),
  };

  const handleLinkClick = () => {
    if (onClose) {
      onClose();
    }
  };

  const sections = [
    { key: 'monitoring', label: 'Monitorowanie', items: groupedItems.monitoring },
    { key: 'config', label: 'Konfiguracja', items: groupedItems.config },
  ];

  return (
    <aside
      className={cn(
        'fixed inset-y-16 left-0 z-40 w-64 bg-surface border-r border-neutral-200 overflow-y-auto transition-transform duration-300 lg:static lg:inset-auto',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}
    >
      <nav className="space-y-6 px-2 py-4">
        {sections.map((section) => {
          if (section.items.length === 0) return null;

          return (
            <div key={section.key}>
              <div className="px-3 py-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                  {section.label}
                </p>
              </div>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const isActive = location.pathname === item.path;

                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={handleLinkClick}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-teal-50 text-teal-700 font-semibold'
                          : 'text-neutral-700 hover:bg-neutral-100'
                      )}
                    >
                      <div className={cn(
                        'flex-shrink-0',
                        isActive ? 'text-teal-600' : 'text-neutral-400'
                      )}>
                        {item.icon}
                      </div>
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
