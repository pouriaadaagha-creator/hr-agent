import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from config import settings
from services.rag_service import retrieve_relevant_chunks, format_context


def _load_prompt_template() -> PromptTemplate:
    """
    Read the prompt template from disk and return a LangChain PromptTemplate.
    Input variables must match the placeholders {context} and {question} in the file.
    """
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts",
        "hr_prompt.txt",
    )

    if not os.path.isfile(prompt_path):
        raise FileNotFoundError(
            f"Prompt file not found at '{prompt_path}'. "
            "Ensure prompts/hr_prompt.txt exists."
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    return PromptTemplate(
        input_variables=["context", "question"],
        template=template_text,
    )


def get_llm() -> ChatOpenAI:
    """
    Return a LangChain ChatOpenAI instance configured to call OpenRouter.
    Model name is read from config so it can be swapped via .env.
    """
    return ChatOpenAI(
        model=settings.model_name,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0,        # deterministic — critical for factual HR answers
        max_tokens=1024,
    )


def answer_question(vector_store, question: str) -> dict[str, str]:
    """
    Full RAG pipeline for a single question:
      1. Retrieve relevant chunks from ChromaDB
      2. Format chunks into a context string
      3. Fill the prompt template
      4. Call the LLM
      5. Return the answer and source filenames

    Returns:
        {
            "answer": "<LLM response>",
            "sources": ["leave_policy.pdf", ...]
        }
    """
    # Step 1 — retrieve
    try:
        chunks: list[Document] = retrieve_relevant_chunks(vector_store, question)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    # Step 2 — format context
    context = format_context(chunks)

    # If no chunks came back the LLM would hallucinate — short-circuit here
    if not context:
        return {
            "answer": "I couldn't find that information in the HR documents.",
            "sources": [],
        }

    # Step 3 — build prompt
    prompt_template = _load_prompt_template()
    filled_prompt = prompt_template.format(context=context, question=question)

    # Step 4 — call LLM
    llm = get_llm()
    try:
        response = llm.invoke(filled_prompt)
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    # Step 5 — extract answer and deduplicated source list
    answer_text: str = response.content.strip()
    sources: list[str] = sorted(
        {chunk.metadata.get("source", "unknown") for chunk in chunks}
    )

    return {"answer": answer_text, "sources": sources}
