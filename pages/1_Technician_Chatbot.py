import streamlit as st
import time
import random
from datetime import datetime

st.set_page_config(page_title="TRACE AI — Chatbot", page_icon="💬", layout="wide")

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .quick-reply {
        display: inline-block;
        background: #16213E;
        border: 1px solid #F59E0B;
        border-radius: 20px;
        padding: 0.4rem 1rem;
        margin: 0.2rem;
        color: #F59E0B;
        font-size: 0.85rem;
    }
    .confidence-bar {
        background: #16213E;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #F59E0B;
        margin: 0.5rem 0;
    }
    .cause-card {
        background: #16213E;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #2D3A5C;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Mock Data ────────────────────────────────────────────────────────────────
FAULT_CODES = {
    "P0191": {
        "name": "Fuel Rail Pressure Sensor Circuit Range/Performance",
        "system": "Fuel",
        "severity": "High",
    },
    "P0087": {
        "name": "Fuel Rail/System Pressure Too Low",
        "system": "Fuel",
        "severity": "High",
    },
    "P0093": {
        "name": "Fuel System Large Leak Detected",
        "system": "Fuel",
        "severity": "Critical",
    },
    "P0234": {
        "name": "Turbocharger Overboost Condition",
        "system": "Turbo",
        "severity": "High",
    },
    "P0299": {
        "name": "Turbocharger Underboost",
        "system": "Turbo",
        "severity": "High",
    },
    "P0401": {
        "name": "EGR Insufficient Flow",
        "system": "Emissions",
        "severity": "Medium",
    },
}

MOCK_TRIAGE_RESULTS = {
    "P0191": [
        {
            "cause": "Weak / failing fuel lift pump",
            "confidence": 0.72,
            "explanation": "Low rail pressure at idle is the classic lift-pump symptom on ISB/ISX.",
            "urgency": "high",
            "estimated_cost_usd": 650,
        },
        {
            "cause": "Clogged fuel filter (overdue replacement)",
            "confidence": 0.18,
            "explanation": "Restricted filter can mimic pump failure; check service interval.",
            "urgency": "medium",
            "estimated_cost_usd": 120,
        },
        {
            "cause": "Fuel rail pressure sensor drift / failure",
            "confidence": 0.10,
            "explanation": "Sensor reading out of range but actual pressure is normal.",
            "urgency": "low",
            "estimated_cost_usd": 280,
        },
    ],
}

EVIDENCE_QUESTIONS = [
    {
        "id": "fuel_pressure_psi",
        "question": "What is the fuel rail pressure reading on your scanner right now?",
        "why_we_ask": "Normal is 870+ PSI at key-on. Below this confirms low pressure issue.",
        "quick_replies": ["Under 500 PSI", "500-870 PSI", "870+ PSI", "Scanner not available"],
    },
    {
        "id": "miles_since_filter",
        "question": "Approximately how many miles since the last fuel filter change?",
        "why_we_ask": "Cummins recommends filter change every 15,000 miles.",
        "quick_replies": ["Under 5,000 mi", "5,000-15,000 mi", "Over 15,000 mi", "Unknown"],
    },
    {
        "id": "visible_leak",
        "question": "Can you see any fuel leak, wet spots, or smell fuel near the rail area?",
        "why_we_ask": "A fuel leak is a SAFETY RISK and triggers immediate escalation.",
        "quick_replies": ["Yes, I see a leak", "No leak visible", "Cannot access area"],
    },
    {
        "id": "cold_start_issue",
        "question": "Does the truck have trouble starting when the engine is cold?",
        "why_we_ask": "Cold start issues point to lift pump weakness rather than sensor failure.",
        "quick_replies": ["Yes, hard cold start", "No cold start issues", "Not sure"],
    },
]

# ── Session State Initialization ─────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_phase" not in st.session_state:
    st.session_state.chat_phase = "idle"  # idle → triage → evidence → result
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "evidence_answers" not in st.session_state:
    st.session_state.evidence_answers = {}
if "sidebar_submitted" not in st.session_state:
    st.session_state.sidebar_submitted = False

# ── Sidebar: Structured Input Form ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Vehicle Info")
    st.caption("Fill in details before starting the chat.")

    with st.form("vehicle_form"):
        fault_code = st.selectbox(
            "Fault Code (DTC)",
            options=[""] + list(FAULT_CODES.keys()),
            format_func=lambda x: f"{x} — {FAULT_CODES[x]['name']}" if x else "Select a fault code...",
        )
        vehicle_id = st.text_input("Vehicle / Unit ID", placeholder="e.g. UNIT-4471")
        mileage = st.number_input("Current Mileage", min_value=0, step=1000, value=0)
        symptoms = st.text_area(
            "Initial Symptoms",
            placeholder="e.g. rough idle, black smoke, loss of power under load",
        )
        submitted = st.form_submit_button("Start Diagnosis", type="primary")

    if submitted and fault_code:
        st.session_state.sidebar_submitted = True
        st.session_state.fault_code = fault_code
        st.session_state.vehicle_id = vehicle_id or "UNIT-0000"
        st.session_state.mileage = mileage
        st.session_state.symptoms = symptoms or "No symptoms described"
        st.session_state.chat_phase = "triage"
        st.session_state.chat_messages = []
        st.session_state.current_question_idx = 0
        st.session_state.evidence_answers = {}
        st.rerun()

    st.divider()
    st.markdown("**Navigation**")
    st.page_link("ui.py", label="Home", icon="🏠")
    st.page_link("pages/1_Technician_Chatbot.py", label="Chatbot", icon="💬")
    st.page_link("pages/2_Approval_Dashboard.py", label="Dashboard", icon="📋")

# ── Main Chat Area ───────────────────────────────────────────────────────────
st.markdown("## 💬 Technician Chatbot")
st.caption(
    "Report fault codes and symptoms through the sidebar, then chat with TRACE AI "
    "to walk through the diagnosis."
)

# Helper to add messages
def add_bot_message(content):
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": content, "time": datetime.now().strftime("%H:%M")}
    )

def add_user_message(content):
    st.session_state.chat_messages.append(
        {"role": "user", "content": content, "time": datetime.now().strftime("%H:%M")}
    )

# ── Phase: Triage (auto-triggered after sidebar submit) ─────────────────────
if st.session_state.chat_phase == "triage" and not any(
    "Triage" in m.get("content", "") for m in st.session_state.chat_messages
):
    fc = st.session_state.fault_code
    fc_info = FAULT_CODES.get(fc, {})

    add_user_message(
        f"**New case submitted**\n\n"
        f"- **Fault code:** {fc} — {fc_info.get('name', 'Unknown')}\n"
        f"- **Vehicle:** {st.session_state.vehicle_id}\n"
        f"- **Mileage:** {st.session_state.mileage:,} mi\n"
        f"- **Symptoms:** {st.session_state.symptoms}"
    )

    # Build triage response
    results = MOCK_TRIAGE_RESULTS.get(fc)
    if results:
        triage_text = "**🔍 Triage Complete — Top 3 Probable Causes:**\n\n"
        for i, r in enumerate(results, 1):
            bar_fill = int(r["confidence"] * 20)
            bar = "█" * bar_fill + "░" * (20 - bar_fill)
            triage_text += (
                f"**{i}. {r['cause']}**\n"
                f"`{bar}` {r['confidence']:.0%} confidence\n"
                f"_{r['explanation']}_\n"
                f"Urgency: **{r['urgency']}** | Est. cost: **${r['estimated_cost_usd']:,}**\n\n"
            )
        triage_text += (
            "---\n"
            "I need to ask you a few follow-up questions to refine this diagnosis. "
            "Ready when you are."
        )
        add_bot_message(triage_text)
        st.session_state.triage_data = results
    else:
        add_bot_message(
            f"I don't have specialized triage data for **{fc}** yet. "
            f"Let me ask some general follow-up questions."
        )
        st.session_state.triage_data = [
            {"cause": "General diagnosis needed", "confidence": 0.50, "urgency": "medium", "estimated_cost_usd": 0}
        ]

    st.session_state.chat_phase = "evidence"
    st.rerun()

# ── Phase: Evidence collection (question by question) ────────────────────────
if st.session_state.chat_phase == "evidence":
    idx = st.session_state.current_question_idx
    if idx < len(EVIDENCE_QUESTIONS) and not any(
        EVIDENCE_QUESTIONS[idx]["question"] in m.get("content", "")
        for m in st.session_state.chat_messages
        if m["role"] == "assistant"
    ):
        q = EVIDENCE_QUESTIONS[idx]
        q_text = (
            f"**Question {idx + 1} of {len(EVIDENCE_QUESTIONS)}:** {q['question']}\n\n"
            f"_Why we ask: {q['why_we_ask']}_"
        )
        add_bot_message(q_text)
        st.rerun()

# ── Display all chat messages ────────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        st.caption(msg.get("time", ""))

# ── Quick reply buttons (for evidence phase) ────────────────────────────────
if st.session_state.chat_phase == "evidence":
    idx = st.session_state.current_question_idx
    if idx < len(EVIDENCE_QUESTIONS):
        q = EVIDENCE_QUESTIONS[idx]
        st.markdown("**Quick replies:**")
        cols = st.columns(len(q["quick_replies"]))
        for i, reply in enumerate(q["quick_replies"]):
            with cols[i]:
                if st.button(reply, key=f"qr_{idx}_{i}", use_container_width=True):
                    add_user_message(reply)
                    st.session_state.evidence_answers[q["id"]] = reply
                    st.session_state.current_question_idx += 1

                    # Check if all questions answered
                    if st.session_state.current_question_idx >= len(EVIDENCE_QUESTIONS):
                        st.session_state.chat_phase = "result"
                    st.rerun()

# ── Phase: Result summary ───────────────────────────────────────────────────
if st.session_state.chat_phase == "result" and not any(
    "Evidence Summary" in m.get("content", "") for m in st.session_state.chat_messages
):
    answers = st.session_state.evidence_answers
    triage = st.session_state.get("triage_data", [{}])
    top = triage[0] if triage else {}

    # Simulate confidence adjustment
    base_conf = top.get("confidence", 0.50)
    delta = 0.0

    if "Under 500" in str(answers.get("fuel_pressure_psi", "")):
        delta += 0.12
    if "Over 15,000" in str(answers.get("miles_since_filter", "")):
        delta += 0.08
    if "cold start" in str(answers.get("cold_start_issue", "")).lower():
        delta += 0.06
    safety_flag = "leak" in str(answers.get("visible_leak", "")).lower()
    if safety_flag:
        delta += 0.0  # safety flag doesn't change confidence, triggers escalation

    updated_conf = min(base_conf + delta, 0.97)
    needs_escalation = updated_conf < 0.70 or top.get("estimated_cost_usd", 0) > 500 or safety_flag

    # Build summary
    summary = "**📊 Evidence Summary & Updated Diagnosis**\n\n"
    summary += "| Question | Your Answer |\n|---|---|\n"
    for q in EVIDENCE_QUESTIONS:
        ans = answers.get(q["id"], "—")
        summary += f"| {q['question'][:50]}... | **{ans}** |\n"

    summary += f"\n\n**Updated confidence:** {base_conf:.0%} → **{updated_conf:.0%}**\n"
    summary += f"**Top cause:** {top.get('cause', 'Unknown')}\n\n"

    if safety_flag:
        summary += (
            "⚠️ **SAFETY ALERT:** Visible fuel leak detected. "
            "This case has been **automatically escalated** to a manager for approval.\n\n"
        )
    elif needs_escalation:
        reason_parts = []
        if updated_conf < 0.70:
            reason_parts.append(f"confidence below 70% ({updated_conf:.0%})")
        if top.get("estimated_cost_usd", 0) > 500:
            reason_parts.append(f"estimated cost ${top['estimated_cost_usd']:,}")
        summary += (
            f"🔶 **Escalation required:** {', '.join(reason_parts)}. "
            f"This case has been sent to the **Approval Dashboard** for manager review.\n\n"
        )
    else:
        summary += "✅ **Auto-approved** — confidence is high and cost is within limits.\n\n"

    summary += (
        "---\n"
        "You can view the case status on the **Approval Dashboard** page. "
        "Thank you for providing the evidence!"
    )

    add_bot_message(summary)
    st.session_state.chat_phase = "done"
    st.rerun()

# ── Chat input (free text fallback) ─────────────────────────────────────────
if st.session_state.chat_phase == "done":
    user_input = st.chat_input("Type a follow-up question...")
    if user_input:
        add_user_message(user_input)
        add_bot_message(
            "Thanks for the follow-up. In the full version, I'd use the LLM to answer. "
            "For now, please check the **Approval Dashboard** for case status, or start a "
            "new diagnosis from the sidebar."
        )
        st.rerun()
elif st.session_state.chat_phase == "idle":
    st.info("👈 Fill in the **Vehicle Info** form in the sidebar to start a diagnosis.")
elif st.session_state.chat_phase == "evidence":
    user_input = st.chat_input("Or type your answer...")
    if user_input:
        idx = st.session_state.current_question_idx
        if idx < len(EVIDENCE_QUESTIONS):
            q = EVIDENCE_QUESTIONS[idx]
            add_user_message(user_input)
            st.session_state.evidence_answers[q["id"]] = user_input
            st.session_state.current_question_idx += 1
            if st.session_state.current_question_idx >= len(EVIDENCE_QUESTIONS):
                st.session_state.chat_phase = "result"
            st.rerun()
