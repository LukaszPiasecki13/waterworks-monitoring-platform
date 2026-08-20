import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'

export function useOrgId(): string | null {
  return useActiveEnvironmentStore((state) => {
    if (state.environment?.type === 'organization') {
      return state.environment.organizationId
    }
    return null
  })
}
