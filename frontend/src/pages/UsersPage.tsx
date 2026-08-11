import { useState } from 'react'
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '@/hooks/useUsers'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { toast } from '@/components/ui/Toast'
import { Plus, Pencil, Trash2, Users } from 'lucide-react'
import type { ManagedUser } from '@/types/coreData'
import { UserFormDialog } from '@/components/dialogs/UserFormDialog'
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

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [selectedUserForGroups, setSelectedUserForGroups] = useState<string | null>(null)

  const handleCreate = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setIsFormOpen(false)
        toast.success('Użytkownik utworzony')
      },
      onError: (error: any) => {
        toast.error(error.message || 'Błąd przy tworzeniu')
      },
    })
  }

  const handleUpdate = (data: any) => {
    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data },
        {
          onSuccess: () => {
            setIsFormOpen(false)
            setEditingId(null)
            toast.success('Użytkownik zaktualizowany')
          },
          onError: (error: any) => {
            toast.error(error.message || 'Błąd przy aktualizacji')
          },
        }
      )
    }
  }

  const handleDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId, {
        onSuccess: () => {
          setDeleteId(null)
          toast.success('Użytkownik usunięty')
        },
        onError: (error: any) => {
          toast.error(error.message || 'Błąd przy usuwaniu')
        },
      })
    }
  }

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
                onClick={() => {
                  setEditingId(row.id)
                  setIsFormOpen(true)
                }}
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setDeleteId(row.id)}
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
                <Button
                  onClick={() => {
                    setEditingId(null)
                    setIsFormOpen(true)
                  }}
                >
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
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        userId={editingId}
        onSubmit={editingId ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Usuń użytkownika"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć tego użytkownika?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
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
