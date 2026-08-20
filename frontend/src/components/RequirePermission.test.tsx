import { render, screen } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { RequirePermission } from './RequirePermission'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import type { UserContextResponse } from '@/types/context'
import type { PermissionCode } from '@/types/permissions'

function renderRequirePermission(
  permission: PermissionCode | undefined,
  children: React.ReactNode,
  permissions?: PermissionCode[]
) {
  return render(
    <MemoryRouter initialEntries={['/test']}>
      <Routes>
        <Route path="/forbidden" element={<div>Forbidden Page</div>} />
        <Route
          path="/test"
          element={
            <RequirePermission permission={permission} permissions={permissions}>
              {children}
            </RequirePermission>
          }
        />
      </Routes>
    </MemoryRouter>
  )
}

describe('RequirePermission', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      userContext: null,
    })
    useActiveEnvironmentStore.setState({ environment: null })
  })

  it('renders children when user has permission in active organization', () => {
    const userContext: UserContextResponse = {
      organizations: [
        {
          organization_id: 'org-1',
          organization_name: 'Org 1',
          permissions: ['CAN_VIEW_USERS'],
        },
      ],
      platform: null,
    }
    useAuthStore.setState({ userContext })
    useActiveEnvironmentStore.setState({
      environment: {
        type: 'organization',
        organizationId: 'org-1',
        organizationName: 'Org 1',
      },
    })

    renderRequirePermission('CAN_VIEW_USERS', <div>Protected content</div>)
    expect(screen.getByText('Protected content')).toBeInTheDocument()
  })

  it('does not render children when user lacks permission in active organization', () => {
    const userContext: UserContextResponse = {
      organizations: [
        {
          organization_id: 'org-1',
          organization_name: 'Org 1',
          permissions: ['CAN_VIEW_ASSETS'],
        },
      ],
      platform: null,
    }
    useAuthStore.setState({ userContext })
    useActiveEnvironmentStore.setState({
      environment: {
        type: 'organization',
        organizationId: 'org-1',
        organizationName: 'Org 1',
      },
    })

    renderRequirePermission('CAN_VIEW_USERS', <div>Protected content</div>)
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
    expect(screen.getByText('Forbidden Page')).toBeInTheDocument()
  })

  it('renders children when user has permission in platform', () => {
    const userContext: UserContextResponse = {
      organizations: [],
      platform: {
        permissions: ['PLATFORM_VIEW_ORGANIZATIONS'],
      },
    }
    useAuthStore.setState({ userContext })
    useActiveEnvironmentStore.setState({
      environment: { type: 'platform' },
    })

    renderRequirePermission('PLATFORM_VIEW_ORGANIZATIONS', <div>Platform content</div>)
    expect(screen.getByText('Platform content')).toBeInTheDocument()
  })

  it('does not render when user has no context', () => {
    useAuthStore.setState({ userContext: null })
    useActiveEnvironmentStore.setState({ environment: null })

    renderRequirePermission('CAN_VIEW_USERS', <div>Protected content</div>)
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })

  it('supports multiple permissions with anyOf logic', () => {
    const userContext: UserContextResponse = {
      organizations: [
        {
          organization_id: 'org-1',
          organization_name: 'Org 1',
          permissions: ['CAN_VIEW_ASSETS'],
        },
      ],
      platform: null,
    }
    useAuthStore.setState({ userContext })
    useActiveEnvironmentStore.setState({
      environment: {
        type: 'organization',
        organizationId: 'org-1',
        organizationName: 'Org 1',
      },
    })

    renderRequirePermission(undefined, <div>Multi-perm content</div>, [
      'CAN_VIEW_USERS',
      'CAN_VIEW_ASSETS',
    ])
    expect(screen.getByText('Multi-perm content')).toBeInTheDocument()
  })
})
