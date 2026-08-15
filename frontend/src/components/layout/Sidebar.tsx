import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/cn';
import { BarChart3, Settings, Users, Droplets, GaugeCircle, LogOut, User, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu';
import type { PermissionCode } from '@/types/permissions';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  permissions?: PermissionCode[];
  requireAll?: boolean;
  section?: 'monitoring' | 'config' | 'admin';
}

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, hasPermission, hasAnyPermission } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const displayName = user ? `${user.first_name} ${user.last_name}`.trim() || user.username : 'User';

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
      section: 'admin',
    },
    {
      label: 'Ustawienia',
      path: '/admin/users',
      icon: <Users className="h-5 w-5" />,
      permissions: ['CAN_VIEW_USERS', 'CAN_MANAGE_USERS', 'CAN_VIEW_SECURITY'],
      section: 'admin',
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
    admin: navItems.filter((i) => i.section === 'admin' && canAccessItem(i)),
  };

  const handleLinkClick = () => {
    if (onClose) {
      onClose();
    }
  };

  const sections = [
    { key: 'monitoring', label: 'Monitorowanie', items: groupedItems.monitoring },
    { key: 'config', label: 'Konfiguracja', items: groupedItems.config },
    { key: 'admin', label: 'Administracja', items: groupedItems.admin },
  ];

  return (
    <aside
      className={cn(
        'fixed inset-y-16 left-0 z-40 w-64 bg-surface border-r border-neutral-200 overflow-y-auto transition-transform duration-300 lg:static lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}
    >
      <nav className="space-y-6 px-2 py-4 flex-1">
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
                          ? 'bg-brand-50 text-brand-700 font-semibold'
                          : 'text-neutral-700 hover:bg-neutral-100'
                      )}
                    >
                      <div className={cn(
                        'flex-shrink-0',
                        isActive ? 'text-brand-600' : 'text-neutral-400'
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

      <div className="border-t border-neutral-200 px-2 py-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-between px-3 py-2 text-left"
            >
              <div className="flex-1">
                <p className="text-sm font-medium text-neutral-900 truncate">{displayName}</p>
                <p className="text-xs text-neutral-500 truncate">{user?.email}</p>
              </div>
              <ChevronUp className="h-4 w-4 text-neutral-400 flex-shrink-0" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" side="top" className="w-56">
            <DropdownMenuItem asChild>
              <Link
                to="/account"
                onClick={handleLinkClick}
                className="flex items-center gap-2 cursor-pointer"
              >
                <User className="h-4 w-4" />
                Mój profil
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                handleLinkClick();
                handleLogout();
              }}
              className="text-red-600 focus:text-red-600 focus:bg-red-50"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Wyloguj się
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
