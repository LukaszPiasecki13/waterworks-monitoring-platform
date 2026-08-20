import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { cn } from '@/lib/cn'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu'
import { Settings, LogOut } from 'lucide-react'

interface UserMenuProps {
  accountPath: '/account' | '/platform/account'
  onNavigate?: () => void
  collapsed?: boolean
}

export function UserMenu({ accountPath, onNavigate, collapsed = false }: UserMenuProps) {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const clear = useActiveEnvironmentStore((s) => s.clear)

  if (!user) {
    return null
  }

  const handleNavigateToAccount = () => {
    navigate(accountPath)
    onNavigate?.()
  }

  const handleLogout = () => {
    useAuthStore.getState().logout()
    clear()
    navigate('/login', { replace: true })
  }

  const getDisplayName = () => {
    const firstName = user.first_name?.trim()
    const lastName = user.last_name?.trim()
    if (firstName || lastName) {
      return `${firstName || ''} ${lastName || ''}`.trim()
    }
    return user.username
  }

  const getInitial = () => {
    const name = getDisplayName()
    return name.charAt(0).toUpperCase()
  }

  return (
    <div className="border-t border-neutral-200 px-2 py-4">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className={cn('flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium text-neutral-700 hover:bg-neutral-100 transition-colors', collapsed && 'lg:justify-center')}>
            <div className="h-8 w-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-semibold flex-shrink-0">
              {getInitial()}
            </div>
            {!collapsed && (
              <div className="flex flex-col items-start overflow-hidden text-left">
                <div className="truncate font-medium">{getDisplayName()}</div>
                <div className="truncate text-xs text-neutral-500">{user.email}</div>
              </div>
            )}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" side="top" className="w-56">
          <DropdownMenuItem onClick={handleNavigateToAccount}>
            <Settings className="h-4 w-4 mr-2" />
            Ustawienia konta
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600 focus:bg-red-50">
            <LogOut className="h-4 w-4 mr-2" />
            Wyloguj się
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
