import { useUsers } from '@/hooks/useUsers'
import {
  useOrganizationMembers,
  useAddOrganizationMember,
  useRemoveOrganizationMember,
} from '@/hooks/useOrganizationMembers'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { toast } from '@/components/ui/Toast'

interface ManageOrganizationMembersDialogProps {
  orgId: string | null
  orgName?: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ManageOrganizationMembersDialog({
  orgId,
  orgName,
  open,
  onOpenChange,
}: ManageOrganizationMembersDialogProps) {
  const { data: allUsers = [], isLoading: isLoadingUsers } = useUsers()
  const { data: members = [], isLoading: isLoadingMembers } = useOrganizationMembers(orgId)
  const addMutation = useAddOrganizationMember(orgId || '')
  const removeMutation = useRemoveOrganizationMember(orgId || '')

  const memberIds = new Set(members.map((m) => m.id))
  const isLoading = isLoadingUsers || isLoadingMembers

  const handleToggle = async (userId: string, isMember: boolean) => {
    try {
      if (isMember) {
        await removeMutation.mutateAsync(userId)
        toast.success('Użytkownik usunięty z organizacji')
      } else {
        await addMutation.mutateAsync(userId)
        toast.success('Użytkownik dodany do organizacji')
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
            Członkowie{orgName ? ` — ${orgName}` : ''}
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <p className="text-sm text-neutral-500 py-4">Ładowanie…</p>
        ) : allUsers.length === 0 ? (
          <p className="text-sm text-neutral-500 py-4">Brak użytkowników w systemie</p>
        ) : (
          <ul className="max-h-80 overflow-y-auto divide-y divide-neutral-200">
            {allUsers.map((user) => {
              const isMember = memberIds.has(user.id)
              const isPending =
                (addMutation.isPending && addMutation.variables === user.id) ||
                (removeMutation.isPending && removeMutation.variables === user.id)

              return (
                <li key={user.id} className="flex items-center justify-between py-2">
                  <label className="flex items-center gap-3 text-sm cursor-pointer flex-1">
                    <input
                      type="checkbox"
                      checked={isMember}
                      disabled={isPending}
                      onChange={() => handleToggle(user.id, isMember)}
                      className="h-4 w-4 rounded border-neutral-300"
                    />
                    <div>
                      <div className="font-medium text-neutral-900">
                        {user.first_name} {user.last_name}
                      </div>
                      <div className="text-xs text-neutral-500">{user.email}</div>
                    </div>
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
