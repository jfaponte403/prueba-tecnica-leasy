import { apiClient } from '../API/ApiClient.ts'

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface AuthUser {
  id: string
  email: string
  display_name: string
}

export const authService = {
  login(credentials: LoginCredentials): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>('/auth/login', credentials)
  },

  me(): Promise<AuthUser> {
    return apiClient.get<AuthUser>('/auth/me')
  },
}
