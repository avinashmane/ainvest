/**
 * composables/useStockQuote.ts
 * ----------------------------
 * Fetches a full Yahoo Finance quote (and optional history) from the FastAPI
 * backend, with optional real-time polling.
 */

import { ref, watch, onUnmounted, type Ref } from 'vue'
import { useBackend } from '@/composables/useBackend'

export interface QuoteData {
  ticker: string
  name: string | null
  longName: string | null
  currency: string | null
  exchange: string | null
  timezone: string | null

  // Price
  lastPrice: number
  previousClose: number
  open: number | null
  dayHigh: number | null
  dayLow: number | null
  regularMarketVolume: number | null

  // Change (computed here)
  basePrice: number
  change: number
  changePct: number

  // 52-week range
  fiftyTwoWeekHigh: number | null
  fiftyTwoWeekLow: number | null

  // Moving averages
  fiftyDayAverage: number | null
  twoHundredDayAverage: number | null

  // Fundamentals
  marketCap: number | null
  trailingPE: number | null
  forwardPE: number | null
  priceToBook: number | null
  trailingEps: number | null
  forwardEps: number | null
  dividendYield: number | null
  dividendRate: number | null
  exDividendDate: number | null
  beta: number | null

  // Margin / returns
  returnOnEquity: number | null
  grossMargins: number | null
  operatingMargins: number | null
  profitMargins: number | null

  // Shares
  sharesOutstanding: number | null
  floatShares: number | null

  // Sector / industry
  sector: string | null
  industry: string | null
  country: string | null
  website: string | null
  description: string | null

  // Analyst targets
  targetHighPrice: number | null
  targetLowPrice: number | null
  targetMeanPrice: number | null
  recommendationMean: number | null
  recommendationKey: string | null
  numberOfAnalystOpinions: number | null
}

export type Period = '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '5y'

export function useStockQuote(
  ticker: Ref<string>,
  period: Ref<Period> = ref('1d'),
  /** Poll interval in ms. 0 = no polling (default). */
  refreshMs: Ref<number> = ref(0),
) {
  const data    = ref<QuoteData | null>(null)
  const loading = ref(false)
  const error   = ref<string | null>(null)
  let   timer: ReturnType<typeof setInterval> | null = null

  const { get } = useBackend()

  async function fetchQuote(t: string): Promise<Record<string, unknown>> {
    return get<Record<string, unknown>>(`/quotes/${t}`)
  }

  async function fetchHistoryFirstClose(t: string, period: Period): Promise<number> {
    const rows = await get<{ Close: number }[]>(`/quotes/${t}/history?period=${period}`)
    if (!rows.length) throw new Error('Empty history')
    return rows[0]!.Close
  }

  function n(v: unknown): number | null {
    const n = typeof v === 'number' ? v : null
    return n
  }

  async function load() {
    if (!ticker.value) return
    loading.value = !data.value // skeleton only on first load
    error.value   = null
    try {
      const raw = await fetchQuote(ticker.value)

      const lastPrice     = (raw.lastPrice     as number) ?? 0
      const previousClose = (raw.previousClose as number) ?? lastPrice

      let basePrice: number
      if (period.value === '1d') {
        basePrice = previousClose
      } else {
        basePrice = await fetchHistoryFirstClose(ticker.value, period.value)
      }

      const change    = lastPrice - basePrice
      const changePct = basePrice !== 0 ? (change / basePrice) * 100 : 0

      data.value = {
        ticker:        ticker.value,
        name:          (raw.name    as string | null) ?? null,
        longName:      (raw.longName as string | null) ?? null,
        currency:      (raw.currency as string | null) ?? null,
        exchange:      (raw.exchange as string | null) ?? null,
        timezone:      (raw.timezone as string | null) ?? null,
        lastPrice, previousClose, basePrice, change, changePct,
        open:                  n(raw.open) ?? n(raw.regularMarketOpen),
        dayHigh:               n(raw.dayHigh) ?? n(raw.regularMarketDayHigh),
        dayLow:                n(raw.dayLow) ?? n(raw.regularMarketDayLow),
        regularMarketVolume:   n(raw.regularMarketVolume),
        fiftyTwoWeekHigh:      n(raw.fiftyTwoWeekHigh),
        fiftyTwoWeekLow:       n(raw.fiftyTwoWeekLow),
        fiftyDayAverage:       n(raw.fiftyDayAverage),
        twoHundredDayAverage:  n(raw.twoHundredDayAverage),
        marketCap:             n(raw.marketCap),
        trailingPE:            n(raw.trailingPE),
        forwardPE:             n(raw.forwardPE),
        priceToBook:           n(raw.priceToBook),
        trailingEps:           n(raw.trailingEps),
        forwardEps:            n(raw.forwardEps),
        dividendYield:         n(raw.dividendYield),
        dividendRate:          n(raw.dividendRate),
        exDividendDate:        n(raw.exDividendDate),
        beta:                  n(raw.beta),
        returnOnEquity:        n(raw.returnOnEquity),
        grossMargins:          n(raw.grossMargins),
        operatingMargins:      n(raw.operatingMargins),
        profitMargins:         n(raw.profitMargins),
        sharesOutstanding:     n(raw.sharesOutstanding),
        floatShares:           n(raw.floatShares),
        sector:                (raw.sector   as string | null) ?? null,
        industry:              (raw.industry as string | null) ?? null,
        country:               (raw.country  as string | null) ?? null,
        website:               (raw.website  as string | null) ?? null,
        description:           (raw.description as string | null) ?? null,
        targetHighPrice:       n(raw.targetHighPrice),
        targetLowPrice:        n(raw.targetLowPrice),
        targetMeanPrice:       n(raw.targetMeanPrice),
        recommendationMean:    n(raw.recommendationMean),
        recommendationKey:     (raw.recommendationKey as string | null) ?? null,
        numberOfAnalystOpinions: n(raw.numberOfAnalystOpinions),
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load quote'
    } finally {
      loading.value = false
    }
  }

  function startPolling() {
    stopPolling()
    if (refreshMs.value > 0) {
      timer = setInterval(load, refreshMs.value)
    }
  }

  function stopPolling() {
    if (timer !== null) { clearInterval(timer); timer = null }
  }

  watch([ticker, period], () => { load(); startPolling() }, { immediate: true })
  watch(refreshMs, startPolling)
  onUnmounted(stopPolling)

  return { data, loading, error, reload: load }
}
