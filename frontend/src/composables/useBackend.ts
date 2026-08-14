/**
 * composables/useBackend.ts
 * -------------------------
 * Thin HTTP client for the FastAPI backend.
 *
 * Usage:
 *   import { useBackend } from '@/composables/useBackend'
 *   const { get } = useBackend()
 *   const data = await get<MyType>('/users/foo/pvt_pf')
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

export function useBackend() {
  async function get<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`)
    if (!res.ok) throw new Error(`Server error ${res.status}`)
    return res.json() as Promise<T>
  }

  return { get }
}
