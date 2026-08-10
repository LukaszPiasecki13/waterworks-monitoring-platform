import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { RequirePermission } from './RequirePermission'

// Mock auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    hasPermission: (perm: string) => perm === 'CAN_VIEW_USERS',
  }),
}))

describe('RequirePermission', () => {
  it('renders children when user has permission', () => {
    render(
      <RequirePermission permission="CAN_VIEW_USERS">
        <div>Protected content</div>
      </RequirePermission>
    )
    expect(screen.getByText('Protected content')).toBeInTheDocument()
  })

  it('does not render children when user lacks permission', () => {
    const { container } = render(
      <RequirePermission permission="CAN_MANAGE_ORGANIZATIONS">
        <div>Protected content</div>
      </RequirePermission>
    )
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })

  it('mounts without error', () => {
    const { container } = render(
      <RequirePermission permission="CAN_MANAGE_ORGANIZATIONS">
        <div>Protected content</div>
      </RequirePermission>
    )
    expect(container).toBeDefined()
  })
})
