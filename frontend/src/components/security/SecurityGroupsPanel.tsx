import { useState, useMemo } from 'react'
import { useSecurityGroups } from '@/hooks/useSecurityGroups'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Plus, Trash2 } from 'lucide-react'
import type { ManagedUser } from '@/types/coreData'
import type { PermissionCode } from '@/types/permissions'
import { NewGroupDialog } from './NewGroupDialog'

interface Draft {
  name: string
  description: string
  permissionCodes: PermissionCode[]
  userIds: string[]
}

interface SecurityGroupsPanelProps {
  users: ManagedUser[]
  canManage: boolean
}

export function SecurityGroupsPanel({ users, canManage }: SecurityGroupsPanelProps) {
  const { permissions, groups, create, save, remove } = useSecurityGroups()
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null)
  const [drafts, setDrafts] = useState<Record<string, Draft>>({})
  const [isNewGroupDialogOpen, setIsNewGroupDialogOpen] = useState(false)
  const [deleteGroupId, setDeleteGroupId] = useState<string | null>(null)
  const [userSearch, setUserSearch] = useState('')

  const selectedGroup = groups.find((g) => g.id === selectedGroupId)

  const getDraft = (groupId: string): Draft => {
    if (!drafts[groupId] && selectedGroup) {
      return {
        name: selectedGroup.name,
        description: selectedGroup.description,
        permissionCodes: selectedGroup.permissions.map((p) => p.code as PermissionCode),
        userIds: selectedGroup.user_ids,
      }
    }
    return (
      drafts[groupId] || {
        name: '',
        description: '',
        permissionCodes: [],
        userIds: [],
      }
    )
  }

  const setDraft = (groupId: string, draft: Draft) => {
    setDrafts((prev) => ({ ...prev, [groupId]: draft }))
  }

  const permissionsByCategory = useMemo(() => {
    const map: Record<string, typeof permissions> = {}
    permissions.forEach((p) => {
      if (!map[p.category]) {
        map[p.category] = []
      }
      map[p.category].push(p)
    })
    return map
  }, [permissions])

  const filteredUsers = useMemo(
    () =>
      users.filter((u) =>
        `${u.first_name} ${u.last_name} ${u.email}`.toLowerCase().includes(userSearch.toLowerCase())
      ),
    [users, userSearch]
  )

  const handleCreateGroup = (name: string) => {
    create.mutate(
      {
        name,
        description: '',
        permission_codes: [],
      },
      {
        onSuccess: (newGroup) => {
          setSelectedGroupId(newGroup.id)
          setIsNewGroupDialogOpen(false)
        },
      }
    )
  }

  const handleSaveGroup = () => {
    if (!selectedGroupId) return
    const draft = getDraft(selectedGroupId)
    save.mutate(
      {
        id: selectedGroupId,
        data: {
          name: draft.name,
          description: draft.description,
          permission_codes: draft.permissionCodes,
          user_ids: draft.userIds,
        },
      },
      {
        onSuccess: () => {
          setDrafts((prev) => {
            const next = { ...prev }
            delete next[selectedGroupId]
            return next
          })
        },
      }
    )
  }

  const handleDeleteGroup = () => {
    if (!deleteGroupId) return
    remove.mutate(deleteGroupId, {
      onSuccess: () => {
        if (selectedGroupId === deleteGroupId) {
          setSelectedGroupId(null)
        }
        setDeleteGroupId(null)
      },
    })
  }

  const isSystemGroup = selectedGroup?.is_system
  const permissionsLocked = isSystemGroup && selectedGroup?.system_key !== 'staff'
  const draft = selectedGroup ? getDraft(selectedGroup.id) : null

  return (
    <div className="grid grid-cols-3 gap-6">
      <Card className="col-span-1">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Grupy użytkowników</CardTitle>
            {canManage && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsNewGroupDialogOpen(true)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-1">
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {groups.length === 0 ? (
              <div className="text-sm text-neutral-500 py-4">Brak grup</div>
            ) : (
              groups.map((group) => (
                <button
                  key={group.id}
                  onClick={() => setSelectedGroupId(group.id)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm flex items-center justify-between gap-2 transition-colors ${
                    selectedGroupId === group.id
                      ? 'bg-blue-50 text-blue-900'
                      : 'hover:bg-neutral-100 text-neutral-900'
                  }`}
                >
                  <span className="truncate font-medium">{group.name}</span>
                  {group.is_system && (
                    <Badge variant="info" className="flex-shrink-0">
                      Systemowa
                    </Badge>
                  )}
                </button>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>
            {selectedGroup ? `${selectedGroup.name}` : 'Wybierz grupę'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {selectedGroup && draft ? (
            <>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-neutral-900">Nazwa</label>
                <Input
                  value={draft.name}
                  onChange={(e) =>
                    setDraft(selectedGroup.id, { ...draft, name: e.target.value })
                  }
                  disabled={isSystemGroup || !canManage}
                  placeholder="Nazwa grupy"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-neutral-900">Opis</label>
                <Textarea
                  value={draft.description}
                  onChange={(e) =>
                    setDraft(selectedGroup.id, { ...draft, description: e.target.value })
                  }
                  disabled={isSystemGroup || !canManage}
                  placeholder="Opis grupy"
                  rows={3}
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="block text-sm font-medium text-neutral-900">Uprawnienia</label>
                  {permissionsLocked && (
                    <span className="text-xs text-neutral-500">
                      {isSystemGroup ? '(Grupa systemowa - chroniona)' : ''}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 p-3 bg-neutral-50 rounded-lg">
                  {Object.entries(permissionsByCategory).map(([category, perms]) => (
                    <div key={category} className="space-y-2">
                      <div className="text-xs font-semibold text-neutral-600 uppercase">
                        {category}
                      </div>
                      <div className="space-y-1">
                        {perms.map((p) => (
                          <label
                            key={p.id}
                            className="flex items-center gap-2 cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={draft.permissionCodes.includes(p.code as PermissionCode)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setDraft(selectedGroup.id, {
                                    ...draft,
                                    permissionCodes: [
                                      ...draft.permissionCodes,
                                      p.code as PermissionCode,
                                    ],
                                  })
                                } else {
                                  setDraft(selectedGroup.id, {
                                    ...draft,
                                    permissionCodes: draft.permissionCodes.filter(
                                      (c) => c !== p.code
                                    ),
                                  })
                                }
                              }}
                              disabled={permissionsLocked || !canManage}
                              className="w-4 h-4"
                            />
                            <span className="text-sm text-neutral-700">{p.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-neutral-900 mb-2">
                    Użytkownicy w grupie
                  </label>
                  <Input
                    placeholder="Szukaj użytkownika..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    disabled={!canManage}
                    className="mb-3"
                  />
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto p-3 bg-neutral-50 rounded-lg">
                  {filteredUsers.length === 0 ? (
                    <div className="text-sm text-neutral-500">Brak użytkowników</div>
                  ) : (
                    filteredUsers.map((user) => (
                      <label key={user.id} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={draft.userIds.includes(String(user.id))}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setDraft(selectedGroup.id, {
                                ...draft,
                                userIds: [...draft.userIds, String(user.id)],
                              })
                            } else {
                              setDraft(selectedGroup.id, {
                                ...draft,
                                userIds: draft.userIds.filter((id) => id !== String(user.id)),
                              })
                            }
                          }}
                          disabled={!canManage}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-neutral-700">
                          {user.first_name} {user.last_name}
                        </span>
                        <span className="text-xs text-neutral-500">({user.email})</span>
                      </label>
                    ))
                  )}
                </div>
              </div>

              {canManage && (
                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    onClick={handleSaveGroup}
                    disabled={save.isPending}
                    className="flex-1"
                  >
                    {save.isPending ? 'Zapisywanie...' : 'Zapisz zmiany'}
                  </Button>
                  {!isSystemGroup && (
                    <Button
                      variant="destructive"
                      onClick={() => setDeleteGroupId(selectedGroup.id)}
                      disabled={remove.isPending}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-neutral-500 text-sm py-8 text-center">
              Wybierz grupę, aby edytować
            </div>
          )}
        </CardContent>
      </Card>

      <NewGroupDialog
        open={isNewGroupDialogOpen}
        onOpenChange={setIsNewGroupDialogOpen}
        onSubmit={handleCreateGroup}
        isLoading={create.isPending}
      />

      <ConfirmDialog
        open={!!deleteGroupId}
        onOpenChange={(open) => !open && setDeleteGroupId(null)}
        title="Usuń grupę"
        description="Ta akcja nie może być cofnięta."
        message={`Czy na pewno chcesz usunąć grupę "${
          groups.find((g) => g.id === deleteGroupId)?.name
        }"?`}
        confirmText="Usuń"
        cancelText="Anuluj"
        isDestructive
        isLoading={remove.isPending}
        onConfirm={handleDeleteGroup}
      />
    </div>
  )
}
