# agents/escalation_agent.py
"""
Escalation Agent — decides if human approval is required based on
confidence, cost, urgency, and safety flags.
If all clear, generates repair steps directly.
LangGraph node function: reads from and writes to TraceState.
"""

from orchestrator.state import TraceState

COST_THRESHOLD = 500        # USD — repairs over this need approval
CONFIDENCE_THRESHOLD = 0.70  # below this → escalate


def escalation_agent(state: TraceState) -> TraceState:
    """
    LangGraph node: decides if human approval is required.
    When escalating, the workflow pauses (returns to FastAPI with status "escalated").
    """
    confidence = state.get("updated_confidence") or state.get("top_confidence", 0.0)
    triage_results = state.get("triage_results", [])
    top_result = triage_results[0] if triage_results else {}

    escalation_reasons = []

    # Check 1: Safety flag from evidence agent
    if state.get("requires_human_approval"):
        escalation_reasons.append(
            state.get("escalation_reason", "Safety risk detected")
        )

    # Check 2: Low confidence
    if confidence < CONFIDENCE_THRESHOLD:
        escalation_reasons.append(
            f"AI confidence is {confidence:.0%} — below the 70% threshold "
            f"required to proceed safely"
        )

    # Check 3: High cost
    estimated_cost = top_result.get("estimated_cost_usd", 0)
    if estimated_cost > COST_THRESHOLD:
        escalation_reasons.append(
            f"Estimated repair cost is ${estimated_cost} — exceeds "
            f"${COST_THRESHOLD} approval threshold"
        )

    # Check 4: High urgency
    if top_result.get("urgency") == "high":
        escalation_reasons.append("High-urgency repair — senior review required")

    if escalation_reasons:
        state["requires_human_approval"] = True
        state["escalation_reason"] = " | ".join(escalation_reasons)
        state["workflow_status"] = "escalated"
        state["human_approved"] = None  # pending
    else:
        # All clear — generate repair steps directly
        state["requires_human_approval"] = False
        state["workflow_status"] = "approved"
        state["repair_steps"] = generate_repair_steps(
            state["fault_code"],
            state.get("top_cause", ""),
            state.get("evidence_collected", {}),
        )

    return state


def generate_repair_steps(fault_code: str, cause: str, evidence: dict) -> list:
    """
    Returns step-by-step repair instructions based on diagnosed cause.
    These are shown to the field tech after approval.
    """
    cause_lower = cause.lower()

    base_steps = {
        "fuel pump": [
            "1. Safety first: ensure engine is off and cool. Remove ignition key.",
            "2. Locate the lift pump (mounted on engine block, driver's side).",
            "3. Relieve fuel system pressure: remove fuel cap, crank engine 3 sec with fuel pump fuse removed.",
            "4. Disconnect fuel lines — have rags ready, expect residual fuel.",
            "5. Remove 4 mounting bolts (13mm socket) and extract pump.",
            "6. Install new pump. Torque bolts to 18 ft-lbs.",
            "7. Reconnect fuel lines. Reinstall fuse. Prime system: key on (don't start) for 30 sec, repeat 3x.",
            "8. Start engine. Verify fuel pressure reads above 870 PSI on scanner.",
            "9. Clear P0191 code. Run engine 5 min and confirm code does not return.",
            "10. Log repair in TRACE and mark as complete.",
        ],
        "fuel filter": [
            "1. Safety first: engine off, cool, ignition key removed.",
            "2. Locate fuel filter housing (on engine, passenger side).",
            "3. Place drain pan under filter housing.",
            "4. Loosen drain plug at bottom of housing — drain fuel completely.",
            "5. Unscrew filter housing cap (use filter wrench if needed).",
            "6. Remove old filter element.",
            "7. Install new OEM filter element (Fleetguard FF5706 or equivalent).",
            "8. Reinstall housing cap. Torque to 25 ft-lbs.",
            "9. Prime fuel system: key on 30 sec x 3 cycles before starting.",
            "10. Start engine. Check for leaks at filter housing.",
            "11. Clear P0191 code and verify it does not return after 2 drive cycles.",
        ],
        "sensor": [
            "1. Safety first: engine off, cool, ignition key removed.",
            "2. Locate Fuel Rail Pressure (FRP) sensor — screwed into the fuel rail, top of engine.",
            "3. Disconnect electrical connector from sensor.",
            "4. Using a 27mm crow's foot wrench, unscrew sensor.",
            "5. Apply thread sealant to new sensor threads (do NOT get sealant in sensor tip).",
            "6. Install new FRP sensor. Torque to 15 ft-lbs.",
            "7. Reconnect electrical connector — should click securely.",
            "8. Start engine. Verify scanner reads 870+ PSI at key-on.",
            "9. Clear P0191 code. Confirm it does not return.",
            "10. Log repair in TRACE.",
        ],
    }

    # Match cause to step list
    for key, steps in base_steps.items():
        if key in cause_lower:
            return steps

    # Generic fallback
    return [
        "1. Consult official Cummins ISB service manual for your engine year.",
        "2. Reference TSB 18-001-13 for P0191 diagnostic procedure.",
        f"3. Diagnosed cause: {cause}.",
        "4. Contact senior engineer for specific repair steps for this cause.",
        "5. Log all actions in TRACE.",
    ]
