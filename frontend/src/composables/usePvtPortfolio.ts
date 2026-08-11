/**
 * composables/usePvtPortfolio.ts
 * --------------------------------
 * Fetches the enriched private portfolio for the signed-in user from
 * GET /users/{email}/pvt_pf
 *
 * Each row already contains live-price columns computed server-side:
 *   lastPrice, prevClose, currentValue,
 *   dayGain, dayGainPct, totalGain, totalGainPct
 *
 * The response also carries a summary object with portfolio-level totals.
 */

import { ref, watch, onUnmounted, type Ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PvtHolding {
  // Raw saved columns
  'Account Number': string
  Symbol: string
  Ticker: string
  Quantity: number
  'Cost Basis': number
  Description: string
  Import_value: string | number

  // Live-price + info columns added by the server
  name: string | null
  currency: string | null
  quoteType: string | null
  sector: string | null
  country: string | null
  trailingPE: number | null
  marketCap: number | null
  lastPrice: number
  prevClose: number
  currentValue: number
  dayGain: number
  dayGainPct: number
  totalGain: number
  totalGainPct: number
}

export interface PvtSummary {
  totalValue: number
  totalCost: number
  totalDayGain: number
  totalDayGainPct: number
  totalGain: number
  totalGainPct: number
}

export interface PvtPortfolioData {
  rows: PvtHolding[]
  summary: PvtSummary
}

// ── Composable ────────────────────────────────────────────────────────────────

export function usePvtPortfolio(
  email: Ref<string | null | undefined>,
  /** Auto-refresh interval in ms. 0 = disabled. Default 60 s. */
  refreshMs: Ref<number> = ref(60_000),
) {
  const data    = ref<PvtPortfolioData | null>(null)
  const loading = ref(false)
  const error   = ref<string | null>(null)
  let   timer: ReturnType<typeof setInterval> | null = null

  async function load() {
    if (!email.value) return
    loading.value = !data.value
    error.value   = null
    try {
      const res = await fetch(`${API_BASE}/users/${encodeURIComponent(email.value)}/pvt_pf`)
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const raw = await res.json() as unknown as { rows: unknown[]; summary: unknown }
      data.value = {
        rows: raw.rows as PvtHolding[],
        summary: raw.summary as PvtSummary,
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load portfolio'
    } finally {
      loading.value = false
    }
  }

  function startPolling() {
    stopPolling()
    if (refreshMs.value > 0) timer = setInterval(load, refreshMs.value)
  }

  function stopPolling() {
    if (timer !== null) { clearInterval(timer); timer = null }
  }

  watch(email, () => { load(); startPolling() }, { immediate: true })
  watch(refreshMs, startPolling)
  onUnmounted(stopPolling)

  return { data, loading, error, reload: load }
}
