import { useCallback, useState } from 'react'
import type { UseMutationResult } from '@tanstack/react-query'
import { toast } from '@/components/ui/Toast'
import { parseApiError } from '@/lib/errors'

export interface CrudMessages {
  createSuccess: string
  updateSuccess: string
  deleteSuccess: string
  createErrorFallback: string
  updateErrorFallback: string
  deleteErrorFallback: string
}

export interface UseCrudPageStateOptions<
  TId,
  TFormData,
  TCreateInput = TFormData,
  TUpdateInput = TFormData,
  TCreateResult = unknown,
> {
  createMutation: UseMutationResult<TCreateResult, unknown, TCreateInput>
  updateMutation: UseMutationResult<unknown, unknown, { id: TId; data: TUpdateInput }>
  deleteMutation: UseMutationResult<unknown, unknown, TId>
  messages: CrudMessages
  /** Przekształć dane z formularza na payload create, gdy się różnią. Domyślnie identyczność. */
  toCreateInput?: (data: TFormData) => TCreateInput
  /** Przekształć dane z formularza na payload update, gdy się różnią. Domyślnie identyczność. */
  toUpdateInput?: (data: TFormData) => TUpdateInput
  /** Dodatkowy efekt uboczny po udanym create, PO domyślnym toast+zamknięciu. */
  onCreateSuccess?: (result: TCreateResult, formData: TFormData) => void
  onUpdateSuccess?: () => void
}

export interface CrudPageState<TId, TFormData> {
  isFormOpen: boolean
  setIsFormOpen: (open: boolean) => void
  editingId: TId | null
  openCreate: () => void
  openEdit: (id: TId) => void
  handleSubmit: (data: TFormData) => void
  isSubmitting: boolean

  deleteId: TId | null
  requestDelete: (id: TId) => void
  cancelDelete: () => void
  confirmDelete: () => void
  isDeleting: boolean

  serverFieldErrors: Record<string, string> | null
}

export function useCrudPageState<
  TId,
  TFormData,
  TCreateInput = TFormData,
  TUpdateInput = TFormData,
  TCreateResult = unknown,
>(
  options: UseCrudPageStateOptions<TId, TFormData, TCreateInput, TUpdateInput, TCreateResult>
): CrudPageState<TId, TFormData> {
  const { createMutation, updateMutation, deleteMutation, messages } = options

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingId, setEditingId] = useState<TId | null>(null)
  const [deleteId, setDeleteId] = useState<TId | null>(null)
  const [serverFieldErrors, setServerFieldErrors] = useState<Record<string, string> | null>(null)

  const openCreate = useCallback(() => {
    setEditingId(null)
    setServerFieldErrors(null)
    setIsFormOpen(true)
  }, [])

  const openEdit = useCallback((id: TId) => {
    setEditingId(id)
    setServerFieldErrors(null)
    setIsFormOpen(true)
  }, [])

  const buildOnError = useCallback(
    (fallback: string) => (error: unknown) => {
      const parsed = parseApiError(error)
      if (parsed.fieldErrors) setServerFieldErrors(parsed.fieldErrors)
      toast.error(parsed.statusCode ? parsed.message : fallback)
    },
    []
  )

  const handleSubmit = useCallback(
    (data: TFormData) => {
      if (editingId !== null) {
        const payload = (options.toUpdateInput ?? ((d: TFormData) => d as unknown as TUpdateInput))(
          data
        )
        updateMutation.mutate(
          { id: editingId, data: payload },
          {
            onSuccess: () => {
              setIsFormOpen(false)
              setEditingId(null)
              setServerFieldErrors(null)
              toast.success(messages.updateSuccess)
              options.onUpdateSuccess?.()
            },
            onError: buildOnError(messages.updateErrorFallback),
          }
        )
      } else {
        const payload = (options.toCreateInput ?? ((d: TFormData) => d as unknown as TCreateInput))(
          data
        )
        createMutation.mutate(payload, {
          onSuccess: (result) => {
            setIsFormOpen(false)
            setServerFieldErrors(null)
            toast.success(messages.createSuccess)
            options.onCreateSuccess?.(result, data)
          },
          onError: buildOnError(messages.createErrorFallback),
        })
      }
    },
    [editingId, createMutation, updateMutation, messages, buildOnError, options]
  )

  const requestDelete = useCallback((id: TId) => setDeleteId(id), [])
  const cancelDelete = useCallback(() => setDeleteId(null), [])

  const confirmDelete = useCallback(() => {
    if (deleteId === null) return
    deleteMutation.mutate(deleteId, {
      onSuccess: () => {
        setDeleteId(null)
        toast.success(messages.deleteSuccess)
      },
      onError: buildOnError(messages.deleteErrorFallback),
    })
  }, [deleteId, deleteMutation, messages, buildOnError])

  return {
    isFormOpen,
    setIsFormOpen,
    editingId,
    openCreate,
    openEdit,
    handleSubmit,
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    deleteId,
    requestDelete,
    cancelDelete,
    confirmDelete,
    isDeleting: deleteMutation.isPending,
    serverFieldErrors,
  }
}
