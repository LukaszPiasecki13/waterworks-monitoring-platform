import { useState, useMemo } from 'react'
import { useAddMember, useMembers } from '@/hooks/useMembers'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { Check, Search } from 'lucide-react'
import type { OrganizationMember } from '@/types/coreData'

interface AddMemberDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AddMemberDialog({ open, onOpenChange }: AddMemberDialogProps) {
  const addMutation = useAddMember()
  const { data: members = [] } = useMembers()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  const [error, setError] = useState<string>('')

  const filteredMembers = useMemo(() => {
    if (!searchQuery.trim()) return []
    const q = searchQuery.toLowerCase()
    return members.filter(
      (m) =>
        m.first_name.toLowerCase().includes(q) ||
        m.last_name.toLowerCase().includes(q) ||
        m.email.toLowerCase().includes(q)
    )
  }, [members, searchQuery])

  const handleSelectUser = (user: OrganizationMember) => {
    setSelectedUserId(user.id)
    setSearchQuery(`${user.first_name} ${user.last_name}`)
  }

  const handleSubmit = async () => {
    if (!selectedUserId) {
      setError('Wybierz użytkownika')
      return
    }
    setError('')
    try {
      await addMutation.mutateAsync(selectedUserId)
      setSearchQuery('')
      setSelectedUserId(null)
      onOpenChange(false)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Nie udało się dodać członka'
      setError(errorMsg)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setSearchQuery('')
      setSelectedUserId(null)
      setError('')
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Dodaj członka organizacji</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="memberSearch" className="block text-sm font-medium text-neutral-700 mb-2">
              Szukaj członka
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-neutral-400" />
              <Input
                id="memberSearch"
                type="text"
                placeholder="Imię, nazwisko lub email..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setSelectedUserId(null)
                }}
                disabled={addMutation.isPending}
                className="pl-9"
              />
            </div>
          </div>

          {searchQuery.trim() && filteredMembers.length > 0 && (
            <div className="border border-neutral-200 rounded-md max-h-56 overflow-y-auto bg-neutral-50">
              {filteredMembers.map((member) => (
                <button
                  key={member.id}
                  onClick={() => handleSelectUser(member)}
                  className="w-full text-left px-4 py-3 hover:bg-neutral-100 border-b border-neutral-100 last:border-0 transition-colors"
                  disabled={addMutation.isPending}
                  type="button"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm text-neutral-900">
                        {member.first_name} {member.last_name}
                      </div>
                      <div className="text-xs text-neutral-600">{member.email}</div>
                    </div>
                    {selectedUserId === member.id && (
                      <Check className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {searchQuery.trim() && filteredMembers.length === 0 && (
            <div className="text-center py-4 text-neutral-500 text-sm">
              Nie znaleziono użytkownika
            </div>
          )}

          {!searchQuery.trim() && (
            <div className="text-center py-4 text-neutral-500 text-sm">
              Zacznij pisać aby szukać
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={addMutation.isPending}
            >
              Anuluj
            </Button>
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={!selectedUserId || addMutation.isPending}
            >
              {addMutation.isPending ? 'Dodawanie...' : 'Dodaj członka'}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  )
}
