import { useQuery } from '@tanstack/react-query'
import { platformAuditService } from '@/services/platformAuditService'
import { queryKeys } from './queryKeys'

interface AuditParams {
  skip?: number
  limit?: number
}

export function usePlatformAudit(params?: AuditParams) {
  return useQuery({
    queryKey: queryKeys.platformAudit.list(params),
    queryFn: () => platformAuditService.list(params),
  })
}
