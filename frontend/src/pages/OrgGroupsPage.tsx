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
import { GroupsManagementView } from '@/components/groups/GroupsManagementView'
import { PERMISSION_CATALOG } from '@/types/permissions'
import type { SecurityGroupCreateRequest, SecurityGroupSaveRequest } from '@/types/coreData'
import type { GroupFormData } from '@/components/dialogs/GroupFormDialog'

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

  const availableUsers = useMemo(
    () => members.map((m) => ({ id: m.id, label: `${m.first_name} ${m.last_name} (${m.email})` })),
    [members]
  )

  const handleCreateGroup = async (data: GroupFormData) => {
    const payload: SecurityGroupCreateRequest = {
      name: data.name,
      description: data.description,
      permission_codes: [],
    }
    return createMutation.mutateAsync(payload)
  }

  const handleUpdateGroup = async (
    id: string,
    data: { name: string; description?: string; permission_codes: string[] }
  ) => {
    const payload: SecurityGroupSaveRequest = {
      name: data.name,
      description: data.description ?? '',
      permission_codes: data.permission_codes,
      user_ids: groups.find((g) => g.id === id)?.user_ids || [],
    }
    await saveMutation.mutateAsync({ id, data: payload })
  }

  const handleDeleteGroup = async (id: string) => {
    await deleteMutation.mutateAsync(id)
  }

  const handleReplaceUsers = async (id: string, userIds: string[]) => {
    await replaceUsersMutation.mutateAsync({ id, userIds })
  }

  return (
    <GroupsManagementView
      groups={groups}
      isLoading={isLoading}
      canManage={canManage}
      title="Grupy organizacji"
      subtitle="Grupy uprawnień w organizacji"
      availablePermissions={availablePermissions}
      availableUsers={availableUsers}
      onCreateGroup={handleCreateGroup}
      onUpdateGroup={handleUpdateGroup}
      onDeleteGroup={handleDeleteGroup}
      onReplaceGroupUsers={handleReplaceUsers}
    />
  )
}
