import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import type { PermissionCode } from '@/types/permissions';

interface RequirePermissionProps {
  children: React.ReactNode;
  permission?: PermissionCode;
  permissions?: PermissionCode[];
  requireAll?: boolean;
}

export function RequirePermission({
  children,
  permission,
  permissions,
  requireAll = false,
}: RequirePermissionProps) {
  const { hasPermission, hasAnyPermission } = useAuthStore();

  if (permission) {
    if (!hasPermission(permission)) {
      return <Navigate to="/forbidden" replace />;
    }
  } else if (permissions && permissions.length > 0) {
    if (requireAll) {
      const hasAll = permissions.every((p) => hasPermission(p));
      if (!hasAll) {
        return <Navigate to="/forbidden" replace />;
      }
    } else {
      if (!hasAnyPermission(permissions)) {
        return <Navigate to="/forbidden" replace />;
      }
    }
  }

  return children;
}
