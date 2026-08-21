import { useState } from 'react'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { useCrudPageState } from '@/hooks/useCrudPageState'
import { useOrganizations, useCreateOrganization, useUpdateOrganization, useDeleteOrganization } from '@/hooks/useOrganizations'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Plus, Pencil, Trash2, Users, Building } from 'lucide-react'
import type { Organization } from '@/types/coreData'
import { OrganizationFormDialog, type OrganizationFormData } from '@/components/dialogs/OrganizationFormDialog'
import { ManageOrganizationMembersDialog } from '@/components/dialogs/ManageOrganizationMembersDialog'

export function PlatformOrganizationsPage() {
  const { data: organizations = [], isLoading } = useOrganizations()
  const createMutation = useCreateOrganization()
  const updateMutation = useUpdateOrganization()
  const deleteMutation = useDeleteOrganization()
  const { hasPermission } = useActivePermissions()
  const [managingMembersOrgId, setManagingMembersOrgId] = useState<string | null>(null)
  const managingMembersOrg = organizations.find((o) => o.id === managingMembersOrgId)

  const canManage = hasPermission('PLATFORM_MANAGE_ORGANIZATIONS')
  const canManageUsers = hasPermission('PLATFORM_MANAGE_MEMBERSHIPS')

  const crud = useCrudPageState<string, OrganizationFormData>({
    createMutation,
    updateMutation,
    deleteMutation,
    messages: {
      createSuccess: 'Organizacja utworzona',
      updateSuccess: 'Organizacja zaktualizowana',
      deleteSuccess: 'Organizacja usunięta',
      createErrorFallback: 'Błąd przy tworzeniu',
      updateErrorFallback: 'Błąd przy aktualizacji',
      deleteErrorFallback: 'Błąd przy usuwaniu',
    },
  })

  const columns = [
    {
      key: 'name',
      label: 'Nazwa',
      render: (row: Organization) => row.name,
    },
    ...(canManage || canManageUsers
      ? [
          {
            key: 'actions',
            label: 'Akcje',
            render: (row: Organization) => (
              <div className="flex gap-2">
                {canManageUsers && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setManagingMembersOrgId(row.id)}
                    aria-label={`Zarządzaj członkami organizacji ${row.name}`}
                  >
                    <Users className="h-4 w-4" />
                  </Button>
                )}
                {canManage && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => crud.openEdit(row.id)}
                      aria-label={`Edytuj organizację ${row.name}`}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => crud.requestDelete(row.id)}
                      aria-label={`Usuń organizację ${row.name}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </>
                )}
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
          <h1 className="text-3xl font-bold text-neutral-900">Organizacje</h1>
          <p className="text-neutral-600">Zarządzanie organizacjami platformy</p>
        </div>
        {canManage && (
          <Button onClick={crud.openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Nowa organizacja
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={organizations}
            isLoading={isLoading}
            emptyState={canManage ? {
              icon: <Building className="h-12 w-12" />,
              title: 'Brak organizacji',
              subtitle: 'Utwórz pierwszą organizację na platformie',
              ctaLabel: 'Dodaj organizację',
              onCta: () => crud.openCreate(),
            } : undefined}
          />
        </CardContent>
      </Card>

      {canManage && (
        <>
          <OrganizationFormDialog
            open={crud.isFormOpen}
            onOpenChange={crud.setIsFormOpen}
            organizationId={crud.editingId}
            onSubmit={crud.handleSubmit}
            isLoading={crud.isSubmitting}
            serverFieldErrors={crud.serverFieldErrors}
          />

          <ConfirmDialog
            open={!!crud.deleteId}
            onOpenChange={(open) => !open && crud.cancelDelete()}
            title="Usuń organizację"
            description="Ta akcja nie może być cofnięta."
            message="Czy na pewno chcesz usunąć tę organizację?"
            confirmText="Usuń"
            cancelText="Anuluj"
            isDestructive
            isLoading={crud.isDeleting}
            onConfirm={crud.confirmDelete}
          />
        </>
      )}

      {canManageUsers && (
        <ManageOrganizationMembersDialog
          orgId={managingMembersOrgId}
          orgName={managingMembersOrg?.name}
          open={!!managingMembersOrgId}
          onOpenChange={(open) => !open && setManagingMembersOrgId(null)}
        />
      )}
    </div>
  )
}
