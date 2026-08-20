import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { Button } from '@/components/ui/Button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu'
import { Building2, Shield, LogOut, ChevronDown } from 'lucide-react'

export function EnvironmentSwitcher() {
  const navigate = useNavigate()
  const { userContext } = useAuthStore()
  const { environment, setOrganization, setPlatform, clear } = useActiveEnvironmentStore()

  if (!userContext || !environment) {
    return null
  }

  const handleSwitchOrganization = (orgId: string, orgName: string) => {
    setOrganization({ id: orgId, name: orgName })
    navigate('/dashboard', { replace: true })
  }

  const handleSwitchPlatform = () => {
    setPlatform()
    navigate('/platform/organizations', { replace: true })
  }

  const handleSwitchEnvironment = () => {
    navigate('/environment-picker', { replace: true })
  }

  const handleLogout = () => {
    const { logout } = useAuthStore.getState()
    logout()
    clear()
    navigate('/login', { replace: true })
  }

  const getDisplayLabel = () => {
    if (environment.type === 'platform') {
      return 'Platforma'
    }
    return environment.organizationName
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="gap-2"
        >
          {environment.type === 'platform' ? (
            <Shield className="h-4 w-4" />
          ) : (
            <Building2 className="h-4 w-4" />
          )}
          <span className="hidden sm:inline">{getDisplayLabel()}</span>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <div className="px-3 py-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500 mb-2">
            Organizacje
          </p>
          {userContext.organizations.length > 0 ? (
            userContext.organizations.map((org) => (
              <DropdownMenuItem
                key={org.organization_id}
                onClick={() => handleSwitchOrganization(org.organization_id, org.organization_name)}
                className={environment.type === 'organization' && environment.organizationId === org.organization_id ? 'bg-blue-50' : ''}
              >
                <Building2 className="h-4 w-4 mr-2" />
                <span>{org.organization_name}</span>
              </DropdownMenuItem>
            ))
          ) : (
            <div className="px-3 py-1 text-xs text-neutral-500">
              Brak dostępu do organizacji
            </div>
          )}
        </div>

        {userContext.platform && (
          <>
            <DropdownMenuSeparator />
            <div className="px-3 py-2">
              <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500 mb-2">
                Platforma
              </p>
              <DropdownMenuItem
                onClick={handleSwitchPlatform}
                className={environment.type === 'platform' ? 'bg-purple-50' : ''}
              >
                <Shield className="h-4 w-4 mr-2" />
                <span>Platforma</span>
              </DropdownMenuItem>
            </div>
          </>
        )}

        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleSwitchEnvironment}>
          Zmień środowisko
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600 focus:bg-red-50">
          <LogOut className="h-4 w-4 mr-2" />
          Wyloguj się
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
