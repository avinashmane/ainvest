<script setup lang="ts">
/**
 * QuotesView.vue
 * --------------
 * Full-page quotes explorer.  Users can search for any ticker or browse the
 * preset watchlist.  Each stock opens as a StockQuoteCard with real-time refresh.
 */

import { ref } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import NavBar from '@/components/NavBar.vue'
import StockQuoteCard from '@/components/StockQuoteCard.vue'

// ── Watchlist ─────────────────────────────────────────────────────────────────

const PRESET_TICKERS = [
  'RELIANCE.NS', 'TCS.NS',      'INFY.NS',     'HDFCBANK.NS',
  'WIPRO.NS',    'ITC.NS',      'SBIN.NS',      'BAJFINANCE.NS',
  'HINDUNILVR.NS', 'AAPL',      'MSFT',         'GOOGL',
  'AMZN',        'TSLA',        'META',          'NVDA',
]

const activeTickers = ref<string[]>(['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS'])
const refreshMs     = ref(30_000)

const REFRESH_OPTIONS = [
  { label: 'Off',  value: 0        },
  { label: '15s',  value: 15_000   },
  { label: '30s',  value: 30_000   },
  { label: '1m',   value: 60_000   },
  { label: '5m',   value: 300_000  },
]

// ── Ticker search / add ───────────────────────────────────────────────────────

const searchInput = ref('')
const searchError = ref('')

function addTicker() {
  const sym = searchInput.value.trim().toUpperCase()
  if (!sym) return
  if (activeTickers.value.includes(sym)) {
    searchError.value = `${sym} is already in the list`
    return
  }
  activeTickers.value.unshift(sym)
  searchInput.value = ''
  searchError.value = ''
}

function removeTicker(sym: string) {
  activeTickers.value = activeTickers.value.filter(t => t !== sym)
}

function togglePreset(sym: string) {
  if (activeTickers.value.includes(sym)) {
    removeTicker(sym)
  } else {
    activeTickers.value.unshift(sym)
  }
}

</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">

    <NavBar />

    <!-- ── Main ─────────────────────────────────────────────────────────────── -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-6 py-8">

      <!-- Controls row -->
      <div class="flex flex-col sm:flex-row gap-3 mb-6 items-start sm:items-center">

        <!-- Ticker search -->
        <form class="flex gap-2 flex-1" @submit.prevent="addTicker">
          <InputText
            v-model="searchInput"
            placeholder="Add ticker, e.g. WIPRO.NS"
            size="small"
            class="flex-1 max-w-xs"
          />
          <Button type="submit" label="Add" size="small" />
        </form>
        <p v-if="searchError" class="text-xs text-red-500">{{ searchError }}</p>

        <!-- Auto-refresh selector -->
        <div class="flex items-center gap-2 text-sm text-slate-600 shrink-0">
          <span class="text-xs text-slate-400">Auto-refresh:</span>
          <div class="flex gap-1">
            <button
              v-for="opt in REFRESH_OPTIONS"
              :key="opt.value"
              :class="[
                'px-2 py-0.5 rounded text-xs border transition-colors',
                refreshMs === opt.value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-slate-500 border-slate-200 hover:border-blue-300'
              ]"
              @click="refreshMs = opt.value"
            >{{ opt.label }}</button>
          </div>
        </div>
      </div>

      <!-- Preset chips -->
      <div class="flex flex-wrap gap-2 mb-6">
        <button
          v-for="sym in PRESET_TICKERS"
          :key="sym"
          :class="[
            'px-2.5 py-1 rounded-full text-xs font-medium border transition-colors',
            activeTickers.includes(sym)
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-slate-500 border-slate-200 hover:border-blue-300 hover:text-blue-600'
          ]"
          @click="togglePreset(sym)"
        >{{ sym }}</button>
      </div>

      <!-- Cards grid -->
      <div v-if="activeTickers.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        <div v-for="sym in activeTickers" :key="sym" class="relative">
          <StockQuoteCard
            :ticker="sym"
            :refresh-ms="refreshMs"
          />
          <button
            class="absolute top-3 right-16 text-slate-300 hover:text-red-500 text-xs transition-colors"
            title="Remove"
            @click="removeTicker(sym)"
          >✕</button>
        </div>
      </div>

      <div v-else class="text-center py-20 text-slate-400 text-sm">
        Add a ticker above or click a preset chip to get started.
      </div>

    </main>

    <!-- ── Footer ───────────────────────────────────────────────────────────── -->
    <footer class="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
      Made with IBM Bob
    </footer>
  </div>
</template>
