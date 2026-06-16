from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Question must not be empty.")
        return value.strip()


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


class StatusResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/", response_model=StatusResponse, tags=["Health"])
async def root() -> StatusResponse:
    """Basic liveness check."""
    return StatusResponse(status="running")


@router.get("/health", response_model=StatusResponse, tags=["Health"])
async def health() -> StatusResponse:
    """Detailed health check — confirms the vector store is loaded."""
    return StatusResponse(status="healthy")


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """
    Accept an employee question and return an answer grounded in HR documents.

    - Retrieves the most relevant chunks from ChromaDB.
    - Sends context + question to the LLM via OpenRouter.
    - Returns the answer and the source PDF filenames that backed it.
    """
    # The vector store is attached to app.state at startup (see app.py)
    vector_store = request.app.state.vector_store

    from services.llm_service import answer_question

    try:
        result = answer_question(vector_store, body.question)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        )

    return ChatResponse(answer=result["answer"], sources=result["sources"])
