# agents/triage_agent.py
"""
Triage Agent — takes fault code + symptoms, returns top 3 causes ranked by confidence.
LangGraph node function: reads from and writes to TraceState.
"""

import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from orchestrator.state import TraceState
from utils.llm import get_llm

TRIAGE_PROMPT = """You are a certified Cummins diesel engine diagnostic expert with 20 years of field experience.

A junior technician has reported the following:
- Fault Code: {fault_code}
- Symptoms: {symptoms}

Your job is to analyze this and identify the top 3 most likely root causes.

Respond ONLY in this exact JSON format, no extra text:
{{
  "causes": [
    {{
      "rank": 1,
      "cause": "name of cause",
      "confidence": 0.72,
      "explanation": "one sentence explaining why this is likely given the symptoms",
      "urgency": "high/medium/low",
      "estimated_cost_usd": 850
    }},
    {{
      "rank": 2,
      "cause": "name of cause",
      "confidence": 0.18,
      "explanation": "one sentence explanation",
      "urgency": "medium",
      "estimated_cost_usd": 120
    }},
    {{
      "rank": 3,
      "cause": "name of cause",
      "confidence": 0.10,
      "explanation": "one sentence explanation",
      "urgency": "low",
      "estimated_cost_usd": 45
    }}
  ]
}}

Rules:
- Confidences must sum to 1.0
- Order by confidence descending
- Be specific to the fault code and symptoms provided
- For P0191 specifically, consider: fuel rail pressure sensor failure, weak lift pump, clogged fuel filter, injector return leak, wiring/connector issue"""


def triage_agent(state: TraceState) -> TraceState:
    """
    LangGraph node: runs triage diagnosis.
    Input: state with fault_code + initial_symptoms
    Output: state updated with triage_results, top_cause, top_confidence
    """
    llm, model_used = get_llm()
    state["model_used"] = model_used

    prompt = PromptTemplate(
        input_variables=["fault_code", "symptoms"],
        template=TRIAGE_PROMPT,
    )

    chain = prompt | llm | StrOutputParser()

    try:
        raw_response = chain.invoke({
            "fault_code": state["fault_code"],
            "symptoms": state["initial_symptoms"],
        })

        # Strip markdown code fences if the LLM wraps its response
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]  # drop first ```json line
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
        causes = result["causes"]

        state["triage_results"] = causes
        state["top_cause"] = causes[0]["cause"]
        state["top_confidence"] = causes[0]["confidence"]
        state["workflow_status"] = "triaged"

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # Fallback: parsing failure → set low confidence to force escalation
        state["triage_results"] = []
        state["top_cause"] = "Unable to parse diagnosis"
        state["top_confidence"] = 0.0
        state["error"] = f"Triage parsing error: {str(e)}"
        state["workflow_status"] = "triaged"

    return state
