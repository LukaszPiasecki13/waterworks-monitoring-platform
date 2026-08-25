import { useMemo } from 'react'
import { ChevronDown } from 'lucide-react'
import { useOrganizations } from '@/hooks/useOrganizations'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/DropdownMenu'

interface OrgSwitcherTabsProps {
  selectedOrgId: string | null
  onSelectOrg: (orgId: string | null) => void
  groupCounts: Record<string, number>
}

export function OrgSwitcherTabs({
  selectedOrgId,
  onSelectOrg,
  groupCounts,
}: OrgSwitcherTabsProps) {
  const { data: organizations = [] } = useOrganizations()

  const items = useMemo(
    () => [
      { id: null, name: 'Platforma', label: 'Platforma', count: groupCounts['platform'] || 0 },
      ...organizations.map((org) => ({
        id: org.id,
        name: org.name,
        label: org.name,
        count: groupCounts[org.id] || 0,
      })),
    ],
    [organizations, groupCounts]
  )

  const selectedItem = items.find((item) => item.id === selectedOrgId) || items[0]

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="w-full flex items-center justify-between px-3 py-2.5 text-sm font-medium text-neutral-900 hover:text-brand-700 transition-colors text-left">
          <span>Zakres: {selectedItem.label}</span>
          <ChevronDown className="h-4 w-4 text-neutral-500" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-48">
        {items.map((item) => (
          <DropdownMenuItem
            key={item.id || 'platform'}
            onClick={() => onSelectOrg(item.id)}
            className="flex items-center justify-between"
          >
            <span className={selectedItem.id === item.id ? 'font-semibold' : ''}>
              {item.label}
            </span>
            <span className="text-xs text-neutral-500 ml-2">{item.count} grup</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
