import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration — all env vars are read once here."""

    # OpenRouter / LLM
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    model_name: str = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Storage paths
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    data_dir: str = os.getenv("DATA_DIR", "./data")

    # RAG chunking parameters
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5

    def validate(self) -> None:
        """Raise at startup if critical config is missing."""
        if not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. "
                "Add it to your .env file before starting the server."
            )


settings = Settings()
