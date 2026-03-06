# TRACE AI

**AI-Powered Field Service Diagnostics for Diesel Technicians**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Models](https://img.shields.io/badge/Models-Llama%203.1%20%2B%20Mistral%207B-blueviolet)
![Status](https://img.shields.io/badge/Status-Demo%20Ready-brightgreen)

**TRACE** (*Triage, Report, Action, Capture, and Escalate Engine*) is a multi-agent AI system that helps junior diesel field technicians diagnose fault codes safely and efficiently. It combines open-source LLMs with a human-in-the-loop approval workflow so that dangerous, costly, or uncertain repairs are always reviewed by a senior engineer before execution.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Demo Script](#demo-script)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Models and Licenses](#models-and-licenses)
- [Data Provenance](#data-provenance)
- [Deliverables Checklist](#deliverables-checklist)
- [Team](#team)
- [License](#license)

---

## Problem Statement

Junior field technicians working on heavy-duty diesel equipment face a steep learning curve. When a fault code appears, they must quickly diagnose the root cause, decide whether the repair is safe to attempt, and execute the fix - all while standing next to a truck in the field with limited connectivity.

**The core challenges:**

- **Long Mean Time to Repair (MTTR):**Inexperienced techs spend excessive time researching fault codes and repair procedures, leading to extended vehicle downtime.
- **Low First-Time Fix Rate (FTFR):**Without guided diagnosis, junior techs often misdiagnose issues, requiring repeat visits and increasing costs.
- **Tribal Knowledge Gap:**Senior engineers hold decades of diagnostic expertise in their heads. When they are unavailable, junior techs are left without guidance.
- **Safety Risk:**Attempting high-risk repairs (fuel system, electrical, structural) without proper oversight can lead to injury, equipment damage, or warranty violations.

TRACE addresses these challenges by putting an AI copilot in the hands of every field technician, backed by a structured escalation path that keeps senior engineers in the loop for critical decisions.

---

## Key Features

- **Multi-Agent Orchestration:**Three specialized agents (Triage, Evidence, Escalation) coordinated by a LangGraph state machine. Each agent handles a distinct phase of the diagnostic workflow.
- **Open-Source LLMs:**Llama 3.1 8B serves as the primary diagnosis model; Mistral 7B acts as an automatic fallback. Both run locally via Ollama with zero external API calls.
- **Human-in-the-Loop Approval:**The system automatically pauses and escalates to a senior engineer when confidence is below 70%, estimated cost exceeds $500, or a safety risk is detected.
- **Offline-First Design:**All inference and data storage run locally on the technician's device. When connectivity returns, completed sessions sync to the cloud automatically.
- **Full Audit Trail:**Every AI decision is logged with inputs, outputs, confidence scores, timestamps, and approver information. A dedicated Decision Audit page provides full traceability.
- **Field-Ready Interface:**Mobile-responsive Streamlit UI with a conversational chatbot for technicians, a back-office approval dashboard for engineers, and a decision audit viewer for compliance.
- **Live KPI Dashboard:**Homepage displays real-time metrics pulled from the local database, including resolved cases, average confidence, and pending reviews.

---

## Architecture

```
+-------------------+        +-------------------+        +---------------------------+
|                   |        |                   |        |   LangGraph Orchestrator  |
|   Field Tech      +------->+   Streamlit UI    +------->+                           |
|   (Mobile/Web)    |  HTTP  |   (Multi-Page)    |  API   |  +---------------------+  |
|                   |        |                   |        |  |   Triage Agent      |  |
+-------------------+        +---+----------+----+        |  |   (Llama 3.1 LLM)  |  |
                                 |          |             |  +---------------------+  |
                                 |          |             |                           |
                     +-----------+--+  +----+---------+   |  +---------------------+  |
                     | Technician   |  | Approval     |   |  |   Evidence Agent    |  |
                     | Chatbot      |  | Dashboard    |   |  |   (Rule-Based)      |  |
                     +--------------+  +------+-------+   |  +---------------------+  |
                                              |           |                           |
                                              |           |  +---------------------+  |
                                     +--------v--------+  |  |   Escalation Agent  |  |
                                     | Senior Engineer  |  |  |   (Rule-Based)      |  |
                                     | Approve / Reject |  |  +----------+----------+  |
                                     +-----------------+  |             |              |
                                                          +---------------------------+
                                                                        |
                                                     +------------------v-----------------+
                                                     |           Data Layer               |
                                                     |                                    |
                                                     |  SQLite (Local)  <-->  Cloud Sync  |
                                                     |  Decision Logs   |   (Reconnect)   |
                                                     +------------------------------------+
```

**Flow:** Tech enters a fault code and symptoms in the chatbot. The Triage Agent diagnoses the top 3 root causes using the LLM. The Evidence Agent asks structured follow-up questions and adjusts confidence scores. The Escalation Agent evaluates safety, cost, and confidence thresholds - auto-approving low-risk repairs or routing to the senior engineer's Approval Dashboard. Once approved, the tech receives step-by-step repair instructions. Every decision is logged to the audit trail.

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/flashyzee/TRACE-AI-.git
cd TRACE-AI-

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start Ollama and pull models (in a separate terminal)
ollama serve
ollama pull llama3.1            # ~4.7 GB, one-time download
ollama pull mistral             # ~4.1 GB, fallback model

# 5. Generate synthetic data (if not already present)
python Trace-app/data/generate_data.py

# 6. Launch the Streamlit UI
streamlit run ui.py

# 7. (Optional) Start the FastAPI backend
uvicorn backend.main:app --reload
```

### Verify

- Streamlit UI: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`
- Enter fault code **P0191** with symptom "low power under load" to run the demo scenario.

---

## Demo Script

When you run through the demo scenario (fault code P0191), the pipeline executes this flow:

1. **Evidence Questions:** The chatbot presents 4 structured follow-up questions for P0191.
2. **Triage Diagnosis:** The LLM diagnoses the top 3 root causes with confidence scores (~10-30 sec).
3. **Evidence Processing:** Confidence scores are adjusted based on the technician's physical observations.
4. **Escalation Check:** The system evaluates safety, cost, and confidence thresholds.
5. **Human Approval:** If escalated, the senior engineer reviews and approves or rejects the repair.
6. **Repair Instructions:** The technician receives step-by-step instructions for the approved repair.

You can also run the end-to-end pipeline directly:

```bash
cd trace-app
python demo.py
```

---

## Project Structure

```
TRACE-AI-/
├── ui.py                              # Streamlit main entry point
├── pages/
│   ├── 1_Technician_Chatbot.py        # Field tech conversational interface
│   ├── 2_Approval_Dashboard.py        # Senior engineer approval workflow
│   └── 3_Decision_Audit.py            # Decision log viewer (audit trail)
│
├── backend/
│   ├── main.py                        # FastAPI application
│   ├── db.py                          # Database operations and schema
│   ├── sync.py                        # Offline-to-cloud sync logic
│   ├── auth.py                        # API key authentication
│   ├── config.py                      # Configuration management
│   ├── schemas.py                     # Pydantic request/response models
│   ├── agents/                        # Agent implementations
│   │   ├── triage_agent.py            # LLM-powered diagnosis
│   │   ├── evidence_agent.py          # Follow-up questions + confidence adjustment
│   │   └── escalation_agent.py        # Approval logic + repair step generation
│   ├── orchestrator/
│   │   ├── state.py                   # TraceState schema (TypedDict)
│   │   └── workflow.py                # LangGraph pipeline + entry points
│   └── utils/
│       └── llm.py                     # Ollama connection with model fallback
│
├── Trace-app/
│   ├── demo.py                        # End-to-end demo script
│   ├── requirements.txt               # Python dependencies
│   ├── agents/                        # Reference agent implementations
│   ├── orchestrator/                  # Reference workflow
│   └── data/
│       ├── generate_data.py           # Synthetic data generator
│       ├── fault_codes.csv            # 50 Cummins diesel fault codes
│       ├── repair_history.csv         # 100 simulated repair records
│       └── example_logs.json          # 12 sample decision log entries
│
├── docs/
│   ├── model_license_statement.md     # Full model + framework license details
│   ├── prompt_examples.md             # Prompt engineering before/after examples
│   ├── Business Sketch.pdf            # Business model overview
│   ├── commercialization_plan.pdf     # Go-to-market strategy
│   ├── pricing_economics.pdf          # Pricing and unit economics
│   ├── integration_sla_legal.pdf      # Integration, SLA, and legal analysis
│   └── pilot_plan.pdf                 # Pilot deployment plan
│
├── data/                              # Runtime databases and logs
├── DATA_PROVENANCE.md                 # Data sourcing and compliance
├── LICENSE                            # MIT License
└── README.md
```

---

## Tech Stack

| Component | Technology | License |
|-----------|-----------|---------|
| AI Orchestration | LangGraph (state machine + SQLite checkpointing) | MIT |
| Primary LLM | Llama 3.1 8B via Ollama | Meta Llama 3.1 Community License |
| Fallback LLM | Mistral 7B via Ollama | Apache 2.0 |
| LLM Integration | LangChain (prompts, Ollama wrapper) | MIT |
| Backend API | FastAPI + Uvicorn | MIT |
| Frontend | Streamlit (multi-page app) | Apache 2.0 |
| Local Database | SQLite | Public Domain |
| Cloud Sync (Simulated) | SQLite (local cloud.db) | Public Domain |
| State Validation | Pydantic | MIT |

---

## Models and Licenses

| Model | License | Usage | Commercial Use |
|-------|---------|-------|----------------|
| Llama 3.1 8B | Meta Llama 3.1 Community License | Primary diagnosis model | Allowed (< 700M MAU) |
| Mistral 7B | Apache 2.0 | Automatic fallback model | Fully permitted |

All models run locally via Ollama. No data is sent to external APIs. No fine-tuning has been performed; all models are used as-is from their official releases.

For full license details, see [docs/model_license_statement.md](docs/model_license_statement.md).

---

## Data Provenance

All data used in this project is **100% synthetic**. No real customer data, proprietary systems, or personally identifiable information (PII) was used at any stage. Fault codes are based on publicly available SAE J1939 / OBD-II standards.

For full details on data sourcing and compliance, see [DATA_PROVENANCE.md](DATA_PROVENANCE.md).

---

## Deliverables Checklist

| Deliverable | Status |
|-------------|--------|
| Working prototype with live demo | Done |
| Multi-agent AI pipeline (Triage + Evidence + Escalation) | Done |
| Human-in-the-loop approval workflow | Done |
| Offline-first with cloud sync | Done |
| Full audit trail and decision logging | Done |
| Open-source LLMs only (no paid APIs) | Done |
| Synthetic data with provenance documentation | Done |
| Model license statement | Done |
| Prompt engineering examples | Done |
| Business sketch | Done |
| Commercialization plan | Done |
| Pricing and unit economics | Done |
| Integration, SLA, and legal analysis | Done |
| Pilot deployment plan | Done |

---

## Team

| Name | Role |
|------|------|
| Nhi Truong | Technical Lead - architecture, backend, AI pipeline, and UI development |
| Zion Adedipe | Technical Lead - infrastructure, integration, and system reliability |
| Campbell Lilian | Strategy and Research - ideation, business analysis, and report preparation |

---

## License

MIT License - see [LICENSE](LICENSE) for details.
