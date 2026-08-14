<script setup lang="ts">
/**
 * PortfolioPie.vue
 * ----------------
 * ECharts-powered donut chart of portfolio holdings.
 *
 * Two independent dropdowns:
 *   1. "Group by"  — Ticker (default) | quoteType | sector | Account Number
 *   2. "Value by"  — Current Value | Cost Basis | Quantity | Total Gain
 *
 * Props:
 *   rows     — AggRow[] (aggregated by ticker, must have numeric fields)
 *   rawRows  — PvtHolding[] (optional; enables "Account Number" grouping)
 *   currency — display currency string (e.g. 'INR')
 */

import { computed, ref } from 'vue'
import {  currSym } from '@/composables/useFormatters' //fValue as _fValue,
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ComposeOption } from 'echarts/core'
import type { PieSeriesOption } from 'echarts/charts'
import type { TooltipComponentOption, LegendComponentOption } from 'echarts/components'

use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer])

type EChartsOption = ComposeOption<PieSeriesOption | TooltipComponentOption | LegendComponentOption>

// ── Prop types ────────────────────────────────────────────────────────────────

interface PieRow {
  Ticker: string
  name: string | null
  currency: string | null
  quoteType: string | null
  sector: string | null
  currentValue: number
  'Cost Basis': number
  Quantity: number
  totalGain: number
  weight: number
}

interface RawRow extends PieRow {
  'Account Number'?: string | null
}

const props = defineProps<{
  rows: PieRow[]
  rawRows?: any[]
  currency?: string | null
}>()

// ── Group-by options ──────────────────────────────────────────────────────────

type GroupKey = 'Ticker' | 'quoteType' | 'sector' | 'Account Number'

const GROUP_OPTIONS = computed(() => {
  const opts: { key: GroupKey; label: string }[] = [
    { key: 'Ticker',        label: 'Ticker'     },
    { key: 'quoteType',     label: 'Quote Type' },
    { key: 'sector',        label: 'Sector'     },
  ]
  if (props.rawRows?.length) opts.push({ key: 'Account Number', label: 'Account' })
  return opts
})

const selectedGroup = ref<GroupKey>('Ticker')

// ── Value-by (field) options ──────────────────────────────────────────────────

type FieldKey = 'currentValue' | 'Cost Basis' | 'Quantity' | 'totalGain'

const FIELDS: { key: FieldKey; label: string }[] = [
  { key: 'currentValue', label: 'Current Value' },
  { key: 'Cost Basis',   label: 'Cost Basis'    },
  { key: 'Quantity',     label: 'Quantity'      },
  { key: 'totalGain',    label: 'Total Gain'    },
]

const selectedField = ref<FieldKey>('currentValue')

const selectedFieldLabel = computed(
  () => FIELDS.find(f => f.key === selectedField.value)?.label ?? ''
)

// ── Aggregate rows by the selected group key ──────────────────────────────────

interface Bucket {
  label: string
  currentValue: number
  'Cost Basis': number
  Quantity: number
  totalGain: number
}

const buckets = computed<Bucket[]>(() => {
  const field = selectedField.value
  const group = selectedGroup.value
  const map   = new Map<string, Bucket>()

  const source: RawRow[] =
    group === 'Account Number' && props.rawRows?.length
      ? props.rawRows
      : (props.rows as RawRow[])

  for (const row of source) {
    const rawKey = group === 'Ticker'
      ? row.Ticker
      : group === 'Account Number'
        ? (row['Account Number'] ?? null)
        : row[group as 'quoteType' | 'sector']

    const key = rawKey?.trim() || '(unknown)'
    const v   = (row[field as keyof PieRow] as number) || 0
    if (v <= 0) continue

    const existing = map.get(key)
    if (existing) {
      existing.currentValue  += row.currentValue
      existing['Cost Basis'] += row['Cost Basis']
      existing.Quantity      += row.Quantity
      existing.totalGain     += row.totalGain
    } else {
      map.set(key, {
        label:        key,
        currentValue: row.currentValue,
        'Cost Basis': row['Cost Basis'],
        Quantity:     row.Quantity,
        totalGain:    row.totalGain,
      })
    }
  }

  return Array.from(map.values())
    .filter(b => b[field] > 0)
    .sort((a, b) => b[field] - a[field])
})

// ── Formatter (field-aware) ───────────────────────────────────────────────────

function fValue(v: number): string {
  if (selectedField.value === 'Quantity') {
    return v.toLocaleString(import.meta.env.VITE_APP_LOCALE, { maximumFractionDigits: 2 })
  }
  return `${currSym(props.currency)}${Math.abs(v).toLocaleString(import.meta.env.VITE_APP_LOCALE, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`
}

// ── ECharts option ────────────────────────────────────────────────────────────

const PALETTE = [
  '#3b82f4', '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981',
  '#ef4444', '#ec4899', '#84cc16', '#f97316', '#6366f1',
]

const option = computed(() => { //<EChartsOption>
  const field  = selectedField.value
  const data   = buckets.value
  const total  = data.reduce((s, b) => s + b[field], 0)

  return {
    color: PALETTE,
    tooltip: {
      trigger: 'item',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      formatter: (p: { name: string; value: number; percent: number }) =>
        `<span style="font-family:ui-monospace,monospace;font-weight:700">${p.name}</span>`
        + `<br/>${fValue(p.value)}`
        + `<span style="color:#94a3b8;margin-left:6px">${p.percent?.toFixed(1)}%</span>`,
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'middle',
      icon: 'roundRect',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 10,
      textStyle: {
        color: '#57606a',
        fontSize: 11,
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
      },
      formatter: (name: string) => {
        const b = data.find(d => d.label === name)
        if (!b) return name
        const pct = total > 0 ? ((b[field] / total) * 100).toFixed(1) : '0.0'
        return `${name} %${pct}` //${fValue(b[field])} 
      },
      rich: {
        name: { width: 120, fontFamily: 'ui-monospace, monospace', fontWeight: '600', color: '#1f2328', fontSize: 11 },
        val:  { width: 80, align: 'right', color: '#57606a', fontSize: 11 },
        pct:  { width: 42, align: 'right', color: '#94a3b8', fontSize: 11 },
      },
    },
    series: [{
      type: 'pie',
      radius: ['42%', '70%'],
      center: ['28%', '50%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        position: 'center',
        formatter: () =>
          `{title|${selectedFieldLabel.value}}\n{count|${data.length} groups}`,
        rich: {
          title: { fontSize: 13, fontWeight: '700', fontFamily: 'ui-sans-serif, system-ui, sans-serif', color: '#1f2328', lineHeight: 22 },
          count: { fontSize: 11, color: '#57606a', fontFamily: 'ui-sans-serif, system-ui, sans-serif', lineHeight: 18 },
        },
      },
      emphasis: {
        label: {
          show: true,
          formatter: (p: { name: string; percent: number }) =>
            `{title|${p.name}}\n{count|${p.percent.toFixed(1)}%}`,
          rich: {
            title: { fontSize: 13, fontWeight: '700', fontFamily: 'ui-monospace, monospace', color: '#1f2328', lineHeight: 22 },
            count: { fontSize: 11, color: '#57606a', fontFamily: 'ui-sans-serif, system-ui, sans-serif', lineHeight: 18 },
          },
        },
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' },
      },
      labelLine: { show: false },
      data: data.map(b => ({ name: b.label, value: b[field] })),
    }],
  }
})
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between gap-3 flex-wrap">
      <h2 class="text-sm font-semibold text-slate-700">Portfolio Distribution</h2>

      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-400">Group by</span>
        <select
          v-model="selectedGroup"
          class="text-xs border border-slate-200 rounded-lg px-2 py-1 text-slate-600
                 bg-white focus:outline-none focus:border-blue-400"
        >
          <option v-for="g in GROUP_OPTIONS" :key="g.key" :value="g.key">
            {{ g.label }}
          </option>
        </select>

        <span class="text-xs text-slate-400">Value by</span>
        <select
          v-model="selectedField"
          class="text-xs border border-slate-200 rounded-lg px-2 py-1 text-slate-600
                 bg-white focus:outline-none focus:border-blue-400"
        >
          <option v-for="f in FIELDS" :key="f.key" :value="f.key">
            {{ f.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Chart -->
    <div class="p-3">
      <VChart
        class="w-full"
        style="height: 360px;"
        :option="option"
        :autoresize="true"
      />
    </div>
  </div>
</template>
