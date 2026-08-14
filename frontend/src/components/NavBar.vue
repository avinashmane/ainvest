<script setup lang="ts">
/**
 * NavBar.vue
 * ----------
 * Application-wide top navigation bar.
 *
 * Features
 * --------
 * • Logo / brand with link to /home
 * • Horizontal nav links (desktop) with active-route highlight
 * • Hamburger menu that expands a mobile drawer on small screens
 * • User avatar + display name (hidden on mobile)
 * • Sign-out button
 * • Shows a "Sign in" button instead when the user is not authenticated
 *   (useful if NavBar is ever rendered on a public page)
 */

import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import BarsIcon    from '@primeicons/vue/bars'
import TimesIcon   from '@primeicons/vue/times'
import SignOutIcon from '@primeicons/vue/sign-out'
import SignInIcon  from '@primeicons/vue/sign-in'
import HomeIcon      from '@primeicons/vue/home'
import ChartLineIcon from '@primeicons/vue/chart-line'
import ArrowsHIcon   from '@primeicons/vue/arrows-h'
import TrophyIcon    from '@primeicons/vue/trophy'
import SearchIcon    from '@primeicons/vue/search'
import BriefcaseIcon from '@primeicons/vue/briefcase'

const auth   = useAuthStore()
const router = useRouter()
const route  = useRoute()

// ── Navigation links ──────────────────────────────────────────────────────────

interface NavLink {
  label:    string
  to:       string
  icon:     object
  external: boolean
}

const NAV_LINKS: NavLink[] = [
  { label: 'Home',         to: '/home',           icon: HomeIcon,       external: false },
  { label: 'Quotes',       to: '/quotes',         icon: SearchIcon,     external: false },
  { label: 'Portfolio',    to: '/portfolio',      icon: BriefcaseIcon,  external: false },
  { label: 'My Portfolio', to: '/pvt-portfolio',  icon: BriefcaseIcon,  external: false },
]

function isActive(link: NavLink): boolean {
  if (link.external) return false
  return route.path === link.to || route.path.startsWith(link.to + '/')
}

function navigate(link: NavLink) {
  mobileOpen.value = false
  if (link.external) {
    window.location.href = link.to
  } else {
    router.push(link.to)
  }
}

// ── Auth actions ──────────────────────────────────────────────────────────────

const signingOut = ref(false)

async function handleSignOut() {
  signingOut.value = true
  mobileOpen.value = false
  try {
    await auth.logout()
    router.push('/login')
  } finally {
    signingOut.value = false
  }
}

function handleSignIn() {
  mobileOpen.value = false
  router.push('/login')
}

// ── Mobile drawer ─────────────────────────────────────────────────────────────

const mobileOpen = ref(false)

const userInitial = computed(() => {
  const name = auth.user?.displayName || auth.user?.email || ''
  return name.charAt(0).toUpperCase()
})
</script>

<template>
  <!-- ── Top bar ─────────────────────────────────────────────────────────────── -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-4">

      <!-- Logo / brand -->
      <a
        href="/home"
        class="flex items-center gap-2 shrink-0 no-underline"
        @click.prevent="router.push('/home')"
      >
        <span class="text-xl leading-none select-none">📈</span>
        <span class="font-bold text-base tracking-tight text-slate-900">AInvest</span>
      </a>

      <!-- ── Desktop nav links ─────────────────────────────────────────────── -->
      <nav class="hidden sm:flex items-center gap-0.5 ml-2 flex-1">
        <template v-for="link in NAV_LINKS" :key="link.label">
          <button
            :class="[
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              isActive(link)
                ? 'bg-blue-50 text-blue-600'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            ]"
            @click="navigate(link)"
          >
            <component :is="link.icon" class="w-3.5 h-3.5 shrink-0" />
            {{ link.label }}
            <span
              v-if="link.external"
              class="text-[9px] text-slate-400 -ml-0.5"
              aria-hidden="true"
            >↗</span>
          </button>
        </template>
      </nav>

      <!-- ── Spacer (mobile) ───────────────────────────────────────────────── -->
      <div class="flex-1 sm:hidden" />

      <!-- ── Right side: user + sign out ──────────────────────────────────── -->
      <div class="hidden sm:flex items-center gap-3 shrink-0">
        <template v-if="auth.isLoggedIn">
          <!-- Avatar + name -->
          <div class="flex items-center gap-2">
            <Avatar
              v-if="auth.user?.photoURL"
              :image="auth.user.photoURL"
              shape="circle"
              class="!w-7 !h-7"
            />
            <Avatar
              v-else
              :label="userInitial"
              shape="circle"
              class="!w-7 !h-7 !text-xs !bg-blue-100 !text-blue-700"
            />
            <span class="text-sm text-slate-700 max-w-[140px] truncate hidden md:block">
              {{ auth.user?.displayName || auth.user?.email }}
            </span>
          </div>

          <!-- Sign out -->
          <Button
            severity="secondary"
            text
            size="small"
            :loading="signingOut"
            class="!px-2 !py-1"
            @click="handleSignOut"
          >
            <template #default>
              <SignOutIcon class="w-3.5 h-3.5" />
              <span class="ml-1.5 text-xs hidden md:inline">Sign out</span>
            </template>
          </Button>
        </template>

        <!-- Not logged in -->
        <template v-else>
          <Button
            severity="primary"
            size="small"
            @click="handleSignIn"
          >
            <template #default>
              <SignInIcon class="w-3.5 h-3.5 mr-1.5" />
              Sign in
            </template>
          </Button>
        </template>
      </div>

      <!-- ── Mobile hamburger ──────────────────────────────────────────────── -->
      <button
        class="sm:hidden flex items-center justify-center w-8 h-8 rounded-lg
               text-slate-500 hover:bg-slate-100 transition-colors"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
        @click="mobileOpen = !mobileOpen"
      >
        <TimesIcon v-if="mobileOpen" class="w-4 h-4" />
        <BarsIcon  v-else            class="w-4 h-4" />
      </button>
    </div>

    <!-- ── Mobile drawer ───────────────────────────────────────────────────── -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div
        v-if="mobileOpen"
        class="sm:hidden border-t border-slate-100 bg-white"
      >
        <!-- User info strip -->
        <div
          v-if="auth.isLoggedIn"
          class="flex items-center gap-3 px-4 py-3 border-b border-slate-100"
        >
          <Avatar
            v-if="auth.user?.photoURL"
            :image="auth.user.photoURL"
            shape="circle"
            class="!w-8 !h-8 shrink-0"
          />
          <Avatar
            v-else
            :label="userInitial"
            shape="circle"
            class="!w-8 !h-8 shrink-0 !text-xs !bg-blue-100 !text-blue-700"
          />
          <div class="min-w-0">
            <p class="text-sm font-medium text-slate-900 truncate">
              {{ auth.user?.displayName || auth.user?.email }}
            </p>
            <p v-if="auth.user?.displayName" class="text-xs text-slate-400 truncate">
              {{ auth.user.email }}
            </p>
          </div>
        </div>

        <!-- Nav links -->
        <nav class="px-2 py-2">
          <button
            v-for="link in NAV_LINKS"
            :key="link.label"
            :class="[
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left',
              isActive(link)
                ? 'bg-blue-50 text-blue-600'
                : 'text-slate-700 hover:bg-slate-100'
            ]"
            @click="navigate(link)"
          >
            <component :is="link.icon" class="w-4 h-4 shrink-0" />
            <span>{{ link.label }}</span>
            <span v-if="link.external" class="ml-auto text-[10px] text-slate-400">↗</span>
          </button>
        </nav>

        <!-- Sign out / sign in -->
        <div class="px-2 pb-3 pt-1 border-t border-slate-100 mt-1">
          <button
            v-if="auth.isLoggedIn"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
                   font-medium text-red-600 hover:bg-red-50 transition-colors"
            :disabled="signingOut"
            @click="handleSignOut"
          >
            <SignOutIcon class="w-4 h-4 shrink-0" />
            {{ signingOut ? 'Signing out…' : 'Sign out' }}
          </button>
          <button
            v-else
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
                   font-medium text-blue-600 hover:bg-blue-50 transition-colors"
            @click="handleSignIn"
          >
            <SignInIcon class="w-4 h-4 shrink-0" />
            Sign in
          </button>
        </div>
      </div>
    </transition>
  </header>
</template>
