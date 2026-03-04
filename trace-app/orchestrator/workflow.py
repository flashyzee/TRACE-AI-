# orchestrator/workflow.py
"""
LangGraph orchestrator: wires Triage → Evidence → Escalation into
one stateful pipeline with SQLite checkpointing for pause/resume.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from orchestrator.state import TraceState
from agents.triage_agent import triage_agent
from agents.evidence_agent import evidence_agent
from agents.escalation_agent import escalation_agent, generate_repair_steps

# Default path; Zion can override via env var or config
DB_PATH = "trace.db"


# ── Routing logic ────────────────────────────────────────────────────────

def route_after_escalation(state: TraceState) -> str:
    """
    After escalation agent runs, decide where to go next.
    If human approval needed → END (FastAPI will poll for approval).
    If no approval needed → END (repair steps already generated).
    """
    if state.get("requires_human_approval"):
        return "escalated"   # workflow pauses here
    return "resolved"        # workflow completes, repair steps ready


# ── Build the graph ──────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    """Builds the state graph (without compiling). Internal helper."""
    graph = StateGraph(TraceState)

    # Add nodes (each node = one agent function)
    graph.add_node("triage", triage_agent)
    graph.add_node("evidence", evidence_agent)
    graph.add_node("escalation", escalation_agent)

    # Set entry point
    graph.set_entry_point("triage")

    # Edges: triage → evidence → escalation
    graph.add_edge("triage", "evidence")
    graph.add_edge("evidence", "escalation")

    # Conditional edge after escalation
    graph.add_conditional_edges(
        "escalation",
        route_after_escalation,
        {
            "escalated": END,   # pause, wait for human approval
            "resolved": END,    # done, repair steps ready
        },
    )

    return graph


# ── Main entry point ─────────────────────────────────────────────────────

def run_workflow(
    fault_code: str,
    symptoms: str,
    session_id: str,
    evidence: dict = None,
) -> TraceState:
    """
    Main function called by FastAPI.

    Args:
        fault_code: e.g. "P0191"
        symptoms: e.g. "rough idle, black smoke"
        session_id: unique ID for this repair session (from Zion's FastAPI)
        evidence: dict of evidence answers (from frontend, optional)

    Returns:
        Final state dict with all agent outputs
    """
    graph = _build_graph()

    # SqliteSaver.from_conn_string is a context manager
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)

        initial_state: TraceState = {
            "session_id": session_id,
            "fault_code": fault_code.upper(),
            "initial_symptoms": symptoms,
            "triage_results": None,
            "top_cause": None,
            "top_confidence": None,
            "evidence_collected": evidence or {},
            "evidence_complete": False,
            "updated_confidence": None,
            "requires_human_approval": None,
            "escalation_reason": None,
            "human_approved": None,
            "approved_by": None,
            "repair_steps": None,
            "workflow_status": "started",
            "model_used": "llama3.1",
            "error": None,
        }

        config = {"configurable": {"thread_id": session_id}}
        final_state = app.invoke(initial_state, config=config)

    return final_state


def run_triage_only(
    fault_code: str,
    symptoms: str,
    session_id: str,
) -> TraceState:
    """
    Step 1 for Rasa flow: runs ONLY the triage agent (LLM diagnosis).
    Returns state with triage_results, top_cause, top_confidence.
    Does NOT run evidence or escalation. Rasa collects evidence first.

    Called by FastAPI: POST /triage
    """
    llm_state: TraceState = {
        "session_id": session_id,
        "fault_code": fault_code.upper(),
        "initial_symptoms": symptoms,
        "triage_results": None,
        "top_cause": None,
        "top_confidence": None,
        "evidence_collected": {},
        "evidence_complete": False,
        "updated_confidence": None,
        "requires_human_approval": None,
        "escalation_reason": None,
        "human_approved": None,
        "approved_by": None,
        "repair_steps": None,
        "workflow_status": "started",
        "model_used": "llama3.1",
        "error": None,
    }

    # Run triage agent directly (no graph needed for a single step)
    result = triage_agent(llm_state)

    # Save checkpoint so evidence step can pick up from here
    graph = _build_graph()
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": session_id}}
        app.update_state(config, result)

    return result


def run_evidence_and_escalation(
    session_id: str,
    evidence: dict,
) -> TraceState:
    """
    Step 2 for Rasa flow: after Rasa has collected evidence answers,
    runs evidence agent (confidence update) + escalation agent.
    Picks up the triage results saved by run_triage_only().

    Called by FastAPI: POST /evidence
    """
    graph = _build_graph()

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": session_id}}

        # Retrieve saved triage state
        saved = app.get_state(config)
        state_values = dict(saved.values)

        # Inject the evidence answers collected by Rasa
        state_values["evidence_collected"] = evidence

        # Run evidence agent → updates confidence
        state_values = evidence_agent(state_values)

        # Run escalation agent → decides approval / generates repair steps
        state_values = escalation_agent(state_values)

        # Save final state to checkpoint (for resume_after_approval if needed)
        app.update_state(config, state_values)

    return state_values


def resume_after_approval(
    session_id: str,
    approved: bool,
    approved_by: str,
) -> TraceState:
    """
    Called by FastAPI when the back-office engineer clicks Approve/Reject.
    Updates the checkpointed state with the human decision (does NOT
    re-run the agent pipeline).
    """
    graph = _build_graph()

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": session_id}}

        # Get the saved state from when the workflow was paused
        current_state = app.get_state(config)
        state_values = dict(current_state.values)

        # Apply human decision
        state_values["human_approved"] = approved
        state_values["approved_by"] = approved_by
        state_values["workflow_status"] = "approved" if approved else "rejected"

        # If approved, generate repair steps
        if approved:
            state_values["repair_steps"] = generate_repair_steps(
                state_values.get("fault_code", "P0191"),
                state_values.get("top_cause", ""),
                state_values.get("evidence_collected", {}),
            )

        # Save updated state to the checkpoint
        app.update_state(config, state_values)

    return state_values
