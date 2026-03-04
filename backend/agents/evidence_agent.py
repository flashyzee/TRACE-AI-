# agents/evidence_agent.py
"""
Evidence Collection Agent: processes technician follow(-) up answers
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

GENERIC_EVIDENCE_QUESTIONS = [
    {
        "id": "symptom_onset",
        "question": "When did you first notice this issue?",
        "type": "text",
        "why_we_ask": "Sudden onset suggests an acute failure (sensor, relay), while gradual suggests wear (pump, filter, valve).",
        "quick_replies": ["Today / suddenly", "This week", "Gradual over weeks", "Intermittent"],
    },
    {
        "id": "warning_lights",
        "question": "Are there any other warning lights or fault codes currently active?",
        "type": "text",
        "why_we_ask": "Multiple codes can point to a shared root cause (e.g., wiring harness, ECM issue).",
        "quick_replies": ["No other lights", "Check engine + other", "Multiple codes", "Not sure"],
    },
    {
        "id": "recent_maintenance",
        "question": "Has any maintenance or repair been performed on this vehicle in the last 30 days?",
        "type": "text",
        "why_we_ask": "Recent work may have introduced the problem (loose connector, wrong part, incomplete procedure).",
        "quick_replies": ["No recent work", "Oil / filter change", "Major repair done", "Unknown"],
    },
    {
        "id": "operating_conditions",
        "question": "Under what conditions does the issue occur?",
        "type": "text",
        "why_we_ask": "Load-dependent symptoms narrow the diagnosis to specific components (turbo, injectors, fuel supply).",
        "quick_replies": ["At idle", "Under load / uphill", "Cold start only", "All conditions"],
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
    fault_code = state.get("fault_code", "").upper()

    confidence_delta = 0.0
    safety_flag = False

    if fault_code == "P0191":
        # ── P0191-specific rules ────────────────────────────────────────

        # Rule 1: Visible leak -> ALWAYS escalate (safety override)
        if evidence.get("visible_leak") in ["Yes, I see a leak", "yes", True]:
            safety_flag = True
            state["escalation_reason"] = (
                "Safety risk: visible fuel leak detected. "
                "Fire hazard, immediate escalation required."
            )

        # Rule 2: Very low fuel pressure -> confirms pump or filter issue
        psi = evidence.get("fuel_pressure_psi", "")
        if "Under 500" in str(psi) or (isinstance(psi, (int, float)) and psi < 500):
            if "pump" in top_cause or "filter" in top_cause:
                confidence_delta += 0.15
            else:
                confidence_delta += 0.05
        elif "870+" in str(psi) or (isinstance(psi, (int, float)) and psi >= 870):
            if "sensor" in top_cause:
                confidence_delta += 0.12
            else:
                confidence_delta -= 0.10

        # Rule 3: Overdue filter -> confirms filter as cause
        miles = evidence.get("miles_since_filter", "")
        if "Over 15,000" in str(miles):
            if "filter" in top_cause:
                confidence_delta += 0.10

        # Rule 4: Cold start issues -> confirms pump weakness
        if evidence.get("cold_start_issue") in ["Yes, hard cold start", "yes", True]:
            if "pump" in top_cause:
                confidence_delta += 0.08

    else:
        # ── Generic rules for all other fault codes ─────────────────────

        # Rule G1: Sudden onset -> confirms acute failure
        onset = str(evidence.get("symptom_onset", "")).lower()
        if "today" in onset or "suddenly" in onset:
            confidence_delta += 0.08
        elif "gradual" in onset:
            confidence_delta += 0.04

        # Rule G2: Multiple codes active -> more complexity, lower certainty
        warnings = str(evidence.get("warning_lights", "")).lower()
        if "multiple" in warnings or "other" in warnings:
            confidence_delta -= 0.05

        # Rule G3: Recent maintenance -> narrows timeline
        maintenance = str(evidence.get("recent_maintenance", "")).lower()
        if "major repair" in maintenance or "oil" in maintenance:
            confidence_delta += 0.05

        # Rule G4: Specific operating conditions -> helps narrow diagnosis
        conditions = str(evidence.get("operating_conditions", "")).lower()
        if "all conditions" in conditions:
            confidence_delta += 0.06
        elif "idle" in conditions or "load" in conditions or "cold" in conditions:
            confidence_delta += 0.04

    # Update state
    updated = min(max(base_confidence + confidence_delta, 0.05), 0.97)
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
    return GENERIC_EVIDENCE_QUESTIONS
