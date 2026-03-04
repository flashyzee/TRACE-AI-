from pydantic import BaseModel
from typing import Optional, Dict


class TriageRequest(BaseModel):
    fault_code: str
    symptoms: str
    session_id: str
    evidence: Optional[Dict] = {}


class TriageResponse(BaseModel):
    result: dict