import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Return a LangChain OpenAIEmbeddings instance pointed at OpenRouter.
    text-embedding-3-small is a native OpenAI model; OpenRouter proxies it.
    """
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is missing — cannot initialise embeddings.")

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
    )


def load_pdfs_from_directory(directory: str) -> list[Document]:
    """
    Load every PDF in *directory* and return a flat list of LangChain Documents.
    Each page becomes one Document with metadata carrying the source filename.
    Raises FileNotFoundError if the directory is empty or contains no PDFs.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Data directory not found: {directory}")

    pdf_files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in '{directory}'. "
            "Run 'python data/generate_pdfs.py' to create sample documents."
        )

    all_documents: list[Document] = []

    for filename in sorted(pdf_files):
        filepath = os.path.join(directory, filename)
        try:
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            # Attach a clean source name so retrieval results are traceable
            for page in pages:
                page.metadata["source"] = filename
            all_documents.extend(pages)
            print(f"  Loaded: {filename} ({len(pages)} page(s))")
        except Exception as exc:
            raise RuntimeError(f"Failed to load PDF '{filename}': {exc}") from exc

    print(f"  Total pages loaded: {len(all_documents)}")
    return all_documents


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split raw page documents into overlapping chunks suitable for embedding.
    chunk_size and chunk_overlap come from central config.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"  Total chunks after splitting: {len(chunks)}")
    return chunks
