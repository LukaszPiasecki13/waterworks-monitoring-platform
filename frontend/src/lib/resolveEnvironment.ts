import type { UserContextResponse, ActiveEnvironment } from '@/types/context'

export interface EnvironmentResolution {
  type: 'single-environment' | 'choose-environment' | 'no-access'
  environment?: ActiveEnvironment
}

export function resolveInitialEnvironment(context: UserContextResponse): EnvironmentResolution {
  const orgCount = context.organizations.length
  const hasPlatform = context.platform !== null
  const totalEnvironments = orgCount + (hasPlatform ? 1 : 0)

  if (totalEnvironments === 0) {
    return { type: 'no-access' }
  }

  if (totalEnvironments === 1) {
    if (hasPlatform) {
      return {
        type: 'single-environment',
        environment: { type: 'platform' },
      }
    } else {
      const org = context.organizations[0]
      return {
        type: 'single-environment',
        environment: {
          type: 'organization',
          organizationId: org.organization_id,
          organizationName: org.organization_name,
        },
      }
    }
  }

  return { type: 'choose-environment' }
}
