import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import settings
from services.embedding_service import (
    get_embedding_model,
    load_pdfs_from_directory,
    split_documents,
)


def _vector_store_exists(path: str) -> bool:
    """Return True if a ChromaDB collection has already been persisted at *path*."""
    return os.path.isdir(path) and any(
        fname.endswith(".sqlite3") or fname == "chroma.sqlite3"
        for fname in os.listdir(path)
    ) or (os.path.isdir(path) and len(os.listdir(path)) > 0)


def build_vector_store() -> Chroma:
    """
    Load PDFs → split into chunks → embed → persist to ChromaDB.
    Called only when the vector store does not yet exist.
    """
    print("[RAG] Building vector store from PDFs...")
    embedding_model = get_embedding_model()
    documents = load_pdfs_from_directory(settings.data_dir)
    chunks = split_documents(documents)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=settings.vector_store_path,
        collection_name="hr_documents",
    )
    print(f"[RAG] Vector store built and persisted at '{settings.vector_store_path}'.")
    return vector_store


def load_vector_store() -> Chroma:
    """
    Load an existing ChromaDB collection from disk without re-embedding.
    """
    print("[RAG] Loading existing vector store...")
    embedding_model = get_embedding_model()

    vector_store = Chroma(
        persist_directory=settings.vector_store_path,
        embedding_function=embedding_model,
        collection_name="hr_documents",
    )
    print("[RAG] Vector store loaded successfully.")
    return vector_store


def get_or_create_vector_store() -> Chroma:
    """
    Entry point used by the application:
    - If vector store exists on disk → load it (fast path).
    - Otherwise → build it from PDFs (first-run path).
    """
    if _vector_store_exists(settings.vector_store_path):
        return load_vector_store()
    return build_vector_store()


def retrieve_relevant_chunks(
    vector_store: Chroma,
    question: str,
) -> list[Document]:
    """
    Run a similarity search against the vector store and return the top-K
    most relevant document chunks for the given question.
    Raises RuntimeError if retrieval fails so the caller can return a clean HTTP error.
    """
    if not question or not question.strip():
        raise ValueError("Question must not be empty.")

    try:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.retrieval_top_k},
        )
        chunks = retriever.invoke(question)
        return chunks
    except Exception as exc:
        raise RuntimeError(f"Retrieval failed: {exc}") from exc


def format_context(chunks: list[Document]) -> str:
    """
    Concatenate retrieved chunks into a single context string for the prompt.
    Each chunk is prefixed with its source filename for transparency.
    """
    if not chunks:
        return ""

    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown")
        parts.append(f"[{i}] Source: {source}\n{chunk.page_content.strip()}")

    return "\n\n---\n\n".join(parts)
