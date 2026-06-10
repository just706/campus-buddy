/** Auth-related type definitions — matches backend auth schemas. */

export interface RegisterRequest {
  username: string
  email: string
  password: string
  phone?: string
  university: string
  college?: string
  major?: string
  grade?: string
  nickname?: string
  gender?: string
}

export interface LoginRequest {
  login: string // email or username
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshRequest {
  refresh_token: string
}
