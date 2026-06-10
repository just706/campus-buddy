/**
 * Auth API — register, login, token refresh.
 */
import http from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, RefreshRequest } from '@/types'

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  return http.post('/auth/register', data)
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  return http.post('/auth/login', data)
}

export async function refreshToken(data: RefreshRequest): Promise<TokenResponse> {
  return http.post('/auth/refresh', data)
}
