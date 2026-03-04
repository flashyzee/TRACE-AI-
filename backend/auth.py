
from fastapi import Header, HTTPException
from .config import TRACE_API_KEY

async def verify_api_key(x_api_key: str = Header(...)):
    """
    Verifies that the request contains the correct API key in headers.
    Raises 401 Unauthorized if invalid.
    """
    if x_api_key != TRACE_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True