import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAddMember } from '@/hooks/useMembers'
import { Button } from '@/components/ui/Button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { HelpCircle } from 'lucide-react'

interface AddMemberDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface AddMemberFormData {
  userId: string
}

export function AddMemberDialog({ open, onOpenChange }: AddMemberDialogProps) {
  const addMutation = useAddMember()
  const [error, setError] = useState<string>('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AddMemberFormData>()

  const onSubmit = async (data: AddMemberFormData) => {
    setError('')
    try {
      await addMutation.mutateAsync(data.userId)
      reset()
      onOpenChange(false)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Nie udało się dodać członka'
      setError(errorMsg)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Dodaj członka organizacji</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-neutral-600 mb-4">
          Wpisz identyfikator użytkownika (UUID) aby dodać go do organizacji
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="userId" className="block text-sm font-medium text-neutral-700 mb-1">
              Identyfikator użytkownika (UUID)
            </label>
            <div className="relative">
              <input
                id="userId"
                type="text"
                placeholder="550e8400-e29b-41d4-a716-446655440000"
                {...register('userId', {
                  required: 'Identyfikator użytkownika jest wymagany',
                  pattern: {
                    value: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
                    message: 'Nieprawidłowy format UUID',
                  },
                })}
                className="min-h-10 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={addMutation.isPending}
              />
              <div className="absolute right-3 top-3 text-neutral-400">
                <HelpCircle className="h-4 w-4" />
              </div>
            </div>
            {errors.userId && (
              <p className="mt-1 text-sm text-red-600">{errors.userId.message}</p>
            )}
            <p className="mt-1 text-xs text-neutral-500">
              Możesz znaleźć UUID użytkownika na liście użytkowników platformy
            </p>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={addMutation.isPending}
            >
              Anuluj
            </Button>
            <Button type="submit" disabled={addMutation.isPending}>
              {addMutation.isPending ? 'Dodawanie...' : 'Dodaj członka'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
