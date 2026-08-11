/* Centralna fabryka kluczy React Query — każdy hook czyta z tego źródła */

export const queryKeys = {
  organizations: {
    all: ['organizations'] as const,
    list: (params?: Record<string, any>) => [
      'organizations',
      'list',
      params,
    ] as const,
    detail: (id: string) => ['organizations', 'detail', id] as const,
  },

  waterObjects: {
    all: ['waterObjects'] as const,
    list: (params?: Record<string, any>) => ['waterObjects', 'list', params] as const,
    detail: (id: string) => ['waterObjects', 'detail', id] as const,
    byOrganization: (orgId: string) => ['waterObjects', 'org', orgId] as const,
  },

  devices: {
    all: ['devices'] as const,
    list: (params?: Record<string, any>) => ['devices', 'list', params] as const,
    detail: (id: string) => ['devices', 'detail', id] as const,
    byWaterObject: (objectId: string) => ['devices', 'object', objectId] as const,
  },

  measurementPoints: {
    all: ['measurementPoints'] as const,
    list: (params?: Record<string, any>) => ['measurementPoints', 'list', params] as const,
    detail: (id: string) => ['measurementPoints', 'detail', id] as const,
    byDevice: (deviceId: string) => ['measurementPoints', 'device', deviceId] as const,
  },

  users: {
    all: ['users'] as const,
    list: (params?: Record<string, any>) => ['users', 'list', params] as const,
    detail: (id: number) => ['users', 'detail', id] as const,
    audit: (id: number) => ['users', 'audit', id] as const,
  },

  objectStatus: {
    all: ['objectStatus'] as const,
    list: (params?: Record<string, any>) => ['objectStatus', 'list', params] as const,
    detail: (id: string) => ['objectStatus', 'detail', id] as const,
    measurements: (id: string, params?: Record<string, any>) => [
      'objectStatus',
      'measurements',
      id,
      params,
    ] as const,
  },

  security: {
    myPermissions: () => ['security', 'me', 'permissions'] as const,
    permissions: {
      all: ['security', 'permissions'] as const,
      list: () => ['security', 'permissions', 'list'] as const,
    },
    groups: {
      all: ['security', 'groups'] as const,
      list: () => ['security', 'groups', 'list'] as const,
      detail: (id: string) => ['security', 'groups', 'detail', id] as const,
    },
    userGroups: (userId: string) => ['security', 'users', userId, 'groups'] as const,
  },
};
