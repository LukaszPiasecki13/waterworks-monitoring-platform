import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useOrganization } from '@/hooks/useOrganizations';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogBody } from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';

const organizationSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana').min(2, 'Minimum 2 znaki'),
});

export type OrganizationFormData = z.infer<typeof organizationSchema>;

interface OrganizationFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  organizationId?: string | null;
  onSubmit: (data: OrganizationFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function OrganizationFormDialog({
  open,
  onOpenChange,
  organizationId,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: OrganizationFormDialogProps) {
  const { data: organization } = useOrganization(organizationId || '');
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<OrganizationFormData>({
    resolver: zodResolver(organizationSchema),
  });

  useEffect(() => {
    if (organizationId && organization) {
      reset({
        name: organization.name,
      });
    } else {
      reset();
    }
  }, [organizationId, organization, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof OrganizationFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: OrganizationFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{organizationId ? 'Edytuj organizację' : 'Nowa organizacja'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <FormField label="Nazwa" error={errors.name?.message} required>
              <Input
                {...register('name')}
                placeholder="Nazwa organizacji"
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
            {organizationId ? 'Aktualizuj' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
