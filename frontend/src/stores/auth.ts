import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  signOut,
  onAuthStateChanged,
  getRedirectResult,
  signInWithRedirect,
  type User,
  signInWithPopup,
} from 'firebase/auth'
import { auth, googleProvider } from '@/firebase'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  const isLoggedIn = computed(() => user.value !== null)

  // Resolve any pending redirect result first, then start the auth listener.
  // This ensures getRedirectResult() is called before onAuthStateChanged fires
  // so the user object is populated synchronously on the return trip.
  getRedirectResult(auth)
    .then((result) => {
      if (result?.user) {
        user.value = result.user
      }
    })
    .catch((err: unknown) => {
      error.value = err instanceof Error ? err.message : 'Google sign-in failed.'
    })
    .finally(() => {
      // Start the persistent auth-state listener after redirect is resolved.
      onAuthStateChanged(auth, (firebaseUser) => {
        console.warn(`onAuthStateChanged`,firebaseUser?.displayName)
        user.value = firebaseUser
        loading.value = false
      })
    })

  /**
   * Kick off the Google OAuth 2.0 redirect flow.
   * The browser navigates away; on return, getRedirectResult() above
   * picks up the signed-in user automatically.
   */
  async function loginWithGoogle() {
    error.value = null
    try {
      await signInWithPopup(auth, googleProvider)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Google sign-in failed.'
      throw err
    }
  }

  async function logout() {
    await signOut(auth)
    user.value = null
  }

  return { user, loading, error, isLoggedIn, loginWithGoogle, logout }
})
