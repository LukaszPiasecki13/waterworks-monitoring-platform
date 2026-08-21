import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUser } from '@/hooks/useUsers';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogBody } from '@/components/ui/Dialog';
import { FormField } from '@/components/ui/FormField';
import { Input } from '@/components/ui/Input';

const userSchema = z.object({
  username: z.string().min(1, 'Nazwa użytkownika jest wymagana').min(3, 'Minimum 3 znaki'),
  email: z.string().email('Podaj prawidłowy email'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  is_active: z.boolean().optional(),
  password: z.string().optional(),
});

export type UserFormData = z.infer<typeof userSchema>;

interface UserFormDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  userId?: string | null;
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
  const { data: user } = useUser(userId || '');
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
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
        is_active: user.is_active,
      });
    } else {
      reset({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_active: true,
      });
    }
  }, [userId, user, reset]);

  useEffect(() => {
    if (!serverFieldErrors) return;
    Object.entries(serverFieldErrors).forEach(([field, message]) => {
      setError(field as keyof UserFormData, { type: 'server', message });
    });
  }, [serverFieldErrors, setError]);

  const handleFormSubmit = (data: UserFormData) => {
    // Password is required for new users (create), optional for updates
    if (!userId && !data.password) {
      setError('password', { type: 'required', message: 'Hasło jest wymagane' });
      return;
    }
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

            <FormField label="Hasło" error={errors.password?.message} required={!userId}>
              <Input
                {...register('password')}
                type="password"
                placeholder={userId ? 'Pozostaw puste, aby nie zmieniać' : 'Hasło'}
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
            {userId ? 'Aktualizuj' : 'Utwórz'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
