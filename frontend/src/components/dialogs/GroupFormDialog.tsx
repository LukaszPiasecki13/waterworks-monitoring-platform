import { useEffect, useMemo, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
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
import { Search } from 'lucide-react';
import type { SecurityGroupSummary, SecurityPermission } from '@/types/coreData';

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
  /** Pełny katalog uprawnień dostępnych na tej płaszczyźnie (już przefiltrowany
   * przez wywołującego do CAN_* dla org, PLATFORM_* dla platformy). */
  availablePermissions: SecurityPermission[];
  /** Użytkownicy dostępni do wyboru na tej płaszczyźnie (platform: wszyscy
   * użytkownicy; org: tylko członkowie tej organizacji). */
  availableUsers: SelectableUser[];
  onSubmit: (data: GroupFormData) => void;
  isLoading?: boolean;
  serverFieldErrors?: Record<string, string> | null;
}

export function GroupFormDialog({
  open,
  onOpenChange,
  group,
  availablePermissions,
  availableUsers,
  onSubmit,
  isLoading = false,
  serverFieldErrors,
}: GroupFormDialogProps) {
  const isEditing = !!group;
  const isNameLocked = group?.is_system ?? false;
  const arePermissionsLocked = (group?.is_system ?? false) && group?.system_key !== 'staff';
  const [permissionSearchQuery, setPermissionSearchQuery] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    setError,
    control,
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

  const filteredPermissions = useMemo(() => {
    if (!permissionSearchQuery.trim()) return availablePermissions;
    const q = permissionSearchQuery.toLowerCase();
    return availablePermissions.filter((p) => p.name.toLowerCase().includes(q));
  }, [availablePermissions, permissionSearchQuery]);

  const permissionsByCategory = useMemo(() => {
    const groups = new Map<string, SecurityPermission[]>();
    for (const permission of filteredPermissions) {
      const list = groups.get(permission.category) ?? [];
      list.push(permission);
      groups.set(permission.category, list);
    }
    return Array.from(groups.entries());
  }, [filteredPermissions]);

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

            <FormField label={`Uprawnienia (${availablePermissions.filter(p => availablePermissions.includes(p)).length > 0 ? (availablePermissions.length > 0 ? `${availablePermissions.filter(p => availablePermissions.includes(p)).length} dostępnych` : '0') : '0'})`}>
              <Controller
                name="permission_codes"
                control={control}
                render={({ field }) => (
                  <div className="space-y-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-neutral-400" />
                      <Input
                        placeholder="Szukaj uprawnień..."
                        value={permissionSearchQuery}
                        onChange={(e) => setPermissionSearchQuery(e.target.value)}
                        disabled={arePermissionsLocked}
                        className="pl-9"
                      />
                    </div>
                    <div className="text-xs text-neutral-600">
                      {field.value.length} / {availablePermissions.length} wybranych
                    </div>
                    <div className="max-h-64 overflow-y-auto rounded-md border border-neutral-200 p-3 space-y-3">
                      {permissionsByCategory.length === 0 ? (
                        <p className="text-sm text-neutral-500">Brak uprawnień spełniających kryterium</p>
                      ) : (
                        permissionsByCategory.map(([category, permissions]) => {
                          const checkedInCategory = permissions.filter((p) =>
                            field.value.includes(p.code)
                          );
                          const allChecked = checkedInCategory.length === permissions.length;
                          const someChecked =
                            checkedInCategory.length > 0 && !allChecked;

                          return (
                            <div key={category}>
                              <div className="flex items-center gap-2 mb-2">
                                <input
                                  type="checkbox"
                                  id={`category-${category}`}
                                  checked={allChecked || someChecked}
                                  disabled={arePermissionsLocked}
                                  onChange={(e) => {
                                    const codes = permissions.map((p) => p.code);
                                    const next = e.target.checked
                                      ? [
                                          ...new Set([...field.value, ...codes]),
                                        ]
                                      : field.value.filter(
                                          (c) => !codes.includes(c)
                                        );
                                    field.onChange(next);
                                  }}
                                />
                                <label
                                  htmlFor={`category-${category}`}
                                  className={`text-xs font-semibold uppercase cursor-pointer ${
                                    someChecked ? 'text-neutral-600' : 'text-neutral-700'
                                  }`}
                                >
                                  {category} ({checkedInCategory.length}/{permissions.length})
                                </label>
                              </div>
                              <div className="ml-4 space-y-1">
                                {permissions.map((permission) => (
                                  <label
                                    key={permission.code}
                                    className="flex items-center gap-2 py-1 text-sm text-neutral-900"
                                  >
                                    <input
                                      type="checkbox"
                                      checked={field.value.includes(
                                        permission.code
                                      )}
                                      disabled={arePermissionsLocked}
                                      onChange={(e) => {
                                        const next = e.target.checked
                                          ? [
                                              ...field.value,
                                              permission.code,
                                            ]
                                          : field.value.filter(
                                              (c) =>
                                                c !== permission.code
                                            );
                                        field.onChange(next);
                                      }}
                                    />
                                    {permission.name}
                                  </label>
                                ))}
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                )}
              />
              {arePermissionsLocked && (
                <p className="text-xs text-neutral-500 mt-2">
                  Uprawnień tej grupy systemowej nie można modyfikować
                </p>
              )}
            </FormField>

            <FormField label="Członkowie">
              <Controller
                name="user_ids"
                control={control}
                render={({ field }) => (
                  <div className="space-y-1 max-h-56 overflow-y-auto rounded-md border border-neutral-200 p-3">
                    {availableUsers.length === 0 && (
                      <p className="text-sm text-neutral-500">Brak dostępnych użytkowników</p>
                    )}
                    {availableUsers.map((user) => (
                      <label
                        key={user.id}
                        className="flex items-center gap-2 py-1 text-sm text-neutral-900"
                      >
                        <input
                          type="checkbox"
                          checked={field.value.includes(user.id)}
                          onChange={(e) => {
                            const next = e.target.checked
                              ? [...field.value, user.id]
                              : field.value.filter((id) => id !== user.id);
                            field.onChange(next);
                          }}
                        />
                        {user.label}
                      </label>
                    ))}
                  </div>
                )}
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
