import { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useWaterObject } from '@/hooks/useWaterObjects';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogBody } from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Select } from '@/components/ui/Select';

const waterObjectSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana').min(2, 'Minimum 2 znaki'),
  object_type: z.string().min(1, 'Typ obiektu jest wymagany'),
  location_description: z.string().optional(),
});

export type WaterObjectFormData = z.infer<typeof waterObjectSchema>;

interface WaterObjectFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  waterObjectId?: string | null;
  onSubmit: (data: WaterObjectFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function WaterObjectFormDialog({
  open,
  onOpenChange,
  waterObjectId,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: WaterObjectFormDialogProps) {
  const { data: waterObject } = useWaterObject(waterObjectId || '');
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<WaterObjectFormData>({
    resolver: zodResolver(waterObjectSchema),
  });
  const nameInputRef = useRef<HTMLInputElement | null>(null);
  const { ref: nameRegisterRef, ...nameRegisterProps } = register('name');

  // Reset form immediately when waterObjectId changes (clear old data before loading new)
  useEffect(() => {
    if (!waterObjectId) {
      reset({
        name: '',
        object_type: '',
        location_description: '',
      });
    } else {
      reset(); // Clear old data while loading new
    }
  }, [waterObjectId, reset]);

  // Populate form with loaded data
  useEffect(() => {
    if (waterObjectId && waterObject) {
      reset({
        name: waterObject.name,
        object_type: waterObject.object_type,
        location_description: waterObject.location_description || '',
      });
    }
  }, [waterObjectId, waterObject, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof WaterObjectFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: WaterObjectFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          const input = nameInputRef.current;
          if (input) {
            input.focus();
            const len = input.value.length;
            input.setSelectionRange(len, len);
          }
        }}
      >
        <DialogHeader>
          <DialogTitle>{waterObjectId ? 'Edytuj obiekt wodny' : 'Nowy obiekt wodny'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <FormField label="Nazwa" error={errors.name?.message} required>
              <Input
                {...nameRegisterProps}
                ref={(el) => {
                  nameRegisterRef(el);
                  nameInputRef.current = el;
                }}
                placeholder="Nazwa obiektu"
                onFocus={(e) => {
                  const len = e.currentTarget.value.length;
                  e.currentTarget.setSelectionRange(len, len);
                }}
                onMouseDown={(e) => {
                  e.preventDefault();
                  const len = e.currentTarget.value.length;
                  e.currentTarget.setSelectionRange(len, len);
                }}
              />
            </FormField>

            <FormField label="Typ obiektu" error={errors.object_type?.message} required>
              <Select {...register('object_type')}>
                <option value="">Wybierz typ</option>
                <option value="reservoir">Zbiornik</option>
                <option value="pump_station">Stacja pomp</option>
                <option value="treatment_plant">Oczyszczalnia</option>
                <option value="distribution_center">Centrum dystrybucji</option>
                <option value="other">Inne</option>
              </Select>
            </FormField>

            <FormField label="Opis lokalizacji" error={errors.location_description?.message}>
              <Textarea
                {...register('location_description')}
                placeholder="Opis lokalizacji"
                className="resize-none"
              />
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
            {waterObjectId ? 'Aktualizuj' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
