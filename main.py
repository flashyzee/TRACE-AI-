from fastapi import FastAPI, Depends
from .auth import verify_api_key
from .schemas import TriageRequest
from .logging_config import audit_log
from .db import log_decision

from orchestrator.workflow import run_workflow

app = FastAPI(title="TRACE AI Backend")


@app.get("/")
def health():
    return {"status": "TRACE AI secure backend running"}


@app.post("/triage")
def triage(request: TriageRequest, auth=Depends(verify_api_key)):

    result = run_workflow(
        fault_code=request.fault_code,
        symptoms=request.symptoms,
        session_id=request.session_id,
        evidence=request.evidence or {},
    )

    top_conf = result.get("top_confidence", 0)

    # Append-only file log
    audit_log({
        "session_id": request.session_id,
        "action": "triage_completed",
        "confidence": top_conf,
    })

    # Database log
    log_decision(
        session_id=request.session_id,
        action="triage_completed",
        confidence=top_conf,
    )

    return result