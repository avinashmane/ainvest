"""
Tests for app/server — portfolio, quotes, auth, and page endpoints.

Uses FastAPI's TestClient and mocks underlying functions so no real
network / Firestore calls are made.

All API routes are mounted under the /api/ prefix.
"""

from __future__ import annotations

import sys
import os

# Ensure app/ is on the path (mirrors how the server adds it)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)

# ── GET / (Vue SPA index) ─────────────────────────────────────────────────────

def test_index_returns_200():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


# ── /api/health ───────────────────────────────────────────────────────────────

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── /api/portfolio ────────────────────────────────────────────────────────────

SAMPLE_DF = pd.DataFrame(
    [
        {"Ticker": "INFY", "Quantity": "10", "Avg Cost": "1500.00"},
        {"Ticker": "TCS",  "Quantity": "5",  "Avg Cost": "3200.00"},
    ]
)


@patch("server.routers.portfolio.read_portfolio", return_value=SAMPLE_DF)
def test_get_portfolio_returns_200(mock_read):
    response = client.get("/api/portfolio")
    assert response.status_code == 200


@patch("server.routers.portfolio.read_portfolio", return_value=SAMPLE_DF)
def test_get_portfolio_returns_list(mock_read):
    response = client.get("/api/portfolio")
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@patch("server.routers.portfolio.read_portfolio", return_value=SAMPLE_DF)
def test_get_portfolio_row_values(mock_read):
    data = client.get("/api/portfolio").json()
    assert data[0]["Ticker"] == "INFY"
    assert data[1]["Ticker"] == "TCS"


@patch("server.routers.portfolio.read_portfolio", return_value=SAMPLE_DF)
def test_get_portfolio_uses_default_params(mock_read):
    from lib.config import PORTFOLIO_URL, PORTFOLIO_NAMED_RANGE
    client.get("/api/portfolio")
    mock_read.assert_called_once_with(url=PORTFOLIO_URL, named_range=PORTFOLIO_NAMED_RANGE)


@patch("server.routers.portfolio.read_portfolio", return_value=SAMPLE_DF)
def test_get_portfolio_accepts_custom_params(mock_read):
    custom_url = "https://docs.google.com/spreadsheets/d/custom/"
    response = client.get(f"/api/portfolio?url={custom_url}&named_range=myRange")
    assert response.status_code == 200
    mock_read.assert_called_once_with(url=custom_url, named_range="myRange")


@patch("server.routers.portfolio.read_portfolio", side_effect=Exception("sheets error"))
def test_get_portfolio_propagates_error_as_502(mock_read):
    response = client.get("/api/portfolio")
    assert response.status_code == 502
    assert "sheets error" in response.json()["detail"]


@patch("server.routers.portfolio.read_portfolio", return_value=pd.DataFrame())
def test_get_portfolio_empty_sheet_returns_empty_list(mock_read):
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    assert response.json() == []


# ── /api/quotes/{ticker} ──────────────────────────────────────────────────────

SAMPLE_QUOTE = {
    "ticker": "INFY.NS",
    "name": "Infosys Limited",
    "currency": "INR",
    "lastPrice": 1500.0,
    "previousClose": 1490.0,
    "dayHigh": 1510.0,
    "dayLow": 1480.0,
    "exchange": "NSI",
    "timezone": "Asia/Calcutta",
}


@patch("server.routers.quotes._fetch_quote", return_value=SAMPLE_QUOTE)
def test_get_quote_returns_200(mock_q):
    response = client.get("/api/quotes/INFY.NS")
    assert response.status_code == 200


@patch("server.routers.quotes._fetch_quote", return_value=SAMPLE_QUOTE)
def test_get_quote_returns_dict(mock_q):
    data = client.get("/api/quotes/INFY.NS").json()
    assert data["ticker"] == "INFY.NS"
    assert data["lastPrice"] == 1500.0


@patch("server.routers.quotes._fetch_quote", side_effect=Exception("yf error"))
def test_get_quote_propagates_error_as_502(mock_q):
    response = client.get("/api/quotes/BAD")
    assert response.status_code == 502
    assert "yf error" in response.json()["detail"]


# ── GET /api/app/login ────────────────────────────────────────────────────────

def test_login_page_returns_200():
    response = client.get("/api/app/login", follow_redirects=False)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_login_page_contains_google_button():
    response = client.get("/api/app/login")
    assert b"btn-google" in response.content


def test_login_page_contains_firebase_config():
    response = client.get("/api/app/login")
    assert b"firebase" in response.content.lower()
    assert b"authDomain" in response.content


def test_login_page_contains_email_form():
    response = client.get("/api/app/login")
    assert b"form-email" in response.content


# ── GET /api/app/home ─────────────────────────────────────────────────────────

def test_home_page_returns_200():
    response = client.get("/api/app/home")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_home_page_contains_auth_guard():
    response = client.get("/api/app/home")
    assert b"page-content" in response.content
    assert b"page-unauth" in response.content


def test_home_page_contains_signout_button():
    response = client.get("/api/app/home")
    assert b"btn-signout" in response.content


# ── POST /api/auth/signout ────────────────────────────────────────────────────

def test_signout_returns_200():
    response = client.post("/api/auth/signout")
    assert response.status_code == 200
    assert response.json() == {"status": "signed_out"}


# ── POST /api/auth/session (invalid token) ───────────────────────────────────

@patch("server.routers.auth._verify_id_token")
def test_session_bad_token_returns_error(mock_verify):
    from fastapi import HTTPException
    mock_verify.side_effect = HTTPException(status_code=401, detail="Invalid ID token")
    response = client.post("/api/auth/session", json={"id_token": "fake"})
    assert response.status_code == 401


# ── POST /api/auth/session (valid token) ─────────────────────────────────────

@patch("server.routers.auth._verify_id_token",
       return_value={"uid": "abc123", "email": "user@example.com"})
def test_session_valid_token_sets_cookie(mock_verify):
    response = client.post("/api/auth/session", json={"id_token": "valid-token"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "ainvest_session" in response.cookies
