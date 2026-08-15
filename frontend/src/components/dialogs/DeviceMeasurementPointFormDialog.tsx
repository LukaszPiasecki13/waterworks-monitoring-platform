import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/Dialog'
import { FormField } from '@/components/ui/FormField'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import type { MeasurementPoint, MeasurementPointCreateRequest, MeasurementPointUpdateRequest } from '@/types/coreData'

interface DeviceMeasurementPointFormDialogProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: MeasurementPointCreateRequest | MeasurementPointUpdateRequest) => void
  device_id: string
  initialData?: MeasurementPoint
  isLoading?: boolean
  serverFieldErrors?: Record<string, string> | null
}

type PointType = 'pressure' | 'flow_rate' | 'total_volume' | 'power_status'

interface FormData {
  external_id: string
  point_type: PointType
  unit: string
  min_technical: string
  max_technical: string
}

export function DeviceMeasurementPointFormDialog({
  isOpen,
  onClose,
  onSubmit,
  device_id,
  initialData,
  isLoading = false,
  serverFieldErrors,
}: DeviceMeasurementPointFormDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      external_id: '',
      point_type: 'pressure',
      unit: '',
      min_technical: '',
      max_technical: '',
    },
  })

  useEffect(() => {
    if (initialData) {
      reset({
        external_id: initialData.external_id,
        point_type: initialData.point_type as PointType,
        unit: initialData.unit,
        min_technical: initialData.min_technical?.toString() || '',
        max_technical: initialData.max_technical?.toString() || '',
      })
    } else {
      reset({
        external_id: '',
        point_type: 'pressure',
        unit: '',
        min_technical: '',
        max_technical: '',
      })
    }
  }, [initialData, reset, isOpen])

  useEffect(() => {
    if (!serverFieldErrors) return
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof FormData, { type: 'server', message })
    })
  }, [serverFieldErrors, setError])

  const handleFormSubmit = (data: FormData) => {
    if (initialData) {
      const updateData: MeasurementPointUpdateRequest = {
        point_type: data.point_type,
        unit: data.unit,
        min_technical: data.min_technical ? parseFloat(data.min_technical) : undefined,
        max_technical: data.max_technical ? parseFloat(data.max_technical) : undefined,
      }
      onSubmit(updateData)
    } else {
      const createData: MeasurementPointCreateRequest = {
        device_id,
        external_id: data.external_id,
        point_type: data.point_type,
        unit: data.unit,
        min_technical: data.min_technical ? parseFloat(data.min_technical) : undefined,
        max_technical: data.max_technical ? parseFloat(data.max_technical) : undefined,
      }
      onSubmit(createData)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            {initialData ? 'Edytuj punkt pomiarowy' : 'Nowy punkt pomiarowy'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <FormField label="Identyfikator czujnika" error={errors.external_id?.message} required>
            <Input
              {...register('external_id', { required: 'Identyfikator czujnika jest wymagany' })}
              placeholder="np. SENSOR_001"
            />
          </FormField>

          <FormField label="Typ Pomiaru" error={errors.point_type?.message} required>
            <Select {...register('point_type', { required: 'Typ pomiaru jest wymagany' })}>
              <option value="">Wybierz typ</option>
              <option value="pressure">Ciśnienie</option>
              <option value="flow_rate">Przepływ</option>
              <option value="total_volume">Całkowita objętość</option>
              <option value="power_status">Status zasilania</option>
            </Select>
          </FormField>

          <FormField label="Jednostka" error={errors.unit?.message} required>
            <Input
              {...register('unit', { required: 'Jednostka jest wymagana' })}
              placeholder="np. bar, L/min"
            />
          </FormField>

          <FormField label="Minimum techniczne" error={errors.min_technical?.message}>
            <Input
              {...register('min_technical')}
              type="number"
              step="0.01"
              placeholder="Brak"
            />
          </FormField>

          <FormField label="Maksimum techniczne" error={errors.max_technical?.message}>
            <Input
              {...register('max_technical')}
              type="number"
              step="0.01"
              placeholder="Brak"
            />
          </FormField>

          <div className="flex gap-3 justify-end pt-4">
            <Button variant="outline" type="button" onClick={onClose}>
              Anuluj
            </Button>
            <Button type="submit" isLoading={isLoading}>
              {initialData ? 'Zapisz' : 'Utwórz'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
