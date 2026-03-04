from fastapi import FastAPI, Depends, Query, HTTPException
from .auth import verify_api_key
from .schemas import TriageRequest, EvidenceRequest, ApprovalRequest
from .logging_config import audit_log
from .db import log_decision, get_decision_logs

from .orchestrator.workflow import (
    run_workflow,
    run_triage_only,
    run_evidence_and_escalation,
    resume_after_approval,
)

app = FastAPI(title="TRACE AI Backend")


@app.get("/")
def health():
    return {"status": "TRACE AI secure backend running"}


@app.post("/triage")
def triage(request: TriageRequest, auth=Depends(verify_api_key)):
    """Step 1: Run LLM triage diagnosis for a fault code."""
    result = run_workflow(
        fault_code=request.fault_code,
        symptoms=request.symptoms,
        session_id=request.session_id,
        evidence=request.evidence or {},
    )

    top_conf = result.get("top_confidence", 0)

    audit_log({
        "session_id": request.session_id,
        "action": "triage_completed",
        "confidence": top_conf,
    })

    log_decision(
        session_id=request.session_id,
        action="triage_completed",
        confidence=top_conf,
        agent_id="triage_agent",
        fault_code=request.fault_code,
    )

    return result


@app.post("/evidence")
def evidence(request: EvidenceRequest, auth=Depends(verify_api_key)):
    """Step 2: Process evidence answers, run escalation check."""
    try:
        result = run_evidence_and_escalation(
            session_id=request.session_id,
            evidence=request.evidence,
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Session {request.session_id} not found or triage not completed: {e}",
        )

    audit_log({
        "session_id": request.session_id,
        "action": "evidence_and_escalation_completed",
        "confidence": result.get("updated_confidence", 0),
        "requires_human_approval": result.get("requires_human_approval"),
    })

    log_decision(
        session_id=request.session_id,
        action="evidence_and_escalation_completed",
        confidence=result.get("updated_confidence", 0),
        agent_id="evidence_agent",
    )

    return result


@app.post("/approve")
def approve(request: ApprovalRequest, auth=Depends(verify_api_key)):
    """Step 3: Manager approves or rejects an escalated case."""
    try:
        result = resume_after_approval(
            session_id=request.session_id,
            approved=request.approved,
            approved_by=request.approved_by,
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Session {request.session_id} not found: {e}",
        )

    action = "human_approved" if request.approved else "human_rejected"

    audit_log({
        "session_id": request.session_id,
        "action": action,
        "approved_by": request.approved_by,
    })

    log_decision(
        session_id=request.session_id,
        action=action,
        confidence=result.get("updated_confidence", 0),
        agent_id="human_reviewer",
        human_approved=request.approved,
    )

    return result


@app.get("/audit")
def audit(
    session_id: str = Query(None),
    agent_id: str = Query(None),
    auth=Depends(verify_api_key),
):
    """Retrieve decision audit logs, optionally filtered."""
    logs = get_decision_logs(session_id=session_id, agent_id=agent_id)
    return {"logs": logs, "count": len(logs)}
