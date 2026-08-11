"""
lib/portfolio.py
----------------
Business logic for enriching a raw private-portfolio DataFrame with
live yfinance prices and computing gain columns.

Public API
----------
enrich_pvt_portfolio(df) -> dict
    Accepts a raw holdings DataFrame (as loaded from Firestore / Google Sheets)
    and returns the shape consumed by the frontend:

        {
            "rows":    [...],          # one dict per holding row
            "summary": {
                "totalValue", "totalCost",
                "totalDayGain", "totalDayGainPct",
                "totalGain",    "totalGainPct",
            }
        }
"""

from __future__ import annotations

import pandas as pd


# ── helpers ───────────────────────────────────────────────────────────────────

from lib.ticker import fetch_quotes as _fetch_quotes


def _q(quotes: dict[str, dict], sym: str, field: str, default: float = 0.0) -> float:
    val = quotes.get(str(sym), {}).get(field)
    return float(val) if val is not None else default


# ── public function ───────────────────────────────────────────────────────────

def enrich_pvt_portfolio(df: pd.DataFrame) -> dict:
    """
    Enrich a raw holdings DataFrame with live prices and compute gain columns.

    Mutates a *copy* of ``df``; the caller's frame is not modified.

    Parameters
    ----------
    df : pd.DataFrame
        Raw rows as loaded from Firestore / Google Sheets.  Expected columns:
        ``Quantity``, ``Cost Basis``, ``Import_value``,
        and either ``Ticker`` or ``Symbol``.

    Returns
    -------
    dict  ``{ "rows": [...], "summary": {...} }``
    """
    df = df.copy()

    # ── 1. Coerce numeric input columns ──────────────────────────────────────
    for col in ("Quantity", "Cost Basis", "Import_value"):
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            ).fillna(0)

    # ── 2. Resolve ticker column ──────────────────────────────────────────────
    ticker_col = "Ticker" if "Ticker" in df.columns else "Symbol"

    # ── 3. Fetch live quotes ──────────────────────────────────────────────────
    unique_tickers: list[str] = df[ticker_col].dropna().unique().tolist()
    quotes = _fetch_quotes(unique_tickers)

    # ── 4. Join price fields onto the DataFrame ───────────────────────────────
    def _str(sym: str, field: str) -> str | None:
        return quotes.get(str(sym), {}).get(field)

    df["lastPrice"]  = df[ticker_col].map(lambda s: _q(quotes, s, "lastPrice"))
    df["prevClose"]  = df[ticker_col].map(lambda s: _q(quotes, s, "previousClose"))
    df["currency"]   = df[ticker_col].map(lambda s: _str(s, "currency"))
    df["name"]       = df[ticker_col].map(lambda s: _str(s, "name"))
    df["quoteType"]  = df[ticker_col].map(lambda s: _str(s, "quoteType"))
    df["sector"]     = df[ticker_col].map(lambda s: _str(s, "sector"))
    df["country"]    = df[ticker_col].map(lambda s: _str(s, "country"))
    df["trailingPE"] = df[ticker_col].map(lambda s: _q(quotes, s, "trailingPE", float("nan")))
    df["marketCap"]  = df[ticker_col].map(lambda s: _q(quotes, s, "marketCap", float("nan")))

    # ── 5. Compute gain columns ───────────────────────────────────────────────
    qty  = df["Quantity"]
    cost = df["Cost Basis"]
    last = df["lastPrice"]
    prev = df["prevClose"].replace(0, float("nan"))

    # Use live price where a quote was found; fall back to Import_value otherwise.
    live_mask = last > 0
    import_value = df.get("Import_value", pd.Series(0, index=df.index))
    df["currentValue"] = (qty * last).where(live_mask, import_value)

    df["dayGain"]      = qty * (last - df["prevClose"])
    df["dayGainPct"]   = (last - df["prevClose"]) / prev * 100
    df["totalGain"]    = df["currentValue"] - cost
    df["totalGainPct"] = df["totalGain"] / cost.replace(0, float("nan")) * 100

    # ── 6. Build summary totals ───────────────────────────────────────────────
    total_value    = float(df["currentValue"].sum())
    total_cost     = float(cost.sum())
    total_day_gain = float(df["dayGain"].sum())
    total_gain     = float(df["totalGain"].sum())
    prev_value     = total_value - total_day_gain
    day_gain_pct   = (total_day_gain / prev_value * 100) if prev_value else 0.0
    gain_pct       = (total_gain    / total_cost  * 100) if total_cost  else 0.0

    return {
        "rows": df.fillna("").to_dict(orient="records"),
        "summary": {
            "totalValue":      total_value,
            "totalCost":       total_cost,
            "totalDayGain":    total_day_gain,
            "totalDayGainPct": day_gain_pct,
            "totalGain":       total_gain,
            "totalGainPct":    gain_pct,
        },
    }
