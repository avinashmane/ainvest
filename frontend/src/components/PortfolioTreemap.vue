<script setup lang="ts">
/**
 * PortfolioTreemap.vue
 * --------------------
 * Pure-SVG squarify treemap of portfolio holdings grouped by:
 *   Level 1 — quoteType  (EQUITY, ETF, MUTUALFUND, …)
 *   Level 2 — sector     (Technology, Financials, …)
 *   Level 3 — tiles      (individual tickers)
 *
 * Tile colour is driven by a user-selectable metric:
 *   totalGainPct | dayGainPct | trailingPE | marketCap
 *
 * Props:
 *   rows     — AggRow[] (aggregated by ticker)
 *   currency — display currency string (e.g. 'INR')
 */

import { computed, ref } from 'vue'

interface TileRow {
  Ticker: string
  name: string | null
  quoteType: string | null
  sector: string | null
  currentValue: number
  totalGainPct: number
  dayGainPct: number
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

interface MetricOption {
  value: ColourMetric
  label: string
}

const METRIC_OPTIONS: MetricOption[] = [
  { value: 'totalGainPct', label: 'Total Gain %'  },
  { value: 'dayGainPct',   label: 'Day Gain %'    },
  { value: 'trailingPE',   label: 'P/E Ratio'     },
  { value: 'marketCap',    label: 'Market Cap'    },
]

const colourMetric = ref<ColourMetric>('totalGainPct')

const selectedOption = computed(
  () => METRIC_OPTIONS.find(o => o.value === colourMetric.value)!
)

// ── Layout constants ──────────────────────────────────────────────────────────
const W = 480
const H = 800

// ── Squarify algorithm ────────────────────────────────────────────────────────

interface Rect { x: number; y: number; w: number; h: number }

interface TileLayout extends Rect { row: TileRow }

function squarify(
  items: { value: number; row: TileRow }[],
  x: number, y: number, w: number, h: number,
): TileLayout[] {
  if (!items.length || w <= 0 || h <= 0) return []
  const total = items.reduce((s, i) => s + i.value, 0)
  const area  = w * h
  const norm  = items.map(i => ({ ...i, area: (i.value / total) * area }))
  const result: TileLayout[] = []
  layoutRow(norm, x, y, w, h, result)
  return result
}

function layoutRow(
  items: { area: number; row: TileRow }[],
  x: number, y: number, w: number, h: number,
  out: TileLayout[],
) {
  if (!items.length || w <= 0 || h <= 0) return

  const totalArea = items.reduce((s, i) => s + i.area, 0)
  let rowItems: typeof items = []
  let bestRatio = Infinity

  for (let i = 0; i < items.length; i++) {
    const candidate = items.slice(0, i + 1)
    const ratio = worstRatio(candidate, w, h)
    if (ratio <= bestRatio) { bestRatio = ratio; rowItems = candidate }
    else break
  }

  const rowArea = rowItems.reduce((s, i) => s + i.area, 0)
  const isWide  = w >= h
  let cx = x, cy = y

  for (const item of rowItems) {
    const fraction = item.area / rowArea
    let rw: number, rh: number
    if (isWide) { rw = (rowArea / totalArea) * w; rh = fraction * h }
    else        { rw = fraction * w; rh = (rowArea / totalArea) * h }
    out.push({ x: cx, y: cy, w: rw, h: rh, row: item.row })
    if (isWide) cy += rh; else cx += rw
  }

  const remaining = items.slice(rowItems.length)
  if (remaining.length) {
    if (isWide) {
      const usedW = (rowArea / totalArea) * w
      layoutRow(remaining, x + usedW, y, w - usedW, h, out)
    } else {
      const usedH = (rowArea / totalArea) * h
      layoutRow(remaining, x, y + usedH, w, h - usedH, out)
    }
  }
}

function worstRatio(items: { area: number }[], w: number, h: number): number {
  const total  = items.reduce((s, i) => s + i.area, 0)
  const short  = Math.min(w, h)
  const long   = Math.max(w, h)
  const rowLen = (total / (w * h)) * (w >= h ? w : h)
  let worst = 0
  for (const item of items) {
    const side  = (item.area / total) * short / rowLen * long
    const ratio = Math.max(side / (item.area / side), (item.area / side) / side)
    if (ratio > worst) worst = ratio
  }
  return worst
}

// ── Grouping helpers ──────────────────────────────────────────────────────────

const LABEL_QT: Record<string, string> = {
  EQUITY:     'Equities',
  ETF:        'ETFs',
  MUTUALFUND: 'Mutual Funds',
  INDEX:      'Indices',
  CURRENCY:   'Currencies',
  FUTURE:     'Futures',
}

function qtLabel(qt: string | null): string {
  return qt ? (LABEL_QT[qt.toUpperCase()] ?? qt) : 'Other'
}

// ── Computed grouped layout ───────────────────────────────────────────────────

const QT_HEADER  = 18
const SEC_HEADER = 14
const PAD        = 2

interface SectorGroup { label: string; value: number; tiles: TileLayout[] }
interface QtGroup {
  label: string; value: number; rect: Rect
  sectors: (SectorGroup & { rect: Rect })[]
}

const groups = computed<QtGroup[]>(() => {
  const rows = props.rows.filter(r => r.currentValue > 0)
  if (!rows.length) return []

  const qtMap = new Map<string, Map<string, TileRow[]>>()
  for (const row of rows) {
    const qt  = row.quoteType?.toUpperCase() ?? 'OTHER'
    const sec = row.sector ?? 'Other'
    if (!qtMap.has(qt)) qtMap.set(qt, new Map())
    const secMap = qtMap.get(qt)!
    if (!secMap.has(sec)) secMap.set(sec, [])
    secMap.get(sec)!.push(row)
  }

  const qtTotals = Array.from(qtMap.entries())
    .map(([qt, secMap]) => ({
      qt,
      value: Array.from(secMap.values()).flat().reduce((s, r) => s + r.currentValue, 0),
      secMap,
    }))
    .sort((a, b) => b.value - a.value)

  const grandTotal = qtTotals.reduce((s, g) => s + g.value, 0)
  let curY = 0
  const result: QtGroup[] = []

  for (const { qt, value, secMap } of qtTotals) {
    const bandH = (value / grandTotal) * H
    if (bandH < QT_HEADER + SEC_HEADER + 4) continue

    const qtRect: Rect = { x: 0, y: curY, w: W, h: bandH }
    const innerY = curY + QT_HEADER
    const innerH = bandH - QT_HEADER

    const sectors = Array.from(secMap.entries())
      .map(([sec, secRows]) => ({
        label: sec,
        value: secRows.reduce((s, r) => s + r.currentValue, 0),
        rows:  secRows.sort((a, b) => b.currentValue - a.currentValue),
      }))
      .sort((a, b) => b.value - a.value)

    const secTotal = sectors.reduce((s, s2) => s + s2.value, 0)
    let curX = 0
    const sectorGroups: (SectorGroup & { rect: Rect })[] = []

    for (const sec of sectors) {
      const secW = (sec.value / secTotal) * W
      if (secW < 4) continue
      const secRect: Rect = { x: curX, y: innerY, w: secW, h: innerH }
      const tileY = innerY + SEC_HEADER + PAD
      const tileH = innerH - SEC_HEADER - PAD
      const tiles = squarify(
        sec.rows.map(r => ({ value: r.currentValue, row: r })),
        curX, tileY, secW, tileH,
      )
      sectorGroups.push({ label: sec.label, value: sec.value, rect: secRect, tiles })
      curX += secW
    }

    result.push({ label: qtLabel(qt), value, rect: qtRect, sectors: sectorGroups })
    curY += bandH
  }

  return result
})

// ── Colour scaling ────────────────────────────────────────────────────────────

/**
 * For PE / market-cap we use a blue intensity scale (neutral, absolute).
 * For gain metrics we use the existing green/red diverging scale.
 */

// Pre-compute min/max of PE and marketCap across visible rows for normalisation.
const peRange = computed(() => {
  const vals = props.rows.map(r => r.trailingPE).filter((v): v is number => v != null && v > 0)
  return vals.length ? { min: Math.min(...vals), max: Math.max(...vals) } : null
})

const mcRange = computed(() => {
  const vals = props.rows.map(r => r.marketCap).filter((v): v is number => v != null && v > 0)
  return vals.length ? { min: Math.min(...vals), max: Math.max(...vals) } : null
})

function metricValue(row: TileRow): number | null {
  const m = colourMetric.value
  if (m === 'totalGainPct') return row.totalGainPct
  if (m === 'dayGainPct')   return row.dayGainPct
  if (m === 'trailingPE')   return row.trailingPE
  if (m === 'marketCap')    return row.marketCap
  return null
}

function tileColor(row: TileRow): string {
  const m   = colourMetric.value
  const val = metricValue(row)

  if (val == null || val === 0) return '#334155'   // slate fallback for missing data

  // ── Gain metrics: diverging green / red ────────────────────────────────────
  if (m === 'totalGainPct' || m === 'dayGainPct') {
    const pct       = val
    const intensity = Math.min(Math.abs(pct) / 10, 1)
    if (pct >= 0) {
      return `rgb(${Math.round(30 - intensity * 10)},${Math.round(140 + intensity * 70)},${Math.round(60 - intensity * 20)})`
    } else {
      return `rgb(${Math.round(180 + intensity * 55)},${Math.round(60 - intensity * 20)},${Math.round(60 - intensity * 20)})`
    }
  }

  // ── Absolute metrics: sequential blue scale ────────────────────────────────
  const range = m === 'trailingPE' ? peRange.value : mcRange.value
  if (!range || range.max === range.min) return '#2563eb'
  const t = (val - range.min) / (range.max - range.min)   // 0 → 1
  const r = Math.round(15  + t * 20)
  const g = Math.round(40  + t * 60)
  const b = Math.round(120 + t * 135)
  return `rgb(${r},${g},${b})`
}

function textColor(row: TileRow): string {
  // Always white on the dark backgrounds we use
  return '#ffffff'
}

// ── Label for the second line inside a tile ───────────────────────────────────

function tileSecondLine(row: TileRow): string {
  const m   = colourMetric.value
  const val = metricValue(row)
  if (val == null) return '—'
  if (m === 'totalGainPct' || m === 'dayGainPct')
    return `${val >= 0 ? '+' : '−'}${Math.abs(val).toFixed(2)}%`
  if (m === 'trailingPE')
    return `PE ${val.toFixed(1)}`
  if (m === 'marketCap')
    return fMc(val)
  return ''
}

function fMc(v: number): string {
  if (v >= 1e12) return `${(v / 1e12).toFixed(1)}T`
  if (v >= 1e9)  return `${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6)  return `${(v / 1e6).toFixed(1)}M`
  return String(v)
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
    <!-- Header ---------------------------------------------------------------- -->
    <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between gap-4">
      <h2 class="text-sm font-semibold text-slate-700 shrink-0">
        Portfolio Map
        <span class="ml-2 text-[10px] font-normal text-slate-400 uppercase tracking-wide">
          tile size = value · grouped by type › sector
        </span>
      </h2>

      <!-- Colour metric dropdown -->
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-[11px] text-slate-400 uppercase tracking-wide">colour by</span>
        <select
          v-model="colourMetric"
          class="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option v-for="opt in METRIC_OPTIONS" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- SVG ------------------------------------------------------------------- -->
    <div class="p-3">
      <svg
        :viewBox="`0 0 ${W} ${H}`"
        class="w-full rounded-xl"
        :style="{ height: `${H}px` }"
        aria-label="Portfolio treemap"
      >
        <g v-for="(qt, qi) in groups" :key="qi">
          <!-- quoteType band background -->
          <rect
            :x="qt.rect.x"      :y="qt.rect.y"
            :width="qt.rect.w"  :height="qt.rect.h"
            fill="#1e293b" rx="4"
          />
          <!-- quoteType label -->
          <text
            :x="qt.rect.x + 6" :y="qt.rect.y + 12"
            fill="#94a3b8" font-size="11" font-weight="700"
            font-family="ui-sans-serif, system-ui, sans-serif"
          >{{ qt.label.toUpperCase() }}</text>

          <g v-for="(sec, si) in qt.sectors" :key="si">
            <!-- sector column background -->
            <rect
              :x="sec.rect.x + 1"               :y="sec.rect.y"
              :width="Math.max(sec.rect.w - 2, 0)" :height="sec.rect.h"
              fill="#0f172a" rx="2"
            />
            <!-- sector label -->
            <text
              :x="sec.rect.x + 4" :y="sec.rect.y + 11"
              fill="#64748b" font-size="9"
              font-family="ui-sans-serif, system-ui, sans-serif"
            >{{ sec.label }}</text>

            <!-- ticker tiles -->
            <g v-for="(tile, ti) in sec.tiles" :key="ti">
              <rect
                :x="tile.x + 1"                  :y="tile.y + 1"
                :width="Math.max(tile.w - 2, 0)"  :height="Math.max(tile.h - 2, 0)"
                :fill="tileColor(tile.row)"
                rx="3"
              />
              <template v-if="tile.w > 48 && tile.h > 28">
                <!-- Ticker symbol -->
                <text
                  :x="tile.x + tile.w / 2"
                  :y="tile.h > 50 ? tile.y + tile.h / 2 - 7 : tile.y + tile.h / 2 + 1"
                  text-anchor="middle" dominant-baseline="middle"
                  :fill="textColor(tile.row)"
                  :font-size="Math.min(Math.max(tile.w / 6, 8), 14)"
                  font-family="ui-monospace, monospace" font-weight="700"
                >{{ tile.row.Ticker }}</text>
                <!-- Metric value (second line) -->
                <text
                  v-if="tile.h > 50"
                  :x="tile.x + tile.w / 2"
                  :y="tile.y + tile.h / 2 + 9"
                  text-anchor="middle" dominant-baseline="middle"
                  :fill="textColor(tile.row)"
                  :font-size="Math.min(Math.max(tile.w / 9, 7), 11)"
                  font-family="ui-sans-serif, system-ui, sans-serif"
                >{{ tileSecondLine(tile.row) }}</text>
              </template>
            </g>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>
