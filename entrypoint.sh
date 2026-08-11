#!/bin/sh
# Start the FastAPI backend in the background, then launch Streamlit.
# Both processes share the same environment (env vars, credentials, etc.).

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
# APP_DIR="$(cd "$(dirname "$0")/app" && pwd)"

echo "==> Starting FastAPI server on port ${PORT:-8080}"
cd "$APP_DIR" && uv run uvicorn app.server.main:app \
    --host 0.0.0.0 --port "${PORT:-8080}" --workers 2 &
FASTAPI_PID=$!

# Give the server a moment to bind before Streamlit starts making calls
sleep 2

echo "==> Starting Streamlit on port ${PORT:-8501}"
cd "$APP_DIR" && uv run streamlit run app/Home.py \
    --server.port="${PORT:-8501}" \
    --server.address=0.0.0.0 \
    --server.headless=true

# If Streamlit exits, stop FastAPI too
kill $FASTAPI_PID 2>/dev/null
