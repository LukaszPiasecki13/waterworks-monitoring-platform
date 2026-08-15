import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUser } from '@/hooks/useUsers';
import { useOrganizations } from '@/hooks/useOrganizations';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogBody } from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';

const userSchema = z.object({
  username: z.string().min(1, 'Nazwa użytkownika jest wymagana').min(3, 'Minimum 3 znaki'),
  email: z.string().email('Podaj prawidłowy email'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  status: z.enum(['regular', 'admin']).optional(),
  is_active: z.boolean().optional(),
  organization_id: z.string().optional(),
});

export type UserFormData = z.infer<typeof userSchema>;

interface UserFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  userId?: number | null;
  onSubmit: (data: UserFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function UserFormDialog({
  open,
  onOpenChange,
  userId,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: UserFormDialogProps) {
  const { data: user } = useUser(userId || 0);
  const { data: organizations = [] } = useOrganizations();
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      status: 'regular',
      is_active: true,
    },
  });

  useEffect(() => {
    if (userId && user) {
      reset({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        status: (user.status as 'regular' | 'admin') || 'regular',
        is_active: user.is_active,
        organization_id: user.organization_id || '',
      });
    } else {
      reset();
    }
  }, [userId, user, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof UserFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: UserFormData) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{userId ? 'Edytuj użytkownika' : 'Nowy użytkownik'}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <FormField label="Nazwa użytkownika" error={errors.username?.message} required>
              <Input
                {...register('username')}
                placeholder="Nazwa użytkownika"
                disabled={!!userId}
              />
            </FormField>

            <FormField label="Email" error={errors.email?.message} required>
              <Input
                {...register('email')}
                type="email"
                placeholder="Email"
              />
            </FormField>

            <FormField label="Imię" error={errors.first_name?.message}>
              <Input
                {...register('first_name')}
                placeholder="Imię"
              />
            </FormField>

            <FormField label="Nazwisko" error={errors.last_name?.message}>
              <Input
                {...register('last_name')}
                placeholder="Nazwisko"
              />
            </FormField>

            <FormField label="Status" error={errors.status?.message}>
              <Select {...register('status')}>
                <option value="regular">Zwykły użytkownik</option>
                <option value="admin">Administrator</option>
              </Select>
            </FormField>

            <FormField label="Organizacja" error={errors.organization_id?.message}>
              <Select {...register('organization_id')}>
                <option value="">Brak (Platform admin)</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
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
            {userId ? 'Aktualizuj' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
