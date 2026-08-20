/* Auth endpoint — /auth/user */
export interface AuthUser {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}
