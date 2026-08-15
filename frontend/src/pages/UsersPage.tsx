import { useState } from 'react'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '@/hooks/useUsers'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { Plus, Pencil, Trash2, Users } from 'lucide-react'
import type { ManagedUser, ManagedUserCreateRequest, ManagedUserUpdateRequest } from '@/types/coreData'
import { UserFormDialog, type UserFormData } from '@/components/dialogs/UserFormDialog'
import { SecurityGroupsPanel } from '@/components/security/SecurityGroupsPanel'
import { UserGroupsModal } from '@/components/security/UserGroupsModal'

export function UsersPage() {
  const { data: users = [], isLoading } = useUsers()
  const createMutation = useCreateUser()
  const updateMutation = useUpdateUser()
  const deleteMutation = useDeleteUser()

  const authStore = useAuthStore()
  const canViewUsers = authStore.hasPermission('CAN_VIEW_USERS') || authStore.hasPermission('CAN_MANAGE_USERS')
  const canManageUsers = authStore.hasPermission('CAN_MANAGE_USERS')
  const canViewSecurity = authStore.hasPermission('CAN_VIEW_SECURITY')
  const canManageSecurity = authStore.hasPermission('CAN_MANAGE_SECURITY')

  const [section, setSection] = useState<'users' | 'groups'>(() => {
    if (canViewUsers) return 'users'
    if (canViewSecurity) return 'groups'
    return 'users'
  })

  const [selectedUserForGroups, setSelectedUserForGroups] = useState<string | null>(null)

  const crud = useCrudPageState<number, UserFormData, ManagedUserCreateRequest, ManagedUserUpdateRequest>({
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
      key: 'status',
      label: 'Status',
      render: (row: ManagedUser) => row.status || '—',
    },
    {
      key: 'is_active',
      label: 'Aktywny',
      render: (row: ManagedUser) => (row.is_active ? '✓' : '✗'),
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: ManagedUser) => (
        <div className="flex gap-2">
          {canManageUsers && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => crud.openEdit(row.id)}
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => crud.requestDelete(row.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </>
          )}
          {canManageSecurity && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedUserForGroups(String(row.id))}
              title="Zarządzaj grupami użytkownika"
            >
              <Users className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="px-6 py-8">
      <div className="mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Użytkownicy i uprawnienia</h1>
          <p className="text-neutral-600">Zarządzanie użytkownikami oraz grupami i uprawnieniami systemu</p>
        </div>
      </div>

      <Tabs
        value={section}
        onValueChange={(value) => {
          if (value === 'users' && !canViewUsers) return
          if (value === 'groups' && !canViewSecurity) return
          setSection(value as 'users' | 'groups')
        }}
      >
        <TabsList>
          {canViewUsers && <TabsTrigger value="users">Użytkownicy</TabsTrigger>}
          {canViewSecurity && <TabsTrigger value="groups">Grupy i uprawnienia</TabsTrigger>}
        </TabsList>

        {canViewUsers && (
          <TabsContent value="users" className="space-y-6">
            <div className="flex items-center justify-between">
              <div />
              {canManageUsers && (
                <Button onClick={crud.openCreate}>
                  <Plus className="mr-2 h-4 w-4" />
                  Nowy użytkownik
                </Button>
              )}
            </div>

            <Card>
              <CardContent className="p-0">
                <DataTable columns={columns} data={users} isLoading={isLoading} />
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {canViewSecurity && (
          <TabsContent value="groups" className="space-y-6">
            <SecurityGroupsPanel users={users} canManage={canManageSecurity} />
          </TabsContent>
        )}
      </Tabs>

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

      {selectedUserForGroups && (
        <UserGroupsModal
          userId={selectedUserForGroups}
          userEmail={users.find((u) => String(u.id) === selectedUserForGroups)?.email || ''}
          onClose={() => setSelectedUserForGroups(null)}
        />
      )}
    </div>
  )
}
