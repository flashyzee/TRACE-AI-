from fastapi import Header, HTTPException
from .config import TRACE_API_KEY


async def verify_api_key(x_api_key: str = Header(...)):
    """
    Verifies that the request contains the correct API key in headers.
    Raises 401 Unauthorized if invalid.
    Raises 503 Service Unavailable if the server API key is not configured.
    """
    if not TRACE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Server API key not configured. Set TRACE_API_KEY environment variable.",
        )
    if x_api_key != TRACE_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid API key")
    return True
