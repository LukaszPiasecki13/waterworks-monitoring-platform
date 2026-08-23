import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useDevice } from '@/hooks/useDevices';
import { useWaterObjects } from '@/hooks/useWaterObjects';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogBody } from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';

const deviceSchema = z.object({
  external_id: z.string(),
  water_object_id: z.string().optional(),
  is_active: z.boolean().optional(),
});

export type DeviceFormData = z.infer<typeof deviceSchema>;

interface DeviceFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  deviceId?: string | null;
  onSubmit: (data: DeviceFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function DeviceFormDialog({
  open,
  onOpenChange,
  deviceId,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: DeviceFormDialogProps) {
  const { data: device } = useDevice(deviceId || '');
  const { data: waterObjects = [] } = useWaterObjects();
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<DeviceFormData>({
    resolver: zodResolver(deviceSchema),
  });

  useEffect(() => {
    if (deviceId && device) {
      reset({
        external_id: device.external_id,
        water_object_id: device.water_object_id ?? undefined,
        is_active: device.is_active,
      });
    } else {
      reset();
    }
  }, [deviceId, device, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof DeviceFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: DeviceFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{deviceId ? 'Edytuj urządzenie' : 'Przypisz urządzenie'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            {!deviceId && (
              <FormField
                label="Numer seryjny (SN)"
                error={errors.external_id?.message}
                required
              >
                <Input
                  {...register('external_id', {
                    required: 'Numer seryjny jest wymagany',
                    minLength: { value: 1, message: 'Wymagane' }
                  })}
                  placeholder="np. WW-3CDC756F6DC0"
                />
              </FormField>
            )}

            {!deviceId && (
              <FormField label="Obiekt wodny" error={errors.water_object_id?.message} required>
                <Select
                  {...register('water_object_id', {
                    required: 'Obiekt wodny jest wymagany'
                  })}
                >
                  <option value="">Wybierz obiekt wodny</option>
                  {waterObjects.map((wo) => (
                    <option key={wo.id} value={wo.id}>
                      {wo.name}
                    </option>
                  ))}
                </Select>
              </FormField>
            )}

            {deviceId && (
              <FormField label="Status">
                <label className="flex items-center gap-2">
                  <input type="checkbox" {...register('is_active')} />
                  <span className="text-sm">Aktywne</span>
                </label>
              </FormField>
            )}
          </form>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            Anuluj
          </Button>
          <Button
            onClick={handleSubmit(handleFormSubmit)}
            isLoading={isLoading}
          >
            {deviceId ? 'Aktualizuj' : 'Przypisz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
