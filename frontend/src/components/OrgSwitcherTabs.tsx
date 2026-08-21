import { useMemo } from 'react'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { useOrganizations } from '@/hooks/useOrganizations'
import { Badge } from '@/components/ui/Badge'

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

  const tabs = useMemo(
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

  const activeTab = selectedOrgId === null ? 'platform' : selectedOrgId

  return (
    <Tabs value={activeTab} onValueChange={(val) => onSelectOrg(val === 'platform' ? null : val)}>
      <TabsList>
        {tabs.map((tab) => (
          <TabsTrigger key={tab.id || 'platform'} value={tab.id || 'platform'}>
            <span>{tab.label}</span>
            {tab.count > 0 && <Badge variant="info" className="ml-2">{tab.count}</Badge>}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  )
}
