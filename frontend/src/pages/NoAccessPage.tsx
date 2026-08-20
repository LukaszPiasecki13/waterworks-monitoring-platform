import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveEnvironmentStore } from '@/stores/activeEnvironmentStore'
import { Button } from '@/components/ui/Button'
import { AlertCircle } from 'lucide-react'

export function NoAccessPage() {
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const { clear } = useActiveEnvironmentStore()

  const handleLogout = () => {
    logout()
    clear()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-neutral-100 px-4 py-6">
      <div className="w-full max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <h1 className="text-2xl font-bold text-neutral-900">Brak dostępu</h1>
        <p className="mt-2 text-neutral-600">
          Nie masz dostępu do żadnego środowiska. Skontaktuj się z administratorem.
        </p>

        <div className="mt-8">
          <Button onClick={handleLogout} className="w-full">
            Wyloguj się
          </Button>
        </div>
      </div>
    </div>
  )
}
