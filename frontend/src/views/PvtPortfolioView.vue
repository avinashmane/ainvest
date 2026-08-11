<script setup lang="ts">
/**
 * PvtPortfolioView.vue
 * --------------------
 * Displays the user's private portfolio with live prices and gain metrics.
 *
 * Summary bar: Portfolio Value · Cost Basis · Day Gain (₹ + %) · Total Gain (₹ + %)
 * Holdings table: one row per holding, all gain columns coloured green/red.
 * "Ratio" toggle: aggregates rows by ticker and adds a portfolio-weight % column.
 * Auto-refreshes every 60 s (configurable).
 */

import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePvtPortfolio, type PvtHolding } from '@/composables/usePvtPortfolio'
import NavBar from '@/components/NavBar.vue'
import PortfolioTreemap from '@/components/PortfolioTreemap.vue'
import PortfolioPie from '@/components/PortfolioPie.vue'

const auth = useAuthStore()

const emailRef  = computed(() => auth.user?.email ?? null)
const refreshMs = ref(60_000)

const REFRESH_OPTIONS = [
  { label: 'Off', value: 0       },
  { label: '30s', value: 30_000  },
  { label: '1m',  value: 60_000  },
  { label: '5m',  value: 300_000 },
]

interface ColDef {
  key: string
  label: string
  class?: string
}

const cols = ref<ColDef[]>([
  { key: 'Ticker',       label: 'Ticker'                     },
  { key: 'name',         label: 'Name',  class: 'hidden md:block' },
  { key: 'weight',       label: 'Weight %'                   },
  { key: 'Quantity',     label: 'Qty'                        },
  { key: 'Cost Basis',   label: 'Cost Basis'                 },
  { key: 'lastPrice',    label: 'Last Price'                 },
  { key: 'currentValue', label: 'Value'                      },
  { key: 'dayGain',      label: 'Day Gain ₹'                 },
  { key: 'dayGainPct',   label: 'Day Gain %'                 },
  { key: 'totalGain',    label: 'Total Gain ₹'               },
  { key: 'totalGainPct', label: 'Total Gain %'               },
])

/** O(1) lookup map derived from cols — rebuilt only when cols changes. */
const colMap = computed(() =>
  new Map(cols.value.map(c => [c.key, c]))
)

/** Returns the value of `attr` for the column with the given `key`, or `''`. */
function getColAttr(key: string, attr: keyof ColDef): string {
  return colMap.value.get(key)?.[attr] ?? ''
}

const { data, loading, error, reload } = usePvtPortfolio(emailRef, refreshMs)

// ── Ratio / aggregate toggle ──────────────────────────────────────────────────

const showRatio = ref(false)

interface AggRow {
  Ticker: string
  name: string | null
  currency: string | null
  quoteType: string | null
  sector: string | null
  Quantity: number
  'Cost Basis': number
  lastPrice: number
  currentValue: number
  dayGain: number
  dayGainPct: number
  totalGain: number
  totalGainPct: number
  trailingPE: number | null
  marketCap: number | null
  /** portfolio weight % */
  weight: number
}

const aggregatedRows = computed<AggRow[]>(() => {
  if (!data.value?.rows.length) return []

  const totalValue = data.value.summary?.totalValue ?? 0
  const map = new Map<string, AggRow>()

  for (const row of data.value.rows) {
    const ticker = row.Ticker || row.Symbol || '—'
    const existing = map.get(ticker)

    const qty   = typeof row.Quantity      === 'number' ? row.Quantity      : parseFloat(String(row.Quantity))      || 0
    const cost  = typeof row['Cost Basis'] === 'number' ? row['Cost Basis'] : parseFloat(String(row['Cost Basis'])) || 0
    const cv    = typeof row.currentValue  === 'number' ? row.currentValue  : parseFloat(String(row.currentValue))  || 0
    const dg    = typeof row.dayGain       === 'number' ? row.dayGain       : parseFloat(String(row.dayGain))       || 0
    const tg    = typeof row.totalGain     === 'number' ? row.totalGain     : parseFloat(String(row.totalGain))     || 0
    const lp    = typeof row.lastPrice     === 'number' ? row.lastPrice     : parseFloat(String(row.lastPrice))     || 0

    if (existing) {
      existing.Quantity      += qty
      existing['Cost Basis'] += cost
      existing.currentValue  += cv
      existing.dayGain       += dg
      existing.totalGain     += tg
      // last price is the same for all lots of a ticker; keep first
    } else {
      map.set(ticker, {
        Ticker:         ticker,
        name:           row.name,
        currency:       row.currency,
        quoteType:      row.quoteType ?? null,
        sector:         row.sector   ?? null,
        Quantity:       qty,
        'Cost Basis':   cost,
        lastPrice:      lp,
        currentValue:   cv,
        dayGain:        dg,
        dayGainPct:     0,   // recalculated below
        totalGain:      tg,
        totalGainPct:   0,   // recalculated below
        trailingPE:     row.trailingPE ?? null,
        marketCap:      row.marketCap  ?? null,
        weight:         0,   // recalculated below
      })
    }
  }

  // Recalculate % columns and weight from aggregated totals
  for (const row of map.values()) {
    const prevClose = row.currentValue - row.dayGain
    row.dayGainPct  = prevClose !== 0 ? (row.dayGain  / prevClose)        * 100 : 0
    row.totalGainPct = row['Cost Basis'] !== 0 ? (row.totalGain / row['Cost Basis']) * 100 : 0
    row.weight      = totalValue !== 0 ? (row.currentValue / totalValue) * 100 : 0
  }

  return Array.from(map.values())
})

// ── Sort state ────────────────────────────────────────────────────────────────

type SortKey = keyof PvtHolding | 'weight'
const sortKey = ref<SortKey>('currentValue')
const sortDir = ref<'asc' | 'desc'>('desc')

function toggleSort(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

function sortRows<T>(rows: T[]): T[] {
  return [...rows].sort((a, b) => {
    const rec = a as Record<string, unknown>
    const av = rec[sortKey.value as string]
    const bv = (b as Record<string, unknown>)[sortKey.value as string]
    const diff = typeof av === 'number' && typeof bv === 'number'
      ? av - bv
      : String(av ?? '').localeCompare(String(bv ?? ''))
    return sortDir.value === 'asc' ? diff : -diff
  })
}

const sortedRows = computed(() => {
  if (showRatio.value) return sortRows(aggregatedRows.value)
  if (!data.value?.rows.length) return []
  return sortRows(data.value.rows)
})

// ── Formatters ────────────────────────────────────────────────────────────────

function fPrice(v: number | string | null | undefined, currency?: string | null): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (isNaN(n)) return '—'
  return `${currSym(currency)}${Math.abs(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function fSigned(v: number | string | null | undefined, currency?: string | null): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (isNaN(n)) return '—'
  const sign = n >= 0 ? '+' : '−'
  return `${sign}${currSym(currency)}${Math.abs(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function fPct(v: number | string | null | undefined): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (isNaN(n)) return '—'
  return `${n >= 0 ? '+' : '−'}${Math.abs(n).toFixed(2)}%`
}

function fQty(v: number | string | null | undefined): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (isNaN(n)) return '—'
  return n.toLocaleString('en-IN', { maximumFractionDigits: 4 })
}

function currSym(c?: string | null): string {
  const m: Record<string, string> = { INR: '₹', USD: '$', EUR: '€', GBP: '£', JPY: '¥' }
  return c ? (m[c] ?? `${c} `) : '₹'
}

function gainClass(v: number | string | null | undefined): string {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  if (isNaN(n)) return 'text-slate-400'
  return n >= 0 ? 'text-emerald-600' : 'text-red-500'
}

// Summary shorthands
const s        = computed(() => data.value?.summary)
const currency = computed(() => data.value?.rows[0]?.currency ?? null)

// Position count shown in header
const positionCount = computed(() =>
  showRatio.value ? aggregatedRows.value.length : (data.value?.rows?.length ?? 0)
)

// Last-refresh timestamp
const lastUpdated = ref('')
function stampNow() {
  const d = new Date()
  lastUpdated.value = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">

    <NavBar />

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">

      <!-- ── Page header ────────────────────────────────────────────────────── -->
      <div class="flex items-center justify-between gap-4 mb-6 flex-wrap">
        <div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight">Private Portfolio</h1>
          <p class="text-xs text-slate-400 mt-0.5">
            Live prices · 60-second server cache
          </p>
        </div>

        <div class="flex items-center gap-3 flex-wrap">
          <!-- Ratio toggle -->
          <button
            :class="[
              'px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors',
              showRatio
                ? 'bg-violet-600 text-white border-violet-600'
                : 'bg-white text-slate-600 border-slate-200 hover:border-violet-300'
            ]"
            @click="showRatio = !showRatio"
          >
            {{ showRatio ? '⊞ Ratio' : '⊞ Ratio' }}
          </button>

          <!-- Refresh buttons -->
          <div class="flex items-center gap-1.5">
            <span class="text-xs text-slate-400">Refresh:</span>
            <button
              v-for="opt in REFRESH_OPTIONS"
              :key="opt.value"
              :class="[
                'px-2 py-0.5 rounded text-xs border transition-colors',
                refreshMs === opt.value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-slate-500 border-slate-200 hover:border-blue-300'
              ]"
              @click="refreshMs = opt.value; reload(); stampNow()"
            >{{ opt.label }}</button>
          </div>

          <!-- Manual reload -->
          <button
            :disabled="loading"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200
                   bg-white text-xs text-slate-600 hover:border-blue-300 transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed"
            @click="reload(); stampNow()"
          >
            <span :class="loading ? 'animate-spin inline-block' : ''">↻</span>
            Reload
          </button>

          <!-- Live indicator -->
          <div class="flex items-center gap-1.5 text-[11px] text-slate-400">
            <span
              :class="loading
                ? 'w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse'
                : 'w-1.5 h-1.5 rounded-full bg-emerald-400'"
            />
            {{ loading ? 'Refreshing…' : lastUpdated ? `Updated ${lastUpdated}` : 'Live' }}
          </div>
        </div>
      </div>

      <!-- ── Error ──────────────────────────────────────────────────────────── -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-6 flex items-center gap-3">
        <span class="text-red-500 text-lg">⚠</span>
        <div>
          <p class="text-sm font-medium text-red-700">Failed to load portfolio</p>
          <p class="text-xs text-red-500 mt-0.5">{{ error }}</p>
        </div>
        <button class="ml-auto text-xs text-blue-600 underline" @click="reload">Retry</button>
      </div>

      <!-- ── Summary cards skeleton ─────────────────────────────────────────── -->
      <div v-if="loading && !data" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        <div v-for="i in 6" :key="i" class="bg-white rounded-2xl border border-slate-100 px-4 py-4 space-y-2">
          <div class="h-2.5 w-20 bg-slate-100 rounded animate-pulse" />
          <div class="h-6 w-24 bg-slate-100 rounded animate-pulse" />
          <div class="h-3 w-16 bg-slate-100 rounded animate-pulse" />
        </div>
      </div>

      <!-- ── Summary cards ──────────────────────────────────────────────────── -->
      <div
        v-else-if="s"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6"
      >
        <!-- Portfolio Value -->
        <div class="bg-white rounded-2xl border border-slate-100 px-4 py-4">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Portfolio Value</p>
          <p class="text-xl font-bold text-slate-900 tabular-nums">{{ fPrice(s.totalValue, currency) }}</p>
        </div>

        <!-- Cost Basis -->
        <div class="bg-white rounded-2xl border border-slate-100 px-4 py-4">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Cost Basis</p>
          <p class="text-xl font-bold text-slate-900 tabular-nums">{{ fPrice(s.totalCost, currency) }}</p>
        </div>

        <!-- Day Gain -->
        <div class="bg-white rounded-2xl border border-slate-100 px-4 py-4">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Day Gain</p>
          <p :class="['text-xl font-bold tabular-nums', gainClass(s.totalDayGain)]">
            {{ fSigned(s.totalDayGain, currency) }}
          </p>
          <p :class="['text-xs tabular-nums mt-0.5', gainClass(s.totalDayGainPct)]">
            {{ fPct(s.totalDayGainPct) }}
          </p>
        </div>

        <!-- Total Gain -->
        <div class="bg-white rounded-2xl border border-slate-100 px-4 py-4">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Total Gain</p>
          <p :class="['text-xl font-bold tabular-nums', gainClass(s.totalGain)]">
            {{ fSigned(s.totalGain, currency) }}
          </p>
          <p :class="['text-xs tabular-nums mt-0.5', gainClass(s.totalGainPct)]">
            {{ fPct(s.totalGainPct) }}
          </p>
        </div>

        <!-- Gain % bar -->
        <div class="col-span-2 bg-white rounded-2xl border border-slate-100 px-4 py-4 flex flex-col justify-between">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-2">Gain vs Cost</p>
          <div class="flex items-center gap-2">
            <!-- <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                :class="(s.totalGainPct ?? 0) >= 0 ? 'bg-emerald-400' : 'bg-red-400'"
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${Math.min(Math.abs(s.totalGainPct ?? 0), 100)}%` }"
              />
            </div> -->
            <span :class="['text-sm font-bold tabular-nums', gainClass(s.totalGainPct)]">
              {{ fPct(s.totalGainPct) }}
            </span>
          </div>
        </div>
      </div>

      <!-- ── Treemap (full width) ───────────────────────────────────────────── -->
      <div v-if="aggregatedRows.length" class="mb-4">
        <PortfolioTreemap
          :rows="aggregatedRows"
          :currency="currency"
        />
      </div>

      <!-- ── Pie (full width) ───────────────────────────────────────────────── -->
      <div v-if="aggregatedRows.length" class="mb-6">
        <PortfolioPie
          :rows="aggregatedRows"
          :currency="currency"
        />
      </div>

      <!-- ── Holdings table ─────────────────────────────────────────────────── -->
      <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-700">
            Holdings
            <span v-if="showRatio" class="ml-2 text-[10px] font-normal text-violet-500 uppercase tracking-wide">
              aggregated by ticker
            </span>
          </h2>
          <span v-if="data" class="text-xs text-slate-400">{{ positionCount }} positions</span>
        </div>

        <!-- Table skeleton -->
        <div v-if="loading && !data" class="divide-y divide-slate-50">
          <div v-for="i in 6" :key="i" class="flex gap-4 px-5 py-3">
            <div class="h-4 w-24 bg-slate-100 rounded animate-pulse" />
            <div class="h-4 w-16 bg-slate-100 rounded animate-pulse" />
            <div class="h-4 flex-1 bg-slate-50 rounded animate-pulse" />
          </div>
        </div>

        <!-- Empty state -->
        <div v-else-if="!data?.rows?.length && !error" class="px-5 py-12 text-center text-slate-400 text-sm">
          No holdings found. Link a Google Sheet in your profile to import positions.
        </div>

        <!-- ── RATIO view ─────────────────────────────────────────────────── -->
        <div v-else-if="showRatio && sortedRows.length" class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="text-[10px] uppercase tracking-wider text-slate-400 border-b border-slate-100">
                <th
                  v-for="col in cols"
                  :key="col.key"
                  :class="[
                    col.class || '',
                    'px-4 py-2.5 text-left font-medium whitespace-nowrap cursor-pointer hover:text-slate-600 select-none',
                    col.key === 'Ticker' ? 'sticky left-0 z-10 bg-white' : '',
                    col.key === 'name'   ? 'hidden sm:table-cell' : '',
                  ]"
                  @click="toggleSort(col.key as SortKey)"
                >
                  {{ col.label }}
                  <span class="ml-0.5 text-[9px]">
                    {{ sortKey === col.key ? (sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                  </span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr
                v-for="row in (sortedRows as AggRow[])"
                :key="row.Ticker"
                class="group hover:bg-slate-50 transition-colors"
              >
                <!-- Ticker -->
                <td class="sticky left-0 z-10 bg-white group-hover:bg-slate-50 transition-colors px-4 py-3 whitespace-nowrap">
                  <span class="font-mono text-xs font-semibold text-slate-700">{{ row.Ticker }}</span>
                </td>

                <!-- Name -->
                <td class="hidden sm:table-cell px-4 py-3 max-w-[180px]">
                  <span class="text-slate-600 text-xs truncate block" :title="row.name ?? ''">
                    {{ row.name || '—' }}
                  </span>
                </td>

                <!-- Weight bar -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2 min-w-[90px]">
                    <div class="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        class="h-full bg-violet-400 rounded-full"
                        :style="{ width: `${Math.min(row.weight, 100)}%` }"
                      />
                    </div>
                    <span class="text-xs tabular-nums text-slate-600 w-10 text-right">
                      {{ row.weight.toFixed(1) }}%
                    </span>
                  </div>
                </td>

                <!-- Qty -->
                <td class="px-4 py-3 text-right tabular-nums text-slate-700 whitespace-nowrap">
                  {{ fQty(row.Quantity) }}
                </td>

                <!-- Cost Basis -->
                <td class="px-4 py-3 text-right tabular-nums text-slate-600 whitespace-nowrap">
                  {{ fPrice(row['Cost Basis'], row.currency) }}
                </td>

                <!-- Last Price -->
                <td class="px-4 py-3 text-right tabular-nums font-medium text-slate-900 whitespace-nowrap">
                  {{ fPrice(row.lastPrice, row.currency) }}
                </td>

                <!-- Current Value -->
                <td class="px-4 py-3 text-right tabular-nums font-semibold text-slate-900 whitespace-nowrap">
                  {{ fPrice(row.currentValue, row.currency) }}
                </td>

                <!-- Day Gain ₹ -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGain)]">
                  {{ fSigned(row.dayGain, row.currency) }}
                </td>

                <!-- Day Gain % -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGainPct)]">
                  {{ fPct(row.dayGainPct) }}
                </td>

                <!-- Total Gain ₹ -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.totalGain)]">
                  {{ fSigned(row.totalGain, row.currency) }}
                </td>

                <!-- Total Gain % -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.totalGainPct)]">
                  {{ fPct(row.totalGainPct) }}
                </td>
              </tr>
            </tbody>

            <!-- Totals row -->
            <tfoot v-if="s" class="border-t-2 border-slate-200 bg-slate-50">
              <tr class="text-sm font-semibold">
                <td class="px-4 py-3 text-slate-500 text-xs uppercase tracking-wide" colspan="2">Totals</td>
                <td class="px-4 py-3 text-right tabular-nums text-violet-600">100%</td>
                <td class="px-4 py-3" />
                <td class="px-4 py-3 text-right tabular-nums text-slate-700">{{ fPrice(s.totalCost, currency) }}</td>
                <td class="px-4 py-3" />
                <td class="px-4 py-3 text-right tabular-nums text-slate-900">{{ fPrice(s.totalValue, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalDayGain)]">{{ fSigned(s.totalDayGain, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalDayGainPct)]">{{ fPct(s.totalDayGainPct) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalGain)]">{{ fSigned(s.totalGain, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalGainPct)]">{{ fPct(s.totalGainPct) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- ── DETAIL view (default) ──────────────────────────────────────── -->
        <div v-else-if="sortedRows.length" class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="text-[10px] uppercase tracking-wider text-slate-400 border-b border-slate-100">
                <th
                  v-for="col in [
                    { key: 'Ticker',       label: 'Ticker'       },
                    { key: 'name',         label: 'Name'         },
                    { key: 'Quantity',     label: 'Qty'          },
                    { key: 'Cost Basis',   label: 'Cost Basis'   },
                    { key: 'lastPrice',    label: 'Last Price'   },
                    { key: 'currentValue', label: 'Value'        },
                    { key: 'dayGain',      label: 'Day Gain ₹'   },
                    { key: 'dayGainPct',   label: 'Day Gain %'   },
                    { key: 'totalGain',    label: 'Total Gain ₹' },
                    { key: 'totalGainPct', label: 'Total Gain %' },
                  ]"
                  :key="col.key"
                  :class="[
                    'px-4 py-2.5 text-left font-medium whitespace-nowrap cursor-pointer hover:text-slate-600 select-none',
                    col.key === 'Ticker' ? 'sticky left-0 z-10 bg-white' : '',
                    col.key === 'name'   ? 'hidden sm:table-cell' : '',
                  ]"
                  @click="toggleSort(col.key as SortKey)"
                >
                  {{ col.label }}
                  <span class="ml-0.5 text-[9px]">
                    {{ sortKey === col.key ? (sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                  </span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr
                v-for="row in (sortedRows as PvtHolding[])"
                :key="`${row.Ticker}-${row['Account Number']}`"
                class="group hover:bg-slate-50 transition-colors"
              >
                <td class="sticky left-0 z-10 bg-white group-hover:bg-slate-50 transition-colors px-4 py-3 whitespace-nowrap">
                  <span class="font-mono text-xs font-semibold text-slate-700">
                    {{ row.Ticker || row.Symbol }}
                  </span>
                </td>
                <td class="hidden sm:table-cell px-4 py-3 max-w-[180px]">
                  <span class="text-slate-600 text-xs truncate block" :title="row.name ?? row.Description ?? ''">
                    {{ row.name || row.Description || '—' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right tabular-nums text-slate-700 whitespace-nowrap">{{ fQty(row.Quantity) }}</td>
                <td class="px-4 py-3 text-right tabular-nums text-slate-600 whitespace-nowrap">{{ fPrice(row['Cost Basis'], row.currency) }}</td>
                <td class="px-4 py-3 text-right tabular-nums font-medium text-slate-900 whitespace-nowrap">{{ fPrice(row.lastPrice, row.currency) }}</td>
                <td class="px-4 py-3 text-right tabular-nums font-semibold text-slate-900 whitespace-nowrap">{{ fPrice(row.currentValue, row.currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGain)]">{{ fSigned(row.dayGain, row.currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGainPct)]">{{ fPct(row.dayGainPct) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.totalGain)]">{{ fSigned(row.totalGain, row.currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.totalGainPct)]">{{ fPct(row.totalGainPct) }}</td>
              </tr>
            </tbody>

            <!-- Totals row -->
            <tfoot v-if="s" class="border-t-2 border-slate-200 bg-slate-50">
              <tr class="text-sm font-semibold">
                <td class="px-4 py-3 text-slate-500 text-xs uppercase tracking-wide" colspan="3">Totals</td>
                <td class="px-4 py-3 text-right tabular-nums text-slate-700">{{ fPrice(s.totalCost, currency) }}</td>
                <td class="px-4 py-3" />
                <td class="px-4 py-3 text-right tabular-nums text-slate-900">{{ fPrice(s.totalValue, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalDayGain)]">{{ fSigned(s.totalDayGain, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalDayGainPct)]">{{ fPct(s.totalDayGainPct) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalGain)]">{{ fSigned(s.totalGain, currency) }}</td>
                <td :class="['px-4 py-3 text-right tabular-nums', gainClass(s.totalGainPct)]">{{ fPct(s.totalGainPct) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

      </div>

    </main>

    <footer class="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
      Made with IBM Bob
    </footer>
  </div>
</template>
