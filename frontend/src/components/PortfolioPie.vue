<script setup lang="ts">
/**
 * PortfolioPie.vue
 * ----------------
 * Pure-SVG donut/pie chart of portfolio holdings.
 * The user picks the numeric field that drives slice size via a dropdown.
 *
 * Props:
 *   rows     — AggRow[] (aggregated by ticker, must have all numeric fields)
 *   currency — display currency string (e.g. 'INR')
 */

import { computed, ref } from 'vue'

interface PieRow {
  Ticker: string
  name: string | null
  currency: string | null
  currentValue: number
  'Cost Basis': number
  Quantity: number
  totalGain: number
  weight: number
}

const props = defineProps<{
  rows: PieRow[]
  currency?: string | null
}>()

// ── Field options ─────────────────────────────────────────────────────────────

interface FieldOption {
  key: keyof PieRow
  label: string
}

const FIELDS: FieldOption[] = [
  { key: 'currentValue', label: 'Current Value'  },
  { key: 'Cost Basis',   label: 'Cost Basis'     },
  { key: 'Quantity',     label: 'Quantity'        },
  { key: 'totalGain',    label: 'Total Gain'      },
]

const selectedField = ref<keyof PieRow>('currentValue')

// ── SVG constants ─────────────────────────────────────────────────────────────

const CX = 160          // centre x
const CY = 160          // centre y
const R  = 130          // outer radius
const R_INNER = 72      // inner radius (donut hole)
const VW = 560          // total viewBox width (pie left + legend right)
const VH = 320          // total viewBox height

// ── Colour palette (10 distinct, accessible) ─────────────────────────────────

const PALETTE = [
  '#3b82f4', '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981',
  '#ef4444', '#ec4899', '#84cc16', '#f97316', '#6366f1',
]

function sliceColor(i: number): string {
  return (PALETTE[i % PALETTE.length] || '') as string
}

// ── Computed slices ───────────────────────────────────────────────────────────

interface Slice {
  ticker: string
  name: string | null
  value: number
  pct: number
  color: string
  // SVG arc path
  path: string
  // label anchor point
  lx: number
  ly: number
}

function polarToXY(angleDeg: number, r: number): [number, number] {
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return [CX + r * Math.cos(rad), CY + r * Math.sin(rad)]
}

function arcPath(startDeg: number, endDeg: number): string {
  // Clamp to prevent degenerate full-circle arcs
  const sweep = Math.min(endDeg - startDeg, 359.999)
  const [x1, y1] = polarToXY(startDeg, R)
  const [x2, y2] = polarToXY(startDeg + sweep, R)
  const [ix1, iy1] = polarToXY(startDeg, R_INNER)
  const [ix2, iy2] = polarToXY(startDeg + sweep, R_INNER)
  const large = sweep > 180 ? 1 : 0
  return [
    `M ${x1} ${y1}`,
    `A ${R} ${R} 0 ${large} 1 ${x2} ${y2}`,
    `L ${ix2} ${iy2}`,
    `A ${R_INNER} ${R_INNER} 0 ${large} 0 ${ix1} ${iy1}`,
    'Z',
  ].join(' ')
}

const slices = computed<Slice[]>(() => {
  const field = selectedField.value
  // Keep only rows where the chosen field is positive
  const rows = props.rows.filter(r => {
    const v = r[field]
    return typeof v === 'number' && v > 0
  })
  if (!rows.length) return []

  const total = rows.reduce((s, r) => s + (r[field] as number), 0)
  if (total === 0) return []

  const result: Slice[] = []
  let angle = 0

  rows.forEach((row, i) => {
    const value = row[field] as number
    const pct   = (value / total) * 100
    const sweep = (value / total) * 360
    const mid   = angle + sweep / 2
    const [lx, ly] = polarToXY(mid, (R + R_INNER) / 2)

    result.push({
      ticker: row.Ticker,
      name:   row.name,
      value,
      pct,
      color:  sliceColor(i),
      path:   arcPath(angle, angle + sweep),
      lx,
      ly,
    })
    angle += sweep
  })

  return result
})

// ── Hover state ───────────────────────────────────────────────────────────────

const hovered = ref<string | null>(null)

// ── Formatters ────────────────────────────────────────────────────────────────

function currSym(c?: string | null): string {
  const m: Record<string, string> = { INR: '₹', USD: '$', EUR: '€', GBP: '£', JPY: '¥' }
  return c ? (m[c] ?? `${c} `) : '₹'
}

function fValue(v: number): string {
  const field = selectedField.value
  if (field === 'Quantity') {
    return v.toLocaleString('en-IN', { maximumFractionDigits: 2 })
  }
  return `${currSym(props.currency)}${Math.abs(v).toLocaleString('en-IN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between gap-3">
      <h2 class="text-sm font-semibold text-slate-700">Portfolio Distribution</h2>
      <!-- Field selector dropdown -->
      <select
        v-model="selectedField"
        class="text-xs border border-slate-200 rounded-lg px-2 py-1 text-slate-600
               bg-white focus:outline-none focus:border-blue-400"
      >
        <option v-for="f in FIELDS" :key="String(f.key)" :value="f.key">
          {{ f.label }}
        </option>
      </select>
    </div>

    <div class="p-3">
      <svg
        :viewBox="`0 0 ${VW} ${VH}`"
        class="w-full"
        :style="{ height: '320px' }"
        aria-label="Portfolio pie chart"
      >
        <!-- ── Donut slices ── -->
        <g>
          <path
            v-for="slice in slices"
            :key="slice.ticker"
            :d="slice.path"
            :fill="slice.color"
            :opacity="hovered === null || hovered === slice.ticker ? 1 : 0.35"
            style="transition: opacity 0.15s;"
            @mouseenter="hovered = slice.ticker"
            @mouseleave="hovered = null"
          />
        </g>

        <!-- ── Centre label (hovered ticker or total) ── -->
        <g>
          <text
            :x="CX" :y="CY - 10"
            text-anchor="middle" dominant-baseline="middle"
            font-family="ui-monospace, monospace"
            font-weight="700"
            font-size="16"
            fill="#1f2328"
          >
            {{
              hovered
                ? slices.find(s => s.ticker === hovered)?.ticker ?? ''
                : FIELDS.find(f => f.key === selectedField)?.label ?? ''
            }}
          </text>
          <text
            :x="CX" :y="CY + 12"
            text-anchor="middle" dominant-baseline="middle"
            font-family="ui-sans-serif, system-ui, sans-serif"
            font-size="12"
            fill="#57606a"
          >
            {{
              hovered
                ? `${slices.find(s => s.ticker === hovered)?.pct.toFixed(1) ?? ''}%`
                : `${slices.length} holdings`
            }}
          </text>
        </g>

        <!-- ── Legend (right side) ── -->
        <g transform="translate(340, 20)">
          <g
            v-for="(slice, i) in slices"
            :key="slice.ticker"
            :transform="`translate(0, ${i * 26})`"
            style="cursor: default;"
            @mouseenter="hovered = slice.ticker"
            @mouseleave="hovered = null"
          >
            <!-- Colour swatch -->
            <rect
              x="0" y="2" width="10" height="10" rx="2"
              :fill="slice.color"
              :opacity="hovered === null || hovered === slice.ticker ? 1 : 0.35"
              style="transition: opacity 0.15s;"
            />
            <!-- Ticker -->
            <text
              x="16" y="11"
              font-family="ui-monospace, monospace"
              font-weight="600"
              font-size="11"
              :fill="hovered === null || hovered === slice.ticker ? '#1f2328' : '#94a3b8'"
              style="transition: fill 0.15s;"
            >{{ slice.ticker }}</text>
            <!-- Value -->
            <text
              x="210" y="11"
              text-anchor="end"
              font-family="ui-sans-serif, system-ui, sans-serif"
              font-size="11"
              :fill="hovered === null || hovered === slice.ticker ? '#57606a' : '#cbd5e1'"
              style="transition: fill 0.15s;"
            >{{ fValue(slice.value) }}</text>
            <!-- Pct -->
            <text
              x="215" y="11"
              font-family="ui-sans-serif, system-ui, sans-serif"
              font-size="11"
              :fill="hovered === null || hovered === slice.ticker ? '#94a3b8' : '#e2e8f0'"
              style="transition: fill 0.15s;"
            >{{ slice.pct.toFixed(1) }}%</text>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>
