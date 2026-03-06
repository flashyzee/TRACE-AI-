# utils/llm.py
"""
Local LLM connection via Ollama with automatic model fallback.
Tries Llama 3.1 8B first, falls back to Mistral 7B if unavailable.
All inference runs locally — no data is sent to external APIs.
"""

from langchain_ollama import ChatOllama

PRIMARY_MODEL = "llama3.1"
FALLBACK_MODEL = "mistral"


def get_llm() -> tuple[ChatOllama, str]:
    """
    Returns (llm_instance, model_name_used).
    Tries Llama 3.1 locally via Ollama first, falls back to Mistral 7B.
    Requires Ollama to be running: ollama serve
    """
    try:
        llm = ChatOllama(model=PRIMARY_MODEL, temperature=0)
        llm.invoke("ping")
        return llm, PRIMARY_MODEL
    except Exception:
        pass

    try:
        llm = ChatOllama(model=FALLBACK_MODEL, temperature=0)
        llm.invoke("ping")
        return llm, FALLBACK_MODEL
    except Exception as e:
        raise RuntimeError(
            "No LLM available. Make sure Ollama is running:\n"
            "  ollama serve\n"
            "  ollama pull llama3.1\n"
            "  ollama pull mistral\n"
            f"Error: {e}"
        )
