# agents/escalation_agent.py
"""
Escalation Agent: decides if human approval is required based on
confidence, cost, urgency, and safety flags.
If all clear, generates repair steps directly.
LangGraph node function: reads from and writes to TraceState.
"""

import json

from orchestrator.state import TraceState

COST_THRESHOLD = 500        # USD; repairs over this need approval
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
            f"AI confidence is {confidence:.0%}, which is below the 70% threshold "
            f"required to proceed safely"
        )

    # Check 3: High cost
    estimated_cost = top_result.get("estimated_cost_usd", 0)
    if estimated_cost > COST_THRESHOLD:
        escalation_reasons.append(
            f"Estimated repair cost is ${estimated_cost}, which exceeds "
            f"${COST_THRESHOLD} approval threshold"
        )

    # Check 4: High urgency
    if top_result.get("urgency") == "high":
        escalation_reasons.append("High(-) urgency repair: senior review required")

    if escalation_reasons:
        state["requires_human_approval"] = True
        state["escalation_reason"] = " | ".join(escalation_reasons)
        state["workflow_status"] = "escalated"
        state["human_approved"] = None  # pending
    else:
        # All clear, generate repair steps directly
        state["requires_human_approval"] = False
        state["workflow_status"] = "approved"
        state["repair_steps"] = generate_repair_steps(
            state["fault_code"],
            state.get("top_cause", ""),
            state.get("evidence_collected", {}),
        )

    return state


REPAIR_STEPS_PROMPT = """You are a certified Cummins diesel engine repair expert with 20 years of field experience.

A diagnosis has been completed and approved. Generate step-by-step repair instructions for a field technician.

- Fault Code: {fault_code}
- Diagnosed Cause: {cause}
- Evidence Collected: {evidence}

Respond ONLY in this exact JSON format, no extra text:
{{
  "steps": [
    "1. First step with specific details (tools, torque specs, part numbers where applicable)",
    "2. Second step...",
    "3. Continue with all necessary steps..."
  ]
}}

Rules:
- Always start with a safety step (engine off, key removed, etc.)
- Include specific tools, torque specs, and part numbers where applicable
- Include verification/testing steps after the repair
- End with clearing codes and logging the repair in TRACE
- Be specific to the diagnosed cause, not generic
- Typically 7 to 12 steps"""


def generate_repair_steps(fault_code: str, cause: str, evidence: dict) -> list:
    """
    Returns step-by-step repair instructions based on diagnosed cause.
    Uses the local LLM via Ollama for context-aware generation.
    Falls back to a generic template if the LLM is unavailable.
    """
    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from utils.llm import get_llm

        llm, _ = get_llm()

        prompt = PromptTemplate(
            input_variables=["fault_code", "cause", "evidence"],
            template=REPAIR_STEPS_PROMPT,
        )

        chain = prompt | llm | StrOutputParser()

        raw_response = chain.invoke({
            "fault_code": fault_code,
            "cause": cause,
            "evidence": json.dumps(evidence) if evidence else "None collected",
        })

        # Strip markdown code fences if the LLM wraps its response
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
        steps = result.get("steps", [])
        if steps and len(steps) >= 3:
            return steps

    except Exception:
        pass

    # Fallback: generic steps if LLM is unavailable or fails
    return [
        "1. Safety first: ensure engine is off and cool. Remove ignition key.",
        f"2. Verify fault code {fault_code} is active using diagnostic scanner.",
        f"3. Diagnosed cause: {cause}.",
        "4. Consult official Cummins ISB service manual for the specific repair procedure.",
        "5. Perform the repair following OEM specifications and torque values.",
        "6. After repair, clear all fault codes with the diagnostic scanner.",
        "7. Start the engine and verify the fault code does not return.",
        "8. Perform a test drive (minimum 20 minutes, varied RPM) to confirm the fix.",
        "9. Log all actions in TRACE and mark the repair as complete.",
    ]
