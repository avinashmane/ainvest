/**
 * composables/useFormatters.ts
 * ----------------------------
 * Shared number / currency / gain formatters used across portfolio views
 * and components.  Import directly (no setup call needed — pure functions).
 *
 * Numeric inputs accept `number | string | null | undefined` throughout so
 * callers never need to coerce before passing.
 */

// ── Currency symbol ───────────────────────────────────────────────────────────

const _CURRENCY_SYMBOLS: Record<string, string> = {
  INR: '₹', USD: '$', EUR: '€', GBP: '£', JPY: '¥',
}

/**
 * Map a currency code to its display symbol.
 * Falls back to `defaultSym` when the code is unknown/absent.
 *
 * @param c          ISO-4217 currency code (e.g. `"INR"`, `"USD"`)
 * @param defaultSym Symbol to use when `c` is null/undefined/unknown.
 *                   Use `""` in contexts where no symbol is better than `$`.
 */
export function currSym(c?: string | null, defaultSym = '$'): string {
  return c ? (_CURRENCY_SYMBOLS[c] ?? `${c} `) : defaultSym
}

// ── Coerce helper (internal) ──────────────────────────────────────────────────

function _n(v: number | string | null | undefined): number {
  return typeof v === 'number' ? v : parseFloat(String(v ?? ''))
}

// ── Price & value formatters ──────────────────────────────────────────────────

/** Absolute price — `$1,23,456.78` */
export function fPrice(v: number | string | null | undefined, currency?: string | null): string {
  const n = _n(v)
  if (isNaN(n)) return '—'
  return `${currSym(currency)}${Math.abs(n).toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/** Signed price with `+`/`−` prefix — `+$1,234.56` */
export function fSigned(v: number | string | null | undefined, currency?: string | null): string {
  const n = _n(v)
  if (isNaN(n)) return '—'
  return `${n >= 0 ? '+' : '−'}${currSym(currency)}${Math.abs(n).toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/** Signed percentage — `+12.34%` */
export function fPct(v: number | string | null | undefined): string {
  const n = _n(v)
  if (isNaN(n)) return '—'
  return `${n >= 0 ? '+' : '−'}${Math.abs(n).toFixed(2)}%`
}

/** Quantity — up to 4 decimal places,import.meta.env.VITE_APP_LOCALEgrouping */
export function fQty(v: number | string | null | undefined): string {
  const n = _n(v)
  if (isNaN(n)) return '—'
  return n.toLocaleString(import.meta.env.VITE_APP_LOCALE, { maximumFractionDigits: 2 })
}

/** Plain number with configurable decimal places */
export function fNum(v: number | null | undefined, decimals = 2): string {
  if (v == null) return '—'
  return v.toLocaleString(import.meta.env.VITE_APP_LOCALE, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

/**
 * Compact large number with currency prefix — T / B / M suffixes.
 * Used for market-cap labels in the treemap.
 */
export function fMc(v: number | null | undefined, currency?: string | null): string {
  if (v == null) return '—'
  const sym = currSym(currency, '')
  if (v >= 1e12) return `${sym}${(v / 1e12).toFixed(1)}T`
  if (v >= 1e9)  return `${sym}${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6)  return `${sym}${(v / 1e6).toFixed(1)}M`
  return `${sym}${v}`
}

/**
 * Large Indian-locale number — T / B / Cr / L suffixes with currency prefix.
 * Used for fundamentals in StockQuoteCard (market cap, revenue, etc.).
 */
export function fLarge(v: number | null | undefined, currency?: string | null): string {
  if (v == null) return '—'
  const sym = currSym(currency, '')
  if (v >= 1e12) return `${sym}${(v / 1e12).toFixed(2)}T`
  if (v >= 1e9)  return `${sym}${(v / 1e9).toFixed(2)}B`
  if (v >= 1e7)  return `${sym}${(v / 1e7).toFixed(2)}Cr`
  if (v >= 1e5)  return `${sym}${(v / 1e5).toFixed(2)}L`
  return `${sym}${v.toLocaleString(import.meta.env.VITE_APP_LOCALE)}`
}

/** Volume — Cr / L suffixes, no currency symbol */
export function fVolume(v: number | null | undefined): string {
  if (v == null) return '—'
  if (v >= 1e7) return `${(v / 1e7).toFixed(2)}Cr`
  if (v >= 1e5) return `${(v / 1e5).toFixed(2)}L`
  return v.toLocaleString(import.meta.env.VITE_APP_LOCALE)
}

// ── CSS class helpers ─────────────────────────────────────────────────────────

/** Tailwind text colour class for a gain/loss value (portfolio tables). */
export function gainClass(v: number | string | null | undefined): string {
  const n = _n(v)
  if (isNaN(n)) return 'text-slate-400'
  return n >= 0 ? 'text-emerald-600' : 'text-red-500'
}

/** Gain colour for dark backgrounds (treemap tooltip). */
export function gainClassDark(v: number | string | null | undefined): string {
  const n = _n(v)
  if (isNaN(n)) return 'text-slate-400'
  return n >= 0 ? 'text-emerald-400' : 'text-red-400'
}
