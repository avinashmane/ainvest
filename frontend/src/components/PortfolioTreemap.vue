<script setup lang="ts">
/**
 * PortfolioTreemap.vue
 * --------------------
 * ECharts-powered treemap of portfolio holdings.
 *
 * Hierarchy:
 *   Level 1 — quoteType  (EQUITY, ETF, MUTUALFUND, …)
 *   Level 2 — sector     (Technology, Financials, …)
 *   Level 3 — tiles      (individual tickers)
 *
 * Tile colour is driven by a user-selectable metric:
 *   totalGainPct | dayGainPct | trailingPE | marketCap
 *
 * Click a tile to open the detail tooltip panel.
 *
 * Props:
 *   rows     — AggRow[] (aggregated by ticker)
 *   currency — display currency string (e.g. 'INR')
 */

import { computed, ref, watch } from 'vue'
import { fPrice, fSigned, fPct, fQty, fMc, gainClass, gainClassDark } from '@/composables/useFormatters'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { TreemapChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ComposeOption } from 'echarts/core'
import type { TreemapSeriesOption } from 'echarts/charts'
import type { TooltipComponentOption } from 'echarts/components'

use([TreemapChart, TooltipComponent, CanvasRenderer])

type EChartsOption = ComposeOption<TreemapSeriesOption | TooltipComponentOption>

// ── Prop types ────────────────────────────────────────────────────────────────

interface TileRow {
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
  weight: number
}

const props = defineProps<{
  rows: TileRow[]
  currency?: string | null
}>()

// ── Colour-metric selector ────────────────────────────────────────────────────

type ColourMetric = 'totalGainPct' | 'dayGainPct' | 'trailingPE' | 'marketCap'

const METRIC_OPTIONS: { value: ColourMetric; label: string }[] = [
  { value: 'totalGainPct', label: 'Total Gain %' },
  { value: 'dayGainPct',   label: 'Day Gain %'   },
  { value: 'trailingPE',   label: 'P/E Ratio'    },
  { value: 'marketCap',    label: 'Market Cap'   },
]

const colourMetric = ref<ColourMetric>('dayGainPct')

// ── Grouping label map ────────────────────────────────────────────────────────

const LABEL_QT: Record<string, string> = {
  EQUITY:     'Equities',
  ETF:        'ETFs',
  MUTUALFUND: 'Mutual Funds',
  INDEX:      'Indices',
  CURRENCY:   'Currencies',
  FUTURE:     'Futures',
  CASH:       'Cash',
  OPTION:     'Options',
}

function qtLabel(qt: string | null): string {
  return qt ? (LABEL_QT[qt.toUpperCase()] ?? qt) : 'Other'
}

// ── Colour scaling ────────────────────────────────────────────────────────────

const peRange = computed(() => {
  const vals = props.rows.map(r => r.trailingPE).filter((v): v is number => v != null && v > 0)
  return vals.length ? { min: Math.min(...vals), max: Math.max(...vals) } : null
})

const mcRange = computed(() => {
  const vals = props.rows.map(r => r.marketCap).filter((v): v is number => v != null && v > 0)
  return vals.length ? { min: Math.min(...vals), max: Math.max(...vals) } : null
})

function tileColor(row: TileRow): string {
  const m = colourMetric.value
  const val = m === 'totalGainPct' ? row.totalGainPct
            : m === 'dayGainPct'   ? row.dayGainPct
            : m === 'trailingPE'   ? row.trailingPE
            : row.marketCap

  if (val == null || val === 0) return '#334155'

  if (m === 'totalGainPct' || m === 'dayGainPct') {
    const intensity = Math.min(Math.abs(val) / 10, 1)
    if (val >= 0) return `rgb(${Math.round(30 - intensity * 10)},${Math.round(140 + intensity * 70)},${Math.round(60 - intensity * 20)})`
    else          return `rgb(${Math.round(180 + intensity * 55)},${Math.round(60 - intensity * 20)},${Math.round(60 - intensity * 20)})`
  }

  const range = m === 'trailingPE' ? peRange.value : mcRange.value
  if (!range || range.max === range.min) return '#2563eb'
  const t = (val - range.min) / (range.max - range.min)
  return `rgb(${Math.round(15 + t * 20)},${Math.round(40 + t * 60)},${Math.round(120 + t * 135)})`
}

function tileSubLabel(row: TileRow): string {
  const m = colourMetric.value
  const val = m === 'totalGainPct' ? row.totalGainPct
            : m === 'dayGainPct'   ? row.dayGainPct
            : m === 'trailingPE'   ? row.trailingPE
            : row.marketCap
  if (val == null) return ''
  if (m === 'totalGainPct' || m === 'dayGainPct') return fPct(val)
  if (m === 'trailingPE') return `PE ${val.toFixed(1)}`
  return fMc(val as number)
}

// ── Build ECharts series data ─────────────────────────────────────────────────

interface LeafData {
  name: string
  value: number
  itemStyle: { color: string }
  label: { formatter: string }
  // stash the full row for the tooltip panel
  row: TileRow
}

const seriesData = computed(() => {
  const rows = props.rows.filter(r => r.currentValue > 0)

  // Group: quoteType → sector → tickers
  const qtMap = new Map<string, Map<string, TileRow[]>>()
  for (const row of rows) {
    const qt  = qtLabel(row.quoteType)
    const sec = row.sector ?? 'Other'
    if (!qtMap.has(qt))  qtMap.set(qt, new Map())
    const secMap = qtMap.get(qt)!
    if (!secMap.has(sec)) secMap.set(sec, [])
    secMap.get(sec)!.push(row)
  }

  return Array.from(qtMap.entries()).map(([qt, secMap]) => ({
    name:  qt,
    value: Array.from(secMap.values()).flat().reduce((s, r) => s + r.currentValue, 0),
    children: Array.from(secMap.entries()).map(([sec, secRows]) => ({
      name:  sec,
      value: secRows.reduce((s, r) => s + r.currentValue, 0),
      children: secRows.map((row): LeafData => ({
        name:      row.Ticker,
        value:     row.currentValue,
        itemStyle: { color: tileColor(row) },
        label:     { formatter: `${row.Ticker}\n${tileSubLabel(row)}` },
        row,
      })),
    })),
  }))
})

// ── ECharts option ────────────────────────────────────────────────────────────

const option = computed<EChartsOption>(() => ({
  tooltip: { show: false },   // we use our own detail panel
  series: [{
    type: 'treemap',
    roam: false,
    nodeClick: false,          // we handle click ourselves
    width: '100%',
    height: '100%',
    squareRatio: 0.7,          // aspect ratio hint for squarify
    breadcrumb: {
      show: true,
      height: 26,
      top: 'top',
      itemStyle: { color: '#1e293b', textStyle: { color: '#94a3b8', fontSize: 11 } },
    },
    levels: [
      // Level 0 — quoteType bands
      {
        itemStyle: { borderColor: '#0f172a', borderWidth: 4, gapWidth: 4 },
        upperLabel: {
          show: true,
          height: 22,
          color: '#94a3b8',
          fontWeight: 700,
          fontSize: 11,
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          formatter: (p: { name: string }) => p.name.toUpperCase(),
        },
      },
      // Level 1 — sector bands
      {
        itemStyle: { borderColor: '#1e293b', borderWidth: 2, gapWidth: 2 },
        upperLabel: {
          show: true,
          height: 16,
          color: '#64748b',
          fontSize: 9,
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        },
      },
      // Level 2 — ticker tiles
      {
        itemStyle: { borderWidth: 1, borderColor: 'rgba(0,0,0,0.2)', gapWidth: 1 },
        label: {
          show: true,
          rich: {
            a: { fontSize: 12, fontWeight: 700, fontFamily: 'ui-monospace, monospace', color: '#fff', lineHeight: 18 },
            b: { fontSize: 10, fontFamily: 'ui-sans-serif, system-ui, sans-serif', color: 'rgba(255,255,255,0.8)', lineHeight: 14 },
          },
        },
      },
    ],
    data: seriesData.value,
  }],
}))

// ── Click-to-detail tooltip panel ─────────────────────────────────────────────

interface TooltipState { row: TileRow; x: number; y: number }
const tooltip  = ref<TooltipState | null>(null)
const chartRef = ref<InstanceType<typeof VChart> | null>(null)

function onChartClick(params: { data?: LeafData; event?: { offsetX: number; offsetY: number } } | any) { // type mismatch
  if (!params.data?.row) { tooltip.value = null; return }
  const row = params.data.row

  if (tooltip.value?.row.Ticker === row.Ticker) { tooltip.value = null; return }

  // Position near cursor, clamped inside the chart container
  const el    = chartRef.value?.$el as HTMLElement | undefined
  const width = el?.clientWidth ?? 800
  const ox    = params.event?.offsetX ?? 0
  const oy    = params.event?.offsetY ?? 0
  tooltip.value = {
    row,
    x: Math.min(ox + 10, width - 252),
    y: oy + 10,
  }
}

// Dismiss tooltip if metric changes (colours re-render, old selection stale)
watch(colourMetric, () => { tooltip.value = null })
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between gap-4">
      <h2 class="text-sm font-semibold text-slate-700 shrink-0">
        Portfolio Map
        <span class="ml-2 text-[10px] font-normal text-slate-400 uppercase tracking-wide">
          tile size = value · grouped by type › sector
        </span>
      </h2>
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-[11px] text-slate-400 uppercase tracking-wide">colour by</span>
        <select
          v-model="colourMetric"
          class="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white text-slate-700
                 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option v-for="opt in METRIC_OPTIONS" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Chart + tooltip wrapper -->
    <div class="relative p-3 h-[95vh]">
      <VChart
        ref="chartRef"
        class="w-full h-full"
        style="min-height: 320px; max-height: 700px;"
        :option="option"
        :autoresize="true"
        @click="onChartClick"
      />

      <!-- Detail tooltip panel -->
      <Transition name="tt">
        <div
          v-if="tooltip"
          class="absolute z-20 w-60 rounded-xl border border-slate-200 bg-slate-900 text-white
                 shadow-xl text-xs pointer-events-none"
          :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
        >
          <!-- Header -->
          <div class="flex items-start justify-between gap-2 px-3 pt-3 pb-2 border-b border-slate-700">
            <div>
              <p class="font-mono font-bold text-sm leading-tight">{{ tooltip.row.Ticker }}</p>
              <p v-if="tooltip.row.name" class="text-slate-400 text-[11px] mt-0.5 leading-snug">{{ tooltip.row.name }}</p>
            </div>
            <span class="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium bg-slate-700 text-slate-300">
              {{ tooltip.row.quoteType ?? '—' }}
            </span>
          </div>

          <!-- Detail rows -->
          <div class="px-3 py-2 space-y-1.5">
            <div class="flex justify-between">
              <span class="text-slate-400">Last Price</span>
              <span class="tabular-nums font-medium">{{ fPrice(tooltip.row.lastPrice, tooltip.row.currency) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Current Value</span>
              <span class="tabular-nums font-medium">{{ fPrice(tooltip.row.currentValue, tooltip.row.currency) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Cost Basis</span>
              <span class="tabular-nums">{{ fPrice(tooltip.row['Cost Basis'], tooltip.row.currency) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Quantity</span>
              <span class="tabular-nums">{{ fQty(tooltip.row.Quantity) }}</span>
            </div>

            <div class="border-t border-slate-700 my-1" />

            <div class="flex justify-between">
              <span class="text-slate-400">Day Gain</span>
              <span :class="['tabular-nums font-medium', gainClass(tooltip.row.dayGain)]">
                {{ fSigned(tooltip.row.dayGain, tooltip.row.currency) }}
                <span class="text-[10px]">({{ fPct(tooltip.row.dayGainPct) }})</span>
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Total Gain</span>
              <span :class="['tabular-nums font-medium', gainClass(tooltip.row.totalGain)]">
                {{ fSigned(tooltip.row.totalGain, tooltip.row.currency) }}
                <span class="text-[10px]">({{ fPct(tooltip.row.totalGainPct) }})</span>
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Weight</span>
              <span class="tabular-nums">{{ tooltip.row.weight.toFixed(2) }}%</span>
            </div>

            <template v-if="tooltip.row.trailingPE != null || tooltip.row.marketCap != null">
              <div class="border-t border-slate-700 my-1" />
              <div v-if="tooltip.row.trailingPE != null" class="flex justify-between">
                <span class="text-slate-400">P/E (trailing)</span>
                <span class="tabular-nums">{{ tooltip.row.trailingPE.toFixed(1) }}</span>
              </div>
              <div v-if="tooltip.row.marketCap != null" class="flex justify-between">
                <span class="text-slate-400">Market Cap</span>
                <span class="tabular-nums">{{ fMc(tooltip.row.marketCap) }}</span>
              </div>
            </template>

            <div v-if="tooltip.row.sector" class="flex justify-between">
              <span class="text-slate-400">Sector</span>
              <span class="text-right max-w-[140px] truncate">{{ tooltip.row.sector }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.tt-enter-active, .tt-leave-active { transition: opacity 0.12s, transform 0.12s; }
.tt-enter-from, .tt-leave-to       { opacity: 0; transform: scale(0.96) translateY(-4px); }
</style>
