<script setup lang="ts">
/**
 * PublicPortfolioView.vue
 * -----------------------
 * Displays the aggregated public portfolio — the net sum of all transactions
 * stored in the background, enriched with live prices.
 *
 * No authentication required.
 * Data source: GET /api/portfolio
 */

import { computed, ref } from 'vue'
import { usePublicPortfolio, type PublicHolding } from '@/composables/usePublicPortfolio'
import { fPrice, fSigned, fPct, fQty, gainClass } from '@/composables/useFormatters'
import NavBar from '@/components/NavBar.vue'
import PortfolioTreemap from '@/components/PortfolioTreemap.vue'
import PortfolioPie from '@/components/PortfolioPie.vue'

const REFRESH_OPTIONS = [
  { label: 'Off', value: 0       },
  { label: '30s', value: 30_000  },
  { label: '1m',  value: 60_000  },
  { label: '5m',  value: 300_000 },
]

const refreshMs = ref(60_000)
const { data, loading, error, reload } = usePublicPortfolio(refreshMs)

// ── Sort state ────────────────────────────────────────────────────────────────

type SortKey = keyof PublicHolding
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

const sortedRows = computed<PublicHolding[]>(() => {
  if (!data.value?.rows.length) return []
  return [...data.value.rows].sort((a, b) => {
    const av = a[sortKey.value]
    const bv = b[sortKey.value]
    const diff = typeof av === 'number' && typeof bv === 'number'
      ? av - bv
      : String(av ?? '').localeCompare(String(bv ?? ''))
    return sortDir.value === 'asc' ? diff : -diff
  })
})

// ── Summary shorthands
const s        = computed(() => data.value?.summary)
const currency = computed(() => data.value?.rows[0]?.currency ?? null)

// Last-refresh timestamp
const lastUpdated = ref('')
function stampNow() {
  const d = new Date()
  lastUpdated.value = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">

    <NavBar />

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">

      <!-- ── Page header ────────────────────────────────────────────────────── -->
      <div class="flex items-center justify-between gap-4 mb-6 flex-wrap">
        <div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight">Public Portfolio</h1>
          <p class="text-xs text-slate-400 mt-0.5">
            Net aggregation of all transactions · Live prices · 60-second server cache
          </p>
        </div>

        <div class="flex items-center gap-3 flex-wrap">
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

        <!-- Gain vs Cost bar -->
        <div class="col-span-2 bg-white rounded-2xl border border-slate-100 px-4 py-4 flex flex-col justify-between">
          <p class="text-[10px] text-slate-400 uppercase tracking-wide mb-2">Gain vs Cost</p>
          <div class="flex items-center gap-2">
            <span :class="['text-sm font-bold tabular-nums', gainClass(s.totalGainPct)]">
              {{ fPct(s.totalGainPct) }}
            </span>
          </div>
        </div>
      </div>

      <!-- ── Holdings table ─────────────────────────────────────────────────── -->
      <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-700">Holdings</h2>
          <span v-if="data" class="text-xs text-slate-400">{{ data.rows.length }} positions</span>
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
          No public holdings found.
        </div>

        <!-- Table -->
        <div v-else-if="sortedRows.length" class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="text-[10px] uppercase tracking-wider text-slate-400 border-b border-slate-100">
                <th
                  v-for="col in [
                    { key: 'Ticker',       label: 'Ticker'       },
                    { key: 'name',         label: 'Name'         },
                    { key: 'weight',       label: 'Weight %'     },
                    { key: 'Quantity',     label: 'Qty'          },
                    { key: 'Cost Basis',   label: 'Cost Basis'   },
                    { key: 'lastPrice',    label: 'Last Price'   },
                    { key: 'currentValue', label: 'Value'        },
                    { key: 'dayGain',      label: 'Day Gain $'   },
                    { key: 'dayGainPct',   label: 'Day Gain %'   },
                    { key: 'totalGain',    label: 'Total Gain $' },
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
                v-for="row in sortedRows"
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
                        class="h-full bg-blue-400 rounded-full"
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

                <!-- Day Gain $ -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGain)]">
                  {{ fSigned(row.dayGain, row.currency) }}
                </td>

                <!-- Day Gain % -->
                <td :class="['px-4 py-3 text-right tabular-nums font-medium whitespace-nowrap', gainClass(row.dayGainPct)]">
                  {{ fPct(row.dayGainPct) }}
                </td>

                <!-- Total Gain $ -->
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
                <td class="px-4 py-3 text-right tabular-nums text-blue-600">100%</td>
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

      </div>

    </main>

    <footer class="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
      Made with IBM Bob
    </footer>
  </div>
</template>
