import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { Sidebar } from './Sidebar'

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    hasPermission: (perm: string) => {
      return ['CAN_VIEW_ASSETS'].includes(perm)
    },
    hasAnyPermission: (perms: string[]) => {
      return perms.some(p => ['CAN_VIEW_ASSETS'].includes(p))
    },
  }),
}))

describe('Sidebar', () => {
  it('renders navigation items', () => {
    render(
      <BrowserRouter>
        <Sidebar isOpen={true} />
      </BrowserRouter>
    )
    expect(screen.getByText('Pulpit')).toBeInTheDocument()
    expect(screen.getByText('Obiekty wodne')).toBeInTheDocument()
  })

  it('renders section headers', () => {
    render(
      <BrowserRouter>
        <Sidebar isOpen={true} />
      </BrowserRouter>
    )
    expect(screen.getByText('Monitorowanie')).toBeInTheDocument()
    expect(screen.getByText('Konfiguracja')).toBeInTheDocument()
  })

  it('hides sections without accessible items', () => {
    // When user has no CAN_VIEW_ORGANIZATIONS permission
    render(
      <BrowserRouter>
        <Sidebar isOpen={true} />
      </BrowserRouter>
    )
    expect(screen.queryByText('Organizacje')).not.toBeInTheDocument()
  })

  it('respects permission-based visibility', () => {
    render(
      <BrowserRouter>
        <Sidebar isOpen={true} />
      </BrowserRouter>
    )
    // CAN_VIEW_ASSETS is mocked as accessible
    expect(screen.getByText('Obiekty wodne')).toBeInTheDocument()
    // CAN_MANAGE_USERS is not mocked, so should be hidden
    expect(screen.queryByText('Użytkownicy')).not.toBeInTheDocument()
  })

  it('calls onClose when link is clicked', () => {
    const handleClose = vi.fn()
    render(
      <BrowserRouter>
        <Sidebar isOpen={true} onClose={handleClose} />
      </BrowserRouter>
    )
    const link = screen.getByText('Pulpit')
    link.click()
    expect(handleClose).toHaveBeenCalled()
  })
})
