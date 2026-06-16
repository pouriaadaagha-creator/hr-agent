#!/bin/bash
# Start FastAPI on internal port 8000
uvicorn app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit on Railway's dynamic PORT (defaults to 8501 locally)
streamlit run demo.py \
  --server.port "${PORT:-8501}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
