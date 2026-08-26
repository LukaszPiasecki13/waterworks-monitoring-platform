export function useGridLayout(orgId: string | null) {
  const getPinnedIds = (): string[] => {
    if (!orgId) return []
    try {
      const stored = localStorage.getItem(`objects-grid-pinned-${orgId}`)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  const getOrder = (): string[] => {
    if (!orgId) return []
    try {
      const stored = localStorage.getItem(`objects-grid-order-${orgId}`)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  const setPinned = (ids: string[]): void => {
    if (!orgId) return
    try {
      localStorage.setItem(`objects-grid-pinned-${orgId}`, JSON.stringify(ids))
    } catch (e) {
      console.error('[useGridLayout] Failed to persist pinned IDs', e)
    }
  }

  const setOrder = (ids: string[]): void => {
    if (!orgId) return
    try {
      localStorage.setItem(`objects-grid-order-${orgId}`, JSON.stringify(ids))
    } catch (e) {
      console.error('[useGridLayout] Failed to persist order', e)
    }
  }

  return { getPinnedIds, getOrder, setPinned, setOrder }
}
