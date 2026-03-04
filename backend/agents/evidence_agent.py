# agents/evidence_agent.py
"""
Evidence Collection Agent — processes technician follow-up answers
and adjusts confidence based on rule-based logic.
LangGraph node function: reads from and writes to TraceState.
"""

from ..orchestrator.state import TraceState

P0191_EVIDENCE_QUESTIONS = [
    {
        "id": "fuel_pressure_psi",
        "question": "What is the fuel rail pressure reading on your scanner right now? (in PSI)",
        "type": "number",
        "why_we_ask": "Normal is 870+ PSI at key-on. Below this confirms low pressure issue.",
        "quick_replies": ["Under 500 PSI", "500-870 PSI", "870+ PSI", "Scanner not available"],
    },
    {
        "id": "miles_since_filter",
        "question": "Approximately how many miles since the last fuel filter change?",
        "type": "number",
        "why_we_ask": "Cummins recommends filter change every 15,000 miles. Overdue filter is common P0191 cause.",
        "quick_replies": ["Under 5,000 mi", "5,000-15,000 mi", "Over 15,000 mi", "Unknown"],
    },
    {
        "id": "visible_leak",
        "question": "Can you visually inspect the fuel rail area? Do you see any fuel leak, wet spots, or fuel smell?",
        "type": "boolean",
        "why_we_ask": "A fuel leak is a SAFETY RISK and automatically triggers escalation regardless of confidence.",
        "quick_replies": ["Yes, I see a leak", "No leak visible", "Cannot access area"],
    },
    {
        "id": "cold_start_issue",
        "question": "Does the truck have trouble starting when the engine is cold (first start of the day)?",
        "type": "boolean",
        "why_we_ask": "Cold start issues point to lift pump weakness rather than sensor failure.",
        "quick_replies": ["Yes, hard cold start", "No cold start issues", "Not sure"],
    },
]


def evidence_agent(state: TraceState) -> TraceState:
    """
    LangGraph node: processes collected evidence and updates confidence.
    In a real app, this runs AFTER the frontend has collected all answers.
    The answers come in via state["evidence_collected"].
    """
    evidence = state.get("evidence_collected", {})
    base_confidence = state.get("top_confidence", 0.5)
    top_cause = state.get("top_cause", "").lower()

    confidence_delta = 0.0
    safety_flag = False

    # Rule 1: Visible leak → ALWAYS escalate (safety override)
    if evidence.get("visible_leak") in ["Yes, I see a leak", "yes", True]:
        safety_flag = True
        state["escalation_reason"] = (
            "Safety risk: visible fuel leak detected. "
            "Fire hazard — immediate escalation required."
        )

    # Rule 2: Very low fuel pressure → confirms pump or filter issue
    psi = evidence.get("fuel_pressure_psi", "")
    if "Under 500" in str(psi) or (isinstance(psi, (int, float)) and psi < 500):
        if "pump" in top_cause or "filter" in top_cause:
            confidence_delta += 0.15  # strong confirmation
        else:
            confidence_delta += 0.05
    elif "870+" in str(psi) or (isinstance(psi, (int, float)) and psi >= 870):
        # High pressure suggests sensor issue, not pump
        if "sensor" in top_cause:
            confidence_delta += 0.12
        else:
            confidence_delta -= 0.10  # contradicts current top cause

    # Rule 3: Overdue filter → confirms filter as cause
    miles = evidence.get("miles_since_filter", "")
    if "Over 15,000" in str(miles):
        if "filter" in top_cause:
            confidence_delta += 0.10

    # Rule 4: Cold start issues → confirms pump weakness
    if evidence.get("cold_start_issue") in ["Yes, hard cold start", "yes", True]:
        if "pump" in top_cause:
            confidence_delta += 0.08

    # Update state
    updated = min(base_confidence + confidence_delta, 0.97)  # cap at 97%
    state["updated_confidence"] = round(updated, 2)
    state["evidence_complete"] = True
    state["workflow_status"] = "evidence_gathering"

    # Pass safety flag to escalation agent
    if safety_flag:
        state["requires_human_approval"] = True

    return state


def get_evidence_questions(fault_code: str) -> list:
    """
    Returns the list of evidence questions for a given fault code.
    Called by FastAPI so the frontend can display questions one by one.
    """
    if fault_code.upper() == "P0191":
        return P0191_EVIDENCE_QUESTIONS
    return []
