import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { TelemetryObjectsList } from '@/components/TelemetryObjectsList'
import { TelemetryDetailChart } from '@/components/TelemetryDetailChart'

export function HomePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null)

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
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Waterworks Monitor</h1>
            <p className="text-sm text-gray-600 mt-1">Panel monitorowania sieci wodociągów</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Wyloguj się
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div>
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Obiekty monitorowania
              </h2>
              <TelemetryObjectsList onSelectObject={setSelectedObjectId} />
            </div>
          </div>

          {/* Main Dashboard */}
          <div className="lg:col-span-3">
            {selectedObjectId ? (
              <TelemetryDetailChart
                objectId={selectedObjectId}
                onClose={() => setSelectedObjectId(null)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <div className="mb-4">
                  <svg
                    className="mx-auto h-16 w-16 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Wybierz obiekt do monitorowania
                </h3>
                <p className="text-gray-600">
                  Kliknij na jeden z obiektów po lewej stronie aby wyświetlić wykresy i szczegóły
                </p>
              </div>
            )}
          </div>
        </div>

        {/* User Info Card */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">
            Profil użytkownika
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-gray-600">Imię</span>
              <p className="font-medium text-gray-900">{user.first_name || '—'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Nazwisko</span>
              <p className="font-medium text-gray-900">{user.last_name || '—'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Email</span>
              <p className="font-medium text-gray-900 text-sm">{user.email}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Status</span>
              <p className="font-medium text-gray-900">{user.status}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
