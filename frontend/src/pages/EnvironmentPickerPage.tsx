import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { resolveInitialEnvironment } from '@/lib/resolveEnvironment'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Building2, Shield } from 'lucide-react'

export function EnvironmentPickerPage() {
  const navigate = useNavigate()
  const { userContext } = useAuthStore()
  const { setOrganization, setPlatform } = useActiveEnvironmentStore()
  const navigationAttemptedRef = useRef(false)

  useEffect(() => {
    if (navigationAttemptedRef.current) return

    if (!userContext) {
      navigationAttemptedRef.current = true
      navigate('/login', { replace: true })
      return
    }

    const resolution = resolveInitialEnvironment(userContext)
    if (resolution.type === 'single-environment') {
      navigationAttemptedRef.current = true
      if (resolution.environment?.type === 'platform') {
        setPlatform()
      } else if (resolution.environment?.type === 'organization') {
        setOrganization({
          id: resolution.environment.organizationId,
          name: resolution.environment.organizationName,
        })
      }
      navigate('/', { replace: true })
    } else if (resolution.type === 'no-access') {
      navigationAttemptedRef.current = true
      navigate('/no-access', { replace: true })
    }
  }, [userContext, setOrganization, setPlatform, navigate])

  if (!userContext) {
    return null
  }

  const handleSelectOrganization = (orgId: string, orgName: string) => {
    setOrganization({ id: orgId, name: orgName })
    navigate('/dashboard', { replace: true })
  }

  const handleSelectPlatform = () => {
    setPlatform()
    navigate('/platform/organizations', { replace: true })
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-neutral-100 px-4 py-6">
      <div className="w-full max-w-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-neutral-900">Waterworks Monitor</h1>
          <p className="mt-2 text-neutral-600">Wybierz środowisko</p>
        </div>

        <div className="grid gap-4">
          {userContext.organizations.length > 0 && (
            <div>
              <h2 className="mb-3 text-sm font-semibold text-neutral-700">Organizacje</h2>
              <div className="space-y-2">
                {userContext.organizations.map((org) => (
                  <button
                    key={org.organization_id}
                    onClick={() =>
                      handleSelectOrganization(org.organization_id, org.organization_name)
                    }
                    className="text-left transition-all hover:shadow-md"
                  >
                    <Card className="border-2 border-transparent hover:border-blue-500">
                      <CardHeader className="pb-3">
                        <div className="flex items-start gap-3">
                          <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                            <Building2 className="h-6 w-6 text-blue-600" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">{org.organization_name}</CardTitle>
                            <p className="text-sm text-neutral-600">
                              {org.permissions.length} uprawnienie
                              {org.permissions.length !== 1 ? 'ń' : ''}
                            </p>
                          </div>
                        </div>
                      </CardHeader>
                    </Card>
                  </button>
                ))}
              </div>
            </div>
          )}

          {userContext.platform && (
            <div>
              <h2 className="mb-3 text-sm font-semibold text-neutral-700">Platforma</h2>
              <button
                onClick={handleSelectPlatform}
                className="text-left transition-all hover:shadow-md w-full"
              >
                <Card className="border-2 border-transparent hover:border-blue-500">
                  <CardHeader className="pb-3">
                    <div className="flex items-start gap-3">
                      <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
                        <Shield className="h-6 w-6 text-purple-600" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">Platforma</CardTitle>
                        <p className="text-sm text-neutral-600">
                          {userContext.platform.permissions.length} uprawnienie
                          {userContext.platform.permissions.length !== 1 ? 'ń' : ''}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
