import { createRouter, createWebHistory } from 'vue-router'
import { watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/quotes',
      name: 'quotes',
      component: () => import('@/views/QuotesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/pvt-portfolio',
      name: 'pvtPortfolio',
      component: () => import('@/views/PvtPortfolioView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/portfolio',
      name: 'portfolio',
      component: () => import('@/views/PublicPortfolioView.vue'),
    },
  ],
})

/** Resolves once Firebase has determined the initial auth state. */
function waitForAuth(): Promise<void> {
  const auth = useAuthStore()
  if (!auth.loading) return Promise.resolve()
  return new Promise((resolve) => {
    const stop = watch(
      () => auth.loading,
      (loading) => {
        if (!loading) {
          stop()
          resolve()
        }
      },
    )
  })
}

// Navigation guard
router.beforeEach(async (to) => {
  await waitForAuth()

  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login' }
  }
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'home' }
  }
})

export default router
