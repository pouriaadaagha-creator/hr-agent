#!/bin/bash
# FastAPI on 127.0.0.1 only — internal, not visible to Railway's router
uvicorn app:app --host 127.0.0.1 --port 8000 &

# Streamlit on 0.0.0.0:$PORT — the only public-facing service
# Starts immediately; FastAPI vector store loads in background
streamlit run demo.py \
  --server.port "${PORT:-8501}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
