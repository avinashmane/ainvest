<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Card from 'primevue/card'
import Divider from 'primevue/divider'
import ChartLineIcon from '@primeicons/vue/chart-line'
import ArrowsHIcon from '@primeicons/vue/arrows-h'
import TrophyIcon from '@primeicons/vue/trophy'
import SearchIcon from '@primeicons/vue/search'
import StockTicker from '@/components/StockTicker.vue'
import NavBar from '@/components/NavBar.vue'

const auth = useAuthStore()
const router = useRouter()

const quickLinks = [
  { label: 'Portfolio',    icon: ChartLineIcon, desc: 'View holdings & P&L',     href: '/portfolio',         color: 'text-blue-600',   internal: true },
  { label: 'Transactions', icon: ArrowsHIcon,   desc: 'Buy & sell stocks',       href: '/transactions', color: 'text-green-600',  internal: false },
  { label: 'Leaderboard',  icon: TrophyIcon,    desc: 'See how you rank',        href: '/leaderboard',        color: 'text-yellow-500', internal: false },
  { label: 'Quotes',       icon: SearchIcon,    desc: 'Live Yahoo Finance data', href: '/quotes',                                                       color: 'text-violet-600', internal: true  },
]

const summaryCards = ['Portfolio Value', 'Cash Balance', 'Total', 'Holdings']

// Demo tickers shown in the Holdings snapshot section
const demoTickers = [
  '^GSPC', '^IXIC', '^DJI', '^RUT',
  '^NSEI',    '^BSESN', '^FTSE', '^N225',
]
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">

    <NavBar />

    <!-- ── Main ──────────────────────────────────────── -->
    <main class="flex-1 max-w-3xl w-full mx-auto px-6 py-10">

      <!-- Welcome -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">
          Welcome back,
          <span class="text-blue-600">
            {{ (auth.user?.displayName || auth.user?.email || '').split(' ')[0] }}
          </span>!
        </h1>
        <p class="text-slate-400 text-xs mt-1">{{ auth.user?.email }}</p>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
        <Card v-for="card in summaryCards" :key="card" class="text-center">
          <template #content>
            <p class="text-xs text-slate-400 mb-1">{{ card }}</p>
            <p class="text-lg font-bold text-slate-800">—</p>
          </template>
        </Card>
      </div>

      <!-- Quick actions -->
      <h2 class="text-sm font-semibold mb-3 text-slate-700">Quick actions</h2>
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 mb-10">
        <template v-for="link in quickLinks" :key="link.label">
          <!-- Internal Vue router link -->
          <a
            v-if="link.internal"
            :href="link.href"
            @click.prevent="router.push(link.href)"
            class="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3
                   hover:shadow-md hover:border-blue-200 transition-all no-underline group cursor-pointer"
          >
            <component :is="link.icon" :class="['w-6 h-6 shrink-0', link.color]" />
            <div>
              <p class="font-medium text-slate-900 text-sm">{{ link.label }}</p>
              <p class="text-slate-400 text-xs">{{ link.desc }}</p>
            </div>
          </a>
          <!-- External link -->
          <a
            v-else
            :href="link.href"
            class="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3
                   hover:shadow-md hover:border-blue-200 transition-all no-underline group"
          >
            <component :is="link.icon" :class="['w-6 h-6 shrink-0', link.color]" />
            <div>
              <p class="font-medium text-slate-900 text-sm">{{ link.label }}</p>
              <p class="text-slate-400 text-xs">{{ link.desc }}</p>
            </div>
          </a>
        </template>
      </div>

      <Divider />

      <!-- Holdings snapshot -->
      <h2 class="text-sm font-semibold mb-3 text-slate-700">Holdings snapshot</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <StockTicker
          v-for="sym in demoTickers"
          :key="sym"
          :ticker="sym"
        />
      </div>

    </main>

    <!-- ── Footer ────────────────────────────────────── -->
    <footer class="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
      Made with IBM Bob
    </footer>
  </div>
</template>
