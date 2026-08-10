import type { PermissionCode } from '@/types/permissions';
import { HomePage } from '@/pages/HomePage';
import { LoginPage } from '@/pages/LoginPage';

export interface RouteConfig {
  path: string;
  label: string;
  description?: string;
  element: React.ReactNode;
  requireAuth?: boolean;
  permissions?: PermissionCode[];
  requireAllPermissions?: boolean;
  children?: RouteConfig[];
}

export const routes: RouteConfig[] = [
  {
    path: '/login',
    label: 'Login',
    element: <LoginPage />,
    requireAuth: false,
  },
  {
    path: '/',
    label: 'Dashboard',
    element: <HomePage />,
    requireAuth: true,
  },
  {
    path: '/water-objects',
    label: 'Water Objects',
    element: <div>Water Objects Page (TODO)</div>,
    requireAuth: true,
    permissions: ['CAN_VIEW_ASSETS'],
  },
  {
    path: '/devices',
    label: 'Devices',
    element: <div>Devices Page (TODO)</div>,
    requireAuth: true,
    permissions: ['CAN_VIEW_ASSETS'],
  },
  {
    path: '/users',
    label: 'Users',
    element: <div>Users Page (TODO)</div>,
    requireAuth: true,
    permissions: ['CAN_MANAGE_USERS'],
  },
  {
    path: '/admin',
    label: 'Administration',
    element: <div>Admin Page (TODO)</div>,
    requireAuth: true,
    permissions: ['CAN_MANAGE_ORGANIZATIONS'],
  },
];
