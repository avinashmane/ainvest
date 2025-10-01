#!/bin/sh
echo "Running Streamlit app on port $PORT"
uv run streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0 --server.headless true