import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ActiveOrganizationState {
  activeOrganizationId: string | null
  activeOrganizationName: string | null
  setActiveOrganization: (org: { id: string; name: string }) => void
  clear: () => void
}

export const useActiveOrganizationStore = create<ActiveOrganizationState>()(
  persist(
    (set) => ({
      activeOrganizationId: null,
      activeOrganizationName: null,

      setActiveOrganization: (org: { id: string; name: string }) => {
        set({
          activeOrganizationId: org.id,
          activeOrganizationName: org.name,
        })
      },

      clear: () => {
        set({
          activeOrganizationId: null,
          activeOrganizationName: null,
        })
      },
    }),
    {
      name: 'active-organization',
    }
  )
)
