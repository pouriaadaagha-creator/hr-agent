#!/bin/bash
# Single service — FastAPI serves both the API and the chat UI
uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
