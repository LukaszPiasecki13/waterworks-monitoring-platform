import { useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'
import { queryKeys } from './queryKeys'

export function useUserContext() {
  const setUserContext = useAuthStore((s) => s.setUserContext)

  const query = useQuery({
    queryKey: queryKeys.auth.userContext(),
    queryFn: () => authService.getMyContext(),
  })

  // Sync to auth store when context is fetched
  useEffect(() => {
    if (query.data) {
      setUserContext(query.data)
    }
  }, [query.data, setUserContext])

  return query
}

export function useRefreshUserContext() {
  const queryClient = useQueryClient()
  return async () => {
    await queryClient.invalidateQueries({ queryKey: queryKeys.auth.userContext() })
    return queryClient.refetchQueries({ queryKey: queryKeys.auth.userContext() })
  }
}
