import streamlit as st
import sys, os, sqlite3
from PIL import Image

_logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))

# DB paths
_DASHBOARD_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dashboard.db")
_TRACE_AI_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "trace_ai.db")


def _get_kpi_stats():
    """Query SQLite databases for live KPI numbers."""
    stats = {
        "resolved": 0,
        "pending": 0,
        "avg_confidence": 0,
        "cases_today": 0,
    }
    try:
        con = sqlite3.connect(_DASHBOARD_DB)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM cases WHERE status != 'pending'")
        stats["resolved"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'pending'")
        stats["pending"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cases WHERE DATE(created_at) = DATE('now')")
        stats["cases_today"] = cur.fetchone()[0]
        con.close()
    except Exception:
        pass
    try:
        con = sqlite3.connect(_DASHBOARD_DB)
        cur = con.cursor()
        cur.execute("SELECT AVG(COALESCE(updated_confidence, confidence)) FROM cases")
        val = cur.fetchone()[0]
        if val is not None:
            stats["avg_confidence"] = round(val * 100) if val <= 1 else round(val)
        con.close()
    except Exception:
        pass
    return stats

st.set_page_config(
    page_title="TRACE AI",
    page_icon=_logo,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global resets & typography ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body { font-family: 'Inter', sans-serif; }

    /* ── Breadcrumb ─────────────────────────────────────────────────────── */
    .breadcrumb {
        font-size: 0.82rem;
        color: #6B7280;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .breadcrumb .active { color: #F59E0B; font-weight: 600; }
    .breadcrumb .sep { color: #4B5563; }

    /* ── Animated Hero ─────────────────────────────────────────────────── */
    @keyframes heroGlow {
        0%, 100% { text-shadow: 0 0 20px rgba(245,158,11,0.3); }
        50% { text-shadow: 0 0 40px rgba(245,158,11,0.6), 0 0 80px rgba(239,68,68,0.2); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(24px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.3); }
        50% { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
    }

    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    .hero-title {
        font-size: 3.4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #F59E0B 0%, #EF4444 50%, #F59E0B 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: heroGlow 3s ease-in-out infinite;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .hero-acronym {
        font-size: 1rem;
        color: #9CA3AF;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .hero-tagline {
        font-size: 1.35rem;
        color: #E5E7EB;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .hero-desc {
        font-size: 1rem;
        color: #9CA3AF;
        max-width: 640px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── KPI Metric Cards ──────────────────────────────────────────────── */
    .kpi-card {
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out both;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #F59E0B, #EF4444);
        border-radius: 14px 14px 0 0;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #F59E0B;
        box-shadow: 0 8px 30px rgba(245,158,11,0.15);
    }
    .kpi-icon { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #F59E0B;
        margin: 0.2rem 0;
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    .kpi-delta {
        font-size: 0.75rem;
        color: #10B981;
        font-weight: 600;
        margin-top: 0.3rem;
    }

    /* ── Workflow Diagram ───────────────────────────────────────────────── */
    .workflow-section {
        margin: 1.5rem 0;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    .workflow-section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #E5E7EB;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .workflow-container {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0;
        padding: 1.5rem 0.5rem;
        background: linear-gradient(145deg, #0f1629 0%, #16213E 100%);
        border-radius: 16px;
        border: 1px solid #2D3A5C;
        overflow-x: auto;
    }
    .wf-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 1rem 0.8rem;
        min-width: 110px;
        position: relative;
        transition: transform 0.3s ease;
    }
    .wf-step:hover { transform: translateY(-3px); }
    .wf-icon {
        width: 50px; height: 50px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 0.5rem;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .wf-step:hover .wf-icon {
        border-color: #F59E0B;
        box-shadow: 0 0 20px rgba(245,158,11,0.3);
    }
    .wf-icon-1 { background: linear-gradient(135deg, #1e3a5f, #2563EB); }
    .wf-icon-2 { background: linear-gradient(135deg, #2d1f4e, #7C3AED); }
    .wf-icon-3 { background: linear-gradient(135deg, #1a3a2f, #059669); }
    .wf-icon-4 { background: linear-gradient(135deg, #3a2a1a, #D97706); }
    .wf-icon-5 { background: linear-gradient(135deg, #3a1a1a, #DC2626); }
    .wf-icon-6 { background: linear-gradient(135deg, #1a3a1a, #10B981); }
    .wf-label {
        font-size: 0.78rem;
        color: #E5E7EB;
        font-weight: 600;
        margin-bottom: 0.15rem;
        white-space: nowrap;
    }
    .wf-sub {
        font-size: 0.68rem;
        color: #6B7280;
        max-width: 100px;
    }
    .wf-arrow {
        color: #F59E0B;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0.1rem;
        opacity: 0.6;
    }

    /* ── Navigation Cards ──────────────────────────────────────────────── */
    .nav-card {
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out both;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .nav-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #F59E0B, #EF4444);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    .nav-card:hover::after { transform: scaleX(1); }
    .nav-card:hover {
        border-color: #F59E0B;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(245,158,11,0.12);
    }
    .nav-card-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
    .nav-card h3 {
        color: #F59E0B;
        margin-bottom: 0.5rem;
        font-size: 1.15rem;
    }
    .nav-card p {
        color: #9CA3AF;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    /* ── How It Works Steps ────────────────────────────────────────────── */
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .step-card {
        background: linear-gradient(145deg, #16213E 0%, #1a2744 100%);
        border: 1px solid #2D3A5C;
        border-radius: 14px;
        padding: 1.5rem 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out both;
    }
    .step-card:hover {
        border-color: #F59E0B;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(245,158,11,0.1);
    }
    .step-num {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F59E0B, #EF4444);
        color: #fff;
        font-weight: 800;
        font-size: 1rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.7rem;
    }
    .step-icon { font-size: 1.6rem; margin-bottom: 0.5rem; }
    .step-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #E5E7EB;
        margin-bottom: 0.3rem;
    }
    .step-desc {
        font-size: 0.82rem;
        color: #9CA3AF;
        line-height: 1.45;
    }

    /* ── Footer ─────────────────────────────────────────────────────────── */
    .footer {
        margin-top: 2.5rem;
        padding: 1.5rem;
        text-align: center;
        border-top: 1px solid #2D3A5C;
        animation: fadeInUp 0.6s ease-out;
    }
    .footer-brand {
        font-size: 0.95rem;
        font-weight: 700;
        color: #F59E0B;
        margin-bottom: 0.5rem;
    }
    .footer-models {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }
    .model-badge {
        background: #16213E;
        border: 1px solid #2D3A5C;
        border-radius: 20px;
        padding: 0.25rem 0.85rem;
        font-size: 0.78rem;
        color: #9CA3AF;
        font-weight: 500;
    }
    .footer-meta {
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 0.3rem;
    }

    /* ── Sidebar branding ──────────────────────────────────────────────── */
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
    .sidebar-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.35rem 0;
        border-bottom: 1px solid #2D3A5C22;
        font-size: 0.85rem;
    }
    .sidebar-stat-label { color: #9CA3AF; }
    .sidebar-stat-value { color: #F59E0B; font-weight: 700; }

    /* ── Hide Streamlit default page nav ───────────────────────────────── */
    [data-testid="stSidebarNav"] { display: none; }

    /* ── Reduce sidebar top padding ──────────────────────────────────── */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    /* ── Section dividers ──────────────────────────────────────────────── */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #E5E7EB;
        margin: 1.5rem 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-title-bar {
        height: 3px;
        width: 40px;
        background: linear-gradient(90deg, #F59E0B, #EF4444);
        border-radius: 2px;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-tagline { font-size: 1.05rem; }
        .hero-desc { font-size: 0.88rem; }
        .hero-container { padding: 1.5rem 0.5rem 1rem; }
        .kpi-card { padding: 1rem 0.8rem; }
        .kpi-value { font-size: 1.5rem; }
        .wf-step { min-width: 80px; padding: 0.6rem 0.4rem; }
        .wf-icon { width: 40px; height: 40px; font-size: 1.1rem; }
        .wf-label { font-size: 0.7rem; }
        .wf-sub { font-size: 0.6rem; max-width: 75px; }
        .wf-arrow { font-size: 0.9rem; }
        .nav-card { padding: 1.2rem; }
        .nav-card h3 { font-size: 1rem; }
        .nav-card p { font-size: 0.82rem; }
        .steps-grid { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.7rem; }
        .step-card { padding: 1rem 0.8rem; }
        .section-title { font-size: 1.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Breadcrumb ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="breadcrumb">'
    '<span class="active">Home</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Animated Hero Section ───────────────────────────────────────────────────
import base64
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"), "rb") as _f:
    _logo_b64 = base64.b64encode(_f.read()).decode()

st.markdown(
    f"""
    <div class="hero-container">
        <img src="data:image/png;base64,{_logo_b64}" alt="TRACE AI Logo"
             style="width:150px; margin-bottom:1rem; animation: fadeInUp 0.6s ease-out;">
        <div class="hero-title">TRACE AI</div>
        <div class="hero-acronym">Triage, Report, Action, Capture and Escalate</div>
        <div class="hero-tagline">Intelligent Diesel Diagnostics for Modern Fleet Maintenance</div>
        <div class="hero-desc">
            A multi-agent AI system that helps junior diesel field technicians
            diagnose fault codes safely and efficiently. It combines open-source
            LLMs with a human-in-the-loop approval workflow so that dangerous,
            costly, or uncertain repairs are always reviewed by a senior engineer
            before execution.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Live KPI Metrics ────────────────────────────────────────────────────────
_kpi = _get_kpi_stats()

st.markdown(
    '<div class="section-title"><div class="section-title-bar"></div> Live Performance</div>',
    unsafe_allow_html=True,
)

# MTTR Reduction, First Time Fix Rate, and Est. Savings are demo baseline values
st.markdown(
    f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap:1rem;">
        <div class="kpi-card" style="animation-delay:0.1s;">
            <div class="kpi-value">{_kpi["resolved"]}</div>
            <div class="kpi-label">Cases Resolved</div>
            <div class="kpi-delta">from database</div>
        </div>
        <div class="kpi-card" style="animation-delay:0.2s;">
            <div class="kpi-value">{_kpi["avg_confidence"]}%</div>
            <div class="kpi-label">Avg Confidence</div>
            <div class="kpi-delta">from decision log</div>
        </div>
        <div class="kpi-card" style="animation-delay:0.3s;">
            <div class="kpi-value">42%</div>
            <div class="kpi-label">MTTR Reduction</div>
            <div class="kpi-delta">vs. manual process</div>
        </div>
        <div class="kpi-card" style="animation-delay:0.4s;">
            <div class="kpi-value">78%</div>
            <div class="kpi-label">First Time Fix Rate</div>
            <div class="kpi-delta">+18% improvement</div>
        </div>
        <div class="kpi-card" style="animation-delay:0.5s;">
            <div class="kpi-value">$24k</div>
            <div class="kpi-label">Est. Savings</div>
            <div class="kpi-delta">this quarter</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Workflow Diagram ────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title"><div class="section-title-bar"></div> TRACE Workflow Pipeline</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow-section">
        <div class="workflow-container">
            <div class="wf-step">
                <div class="wf-icon wf-icon-1">👷</div>
                <div class="wf-label">Field Tech</div>
                <div class="wf-sub">Reports fault code & symptoms</div>
            </div>
            <div class="wf-arrow">▸</div>
            <div class="wf-step">
                <div class="wf-icon wf-icon-2">🧠</div>
                <div class="wf-label">Triage Agent</div>
                <div class="wf-sub">Ranks root causes by confidence</div>
            </div>
            <div class="wf-arrow">▸</div>
            <div class="wf-step">
                <div class="wf-icon wf-icon-3">🔍</div>
                <div class="wf-label">Evidence</div>
                <div class="wf-sub">Collects targeted follow ups</div>
            </div>
            <div class="wf-arrow">▸</div>
            <div class="wf-step">
                <div class="wf-icon wf-icon-4">⚡</div>
                <div class="wf-label">Escalation</div>
                <div class="wf-sub">Flags high cost or low confidence</div>
            </div>
            <div class="wf-arrow">▸</div>
            <div class="wf-step">
                <div class="wf-icon wf-icon-5">✅</div>
                <div class="wf-label">Human Approval</div>
                <div class="wf-sub">Manager reviews & decides</div>
            </div>
            <div class="wf-arrow">▸</div>
            <div class="wf-step">
                <div class="wf-icon wf-icon-6">🏁</div>
                <div class="wf-label">Resolution</div>
                <div class="wf-sub">Repair steps delivered</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Navigation Cards ────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title"><div class="section-title-bar"></div> Get Started</div>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        """
        <div class="nav-card" style="animation-delay:0.1s;">
            <h3>Technician Chatbot</h3>
            <p>Report fault codes, describe symptoms, and get AI powered
            diagnosis with step by step repair guidance in the field.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Technician_Chatbot.py", label="Open Chatbot  ➜")

with col_right:
    st.markdown(
        """
        <div class="nav-card" style="animation-delay:0.2s;">
            <h3>Approval Dashboard</h3>
            <p>Review escalated cases, approve or reject repair plans,
            and track decision history with a full audit trail.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/2_Approval_Dashboard.py", label="Open Dashboard  ➜"
    )

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── How It Works ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-title"><div class="section-title-bar"></div> How It Works</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="steps-grid">
        <div class="step-card" style="animation-delay:0.1s;">
            <div class="step-num">1</div>
            <div class="step-title">Report</div>
            <div class="step-desc">
                Technician enters the DTC fault code, vehicle ID, mileage,
                and describes the symptoms they observe.
            </div>
        </div>
        <div class="step-card" style="animation-delay:0.2s;">
            <div class="step-num">2</div>
            <div class="step-title">Triage</div>
            <div class="step-desc">
                The AI agent analyzes the fault code and ranks the top 3
                probable root causes with confidence scores.
            </div>
        </div>
        <div class="step-card" style="animation-delay:0.3s;">
            <div class="step-num">3</div>
            <div class="step-title">Evidence</div>
            <div class="step-desc">
                TRACE asks targeted follow up questions (fuel pressure, mileage,
                visible leaks) to refine the diagnosis.
            </div>
        </div>
        <div class="step-card" style="animation-delay:0.4s;">
            <div class="step-num">4</div>
            <div class="step-title">Escalation</div>
            <div class="step-desc">
                If confidence is low or repair cost is high, the case is
                escalated to a manager for human review.
            </div>
        </div>
        <div class="step-card" style="animation-delay:0.5s;">
            <div class="step-num">5</div>
            <div class="step-title">Resolution</div>
            <div class="step-desc">
                Approved repair steps are delivered to the technician.
                Every decision is logged for full compliance.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
        <div class="footer-brand">TRACE AI  ·  Triage, Report, Action, Capture and Escalate</div>
        <div class="footer-models">
            <span class="model-badge">Llama 3.1 (Triage)</span>
            <span class="model-badge">Mistral 7B (Fallback)</span>
            <span class="model-badge">Offline First</span>
            <span class="model-badge">Cloud Sync</span>
        </div>
        <div class="footer-meta">
            MIT License  ·  XTern Challenge Demo
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ─────────────────────────────────────────────────────────────────
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

    # Role selector (global)
    ROLE_NAMES = {
        "Fleet Manager": "Zion Adedipe",
        "Senior Technician": "Nhi Truong",
        "Junior Technician": "Lilian Campbell",
    }
    role = st.selectbox(
        "Your Role",
        list(ROLE_NAMES.keys()),
        index=list(ROLE_NAMES.keys()).index(
            st.session_state.get("global_role", "Fleet Manager")
        ),
        key="home_role_selector",
    )
    st.session_state["global_role"] = role
    st.session_state["dashboard_role"] = role

    user_name = ROLE_NAMES[role]
    st.markdown(
        f'<div style="background:#16213E; border:1px solid #2D3A5C; border-radius:10px; '
        f'padding:0.6rem 0.8rem; margin-top:0.3rem; margin-bottom:0.3rem;">'
        f'<div style="font-size:0.72rem; color:#9CA3AF; text-transform:uppercase; '
        f'letter-spacing:0.05em; font-weight:600;">Logged in as</div>'
        f'<div style="font-size:0.95rem; font-weight:700; color:#F59E0B; margin-top:0.15rem;">'
        f'{user_name}</div>'
        f'<div style="font-size:0.78rem; color:#9CA3AF;">{role}</div>'
        f'</div>',
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

    # Sync status
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    from backend.sync import check_connectivity
    is_online = check_connectivity()

    if is_online:
        st.markdown(
            '<div class="sync-indicator sync-online">'
            '<span class="sync-dot"></span> Online'
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

    st.divider()

    # Quick stats
    # Est. Savings is a demo baseline value
    st.markdown("**Quick Stats**")
    st.markdown(
        f"""
        <div style="padding:0.3rem 0;">
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Cases Today</span>
                <span class="sidebar-stat-value">{_kpi["cases_today"]}</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Pending Review</span>
                <span class="sidebar-stat-value">{_kpi["pending"]}</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Avg Confidence</span>
                <span class="sidebar-stat-value">{_kpi["avg_confidence"]}%</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Est. Savings</span>
                <span class="sidebar-stat-value">$4.2k</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
