import { useOrganizations } from '@/hooks/useOrganizations'
import {
  useUserOrganizations,
  useAssignUserOrganization,
  useRemoveUserOrganization,
} from '@/hooks/useUserOrganizations'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { toast } from '@/components/ui/Toast'

interface ManageUserOrganizationsDialogProps {
  userId: string | null
  username?: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ManageUserOrganizationsDialog({
  userId,
  username,
  open,
  onOpenChange,
}: ManageUserOrganizationsDialogProps) {
  const { data: allOrgs = [], isLoading: isLoadingAll } = useOrganizations()
  const { data: userOrgsResponse, isLoading: isLoadingUser } = useUserOrganizations(userId)
  const assignMutation = useAssignUserOrganization(userId || '')
  const removeMutation = useRemoveUserOrganization(userId || '')

  const assignedIds = new Set((userOrgsResponse?.organizations ?? []).map((o) => o.id))
  const isLoading = isLoadingAll || isLoadingUser

  const handleToggle = async (orgId: string, isAssigned: boolean) => {
    try {
      if (isAssigned) {
        await removeMutation.mutateAsync(orgId)
        toast.success('Użytkownik odłączony od organizacji')
      } else {
        await assignMutation.mutateAsync(orgId)
        toast.success('Użytkownik przypisany do organizacji')
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Operacja nie powiodła się'
      toast.error(message)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            Organizacje{username ? ` — ${username}` : ''}
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <p className="text-sm text-neutral-500 py-4">Ładowanie…</p>
        ) : allOrgs.length === 0 ? (
          <p className="text-sm text-neutral-500 py-4">Brak organizacji w systemie</p>
        ) : (
          <ul className="max-h-80 overflow-y-auto divide-y divide-neutral-200">
            {allOrgs.map((org) => {
              const isAssigned = assignedIds.has(org.id)
              const isPending =
                (assignMutation.isPending && assignMutation.variables === org.id) ||
                (removeMutation.isPending && removeMutation.variables === org.id)

              return (
                <li key={org.id} className="flex items-center justify-between py-2">
                  <label className="flex items-center gap-3 text-sm cursor-pointer flex-1">
                    <input
                      type="checkbox"
                      checked={isAssigned}
                      disabled={isPending}
                      onChange={() => handleToggle(org.id, isAssigned)}
                      className="h-4 w-4 rounded border-neutral-300"
                    />
                    {org.name}
                  </label>
                  {isPending && (
                    <span className="text-xs text-neutral-400">Zapisywanie…</span>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </DialogContent>
    </Dialog>
  )
}
