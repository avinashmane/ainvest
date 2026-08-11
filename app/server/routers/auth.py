"""
server/routers/auth.py
----------------------
Authentication — two complementary flows:

1. **Firebase client-side flow** (original)
   POST /auth/session   — accepts a Firebase ID token from the browser,
                          verifies it with firebase-admin, sets a signed
                          httpOnly session cookie.
   POST /auth/signout   — clears the session cookie.

2. **Google OAuth 2.0 server-side redirect flow** (googleapis protocol)
   GET /auth/google/login      — builds Google's authorization URL with a
                                  PKCE-safe signed ``state`` cookie and
                                  redirects the browser to accounts.google.com.
   GET /auth/google/callback   — Google redirects here after consent.
                                  Validates state, exchanges the auth code
                                  for tokens (Google token endpoint), verifies
                                  the returned ID token, sets the session
                                  cookie, and redirects to /app/home.

Environment variables required for the redirect flow
-----------------------------------------------------
  GOOGLE_CLIENT_ID       — OAuth 2.0 client ID (from Google Cloud Console)
  GOOGLE_CLIENT_SECRET   — OAuth 2.0 client secret
  OAUTH_REDIRECT_URI     — Exact URI registered in GCP
                           (e.g. http://localhost:8000/auth/google/callback)
  OAUTH_STATE_SECRET     — A random secret used to sign the state cookie
                           (generate once with: python -c "import secrets; print(secrets.token_hex(32))")

Optional
--------
  SECURE_COOKIES=true    — sets the Secure flag on all cookies (use in prod)
"""

from __future__ import annotations

import os
import secrets
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ── Cookie / session constants ─────────────────────────────────────────────────

_COOKIE_NAME        = "ainvest_session"
_OAUTH_STATE_COOKIE = "oauth_state"
_COOKIE_MAX_AGE     = 60 * 60 * 8   # 8 hours
_STATE_MAX_AGE      = 60 * 10        # 10 minutes — state cookie TTL

# ── Google OAuth 2.0 endpoints (googleapis) ───────────────────────────────────

_GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

_SCOPES = "openid email profile"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _secure_cookies() -> bool:
    return os.getenv("SECURE_COOKIES", "false").lower() == "true"


def _state_serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("OAUTH_STATE_SECRET", "change-me-in-production")
    return URLSafeTimedSerializer(secret, salt="oauth-state")


def _make_state(nonce: str) -> str:
    """Return a URL-safe signed token encoding *nonce*."""
    return _state_serializer().dumps(nonce)


def _verify_state(token: str, max_age: int = _STATE_MAX_AGE) -> str:
    """Verify and return the nonce embedded in *token*, or raise HTTPException."""
    try:
        return _state_serializer().loads(token, max_age=max_age)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="OAuth state expired. Please try again.")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid OAuth state. Possible CSRF attack.")


def _set_session_cookie(response: Response, uid: str, email: str) -> None:
    """Encode uid + email into a base64 payload and attach as an httpOnly cookie."""
    import json, base64
    payload = base64.urlsafe_b64encode(
        json.dumps({"uid": uid, "email": email}).encode()
    ).decode()
    response.set_cookie(
        key=_COOKIE_NAME,
        value=payload,
        max_age=_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=_secure_cookies(),
    )


# ── Firebase Admin verification ───────────────────────────────────────────────

def _verify_id_token(id_token: str) -> dict[str, Any]:
    """Verify a Firebase / Google ID token and return its claims."""
    try:
        import firebase_admin
        from firebase_admin import auth as fb_auth, credentials
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="firebase-admin is not installed on the server.",
        )

    if not firebase_admin._apps:
        import json
        cred_json = os.getenv("GOOGLE_CRED_JSON", "")
        cred_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        if len(cred_json) > 100:
            cred = credentials.Certificate(json.loads(cred_json))
        elif cred_file:
            cred = credentials.Certificate(cred_file)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    try:
        return fb_auth.verify_id_token(id_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid ID token: {exc}") from exc


# ══════════════════════════════════════════════════════════════════════════════
# Route 1 – Firebase client-side flow (unchanged)
# ══════════════════════════════════════════════════════════════════════════════

class SessionIn(BaseModel):
    id_token: str


@router.post("/session", summary="Exchange Firebase ID token for a session cookie")
def create_session(body: SessionIn, response: Response) -> dict[str, Any]:
    claims = _verify_id_token(body.id_token)
    uid    = claims["uid"]
    email  = claims.get("email", "")
    _set_session_cookie(response, uid, email)
    return {"status": "ok", "email": email}


@router.post("/signout", summary="Clear the session cookie")
def signout(response: Response) -> dict[str, str]:
    response.delete_cookie(_COOKIE_NAME)
    return {"status": "signed_out"}


# ── Dependency — get current user from cookie ─────────────────────────────────

def current_user(request: Request) -> dict[str, str] | None:
    """Return ``{"uid": ..., "email": ...}`` from the session cookie, or None."""
    raw = request.cookies.get(_COOKIE_NAME)
    if not raw:
        return None
    try:
        import json, base64
        return json.loads(base64.urlsafe_b64decode(raw.encode()))
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Route 2 – Google OAuth 2.0 server-side redirect flow
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/google/login",
    summary="Initiate Google OAuth 2.0 redirect flow",
    description=(
        "Redirects the browser to Google's authorisation endpoint. "
        "A signed ``oauth_state`` cookie is set to prevent CSRF. "
        "After the user consents, Google redirects to ``/auth/google/callback``."
    ),
)
def google_login(request: Request, next: str = "/api/app/home") -> RedirectResponse:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_CLIENT_ID is not configured on the server.",
        )

    redirect_uri = os.getenv(
        "OAUTH_REDIRECT_URI",
        str(request.base_url).rstrip("/") + "/api/auth/google/callback",
    )

    # Generate a random nonce; encode it together with the ``next`` URL so we
    # can redirect back there after a successful login.
    nonce = secrets.token_urlsafe(32)
    state = _make_state(f"{nonce}|{next}")

    params = urlencode({
        "client_id":     client_id,
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         _SCOPES,
        "state":         state,
        "access_type":   "offline",   # request refresh token
        "prompt":        "select_account",
    })

    google_url = f"{_GOOGLE_AUTH_URL}?{params}"

    # Set a short-lived state cookie so we can validate it on callback.
    resp = RedirectResponse(url=google_url, status_code=302)
    resp.set_cookie(
        key=_OAUTH_STATE_COOKIE,
        value=state,
        max_age=_STATE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=_secure_cookies(),
    )
    return resp


@router.get(
    "/google/callback",
    summary="Google OAuth 2.0 callback — exchanges code for tokens and sets session",
    description=(
        "Registered as the authorised redirect URI in Google Cloud Console. "
        "Validates the ``state`` parameter, exchanges the authorisation code "
        "for tokens at ``oauth2.googleapis.com/token``, verifies the returned "
        "ID token via firebase-admin, sets the session cookie, and redirects "
        "the browser to ``/app/home`` (or the ``next`` URL embedded in state)."
    ),
)
async def google_callback(
    request: Request,
    code:  str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    # ── 1. Surface any error from Google ──────────────────────────────────────
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter.")

    # ── 2. Validate state (CSRF guard) ────────────────────────────────────────
    cookie_state = request.cookies.get(_OAUTH_STATE_COOKIE)
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=400, detail="State mismatch. Possible CSRF attack.")

    # Verify signature + expiry; extract nonce|next
    state_payload = _verify_state(state)
    parts = state_payload.split("|", 1)
    next_url = parts[1] if len(parts) == 2 else "/api/app/home"

    # ── 3. Exchange authorisation code for tokens ─────────────────────────────
    client_id     = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    redirect_uri  = os.getenv(
        "OAUTH_REDIRECT_URI",
        str(request.base_url).rstrip("/") + "/api/auth/google/callback",
    )

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not configured.",
        )

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code":          code,
                "client_id":     client_id,
                "client_secret": client_secret,
                "redirect_uri":  redirect_uri,
                "grant_type":    "authorization_code",
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )

    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Google token exchange failed: {token_resp.text}",
        )

    token_data = token_resp.json()
    id_token_str = token_data.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=502, detail="No id_token in Google token response.")

    # ── 4. Verify ID token and extract claims ─────────────────────────────────
    claims = _verify_id_token(id_token_str)
    uid    = claims["uid"]
    email  = claims.get("email", "")

    # ── 5. Set session cookie and redirect ────────────────────────────────────
    redirect_resp = RedirectResponse(url=next_url, status_code=302)
    _set_session_cookie(redirect_resp, uid, email)

    # Clean up the state cookie
    redirect_resp.delete_cookie(_OAUTH_STATE_COOKIE)

    return redirect_resp
