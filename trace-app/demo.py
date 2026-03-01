"""
TRACE AI Demo Script
====================
Run this to see the full AI pipeline in action.

Prerequisites:
  1. pip install -r requirements.txt
  2. ollama serve        (in a separate terminal)
  3. ollama pull llama3.1  (one-time download)

Usage:
  cd trace-app
  python demo.py
"""

import json
import time
from orchestrator.workflow import run_workflow, resume_after_approval
from agents.evidence_agent import get_evidence_questions


def print_divider(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    session_id = f"DEMO-{int(time.time())}"

    # ── Step 1: Show evidence questions ──────────────────────────
    print_divider("STEP 1: Evidence Questions for P0191")
    questions = get_evidence_questions("P0191")
    for q in questions:
        print(f"  [{q['id']}]")
        print(f"    Q: {q['question']}")
        print(f"    Quick replies: {q['quick_replies']}")
        print()

    # ── Step 2: Run full pipeline ────────────────────────────────
    print_divider("STEP 2: Running Triage → Evidence → Escalation")
    print("  Fault code:  P0191")
    print("  Symptoms:    rough idle, black smoke, hard cold start")
    print("  Evidence:    Under 500 PSI, filter overdue, no leak, hard cold start")
    print("\n  Calling LLM (this may take 10-30 seconds)...\n")

    result = run_workflow(
        fault_code="P0191",
        symptoms="rough idle, black smoke, hard cold start",
        session_id=session_id,
        evidence={
            "fuel_pressure_psi": "Under 500 PSI",
            "miles_since_filter": "Over 15,000 mi",
            "visible_leak": "No leak visible",
            "cold_start_issue": "Yes, hard cold start",
        },
    )

    # ── Step 3: Show triage results ──────────────────────────────
    print_divider("STEP 3: Triage Agent Results")
    print(f"  Model used: {result['model_used']}")
    if result["triage_results"]:
        for c in result["triage_results"]:
            rank = c.get("rank", "?")
            conf = c["confidence"]
            print(f"  #{rank}  {c['cause']}")
            print(f"       Confidence: {conf:.0%}  |  Urgency: {c.get('urgency', 'N/A')}  |  Cost: ${c.get('estimated_cost_usd', 'N/A')}")
            print(f"       {c.get('explanation', '')}")
            print()
    if result.get("error"):
        print(f"  Error: {result['error']}")

    # ── Step 4: Show evidence + escalation results ───────────────
    print_divider("STEP 4: Evidence & Escalation Results")
    print(f"  Triage confidence:   {result['top_confidence']:.0%}")
    print(f"  Updated confidence:  {result['updated_confidence']:.0%}")
    print(f"  Needs approval:      {result['requires_human_approval']}")
    print(f"  Escalation reason:   {result.get('escalation_reason', 'N/A')}")
    print(f"  Workflow status:     {result['workflow_status']}")

    # ── Step 5: Simulate human approval ──────────────────────────
    if result["requires_human_approval"]:
        print_divider("STEP 5: Senior Engineer Approves")
        print("  Simulating: Eng_Johnson clicks 'Approve'...\n")

        approved_result = resume_after_approval(
            session_id=session_id,
            approved=True,
            approved_by="Eng_Johnson",
        )

        print(f"  Status:         {approved_result['workflow_status']}")
        print(f"  Human approved: {approved_result['human_approved']}")
        print(f"  Approved by:    {approved_result['approved_by']}")
        print()

        if approved_result.get("repair_steps"):
            print("  Repair steps delivered to tech:")
            for step in approved_result["repair_steps"]:
                print(f"    {step}")
    else:
        print_divider("STEP 5: No Escalation Needed")
        print("  Tech can proceed directly with repair steps:")
        if result.get("repair_steps"):
            for step in result["repair_steps"]:
                print(f"    {step}")

    # ── Summary ──────────────────────────────────────────────────
    print_divider("DEMO COMPLETE")
    print(f"  Session ID:  {session_id}")
    print(f"  Flow:        Triage → Evidence → Escalation → Approval → Repair Steps")
    print(f"  Model:       {result['model_used']}")
    print()
    print()


if __name__ == "__main__":
    main()
