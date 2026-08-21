import { useMemo, useState } from 'react'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/Popover'
import { Input } from '@/components/ui/Input'
import type { SecurityGroupSummary } from '@/types/coreData'

interface SelectableUser {
  id: string
  label: string
}

interface GroupMembersTabProps {
  group: SecurityGroupSummary
  availableUsers: SelectableUser[]
  onReplaceUsers: (userIds: string[]) => void
  isLoading?: boolean
}

function getInitials(label: string): string {
  const parts = label.split(/[\s(]+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return (label[0] || '?').toUpperCase()
}

function getUserNameAndEmail(label: string): { name: string; email?: string } {
  const match = label.match(/^(.+?)\s*\((.+?)\)$/)
  if (match) {
    return { name: match[1].trim(), email: match[2].trim() }
  }
  return { name: label }
}

export function GroupMembersTab({
  group,
  availableUsers,
  onReplaceUsers,
  isLoading = false,
}: GroupMembersTabProps) {
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const currentUserIds = useMemo(() => new Set(group.user_ids), [group.user_ids])

  const currentMembers = useMemo(
    () =>
      availableUsers.filter((u) => currentUserIds.has(u.id)),
    [availableUsers, currentUserIds]
  )

  const availableToAdd = useMemo(
    () =>
      availableUsers.filter(
        (u) => !currentUserIds.has(u.id) && u.label.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    [availableUsers, currentUserIds, searchQuery]
  )

  const handleRemoveUser = (userId: string) => {
    const newUserIds = group.user_ids.filter((id) => id !== userId)
    onReplaceUsers(newUserIds)
  }

  const handleAddUser = (userId: string) => {
    const newUserIds = [...group.user_ids, userId]
    onReplaceUsers(newUserIds)
    setSearchQuery('')
  }

  return (
    <div className="rounded-lg border border-neutral-200 flex flex-col flex-1 min-h-0 px-6 py-4">
      {currentMembers.length === 0 ? (
        <div className="p-8 text-center flex-1 flex flex-col items-center justify-center">
          <p className="text-sm text-neutral-500 mb-4">Brak członków w tej grupie</p>
          <Popover open={isAddOpen} onOpenChange={setIsAddOpen}>
            <PopoverTrigger asChild>
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                + Dodaj członka
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-72" align="start">
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium mb-2">Wybierz członka</p>
                  <Input
                    placeholder="Szukaj…"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="text-sm"
                  />
                </div>
                <div className="max-h-64 overflow-y-auto scrollbar-hide space-y-1">
                  {availableToAdd.length === 0 && (
                    <p className="text-sm text-neutral-500 py-2">Brak dostępnych użytkowników</p>
                  )}
                  {availableToAdd.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => {
                        handleAddUser(user.id)
                        if (availableToAdd.length === 1) {
                          setIsAddOpen(false)
                        }
                      }}
                      className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-neutral-100 transition-colors"
                    >
                      {user.label}
                    </button>
                  ))}
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto scrollbar-hide divide-y divide-neutral-200">
            {currentMembers.map((member) => {
              const { name, email } = getUserNameAndEmail(member.label)
              return (
                <div key={member.id} className="flex items-center gap-3 p-4 hover:bg-neutral-50">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-900 flex-shrink-0">
                    {getInitials(member.label)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{name}</p>
                    {email && (
                      <p className="text-xs text-neutral-500 truncate">{email}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveUser(member.id)}
                    disabled={isLoading}
                    className="text-neutral-500 hover:text-neutral-700 text-lg leading-none disabled:opacity-50"
                  >
                    ×
                  </button>
                </div>
              )
            })}
          </div>
          <div className="border-t border-neutral-200 bg-neutral-50 p-4">
            <Popover open={isAddOpen} onOpenChange={setIsAddOpen}>
              <PopoverTrigger asChild>
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                  + Dodaj członka
                </button>
              </PopoverTrigger>
              <PopoverContent className="w-72" align="start">
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium mb-2">Wybierz członka</p>
                    <Input
                      placeholder="Szukaj…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="text-sm"
                    />
                  </div>
                  <div className="max-h-64 overflow-y-auto scrollbar-hide space-y-1">
                    {availableToAdd.length === 0 && (
                      <p className="text-sm text-neutral-500 py-2">Wszyscy użytkownicy już należą do tej grupy</p>
                    )}
                    {availableToAdd.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => {
                          handleAddUser(user.id)
                          if (availableToAdd.length === 1) {
                            setIsAddOpen(false)
                          }
                        }}
                        className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-neutral-100 transition-colors"
                      >
                        {user.label}
                      </button>
                    ))}
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </>
      )}
    </div>
  )
}
