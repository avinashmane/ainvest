<script setup lang="ts">
/**
 * StockQuoteCard.vue
 * ------------------
 * Full-detail Yahoo Finance quote card.
 *
 * Props
 * -----
 * ticker     — Yahoo Finance symbol, e.g. "RELIANCE.NS"
 * period     — comparison window for the change badge (default '1d')
 * refreshMs  — auto-refresh interval in ms (default 30000 = 30 s; 0 = off)
 * compact    — show a slim single-row summary instead of the full card
 */

import { computed, ref, toRef } from 'vue'
import { useStockQuote, type Period } from '@/composables/useStockQuote'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

const props = withDefaults(defineProps<{
  ticker:    string
  period?:   Period
  refreshMs?: number
  compact?:  boolean
}>(), {
  period:    '1d',
  refreshMs: 30_000,
  compact:   false,
})

const tickerRef    = toRef(props, 'ticker')
const periodRef    = ref<Period>(props.period)
const refreshMsRef = toRef(props, 'refreshMs')

const { data, loading, error, reload } = useStockQuote(tickerRef, periodRef, refreshMsRef)

// ── Period picker ─────────────────────────────────────────────────────────────

const PERIOD_OPTIONS: { label: string; value: Period }[] = [
  { label: '1D',  value: '1d'  },
  { label: '5D',  value: '5d'  },
  { label: '1M',  value: '1mo' },
  { label: '3M',  value: '3mo' },
  { label: '6M',  value: '6mo' },
  { label: '1Y',  value: '1y'  },
  { label: '5Y',  value: '5y'  },
]

// ── Direction helpers ─────────────────────────────────────────────────────────

const isUp   = computed(() => (data.value?.change ?? 0) >= 0)
const isDown = computed(() => (data.value?.change ?? 0) <  0)

// ── Recommendation badge ──────────────────────────────────────────────────────

const recSeverity = computed((): 'success' | 'warn' | 'danger' | 'secondary' => {
  const k = data.value?.recommendationKey?.toLowerCase() ?? ''
  if (k.includes('buy') || k === 'strong_buy') return 'success'
  if (k.includes('sell'))                       return 'danger'
  if (k === 'hold')                             return 'warn'
  return 'secondary'
})

const recLabel = computed(() => {
  const k = data.value?.recommendationKey ?? ''
  return k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
})

// ── 52-week fill percentage for the range bar ─────────────────────────────────

const rangeBarPct = computed(() => {
  const d = data.value
  if (!d?.fiftyTwoWeekHigh || !d?.fiftyTwoWeekLow) return null
  const range = d.fiftyTwoWeekHigh - d.fiftyTwoWeekLow
  if (range === 0) return 50
  return Math.round(((d.lastPrice - d.fiftyTwoWeekLow) / range) * 100)
})

// ── Number formatters ─────────────────────────────────────────────────────────

function fPrice(v: number | null | undefined, currency: string | null | undefined): string {
  if (v == null) return '—'
  const sym = currencySymbol(currency)
  return `${sym}${v.toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function fNum(v: number | null | undefined, decimals = 2): string {
  if (v == null) return '—'
  return v.toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function fPct(v: number | null | undefined): string {
  if (v == null) return '—'
  return `${(v * 100).toFixed(2)}%`
}

function fLarge(v: number | null | undefined, currency: string | null | undefined): string {
  if (v == null) return '—'
  const sym = currencySymbol(currency)
  if (v >= 1e12) return `${sym}${(v / 1e12).toFixed(2)}T`
  if (v >= 1e9)  return `${sym}${(v / 1e9).toFixed(2)}B`
  if (v >= 1e7)  return `${sym}${(v / 1e7).toFixed(2)}Cr`
  if (v >= 1e5)  return `${sym}${(v / 1e5).toFixed(2)}L`
  return `${sym}${v.toLocaleString(import.meta.env.VITE_APP_LOCALE)}`
}

function fVolume(v: number | null | undefined): string {
  if (v == null) return '—'
  if (v >= 1e7) return `${(v / 1e7).toFixed(2)}Cr`
  if (v >= 1e5) return `${(v / 1e5).toFixed(2)}L`
  return v.toLocaleString(import.meta.env.VITE_APP_LOCALE)
}

function currencySymbol(c: string | null | undefined): string {
  const m: Record<string, string> = {
    INR: '$', USD: '$', EUR: '€', GBP: '£', JPY: '¥',
  }
  return c ? (m[c] ?? `${c} `) : ''
}

const priceStr  = computed(() => fPrice(data.value?.lastPrice, data.value?.currency))
const changeStr = computed(() => {
  const d = data.value
  if (!d) return ''
  const sign = d.change >= 0 ? '+' : '−'
  return `${sign}${fPrice(Math.abs(d.change), d.currency)}`
})
const pctStr = computed(() => {
  const d = data.value
  if (!d) return ''
  const sign = d.changePct >= 0 ? '+' : '−'
  return `${sign}${Math.abs(d.changePct).toFixed(2)}%`
})

const lastUpdated = computed(() => {
  if (!data.value) return ''
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
})
</script>

<template>

  <!-- ── Compact row variant ────────────────────────────────────────────────── -->
  <span
    v-if="compact"
    class="inline-flex items-center gap-2 font-mono text-sm"
    :title="data?.name ?? ticker"
  >
    <span v-if="loading" class="text-slate-400 animate-pulse">{{ ticker }} …</span>
    <span v-else-if="error" class="text-red-500 text-xs">{{ ticker }} ✕</span>
    <template v-else-if="data">
      <span class="text-slate-500 font-medium text-xs uppercase">{{ data.ticker }}</span>
      <span class="text-slate-900 font-bold">{{ priceStr }}</span>
      <span :class="isUp ? 'text-emerald-600' : isDown ? 'text-red-500' : 'text-slate-400'"
            class="flex items-center gap-0.5 text-xs">
        <svg v-if="isUp"   viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current"><polygon points="5,1 9,9 1,9"/></svg>
        <svg v-else-if="isDown" viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current"><polygon points="5,9 9,1 1,1"/></svg>
        {{ changeStr }} ({{ pctStr }})
      </span>
    </template>
  </span>

  <!-- ── Full card variant ──────────────────────────────────────────────────── -->
  <div
    v-else
    class="bg-white border border-slate-200 rounded-2xl overflow-hidden select-none"
  >

    <!-- Loading skeleton -->
    <template v-if="loading && !data">
      <div class="p-5 space-y-3">
        <div class="h-3 w-28 bg-slate-100 rounded animate-pulse" />
        <div class="h-8 w-40 bg-slate-100 rounded animate-pulse" />
        <div class="h-4 w-24 bg-slate-100 rounded animate-pulse" />
        <div class="h-px w-full bg-slate-100 my-2" />
        <div class="grid grid-cols-2 gap-3">
          <div v-for="i in 8" :key="i" class="h-10 bg-slate-50 rounded animate-pulse" />
        </div>
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="error">
      <div class="p-5">
        <p class="text-xs font-semibold text-slate-400 uppercase mb-1">{{ ticker }}</p>
        <p class="text-sm text-red-500">{{ error }}</p>
        <button
          class="mt-3 text-xs text-blue-600 underline"
          @click="reload"
        >Retry</button>
      </div>
    </template>

    <template v-else-if="data">

      <!-- ── Header ──────────────────────────────────────────────────────────── -->
      <div class="px-5 pt-5 pb-4">

        <!-- Ticker + exchange row -->
        <div class="flex items-start justify-between gap-2 mb-1">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">
                {{ data.ticker }}
              </span>
              <span
                v-if="data.exchange"
                class="text-[10px] font-medium bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded"
              >{{ data.exchange }}</span>
              <span
                v-if="data.sector"
                class="text-[10px] font-medium bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded"
              >{{ data.sector }}</span>
            </div>
            <p class="text-sm font-semibold text-slate-800 truncate mt-0.5" :title="data.longName ?? data.name ?? ''">
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

        <!-- Price + change -->
        <div class="flex items-end gap-3 mt-3">
          <p class="text-3xl font-bold tabular-nums text-slate-900 leading-none">
            {{ priceStr }}
          </p>

          <div class="flex items-center gap-1.5 mb-0.5">
            <!-- up -->
            <template v-if="isUp">
              <span class="flex items-center justify-center w-5 h-5 rounded-full bg-emerald-50 text-emerald-600">
                <svg viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current"><polygon points="5,1 9,9 1,9"/></svg>
              </span>
              <span class="text-sm font-semibold text-emerald-600 tabular-nums">{{ changeStr }}</span>
              <span class="text-sm text-emerald-500 tabular-nums">({{ pctStr }})</span>
            </template>
            <!-- down -->
            <template v-else-if="isDown">
              <span class="flex items-center justify-center w-5 h-5 rounded-full bg-red-50 text-red-500">
                <svg viewBox="0 0 10 10" class="w-2.5 h-2.5 fill-current"><polygon points="5,9 9,1 1,1"/></svg>
              </span>
              <span class="text-sm font-semibold text-red-500 tabular-nums">{{ changeStr }}</span>
              <span class="text-sm text-red-400 tabular-nums">({{ pctStr }})</span>
            </template>
            <template v-else>
              <span class="text-sm font-semibold text-slate-400">—</span>
            </template>
          </div>
        </div>

        <!-- Last updated + refresh indicator -->
        <div class="flex items-center gap-2 mt-1.5">
          <span
            v-if="loading"
            class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"
            title="Refreshing…"
          />
          <span v-else class="w-1.5 h-1.5 rounded-full bg-emerald-400" title="Live" />
          <span class="text-[10px] text-slate-400">
            {{ loading ? 'Refreshing…' : `Updated ${lastUpdated}` }}
            <template v-if="refreshMs > 0"> · auto-refresh {{ refreshMs / 1000 }}s</template>
          </span>
        </div>
      </div>

      <!-- ── Day range bar ────────────────────────────────────────────────────── -->
      <div class="px-5 pb-4">
        <div class="flex justify-between text-[10px] text-slate-400 mb-1">
          <span>Day Low  {{ fPrice(data.dayLow, data.currency) }}</span>
          <span>Day High {{ fPrice(data.dayHigh, data.currency) }}</span>
        </div>
        <div class="relative h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            v-if="data.dayLow != null && data.dayHigh != null && data.dayHigh !== data.dayLow"
            class="absolute top-0 left-0 h-full bg-blue-400 rounded-full"
            :style="{
              width: `${((data.lastPrice - data.dayLow!) / (data.dayHigh! - data.dayLow!)) * 100}%`
            }"
          />
        </div>
      </div>

      <!-- ── Divider ──────────────────────────────────────────────────────────── -->
      <div class="h-px bg-slate-100 mx-5 mb-4" />

      <!-- ── Stat grid ────────────────────────────────────────────────────────── -->
      <div class="px-5 pb-4 grid grid-cols-2 gap-x-6 gap-y-3.5">

        <!-- Open -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Open</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.open, data.currency) }}</p>
        </div>

        <!-- Prev Close -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Prev Close</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.previousClose, data.currency) }}</p>
        </div>

        <!-- Volume -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Volume</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fVolume(data.regularMarketVolume) }}</p>
        </div>

        <!-- Market Cap -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Mkt Cap</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fLarge(data.marketCap, data.currency) }}</p>
        </div>

        <!-- 52-week High -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">52W High</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.fiftyTwoWeekHigh, data.currency) }}</p>
        </div>

        <!-- 52-week Low -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">52W Low</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.fiftyTwoWeekLow, data.currency) }}</p>
        </div>

        <!-- 52-week range bar (full width) -->
        <div class="col-span-2" v-if="rangeBarPct != null">
          <div class="flex justify-between text-[10px] text-slate-400 mb-1">
            <span>52W Range</span>
            <span>{{ rangeBarPct }}% from low</span>
          </div>
          <div class="relative h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              class="absolute top-0 left-0 h-full bg-violet-400 rounded-full"
              :style="{ width: `${rangeBarPct}%` }"
            />
          </div>
        </div>

        <!-- 50D MA -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">50D Avg</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.fiftyDayAverage, data.currency) }}</p>
        </div>

        <!-- 200D MA -->
        <div>
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">200D Avg</p>
          <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.twoHundredDayAverage, data.currency) }}</p>
        </div>
      </div>

      <!-- ── Fundamentals ─────────────────────────────────────────────────────── -->
      <div class="mx-5 mb-4">
        <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-2">Fundamentals</p>
        <div class="grid grid-cols-2 gap-x-6 gap-y-3.5">

          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">P/E (TTM)</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fNum(data.trailingPE) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Fwd P/E</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fNum(data.forwardPE) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">P/B</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fNum(data.priceToBook) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Beta</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fNum(data.beta) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">EPS (TTM)</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.trailingEps, data.currency) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Fwd EPS</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.forwardEps, data.currency) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Div Yield</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPct(data.dividendYield) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Div Rate</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPrice(data.dividendRate, data.currency) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Gross Margin</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPct(data.grossMargins) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Net Margin</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPct(data.profitMargins) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">ROE</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fPct(data.returnOnEquity) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Shares Out</p>
            <p class="text-sm font-medium text-slate-800 tabular-nums">{{ fLarge(data.sharesOutstanding, null) }}</p>
          </div>
        </div>
      </div>

      <!-- ── Analyst targets ──────────────────────────────────────────────────── -->
      <div
        v-if="data.targetMeanPrice != null || data.recommendationKey"
        class="mx-5 mb-4"
      >
        <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-2">Analyst Consensus</p>
        <div class="flex items-center gap-3 flex-wrap mb-3">
          <Tag
            v-if="data.recommendationKey"
            :severity="recSeverity"
            :value="recLabel"
            class="text-xs"
          />
          <span v-if="data.numberOfAnalystOpinions" class="text-xs text-slate-400">
            {{ data.numberOfAnalystOpinions }} analysts
          </span>
        </div>

        <!-- Price target bar -->
        <div
          v-if="data.targetLowPrice != null && data.targetHighPrice != null && data.targetMeanPrice != null"
        >
          <div class="flex justify-between text-[10px] text-slate-400 mb-1">
            <span>Low {{ fPrice(data.targetLowPrice, data.currency) }}</span>
            <span>Mean {{ fPrice(data.targetMeanPrice, data.currency) }}</span>
            <span>High {{ fPrice(data.targetHighPrice, data.currency) }}</span>
          </div>
          <div class="relative h-2 bg-slate-100 rounded-full overflow-hidden">
            <!-- Mean marker -->
            <div
              class="absolute top-0 h-full w-0.5 bg-blue-500"
              :style="{
                left: `${((data.targetMeanPrice - data.targetLowPrice) / (data.targetHighPrice - data.targetLowPrice)) * 100}%`
              }"
            />
            <!-- Current price marker -->
            <div
              v-if="data.targetHighPrice !== data.targetLowPrice"
              class="absolute top-0.5 h-3 w-3 -mt-0.5 bg-slate-700 rounded-full border-2 border-white"
              :style="{
                left: `calc(${Math.max(0, Math.min(100, ((data.lastPrice - data.targetLowPrice) / (data.targetHighPrice - data.targetLowPrice)) * 100))}% - 6px)`
              }"
            />
          </div>
        </div>
      </div>

      <!-- ── Company info footer ──────────────────────────────────────────────── -->
      <div
        v-if="data.industry || data.country || data.website"
        class="px-5 py-3 border-t border-slate-100 flex items-center justify-between gap-2 flex-wrap"
      >
        <div class="flex items-center gap-2 text-xs text-slate-400 flex-wrap">
          <span v-if="data.industry">{{ data.industry }}</span>
          <span v-if="data.industry && data.country" class="text-slate-200">·</span>
          <span v-if="data.country">{{ data.country }}</span>
        </div>
        <a
          v-if="data.website"
          :href="data.website"
          target="_blank"
          rel="noopener noreferrer"
          class="text-xs text-blue-500 hover:underline"
        >
          {{ data.website.replace(/^https?:\/\//, '') }}
        </a>
      </div>

    </template>
  </div>
</template>
