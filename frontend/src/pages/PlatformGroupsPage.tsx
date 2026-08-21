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
import { GroupsManagementView } from '@/components/groups/GroupsManagementView'
import { OrgSwitcherTabs } from '@/components/OrgSwitcherTabs'
import { PERMISSION_CATALOG } from '@/types/permissions'
import type { SecurityGroupCreateRequest, SecurityGroupSaveRequest } from '@/types/coreData'
import type { GroupFormData } from '@/components/dialogs/GroupFormDialog'

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

  const availableUsers = useMemo(
    () => users.map((u) => ({ id: u.id, label: `${u.first_name} ${u.last_name} (${u.email})` })),
    [users]
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
      user_ids: allGroups.find((g) => g.id === id)?.user_ids || [],
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
    <div className="px-6 py-8">
      <GroupsManagementView
        groups={filteredGroups}
        isLoading={isLoading}
        canManage={canManage}
        title="Grupy platformy"
        subtitle="Grupy uprawnień na platformie"
        availablePermissions={availablePermissions}
        availableUsers={availableUsers}
        onCreateGroup={handleCreateGroup}
        onUpdateGroup={handleUpdateGroup}
        onDeleteGroup={handleDeleteGroup}
        onReplaceGroupUsers={handleReplaceUsers}
        tabs={<OrgSwitcherTabs selectedOrgId={selectedOrgId} onSelectOrg={setSelectedOrgId} groupCounts={groupCounts} />}
      />
    </div>
  )
}
