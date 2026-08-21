import { useMemo, useState } from 'react'
import {
  usePlatformGroups,
  useCreatePlatformGroup,
  useSavePlatformGroup,
  useReplacePlatformGroupUsers,
  useDeletePlatformGroup,
} from '@/hooks/usePlatformGroups'
import { useUsers } from '@/hooks/useUsers'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Plus, Pencil, Trash2, Shield } from 'lucide-react'
import { GroupFormDialog, type GroupFormData, type SelectableUser } from '@/components/dialogs/GroupFormDialog'
import { OrgSwitcherTabs } from '@/components/OrgSwitcherTabs'
import { PERMISSION_CATALOG } from '@/types/permissions'
import type { SecurityGroupSummary, SecurityGroupSaveRequest } from '@/types/coreData'

export function PlatformGroupsPage() {
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null)
  const { data: allGroups = [], isLoading } = usePlatformGroups()
  const { data: users = [] } = useUsers()
  const createMutation = useCreatePlatformGroup()
  const saveMutation = useSavePlatformGroup()
  const replaceUsersMutation = useReplacePlatformGroupUsers()
  const deleteMutation = useDeletePlatformGroup()
  const { hasPermission } = useActivePermissions()

  const canManage = hasPermission('PLATFORM_MANAGE_ORGANIZATIONS')

  const filteredGroups = useMemo(
    () =>
      allGroups.filter((g) =>
        selectedOrgId === null ? g.organization_id === null : g.organization_id === selectedOrgId
      ),
    [allGroups, selectedOrgId]
  )

  const groupCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    counts['platform'] = allGroups.filter((g) => g.organization_id === null).length
    allGroups.forEach((g) => {
      if (g.organization_id) {
        counts[g.organization_id] = (counts[g.organization_id] || 0) + 1
      }
    })
    return counts
  }, [allGroups])

  const availablePermissions = useMemo(
    () =>
      PERMISSION_CATALOG.filter((p) => p.plane === 'platform').map((p) => ({
        id: p.code,
        code: p.code,
        name: p.name,
        category: p.category,
      })),
    []
  )

  const availableUsers: SelectableUser[] = useMemo(
    () => users.map((u) => ({ id: u.id, label: `${u.first_name} ${u.last_name} (${u.email})` })),
    [users]
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

  const currentGroup = allGroups.find((g: SecurityGroupSummary) => g.id === crud.editingId) ?? null

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

  const orgTitle = selectedOrgId === null ? 'Grupy platformy' : 'Grupy organizacji'
  const orgSubtitle =
    selectedOrgId === null ? 'Grupy uprawnień na platformie' : 'Grupy uprawnień w organizacji'

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">{orgTitle}</h1>
          <p className="text-neutral-600">{orgSubtitle}</p>
        </div>
        {canManage && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Nowa grupa
          </Button>
        )}
      </div>

      <div className="mb-6">
        <OrgSwitcherTabs selectedOrgId={selectedOrgId} onSelectOrg={setSelectedOrgId} groupCounts={groupCounts} />
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={filteredGroups}
            isLoading={isLoading}
            emptyState={canManage ? {
              icon: <Shield className="h-12 w-12" />,
              title: selectedOrgId === null ? 'Brak grup platformy' : 'Brak grup w organizacji',
              subtitle: selectedOrgId === null ? 'Utwórz grupy uprawnień dla administratorów' : 'Utwórz grupy uprawnień dla członków',
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
