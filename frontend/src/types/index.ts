export interface User {
  id: string
  organization_id: string | null
  username: string
  email: string
  first_name: string
  last_name: string
  status: string
  is_active: boolean
}

export interface LoginResponse {
  access: string
  refresh: string
}
