# AInvest

An AI-powered investment assistant and portfolio tracker.
A **FastAPI** backend serves market data and user state; a **Vue 3** SPA is the
primary UI; a **Streamlit** app provides a secondary analytics interface.

**Live demos**
- https://ainvest.forthe.life
- https://ainvest-1008690560612.us-central1.run.app/
- https://ainvest.streamlit.app

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser                                             │
│  Vue 3 SPA  (frontend/ → built into app/ui/)         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP  /api/*
┌──────────────────────▼──────────────────────────────┐
│  FastAPI server  (app/server/)                       │
│  /api/quotes/*   – yfinance market data              │
│  /api/portfolio  – Google Sheets public portfolio    │
│  /api/users/*    – Firestore user profiles & tx      │
│  /api/auth/*     – Firebase / Google OAuth           │
│  /api/app/*      – Jinja2 HTML pages (login, home)   │
│  /               – serves Vue SPA (app/ui/)          │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
  ┌───────▼──────┐        ┌─────────▼──────┐
  │  Firestore   │        │  Google Sheets  │
  │  (users, tx, │        │  (public PF)    │
  │   pvt_pf)    │        └────────────────┘
  └──────────────┘

  Streamlit UI (app/Home.py) — secondary analytics interface
  calls the same FastAPI server via lib/api_client.py
```

---

## Project layout

```
ainvest/
├── app/
│   ├── Home.py                  # Streamlit entry point
│   ├── config.yaml              # Portfolio URL, named ranges, API base URL
│   ├── firebase.yaml            # Firebase web SDK config (non-secret keys)
│   ├── agents/                  # Agno AI agents (search, yfinance, email, …)
│   ├── components/              # Streamlit UI components
│   ├── lib/
│   │   ├── api_client.py        # HTTP client used by the Streamlit app
│   │   ├── config.py            # Typed constants loaded from config.yaml
│   │   ├── database.py          # Firestore db singleton
│   │   ├── gsheets.py           # gspread helpers (get_client, named_range_to_df)
│   │   ├── model.py             # Shared Pydantic models
│   │   ├── portfolio.py         # enrich_pvt_portfolio() — live-price enrichment
│   │   ├── portfolio_gsheet.py  # read_portfolio() — Google Sheets loader
│   │   ├── ticker.py            # Ticker class + fetch_quotes() — TTL-cached yfinance
│   │   ├── user.py              # User / Accounts — Firestore user model
│   │   └── yf.py                # Low-level yfinance helpers
│   ├── pages/                   # Streamlit multi-page app pages
│   ├── server/
│   │   ├── main.py              # FastAPI app, mounts routers + Vue SPA
│   │   ├── routers/
│   │   │   ├── quotes.py        # GET /api/quotes/{ticker}  (delegates to lib/ticker)
│   │   │   ├── portfolio.py     # GET /api/portfolio
│   │   │   ├── users.py         # /api/users/*
│   │   │   ├── auth.py          # /api/auth/* (Firebase + Google OAuth)
│   │   │   └── app_pages.py     # /api/app/login  /api/app/home
│   │   └── templates/           # Jinja2 HTML templates
│   └── ui/                      # Built Vue SPA (committed, served by FastAPI)
├── frontend/                    # Vue 3 + Vite source
│   └── src/
│       ├── views/               # Page-level Vue components
│       ├── components/          # Reusable UI components
│       ├── composables/         # useStockQuote, useAuth, …
│       ├── stores/              # Pinia stores
│       └── router/              # Vue Router routes
├── tests/
│   ├── conftest.py              # Top-level fixtures (mocks lib.database)
│   ├── lib/
│   │   ├── test_database.py     # Integration tests (skipped without GCP creds)
│   │   ├── test_portfolio_gsheet.py
│   │   └── test_user.py
│   └── server/
│       └── test_main.py         # FastAPI endpoint tests via TestClient
├── Dockerfile
├── Makefile
├── pyproject.toml               # uv / pip project metadata
└── uv.lock
```

---

## Quick start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| [uv](https://docs.astral.sh/uv/) | latest |
| Node.js + [pnpm](https://pnpm.io/) | 18+ / 8+ (frontend only) |

### 1. Install Python dependencies

```bash
uv sync
```

### 2. Configure environment

Copy `.env_docker` to `.env` and fill in the required values:

```bash
cp .env_docker .env
```

Key variables:

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOOGLE_CRED_JSON` | Yes | Google service-account JSON (base64 or raw) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Alt. to above | Path to service-account key file |
| `GOOGLE_CLIENT_ID` | OAuth flow | Google OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth flow | Google OAuth 2.0 client secret |
| `OAUTH_REDIRECT_URI` | OAuth flow | Registered redirect URI |
| `OAUTH_STATE_SECRET` | OAuth flow | Random secret for CSRF state cookie |
| `FIREBASE_API_KEY` | Yes | Firebase web SDK API key |
| `FIREBASE_AUTH_DOMAIN` | Yes | Firebase auth domain |
| `FIREBASE_PROJECT_ID` | Yes | Firebase project ID |
| `VITE_API_BASE_URL` | No | API base URL (default: `http://localhost:8000/api`) |
| `FRONTEND_URL` | No | Production frontend URL for CORS |
| `STREAMLIT_URL` | No | Streamlit app URL shown on home page |
| `SECURE_COOKIES` | No | Set `true` in production to add `Secure` flag |

### 3. Run locally

**FastAPI backend** (port 8000):

```bash
make srv
```

**Vue frontend** dev server (port 5173):

```bash
make ui
```

**Streamlit app** (port 8501):

```bash
make dev
```

All three can run simultaneously. The Vue dev server proxies `/api/*` to the
FastAPI backend automatically.

---

## Building the Vue SPA

```bash
make ui-build
```

This runs `pnpm build` inside `frontend/` and writes the output to `app/ui/`,
where it is committed and served directly by the FastAPI `StaticFiles` mount.

---

## Testing

```bash
make test              # run full test suite
make test_lib          # lib/ tests only
make test_server       # server/ tests only
make test_<keyword>    # e.g. make test_portfolio — runs pytest -k portfolio
```

Tests that require live Google credentials are automatically skipped when
`GOOGLE_CRED_JSON` / `GOOGLE_APPLICATION_CREDENTIALS` are absent.

---

## Docker

```bash
make build             # build image
make run               # stop → rm → run container on :8080
make d-push            # push to Artifact Registry
make d-deploy          # deploy to Cloud Run (us-central1)
make d-update          # update Cloud Run env vars only
```

---

## API reference

The FastAPI server generates interactive docs at runtime:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |

Key endpoints:

```
GET  /api/health
GET  /api/quotes/{ticker}
GET  /api/quotes/{ticker}/history
GET  /api/quotes/{tickers}/history/multi
POST /api/quotes/search
GET  /api/portfolio
GET  /api/users/{email}/profile
GET  /api/users/{email}/transactions
GET  /api/users/{email}/pvt_pf
GET  /api/app/login
GET  /api/app/home
POST /api/auth/session
POST /api/auth/signout
GET  /api/auth/google/login
GET  /api/auth/google/callback
```
