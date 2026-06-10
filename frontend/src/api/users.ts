/**
 * Users API — profile management.
 */
import http from './client'
import type { UserResponse, UserUpdateRequest } from '@/types'

export async function getMe(): Promise<UserResponse> {
  return http.get('/users/me')
}

export async function updateMe(data: UserUpdateRequest): Promise<UserResponse> {
  return http.put('/users/me', data)
}

/** Get a user's public profile by ID. */
export async function getUserById(id: number): Promise<UserResponse> {
  return http.get(`/users/${id}`)
}
