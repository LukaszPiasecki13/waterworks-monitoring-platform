import { useMemo, useState } from 'react'
import { cn } from '@/lib/cn'
import { Input } from '@/components/ui/Input'
import type { SecurityGroupSummary } from '@/types/coreData'

interface GroupSidebarListProps {
  groups: SecurityGroupSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function GroupSidebarList({ groups, selectedId, onSelect }: GroupSidebarListProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const { systemGroups, ownGroups } = useMemo(() => {
    const filtered = groups.filter((g) =>
      g.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    return {
      systemGroups: filtered.filter((g) => g.is_system),
      ownGroups: filtered.filter((g) => !g.is_system),
    }
  }, [groups, searchQuery])

  return (
    <div className="flex flex-col h-full bg-neutral-50 border-r border-neutral-200">
      <div className="p-3">
        <Input
          placeholder="Szukaj grupy…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="text-sm"
        />
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {systemGroups.length > 0 && (
          <div>
            <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Systemowe
            </div>
            <div className="space-y-1 px-2">
              {systemGroups.map((group) => (
                <button
                  key={group.id}
                  onClick={() => onSelect(group.id)}
                  className={cn(
                    'w-full flex items-center justify-between rounded-md px-3 py-2 text-sm text-left transition-colors',
                    selectedId === group.id
                      ? 'bg-blue-100 text-blue-900 font-medium'
                      : 'text-neutral-900 hover:bg-neutral-100'
                  )}
                >
                  <span>{group.name}</span>
                  <span className={cn(
                    'text-xs',
                    selectedId === group.id ? 'text-blue-700' : 'text-neutral-500'
                  )}>
                    {group.user_ids.length}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {ownGroups.length > 0 && (
          <div className="mt-4">
            <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Własne
            </div>
            <div className="space-y-1 px-2">
              {ownGroups.map((group) => (
                <button
                  key={group.id}
                  onClick={() => onSelect(group.id)}
                  className={cn(
                    'w-full flex items-center justify-between rounded-md px-3 py-2 text-sm text-left transition-colors',
                    selectedId === group.id
                      ? 'bg-blue-100 text-blue-900 font-medium'
                      : 'text-neutral-900 hover:bg-neutral-100'
                  )}
                >
                  <span>{group.name}</span>
                  <span className={cn(
                    'text-xs',
                    selectedId === group.id ? 'text-blue-700' : 'text-neutral-500'
                  )}>
                    {group.user_ids.length}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {systemGroups.length === 0 && ownGroups.length === 0 && (
          <div className="p-4 text-center text-sm text-neutral-500">
            Brak grup spełniających kryterium
          </div>
        )}
      </div>
    </div>
  )
}
