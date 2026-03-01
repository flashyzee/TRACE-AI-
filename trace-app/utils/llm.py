# utils/llm.py
"""
Ollama LLM connection with automatic fallback.
Tries Llama 3.1 first, falls back to Mistral if unavailable.
"""

from langchain_ollama import OllamaLLM

OLLAMA_BASE_URL = "http://localhost:11434"
PRIMARY_MODEL = "llama3.1"
FALLBACK_MODEL = "mistral"


def get_llm() -> tuple[OllamaLLM, str]:
    """
    Returns (llm_instance, model_name_used).
    Tries Llama 3.1 first, falls back to Mistral if unavailable.
    """
    try:
        llm = OllamaLLM(model=PRIMARY_MODEL, base_url=OLLAMA_BASE_URL)
        llm.invoke("test")  # quick ping to confirm model is loaded
        return llm, PRIMARY_MODEL
    except Exception:
        try:
            llm = OllamaLLM(model=FALLBACK_MODEL, base_url=OLLAMA_BASE_URL)
            llm.invoke("test")
            return llm, FALLBACK_MODEL
        except Exception as e:
            raise RuntimeError(
                f"No LLM available. Is Ollama running? Error: {e}"
            )
