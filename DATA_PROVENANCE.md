# Data Provenance: TRACE AI

All data used in this project is **100% synthetic**. No real customer data, proprietary systems, or personally identifiable information (PII) was used at any stage.

## Datasets

### fault_codes.csv (50 records)
- **Source:** Generated programmatically using publicly available SAE J1939 / OBD-II fault code definitions.
- **Contents:** Fault code, name, system, severity, and common causes for Cummins diesel engines.
- **PII:** None. Codes are industry-standard identifiers with no link to any real vehicle or person.

### repair_history.csv (100 records)
- **Source:** Procedurally generated using Python's `random` library (`data/generate_data.py`).
- **Contents:** Simulated repair sessions with randomized technician IDs, fault codes, symptoms, outcomes, confidence scores, and timestamps.
- **PII:** None. Technician IDs (e.g., `TechA_001`) and engineer names (e.g., `Eng_Johnson`) are fictional placeholders.

### example_logs.json (5 records)
- **Source:** Hand-written sample entries representing a single P0191 diagnostic session.
- **Contents:** Decision log entries showing the full agent pipeline (triage, evidence, escalation, approval, resolution).
- **PII:** None. All session IDs, agent IDs, and approver names are fictional.

## AI Models

| Model | License | Source |
|-------|---------|--------|
| Llama 3.1 8B | Meta Llama 3 Community License | ollama.com, free for research and commercial use (under 700M monthly active users) |
| Mistral 7B | Apache 2.0 | ollama.com, fully open(-) source, commercial use allowed |

No proprietary or closed(-) source AI models are used. All inference runs locally via Ollama, and no data is sent to external APIs.

## Compliance Notes

- No real Cummins systems, diagnostic tools, or customer data were accessed.
- All fault code descriptions are derived from publicly available OBD-II / SAE J1939 standards.
- The project complies with the competition requirement to use only synthetic or publicly available data.
