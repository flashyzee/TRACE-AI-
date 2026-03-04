import os
import warnings

# API key for securing the FastAPI backend.
# Set via environment variable. See .env.example for setup instructions.
TRACE_API_KEY = os.getenv("TRACE_API_KEY", "")

if not TRACE_API_KEY:
    warnings.warn(
        "TRACE_API_KEY is not set. The FastAPI backend will reject all requests. "
        "See .env.example for setup instructions.",
        UserWarning,
        stacklevel=2,
    )
