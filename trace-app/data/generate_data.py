# data/generate_data.py
"""
Generates synthetic data for the TRACE demo:
  - fault_codes.csv (50 Cummins fault codes)
  - repair_history.csv (100 repair records)
  - example_logs.json (5 decision log entries for the rubric)

Run once:  python data/generate_data.py
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

# Ensure output directory exists
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Fault codes (50 rows) ────────────────────────────────────────────────

FAULT_CODES = [
    {"code": "P0191", "name": "Fuel Rail Pressure Sensor Circuit Range/Performance",
     "system": "Fuel", "severity": "High",
     "common_causes": "Sensor failure, weak pump, clogged filter"},
    {"code": "P0087", "name": "Fuel Rail/System Pressure Too Low",
     "system": "Fuel", "severity": "High",
     "common_causes": "Fuel pump, pressure regulator, filter"},
    {"code": "P0093", "name": "Fuel System Large Leak Detected",
     "system": "Fuel", "severity": "Critical",
     "common_causes": "Fuel line, injector o-ring, rail"},
    {"code": "P0234", "name": "Turbocharger Overboost Condition",
     "system": "Turbo", "severity": "High",
     "common_causes": "Wastegate, boost pressure sensor, ECM"},
    {"code": "P0541", "name": "Intake Air Heater Relay Circuit Low",
     "system": "Electrical", "severity": "Medium",
     "common_causes": "Relay, wiring, grid heater"},
    {"code": "P0401", "name": "EGR Insufficient Flow",
     "system": "Emissions", "severity": "Medium",
     "common_causes": "EGR valve, passages, sensor"},
    {"code": "P0402", "name": "EGR Excessive Flow",
     "system": "Emissions", "severity": "Medium",
     "common_causes": "EGR valve stuck open"},
    {"code": "P0299", "name": "Turbocharger Underboost",
     "system": "Turbo", "severity": "High",
     "common_causes": "Boost leak, turbo wear, VGT actuator"},
    {"code": "P0380", "name": "Glow Plug Circuit Malfunction",
     "system": "Electrical", "severity": "Medium",
     "common_causes": "Glow plug, relay, wiring"},
    {"code": "P2BAC", "name": "NOx Limit Exceeded - EGR Deactivated",
     "system": "Emissions", "severity": "High",
     "common_causes": "Secondary to P0191"},
]

EXTRA_CODES = [
    ("P0100", "Mass Air Flow Sensor Circuit", "Air", "Medium", "MAF sensor, wiring, air filter"),
    ("P0101", "Mass Air Flow Out of Range", "Air", "Medium", "MAF sensor, air leak"),
    ("P0180", "Fuel Temperature Sensor Circuit", "Fuel", "Low", "Sensor, wiring"),
    ("P0183", "Fuel Temperature Sensor High", "Fuel", "Low", "Sensor stuck high"),
    ("P0200", "Injector Circuit Open", "Fuel", "High", "Injector, wiring harness"),
    ("P0201", "Injector 1 Circuit", "Fuel", "High", "Injector 1 coil, wiring"),
    ("P0202", "Injector 2 Circuit", "Fuel", "High", "Injector 2 coil, wiring"),
    ("P0203", "Injector 3 Circuit", "Fuel", "High", "Injector 3 coil, wiring"),
    ("P0204", "Injector 4 Circuit", "Fuel", "High", "Injector 4 coil, wiring"),
    ("P0205", "Injector 5 Circuit", "Fuel", "High", "Injector 5 coil, wiring"),
    ("P0206", "Injector 6 Circuit", "Fuel", "High", "Injector 6 coil, wiring"),
    ("P0335", "Crankshaft Position Sensor", "Engine", "High", "CKP sensor, tone ring, wiring"),
    ("P0340", "Camshaft Position Sensor", "Engine", "High", "CMP sensor, timing, wiring"),
    ("P0500", "Vehicle Speed Sensor", "Drivetrain", "Medium", "VSS, wiring, TCM"),
    ("P0600", "Serial Communication Link", "Electrical", "High", "CAN bus, ECM, wiring"),
    ("P0700", "Transmission Control System", "Transmission", "High", "TCM, solenoids"),
    ("P1093", "Fuel Rail Pressure Low During Power Enrichment", "Fuel", "High", "Pump, filter, injectors"),
    ("P1094", "Fuel Rail Pressure High During Power Enrichment", "Fuel", "Medium", "Pressure regulator, sensor"),
    ("P1261", "High Pressure Injector Control, Cylinder 1", "Fuel", "High", "HPOP, injector 1"),
    ("P0420", "Catalyst Efficiency Below Threshold", "Emissions", "Medium", "DPF, SCR, DEF system"),
    ("P0471", "Exhaust Pressure Sensor Range", "Exhaust", "Medium", "Sensor, DPF clog"),
    ("P0472", "Exhaust Pressure Sensor Low", "Exhaust", "Medium", "Sensor, wiring"),
    ("P0473", "Exhaust Pressure Sensor High", "Exhaust", "Medium", "Blocked DPF, sensor"),
    ("P0478", "Exhaust Pressure Control High", "Exhaust", "High", "EBV stuck, actuator"),
    ("P2002", "DPF Efficiency Below Threshold", "Emissions", "High", "DPF clog, regen failure"),
    ("P203F", "Reductant Quality Sensor", "Emissions", "Medium", "DEF quality, sensor"),
    ("P2047", "Reductant Injector Circuit Low", "Emissions", "High", "DEF injector, wiring"),
    ("P2048", "Reductant Injector Circuit High", "Emissions", "High", "DEF injector, short"),
    ("P2269", "Water In Fuel Sensor", "Fuel", "Medium", "Water separator, sensor"),
    ("P0560", "System Voltage Malfunction", "Electrical", "Medium", "Alternator, battery, wiring"),
    ("P0562", "System Voltage Low", "Electrical", "High", "Alternator, battery failing"),
    ("P0563", "System Voltage High", "Electrical", "Medium", "Voltage regulator, alternator"),
    ("P0480", "Cooling Fan Relay Circuit", "Cooling", "Medium", "Fan relay, wiring, ECM"),
    ("P0481", "Cooling Fan Relay 2 Circuit", "Cooling", "Medium", "Fan relay 2"),
    ("P0482", "Cooling Fan Relay 3 Circuit", "Cooling", "Medium", "Fan relay 3"),
    ("P0116", "Engine Coolant Temp Sensor Range", "Cooling", "Medium", "ECT sensor, thermostat"),
    ("P0117", "Engine Coolant Temp Sensor Low", "Cooling", "Low", "ECT sensor, wiring short"),
    ("P0118", "Engine Coolant Temp Sensor High", "Cooling", "High", "ECT sensor, open circuit"),
    ("P0125", "Insufficient Coolant Temp For Closed Loop", "Cooling", "Low", "Thermostat stuck open"),
    ("P0128", "Coolant Temp Below Thermostat Regulating Temp", "Cooling", "Low", "Thermostat"),
]

all_codes = FAULT_CODES.copy()
for code, name, system, severity, causes in EXTRA_CODES:
    all_codes.append({
        "code": code, "name": name, "system": system,
        "severity": severity, "common_causes": causes,
    })

fault_codes_path = os.path.join(DATA_DIR, "fault_codes.csv")
with open(fault_codes_path, "w", newline="") as f:
    writer = csv.DictWriter(
        f, fieldnames=["code", "name", "system", "severity", "common_causes"]
    )
    writer.writeheader()
    writer.writerows(all_codes)
print(f"Generated {len(all_codes)} fault codes -> {fault_codes_path}")


# ── Repair history (100 rows) ────────────────────────────────────────────

TECHS = ["TechA_001", "TechB_002", "TechC_003", "TechD_004", "TechE_005"]
ENGINEERS = ["Eng_Johnson", "Eng_Martinez", "Eng_Williams", "Eng_Chen"]
OUTCOMES = ["resolved", "resolved", "resolved", "escalated_resolved", "parts_ordered"]
CAUSES = {
    "P0191": [
        "Fuel rail pressure sensor failure", "Weak lift pump",
        "Clogged fuel filter", "Injector return leak",
        "Wiring connector corrosion",
    ],
    "P0087": ["Fuel pump failure", "Blocked fuel filter", "Fuel pressure regulator"],
    "P0234": ["Wastegate actuator failure", "Boost pressure sensor", "Boost hose leak"],
}

random.seed(42)  # reproducible demo data
repairs = []
base_date = datetime(2024, 1, 1)

for i in range(100):
    fault = random.choice(list(CAUSES.keys()))
    cause = random.choice(CAUSES[fault])
    confidence = round(random.uniform(0.55, 0.97), 2)
    escalated = confidence < 0.70 or random.random() < 0.25
    approved = True if escalated and random.random() < 0.90 else None

    repair = {
        "repair_id": f"REP-{1000 + i}",
        "timestamp": (
            base_date + timedelta(days=i * 3, hours=random.randint(7, 17))
        ).isoformat(),
        "tech_id": random.choice(TECHS),
        "fault_code": fault,
        "symptoms": random.choice([
            "rough idle and black smoke", "hard start and low power",
            "check engine light, idling rough", "engine hesitation under load",
            "stalling at low RPM", "excessive fuel consumption",
        ]),
        "ai_diagnosis": cause,
        "confidence": confidence,
        "evidence_collected": "yes",
        "escalated": escalated,
        "approved_by": random.choice(ENGINEERS) if escalated and approved else "",
        "outcome": random.choice(OUTCOMES),
        "resolution_time_hours": round(random.uniform(0.5, 6.0), 1),
        "model_used": random.choice(["llama3.1", "llama3.1", "mistral"]),
    }
    repairs.append(repair)

history_path = os.path.join(DATA_DIR, "repair_history.csv")
with open(history_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(repairs[0].keys()))
    writer.writeheader()
    writer.writerows(repairs)
print(f"Generated {len(repairs)} repair history records -> {history_path}")


# ── Example decision logs (5 rows, for rubric) ───────────────────────────

example_logs = [
    {
        "log_id": "LOG-001",
        "timestamp": "2024-03-15T09:23:41Z",
        "session_id": "SESSION-REP-1000",
        "agent_id": "triage_agent",
        "fault_code": "P0191",
        "inputs": {
            "fault_code": "P0191",
            "symptoms": "rough idle, black smoke, hard cold start",
        },
        "output": {
            "top_cause": "Weak lift pump",
            "confidence": 0.72,
            "model": "llama3.1",
        },
        "confidence": 0.72,
        "human_approved": False,
        "model_used": "llama3.1",
        "notes": "Initial triage -- sent to evidence collection",
    },
    {
        "log_id": "LOG-002",
        "timestamp": "2024-03-15T09:24:18Z",
        "session_id": "SESSION-REP-1000",
        "agent_id": "evidence_agent",
        "fault_code": "P0191",
        "inputs": {
            "fuel_pressure_psi": "Under 500 PSI",
            "miles_since_filter": "Over 15,000 mi",
            "visible_leak": "No leak visible",
            "cold_start_issue": "Yes, hard cold start",
        },
        "output": {"updated_confidence": 0.87, "evidence_complete": True},
        "confidence": 0.87,
        "human_approved": False,
        "model_used": "llama3.1",
        "notes": "Evidence confirmed pump weakness -- confidence raised to 87%",
    },
    {
        "log_id": "LOG-003",
        "timestamp": "2024-03-15T09:24:52Z",
        "session_id": "SESSION-REP-1000",
        "agent_id": "escalation_agent",
        "fault_code": "P0191",
        "inputs": {
            "confidence": 0.87,
            "estimated_cost_usd": 850,
            "urgency": "high",
        },
        "output": {
            "requires_human_approval": True,
            "reason": "Estimated repair cost $850 exceeds $500 threshold",
        },
        "confidence": 0.87,
        "human_approved": None,
        "model_used": "llama3.1",
        "notes": "Escalated to back-office -- cost threshold exceeded",
    },
    {
        "log_id": "LOG-004",
        "timestamp": "2024-03-15T09:31:05Z",
        "session_id": "SESSION-REP-1000",
        "agent_id": "human_approval",
        "fault_code": "P0191",
        "inputs": {"repair_id": "REP-1000", "action": "approve"},
        "output": {"approved": True, "approved_by": "Eng_Johnson"},
        "confidence": 0.87,
        "human_approved": True,
        "model_used": "N/A",
        "notes": "Senior engineer Eng_Johnson approved repair at 09:31 AM",
    },
    {
        "log_id": "LOG-005",
        "timestamp": "2024-03-15T09:31:08Z",
        "session_id": "SESSION-REP-1000",
        "agent_id": "resolution_agent",
        "fault_code": "P0191",
        "inputs": {"cause": "Weak lift pump", "approved": True},
        "output": {"repair_steps_generated": True, "steps_count": 10},
        "confidence": 0.87,
        "human_approved": True,
        "model_used": "llama3.1",
        "notes": "Repair steps delivered to tech. Total resolution time: 7 min 27 sec",
    },
]

logs_path = os.path.join(DATA_DIR, "example_logs.json")
with open(logs_path, "w") as f:
    json.dump(example_logs, f, indent=2)
print(f"Generated 5 example decision log entries -> {logs_path}")
