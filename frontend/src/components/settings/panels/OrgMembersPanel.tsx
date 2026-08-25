import { useState } from 'react'
import { useMembers, useRemoveMember } from '@/hooks/useMembers'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { AddMemberDialog } from '@/components/dialogs/AddMemberDialog'
import { Plus, Trash2 } from 'lucide-react'
import type { OrganizationMember } from '@/types/coreData'

export function OrgMembersPanel() {
  const { data: members = [], isLoading } = useMembers()
  const removeMutation = useRemoveMember()
  const { hasPermission } = useActivePermissions()

  const canManageMemberships = hasPermission('CAN_MANAGE_USERS')

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [memberToDelete, setMemberToDelete] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDeleteMember = async () => {
    if (!memberToDelete) return
    setIsDeleting(true)
    try {
      await removeMutation.mutateAsync(memberToDelete)
      setMemberToDelete(null)
    } finally {
      setIsDeleting(false)
    }
  }

  const columns = [
    {
      key: 'username',
      label: 'Nazwa użytkownika',
      render: (row: OrganizationMember) => row.username,
    },
    {
      key: 'email',
      label: 'Email',
      render: (row: OrganizationMember) => row.email,
    },
    {
      key: 'first_name',
      label: 'Imię',
      render: (row: OrganizationMember) => row.first_name || '—',
    },
    {
      key: 'last_name',
      label: 'Nazwisko',
      render: (row: OrganizationMember) => row.last_name || '—',
    },
    {
      key: 'actions',
      label: 'Akcje',
      width: '76px',
      render: (row: OrganizationMember) => (
        <div className="flex gap-2">
          {canManageMemberships && (
            <Button
              variant="outline"
              size="sm"
              className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
              onClick={() => setMemberToDelete(row.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <>
      <div className="px-6 pt-6 pb-4 border-b border-neutral-200">
        <h2 className="text-lg font-semibold text-neutral-900">Członkowie</h2>
        <p className="text-sm text-neutral-600 mt-1">Zarządzaj członkami organizacji</p>
      </div>

      <div className="flex items-center justify-between mb-6 px-6 pt-6">
        {canManageMemberships && (
          <Button onClick={() => setIsAddDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Dodaj członka
          </Button>
        )}
      </div>

      <div className="px-6 pb-6">
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={members} isLoading={isLoading} />
          </CardContent>
        </Card>
      </div>

      <AddMemberDialog
        open={isAddDialogOpen}
        onOpenChange={setIsAddDialogOpen}
      />

      <ConfirmDialog
        open={!!memberToDelete}
        onOpenChange={(open) => !open && setMemberToDelete(null)}
        title="Usuń członka"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz usunąć tego członka z organizacji?"
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={isDeleting}
        onConfirm={handleDeleteMember}
      />
    </>
  )
}
