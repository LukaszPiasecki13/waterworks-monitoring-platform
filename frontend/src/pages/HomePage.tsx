import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export function HomePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  if (!user) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="min-h-dvh bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Waterworks Monitor</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Wyloguj się
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Witaj, {user.first_name || user.username}!</h2>
          <div className="space-y-2 text-gray-600">
            <p>
              <span className="font-medium">Email:</span> {user.email}
            </p>
            <p>
              <span className="font-medium">Status:</span> {user.status}
            </p>
            {user.last_name && (
              <p>
                <span className="font-medium">Nazwisko:</span> {user.last_name}
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
