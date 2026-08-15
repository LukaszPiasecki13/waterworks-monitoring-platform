import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/authService'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { FormField } from '@/components/ui/FormField'
import { Input } from '@/components/ui/Input'
import { toast } from '@/components/ui/Toast'

interface AccountFormData {
  username: string
  email: string
  first_name: string
  last_name: string
}

export function AccountPage() {
  const user = useAuthStore((s) => s.user)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AccountFormData>({
    defaultValues: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
    },
  })

  useEffect(() => {
    if (user) {
      reset({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      })
    }
  }, [user, reset])

  const onSubmit = async (data: AccountFormData) => {
    try {
      const updated = await authService.updateProfile({
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
      })

      useAuthStore.setState({ user: updated })
      toast.success('Profil zaktualizowany')
    } catch (error: unknown) {
      toast.error(error instanceof Error ? error.message : 'Błąd przy aktualizacji profilu')
    }
  }

  if (!user) {
    return (
      <div className="px-6 py-8">
        <div className="text-neutral-500">Ładowanie profilu...</div>
      </div>
    )
  }

  return (
    <div className="px-6 py-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Mój profil</h1>
        <p className="text-neutral-600 mt-2">Zarządzanie swoim kontem i ustawieniami</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dane profilu</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <FormField label="Nazwa użytkownika" error={errors.username?.message} required>
              <Input {...register('username')} disabled placeholder="Nazwa użytkownika" />
            </FormField>

            <FormField label="Email" error={errors.email?.message} required>
              <Input
                {...register('email', { required: 'Email jest wymagany' })}
                type="email"
                placeholder="Email"
              />
            </FormField>

            <FormField label="Imię" error={errors.first_name?.message}>
              <Input {...register('first_name')} placeholder="Imię" />
            </FormField>

            <FormField label="Nazwisko" error={errors.last_name?.message}>
              <Input {...register('last_name')} placeholder="Nazwisko" />
            </FormField>

            <div className="pt-4 flex gap-3 justify-end">
              <Button variant="outline" type="button">
                Anuluj
              </Button>
              <Button type="submit" isLoading={isSubmitting}>
                Zapisz zmiany
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Uprawnienia</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-neutral-600">
            <p>
              Status: <span className="font-semibold text-neutral-900">{user.status}</span>
            </p>
            <p className="mt-2 text-xs text-neutral-500">
              Twoje uprawnienia do zasobów są zarządzane przez administratora systemu.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
