import { useState } from 'react'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '@/hooks/useUsers'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Plus, Pencil, Trash2, Building2, Users } from 'lucide-react'
import type { ManagedUser, ManagedUserCreateRequest, ManagedUserUpdateRequest } from '@/types/coreData'
import { UserFormDialog, type UserFormData } from '@/components/dialogs/UserFormDialog'
import { ManageUserOrganizationsDialog } from '@/components/dialogs/ManageUserOrganizationsDialog'

export function PlatformUsersPage() {
  const { data: users = [], isLoading } = useUsers()
  const createMutation = useCreateUser()
  const updateMutation = useUpdateUser()
  const deleteMutation = useDeleteUser()
  const { hasPermission } = useActivePermissions()
  const [orgDialogUser, setOrgDialogUser] = useState<ManagedUser | null>(null)

  const canManageUsers = hasPermission('PLATFORM_MANAGE_USERS')

  const crud = useCrudPageState<string, UserFormData, ManagedUserCreateRequest, ManagedUserUpdateRequest>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Użytkownik utworzony',
      updateSuccess: 'Użytkownik zaktualizowany',
      deleteSuccess: 'Użytkownik usunięty',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
  })

  const columns = [
    {
      key: 'username',
      label: 'Nazwa użytkownika',
      render: (row: ManagedUser) => row.username,
    },
    {
      key: 'email',
      label: 'Email',
      render: (row: ManagedUser) => row.email,
    },
    {
      key: 'is_active',
      label: 'Aktywny',
      render: (row: ManagedUser) => (row.is_active ? '✓' : '✗'),
    },
    ...(canManageUsers
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: ManagedUser) => (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setOrgDialogUser(row)}
                  aria-label={`Zarządzaj organizacjami użytkownika ${row.username}`}
                >
                  <Building2 className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => crud.openEdit(row.id)}
                  aria-label={`Edytuj użytkownika ${row.username}`}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => crud.requestDelete(row.id)}
                  aria-label={`Usuń użytkownika ${row.username}`}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ),
          },
        ]
      : []),
  ]

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Użytkownicy</h1>
          <p className="text-neutral-600">Zarządzanie użytkownikami platformy</p>
        </div>
        {canManageUsers && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Nowy użytkownik
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={users}
            isLoading={isLoading}
            emptyState={canManageUsers ? {
              icon: <Users className="h-12 w-12" />,
              title: 'Brak użytkowników',
              subtitle: 'Utwórz konta dla administratorów i operatorów',
              ctaLabel: 'Dodaj użytkownika',
              onCta: () => crud.openCreate(),
            } : undefined}
          />
        </CardContent>
      </Card>

      {canManageUsers && (
        <>
          <UserFormDialog
            open={crud.isFormOpen}
            onOpenChange={crud.setIsFormOpen}
            userId={crud.editingId}
            onSubmit={crud.handleSubmit}
            isLoading={crud.isSubmitting}
            serverFieldErrors={crud.serverFieldErrors}
          />

          <ConfirmDialog
            open={!!crud.deleteId}
            onOpenChange={(open) => !open && crud.cancelDelete()}
            title="Usuń użytkownika"
            description="Ta akcja nie może być cofnięta."
            message="Czy na pewno chcesz usunąć tego użytkownika?"
            confirmText="Usuń"
            cancelText="Anuluj"
            isDestructive
            isLoading={crud.isDeleting}
            onConfirm={crud.confirmDelete}
          />

          <ManageUserOrganizationsDialog
            userId={orgDialogUser?.id ?? null}
            username={orgDialogUser?.username}
            open={!!orgDialogUser}
            onOpenChange={(open) => !open && setOrgDialogUser(null)}
          />
        </>
      )}
    </div>
  )
}
