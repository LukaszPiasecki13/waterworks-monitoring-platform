import { useEffect, useMemo, useState } from 'react'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { GroupFormDialog, type GroupFormData } from '@/components/dialogs/GroupFormDialog'
import { GroupSidebarList } from './GroupSidebarList'
import { GroupDetailPanel } from './GroupDetailPanel'
import type { SecurityGroupSummary, SecurityPermission } from '@/types/coreData'

interface SelectableUser {
  id: string
  label: string
}

interface GroupsManagementViewProps {
  groups: SecurityGroupSummary[]
  isLoading: boolean
  canManage: boolean
  title?: string
  subtitle?: string
  availablePermissions: SecurityPermission[]
  availableUsers: SelectableUser[]
  onCreateGroup: (data: GroupFormData) => Promise<SecurityGroupSummary>
  onUpdateGroup: (id: string, data: { name: string; description?: string; permission_codes: string[] }) => Promise<void>
  onDeleteGroup: (id: string) => Promise<void>
  onReplaceGroupUsers: (id: string, userIds: string[]) => Promise<void>
  tabs?: React.ReactNode
}

export function GroupsManagementView({
  groups,
  isLoading,
  canManage,
  title,
  subtitle,
  availablePermissions,
  availableUsers,
  onCreateGroup,
  onUpdateGroup,
  onDeleteGroup,
  onReplaceGroupUsers,
  tabs,
}: GroupsManagementViewProps) {
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingGroupId, setEditingGroupId] = useState<string | null>(null)
  const [deleteGroupId, setDeleteGroupId] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const selectedGroup = useMemo(
    () => groups.find((g) => g.id === selectedGroupId) ?? null,
    [groups, selectedGroupId]
  )

  // Auto-select first group when groups load
  useEffect(() => {
    if (!selectedGroupId && groups.length > 0) {
      setSelectedGroupId(groups[0].id)
    }
  }, [groups, selectedGroupId])

  const handleOpenCreate = () => {
    setEditingGroupId(null)
    setIsFormOpen(true)
  }

  const handleOpenEdit = () => {
    if (selectedGroup) {
      setEditingGroupId(selectedGroup.id)
      setIsFormOpen(true)
    }
  }

  const handleFormSubmit = async (data: GroupFormData) => {
    try {
      setIsSaving(true)
      if (editingGroupId) {
        await onUpdateGroup(editingGroupId, {
          name: data.name,
          description: data.description,
          permission_codes: selectedGroup?.permissions.map((p) => p.code) || [],
        })
      } else {
        const createdGroup = await onCreateGroup({
          ...data,
          permission_codes: [],
          user_ids: [],
        })
        setSelectedGroupId(createdGroup.id)
      }
      setIsFormOpen(false)
    } finally {
      setIsSaving(false)
    }
  }

  const handleSavePermissions = async (permissionCodes: string[]) => {
    if (!selectedGroup) return
    try {
      setIsSaving(true)
      await onUpdateGroup(selectedGroup.id, {
        name: selectedGroup.name,
        description: selectedGroup.description ?? '',
        permission_codes: permissionCodes,
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleReplaceUsers = async (userIds: string[]) => {
    if (!selectedGroup) return
    try {
      setIsSaving(true)
      await onReplaceGroupUsers(selectedGroup.id, userIds)
    } finally {
      setIsSaving(false)
    }
  }

  const handleRequestDelete = () => {
    if (selectedGroup && !selectedGroup.is_system) {
      setDeleteGroupId(selectedGroup.id)
    }
  }

  const handleConfirmDelete = async () => {
    if (!deleteGroupId) return
    try {
      setIsSaving(true)
      await onDeleteGroup(deleteGroupId)
      setDeleteGroupId(null)
      if (selectedGroupId === deleteGroupId) {
        setSelectedGroupId(null)
      }
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin h-8 w-8 border-2 border-brand-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <>
      {title && (
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-neutral-900">{title}</h1>
          {subtitle && <p className="text-neutral-600 mt-1">{subtitle}</p>}
        </div>
      )}
      <Card className="overflow-hidden p-0">
        <div className="flex gap-0">
        <div className="w-64 border-r border-neutral-200 flex flex-col">
          <GroupSidebarList
            groups={groups}
            selectedId={selectedGroupId}
            onSelect={setSelectedGroupId}
            tabs={tabs}
            canManage={canManage}
            onCreateGroup={handleOpenCreate}
          />
          </div>

          <GroupDetailPanel
            group={selectedGroup}
            availablePermissions={availablePermissions}
            availableUsers={availableUsers}
            canManage={canManage}
            onEdit={handleOpenEdit}
            onDelete={handleRequestDelete}
            onSavePermissions={handleSavePermissions}
            onReplaceUsers={handleReplaceUsers}
            isSaving={isSaving}
          />
        </div>
      </Card>

      {canManage && (
        <>
          <GroupFormDialog
            open={isFormOpen}
            onOpenChange={setIsFormOpen}
            group={editingGroupId ? selectedGroup : null}
            availablePermissions={[]}
            availableUsers={[]}
            onSubmit={handleFormSubmit}
            isLoading={isSaving}
          />

          <ConfirmDialog
            open={!!deleteGroupId}
            onOpenChange={(open) => !open && setDeleteGroupId(null)}
            title="Usuń grupę"
            description="Ta akcja nie może być cofnięta."
            message={
              selectedGroup
                ? `Czy na pewno chcesz usunąć grupę "${selectedGroup.name}" (${selectedGroup.user_ids.length} członków)?`
                : 'Czy na pewno chcesz usunąć tę grupę?'
            }
            confirmText="Usuń"
            cancelText="Anuluj"
            isDestructive
            isLoading={isSaving}
            onConfirm={handleConfirmDelete}
          />
        </>
      )}
    </>
  )
}
