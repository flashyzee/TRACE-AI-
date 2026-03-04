# utils/llm.py
"""
Groq Cloud LLM connection with automatic fallback.
Tries Llama 3.1 8B first, falls back to Mixtral 8x7B if unavailable.
Uses the same open-source models previously run locally via Ollama,
now hosted on Groq's cloud for deployment flexibility.
"""

import os
from pathlib import Path
from langchain_groq import ChatGroq

PRIMARY_MODEL = "llama-3.1-8b-instant"
FALLBACK_MODEL = "mixtral-8x7b-32768"

# Load .env file if it exists (for local development / Streamlit)
_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def get_llm() -> tuple[ChatGroq, str]:
    """
    Returns (llm_instance, model_name_used).
    Tries Llama 3.1 first, falls back to Mixtral if unavailable.
    Requires GROQ_API_KEY environment variable or .env file.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Get a free key at https://console.groq.com/keys"
        )

    try:
        llm = ChatGroq(model=PRIMARY_MODEL, api_key=api_key, temperature=0)
        return llm, PRIMARY_MODEL
    except Exception:
        try:
            llm = ChatGroq(model=FALLBACK_MODEL, api_key=api_key, temperature=0)
            return llm, FALLBACK_MODEL
        except Exception as e:
            raise RuntimeError(
                f"No LLM available via Groq. Check your API key. Error: {e}"
            )
