# TRACE AI-Assisted Field Service Workflow

**TRACE** (*Triage, Report, Action, Capture, and Escalate Engine*) is an AI-powered field service app that helps junior diesel technicians diagnose fault codes safely and efficiently. When a tech scans a fault code (e.g., P0191) off a Cummins truck, TRACE guides them through diagnosis using 3 AI agents and automatically escalates dangerous or uncertain repairs to a senior engineer for human approval.

**Demo scenario:** Junior tech enters fault code P0191 (fuel rail pressure issue) + symptoms → AI diagnoses top 3 causes → asks follow-up questions → flags for approval if risky → senior engineer approves → tech gets step-by-step repair instructions → everything is logged.

---

## Features

- **Triage Agent** — Diagnoses the top 3 most likely root causes ranked by confidence using Llama 3.1.
- **Evidence Collection Agent** — Asks structured follow-up questions and adjusts confidence based on physical observations.
- **Escalation Agent** — Automatically pauses the workflow if confidence < 70%, cost > $500, or a safety risk is detected. Requires human approval before proceeding.
- **Human-in-the-Loop** — Senior engineers approve or reject repairs from a back-office dashboard.
- **Full Audit Trail** — Every AI decision is logged with inputs, outputs, confidence scores, timestamps, and approver info.
- **Offline-Ready** — Runs entirely on local LLMs via Ollama. No internet required for diagnosis.
- **Model Fallback** — Automatically switches from Llama 3.1 to Mistral 7B if the primary model is unavailable.

---

## Architecture

```
Field Tech (mobile)  →  FastAPI Server  →  LangGraph Orchestrator
                                              ├── Triage Agent (LLM)
                                              ├── Evidence Agent (rule-based)
                                              └── Escalation Agent (rule-based)
                                                    ├── Auto-approve → Repair Steps
                                                    └── Escalate → Back-Office Dashboard
                                                                      ↓
                                                              Senior Engineer
                                                              Approve / Reject
                                                                      ↓
                                                              Repair Steps → Tech

Storage: SQLite (local, checkpointed) → Supabase (cloud sync when online)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Orchestration | LangGraph (state machine + SQLite checkpointing) |
| LLM Backend | Ollama (local) — Llama 3.1 (primary), Mistral 7B (fallback) |
| LLM Integration | LangChain (prompts, Ollama wrapper) |
| Backend API | FastAPI + Uvicorn |
| Chatbot NLP | Rasa |
| Database | SQLite (local) + Supabase (cloud sync) |
| Frontend | React 18 |
| State Validation | Pydantic |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed

---

## Setup — Run in 10 Commands

```bash
# 1. Clone the repo
git clone https://github.com/flashyzee/TRACE-AI-.git
cd TRACE-AI-

# 2. Set up Python environment
cd trace-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start Ollama and pull models (in a separate terminal)
ollama serve
ollama pull llama3.1            # ~4.7GB, one-time download
ollama pull mistral             # ~4.1GB, fallback model

# 5. Generate synthetic data (if not already present)
python data/generate_data.py

# 6. Run the end-to-end demo
python demo.py
```

---

## Demo Script — What to Expect

When you run `python demo.py`, the pipeline executes this flow:

1. **Shows evidence questions** — 4 structured follow-up questions for P0191
2. **Runs triage** — LLM diagnoses top 3 causes with confidence scores (~10-30 sec)
3. **Processes evidence** — Adjusts confidence based on tech's answers
4. **Checks escalation** — Evaluates safety, cost, confidence thresholds
5. **Simulates approval** — Senior engineer approves the repair
6. **Delivers repair steps** — Step-by-step instructions for the tech

---

## Project Structure

```
trace-app/
├── agents/
│   ├── triage_agent.py          # AI diagnosis (LLM-powered)
│   ├── evidence_agent.py        # Follow-up questions + confidence adjustment
│   └── escalation_agent.py      # Approval logic + repair step generation
├── orchestrator/
│   ├── state.py                 # Shared state schema (TraceState TypedDict)
│   └── workflow.py              # LangGraph pipeline + step-by-step entry points
├── utils/
│   └── llm.py                   # Ollama connection with model fallback
├── data/
│   ├── generate_data.py         # Synthetic data generator
│   ├── fault_codes.csv          # 50 Cummins diesel fault codes
│   ├── repair_history.csv       # 100 simulated repair records
│   └── example_logs.json        # 5 sample decision log entries
├── docs/
│   └── prompt_examples.md       # 5 prompt engineering before/after examples
├── demo.py                      # End-to-end demo script
└── requirements.txt             # Python dependencies
```

---

## API Entry Points (for FastAPI integration)

```python
from orchestrator.workflow import (
    run_triage_only,              # Step 1: LLM diagnosis only
    run_evidence_and_escalation,  # Step 2: process evidence + check escalation
    resume_after_approval,        # Step 3: after human approves/rejects
    run_workflow,                 # Alternative: run entire pipeline in one call
)
from agents.evidence_agent import get_evidence_questions  # Get question list for chatbot
```

---

## Data

All data is **100% synthetic**. See [DATA_PROVENANCE.md](DATA_PROVENANCE.md) for full details.

- `fault_codes.csv` — 50 Cummins diesel fault codes from public OBD-II / SAE J1939 standards
- `repair_history.csv` — 100 procedurally generated repair records
- `example_logs.json` — 5 hand-written decision log entries for audit trail demonstration

---

## AI Models Used

| Model | License | Usage |
|-------|---------|-------|
| Llama 3.1 8B | Meta Llama 3 Community License | Primary diagnosis model |
| Mistral 7B | Apache 2.0 | Fallback when Llama 3.1 unavailable |

All models run locally via Ollama. No data is sent to external APIs.

---

## License

MIT License — see [LICENSE](LICENSE)
