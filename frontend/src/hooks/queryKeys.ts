/* Centralna fabryka kluczy React Query — każdy hook czyta z tego źródła */

export const queryKeys = {
  auth: {
    userContext: () => ['auth', 'userContext'] as const,
  },

  organizations: {
    all: ['organizations'] as const,
    list: (params?: object) => [
      'organizations',
      'list',
      params,
    ] as const,
    detail: (id: string) => ['organizations', 'detail', id] as const,
  },

  waterObjects: {
    all: ['waterObjects'] as const,
    list: (params?: object) => ['waterObjects', 'list', params] as const,
    detail: (id: string) => ['waterObjects', 'detail', id] as const,
    byOrganization: (orgId: string) => ['waterObjects', 'org', orgId] as const,
  },

  devices: {
    all: ['devices'] as const,
    list: (params?: object) => ['devices', 'list', params] as const,
    detail: (id: string) => ['devices', 'detail', id] as const,
    byWaterObject: (objectId: string) => ['devices', 'object', objectId] as const,
  },

  measurementPoints: {
    all: ['measurementPoints'] as const,
    list: (params?: object) => ['measurementPoints', 'list', params] as const,
    detail: (id: string) => ['measurementPoints', 'detail', id] as const,
    byDevice: (deviceId: string) => ['measurementPoints', 'device', deviceId] as const,
  },

  users: {
    all: ['users'] as const,
    list: (params?: object) => ['users', 'list', params] as const,
    detail: (id: string) => ['users', 'detail', id] as const,
    audit: (id: string) => ['users', 'audit', id] as const,
    organizations: (id: string) => ['users', 'organizations', id] as const,
  },

  members: {
    all: ['members'] as const,
    list: (orgId: string) => ['members', orgId] as const,
  },

  orgGroups: {
    all: ['orgGroups'] as const,
    list: (orgId: string) => ['orgGroups', orgId] as const,
  },

  platformGroups: {
    all: ['platformGroups'] as const,
    list: () => ['platformGroups'] as const,
  },

  platformAudit: {
    all: ['platformAudit'] as const,
    list: (params?: { skip?: number; limit?: number }) => ['platformAudit', params] as const,
  },

  telemetry: {
    objects: (orgId: string | null, limit: number) =>
      ['telemetry', 'objects', orgId, limit] as const,
    object: (objectId: string, orgId: string | null) =>
      ['telemetry', 'object', objectId, orgId] as const,
    measurements: (objectId: string, pointId: string | undefined, hoursBack: number, orgId: string | null) =>
      ['telemetry', 'measurements', objectId, pointId, hoursBack, orgId] as const,
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
