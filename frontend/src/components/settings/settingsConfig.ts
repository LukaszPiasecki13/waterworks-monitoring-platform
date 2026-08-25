import type { PermissionCode } from '@/types/permissions';
import type { LucideIcon } from 'lucide-react';
import { Users, UsersRound, UserCircle } from 'lucide-react';

export interface SettingsSection {
  key: string;
  label: string;
  permission: PermissionCode | PermissionCode[];
  icon?: LucideIcon;
  render: () => React.ReactNode;
}

export const getPlatformSections = (): SettingsSection[] => [
  {
    key: 'users',
    label: 'Użytkownicy',
    permission: 'PLATFORM_VIEW_USERS',
    icon: Users,
    render: () => null, // Set in SettingsDialog dynamically
  },
  {
    key: 'groups',
    label: 'Grupy',
    permission: 'PLATFORM_MANAGE_ORGANIZATIONS',
    icon: UsersRound,
    render: () => null, // Set in SettingsDialog dynamically
  },
  {
    key: 'account',
    label: 'Moje konto',
    permission: [] as PermissionCode[], // Everyone has access
    icon: UserCircle,
    render: () => null, // Set in SettingsDialog dynamically
  },
];

export const getOrgSections = (): SettingsSection[] => [
  {
    key: 'members',
    label: 'Członkowie',
    permission: 'CAN_MANAGE_USERS',
    icon: Users,
    render: () => null, // Set in SettingsDialog dynamically
  },
  {
    key: 'groups',
    label: 'Grupy',
    permission: 'CAN_VIEW_SECURITY',
    icon: UsersRound,
    render: () => null, // Set in SettingsDialog dynamically
  },
  {
    key: 'account',
    label: 'Moje konto',
    permission: [] as PermissionCode[], // Everyone has access
    icon: UserCircle,
    render: () => null, // Set in SettingsDialog dynamically
  },
];
