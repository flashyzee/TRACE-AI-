# orchestrator/state.py
"""
Shared state schema for the TRACE workflow.
This TypedDict defines every field that flows between the 3 agents.
All agents read from and write to this single state object.
"""

from typing import TypedDict, Optional, List


class TraceState(TypedDict):
    # Input 
    session_id: str
    fault_code: str                # e.g. "P0191"
    initial_symptoms: str          # e.g. "rough idle, black smoke"

    # Triage Agent output 
    triage_results: Optional[List[dict]]
    # Each dict: {"cause": str, "confidence": float, "explanation": str,
    #             "urgency": str, "estimated_cost_usd": int}
    top_cause: Optional[str]
    top_confidence: Optional[float]  # 0.0 to 1.0

    # Evidence Agent output 
    evidence_collected: Optional[dict]
    # Keys: "fuel_pressure_psi", "miles_since_filter", "visible_leak",
    #        "cold_start_issue"
    evidence_complete: Optional[bool]
    updated_confidence: Optional[float]  # confidence AFTER evidence

    # Escalation Agent output 
    requires_human_approval: Optional[bool]
    escalation_reason: Optional[str]
    # e.g. "Confidence below 70%" or "Safety risk: potential fuel leak"
    human_approved: Optional[bool]   # None = pending, True/False = decided
    approved_by: Optional[str]       # name of senior engineer

    # Final output 
    repair_steps: Optional[List[str]]  # step-by-step repair instructions
    workflow_status: str
    # Values: "started", "triaged", "evidence_gathering",
    #         "escalated", "approved", "rejected", "resolved"

    # Metadata (for decision log) 
    model_used: str                  # "llama3.1" or "mistral" (fallback)
    error: Optional[str]             # any error message
