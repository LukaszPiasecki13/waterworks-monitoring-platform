/* Auth endpoint — /auth/user */
export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  status: string;
  organization_id: string | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}
