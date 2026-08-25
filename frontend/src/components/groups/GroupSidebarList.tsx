import { useMemo } from 'react'
import { Plus } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { SecurityGroupSummary } from '@/types/coreData'

interface GroupSidebarListProps {
  groups: SecurityGroupSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
  tabs?: React.ReactNode
  canManage?: boolean
  onCreateGroup?: () => void
}

export function GroupSidebarList({
  groups,
  selectedId,
  onSelect,
  tabs,
  canManage = false,
  onCreateGroup,
}: GroupSidebarListProps) {
  const { systemGroups, ownGroups } = useMemo(() => {
    return {
      systemGroups: groups.filter((g) => g.is_system),
      ownGroups: groups.filter((g) => !g.is_system),
    }
  }, [groups])

  return (
    <div className="flex flex-col h-full bg-neutral-50 border-r border-neutral-200">
      {tabs && <div className="border-b border-neutral-200">{tabs}</div>}

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
                      ? 'bg-brand-50 text-brand-700 font-medium'
                      : 'text-neutral-900 hover:bg-neutral-100'
                  )}
                >
                  <span>{group.name}</span>
                  <span className={cn(
                    'text-xs',
                    selectedId === group.id ? 'text-brand-700' : 'text-neutral-500'
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
                      ? 'bg-brand-50 text-brand-700 font-medium'
                      : 'text-neutral-900 hover:bg-neutral-100'
                  )}
                >
                  <span>{group.name}</span>
                  <span className={cn(
                    'text-xs',
                    selectedId === group.id ? 'text-brand-700' : 'text-neutral-500'
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
            Brak grup
          </div>
        )}
      </div>

      {canManage && onCreateGroup && (
        <div className="border-t border-neutral-200 p-2">
          <button
            onClick={onCreateGroup}
            className="w-full flex items-center gap-1.5 px-3 py-2 text-sm text-brand-600 hover:text-brand-700 hover:bg-neutral-100 rounded-md font-medium transition-colors"
          >
            <Plus className="h-4 w-4" />
            Nowa grupa
          </button>
        </div>
      )}
    </div>
  )
}
