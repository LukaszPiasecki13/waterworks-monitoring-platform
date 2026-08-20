import { describe, it, expect, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './ProtectedRoute'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'

const mockUser = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  is_active: true,
}

function renderWithRouter(initialEntry = '/') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/environment-picker" element={<div>Environment Picker</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<div>Home Page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
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

  it('redirects unauthenticated user to /login', () => {
    useAuthStore.setState({ isAuthenticated: false })
    const { container } = renderWithRouter('/')
    expect(container.textContent).toContain('Login Page')
  })

  it('renders protected content when authenticated with environment', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      user: mockUser,
      accessToken: 'token',
    })
    useActiveEnvironmentStore.setState({
      environment: {
        type: 'organization',
        organizationId: 'org-1',
        organizationName: 'Test Org',
      },
    })
    const { container } = renderWithRouter('/')
    expect(container.textContent).toContain('Home Page')
  })

  it('redirects to environment picker when authenticated but no environment selected', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      user: mockUser,
      accessToken: 'token',
    })
    useActiveEnvironmentStore.setState({ environment: null })
    const { container } = renderWithRouter('/')
    expect(container.textContent).toContain('Environment Picker')
  })
})
