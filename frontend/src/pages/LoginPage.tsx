import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { AxiosError } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/authService'

interface LoginFormData {
  username: string
  password: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuthStore()
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setError('')

    try {
      const { access, refresh } = await authService.login(data)
      const userProfile = await authService.getUserProfile(access)

      login(access, refresh, userProfile)
      navigate('/', { replace: true })
    } catch (err) {
      console.error('Login error:', err)
      const axiosErr = err as AxiosError<{ detail?: string }>
      if (axiosErr.response?.status === 401) {
        setError('Nieprawidłowa nazwa użytkownika lub hasło')
      } else if (axiosErr.response?.data?.detail) {
        setError(axiosErr.response.data.detail)
      } else {
        setError('Wystąpił błąd podczas logowania. Spróbuj ponownie.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-gray-100 px-4 py-6">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-md sm:p-8">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-900">Waterworks Monitor</h1>
        <h2 className="text-xl text-center mb-6 text-gray-600">Logowanie</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Nazwa użytkownika lub email
            </label>
            <input
              id="username"
              type="text"
              {...register('username', {
                required: 'Nazwa użytkownika lub email są wymagane',
              })}
              className="min-h-10 w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="użytkownik lub twój@email.pl"
              disabled={isLoading}
            />
            {errors.username && (
              <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Hasło
            </label>
            <input
              id="password"
              type="password"
              {...register('password', {
                required: 'Hasło jest wymagane',
              })}
              className="min-h-10 w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              disabled={isLoading}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="min-h-10 w-full rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {isLoading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
        </form>
      </div>
    </div>
  )
}
