import streamlit as st
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
import random
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from backend.logging_config import audit_log

_logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo.png"))
st.set_page_config(page_title="TRACE AI Dashboard", page_icon=_logo, layout="wide")

# ── Database Setup ───────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dashboard.db")


def init_dashboard_db():
    """Create the dashboard tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            fault_code TEXT NOT NULL,
            fault_name TEXT,
            vehicle_id TEXT,
            mileage INTEGER,
            symptoms TEXT,
            top_cause TEXT,
            confidence REAL,
            updated_confidence REAL,
            estimated_cost INTEGER,
            urgency TEXT,
            escalation_reason TEXT,
            evidence_json TEXT,
            status TEXT DEFAULT 'pending',
            approved_by TEXT,
            reviewer_notes TEXT,
            repair_steps_json TEXT,
            created_at TEXT,
            decided_at TEXT,
            sync_status TEXT DEFAULT 'pending'
        )
        """
    )
    try:
        conn.execute("ALTER TABLE cases ADD COLUMN sync_status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def seed_mock_cases():
    """Insert mock escalated cases if the table is empty."""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    if count > 0:
        conn.close()
        return

    mock_cases = [
        {
            "session_id": "SESS-2024-0041",
            "fault_code": "P0191",
            "fault_name": "Fuel Rail Pressure Sensor Circuit Range/Performance",
            "vehicle_id": "UNIT-4471",
            "mileage": 187000,
            "symptoms": "Rough idle, intermittent loss of power under load, occasional black smoke",
            "top_cause": "Weak / failing fuel lift pump",
            "confidence": 0.72,
            "updated_confidence": 0.84,
            "estimated_cost": 650,
            "urgency": "high",
            "escalation_reason": "Estimated repair cost exceeds $500 threshold",
            "evidence_json": json.dumps({
                "fuel_pressure_psi": "Under 500 PSI",
                "miles_since_filter": "5,000 to 15,000 mi",
                "visible_leak": "No leak visible",
                "cold_start_issue": "Yes, hard cold start",
            }),
            "status": "pending",
            "repair_steps_json": json.dumps([
                "1. Verify fault code P0191 with diagnostic scanner",
                "2. Check fuel rail pressure at key on (should be 870+ PSI)",
                "3. Inspect fuel filter condition and replace if overdue",
                "4. Test lift pump output pressure (min 45 PSI at idle)",
                "5. If pump pressure low, replace fuel lift pump assembly",
                "6. Clear codes and run test drive (20 min, varied RPM)",
                "7. Recheck scanner for returning codes",
            ]),
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        },
        {
            "session_id": "SESS-2024-0042",
            "fault_code": "P0093",
            "fault_name": "Fuel System Large Leak Detected",
            "vehicle_id": "UNIT-3318",
            "mileage": 245000,
            "symptoms": "Strong fuel smell in cab, wet spots under truck, CEL on",
            "top_cause": "Fuel injector o ring leak",
            "confidence": 0.65,
            "updated_confidence": 0.65,
            "estimated_cost": 420,
            "urgency": "critical",
            "escalation_reason": "Safety risk: visible fuel leak detected. Fire hazard, immediate escalation required.",
            "evidence_json": json.dumps({
                "fuel_pressure_psi": "500 to 870 PSI",
                "miles_since_filter": "Under 5,000 mi",
                "visible_leak": "Yes, I see a leak",
                "cold_start_issue": "No cold start issues",
            }),
            "status": "pending",
            "repair_steps_json": json.dumps([
                "1. SAFETY: Isolate vehicle, no hot work within 25 ft",
                "2. Verify fault code P0093 with diagnostic scanner",
                "3. Visually inspect all fuel line connections and injector o rings",
                "4. Identify leak source using UV dye if needed",
                "5. Replace damaged o ring(s) and torque to spec",
                "6. Pressure test fuel system before starting engine",
                "7. Clear codes and monitor for 30 min idle",
            ]),
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        },
        {
            "session_id": "SESS-2024-0043",
            "fault_code": "P0234",
            "fault_name": "Turbocharger Overboost Condition",
            "vehicle_id": "UNIT-5590",
            "mileage": 312000,
            "symptoms": "Excessive boost pressure, surging at highway speeds",
            "top_cause": "Wastegate actuator stuck closed",
            "confidence": 0.58,
            "updated_confidence": 0.62,
            "estimated_cost": 890,
            "urgency": "high",
            "escalation_reason": "Confidence below 70% (62%) and estimated cost exceeds $500",
            "evidence_json": json.dumps({
                "boost_pressure": "Above 35 PSI",
                "wastegate_movement": "Restricted / stuck",
                "turbo_noise": "Whining noise at high RPM",
                "oil_in_intercooler": "No oil detected",
            }),
            "status": "pending",
            "repair_steps_json": json.dumps([
                "1. Verify fault code P0234 with diagnostic scanner",
                "2. Monitor boost pressure with live data (max should be ~30 PSI)",
                "3. Inspect wastegate actuator rod for free movement",
                "4. Check actuator vacuum line for leaks",
                "5. If stuck, replace wastegate actuator assembly",
                "6. Recalibrate turbo VGT position if applicable",
                "7. Test drive under load, verify boost stays below limit",
            ]),
            "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
        },
        {
            "session_id": "SESS-2024-0038",
            "fault_code": "P0191",
            "fault_name": "Fuel Rail Pressure Sensor Circuit Range/Performance",
            "vehicle_id": "UNIT-2201",
            "mileage": 156000,
            "symptoms": "Low power complaint, fuel pressure reading low on scanner",
            "top_cause": "Clogged fuel filter (overdue replacement)",
            "confidence": 0.68,
            "updated_confidence": 0.78,
            "estimated_cost": 120,
            "urgency": "medium",
            "escalation_reason": "Initial confidence below 70%",
            "evidence_json": json.dumps({
                "fuel_pressure_psi": "500 to 870 PSI",
                "miles_since_filter": "Over 15,000 mi",
                "visible_leak": "No leak visible",
                "cold_start_issue": "No cold start issues",
            }),
            "status": "approved",
            "approved_by": "Mike R. (Fleet Manager)",
            "reviewer_notes": "Straightforward filter replacement. Approved: low cost, high likelihood.",
            "repair_steps_json": json.dumps([
                "1. Verify fault code P0191 with diagnostic scanner",
                "2. Remove and inspect fuel filter",
                "3. Install new Fleetguard FS1000 fuel filter",
                "4. Prime fuel system and bleed air",
                "5. Start engine and check for leaks",
                "6. Clear codes and verify rail pressure returns to 870+ PSI",
            ]),
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "decided_at": (datetime.now() - timedelta(hours=20)).isoformat(),
        },
        {
            "session_id": "SESS-2024-0035",
            "fault_code": "P0299",
            "fault_name": "Turbocharger Underboost",
            "vehicle_id": "UNIT-6678",
            "mileage": 289000,
            "symptoms": "Severe power loss on hills, black smoke, turbo not spooling",
            "top_cause": "Turbocharger bearing failure",
            "confidence": 0.45,
            "updated_confidence": 0.52,
            "estimated_cost": 3200,
            "urgency": "high",
            "escalation_reason": "Confidence 52% (below 70%) and estimated cost $3,200",
            "evidence_json": json.dumps({
                "boost_pressure": "Under 10 PSI at full throttle",
                "shaft_play": "Excessive radial play detected",
                "oil_consumption": "Burning ~1 qt per 500 miles",
                "exhaust_color": "Heavy blue/black smoke",
            }),
            "status": "rejected",
            "approved_by": "Sarah K. (Senior Tech Lead)",
            "reviewer_notes": "Confidence too low for $3,200 repair. Requesting second opinion and physical inspection before approving turbo replacement.",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "decided_at": (datetime.now() - timedelta(days=1, hours=18)).isoformat(),
        },
    ]

    for case in mock_cases:
        cols = ", ".join(case.keys())
        placeholders = ", ".join(["?"] * len(case))
        conn.execute(f"INSERT INTO cases ({cols}) VALUES ({placeholders})", list(case.values()))

    conn.commit()
    conn.close()


def get_cases(status_filter=None):
    """Fetch cases from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if status_filter:
        rows = conn.execute(
            "SELECT * FROM cases WHERE status = ? ORDER BY created_at DESC", (status_filter,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_case_decision(session_id, status, approved_by, notes):
    """Write an approval or rejection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        UPDATE cases
        SET status = ?, approved_by = ?, reviewer_notes = ?, decided_at = ?,
            sync_status = 'pending'
        WHERE session_id = ?
        """,
        (status, approved_by, notes, datetime.now().isoformat(), session_id),
    )
    conn.commit()
    conn.close()


# ── Initialize ───────────────────────────────────────────────────────────────
init_dashboard_db()
seed_mock_cases()

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body { font-family: 'Inter', sans-serif; }

    /* ── Animations ────────────────────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.3); }
        50% { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
    }
    @keyframes progressFill {
        from { width: 0%; }
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

    /* ── Summary Cards ─────────────────────────────────────────────────── */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .summary-card {
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
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .summary-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .summary-card-pending::before { background: #F59E0B; }
    .summary-card-approved::before { background: #10B981; }
    .summary-card-rejected::before { background: #EF4444; }
    .summary-card-cost::before { background: linear-gradient(90deg, #F59E0B, #EF4444); }
    .summary-card-total::before { background: #3B82F6; }
    .summary-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
    .summary-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.1rem 0;
    }
    .summary-value-pending { color: #F59E0B; }
    .summary-value-approved { color: #10B981; }
    .summary-value-rejected { color: #EF4444; }
    .summary-value-cost { color: #F59E0B; }
    .summary-value-total { color: #3B82F6; }
    .summary-label {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 500;
    }

    /* ── Case Cards ────────────────────────────────────────────────────── */
    .case-card-outer {
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .case-card-outer:hover {
        border-color: #3D4A6C;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }
    .case-border-critical { border-left: 4px solid #EF4444; }
    .case-border-high { border-left: 4px solid #F59E0B; }
    .case-border-medium { border-left: 4px solid #3B82F6; }
    .case-border-low { border-left: 4px solid #6B7280; }

    /* ── Severity Badge ────────────────────────────────────────────────── */
    .severity-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.2rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .severity-critical { background: #EF444422; color: #EF4444; }
    .severity-high { background: #F59E0B22; color: #F59E0B; }
    .severity-medium { background: #3B82F622; color: #3B82F6; }
    .severity-low { background: #6B728022; color: #9CA3AF; }

    /* ── Status Badge ──────────────────────────────────────────────────── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.85rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .status-pending { background: #F59E0B22; color: #F59E0B; }
    .status-approved { background: #10B98122; color: #10B981; }
    .status-rejected { background: #EF444422; color: #EF4444; }

    /* ── Confidence Bar ────────────────────────────────────────────────── */
    .conf-bar-track {
        background: #0a0f1f;
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
        flex: 1;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 6px;
        animation: progressFill 0.8s ease-out;
    }
    .conf-display {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .conf-value {
        font-weight: 800;
        font-size: 1.1rem;
        min-width: 45px;
    }

    /* ── Detail Fields ─────────────────────────────────────────────────── */
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.8rem;
        margin: 0.8rem 0;
    }
    .detail-item {
        background: #0f1629;
        border-radius: 10px;
        padding: 0.8rem;
        border: 1px solid #2D3A5C44;
    }
    .detail-label {
        font-size: 0.72rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .detail-value {
        font-size: 0.92rem;
        color: #E5E7EB;
        font-weight: 600;
    }

    /* ── Evidence Table ────────────────────────────────────────────────── */
    .evidence-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .evidence-table th {
        background: #0f1629;
        color: #9CA3AF;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.6rem 1rem;
        text-align: left;
        font-weight: 600;
    }
    .evidence-table td {
        padding: 0.5rem 1rem;
        font-size: 0.88rem;
        color: #E5E7EB;
        border-bottom: 1px solid #2D3A5C33;
    }
    .evidence-table tr:last-child td { border-bottom: none; }

    /* ── Repair Steps ──────────────────────────────────────────────────── */
    .repair-step {
        display: flex;
        align-items: flex-start;
        gap: 0.7rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2D3A5C22;
    }
    .repair-step:last-child { border-bottom: none; }
    .repair-step-num {
        width: 24px; height: 24px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F59E0B33, #F59E0B11);
        color: #F59E0B;
        font-size: 0.72rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 0.1rem;
    }
    .repair-step-text {
        font-size: 0.88rem;
        color: #E5E7EB;
        line-height: 1.4;
    }

    /* ── Decision Info ─────────────────────────────────────────────────── */
    .decision-box {
        background: #0f1629;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #2D3A5C44;
        margin: 0.5rem 0;
    }
    .decision-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .decision-by {
        font-size: 0.85rem;
        color: #9CA3AF;
    }
    .decision-notes {
        font-size: 0.88rem;
        color: #E5E7EB;
        font-style: italic;
        padding: 0.5rem 0.8rem;
        border-left: 3px solid #3B82F6;
        background: #16213E;
        border-radius: 0 8px 8px 0;
    }

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

    /* ── Sync History Table ────────────────────────────────────────────── */
    .sync-history-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid #2D3A5C33;
        font-size: 0.85rem;
    }
    .sync-history-row:last-child { border-bottom: none; }
    .sync-history-icon {
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    .sync-history-icon-ok { background: #10B98122; }
    .sync-history-icon-err { background: #EF444422; }
    .sync-history-details { flex: 1; }
    .sync-history-time { color: #6B7280; font-size: 0.75rem; }

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
    st.session_state["dashboard_role"] = role
    user_name = ROLE_NAMES.get(role, "Zion Adedipe")
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
    import sys
    import time as _time
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from backend.sync import (
        check_connectivity, get_sync_stats, sync_to_cloud,
        get_last_sync_time, get_pending_count, format_time_ago,
        get_sync_history, log_sync_event,
    )

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

    if is_online and pending_total > 0:
        if st.button("Sync Now", type="primary", use_container_width=True):
            with st.spinner("Syncing to cloud..."):
                _time.sleep(1)
                sync_result = sync_to_cloud()
            st.success(
                f"Synced {sync_result['cases_synced']} cases, "
                f"{sync_result['decisions_synced']} decisions"
            )
            if sync_result["errors"]:
                st.error(f"Errors: {sync_result['errors']}")
            st.rerun()
    elif not is_online and pending_total > 0:
        st.info(f"{pending_total} record(s) queued. Go online to sync.")



# ── Breadcrumb ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="breadcrumb">'
    '<a href="/">Home</a>'
    '<span class="sep">›</span>'
    '<span class="active">Approval Dashboard</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Page Header ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-header">'
    '<span class="page-header-title">Approval Dashboard</span>'
    '<span class="page-header-badge">' + role + '</span>'
    '</div>',
    unsafe_allow_html=True,
)
st.caption("Review escalated cases that require human review before repair steps can be issued.")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Offline / Reconnect Banner ──────────────────────────────────────────────
_is_online = st.session_state.get("is_online", True)
if not _is_online:
    st.markdown(
        '<div class="offline-banner">'
        '<span>Offline Mode: All data saved locally. Will sync when connection is restored.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

if st.session_state.get("show_reconnect_sync"):
    _pending = get_pending_count()
    if _pending > 0:
        st.markdown(
            '<div class="online-banner">'
            '<span>Connection restored! Syncing offline data...</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        progress_bar = st.progress(0, text=f"Syncing... {_pending} records pending")
        sync_result = sync_to_cloud()
        total_synced = sync_result["cases_synced"] + sync_result["decisions_synced"]
        for i in range(_pending):
            _time.sleep(0.25 + random.uniform(0, 0.15))
            remaining = _pending - i - 1
            progress_bar.progress(
                (i + 1) / _pending,
                text=f"Syncing... {remaining} records remaining",
            )
        progress_bar.progress(1.0, text=f"Synced! {total_synced} records uploaded to cloud")
        log_sync_event(
            "reconnect_sync",
            cases_synced=sync_result["cases_synced"],
            decisions_synced=sync_result["decisions_synced"],
        )
        _time.sleep(1.5)
        st.session_state.show_reconnect_sync = False
        st.rerun()
    else:
        st.markdown(
            '<div class="online-banner">'
            '<span>Back online! All records are already synced.</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.session_state.show_reconnect_sync = False

# ── Summary Metrics ──────────────────────────────────────────────────────────
all_cases = get_cases()
pending = [c for c in all_cases if c["status"] == "pending"]
approved = [c for c in all_cases if c["status"] == "approved"]
rejected = [c for c in all_cases if c["status"] == "rejected"]
total_cost = sum(c.get("estimated_cost", 0) for c in pending)

st.markdown(
    f"""
    <div class="summary-grid">
        <div class="summary-card summary-card-total" style="animation-delay:0.05s;">
            <div class="summary-icon"></div>
            <div class="summary-value summary-value-total">{len(all_cases)}</div>
            <div class="summary-label">Total Cases</div>
        </div>
        <div class="summary-card summary-card-pending" style="animation-delay:0.1s;">
            <div class="summary-icon"></div>
            <div class="summary-value summary-value-pending">{len(pending)}</div>
            <div class="summary-label">Pending</div>
        </div>
        <div class="summary-card summary-card-approved" style="animation-delay:0.15s;">
            <div class="summary-icon"></div>
            <div class="summary-value summary-value-approved">{len(approved)}</div>
            <div class="summary-label">Approved</div>
        </div>
        <div class="summary-card summary-card-rejected" style="animation-delay:0.2s;">
            <div class="summary-icon"></div>
            <div class="summary-value summary-value-rejected">{len(rejected)}</div>
            <div class="summary-label">Rejected</div>
        </div>
        <div class="summary-card summary-card-cost" style="animation-delay:0.25s;">
            <div class="summary-icon"></div>
            <div class="summary-value summary-value-cost">${total_cost:,}</div>
            <div class="summary-label">Pending Cost</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tabs: Pending | History | Sync Status ───────────────────────────────────
tab_pending, tab_history, tab_sync = st.tabs(
    ["Pending Approval", "Decision History", "Sync Status"]
)


# ── Helper: render a case card ───────────────────────────────────────────────
def render_case_card(case, allow_actions=False):
    """Render a single case as a detailed card."""
    urgency = case.get("urgency", "medium")
    status = case.get("status", "pending")

    evidence = {}
    try:
        evidence = json.loads(case.get("evidence_json", "{}"))
    except (json.JSONDecodeError, TypeError):
        pass

    repair_steps = []
    try:
        repair_steps = json.loads(case.get("repair_steps_json", "[]"))
    except (json.JSONDecodeError, TypeError):
        pass

    # Card header row
    header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
    with header_col1:
        st.markdown(
            f"#### {case['fault_code']}  |  {case.get('fault_name', 'Unknown')}"
        )
    with header_col2:
        st.markdown(
            f'<span class="severity-badge severity-{urgency}">{urgency.upper()}</span>',
            unsafe_allow_html=True,
        )
    with header_col3:
        st.markdown(
            f'<span class="status-badge status-{status}">{status.upper()}</span>',
            unsafe_allow_html=True,
        )

    # Detail grid
    conf = case.get("updated_confidence") or case.get("confidence", 0)
    conf_pct = int(conf * 100)
    conf_color = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.5 else "#EF4444"

    created = case.get("created_at", "")
    age_str = "N/A"
    if created:
        try:
            dt = datetime.fromisoformat(created)
            age = datetime.now() - dt
            if age.total_seconds() < 3600:
                age_str = f"{int(age.total_seconds() / 60)} min ago"
            elif age.total_seconds() < 86400:
                age_str = f"{int(age.total_seconds() / 3600)} hr ago"
            else:
                age_str = f"{age.days} day(s) ago"
        except ValueError:
            age_str = created[:16]

    st.markdown(
        f"""
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Vehicle</div>
                <div class="detail-value">{case.get('vehicle_id', 'N/A')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Mileage</div>
                <div class="detail-value">{case.get('mileage', 0):,} mi</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Top Cause</div>
                <div class="detail-value">{case.get('top_cause', 'N/A')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Est. Cost</div>
                <div class="detail-value" style="color:#F59E0B">${case.get('estimated_cost', 0):,}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Submitted</div>
                <div class="detail-value">{age_str}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Session</div>
                <div class="detail-value" style="font-size:0.8rem">{case.get('session_id', 'N/A')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Confidence bar
    st.markdown(
        f"""
        <div style="margin: 0.6rem 0;">
            <div class="detail-label" style="margin-bottom:0.4rem;">Confidence Score</div>
            <div class="conf-display">
                <span class="conf-value" style="color:{conf_color}">{conf_pct}%</span>
                <div class="conf-bar-track">
                    <div class="conf-bar-fill" style="width:{conf_pct}%; background:linear-gradient(90deg, {conf_color}, {conf_color}88);"></div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:#6B7280; margin-top:0.2rem;">
                Initial: {case.get('confidence', 0):.0%} → Updated: {conf:.0%}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Symptoms
    st.markdown(f"**Symptoms:** {case.get('symptoms', 'N/A')}")

    # Escalation reason
    reason = case.get("escalation_reason", "")
    if reason:
        if "safety" in reason.lower() or "fire" in reason.lower():
            st.error(reason)
        else:
            st.warning(reason)

    # Evidence section
    with st.expander("Evidence Collected", expanded=(status == "pending")):
        if evidence:
            table_html = '<table class="evidence-table"><tr><th>Parameter</th><th>Response</th></tr>'
            for key, val in evidence.items():
                label = key.replace("_", " ").title()
                table_html += f'<tr><td>{label}</td><td><strong>{val}</strong></td></tr>'
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.caption("No evidence data available.")

    # Repair steps preview
    role = st.session_state.get("dashboard_role", "Fleet Manager")
    with st.expander("Proposed Repair Steps", expanded=False):
        if repair_steps:
            steps_html = ""
            for step in repair_steps:
                # Extract step number if present
                parts = step.split(". ", 1)
                if len(parts) == 2 and parts[0].strip().isdigit():
                    num = parts[0].strip()
                    text = parts[1]
                else:
                    num = "•"
                    text = step
                steps_html += (
                    f'<div class="repair-step">'
                    f'<div class="repair-step-num">{num}</div>'
                    f'<div class="repair-step-text">{text}</div>'
                    f'</div>'
                )
            st.markdown(steps_html, unsafe_allow_html=True)
        else:
            st.caption("No repair steps generated yet.")

    # Decision info (for history)
    if status in ("approved", "rejected"):
        decided = case.get("decided_at", "")
        status_icon = ""
        status_color = "#10B981" if status == "approved" else "#EF4444"

        decision_html = f"""
        <div class="decision-box">
            <div class="decision-header">
                <span style="font-size:1.1rem">{status_icon}</span>
                <span style="font-weight:700; color:{status_color}; text-transform:uppercase;">{status}</span>
            </div>
            <div class="decision-by">
                By <strong>{case.get('approved_by', 'N/A')}</strong>
                {f' on {decided[:16]}' if decided else ''}
            </div>
        """
        if case.get("reviewer_notes"):
            decision_html += f'<div class="decision-notes" style="margin-top:0.5rem">{case["reviewer_notes"]}</div>'
        decision_html += '</div>'
        st.markdown(decision_html, unsafe_allow_html=True)

    # Read only notice for junior technicians
    if allow_actions and status == "pending" and role == "Junior Technician":
        st.info("View only: approval requires Fleet Manager or Senior Technician.")

    # Action buttons (for pending cases)
    if allow_actions and status == "pending" and role != "Junior Technician":
        st.markdown("---")

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            reviewer_name = st.text_input(
                "Your name",
                value="",
                placeholder="e.g. Mike R.",
                key=f"name_{case['session_id']}",
            )
        with action_col2:
            pass  # spacer

        notes = st.text_area(
            "Reviewer notes (optional)",
            placeholder="Add context for your decision...",
            key=f"notes_{case['session_id']}",
            height=80,
        )

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        with btn_col1:
            if st.button(
                "Approve",
                key=f"approve_{case['session_id']}",
                type="primary",
                use_container_width=True,
            ):
                name = reviewer_name or f"{role}"
                update_case_decision(
                    case["session_id"], "approved", f"{name} ({role})", notes
                )
                audit_log({
                    "log_id": f"LOG-{case['session_id']}-APPR",
                    "session_id": case["session_id"],
                    "agent_id": "human_reviewer",
                    "action": "human_approval",
                    "fault_code": case.get("fault_code", ""),
                    "inputs": {
                        "reviewer": f"{name} ({role})",
                        "review_action": "approve",
                    },
                    "output": {
                        "decision": "approved",
                        "reviewer_notes": notes or "",
                    },
                    "confidence": case.get("updated_confidence") or case.get("confidence", 0),
                    "human_approved": True,
                    "model_used": None,
                })
                st.success("Case approved!")
                st.rerun()
        with btn_col2:
            if st.button(
                "Reject",
                key=f"reject_{case['session_id']}",
                use_container_width=True,
            ):
                name = reviewer_name or f"{role}"
                update_case_decision(
                    case["session_id"], "rejected", f"{name} ({role})", notes
                )
                audit_log({
                    "log_id": f"LOG-{case['session_id']}-REJ",
                    "session_id": case["session_id"],
                    "agent_id": "human_reviewer",
                    "action": "human_rejection",
                    "fault_code": case.get("fault_code", ""),
                    "inputs": {
                        "reviewer": f"{name} ({role})",
                        "review_action": "reject",
                    },
                    "output": {
                        "decision": "rejected",
                        "reviewer_notes": notes or "",
                    },
                    "confidence": case.get("updated_confidence") or case.get("confidence", 0),
                    "human_approved": False,
                    "model_used": None,
                })
                st.error("Case rejected.")
                st.rerun()

    st.markdown("---")


# ── Tab: Pending Approval ────────────────────────────────────────────────────
with tab_pending:
    pending_cases = get_cases("pending")
    if not pending_cases:
        st.markdown(
            """
            <div style="text-align:center; padding:3rem 1rem;">
                <div style="font-size:1.1rem; color:#10B981; font-weight:600;">All Clear</div>
                <div style="font-size:0.9rem; color:#9CA3AF;">No cases pending approval at this time.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"Showing {len(pending_cases)} case(s) awaiting your review.")
        for case in pending_cases:
            render_case_card(case, allow_actions=True)

# ── Tab: Decision History ────────────────────────────────────────────────────
with tab_history:
    st.markdown(
        '<div class="page-header" style="margin-bottom:0.8rem;">'
        '<span style="font-size:1.1rem; font-weight:700; color:#E5E7EB;">Decision History & Audit Trail</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Filters
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    with filter_col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "approved", "rejected"],
            format_func=lambda x: x.capitalize(),
        )
    with filter_col2:
        all_codes = sorted(set(c.get("fault_code", "") for c in all_cases))
        code_filter = st.selectbox("Fault Code", ["All"] + all_codes)
    with filter_col3:
        urgency_filter = st.selectbox(
            "Urgency", ["All", "critical", "high", "medium", "low"],
            format_func=lambda x: x.capitalize(),
        )
    with filter_col4:
        date_range = st.selectbox("Time Range", ["All Time", "Last 24h", "Last 7 days", "Last 30 days"])

    # Apply filters
    history = [c for c in all_cases if c["status"] in ("approved", "rejected")]

    if status_filter != "All":
        history = [c for c in history if c["status"] == status_filter]
    if code_filter != "All":
        history = [c for c in history if c.get("fault_code") == code_filter]
    if urgency_filter != "All":
        history = [c for c in history if c.get("urgency") == urgency_filter]
    if date_range != "All Time":
        now = datetime.now()
        cutoff_map = {"Last 24h": 1, "Last 7 days": 7, "Last 30 days": 30}
        cutoff = now - timedelta(days=cutoff_map[date_range])
        filtered = []
        for c in history:
            try:
                dt = datetime.fromisoformat(c.get("created_at", ""))
                if dt >= cutoff:
                    filtered.append(c)
            except ValueError:
                filtered.append(c)
        history = filtered

    if not history:
        st.markdown(
            """
            <div style="text-align:center; padding:2rem 1rem;">
                <div style="font-size:0.95rem; color:#9CA3AF;">No decisions match your filters.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"Showing {len(history)} decision(s).")
        for case in history:
            render_case_card(case, allow_actions=False)

# ── Tab: Sync Status ────────────────────────────────────────────────────────
with tab_sync:
    st.markdown(
        '<div class="page-header" style="margin-bottom:0.8rem;">'
        '<span style="font-size:1.1rem; font-weight:700; color:#E5E7EB;">'
        'Sync Status & History</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Connection status card
    sync_col1, sync_col2, sync_col3, sync_col4 = st.columns(4)

    _eff_online = st.session_state.get("is_online", True)
    _stats = get_sync_stats()
    _pending = _stats["cases_pending"] + _stats["decisions_pending"]
    _synced = _stats["cases_synced"] + _stats["decisions_synced"]
    _last = get_last_sync_time()
    _last_text = format_time_ago(_last)

    with sync_col1:
        status_color = "#10B981" if _eff_online else "#F59E0B"
        status_label = "Online" if _eff_online else "Offline"
        st.markdown(
            f"""
            <div class="summary-card" style="border-top: 3px solid {status_color};">
                <div class="summary-icon" style="font-size:1.6rem;">
                    {'Online' if _eff_online else 'Offline'}
                </div>
                <div class="summary-value" style="color:{status_color}; font-size:1.3rem;">
                    {status_label}
                </div>
                <div class="summary-label">Connection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sync_col2:
        st.markdown(
            f"""
            <div class="summary-card" style="border-top: 3px solid {'#F59E0B' if _pending > 0 else '#10B981'};">
                <div class="summary-icon"></div>
                <div class="summary-value" style="color:{'#F59E0B' if _pending > 0 else '#10B981'}; font-size:1.3rem;">
                    {_pending}
                </div>
                <div class="summary-label">Pending Sync</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sync_col3:
        st.markdown(
            f"""
            <div class="summary-card" style="border-top: 3px solid #10B981;">
                <div class="summary-icon"></div>
                <div class="summary-value" style="color:#10B981; font-size:1.3rem;">
                    {_synced}
                </div>
                <div class="summary-label">Total Synced</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sync_col4:
        st.markdown(
            f"""
            <div class="summary-card" style="border-top: 3px solid #3B82F6;">
                <div class="summary-icon"></div>
                <div class="summary-value" style="color:#3B82F6; font-size:1rem;">
                    {_last_text}
                </div>
                <div class="summary-label">Last Sync</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Breakdown
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    det_col1, det_col2 = st.columns(2)
    with det_col1:
        st.markdown("##### Records Breakdown")
        st.markdown(
            f"""
            <div class="sync-stats-card">
                <div class="sync-stat-row">
                    <span class="sync-stat-label">Cases pending</span>
                    <span class="sync-stat-value">{_stats['cases_pending']}</span>
                </div>
                <div class="sync-stat-row">
                    <span class="sync-stat-label">Cases synced</span>
                    <span class="sync-stat-value" style="color:#10B981">{_stats['cases_synced']}</span>
                </div>
                <div class="sync-stat-row">
                    <span class="sync-stat-label">Decisions pending</span>
                    <span class="sync-stat-value">{_stats['decisions_pending']}</span>
                </div>
                <div class="sync-stat-row">
                    <span class="sync-stat-label">Decisions synced</span>
                    <span class="sync-stat-value" style="color:#10B981">{_stats['decisions_synced']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with det_col2:
        st.markdown("##### Sync History (Last 10)")
        sync_history = get_sync_history(limit=10)
        if not sync_history:
            st.caption("No sync events recorded yet.")
        else:
            history_html = '<div class="sync-stats-card">'
            for event in sync_history:
                evt_type = event.get("event_type", "")
                cases_s = event.get("cases_synced", 0)
                decs_s = event.get("decisions_synced", 0)
                errs = event.get("errors_count", 0)
                ts = event.get("timestamp", "")
                ts_ago = format_time_ago(ts)

                icon_class = "sync-history-icon-ok" if errs == 0 else "sync-history-icon-err"
                icon = ""
                label = "Reconnect sync" if "reconnect" in evt_type else "Cloud sync"
                detail = f"{cases_s} cases, {decs_s} decisions"
                if errs > 0:
                    detail += f", {errs} error(s)"

                history_html += (
                    f'<div class="sync-history-row">'
                    f'<div class="sync-history-icon {icon_class}">{icon}</div>'
                    f'<div class="sync-history-details">'
                    f'<div style="color:#E5E7EB; font-weight:600; font-size:0.83rem;">{label}</div>'
                    f'<div style="color:#9CA3AF; font-size:0.78rem;">{detail}</div>'
                    f'</div>'
                    f'<div class="sync-history-time">{ts_ago}</div>'
                    f'</div>'
                )
            history_html += '</div>'
            st.markdown(history_html, unsafe_allow_html=True)
