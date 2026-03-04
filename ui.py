import streamlit as st

st.set_page_config(
    page_title="TRACE AI",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for dark industrial look ──────────────────────────────────────
st.markdown(
    """
    <style>
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #F59E0B, #EF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #9CA3AF;
        margin-top: 0;
    }
    .nav-card {
        background: #16213E;
        border: 1px solid #2D3A5C;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .nav-card:hover {
        border-color: #F59E0B;
    }
    .nav-card h3 {
        color: #F59E0B;
        margin-bottom: 0.5rem;
    }
    .nav-card p {
        color: #9CA3AF;
        font-size: 0.95rem;
    }
    .stat-box {
        background: #16213E;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid #F59E0B;
    }
    .stat-box h2 {
        color: #F59E0B;
        margin: 0;
    }
    .stat-box p {
        color: #9CA3AF;
        margin: 0;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">TRACE AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">'
    "Transparent Repair Automation with Compliance Engine &mdash; "
    "AI-powered diesel diagnostics for fleet maintenance"
    "</p>",
    unsafe_allow_html=True,
)

st.divider()

# ── Quick Stats (mock data) ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        '<div class="stat-box"><h2>12</h2><p>Cases Today</p></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        '<div class="stat-box"><h2>3</h2><p>Pending Approval</p></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        '<div class="stat-box"><h2>87%</h2><p>Avg Confidence</p></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        '<div class="stat-box"><h2>$4.2k</h2><p>Est. Savings</p></div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── Navigation Cards ─────────────────────────────────────────────────────────
st.subheader("Get Started")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        """
        <div class="nav-card">
            <h3>💬 Technician Chatbot</h3>
            <p>Report fault codes, describe symptoms, and get AI-powered
            diagnosis with step-by-step repair guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Technician_Chatbot.py", label="Open Chatbot →", icon="💬")

with col_right:
    st.markdown(
        """
        <div class="nav-card">
            <h3>📋 Approval Dashboard</h3>
            <p>Review escalated cases, approve or reject repair plans,
            and track decision history with full audit trail.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/2_Approval_Dashboard.py", label="Open Dashboard →", icon="📋"
    )

st.divider()

# ── How It Works ─────────────────────────────────────────────────────────────
st.subheader("How TRACE AI Works")

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown("**Step 1 — Triage**")
    st.caption(
        "Technician reports a fault code and symptoms. "
        "The AI ranks the top 3 probable root causes with confidence scores."
    )

with step2:
    st.markdown("**Step 2 — Evidence**")
    st.caption(
        "The system asks targeted follow-up questions "
        "(fuel pressure, mileage, visible leaks) to refine the diagnosis."
    )

with step3:
    st.markdown("**Step 3 — Escalation**")
    st.caption(
        "If confidence is low or cost is high, the case is escalated "
        "to a manager for approval before repair steps are issued."
    )

# ── Sidebar info ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/maintenance.png",
        width=64,
    )
    st.markdown("### TRACE AI")
    st.caption("v0.1.0 — Pilot Build")
    st.divider()
    st.markdown("**Quick Links**")
    st.page_link("ui.py", label="Home", icon="🏠")
    st.page_link("pages/1_Technician_Chatbot.py", label="Chatbot", icon="💬")
    st.page_link("pages/2_Approval_Dashboard.py", label="Dashboard", icon="📋")

    st.divider()
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    from backend.sync import check_connectivity
    is_online = check_connectivity()
    if is_online:
        st.success("ONLINE")
    else:
        st.warning("OFFLINE — Local mode")
    st.caption("Connectivity detected automatically.")
