import os
import sys
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import settings
from routes.chat import router

# Read the HTML UI once at import time — avoids aiofiles dependency
_HTML_PATH = os.path.join(os.path.dirname(__file__), "static", "index.html")
with open(_HTML_PATH, "r", encoding="utf-8") as _f:
    _HTML_CONTENT = _f.read()


def _ensure_sample_pdfs() -> None:
    data_dir = settings.data_dir
    os.makedirs(data_dir, exist_ok=True)
    has_pdfs = any(f.lower().endswith(".pdf") for f in os.listdir(data_dir))
    if not has_pdfs:
        print("[Startup] No PDFs found — generating sample HR documents...")
        generate_script = os.path.join(os.path.dirname(__file__), "data", "generate_pdfs.py")
        if not os.path.isfile(generate_script):
            print("[Startup] WARNING: data/generate_pdfs.py not found.")
            return
        import runpy
        runpy.run_path(generate_script, run_name="__main__")
        print("[Startup] Sample PDFs generated.")


def _build_vector_store_background(app: FastAPI) -> None:
    try:
        print("[RAG] Initialising vector store in background...")
        _ensure_sample_pdfs()
        from services.rag_service import get_or_create_vector_store
        app.state.vector_store = get_or_create_vector_store()
        app.state.ready = True
        print("[RAG] Vector store ready — agent is fully operational.")
    except Exception as exc:
        print(f"[RAG] ERROR building vector store: {exc}")
        app.state.ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Acme HR Agent is initialising...")

    try:
        settings.validate()
    except ValueError as exc:
        print(f"[Startup] FATAL: {exc}")
        sys.exit(1)

    app.state.ready = False
    app.state.vector_store = None

    thread = threading.Thread(
        target=_build_vector_store_background,
        args=(app,),
        daemon=True,
    )
    thread.start()

    print("[Startup] Server is up. Vector store loading in background...")
    yield
    print("[Shutdown] HR Agent stopped.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Acme HR AI Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def root() -> HTMLResponse:
    """Serve the chat UI — no file I/O at request time."""
    return HTMLResponse(content=_HTML_CONTENT)
