import { useMemo } from 'react'
import type { PermissionCode } from '@/types/permissions'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'

interface UseActivePermissionsResult {
  permissions: PermissionCode[]
  hasPermission: (permission: PermissionCode) => boolean
  hasAnyPermission: (permissions: PermissionCode[]) => boolean
}

export function useActivePermissions(): UseActivePermissionsResult {
  const userContext = useAuthStore((s) => s.userContext)
  const environment = useActiveEnvironmentStore((s) => s.environment)

  const permissions = useMemo<PermissionCode[]>(() => {
    if (!environment || !userContext) return []

    if (environment.type === 'platform') {
      return (userContext.platform?.permissions ?? []) as PermissionCode[]
    }

    const org = userContext.organizations.find(
      (o) => o.organization_id === environment.organizationId
    )
    return (org?.permissions ?? []) as PermissionCode[]
  }, [environment, userContext])

  return {
    permissions,
    hasPermission: (p: PermissionCode) => permissions.includes(p),
    hasAnyPermission: (ps: PermissionCode[]) => ps.some((p) => permissions.includes(p)),
  }
}
