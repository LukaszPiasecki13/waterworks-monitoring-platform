import { useState, useEffect } from 'react'
import * as RadixDialog from '@radix-ui/react-dialog'
import { useSecurityGroups, useUserGroups, useReplaceUserGroups } from '@/hooks/useSecurityGroups'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/Dialog'
import { toast } from '@/components/ui/Toast'

interface UserGroupsModalProps {
  userId: string
  userEmail: string
  onClose: () => void
}

export function UserGroupsModal({ userId, userEmail, onClose }: UserGroupsModalProps) {
  const { groups } = useSecurityGroups()
  const { data: userGroupIds = [] } = useUserGroups(userId)
  const replaceUserGroups = useReplaceUserGroups()

  const [selectedGroupIds, setSelectedGroupIds] = useState<string[]>([])
  const [isChanged, setIsChanged] = useState(false)

  useEffect(() => {
    setSelectedGroupIds(userGroupIds)
    setIsChanged(false)
  }, [userGroupIds])

  const handleToggleGroup = (groupId: string) => {
    setSelectedGroupIds((prev) => {
      const next = prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
      setIsChanged(
        next.length !== userGroupIds.length ||
          !next.every((id) => userGroupIds.includes(id))
      )
      return next
    })
  }

  const handleSave = () => {
    replaceUserGroups.mutate(
      { userId, groupIds: selectedGroupIds },
      {
        onSuccess: () => {
          setIsChanged(false)
          onClose()
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Błąd przy aktualizacji grup')
        },
      }
    )
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Grupy użytkownika: {userEmail}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3 py-4 max-h-96 overflow-y-auto">
          {groups.length === 0 ? (
            <div className="text-sm text-neutral-500">Brak grup</div>
          ) : (
            groups.map((group) => (
              <label
                key={group.id}
                className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-neutral-100 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedGroupIds.includes(group.id)}
                  onChange={() => handleToggleGroup(group.id)}
                  className="w-4 h-4"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-neutral-900">{group.name}</div>
                  <div className="text-xs text-neutral-500">{group.description}</div>
                </div>
                {group.is_system && (
                  <Badge variant="info" className="flex-shrink-0">
                    Systemowa
                  </Badge>
                )}
              </label>
            ))
          )}
        </div>
        <DialogFooter>
          <RadixDialog.Close asChild>
            <Button variant="outline">Anuluj</Button>
          </RadixDialog.Close>
          <Button onClick={handleSave} disabled={!isChanged || replaceUserGroups.isPending}>
            {replaceUserGroups.isPending ? 'Zapisywanie...' : 'Zapisz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
