import streamlit as st
import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="TRACE AI — Approval Dashboard", page_icon="📋", layout="wide")

# ── Database Setup ───────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard.db")


def init_dashboard_db():
    """Create the dashboard tables if they don't exist."""
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
            decided_at TEXT
        )
        """
    )
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
                "miles_since_filter": "5,000-15,000 mi",
                "visible_leak": "No leak visible",
                "cold_start_issue": "Yes, hard cold start",
            }),
            "status": "pending",
            "repair_steps_json": json.dumps([
                "1. Verify fault code P0191 with diagnostic scanner",
                "2. Check fuel rail pressure at key-on (should be 870+ PSI)",
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
            "top_cause": "Fuel injector o-ring leak",
            "confidence": 0.65,
            "updated_confidence": 0.65,
            "estimated_cost": 420,
            "urgency": "critical",
            "escalation_reason": "Safety risk: visible fuel leak detected. Fire hazard — immediate escalation required.",
            "evidence_json": json.dumps({
                "fuel_pressure_psi": "500-870 PSI",
                "miles_since_filter": "Under 5,000 mi",
                "visible_leak": "Yes, I see a leak",
                "cold_start_issue": "No cold start issues",
            }),
            "status": "pending",
            "repair_steps_json": json.dumps([
                "1. SAFETY: Isolate vehicle — no hot work within 25 ft",
                "2. Verify fault code P0093 with diagnostic scanner",
                "3. Visually inspect all fuel line connections and injector o-rings",
                "4. Identify leak source using UV dye if needed",
                "5. Replace damaged o-ring(s) and torque to spec",
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
                "fuel_pressure_psi": "500-870 PSI",
                "miles_since_filter": "Over 15,000 mi",
                "visible_leak": "No leak visible",
                "cold_start_issue": "No cold start issues",
            }),
            "status": "approved",
            "approved_by": "Mike R. (Fleet Manager)",
            "reviewer_notes": "Straightforward filter replacement. Approved — low cost, high likelihood.",
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
        SET status = ?, approved_by = ?, reviewer_notes = ?, decided_at = ?
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
    .case-card {
        background: #16213E;
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .case-card-critical {
        border-left: 4px solid #EF4444;
    }
    .case-card-high {
        border-left: 4px solid #F59E0B;
    }
    .case-card-medium {
        border-left: 4px solid #3B82F6;
    }
    .badge-pending {
        background: #F59E0B22;
        color: #F59E0B;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-approved {
        background: #10B98122;
        color: #10B981;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-rejected {
        background: #EF444422;
        color: #EF4444;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .metric-highlight {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F59E0B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Dashboard Settings")

    role = st.selectbox(
        "Your Role",
        ["Fleet Manager", "Senior Technician"],
        help="Different roles see different information emphasis.",
    )
    st.session_state["dashboard_role"] = role

    st.divider()
    st.markdown("**Navigation**")
    st.page_link("ui.py", label="Home", icon="🏠")
    st.page_link("pages/1_Technician_Chatbot.py", label="Chatbot", icon="💬")
    st.page_link("pages/2_Approval_Dashboard.py", label="Dashboard", icon="📋")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 📋 Approval Dashboard")
st.caption(f"Logged in as: **{role}** | Showing cases that require human review")

# ── Summary Metrics ──────────────────────────────────────────────────────────
all_cases = get_cases()
pending = [c for c in all_cases if c["status"] == "pending"]
approved = [c for c in all_cases if c["status"] == "approved"]
rejected = [c for c in all_cases if c["status"] == "rejected"]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Pending", len(pending))
with m2:
    st.metric("Approved", len(approved))
with m3:
    st.metric("Rejected", len(rejected))
with m4:
    total_cost = sum(c.get("estimated_cost", 0) for c in pending)
    st.metric("Pending Est. Cost", f"${total_cost:,}")

st.divider()

# ── Tabs: Pending | History ──────────────────────────────────────────────────
tab_pending, tab_history = st.tabs(["🔶 Pending Approval", "📜 Decision History"])

# ── Helper: render a case card ───────────────────────────────────────────────
def render_case_card(case, allow_actions=False):
    """Render a single case as a detailed card."""
    urgency = case.get("urgency", "medium")
    status = case.get("status", "pending")
    card_class = f"case-card case-card-{urgency}"
    badge_class = f"badge-{status}"

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

    # Card header
    col_title, col_badge = st.columns([4, 1])
    with col_title:
        st.markdown(
            f"### {case['fault_code']} — {case.get('fault_name', 'Unknown')}"
        )
    with col_badge:
        st.markdown(
            f'<span class="{badge_class}">{status.upper()}</span>',
            unsafe_allow_html=True,
        )

    # Key details in columns
    role = st.session_state.get("dashboard_role", "Fleet Manager")

    if role == "Fleet Manager":
        # Manager view: cost-focused
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"**Vehicle:** {case.get('vehicle_id', '—')}")
            st.caption(f"Mileage: {case.get('mileage', 0):,} mi")
        with c2:
            conf = case.get("updated_confidence") or case.get("confidence", 0)
            color = "#10B981" if conf >= 0.7 else "#F59E0B" if conf >= 0.5 else "#EF4444"
            st.markdown(f"**Confidence:** <span style='color:{color}'>{conf:.0%}</span>", unsafe_allow_html=True)
            st.caption(f"Initial: {case.get('confidence', 0):.0%}")
        with c3:
            st.markdown(f"**Est. Cost:** ${case.get('estimated_cost', 0):,}")
            st.caption(f"Urgency: {urgency.upper()}")
        with c4:
            created = case.get("created_at", "")
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
                    st.markdown(f"**Submitted:** {age_str}")
                except ValueError:
                    st.markdown(f"**Submitted:** {created[:16]}")
            st.caption(f"Session: {case.get('session_id', '—')}")
    else:
        # Senior Technician view: technical focus
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Top Cause:** {case.get('top_cause', '—')}")
            st.caption(f"Fault: {case['fault_code']} | Vehicle: {case.get('vehicle_id', '—')}")
        with c2:
            conf = case.get("updated_confidence") or case.get("confidence", 0)
            bar_fill = int(conf * 20)
            bar = "█" * bar_fill + "░" * (20 - bar_fill)
            st.markdown(f"**Confidence:** `{bar}` {conf:.0%}")
            st.caption(f"Initial: {case.get('confidence', 0):.0%} → Updated: {conf:.0%}")
        with c3:
            st.markdown(f"**Urgency:** {urgency.upper()}")
            st.caption(f"Mileage: {case.get('mileage', 0):,} mi")

    # Symptoms
    st.markdown(f"**Symptoms:** {case.get('symptoms', '—')}")

    # Escalation reason
    reason = case.get("escalation_reason", "")
    if reason:
        if "safety" in reason.lower() or "fire" in reason.lower():
            st.error(f"⚠️ {reason}")
        else:
            st.warning(f"🔶 {reason}")

    # Expandable sections
    with st.expander("📊 Evidence Collected"):
        if evidence:
            for key, val in evidence.items():
                label = key.replace("_", " ").title()
                st.markdown(f"- **{label}:** {val}")
        else:
            st.caption("No evidence data available.")

    if role == "Senior Technician" or status != "pending":
        with st.expander("🔧 Proposed Repair Steps"):
            if repair_steps:
                for step in repair_steps:
                    st.markdown(f"  {step}")
            else:
                st.caption("No repair steps generated yet.")

    # Decision info (for history)
    if status in ("approved", "rejected"):
        decided = case.get("decided_at", "")
        st.markdown(
            f"**Decision:** {status.upper()} by **{case.get('approved_by', '—')}**"
            + (f" on {decided[:16]}" if decided else "")
        )
        if case.get("reviewer_notes"):
            st.info(f"💬 Notes: {case['reviewer_notes']}")

    # Action buttons (for pending cases)
    if allow_actions and status == "pending":
        st.markdown("---")
        reviewer_name = st.text_input(
            "Your name",
            value="",
            placeholder="e.g. Mike R.",
            key=f"name_{case['session_id']}",
        )
        notes = st.text_area(
            "Reviewer notes (optional)",
            placeholder="Add context for your decision...",
            key=f"notes_{case['session_id']}",
            height=80,
        )

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        with btn_col1:
            if st.button(
                "✅ Approve",
                key=f"approve_{case['session_id']}",
                type="primary",
                use_container_width=True,
            ):
                name = reviewer_name or f"{role}"
                update_case_decision(
                    case["session_id"], "approved", f"{name} ({role})", notes
                )
                st.success("Case approved!")
                st.rerun()
        with btn_col2:
            if st.button(
                "❌ Reject",
                key=f"reject_{case['session_id']}",
                use_container_width=True,
            ):
                name = reviewer_name or f"{role}"
                update_case_decision(
                    case["session_id"], "rejected", f"{name} ({role})", notes
                )
                st.error("Case rejected.")
                st.rerun()

    st.markdown("---")


# ── Tab: Pending Approval ────────────────────────────────────────────────────
with tab_pending:
    pending_cases = get_cases("pending")
    if not pending_cases:
        st.success("No cases pending approval. All clear!")
    else:
        st.caption(f"Showing {len(pending_cases)} case(s) awaiting your review.")
        for case in pending_cases:
            render_case_card(case, allow_actions=True)

# ── Tab: Decision History (with filters) ─────────────────────────────────────
with tab_history:
    st.subheader("Decision History & Audit Trail")

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
        st.info("No decisions match your filters.")
    else:
        st.caption(f"Showing {len(history)} decision(s).")
        for case in history:
            render_case_card(case, allow_actions=False)
