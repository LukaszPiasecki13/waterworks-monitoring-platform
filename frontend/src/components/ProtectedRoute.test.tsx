import { describe, it, expect, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './ProtectedRoute'
import { useAuthStore } from '@/stores/authStore'

const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  status: 'active',
}

function renderWithRouter(initialEntry = '/') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
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
    })
  })

  it('redirects unauthenticated user to /login', () => {
    useAuthStore.setState({ isAuthenticated: false })
    const { container } = renderWithRouter('/')
    expect(container.textContent).toContain('Login Page')
  })

  it('renders protected content when authenticated', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      user: mockUser,
      accessToken: 'token',
    })
    const { container } = renderWithRouter('/')
    expect(container.textContent).toContain('Home Page')
  })
})
