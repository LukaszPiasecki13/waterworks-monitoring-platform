import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ActiveEnvironment, OrganizationEnvironment, PlatformEnvironment } from '@/types/context'

interface ActiveEnvironmentState {
  environment: ActiveEnvironment
  setOrganization: (org: { id: string; name: string }) => void
  setPlatform: () => void
  clear: () => void
}

export const useActiveEnvironmentStore = create<ActiveEnvironmentState>()(
  persist(
    (set) => ({
      environment: null,

      setOrganization: (org: { id: string; name: string }) => {
        const environment: OrganizationEnvironment = {
          type: 'organization',
          organizationId: org.id,
          organizationName: org.name,
        }
        set({ environment })
      },

      setPlatform: () => {
        const environment: PlatformEnvironment = { type: 'platform' }
        set({ environment })
      },

      clear: () => {
        set({ environment: null })
      },
    }),
    {
      name: 'active-environment',
    }
  )
)
