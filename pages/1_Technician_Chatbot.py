import streamlit as st
import time
import random
import os
from datetime import datetime
from PIL import Image

_logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo.png"))
st.set_page_config(page_title="TRACE AI Chatbot", page_icon=_logo, layout="wide")

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body { font-family: 'Inter', sans-serif; }

    /* ── Animations ────────────────────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.3); }
        50% { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
    }
    @keyframes progressFill {
        from { width: 0%; }
    }
    @keyframes typingDot {
        0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
        30% { opacity: 1; transform: scale(1); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* ── Breadcrumb ─────────────────────────────────────────────────────── */
    .breadcrumb {
        font-size: 0.82rem;
        color: #6B7280;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .breadcrumb a { color: #6B7280; text-decoration: none; }
    .breadcrumb a:hover { color: #F59E0B; }
    .breadcrumb .active { color: #F59E0B; font-weight: 600; }
    .breadcrumb .sep { color: #4B5563; }

    /* ── Chat Bubbles ──────────────────────────────────────────────────── */
    .chat-container {
        max-width: 100%;
        padding: 0.5rem 0;
    }
    .chat-bubble {
        max-width: 85%;
        padding: 1rem 1.2rem;
        border-radius: 18px;
        margin-bottom: 0.4rem;
        line-height: 1.55;
        font-size: 0.92rem;
        animation: fadeInUp 0.3s ease-out;
        position: relative;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: #000;
        margin-left: auto;
        border-bottom-right-radius: 6px;
        font-weight: 500;
    }
    .chat-bubble-bot {
        background: linear-gradient(145deg, #1e2a4a, #16213E);
        color: #E5E7EB;
        border: 1px solid #2D3A5C;
        margin-right: auto;
        border-bottom-left-radius: 6px;
    }
    .chat-row {
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
        animation: fadeInUp 0.35s ease-out;
    }
    .chat-row-user { justify-content: flex-end; }
    .chat-row-bot { justify-content: flex-start; }
    .chat-avatar {
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .chat-avatar-bot { background: #16213E; border: 1.5px solid #F59E0B; }
    .chat-avatar-user { background: #F59E0B; color: #000; }
    .chat-time {
        font-size: 0.7rem;
        color: #6B7280;
        margin-top: 0.15rem;
        padding: 0 0.5rem;
    }
    .chat-time-user { text-align: right; }
    .chat-time-bot { text-align: left; }

    /* ── Quick Reply Buttons ───────────────────────────────────────────── */
    .qr-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.5rem 0 1rem;
        animation: fadeInUp 0.4s ease-out;
    }

    /* ── Sidebar Styling ───────────────────────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 0.1rem 0 0.15rem;
    }
    .sidebar-brand-name {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F59E0B, #EF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-brand-version {
        font-size: 0.75rem;
        color: #6B7280;
    }
    .sync-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .sync-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
        animation: pulseGlow 2s ease-in-out infinite;
    }
    .sync-online { background: #0f2a1a; color: #10B981; }
    .sync-online .sync-dot { background: #10B981; }
    .sync-offline { background: #2a1a0f; color: #F59E0B; }
    .sync-offline .sync-dot { background: #F59E0B; }

    /* ── Session Info Card ─────────────────────────────────────────────── */
    .session-card {
        background: linear-gradient(145deg, #0f1629, #16213E);
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .session-card-title {
        font-size: 0.8rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .session-field {
        display: flex;
        justify-content: space-between;
        padding: 0.3rem 0;
        border-bottom: 1px solid #2D3A5C33;
        font-size: 0.85rem;
    }
    .session-field-label { color: #9CA3AF; }
    .session-field-value { color: #E5E7EB; font-weight: 600; }

    /* ── Confidence Gauge ──────────────────────────────────────────────── */
    .gauge-container {
        background: linear-gradient(145deg, #0f1629, #16213E);
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .gauge-label {
        font-size: 0.8rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .gauge-value {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .gauge-bar-track {
        background: #0a0f1f;
        border-radius: 8px;
        height: 12px;
        overflow: hidden;
        position: relative;
    }
    .gauge-bar-fill {
        height: 100%;
        border-radius: 8px;
        animation: progressFill 1s ease-out;
        transition: width 0.5s ease;
    }
    .gauge-subtext {
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 0.4rem;
    }

    /* ── Progress Tracker ──────────────────────────────────────────────── */
    .progress-tracker {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0.8rem 0;
        padding: 0.6rem 0;
    }
    .pt-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        position: relative;
    }
    .pt-dot {
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        transition: all 0.3s ease;
        z-index: 2;
    }
    .pt-dot-done { background: #10B981; color: #fff; }
    .pt-dot-active { background: #F59E0B; color: #000; animation: pulseGlow 2s ease-in-out infinite; }
    .pt-dot-pending { background: #2D3A5C; color: #6B7280; }
    .pt-label {
        font-size: 0.68rem;
        color: #9CA3AF;
        font-weight: 500;
        white-space: nowrap;
    }
    .pt-label-active { color: #F59E0B; font-weight: 700; }
    .pt-label-done { color: #10B981; }
    .pt-connector {
        flex: 1;
        height: 2px;
        background: #2D3A5C;
        margin: 0 -0.5rem;
        margin-bottom: 1.2rem;
        z-index: 1;
    }
    .pt-connector-done { background: #10B981; }
    .pt-connector-active { background: linear-gradient(90deg, #10B981, #F59E0B); }

    /* ── Evidence Cards ────────────────────────────────────────────────── */
    .evidence-card {
        background: linear-gradient(145deg, #16213E, #1a2744);
        border: 1px solid #2D3A5C;
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        animation: fadeInUp 0.4s ease-out;
    }
    .evidence-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }
    .evidence-q-num {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: #000;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
    }
    .evidence-why {
        font-size: 0.78rem;
        color: #6B7280;
        font-style: italic;
        background: #0f1629;
        padding: 0.4rem 0.7rem;
        border-radius: 8px;
        border-left: 3px solid #F59E0B;
        margin-top: 0.5rem;
    }

    /* ── Cause Card ────────────────────────────────────────────────────── */
    .cause-card {
        background: linear-gradient(145deg, #16213E, #1a2744);
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .cause-card:hover {
        border-color: #F59E0B;
        transform: translateX(4px);
    }
    .cause-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px; height: 24px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        margin-right: 0.5rem;
    }
    .cause-bar-track {
        background: #0a0f1f;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        margin: 0.4rem 0;
    }
    .cause-bar-fill {
        height: 100%;
        border-radius: 6px;
        animation: progressFill 0.8s ease-out;
    }

    /* ── Loading Spinner ───────────────────────────────────────────────── */
    .typing-indicator {
        display: flex;
        gap: 0.3rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(145deg, #1e2a4a, #16213E);
        border: 1px solid #2D3A5C;
        border-radius: 18px;
        border-bottom-left-radius: 6px;
        display: inline-flex;
        animation: fadeIn 0.3s ease-out;
    }
    .typing-dot {
        width: 8px; height: 8px;
        background: #F59E0B;
        border-radius: 50%;
        animation: typingDot 1.4s ease-in-out infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    /* ── Offline Banner ────────────────────────────────────────────────── */
    @keyframes slideBanner {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .offline-banner {
        background: linear-gradient(135deg, #92400E, #B45309);
        color: #FEF3C7;
        padding: 0.7rem 1.2rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
        font-weight: 600;
        animation: slideBanner 0.4s ease-out;
        margin-bottom: 1rem;
        border: 1px solid #D97706;
    }
    .offline-banner-icon { font-size: 1.2rem; }
    .online-banner {
        background: linear-gradient(135deg, #064E3B, #065F46);
        color: #A7F3D0;
        padding: 0.7rem 1.2rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
        font-weight: 600;
        animation: slideBanner 0.4s ease-out;
        margin-bottom: 1rem;
        border: 1px solid #10B981;
    }

    /* ── Sync Stats Card ──────────────────────────────────────────────── */
    .sync-stats-card {
        background: linear-gradient(145deg, #0f1629, #16213E);
        border: 1px solid #2D3A5C;
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
    }
    .sync-stat-row {
        display: flex;
        justify-content: space-between;
        padding: 0.25rem 0;
        font-size: 0.8rem;
    }
    .sync-stat-label { color: #9CA3AF; }
    .sync-stat-value { color: #E5E7EB; font-weight: 600; }

    /* ── Hide Streamlit default page nav ───────────────────────────────── */
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

    /* ── Page header ───────────────────────────────────────────────────── */
    .page-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.3rem;
    }
    .page-header-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #E5E7EB;
    }
    .page-header-badge {
        background: #16213E;
        border: 1px solid #2D3A5C;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        color: #9CA3AF;
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
            "explanation": "Low rail pressure at idle is the classic lift pump symptom on ISB/ISX.",
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
        "why_we_ask": "Normal is 870+ PSI at key on. Below this confirms low pressure issue.",
        "quick_replies": ["Under 500 PSI", "500 to 870 PSI", "870+ PSI", "Scanner not available"],
    },
    {
        "id": "miles_since_filter",
        "question": "Approximately how many miles since the last fuel filter change?",
        "why_we_ask": "Cummins recommends filter change every 15,000 miles.",
        "quick_replies": ["Under 5,000 mi", "5,000 to 15,000 mi", "Over 15,000 mi", "Unknown"],
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
    st.session_state.chat_phase = "idle"  # idle, triage, evidence, result, done
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "evidence_answers" not in st.session_state:
    st.session_state.evidence_answers = {}
if "sidebar_submitted" not in st.session_state:
    st.session_state.sidebar_submitted = False

# ── Helper functions ─────────────────────────────────────────────────────────
def add_bot_message(content):
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": content, "time": datetime.now().strftime("%H:%M")}
    )

def add_user_message(content):
    st.session_state.chat_messages.append(
        {"role": "user", "content": content, "time": datetime.now().strftime("%H:%M")}
    )

def get_phase_index(phase):
    phases = ["idle", "triage", "evidence", "result", "done"]
    return phases.index(phase) if phase in phases else 0

def get_current_confidence():
    """Calculate current confidence based on triage + evidence answers."""
    # If backend already computed an updated confidence, use it
    if st.session_state.get("backend_confidence") is not None:
        return st.session_state.backend_confidence

    triage = st.session_state.get("triage_data", [{}])
    top = triage[0] if triage else {}
    base_conf = top.get("confidence", 0.0)
    answers = st.session_state.evidence_answers

    if not answers:
        return base_conf

    # Fallback: local P0191-specific rules
    delta = 0.0
    if "Under 500" in str(answers.get("fuel_pressure_psi", "")):
        delta += 0.12
    if "Over 15,000" in str(answers.get("miles_since_filter", "")):
        delta += 0.08
    if "cold start" in str(answers.get("cold_start_issue", "")).lower():
        delta += 0.06
    return min(base_conf + delta, 0.97)


def generate_session_id():
    """Generate a unique session ID for the backend workflow."""
    return f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-name">TRACE AI</div>
            <div class="sidebar-brand-version">v0.1.0 Pilot Build</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Navigation
    st.markdown("**Navigation**")
    st.page_link("ui.py", label="Home")
    st.page_link("pages/1_Technician_Chatbot.py", label="Technician Chatbot")
    st.page_link("pages/2_Approval_Dashboard.py", label="Approval Dashboard")
    st.page_link("pages/3_Decision_Audit.py", label="Decision Audit")

    st.divider()

    # Vehicle Info Form
    st.markdown("### Vehicle Info")
    st.caption("Fill in details before starting the chat.")

    with st.form("vehicle_form"):
        fault_code = st.selectbox(
            "Fault Code (DTC)",
            options=[""] + list(FAULT_CODES.keys()),
            format_func=lambda x: f"{x}  |  {FAULT_CODES[x]['name']}" if x else "Select a fault code...",
        )
        vehicle_id = st.text_input("Vehicle / Unit ID", placeholder="e.g. UNIT-4471")
        mileage = st.number_input("Current Mileage", min_value=0, step=1000, value=0)
        symptoms = st.text_area(
            "Initial Symptoms",
            placeholder="e.g. rough idle, black smoke, loss of power under load",
        )
        submitted = st.form_submit_button("Start Diagnosis", type="primary", use_container_width=True)

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

    # Session info card (only when active)
    if st.session_state.chat_phase != "idle":
        st.divider()

        fc = st.session_state.get("fault_code", "")
        fc_info = FAULT_CODES.get(fc, {})
        severity = fc_info.get("severity", "N/A")
        sev_color = "#EF4444" if severity == "Critical" else "#F59E0B" if severity == "High" else "#3B82F6"

        st.markdown(
            f"""
            <div class="session-card">
                <div class="session-card-title">Current Session</div>
                <div class="session-field">
                    <span class="session-field-label">Fault Code</span>
                    <span class="session-field-value">{fc}</span>
                </div>
                <div class="session-field">
                    <span class="session-field-label">System</span>
                    <span class="session-field-value">{fc_info.get('system', 'N/A')}</span>
                </div>
                <div class="session-field">
                    <span class="session-field-label">Severity</span>
                    <span class="session-field-value" style="color:{sev_color}">{severity}</span>
                </div>
                <div class="session-field">
                    <span class="session-field-label">Vehicle</span>
                    <span class="session-field-value">{st.session_state.get('vehicle_id', 'N/A')}</span>
                </div>
                <div class="session-field">
                    <span class="session-field-label">Phase</span>
                    <span class="session-field-value" style="color:#F59E0B">{st.session_state.chat_phase.upper()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Confidence Gauge
        conf = get_current_confidence()
        if conf > 0:
            conf_pct = int(conf * 100)
            conf_color = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.5 else "#EF4444"
            st.markdown(
                f"""
                <div class="gauge-container">
                    <div class="gauge-label">Confidence Score</div>
                    <div class="gauge-value" style="color:{conf_color}">{conf_pct}%</div>
                    <div class="gauge-bar-track">
                        <div class="gauge-bar-fill" style="width:{conf_pct}%; background: linear-gradient(90deg, {conf_color}, {conf_color}aa);"></div>
                    </div>
                    <div class="gauge-subtext">Updates as evidence is collected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # Simulated Offline Mode
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from backend.sync import (
        check_connectivity, get_sync_stats, get_last_sync_time,
        get_pending_count, format_time_ago, sync_to_cloud, log_sync_event,
    )
    import uuid

    try:
        from backend.orchestrator.workflow import run_triage_only, run_evidence_and_escalation
        from backend.agents.evidence_agent import get_evidence_questions as backend_get_evidence_questions
        _BACKEND_AVAILABLE = True
    except ImportError:
        _BACKEND_AVAILABLE = False

    real_online = check_connectivity()

    was_simulating = st.session_state.get("simulate_offline", False)
    simulate_offline = st.toggle(
        "Simulate Offline Mode",
        value=was_simulating,
        help="Toggle to simulate offline behavior for demo purposes",
    )
    st.session_state.simulate_offline = simulate_offline

    if was_simulating and not simulate_offline:
        st.session_state.show_reconnect_sync = True

    is_online = real_online and not simulate_offline
    st.session_state.is_online = is_online

    if is_online:
        st.markdown(
            '<div class="sync-indicator sync-online">'
            '<span class="sync-dot"></span> Cloud Sync: Online'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sync-indicator sync-offline">'
            '<span class="sync-dot"></span> Offline (Local Mode)'
            '</div>',
            unsafe_allow_html=True,
        )

    stats = get_sync_stats()
    pending_total = stats["cases_pending"] + stats["decisions_pending"]
    synced_total = stats["cases_synced"] + stats["decisions_synced"]
    last_sync = get_last_sync_time()
    last_sync_text = format_time_ago(last_sync)

    st.markdown(
        f"""
        <div class="sync-stats-card">
            <div class="sync-stat-row">
                <span class="sync-stat-label">Last sync</span>
                <span class="sync-stat-value">{last_sync_text}</span>
            </div>
            <div class="sync-stat-row">
                <span class="sync-stat-label">Pending</span>
                <span class="sync-stat-value" style="color:{'#F59E0B' if pending_total > 0 else '#10B981'}">{pending_total}</span>
            </div>
            <div class="sync-stat-row">
                <span class="sync-stat-label">Total synced</span>
                <span class="sync-stat-value">{synced_total}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("LLM runs on device via Ollama. No cloud needed for diagnosis.")



# ── Breadcrumb ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="breadcrumb">'
    '<a href="/">Home</a>'
    '<span class="sep">›</span>'
    '<span class="active">Technician Chatbot</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Page Header ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-header">'
    '<span class="page-header-title">Technician Chatbot</span>'
    '<span class="page-header-badge">AI Diagnosis Assistant</span>'
    '</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Report fault codes and symptoms through the sidebar, then chat with TRACE AI "
    "to walk through the diagnosis."
)

# ── Progress Tracker ────────────────────────────────────────────────────────
phase = st.session_state.chat_phase
phase_idx = get_phase_index(phase)

steps = [
    ("📝", "Report"),
    ("🧠", "Triage"),
    ("🔍", "Evidence"),
    ("⚡", "Escalation"),
    ("✅", "Done"),
]

tracker_html = '<div class="progress-tracker">'
for i, (icon, label) in enumerate(steps):
    if i > 0:
        conn_class = "pt-connector"
        if i < phase_idx:
            conn_class += " pt-connector-done"
        elif i == phase_idx:
            conn_class += " pt-connector-active"
        tracker_html += f'<div class="{conn_class}"></div>'

    dot_class = "pt-dot"
    label_class = "pt-label"
    if i < phase_idx:
        dot_class += " pt-dot-done"
        label_class += " pt-label-done"
        dot_content = "✓"
    elif i == phase_idx:
        dot_class += " pt-dot-active"
        label_class += " pt-label-active"
        dot_content = icon
    else:
        dot_class += " pt-dot-pending"
        dot_content = icon

    tracker_html += (
        f'<div class="pt-step">'
        f'<div class="{dot_class}">{dot_content}</div>'
        f'<div class="{label_class}">{label}</div>'
        f'</div>'
    )
tracker_html += '</div>'
st.markdown(tracker_html, unsafe_allow_html=True)

st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

# ── Offline / Reconnect Banner ──────────────────────────────────────────────
_is_online = st.session_state.get("is_online", True)
if not _is_online:
    st.markdown(
        '<div class="offline-banner">'
        '<span class="offline-banner-icon">📡</span>'
        '<span>Offline Mode: All data saved locally. Will sync when connection is restored.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

if st.session_state.get("show_reconnect_sync"):
    pending = get_pending_count()
    if pending > 0:
        st.markdown(
            '<div class="online-banner">'
            '<span class="offline-banner-icon">🔄</span>'
            '<span>Connection restored! Syncing offline data...</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        progress_bar = st.progress(0, text=f"Syncing... {pending} records pending")
        # Sync first, then animate progress for visual effect
        sync_result = sync_to_cloud()
        total_synced = sync_result["cases_synced"] + sync_result["decisions_synced"]
        for i in range(pending):
            time.sleep(0.25 + random.uniform(0, 0.15))
            remaining = pending - i - 1
            progress_bar.progress(
                (i + 1) / pending,
                text=f"Syncing... {remaining} records remaining",
            )
        progress_bar.progress(1.0, text=f"Synced! {total_synced} records uploaded to cloud")
        log_sync_event(
            "reconnect_sync",
            cases_synced=sync_result["cases_synced"],
            decisions_synced=sync_result["decisions_synced"],
        )
        time.sleep(1.5)
        st.session_state.show_reconnect_sync = False
        st.rerun()
    else:
        st.markdown(
            '<div class="online-banner">'
            '<span class="offline-banner-icon">✅</span>'
            '<span>Back online! All records are already synced.</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.session_state.show_reconnect_sync = False

# ── Phase: Triage (auto triggered after sidebar submit) ──────────────────────
if st.session_state.chat_phase == "triage" and not any(
    "Triage" in m.get("content", "") for m in st.session_state.chat_messages
):
    fc = st.session_state.fault_code
    fc_info = FAULT_CODES.get(fc, {})

    add_user_message(
        f"**New case submitted**\n\n"
        f"- **Fault code:** {fc}  |  {fc_info.get('name', 'Unknown')}\n"
        f"- **Vehicle:** {st.session_state.vehicle_id}\n"
        f"- **Mileage:** {st.session_state.mileage:,} mi\n"
        f"- **Symptoms:** {st.session_state.symptoms}"
    )

    # Try real backend (LLM triage), fall back to mock data
    results = None
    session_id = generate_session_id()
    st.session_state.session_id = session_id
    st.session_state.backend_available = False
    st.session_state.backend_confidence = None

    if _BACKEND_AVAILABLE:
        try:
            triage_state = run_triage_only(
                fault_code=fc,
                symptoms=st.session_state.symptoms,
                session_id=session_id,
            )
            if triage_state.get("triage_results"):
                results = triage_state["triage_results"]
                st.session_state.backend_available = True
        except Exception:
            results = MOCK_TRIAGE_RESULTS.get(fc)
    else:
        results = MOCK_TRIAGE_RESULTS.get(fc)

    if not results:
        results = MOCK_TRIAGE_RESULTS.get(fc)

    if results:
        triage_text = "**Triage Complete: Top 3 Probable Causes**\n\n"
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
            "I need to ask you a few follow up questions to refine this diagnosis. "
            "Ready when you are."
        )
        add_bot_message(triage_text)
        st.session_state.triage_data = results
    else:
        add_bot_message(
            f"I don't have specialized triage data for **{fc}** yet. "
            f"Let me ask some general follow up questions."
        )
        st.session_state.triage_data = [
            {"cause": "General diagnosis needed", "confidence": 0.50, "urgency": "medium", "estimated_cost_usd": 0}
        ]

    # Load evidence questions from backend (with fallback)
    if _BACKEND_AVAILABLE:
        try:
            backend_qs = backend_get_evidence_questions(fc)
            if backend_qs:
                st.session_state.active_evidence_questions = backend_qs
            else:
                st.session_state.active_evidence_questions = EVIDENCE_QUESTIONS
        except Exception:
            st.session_state.active_evidence_questions = EVIDENCE_QUESTIONS
    else:
        st.session_state.active_evidence_questions = EVIDENCE_QUESTIONS

    st.session_state.chat_phase = "evidence"
    st.rerun()

# ── Phase: Evidence collection (question by question) ────────────────────────
if st.session_state.chat_phase == "evidence":
    questions = st.session_state.get("active_evidence_questions", EVIDENCE_QUESTIONS)
    idx = st.session_state.current_question_idx
    if idx < len(questions) and not any(
        questions[idx]["question"] in m.get("content", "")
        for m in st.session_state.chat_messages
        if m["role"] == "assistant"
    ):
        q = questions[idx]
        q_text = (
            f"**Question {idx + 1} of {len(questions)}:** {q['question']}\n\n"
            f"_Why we ask: {q['why_we_ask']}_"
        )
        add_bot_message(q_text)
        st.rerun()

# ── Display all chat messages (styled bubbles) ──────────────────────────────
for msg in st.session_state.chat_messages:
    is_user = msg["role"] == "user"

    if is_user:
        st.markdown(
            f'<div class="chat-row chat-row-user">'
            f'<div>'
            f'<div class="chat-bubble chat-bubble-user">{msg["content"]}</div>'
            f'<div class="chat-time chat-time-user">{msg.get("time", "")}</div>'
            f'</div>'
            f'<div class="chat-avatar chat-avatar-user">👷</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chat-row chat-row-bot">'
            f'<div class="chat-avatar chat-avatar-bot">🤖</div>'
            f'<div>'
            f'<div class="chat-bubble chat-bubble-bot">{msg["content"]}</div>'
            f'<div class="chat-time chat-time-bot">{msg.get("time", "")}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Quick reply buttons (evidence phase) ─────────────────────────────────────
if st.session_state.chat_phase == "evidence":
    questions = st.session_state.get("active_evidence_questions", EVIDENCE_QUESTIONS)
    idx = st.session_state.current_question_idx
    if idx < len(questions):
        q = questions[idx]

        # Evidence card with question context
        st.markdown(
            f"""
            <div class="evidence-card">
                <div class="evidence-card-header">
                    <span class="evidence-q-num">Question {idx + 1} of {len(questions)}</span>
                </div>
                <div class="evidence-why">💡 {q['why_we_ask']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Select your answer:**")
        cols = st.columns(len(q["quick_replies"]))
        for i, reply in enumerate(q["quick_replies"]):
            with cols[i]:
                if st.button(reply, key=f"qr_{idx}_{i}", use_container_width=True):
                    add_user_message(reply)
                    st.session_state.evidence_answers[q["id"]] = reply
                    st.session_state.current_question_idx += 1

                    if st.session_state.current_question_idx >= len(questions):
                        st.session_state.chat_phase = "result"
                    st.rerun()

# ── Phase: Result summary ───────────────────────────────────────────────────
if st.session_state.chat_phase == "result" and not any(
    "Evidence Summary" in m.get("content", "") for m in st.session_state.chat_messages
):
    answers = st.session_state.evidence_answers
    triage = st.session_state.get("triage_data", [{}])
    top = triage[0] if triage else {}
    questions = st.session_state.get("active_evidence_questions", EVIDENCE_QUESTIONS)

    # Try real backend for evidence + escalation
    updated_conf = None
    needs_escalation = None
    safety_flag = False
    escalation_reason = ""

    if _BACKEND_AVAILABLE and st.session_state.get("backend_available") and st.session_state.get("session_id"):
        try:
            result_state = run_evidence_and_escalation(
                session_id=st.session_state.session_id,
                evidence=answers,
            )
            updated_conf = result_state.get("updated_confidence", top.get("confidence", 0.50))
            needs_escalation = result_state.get("requires_human_approval", False)
            safety_flag = "safety" in str(result_state.get("escalation_reason", "")).lower()
            escalation_reason = result_state.get("escalation_reason", "")
            st.session_state.backend_confidence = updated_conf
        except Exception:
            pass  # fall through to local computation

    # Fallback: local hardcoded rules
    if updated_conf is None:
        base_conf = top.get("confidence", 0.50)
        delta = 0.0
        if "Under 500" in str(answers.get("fuel_pressure_psi", "")):
            delta += 0.12
        if "Over 15,000" in str(answers.get("miles_since_filter", "")):
            delta += 0.08
        if "cold start" in str(answers.get("cold_start_issue", "")).lower():
            delta += 0.06
        safety_flag = "leak" in str(answers.get("visible_leak", "")).lower()
        updated_conf = min(base_conf + delta, 0.97)
        needs_escalation = updated_conf < 0.70 or top.get("estimated_cost_usd", 0) > 500 or safety_flag

    base_conf = top.get("confidence", 0.50)

    summary = "**Evidence Summary & Updated Diagnosis**\n\n"
    summary += "| Question | Your Answer |\n|---|---|\n"
    for q in questions:
        ans = answers.get(q["id"], "N/A")
        summary += f"| {q['question'][:50]}... | **{ans}** |\n"

    summary += f"\n\n**Updated confidence:** {base_conf:.0%} -> **{updated_conf:.0%}**\n"
    summary += f"**Top cause:** {top.get('cause', 'Unknown')}\n\n"

    if safety_flag:
        summary += (
            "**SAFETY ALERT:** Visible fuel leak detected. "
            "This case has been **automatically escalated** to a manager for approval.\n\n"
        )
    elif needs_escalation:
        if escalation_reason:
            summary += f"**Escalation required:** {escalation_reason}\n\n"
        else:
            reason_parts = []
            if updated_conf < 0.70:
                reason_parts.append(f"confidence below 70% ({updated_conf:.0%})")
            if top.get("estimated_cost_usd", 0) > 500:
                reason_parts.append(f"estimated cost ${top['estimated_cost_usd']:,}")
            summary += (
                f"**Escalation required:** {', '.join(reason_parts)}. "
                f"This case has been sent to the **Approval Dashboard** for manager review.\n\n"
            )
    else:
        summary += "**Auto approved:** confidence is high and cost is within limits.\n\n"

    summary += (
        "You can view the case status on the **Approval Dashboard** page. "
        "Thank you for providing the evidence!"
    )

    add_bot_message(summary)
    st.session_state.chat_phase = "done"
    st.rerun()

# ── Chat input (free text) ──────────────────────────────────────────────────
if st.session_state.chat_phase == "done":
    user_input = st.chat_input("Type a follow up question...")
    if user_input:
        add_user_message(user_input)
        add_bot_message(
            "Thanks for the follow up. In the full version, I'd use the LLM to answer. "
            "For now, please check the **Approval Dashboard** for case status, or start a "
            "new diagnosis from the sidebar."
        )
        st.rerun()
elif st.session_state.chat_phase == "idle":
    st.markdown(
        """
        <div style="text-align:center; padding:3rem 1rem; animation: fadeInUp 0.5s ease-out;">
            <div style="height:1rem;"></div>
            <div style="font-size:1.1rem; color:#E5E7EB; font-weight:600; margin-bottom:0.5rem;">
                Ready to Diagnose
            </div>
            <div style="font-size:0.9rem; color:#9CA3AF; max-width:400px; margin:0 auto;">
                Fill in the <strong style="color:#F59E0B">Vehicle Info</strong> form in the sidebar
                to begin a new diagnosis session.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
