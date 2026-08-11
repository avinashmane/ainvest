"""
server/routers/app_pages.py
---------------------------
HTML page routes — served via Jinja2 templates.

GET /api/app/login   → login.html  (Firebase Google sign-in)
GET /api/app/home    → home.html   (post-login dashboard)
"""

from __future__ import annotations

import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from lib.config import FIREBASE_CONFIG
from server.routers.auth import current_user

router = APIRouter(prefix="/api/app", tags=["pages"], include_in_schema=False)

_templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Streamlit app URL — used for "Open in app" links on the home page
_STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")



def _base_ctx(firebase_config=FIREBASE_CONFIG) -> dict:
    return {"firebase_config": firebase_config, "streamlit_url": _STREAMLIT_URL}


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    """Show the login page. If already authenticated, redirect to /app/home."""
    # print(_base_ctx())
    if current_user(request):
        return RedirectResponse("/api/app/home")
    return _templates.TemplateResponse(request, "login.html", _base_ctx())


@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request) -> HTMLResponse:
    """Show the home dashboard. Unauthenticated users see a sign-in prompt."""
    return _templates.TemplateResponse(request, "home.html", _base_ctx())
