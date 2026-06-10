/** LocalStorage utilities with JSON serialization and error handling. */

export function getItem<T = string>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return null
    return JSON.parse(raw) as T
  } catch {
    return localStorage.getItem(key) as unknown as T
  }
}

export function setItem(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // Storage full or unavailable
    console.warn(`Failed to write to localStorage: ${key}`)
  }
}

export function removeItem(key: string): void {
  localStorage.removeItem(key)
}
