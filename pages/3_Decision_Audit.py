import streamlit as st
import json
import os
import sys
import csv
import io
from datetime import datetime, timedelta
from PIL import Image

_logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo.png"))
st.set_page_config(page_title="TRACE AI Decision Audit", page_icon=_logo, layout="wide")

# ── Backend imports ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from backend.db import get_decision_logs
from backend.logging_config import read_audit_log
from backend.sync import check_connectivity

# ── Paths ────────────────────────────────────────────────────────────────────
EXAMPLE_LOGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "example_logs.json"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.3); }
        50% { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
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

    /* ── Sidebar ────────────────────────────────────────────────────────── */
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

    /* ── Summary Cards ─────────────────────────────────────────────────── */
    .audit-summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .audit-summary-card {
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .audit-summary-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .audit-summary-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .asc-total::before { background: #3B82F6; }
    .asc-agents::before { background: #7C3AED; }
    .asc-sessions::before { background: #F59E0B; }
    .asc-approved::before { background: #10B981; }
    .asc-confidence::before { background: linear-gradient(90deg, #F59E0B, #10B981); }
    .audit-summary-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0.1rem 0;
    }
    .audit-summary-label {
        font-size: 0.75rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 500;
    }

    /* ── Timeline ──────────────────────────────────────────────────────── */
    .timeline-container {
        position: relative;
        padding: 0 0 0 2rem;
    }
    .timeline-container::before {
        content: '';
        position: absolute;
        left: 14px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #F59E0B 0%, #3B82F6 50%, #10B981 100%);
    }
    .timeline-entry {
        position: relative;
        margin-bottom: 1rem;
        padding: 1rem 1.2rem;
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        animation: fadeInUp 0.4s ease-out both;
        transition: all 0.2s ease;
    }
    .timeline-entry:hover {
        border-color: #3D4A6C;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .timeline-dot {
        position: absolute;
        left: -26px;
        top: 1.2rem;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 2px solid #0a0f1f;
    }
    .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .timeline-action {
        font-weight: 700;
        font-size: 0.95rem;
        color: #E5E7EB;
    }
    .timeline-time {
        font-size: 0.78rem;
        color: #6B7280;
        font-family: 'Inter', monospace;
    }
    .timeline-agent-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-triage { background: #7C3AED22; color: #A78BFA; }
    .badge-evidence { background: #3B82F622; color: #60A5FA; }
    .badge-escalation { background: #F59E0B22; color: #FBBF24; }
    .badge-human { background: #10B98122; color: #34D399; }
    .timeline-conf {
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .timeline-detail {
        font-size: 0.85rem;
        color: #9CA3AF;
        line-height: 1.5;
        margin-top: 0.3rem;
    }

    /* ── Confidence Strip ─────────────────────────────────────────────── */
    .conf-strip {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        animation: fadeInUp 0.4s ease-out both;
    }
    .conf-strip-label {
        font-size: 0.75rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        white-space: nowrap;
    }
    .conf-strip-values {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        flex: 1;
    }
    .conf-strip-val {
        font-size: 1.1rem;
        font-weight: 800;
        min-width: 3rem;
        text-align: center;
    }
    .conf-strip-arrow {
        color: #6B7280;
        font-size: 0.9rem;
    }
    .conf-strip-bar-track {
        flex: 1;
        height: 6px;
        background: #0f1629;
        border-radius: 3px;
        overflow: hidden;
        position: relative;
    }
    .conf-strip-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.6s ease;
    }
    .conf-strip-delta {
        font-size: 0.85rem;
        font-weight: 700;
        padding: 0.15rem 0.6rem;
        border-radius: 10px;
        white-space: nowrap;
    }

    /* ── Log Table ─────────────────────────────────────────────────────── */
    .log-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        font-size: 0.85rem;
    }
    .log-table th {
        background: #0f1629;
        color: #9CA3AF;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.7rem 0.8rem;
        text-align: left;
        font-weight: 600;
        position: sticky;
        top: 0;
    }
    .log-table td {
        padding: 0.55rem 0.8rem;
        color: #E5E7EB;
        border-bottom: 1px solid #2D3A5C33;
        vertical-align: top;
    }
    .log-table tr:last-child td { border-bottom: none; }
    .log-table tr:hover td { background: #16213E88; }
    </style>
    """,
    unsafe_allow_html=True,
)

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

    # Logged-in user badge
    ROLE_NAMES = {
        "Fleet Manager": "Zion Adedipe",
        "Senior Technician": "Nhi Truong",
        "Junior Technician": "Lilian Campbell",
    }
    role = st.session_state.get("global_role", "Fleet Manager")
    user_name = ROLE_NAMES.get(role, "Zion")
    st.markdown(
        f'<div style="background:#16213E; border:1px solid #2D3A5C; border-radius:10px; '
        f'padding:0.6rem 0.8rem; margin-bottom:0.3rem;">'
        f'<div style="font-size:0.72rem; color:#9CA3AF; text-transform:uppercase; '
        f'letter-spacing:0.05em; font-weight:600;">Logged in as</div>'
        f'<div style="font-size:0.95rem; font-weight:700; color:#F59E0B; margin-top:0.15rem;">'
        f'{user_name}</div>'
        f'<div style="font-size:0.78rem; color:#9CA3AF;">{role}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Simulated Offline Mode
    from backend.sync import get_sync_stats, get_last_sync_time, format_time_ago

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


# ── Data Loading ─────────────────────────────────────────────────────────────
def load_example_logs():
    """Load the example_logs.json file."""
    if os.path.exists(EXAMPLE_LOGS_PATH):
        with open(EXAMPLE_LOGS_PATH, "r") as f:
            return json.load(f)
    return []


def load_all_logs():
    """Merge example logs, SQLite logs, and audit file logs into one list."""
    all_logs = []

    # 1. Example logs (demo data)
    example = load_example_logs()
    for entry in example:
        entry["_source"] = "example_logs.json"
        all_logs.append(entry)

    # 2. SQLite decision_log table
    try:
        db_logs = get_decision_logs()
        for entry in db_logs:
            entry["_source"] = "sqlite"
            if "log_id" not in entry or not entry.get("log_id"):
                entry["log_id"] = f"DB-{entry.get('id', '?')}"
            all_logs.append(entry)
    except Exception:
        pass

    # 3. Audit log file (JSON Lines)
    try:
        file_logs = read_audit_log()
        for i, entry in enumerate(file_logs):
            entry["_source"] = "audit_file"
            if "log_id" not in entry:
                entry["log_id"] = f"FILE-{i+1}"
            all_logs.append(entry)
    except Exception:
        pass

    return all_logs


# ── Helpers ──────────────────────────────────────────────────────────────────
AGENT_COLORS = {
    "triage_agent": ("#A78BFA", "badge-triage", "#7C3AED"),
    "evidence_agent": ("#60A5FA", "badge-evidence", "#3B82F6"),
    "escalation_agent": ("#FBBF24", "badge-escalation", "#F59E0B"),
    "human_reviewer": ("#34D399", "badge-human", "#10B981"),
}


def get_agent_style(agent_id):
    """Return (text_color, badge_class, dot_color) for a given agent."""
    return AGENT_COLORS.get(agent_id, ("#9CA3AF", "badge-triage", "#6B7280"))


def format_action(action):
    """Convert snake_case action to readable title."""
    return action.replace("_", " ").title() if action else "Unknown"


def get_output_summary(entry):
    """Extract a short summary string from the output field."""
    output = entry.get("output", {})
    if isinstance(output, str):
        return output

    if not isinstance(output, dict):
        return ""

    # Pick the most meaningful field
    if "decision" in output:
        return f"Decision: {output['decision']}"
    if "updated_confidence" in output:
        return f"Confidence updated to {output['updated_confidence']}"
    if "top_causes" in output:
        causes = output["top_causes"]
        if causes and isinstance(causes, list):
            return f"Top cause: {causes[0].get('cause', 'N/A')}"
    if "requires_human_approval" in output:
        if output["requires_human_approval"]:
            return "Escalated for human approval"
        return "Auto approved"
    if "technician_response" in output:
        return f"Response: {output['technician_response']}"
    if "evidence_summary" in output:
        return output["evidence_summary"][:120]
    if "repair_steps_delivered" in output:
        return "Repair steps delivered to technician"
    if "session_summary" in output:
        return "Session closed, fully traceable"
    if "steps" in output:
        return f"{output.get('steps_count', len(output['steps']))} repair steps generated"
    if "notification_delivered" in output:
        return "Notification sent to review queue"

    # Fallback: first key-value
    for k, v in output.items():
        if isinstance(v, (str, int, float, bool)):
            return f"{k}: {v}"
    return ""


def logs_to_csv(logs):
    """Convert log entries to CSV string for download."""
    output = io.StringIO()
    fieldnames = [
        "log_id", "timestamp", "session_id", "agent_id", "action",
        "fault_code", "confidence", "human_approved", "model_used",
        "inputs", "output", "metadata",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for log in logs:
        row = {}
        for f in fieldnames:
            val = log.get(f, "")
            if isinstance(val, (dict, list)):
                val = json.dumps(val)
            row[f] = val
        writer.writerow(row)
    return output.getvalue()


# ── Load Data ────────────────────────────────────────────────────────────────
all_logs = load_all_logs()

# ── Breadcrumb ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="breadcrumb">'
    '<a href="/">Home</a>'
    '<span class="sep">></span>'
    '<span class="active">Decision Audit</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-header">'
    '<span class="page-header-title">Decision Audit Trail</span>'
    '<span class="page-header-badge">Compliance & Traceability</span>'
    '</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Every agent action is logged with a timestamp, agent ID, inputs, output, and confidence score. "
    "This page provides full visibility into the AI decision pipeline for compliance and review."
)
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Summary Metrics ──────────────────────────────────────────────────────────
unique_sessions = set(e.get("session_id", "") for e in all_logs if e.get("session_id"))
unique_agents = set(e.get("agent_id", "") for e in all_logs if e.get("agent_id"))
approved_count = sum(1 for e in all_logs if e.get("human_approved") is True)
confidences = [e.get("confidence", 0) for e in all_logs if e.get("confidence")]
avg_conf = sum(confidences) / len(confidences) if confidences else 0

st.markdown(
    f"""
    <div class="audit-summary-grid">
        <div class="audit-summary-card asc-total" style="animation-delay:0.05s;">
            <div class="audit-summary-value" style="color:#3B82F6">{len(all_logs)}</div>
            <div class="audit-summary-label">Total Log Entries</div>
        </div>
        <div class="audit-summary-card asc-sessions" style="animation-delay:0.1s;">
            <div class="audit-summary-value" style="color:#F59E0B">{len(unique_sessions)}</div>
            <div class="audit-summary-label">Sessions</div>
        </div>
        <div class="audit-summary-card asc-agents" style="animation-delay:0.15s;">
            <div class="audit-summary-value" style="color:#A78BFA">{len(unique_agents)}</div>
            <div class="audit-summary-label">Agents Involved</div>
        </div>
        <div class="audit-summary-card asc-approved" style="animation-delay:0.2s;">
            <div class="audit-summary-value" style="color:#10B981">{approved_count}</div>
            <div class="audit-summary-label">Human Approved</div>
        </div>
        <div class="audit-summary-card asc-confidence" style="animation-delay:0.25s;">
            <div class="audit-summary-value" style="color:#F59E0B">{avg_conf:.0%}</div>
            <div class="audit-summary-label">Avg Confidence</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Filters ──────────────────────────────────────────────────────────────────
st.markdown("#### Filters")
filter_cols = st.columns(4)

with filter_cols[0]:
    agent_options = ["All"] + sorted(unique_agents)
    selected_agent = st.selectbox(
        "Agent",
        agent_options,
        format_func=lambda x: format_action(x) if x != "All" else "All Agents",
    )

with filter_cols[1]:
    session_options = ["All"] + sorted(unique_sessions)
    selected_session = st.selectbox("Session", session_options)

with filter_cols[2]:
    action_options = ["All"] + sorted(set(e.get("action", "") for e in all_logs if e.get("action")))
    selected_action = st.selectbox(
        "Action",
        action_options,
        format_func=lambda x: format_action(x) if x != "All" else "All Actions",
    )

with filter_cols[3]:
    source_options = ["All", "example_logs.json", "sqlite", "audit_file"]
    selected_source = st.selectbox(
        "Data Source",
        source_options,
        format_func=lambda x: {
            "All": "All Sources",
            "example_logs.json": "Example Logs",
            "sqlite": "SQLite Database",
            "audit_file": "Audit Log File",
        }.get(x, x),
    )

# Apply filters
filtered_logs = all_logs
if selected_agent != "All":
    filtered_logs = [e for e in filtered_logs if e.get("agent_id") == selected_agent]
if selected_session != "All":
    filtered_logs = [e for e in filtered_logs if e.get("session_id") == selected_session]
if selected_action != "All":
    filtered_logs = [e for e in filtered_logs if e.get("action") == selected_action]
if selected_source != "All":
    filtered_logs = [e for e in filtered_logs if e.get("_source") == selected_source]

st.markdown(f"Showing **{len(filtered_logs)}** of {len(all_logs)} entries.")
st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

# ── Tabs: Timeline | Table | Raw JSON ────────────────────────────────────────
tab_timeline, tab_table, tab_export = st.tabs(
    ["Workflow Timeline", "Table View", "Export & Raw Data"]
)


# ── Tab: Timeline ────────────────────────────────────────────────────────────
with tab_timeline:
    if not filtered_logs:
        st.markdown(
            '<div style="text-align:center; padding:2rem; color:#9CA3AF;">'
            "No log entries match your filters."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # Group by session
        sessions = {}
        for entry in filtered_logs:
            sid = entry.get("session_id", "Unknown")
            sessions.setdefault(sid, []).append(entry)

        for session_id, entries in sessions.items():
            st.markdown(f"**Session:** `{session_id}`")

            # Confidence summary strip
            conf_values = [
                e.get("confidence", 0)
                for e in entries
                if e.get("confidence") is not None
            ]
            if conf_values:
                start_conf = conf_values[0]
                end_conf = conf_values[-1]
                delta = end_conf - start_conf
                start_pct = int(start_conf * 100)
                end_pct = int(end_conf * 100)
                delta_pct = int(delta * 100)

                end_color = "#10B981" if end_conf >= 0.7 else "#F59E0B" if end_conf >= 0.5 else "#EF4444"
                start_color = "#10B981" if start_conf >= 0.7 else "#F59E0B" if start_conf >= 0.5 else "#EF4444"
                delta_sign = "+" if delta >= 0 else ""
                delta_bg = "#10B98122" if delta >= 0 else "#EF444422"
                delta_color = "#10B981" if delta >= 0 else "#EF4444"

                st.markdown(
                    f'<div class="conf-strip">'
                    f'<span class="conf-strip-label">Confidence</span>'
                    f'<div class="conf-strip-values">'
                    f'<span class="conf-strip-val" style="color:{start_color}">{start_pct}%</span>'
                    f'<div class="conf-strip-bar-track">'
                    f'<div class="conf-strip-bar-fill" style="width:{end_pct}%; background:linear-gradient(90deg, {start_color}, {end_color});"></div>'
                    f'</div>'
                    f'<span class="conf-strip-val" style="color:{end_color}">{end_pct}%</span>'
                    f'</div>'
                    f'<span class="conf-strip-delta" style="background:{delta_bg}; color:{delta_color}">{delta_sign}{delta_pct}%</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Timeline entries
            timeline_html = '<div class="timeline-container">'
            for i, entry in enumerate(entries):
                agent = entry.get("agent_id", "unknown")
                text_color, badge_class, dot_color = get_agent_style(agent)
                action_label = format_action(entry.get("action", ""))
                ts = entry.get("timestamp", "")
                conf = entry.get("confidence")
                summary = get_output_summary(entry)

                conf_html = ""
                if conf is not None:
                    conf_pct = int(conf * 100)
                    conf_color = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.5 else "#EF4444"
                    conf_html = (
                        f'<div class="timeline-conf" style="color:{conf_color}">'
                        f"Confidence: {conf_pct}%</div>"
                    )

                human = entry.get("human_approved")
                human_html = ""
                if human is True:
                    human_html = '<span style="color:#10B981; font-size:0.78rem; font-weight:600; margin-left:0.5rem;">Approved</span>'
                elif human is False:
                    human_html = '<span style="color:#EF4444; font-size:0.78rem; font-weight:600; margin-left:0.5rem;">Rejected</span>'

                model_html = ""
                model = entry.get("model_used")
                if model and model != "N/A":
                    model_html = (
                        f'<span style="font-size:0.72rem; color:#6B7280; '
                        f'background:#0f1629; padding:0.1rem 0.5rem; border-radius:8px; '
                        f'margin-left:0.5rem;">{model}</span>'
                    )

                timeline_html += (
                    f'<div class="timeline-entry" style="animation-delay:{i * 0.05}s;">'
                    f'<div class="timeline-dot" style="background:{dot_color};"></div>'
                    f'<div class="timeline-header">'
                    f'<div>'
                    f'<span class="timeline-action">{action_label}</span>'
                    f'<span class="timeline-agent-badge {badge_class}">{agent.replace("_", " ")}</span>'
                    f'{human_html}{model_html}'
                    f'</div>'
                    f'<span class="timeline-time">{ts}</span>'
                    f'</div>'
                    f'{conf_html}'
                    f'<div class="timeline-detail">{summary}</div>'
                    f'</div>'
                )

            timeline_html += "</div>"
            st.markdown(timeline_html, unsafe_allow_html=True)
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)


# ── Tab: Table View ──────────────────────────────────────────────────────────
with tab_table:
    if not filtered_logs:
        st.markdown(
            '<div style="text-align:center; padding:2rem; color:#9CA3AF;">'
            "No log entries match your filters."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        table_html = (
            '<div style="max-height:600px; overflow-y:auto; border-radius:12px; border:1px solid #2D3A5C;">'
            '<table class="log-table">'
            '<tr>'
            '<th>Log ID</th><th>Timestamp</th><th>Agent</th><th>Action</th>'
            '<th>Confidence</th><th>Human</th><th>Model</th><th>Summary</th>'
            '</tr>'
        )

        for entry in filtered_logs:
            agent = entry.get("agent_id", "")
            text_color, badge_class, _ = get_agent_style(agent)
            conf = entry.get("confidence")
            conf_str = ""
            if conf is not None:
                conf_pct = int(conf * 100)
                c_color = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.5 else "#EF4444"
                conf_str = f'<span style="color:{c_color}; font-weight:700;">{conf_pct}%</span>'

            human = entry.get("human_approved")
            if human is True:
                human_str = '<span style="color:#10B981; font-weight:600;">Yes</span>'
            elif human is False:
                human_str = '<span style="color:#EF4444; font-weight:600;">No</span>'
            else:
                human_str = '<span style="color:#6B7280;">Pending</span>'

            model = entry.get("model_used") or ""
            if model == "N/A":
                model = ""
            summary = get_output_summary(entry)
            if len(summary) > 80:
                summary = summary[:77] + "..."

            table_html += (
                f'<tr>'
                f'<td style="font-family:monospace; font-size:0.8rem; color:#F59E0B;">{entry.get("log_id", "")}</td>'
                f'<td style="font-size:0.78rem; color:#9CA3AF; white-space:nowrap;">{entry.get("timestamp", "")}</td>'
                f'<td><span class="timeline-agent-badge {badge_class}">{agent.replace("_", " ")}</span></td>'
                f'<td style="font-weight:600;">{format_action(entry.get("action", ""))}</td>'
                f'<td>{conf_str}</td>'
                f'<td>{human_str}</td>'
                f'<td style="font-size:0.78rem; color:#9CA3AF;">{model}</td>'
                f'<td style="font-size:0.82rem; color:#9CA3AF;">{summary}</td>'
                f'</tr>'
            )

        table_html += "</table></div>"
        st.markdown(table_html, unsafe_allow_html=True)


# ── Tab: Export & Raw Data ───────────────────────────────────────────────────
with tab_export:
    st.markdown("#### Download Audit Logs")
    st.caption("Export the filtered logs for external review, compliance audits, or integration with other systems.")

    export_cols = st.columns(2)
    with export_cols[0]:
        # JSON export
        json_str = json.dumps(filtered_logs, indent=2, default=str)
        st.download_button(
            label="Download as JSON",
            data=json_str,
            file_name="trace_decision_audit.json",
            mime="application/json",
            use_container_width=True,
        )

    with export_cols[1]:
        # CSV export
        csv_str = logs_to_csv(filtered_logs)
        st.download_button(
            label="Download as CSV",
            data=csv_str,
            file_name="trace_decision_audit.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Raw JSON viewer
    st.markdown("#### Raw Log Data")
    st.caption("Inspect the full JSON payload of each log entry for debugging or detailed review.")

    if filtered_logs:
        selected_log_id = st.selectbox(
            "Select a log entry",
            [f"{e.get('log_id', '?')}  |  {format_action(e.get('action', ''))}" for e in filtered_logs],
        )
        idx = [f"{e.get('log_id', '?')}  |  {format_action(e.get('action', ''))}" for e in filtered_logs].index(selected_log_id)
        selected_entry = filtered_logs[idx]

        # Remove internal source tag for display
        display_entry = {k: v for k, v in selected_entry.items() if k != "_source"}
        st.json(display_entry)
    else:
        st.markdown(
            '<div style="text-align:center; padding:2rem; color:#9CA3AF;">'
            "No entries to display."
            "</div>",
            unsafe_allow_html=True,
        )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; padding:1rem; border-top:1px solid #2D3A5C; font-size:0.78rem; color:#6B7280;">
        TRACE AI Decision Audit Trail |
        Every action logged with timestamp, agent ID, inputs, output, and confidence |
        Compliant with fleet maintenance record keeping standards
    </div>
    """,
    unsafe_allow_html=True,
)
