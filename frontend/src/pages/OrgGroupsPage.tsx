import { useMemo } from 'react'
import {
  useOrgGroups,
  useCreateOrgGroup,
  useSaveOrgGroup,
  useReplaceOrgGroupUsers,
  useDeleteOrgGroup,
} from '@/hooks/useOrgGroups'
import { useMembers } from '@/hooks/useMembers'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Plus, Pencil, Trash2, Shield } from 'lucide-react'
import { GroupFormDialog, type GroupFormData, type SelectableUser } from '@/components/dialogs/GroupFormDialog'
import { PERMISSION_CATALOG } from '@/types/permissions'
import type { SecurityGroupSummary, SecurityGroupSaveRequest } from '@/types/coreData'

export function OrgGroupsPage() {
  const { data: groups = [], isLoading } = useOrgGroups()
  const { data: members = [] } = useMembers()
  const createMutation = useCreateOrgGroup()
  const saveMutation = useSaveOrgGroup()
  const replaceUsersMutation = useReplaceOrgGroupUsers()
  const deleteMutation = useDeleteOrgGroup()
  const { hasPermission } = useActivePermissions()

  const canManage = hasPermission('CAN_MANAGE_SECURITY')

  const availablePermissions = useMemo(
    () =>
      PERMISSION_CATALOG.filter((p) => p.plane === 'organization').map((p) => ({
        id: p.code,
        code: p.code,
        name: p.name,
        category: p.category,
      })),
    []
  )

  const availableUsers: SelectableUser[] = useMemo(
    () => members.map((m) => ({ id: m.id, label: `${m.first_name} ${m.last_name} (${m.email})` })),
    [members]
  )

  const crud = useCrudPageState<
    string,
    GroupFormData,
    { name: string; description?: string; permission_codes: string[] },
    SecurityGroupSaveRequest,
    SecurityGroupSummary
  >({
    createMutation,
    updateMutation: saveMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Grupa utworzona',
      updateSuccess: 'Grupa zaktualizowana',
      deleteSuccess: 'Grupa usunięta',
      createErrorFallback: 'Błąd przy tworzeniu grupy',
      updateErrorFallback: 'Błąd przy aktualizacji grupy',
      deleteErrorFallback: 'Błąd przy usuwaniu grupy',
    },
    toCreateInput: (data) => ({
      name: data.name,
      description: data.description,
      permission_codes: data.permission_codes,
    }),
    toUpdateInput: (data) => ({
      name: data.name,
      description: data.description ?? '',
      permission_codes: data.permission_codes,
      user_ids: data.user_ids,
    }),
    onCreateSuccess: (createdGroup, formData) => {
      if (formData.user_ids.length > 0) {
        replaceUsersMutation.mutate({ id: createdGroup.id, userIds: formData.user_ids })
      }
    },
  })

  const currentGroup = groups.find((g: SecurityGroupSummary) => g.id === crud.editingId) ?? null

  const columns = [
    { key: 'name', label: 'Nazwa grupy', render: (row: SecurityGroupSummary) => row.name },
    {
      key: 'permissions_count',
      label: 'Uprawnienia',
      render: (row: SecurityGroupSummary) => row.permissions?.length || 0,
    },
    { key: 'description', label: 'Opis', render: (row: SecurityGroupSummary) => row.description || '—' },
    ...(canManage
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: SecurityGroupSummary) => (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => crud.openEdit(row.id)} aria-label={`Edytuj grupę ${row.name}`}>
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  disabled={row.is_system}
                  aria-label={`Usuń grupę ${row.name}`}
                  title={row.is_system ? 'Nie możesz usunąć grupy systemowej' : undefined}
                  onClick={() => crud.requestDelete(row.id)}
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
          <h1 className="text-3xl font-bold text-neutral-900">Grupy organizacji</h1>
          <p className="text-neutral-600">Grupy uprawnień w organizacji</p>
        </div>
        {canManage && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Nowa grupa
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={groups}
            isLoading={isLoading}
            emptyState={canManage ? {
              icon: <Shield className="h-12 w-12" />,
              title: 'Brak grup bezpieczeństwa',
              subtitle: 'Utwórz grupy uprawnień dla członków organizacji',
              ctaLabel: 'Dodaj grupę',
              onCta: () => crud.openCreate(),
            } : undefined}
          />
        </CardContent>
      </Card>

      {canManage && (
        <>
          <GroupFormDialog
            open={crud.isFormOpen}
            onOpenChange={crud.setIsFormOpen}
            group={currentGroup}
            availablePermissions={availablePermissions}
            availableUsers={availableUsers}
            onSubmit={crud.handleSubmit}
            isLoading={crud.isSubmitting}
            serverFieldErrors={crud.serverFieldErrors}
          />

          <ConfirmDialog
            open={!!crud.deleteId}
            onOpenChange={(open) => !open && crud.cancelDelete()}
            title="Usuń grupę"
            description="Ta akcja nie może być cofnięta."
            message="Czy na pewno chcesz usunąć tę grupę?"
            confirmText="Usuń"
            cancelText="Anuluj"
            isDestructive
            isLoading={crud.isDeleting}
            onConfirm={crud.confirmDelete}
          />
        </>
      )}
    </div>
  )
}
