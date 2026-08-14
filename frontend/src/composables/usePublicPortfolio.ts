/**
 * composables/usePublicPortfolio.ts
 * ----------------------------------
 * Fetches the public/aggregated portfolio from GET /portfolio.
 *
 * The endpoint returns the net aggregation of all transactions stored in
 * the background (across all users), enriched with live-price columns.
 *
 * No authentication is required.
 */

import { ref, watch, onUnmounted } from 'vue'
import { useBackend } from '@/composables/useBackend'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PublicHolding {
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
  weight: number
}

export interface PublicSummary {
  totalValue: number
  totalCost: number
  totalDayGain: number
  totalDayGainPct: number
  totalGain: number
  totalGainPct: number
}

export interface PublicPortfolioData {
  rows: PublicHolding[]
  summary: PublicSummary
}

// ── Composable ────────────────────────────────────────────────────────────────

export function usePublicPortfolio(
  /** Auto-refresh interval in ms. 0 = disabled. Default 60 s. */
  refreshMs = ref(60_000),
) {
  const data    = ref<PublicPortfolioData | null>(null)
  const loading = ref(false)
  const error   = ref<string | null>(null)
  let   timer: ReturnType<typeof setInterval> | null = null

  const { get } = useBackend()

  async function load() {
    loading.value = !data.value
    error.value   = null
    try {
      const raw = await get<{ rows: unknown[]; summary: unknown }>('/portfolio')
      data.value = {
        rows:    raw.rows    as PublicHolding[],
        summary: raw.summary as PublicSummary,
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load public portfolio'
    } finally {
      loading.value = false
    }
  }

  function startPolling() {
    if (timer !== null) { clearInterval(timer); timer = null }
    if (refreshMs.value > 0) timer = setInterval(load, refreshMs.value)
  }

  watch(refreshMs, startPolling)
  onUnmounted(() => { if (timer !== null) clearInterval(timer) })

  load()
  startPolling()

  return { data, loading, error, reload: load }
}
