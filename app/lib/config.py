"""
lib/config.py
-------------
Loads app/config.yaml once at import time and exposes typed constants.
"""

from __future__ import annotations

import os
from pathlib import Path
import yaml

_config_path = Path(__file__).parent.parent / "config.yaml"
_firebase_path = Path(__file__).parent.parent / "firebase.yaml"

with _config_path.open() as _f:
    _cfg = yaml.safe_load(_f)

with _firebase_path.open() as _f:
    _firebase_cfg: dict = yaml.safe_load(_f).get("firebaseConfig", {})

_portfolio = _cfg["portfolio"]

PORTFOLIO_URL: str = _portfolio["url"]
PORTFOLIO_NAMED_RANGE: str = _portfolio["named_range"]
PVT_PF_SAVE_COLS: list[str] = _portfolio["pvt_save_cols"]

# API base URL — can be overridden with the API_BASE_URL environment variable
API_BASE_URL: str = os.getenv("VITE_API_BASE_URL",  "http://localhost:8080/api")

# Firebase web SDK config (public — safe to expose in HTML)
FIREBASE_CONFIG: dict = {
    "apiKey":            os.getenv("FIREBASE_API_KEY",             _firebase_cfg.get("apiKey", "")),
    "authDomain":        os.getenv("FIREBASE_AUTH_DOMAIN",         _firebase_cfg.get("authDomain", "")),
    "projectId":         os.getenv("FIREBASE_PROJECT_ID",          _firebase_cfg.get("projectId", "")),
    "storageBucket":     os.getenv("FIREBASE_STORAGE_BUCKET",      _firebase_cfg.get("storageBucket", "")),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", _firebase_cfg.get("messagingSenderId", "")),
    "appId":             os.getenv("FIREBASE_APP_ID",              _firebase_cfg.get("appId", "")),
}
