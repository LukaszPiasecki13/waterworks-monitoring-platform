import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useActiveOrganizationStore } from '@/stores/activeOrganizationStore'
import { useOrganizations } from '@/hooks/useOrganizations'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover'
import { ChevronDown, Check } from 'lucide-react'

export function OrganizationSwitcher() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const activeOrgId = useActiveOrganizationStore((state) => state.activeOrganizationId)
  const activeOrgName = useActiveOrganizationStore((state) => state.activeOrganizationName)
  const setActiveOrganization = useActiveOrganizationStore((state) => state.setActiveOrganization)

  const isPlatformAdmin = user?.organization_id === null

  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  // Fetch organizations
  const { data: organizations = [] } = useOrganizations(
    debouncedSearch ? { name: debouncedSearch, limit: 20 } : { limit: 20 },
    { enabled: isPlatformAdmin && open }
  )

  if (!user) {
    return null
  }

  if (!isPlatformAdmin) {
    // Regular user: show static badge
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-neutral-100">
        <div className="text-base font-medium text-neutral-900">{activeOrgName || 'Organization'}</div>
      </div>
    )
  }

  // Platform admin: show dropdown
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="gap-2 w-auto h-11 text-base px-4">
          <span className="truncate max-w-md">{activeOrgName || 'Select Organization'}</span>
          <ChevronDown className="h-4 w-4 flex-shrink-0" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-0" align="start">
        <div className="space-y-2 p-2">
          <div className="px-2">
            <Input
              placeholder="Szukaj organizacji..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-10 text-base"
              autoFocus
            />
          </div>

          <div className="max-h-64 overflow-y-auto">
            {organizations.length === 0 ? (
              <div className="px-3 py-2 text-sm text-neutral-500">Brak organizacji</div>
            ) : (
              organizations.map((org) => (
                <button
                  key={org.id}
                  onClick={() => {
                    if (org.id !== activeOrgId) {
                      setActiveOrganization({ id: org.id, name: org.name })
                      navigate('/dashboard', { replace: true })
                    }
                    setOpen(false)
                  }}
                  title={org.name}
                  aria-current={org.id === activeOrgId ? 'true' : undefined}
                  className={`w-full text-left px-3 py-2 text-sm rounded-md flex items-center gap-2 hover:bg-neutral-100 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:outline-none ${
                    org.id === activeOrgId ? 'bg-neutral-50' : ''
                  }`}
                >
                  {org.id === activeOrgId && <Check className="h-4 w-4 text-brand-600 flex-shrink-0" aria-hidden="true" />}
                  <span className={`truncate ${org.id === activeOrgId ? 'font-medium' : ''}`}>{org.name}</span>
                </button>
              ))
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
