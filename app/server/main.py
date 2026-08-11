"""
app/server/main.py
------------------
FastAPI server that centralises all yfinance and Firebase/Firestore access.

Routers
-------
/quotes      - yfinance market data
/portfolio   - Google Sheets portfolio (public)
/users       - Firestore user profiles, transactions, private portfolio

Static UI
---------
GET /  and all unmatched paths serve the Vue SPA from app/ui (built by `make ui-build`).
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Allow running from project root: `uvicorn app.server.main:app`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# CORS origins — the Vue dev server (port 5173) plus any explicitly configured
# production URL.  A bare "*" cannot be used together with allow_credentials=True
# (the spec forbids it), so we enumerate known origins instead.
_dev_origins = [
    "http://localhost:5173",
    "http://localhost:4173",   # vite preview
    "http://localhost:5000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
     
    
]
_prod_origin = os.getenv("FRONTEND_URL", "")
origins = _dev_origins + ([_prod_origin] if _prod_origin else [])

from server.routers import quotes, portfolio, users, auth, app_pages

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ainvest API",
    description="yfinance quotes, Google Sheets portfolio, Firestore user data.",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes.router)
app.include_router(portfolio.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(app_pages.router)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# ── Vue SPA — must be mounted last so API routes take priority ─────────────────
# StaticFiles(html=True) serves index.html for / and for any path that has no
# matching file, which gives Vue Router full control over client-side navigation.
_UI_DIR = Path(__file__).parent.parent / "ui"
app.mount("/", StaticFiles(directory=str(_UI_DIR), html=True), name="ui")


# Catch-all handler for Vue Router HTML5 History mode
@app.exception_handler(404)
async def vue_router_catch_all(request: Request, exc: HTTPException):
    # Check if the requested path looks like a static asset file
    # This prevents serving index.html for broken images or missing JS files
    if request.url.path.startswith(("/assets", "/api")):
        return HTMLResponse(content="Not Found", status_code=404)
        
    return RedirectResponse(url="/")

