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
  name: z.string().min(1, 'Nazwa jest wymagana').min(2, 'Minimum 2 znaki'),
  device_type: z.string().optional(),
  water_object_id: z.string().min(1, 'Obiekt wodny jest wymagany'),
});

type DeviceFormData = z.infer<typeof deviceSchema>;

interface DeviceFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  deviceId?: string | null;
  onSubmit: (data: DeviceFormData) => void;
  isLoading?: boolean;
}

export function DeviceFormDialog({
  open,
  onOpenChange,
  deviceId,
  onSubmit,
  isLoading = false,
}: DeviceFormDialogProps) {
  const { data: device } = useDevice(deviceId || '');
  const { data: waterObjects = [] } = useWaterObjects();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DeviceFormData>({
    resolver: zodResolver(deviceSchema),
  });

  useEffect(() => {
    if (deviceId && device) {
      reset({
        name: device.name,
        device_type: device.device_type || '',
        water_object_id: device.water_object_id,
      });
    } else {
      reset();
    }
  }, [deviceId, device, reset]);

  const handleFormSubmit = (data: DeviceFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{deviceId ? 'Edytuj urządzenie' : 'Nowe urządzenie'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <FormField label="Nazwa" error={errors.name?.message} required>
              <Input
                {...register('name')}
                placeholder="Nazwa urządzenia"
              />
            </FormField>

            <FormField label="Typ urządzenia" error={errors.device_type?.message}>
              <Input
                {...register('device_type')}
                placeholder="np. Czujnik temperatury"
              />
            </FormField>

            <FormField label="Obiekt wodny" error={errors.water_object_id?.message} required>
              <Select {...register('water_object_id')}>
                <option value="">Wybierz obiekt wodny</option>
                {waterObjects.map((wo) => (
                  <option key={wo.id} value={wo.id}>
                    {wo.name}
                  </option>
                ))}
              </Select>
            </FormField>
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
            {deviceId ? 'Aktualizuj' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
