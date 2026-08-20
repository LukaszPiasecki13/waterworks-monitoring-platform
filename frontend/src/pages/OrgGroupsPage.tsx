import { useOrgGroups } from '@/hooks/useOrgGroups'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import type { SecurityGroupSummary } from '@/types/coreData'

export function OrgGroupsPage() {
  const { data: groups = [], isLoading } = useOrgGroups()

  const columns = [
    {
      key: 'name',
      label: 'Nazwa grupy',
      render: (row: SecurityGroupSummary) => row.name,
    },
    {
      key: 'permissions_count',
      label: 'Uprawnienia',
      render: (row: SecurityGroupSummary) => row.permissions?.length || 0,
    },
    {
      key: 'description',
      label: 'Opis',
      render: (row: SecurityGroupSummary) => row.description || '—',
    },
  ]

  return (
    <div className="px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-900">Grupy organizacji</h1>
        <p className="text-neutral-600 mt-2">Grupy uprawnień w organizacji (widok tylko do odczytu)</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={groups} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  )
}
