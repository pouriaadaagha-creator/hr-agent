#!/bin/bash
# FastAPI on 127.0.0.1 only — internal, not visible to Railway's router
uvicorn app:app --host 127.0.0.1 --port 8000 &

# Wait for FastAPI to be ready before Streamlit starts
sleep 5

# Streamlit on 0.0.0.0:$PORT — this is the only public-facing service
streamlit run demo.py \
  --server.port "${PORT:-8501}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
