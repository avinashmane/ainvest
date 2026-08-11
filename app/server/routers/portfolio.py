"""
server/routers/portfolio.py
---------------------------
Google Sheets portfolio endpoint (public / no auth required).

GET /portfolio
    Query params:
        url          - Google Sheets URL (defaults to config value)
        named_range  - Named range (defaults to config value)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from lib.portfolio_gsheet import read_portfolio
from lib.config import PORTFOLIO_URL, PORTFOLIO_NAMED_RANGE

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("", summary="Fetch portfolio holdings from Google Sheets")
def get_portfolio(
    url: str = Query(default=PORTFOLIO_URL,
                     description="Full Google Sheets URL."),
    named_range: str = Query(default=PORTFOLIO_NAMED_RANGE,
                             description="Named range that contains the table."),
) -> JSONResponse:
    """Return portfolio holdings as a list of row objects."""
    try:
        df = read_portfolio(url=url, named_range=named_range)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return JSONResponse(content=df.to_dict(orient="records"))
