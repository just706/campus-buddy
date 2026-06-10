/** User-related type definitions — matches backend user schemas. */

export interface UserResponse {
  id: number
  username: string
  email: string
  phone: string | null
  university: string
  college: string | null
  major: string | null
  grade: string | null
  nickname: string | null
  avatar: string | null
  gender: string | null
  bio: string | null
  tags: string[] | null
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface UserUpdateRequest {
  nickname?: string
  avatar?: string
  gender?: string
  bio?: string
  tags?: string[]
  phone?: string
  university?: string
  college?: string
  major?: string
  grade?: string
}
