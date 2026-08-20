import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/authService'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { FormField } from '@/components/ui/FormField'
import { Input } from '@/components/ui/Input'
import { toast } from '@/components/ui/Toast'
import { Shield, Building2 } from 'lucide-react'

interface AccountFormData {
  username: string
  email: string
  first_name: string
  last_name: string
}

export function AccountPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'permissions'>('profile')
  const user = useAuthStore((s) => s.user)
  const userContext = useAuthStore((s) => s.userContext)
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
    <div className="px-6 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Mój profil</h1>
        <p className="text-neutral-600 mt-2">Zarządzanie swoim kontem i ustawieniami</p>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'profile' | 'permissions')}>
        <TabsList>
          <TabsTrigger value="profile">Profil</TabsTrigger>
          <TabsTrigger value="permissions">Dostęp</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
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
        </TabsContent>

        <TabsContent value="permissions" className="space-y-6">
          {userContext ? (
            <>
              {userContext.organizations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Building2 className="h-5 w-5" />
                      Dostęp do organizacji
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {userContext.organizations.map((org) => (
                        <div
                          key={org.organization_id}
                          className="border border-neutral-200 rounded-lg p-4"
                        >
                          <h3 className="font-semibold text-neutral-900">{org.organization_name}</h3>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {org.permissions.length > 0 ? (
                              org.permissions.map((perm) => (
                                <span
                                  key={perm}
                                  className="inline-block px-2 py-1 text-xs rounded bg-blue-50 text-blue-700 border border-blue-200"
                                >
                                  {perm}
                                </span>
                              ))
                            ) : (
                              <span className="text-sm text-neutral-500">Brak uprawnień</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {userContext.platform && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Dostęp do platformy
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {userContext.platform.permissions.length > 0 ? (
                        userContext.platform.permissions.map((perm) => (
                          <span
                            key={perm}
                            className="inline-block px-3 py-1 text-xs rounded bg-purple-50 text-purple-700 border border-purple-200"
                          >
                            {perm}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm text-neutral-500">Brak uprawnień</span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {userContext.organizations.length === 0 && !userContext.platform && (
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-neutral-500">
                      Nie masz dostępu do żadnego środowiska
                    </p>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-neutral-500">Ładowanie uprawnień...</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
