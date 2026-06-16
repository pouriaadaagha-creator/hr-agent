import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.chat import router


# ---------------------------------------------------------------------------
# Auto-generate sample PDFs if the data directory is empty
# ---------------------------------------------------------------------------

def _ensure_sample_pdfs() -> None:
    """Generate sample HR PDFs on first run if none exist yet."""
    data_dir = settings.data_dir
    os.makedirs(data_dir, exist_ok=True)

    has_pdfs = any(f.lower().endswith(".pdf") for f in os.listdir(data_dir))
    if not has_pdfs:
        print("[Startup] No PDFs found — generating sample HR documents...")
        # Resolve the generator script relative to this file
        generate_script = os.path.join(
            os.path.dirname(__file__), "data", "generate_pdfs.py"
        )
        if not os.path.isfile(generate_script):
            print(
                "[Startup] WARNING: data/generate_pdfs.py not found. "
                "Place PDF files in the data/ directory manually."
            )
            return
        # Run the generator in the same Python interpreter
        import runpy
        runpy.run_path(generate_script, run_name="__main__")
        print("[Startup] Sample PDFs generated.")


# ---------------------------------------------------------------------------
# Lifespan — runs once at startup and once at shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
      1. Validate config (API key present)
      2. Ensure sample PDFs exist
      3. Build or load the ChromaDB vector store
      4. Attach it to app.state so all routes can access it

    Shutdown:
      - Nothing to clean up (ChromaDB is file-based)
    """
    print("[Startup] Acme HR Agent is initialising...")

    # 1 — Config validation
    try:
        settings.validate()
    except ValueError as exc:
        print(f"[Startup] FATAL: {exc}")
        sys.exit(1)

    # 2 — PDFs
    _ensure_sample_pdfs()

    # 3 — Vector store
    from services.rag_service import get_or_create_vector_store
    app.state.vector_store = get_or_create_vector_store()

    print("[Startup] HR Agent is ready. Visit http://127.0.0.1:8000/docs")
    yield
    print("[Shutdown] HR Agent stopped.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Acme HR AI Agent",
    description=(
        "An HR assistant that answers employee questions "
        "based exclusively on company HR documents using RAG."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — open during development; restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(router)
