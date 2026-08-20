import { useMemo } from 'react'
import { usePlatformAudit } from '@/hooks/usePlatformAudit'
import { useOrganizations } from '@/hooks/useOrganizations'
import { Card, CardContent } from '@/components/ui/Card'
import { DataTable } from '@/components/ui/DataTable'
import type { AuditEvent } from '@/types/coreData'

export function PlatformAuditPage() {
  const { data: auditEvents = [], isLoading: isLoadingAudit } = usePlatformAudit()
  const { data: organizations = [], isLoading: isLoadingOrgs } = useOrganizations()

  const orgNameMap = useMemo(() => {
    const map = new Map<string, string>()
    organizations.forEach((org) => {
      map.set(org.id, org.name)
    })
    return map
  }, [organizations])

  const columns = [
    {
      key: 'created_at',
      label: 'Data',
      render: (row: AuditEvent) => {
        const date = new Date(row.created_at)
        return date.toLocaleString('pl-PL')
      },
    },
    {
      key: 'actor_id',
      label: 'Aktor',
      render: (row: AuditEvent) => row.actor_id.substring(0, 8) + '...',
    },
    {
      key: 'action',
      label: 'Akcja',
      render: (row: AuditEvent) => row.action,
    },
    {
      key: 'context',
      label: 'Kontekst',
      render: (row: AuditEvent) => {
        if (row.context_type === 'organization' && row.context_id) {
          const orgName = orgNameMap.get(row.context_id)
          if (orgName) {
            return orgName
          }
          return `Gmina usunięta (ID: ${row.context_id.substring(0, 8)}...)`
        }
        return 'Platforma'
      },
    },
  ]

  return (
    <div className="px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-900">Audyt platformy</h1>
        <p className="text-neutral-600 mt-2">Dziennik zdarzeń i zmian na platformie</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={auditEvents}
            isLoading={isLoadingAudit || isLoadingOrgs}
          />
        </CardContent>
      </Card>
    </div>
  )
}
