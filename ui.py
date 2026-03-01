import streamlit as st
from agents.triage_agent import run_triage
from agents.evidence_agent import collect_evidence
from agents.escalation_agent import escalate_incident
from db import init_db
from sqlmodel import Session
from models import Incident, Evidence, Escalation

# Initialize database (optional, ensures tables exist)
init_db()

st.set_page_config(page_title="TRACE AI Dashboard", layout="wide")
st.title("TRACE AI Dashboard")

st.markdown(
    """
    Enter a new incident description below and TRACE AI will:
    - Triage the incident  
    - Collect evidence  
    - Escalate if needed
    """
)

# Incident input form
with st.form("incident_form"):
    description = st.text_area("Incident Description")
    submit_btn = st.form_submit_button("Submit Incident")

if submit_btn and description.strip():
    st.subheader("Processing Incident...")
    
    # Run agents
    triage_result = run_triage({"description": description})
    evidence_result = collect_evidence({"description": description})
    escalation_result = escalate_incident({"description": description})
    
    # Display results
    st.subheader("Results")
    st.write(f"**Triage:** {triage_result}")
    st.write(f"**Evidence:** {evidence_result}")
    st.write(f"**Escalation:** {escalation_result}")

    # Save to database (optional)
    with Session(init_db()) as session:
        incident = Incident(type="generic", severity=triage_result, status="triaged")
        session.add(incident)
        session.commit()
        st.success("Incident saved to database!")

# Display past incidents from DB
st.markdown("---")
st.subheader("Incident History")
with Session(init_db()) as session:
    incidents = session.query(Incident).all()
    if incidents:
        for inc in incidents:
            st.write(f"ID: {inc.id} | Type: {inc.type} | Severity: {inc.severity} | Status: {inc.status}")
    else:
        st.write("No incidents recorded yet.")
