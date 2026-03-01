# orchestrator/workflow.py
"""
LangGraph orchestrator — wires Triage → Evidence → Escalation into
one stateful pipeline with SQLite checkpointing for pause/resume.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from orchestrator.state import TraceState
from agents.triage_agent import triage_agent
from agents.evidence_agent import evidence_agent
from agents.escalation_agent import escalation_agent, generate_repair_steps

# Default path — Zion can override via env var or config
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
            "escalated": END,   # pause — wait for human approval
            "resolved": END,    # done — repair steps ready
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


def resume_after_approval(
    session_id: str,
    approved: bool,
    approved_by: str,
) -> TraceState:
    """
    Called by FastAPI when the back-office engineer clicks Approve/Reject.
    Resumes the paused workflow with the human decision.
    """
    graph = _build_graph()

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": session_id}}

        # Build the update with human decision
        update = {
            "human_approved": approved,
            "approved_by": approved_by,
            "workflow_status": "approved" if approved else "rejected",
        }

        # If approved, generate repair steps from the saved state
        if approved:
            current_state = app.get_state(config)
            cause = current_state.values.get("top_cause", "")
            fault_code = current_state.values.get("fault_code", "P0191")
            evidence_data = current_state.values.get("evidence_collected", {})
            update["repair_steps"] = generate_repair_steps(
                fault_code, cause, evidence_data
            )

        final_state = app.invoke(update, config=config)

    return final_state
