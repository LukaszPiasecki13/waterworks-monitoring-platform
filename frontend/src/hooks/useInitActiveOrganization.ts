import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useActiveOrganizationStore } from '@/stores/activeOrganizationStore'
import { useOrganizations } from './useOrganizations'

export function useInitActiveOrganization() {
  const user = useAuthStore((state) => state.user)
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)
  const setActiveOrganization = useActiveOrganizationStore((state) => state.setActiveOrganization)
  const clearActiveOrganization = useActiveOrganizationStore((state) => state.clear)

  const isPlatformAdmin = user?.organization_id === null

  // Fetch organizations for admin only
  const { data: organizations } = isPlatformAdmin
    ? useOrganizations({ limit: 1 })
    : { data: undefined }

  useEffect(() => {
    if (!user) {
      clearActiveOrganization()
      return
    }

    if (!isPlatformAdmin) {
      // Regular user: always force their organization
      if (user.organization_id) {
        setActiveOrganization({
          id: user.organization_id,
          name: 'Organization', // Backend should provide org name; fallback to generic placeholder
        })
      }
    } else {
      // Platform admin
      if (activeOrgId) {
        // Already has a saved value — validation would go here if we fetch full list
        // For now, trust what's in localStorage
      } else if (organizations && organizations.length > 0) {
        // No saved value, set first organization as default
        const firstOrg = organizations[0]
        setActiveOrganization({
          id: firstOrg.id,
          name: firstOrg.name,
        })
      } else if (!organizations && !activeOrgId) {
        // Admin with no organizations at all
        clearActiveOrganization()
      }
    }
  }, [user, isPlatformAdmin, organizations, activeOrgId, setActiveOrganization, clearActiveOrganization])
}
