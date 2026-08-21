import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/DropdownMenu'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { GroupMembersTab } from './GroupMembersTab'
import { GroupPermissionsTab } from './GroupPermissionsTab'
import type { SecurityGroupSummary, SecurityPermission } from '@/types/coreData'

interface SelectableUser {
  id: string
  label: string
}

interface GroupDetailPanelProps {
  group: SecurityGroupSummary | null
  availablePermissions: SecurityPermission[]
  availableUsers: SelectableUser[]
  canManage: boolean
  onEdit: () => void
  onDelete: () => void
  onSavePermissions: (permissionCodes: string[]) => Promise<void>
  onReplaceUsers: (userIds: string[]) => Promise<void>
  isSaving?: boolean
}

export function GroupDetailPanel({
  group,
  availablePermissions,
  availableUsers,
  canManage,
  onEdit,
  onDelete,
  onSavePermissions,
  onReplaceUsers,
  isSaving = false,
}: GroupDetailPanelProps) {
  const [activeTab, setActiveTab] = useState('members')

  if (!group) {
    return (
      <div className="flex-1 flex items-center justify-center text-neutral-500">
        Wybierz grupę, aby wyświetlić szczegóły
      </div>
    )
  }

  const memberCount = group.user_ids.length

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-neutral-200 px-6 py-4">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-xl font-bold text-neutral-900 truncate">{group.name}</h2>
              {group.is_system && (
                <Badge className="bg-amber-100 text-amber-900 text-xs">systemowa</Badge>
              )}
            </div>
            {group.description && (
              <p className="text-sm text-neutral-600 line-clamp-2">{group.description}</p>
            )}
          </div>
          {canManage && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="px-3 py-2 rounded-md border border-neutral-200 hover:bg-neutral-50 text-neutral-600 font-mono text-lg leading-none">
                  ⋮
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-44">
                <DropdownMenuItem onClick={onEdit}>
                  ✎ Edytuj nazwę i opis
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={onDelete}
                  disabled={group.is_system}
                  className={group.is_system ? 'opacity-50 cursor-not-allowed' : ''}
                >
                  <span className="text-red-600">🗑 Usuń grupę</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="border-b border-neutral-200 px-6">
          <TabsList className="rounded-none border-0 bg-transparent p-0 h-auto">
            <TabsTrigger
              value="members"
              className="rounded-none border-b-2 border-transparent px-0 py-3 text-sm font-medium text-neutral-600 data-[state=active]:border-blue-500 data-[state=active]:text-neutral-900 data-[state=active]:bg-transparent data-[state=active]:shadow-none mr-6"
            >
              Członkowie · {memberCount}
            </TabsTrigger>
            <TabsTrigger
              value="permissions"
              className="rounded-none border-b-2 border-transparent px-0 py-3 text-sm font-medium text-neutral-600 data-[state=active]:border-blue-500 data-[state=active]:text-neutral-900 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
            >
              Uprawnienia · {group.permissions.length}
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Members Tab */}
        <TabsContent
          value="members"
          className="flex-1 flex flex-col overflow-hidden m-0"
        >
          <GroupMembersTab
            group={group}
            availableUsers={availableUsers}
            onReplaceUsers={onReplaceUsers}
            isLoading={isSaving}
          />
        </TabsContent>

        {/* Permissions Tab */}
        <TabsContent
          value="permissions"
          className="flex-1 flex flex-col overflow-hidden m-0"
        >
          <GroupPermissionsTab
            group={group}
            availablePermissions={availablePermissions}
            onSave={onSavePermissions}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
