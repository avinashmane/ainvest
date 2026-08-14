<script setup lang="ts">
/**
 * StockTicker.vue
 * ---------------
 * Shows a stock price with absolute and percentage change relative to a
 * configurable period, with ▲/▼ directional indicators.
 *
 * Props
 * -----
 * ticker   — Yahoo Finance ticker symbol, e.g. "RELIANCE.NS"
 * period   — comparison window: '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '5y'
 *            Defaults to '1d' (uses previousClose from the quote endpoint).
 * compact  — if true, renders a smaller inline chip style instead of a card
 */

import { computed, toRef, ref } from 'vue'
import { useStockQuote, type Period } from '@/composables/useStockQuote'
import Select from 'primevue/select'

const props = withDefaults(defineProps<{
  ticker:   string
  period?:  Period
  compact?: boolean
}>(), {
  period:  '1d',
  compact: false,
})

const tickerRef = toRef(props, 'ticker')
const periodRef = ref<Period>(props.period)

const { data, loading, error } = useStockQuote(tickerRef, periodRef)

const PERIOD_OPTIONS: { label: string; value: Period }[] = [
  { label: '1D',  value: '1d'  },
  { label: '5D',  value: '5d'  },
  { label: '1M',  value: '1mo' },
  { label: '3M',  value: '3mo' },
  { label: '6M',  value: '6mo' },
  { label: '1Y',  value: '1y'  },
  { label: '5Y',  value: '5y'  },
]

// ── Derived display values ────────────────────────────────────────────────────

const isUp   = computed(() => (data.value?.change ?? 0) >= 0)
const isDown = computed(() => (data.value?.change ?? 0) <  0)

/** Formatted price, e.g. "$2,430.50" */
const priceStr = computed(() => {
  if (!data.value) return '—'
  const { lastPrice, currency } = data.value
  return formatPrice(lastPrice, currency)
})

/** Absolute change, e.g. "+$34.20" or "−$12.80" */
const changeStr = computed(() => {
  if (!data.value) return ''
  const { change, currency } = data.value
  const sign = change >= 0 ? '+' : '−'
  return `${sign}${formatPrice(Math.abs(change), currency)}`
})

/** Percentage change, e.g. "+1.43%" */
const pctStr = computed(() => {
  if (!data.value) return ''
  const { changePct } = data.value
  const sign = changePct >= 0 ? '+' : '−'
  return `${sign}${Math.abs(changePct).toFixed(2)}%`
})

/** Human-readable period label for the "vs …" subtitle */
const periodLabel = computed(() => {
  const map: Record<Period, string> = {
    '1d':  'prev close',
    '5d':  '5 days ago',
    '1mo': '1 month ago',
    '3mo': '3 months ago',
    '6mo': '6 months ago',
    '1y':  '1 year ago',
    '5y':  '5 years ago',
  }
  return map[periodRef.value] ?? periodRef.value
})

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatPrice(value: number, currency: string | null | undefined): string {
  const sym = currencySymbol(currency)
  return `${sym}${value.toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function currencySymbol(currency: string | null | undefined): string {
  const map: Record<string, string> = {
    INR: '$', USD: '$', EUR: '€', GBP: '£', JPY: '¥',
  }
  return currency ? (map[currency] ?? `${currency} `) : ''
}
</script>

<template>
  <!-- ── Compact chip variant ───────────────────────────────────────────────── -->
  <span
    v-if="compact"
    class="inline-flex items-center gap-1.5 font-mono text-sm"
    :title="`${data?.name ?? ticker} — vs ${periodLabel}`"
  >
    <!-- loading -->
    <span v-if="loading" class="text-slate-400 animate-pulse">{{ ticker }} …</span>

    <!-- error -->
    <span v-else-if="error" class="text-red-500 text-xs">{{ ticker }} ✕</span>

    <!-- data -->
    <template v-else-if="data">
      <span class="text-slate-700 font-semibold">{{ priceStr }}</span>

      <!-- up arrow -->
      <span v-if="isUp" class="text-emerald-600 flex items-center gap-0.5">
        <svg viewBox="0 0 10 10" class="w-3 h-3 fill-current" aria-hidden="true">
          <polygon points="5,1 9,9 1,9" />
        </svg>
        {{ changeStr }}
        <span class="text-slate-400 font-normal">({{ pctStr }})</span>
      </span>

      <!-- down arrow -->
      <span v-else-if="isDown" class="text-red-500 flex items-center gap-0.5">
        <svg viewBox="0 0 10 10" class="w-3 h-3 fill-current" aria-hidden="true">
          <polygon points="5,9 9,1 1,1" />
        </svg>
        {{ changeStr }}
        <span class="text-slate-400 font-normal">({{ pctStr }})</span>
      </span>

      <span v-else class="text-slate-400">{{ changeStr }} ({{ pctStr }})</span>
    </template>
  </span>

  <!-- ── Card variant ───────────────────────────────────────────────────────── -->
  <div
    v-else
    class="bg-white border border-slate-200 rounded-2xl px-5 py-4 min-w-[200px] select-none"
  >
    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="h-3 w-24 bg-slate-100 rounded animate-pulse mb-3" />
      <div class="h-7 w-32 bg-slate-100 rounded animate-pulse mb-2" />
      <div class="h-4 w-20 bg-slate-100 rounded animate-pulse" />
    </template>

    <!-- Error state -->
    <template v-else-if="error">
      <p class="text-xs font-medium text-slate-400 mb-1 uppercase tracking-wide">{{ ticker }}</p>
      <p class="text-xs text-red-500">{{ error }}</p>
    </template>

    <!-- Loaded data -->
    <template v-else-if="data">
      <!-- Header row: ticker + name -->
      <div class="flex items-start justify-between gap-2 mb-3">
        <div class="min-w-0">
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider leading-none mb-0.5">
            {{ data.ticker }}
          </p>
          <p
            v-if="data.name"
            class="text-sm font-medium text-slate-700 truncate max-w-[160px]"
            :title="data.name"
          >
            {{ data.name }}
          </p>
        </div>

        <!-- Period selector -->
        <Select
          v-model="periodRef"
          :options="PERIOD_OPTIONS"
          option-label="label"
          option-value="value"
          size="small"
          class="text-xs w-20 shrink-0"
        />
      </div>

      <!-- Price -->
      <p class="text-2xl font-bold tabular-nums text-slate-900 leading-tight mb-1">
        {{ priceStr }}
      </p>

      <!-- Change row -->
      <div class="flex items-center gap-1.5">

        <!-- ▲ Up indicator -->
        <template v-if="isUp">
          <span
            class="inline-flex items-center justify-center w-5 h-5 rounded-full
                   bg-emerald-50 text-emerald-600"
            aria-label="Up"
          >
            <svg viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current" aria-hidden="true">
              <polygon points="5,1 9,9 1,9" />
            </svg>
          </span>
          <span class="text-sm font-semibold text-emerald-600 tabular-nums">
            {{ changeStr }}
          </span>
          <span class="text-sm text-emerald-500 tabular-nums">({{ pctStr }})</span>
        </template>

        <!-- ▼ Down indicator -->
        <template v-else-if="isDown">
          <span
            class="inline-flex items-center justify-center w-5 h-5 rounded-full
                   bg-red-50 text-red-500"
            aria-label="Down"
          >
            <svg viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current" aria-hidden="true">
              <polygon points="5,9 9,1 1,1" />
            </svg>
          </span>
          <span class="text-sm font-semibold text-red-500 tabular-nums">
            {{ changeStr }}
          </span>
          <span class="text-sm text-red-400 tabular-nums">({{ pctStr }})</span>
        </template>

        <!-- Flat / zero -->
        <template v-else>
          <span class="text-sm font-semibold text-slate-400 tabular-nums">—</span>
        </template>

        <!-- vs period subtitle -->
        <span class="ml-auto text-xs text-slate-300 whitespace-nowrap">
          vs {{ periodLabel }}
        </span>
      </div>
    </template>
  </div>
</template>
