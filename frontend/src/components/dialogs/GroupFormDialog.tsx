import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogBody,
} from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';
import type { SecurityGroupSummary } from '@/types/coreData';

const groupSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana').max(120, 'Maksymalnie 120 znaków'),
  description: z.string().max(500, 'Maksymalnie 500 znaków').optional(),
  permission_codes: z.array(z.string()),
  user_ids: z.array(z.string()),
});

export type GroupFormData = z.infer<typeof groupSchema>;

export interface SelectableUser {
  id: string;
  label: string;
}

interface GroupFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  group?: SecurityGroupSummary | null;
  availablePermissions: unknown[];
  availableUsers: unknown[];
  onSubmit: (data: GroupFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function GroupFormDialog({
  open,
  onOpenChange,
  group,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: GroupFormDialogProps) {
  const isEditing = !!group;
  const isNameLocked = group?.is_system ?? false;

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<GroupFormData>({
    resolver: zodResolver(groupSchema),
    defaultValues: { name: '', description: '', permission_codes: [], user_ids: [] },
  });

  useEffect(() => {
    if (group) {
      reset({
        name: group.name,
        description: group.description ?? '',
        permission_codes: group.permissions.map((p) => p.code),
        user_ids: group.user_ids,
      });
    } else {
      reset({ name: '', description: '', permission_codes: [], user_ids: [] });
    }
  }, [group, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof GroupFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: GroupFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edytuj grupę' : 'Nowa grupa'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <FormField label="Nazwa" error={errors.name?.message} required>
              <Input
                {...register('name')}
                placeholder="Nazwa grupy"
                disabled={isNameLocked}
              />
              {isNameLocked && (
                <p className="text-xs text-neutral-500">
                  Nie możesz edytować grupy systemowej
                </p>
              )}
            </FormField>

            <FormField label="Opis" error={errors.description?.message}>
              <Input
                {...register('description')}
                placeholder="Opis grupy"
                disabled={isNameLocked}
              />
            </FormField>
          </form>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            Anuluj
          </Button>
          <Button onClick={handleSubmit(handleFormSubmit)} isLoading={isLoading}>
            {isEditing ? 'Zapisz' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
