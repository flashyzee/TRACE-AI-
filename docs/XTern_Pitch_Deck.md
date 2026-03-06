# TRACE AI - XTern Challenge Pitch Deck
## Complete Slide Content (10-Minute Presentation)

---

## SLIDE 1: Title Slide
**Title:** TRACE AI
**Subtitle:** Transparent Repair Automation with Compliance Engine

**Visual suggestion:** Clean, bold product logo centered. Team photos or avatars in a row at the bottom. Cummins-inspired color palette (dark charcoal, red accent, white).

**Bullet points:**
- XTern Challenge: Service Engineering Reboot
- Nhi Truong - Technical Lead (Architecture, AI Pipeline, UI)
- Zion Adedipe - Technical Lead (Infrastructure, Integration, Reliability)
- Campbell Lilian - Strategy & Research (Business Analysis, Ideation)

**Speaker notes:**
"Good morning. We're Team TRACE, and we built an AI-powered diagnostic assistant for the technicians who keep diesel fleets running. TRACE stands for Transparent Repair Automation with Compliance Engine. Over the next ten minutes, we'll show you why this matters, how it works, and a live demo. Let's start with the problem."

---

## SLIDE 2: The Problem
**Title:** The Knowledge Gap Is Costing Fleets Millions

**Visual suggestion:** Split image - left side shows an overwhelmed junior tech staring at a diagnostic scanner in an engine bay, right side shows a stack of paper service manuals. Key stats in large bold callout boxes.

**Bullet points:**
- Mean Time to Repair (MTTR) in heavy-duty diesel: 4-8 hours per incident
- First-Time Fix Rate (FTFR) industry average: ~60% - 4 in 10 repairs need a return visit
- 40% of experienced diesel techs are retiring within 10 years (TechForce Foundation)
- Junior techs rely on tribal knowledge that walks out the door with senior staff
- A misdiagnosis on a safety-critical system (brakes, fuel, exhaust) can endanger lives

**Speaker notes:**
"Here's the reality on the ground. When a diesel truck throws a fault code in the field, a junior technician has to figure out what's wrong - often alone, often in a remote location with no cell signal, and often without the years of experience needed to diagnose it correctly. Industry data tells us the average repair takes four to eight hours. Only about sixty percent of repairs are fixed on the first visit. That means four out of ten times, the truck gets repaired wrong, has to come back, and the fleet loses another day of revenue. And it's getting worse - forty percent of experienced diesel techs are approaching retirement. The tribal knowledge they carry doesn't transfer to a manual. It walks out the door with them. On safety-critical systems like fuel delivery, brakes, or exhaust aftertreatment, a wrong diagnosis isn't just expensive - it's dangerous."

---

## SLIDE 3: User Story
**Title:** A Day in the Life: Fault Code P0191

**Visual suggestion:** Two-column comparison. Left column header: "WITHOUT TRACE" (red/warning tones). Right column header: "WITH TRACE" (green/success tones). Timeline format showing the same technician's day side-by-side.

**Bullet points (WITHOUT TRACE):**
- Junior tech Jake sees P0191 (Fuel Rail Pressure Too Low) on a Cummins ISB 6.7L
- Googles the code on his phone, gets 15 forum posts with conflicting advice
- Guesses it's the fuel filter, replaces it - truck still won't start right
- Calls senior tech (who's on another job 2 hours away), waits 90 minutes for a callback
- Total: 7 hours, wrong part ordered, truck still down the next day

**Bullet points (WITH TRACE):**
- Jake opens TRACE, enters P0191 + symptoms in 30 seconds
- AI returns top 3 ranked causes: weak lift pump (72%), clogged filter (18%), injector leak (10%)
- Evidence questions narrow it to lift pump at 87% confidence
- Case auto-escalates (cost > $500) to senior engineer Sarah, who approves in 2 minutes
- Jake gets 10-step repair instructions. Truck rolls by lunch. Total: 3.5 hours

**Speaker notes:**
"Let me make this concrete. Meet Jake, a junior diesel tech with eight months of experience. He's at a customer site and a Cummins ISB 6.7 throws P0191 - Fuel Rail Pressure Too Low. Without TRACE, Jake searches his phone, gets conflicting advice, takes a guess, replaces the fuel filter. The truck still won't start right. He calls his senior tech who's two hours away on another job. By the end of the day, he's spent seven hours, ordered the wrong part, and the truck is still down. With TRACE, Jake enters the fault code and symptoms. In seconds, the AI ranks weak lift pump as the most likely cause at 72% confidence. TRACE asks targeted follow-up questions - fuel pressure reading, miles since filter change, any visible leaks, cold start issues. Based on Jake's answers, confidence adjusts to 87%. Because the estimated repair cost is $850 - above our $500 threshold - the case automatically escalates to senior engineer Sarah. She reviews the diagnosis on her dashboard, approves it in two minutes, and Jake receives step-by-step repair instructions tailored to his experience level. The truck is rolling by lunch."

---

## SLIDE 4: Our Solution
**Title:** TRACE AI: Diagnosis You Can Trust

**Visual suggestion:** A single clean sentence at the top in large font. Below it, three icon cards side by side: a speedometer (faster), a shield (safer), a clipboard with checkmark (traceable).

**Bullet points:**
- A multi-agent AI system that guides junior diesel technicians through fault diagnosis
- Three promises:
  - **Faster** - AI-ranked root causes in seconds, not hours of guesswork
  - **Safer** - Human-in-the-loop approval before any safety-critical repair
  - **Traceable** - Every decision logged for compliance, warranty, and legal defensibility
- Built entirely on open-source models. Runs fully offline. Zero external API calls.

**Speaker notes:**
"TRACE AI is a multi-agent system that guides junior technicians from fault code to fix - faster, safer, and with a full paper trail. Faster, because ranked diagnoses replace hours of guessing. Safer, because a senior engineer approves every high-risk repair before the tech touches the truck. And traceable, because every AI recommendation, every confidence score, every human approval is logged and exportable. And here's what makes it practical for the field: it runs entirely on open-source models, entirely offline, with zero external API calls. No cloud dependency. No data leaving the device."

---

## SLIDE 5: Architecture Overview
**Title:** How It All Fits Together

**Visual suggestion:** Left-to-right pipeline diagram with five connected boxes:
`Technician Input` -> `Triage Agent (LLM)` -> `Evidence Agent (Rules)` -> `Escalation Agent (Rules)` -> `Human Approval / Auto-Resolve`
Below the pipeline: tech stack icons - LangGraph, Ollama, SQLite, Streamlit, FastAPI.
A cloud icon with a dotted line labeled "Sync when online" connecting to a cloud database.

**Bullet points:**
- Multi-agent orchestration via LangGraph state machine
- Local LLM inference via Ollama (Llama 3.1 8B primary, Mistral 7B fallback)
- SQLite for all persistence - cases, decisions, audit logs
- Streamlit multi-page UI + FastAPI backend with API key auth
- Everything runs locally. Offline-first by design.

**Speaker notes:**
"Here's the architecture. TRACE is a pipeline of three specialized AI agents orchestrated by LangGraph, which manages state transitions like a state machine. The technician inputs a fault code and symptoms. The Triage Agent calls a local Llama 3.1 model to generate ranked diagnoses. The Evidence Agent asks follow-up questions and adjusts confidence scores. The Escalation Agent checks four triggers to decide if a human needs to approve. If escalated, the case goes to a senior engineer's dashboard. If all clear, repair steps are delivered automatically. All of this runs locally - Ollama handles model inference on-device, SQLite stores everything, and the UI is a mobile-responsive Streamlit app. When connectivity returns, a sync engine pushes records to the cloud. No internet required for any core function."

---

## SLIDE 6: The AI Agents
**Title:** Three Agents, One Pipeline

**Visual suggestion:** Three horizontal cards, each with an icon, agent name, and key details. Use color coding: Triage (blue - AI/LLM), Evidence (amber - rule-based), Escalation (red - rule-based). Show "LLM-powered" badge on Triage and "Deterministic" badges on Evidence and Escalation.

**Bullet points:**
- **Triage Agent** (LLM-powered): Takes fault code + symptoms, calls Llama 3.1 8B, returns top 3 root causes with confidence scores, urgency, and estimated repair cost. Uses persona-engineered structured prompting.
- **Evidence Agent** (rule-based): Presents targeted follow-up questions (fuel pressure reading, filter mileage, visible leaks, cold starts). Adjusts confidence with deterministic rules. Visible leak = automatic safety escalation.
- **Escalation Agent** (rule-based): Four triggers - confidence < 70%, cost > $500, high urgency, or safety flag. Any trigger fires = case paused and routed to senior engineer.
- Design choice: only the initial triage uses an LLM. All safety-critical decisions are deterministic and fully auditable.

**Speaker notes:**
"Let me walk you through each agent. The Triage Agent is our LLM-powered diagnostician. It takes the fault code and symptoms, sends them to a locally-running Llama 3.1 model with a carefully engineered prompt - we give the model a persona of a certified Cummins diagnostic expert with twenty years of experience and require structured JSON output. It returns exactly three ranked root causes with confidence percentages, urgency levels, and cost estimates. The Evidence Agent is entirely rule-based - no LLM. It asks the technician targeted follow-up questions specific to the diagnosis: what's the fuel rail pressure reading? How many miles since the last filter change? Any visible leaks? Based on the answers, it adjusts confidence scores using deterministic rules. If the tech reports a visible fuel leak, that triggers an automatic safety escalation regardless of anything else. The Escalation Agent is also rule-based. It checks four triggers: confidence below 70%, cost above $500, high urgency, or a safety flag. If any single trigger fires, the case is paused and routed to a senior engineer. This is a deliberate design choice: we use the LLM where it adds the most value - pattern matching across thousands of possible fault causes - but every safety-critical decision is deterministic and fully auditable. No black box."

---

## SLIDE 7: Human-in-the-Loop
**Title:** AI Recommends. Humans Decide.

**Visual suggestion:** Workflow diagram showing the escalation path. Left: "AI Diagnosis Complete" box with a decision diamond showing the four triggers. Right: "Approval Dashboard" screenshot mockup showing the senior engineer's view with approve/reject buttons. Bottom: "Technician receives repair steps ONLY after approval."

**Bullet points:**
- Four escalation triggers (any one fires = escalation):
  - Confidence score < 70%
  - Estimated repair cost > $500
  - Urgency rated "High"
  - Safety flag detected (e.g., visible fuel leak)
- Senior engineer sees: full diagnosis, evidence collected, confidence gauge, cost estimate, urgency level
- Engineer approves or rejects with written notes
- Technician receives repair instructions ONLY after human approval
- No junior tech performs a safety-critical repair unsupervised

**Speaker notes:**
"This is the heart of our governance model. TRACE does not let a junior technician act on an AI recommendation for any high-stakes repair without human approval. We have four escalation triggers - if the confidence is below 70%, if the estimated cost exceeds $500, if urgency is high, or if any safety flag is detected, the case is immediately paused and sent to the Approval Dashboard. The senior engineer sees everything: the AI's diagnosis, the evidence the tech provided, the confidence score displayed as a visual gauge, the cost estimate, the urgency level. They can approve with notes, or reject and provide alternative guidance. The technician only receives repair instructions after that human signs off. This means there is always a named, accountable human behind every safety-critical decision. The AI accelerates the process, but a human owns the outcome."

---

## SLIDE 8: Offline Strategy
**Title:** Works Where Your Techs Work

**Visual suggestion:** Illustration of a truck broken down in a rural area with no cell signal bars. Below: diagram showing local SQLite + Ollama running on a laptop/tablet, with a dotted "sync" arrow to a cloud icon labeled "When back online."

**Bullet points:**
- All AI inference runs locally via Ollama - no internet required for diagnosis
- All data stored in local SQLite - cases, decisions, audit logs persist offline
- Sync engine activates on reconnect: pushes unsynced records to cloud, reconciles with last-write-wins
- Field reality: techs work inside engine bays, in rural dead zones, at highway breakdowns
- TRACE works everywhere the truck breaks down

**Speaker notes:**
"Field technicians don't work in offices with reliable Wi-Fi. They work inside engine bays where Bluetooth barely reaches, on rural highways with no cell signal, at truck stops at two in the morning. If your diagnostic tool requires an internet connection, it fails exactly when and where it's needed most. TRACE is offline-first by design. The Llama 3.1 model runs locally through Ollama. All data is stored in a local SQLite database. The technician can complete an entire diagnostic workflow - triage, evidence collection, escalation, even receive auto-approved repair steps - with zero internet. When connectivity returns, our sync engine pushes unsynced records to the cloud and reconciles any conflicts using a last-write-wins strategy. The tool works everywhere the truck breaks down."

---

## SLIDE 9: Decision Audit Trail
**Title:** Every Decision, Documented

**Visual suggestion:** Screenshot of the Decision Audit page showing the timeline view with agent actions, plus a snippet of the table view. Callout box highlighting a single log entry with all its fields. Small icons for CSV and JSON export.

**Bullet points:**
- Every agent action logged: timestamp, agent ID, inputs, output, confidence score, model used, human approval status
- Timeline view grouped by session - see the full diagnostic journey at a glance
- Table view with filters: by agent, session, action type, data source
- One-click export to CSV or JSON
- Built for: fleet compliance audits, warranty claim documentation, legal defensibility, regulatory review

**Speaker notes:**
"In fleet maintenance, documentation isn't optional - it's a legal and business requirement. TRACE logs every single action across the pipeline. When the Triage Agent generates a diagnosis, we log the timestamp, which model was used, what inputs it received, what it output, and the confidence score. When the Evidence Agent adjusts confidence, that's logged. When the Escalation Agent triggers, that's logged. When a senior engineer approves or rejects, their name, their notes, and the timestamp are logged. The Decision Audit page gives you two views: a timeline that shows the full diagnostic journey grouped by session, and a filterable table. You can export everything to CSV or JSON with one click. This is the compliance backbone. For warranty claims, you can prove exactly what was diagnosed, what evidence supported it, and who approved the repair. For regulatory audits, you have a complete chain of custody. For legal situations, you have timestamped, tamper-evident records of every decision."

---

## SLIDE 10: Live Demo
**Title:** Let's See It Work - P0191 Live Demo

**Visual suggestion:** This slide is a roadmap for the live demo. Show a numbered flow: (1) Enter fault code -> (2) AI triage -> (3) Evidence questions -> (4) Escalation -> (5) Senior approval -> (6) Repair steps delivered. Each step has a one-line description.

**Bullet points:**
- Scenario: Fault code P0191 (Fuel Rail Pressure Too Low) on a Cummins ISB 6.7L
- Watch for these key moments:
  1. AI returns 3 ranked causes in seconds (weak lift pump at 72% confidence)
  2. Evidence questions adjust confidence from 72% to 87%
  3. Auto-escalation triggers on cost ($850 > $500 threshold)
  4. Senior engineer reviews and approves on the Approval Dashboard
  5. Technician receives 10-step repair instructions
- Full audit trail generated automatically throughout

**Speaker notes:**
"Now let's see TRACE in action. I'm going to walk through our demo scenario: fault code P0191, Fuel Rail Pressure Too Low, on a Cummins ISB 6.7L diesel. [SWITCH TO LIVE DEMO] First, our technician enters the fault code, vehicle ID, mileage, and symptoms into the chatbot interface. Watch - the Triage Agent calls our local Llama model and returns three ranked root causes. Weak lift pump comes back at 72% confidence, clogged fuel filter at 18%, and injector leak at 10%. Now the Evidence Agent kicks in with follow-up questions. The tech reports fuel pressure under 500 PSI - that's well below the normal 870-plus. Filter was last changed 15,000 miles ago - overdue. No visible leaks. Hard cold starts for two weeks. Based on these answers, confidence adjusts up to 87%. Now the Escalation Agent evaluates: confidence is above 70% - no trigger. But estimated cost is $850, which exceeds our $500 threshold - trigger fires. The case is paused and appears on the Approval Dashboard. Let me switch to the senior engineer's view. Sarah sees the full diagnosis, the evidence, the confidence gauge at 87%, the cost estimate. She approves with a note. Now back on the technician's side - Jake receives his 10-step repair instructions. And if we check the Decision Audit page, every single step we just walked through is logged with timestamps. [END DEMO]"

---

## SLIDE 11: Business Impact & KPIs
**Title:** The Numbers That Matter

**Visual suggestion:** Four large KPI cards in a row: MTTR (with down arrow), FTFR (with up arrow), Quarterly Savings, ROI Timeline. Below: a small "Assumptions" box in lighter text.

**Bullet points:**
- **MTTR reduction: 42%** - from ~6 hours average to ~3.5 hours (AI-guided diagnosis eliminates guesswork and callback wait times)
- **FTFR improvement: 78%** - up from ~60% industry baseline (ranked root causes + evidence validation reduce misdiagnosis)
- **Estimated savings: $24,000/quarter** for a 50-truck fleet (fewer return visits, less parts waste, reduced downtime)
- **ROI: break-even within 6 months** at $200/truck/month subscription
- Assumptions: $85/hr loaded tech rate, 2.5 repairs/truck/month, 30% reduction in unnecessary parts orders

**Speaker notes:**
"Let's talk impact. We're targeting a 42% reduction in Mean Time to Repair - from roughly six hours down to three and a half. That comes from eliminating the guesswork loop: no more Googling, no more waiting 90 minutes for a senior tech callback, no more replacing the wrong part first. We're targeting a First-Time Fix Rate of 78%, up from the industry average of about 60%. That improvement comes from AI-ranked diagnoses validated by evidence collection before the tech picks up a wrench. For a 50-truck fleet, we estimate savings of $24,000 per quarter - driven by fewer return visits, less parts waste, and reduced vehicle downtime. At a subscription price of $200 per truck per month, a fleet operator breaks even within six months. I want to be transparent about our assumptions: we're using an $85 per hour loaded technician rate, an average of 2.5 repairs per truck per month, and a 30% reduction in unnecessary parts orders. These are projections based on the diagnostic improvement we've demonstrated, not field-validated production numbers yet."

---

## SLIDE 12: Governance & Safety
**Title:** Built for Accountability

**Visual suggestion:** Four governance pillars displayed as vertical bars or shield icons: Human Accountability, Zero Real Data, Fail-Safe Design, Audit Retention. Each with a one-line description.

**Bullet points:**
- **Human accountability**: Every safety-critical, warranty-affecting, or billing-relevant action has a named human approver
- **Zero PII exposure**: 100% synthetic data - 50 fault codes from SAE J1939/OBD-II standards, 100 simulated repair records, 12 example decision logs. All generated programmatically.
- **Fail-safe design**: If the LLM output fails to parse, confidence defaults to low, which forces escalation. The system fails toward human oversight, never away from it.
- **Audit retention**: Decision logs support 7-year retention for fleet maintenance compliance standards

**Speaker notes:**
"Governance isn't an afterthought in TRACE - it's foundational. Four pillars. First, human accountability: no repair that involves safety risk, warranty implications, or significant cost happens without a named human approver on record. Second, data privacy: we use zero real customer data. Every fault code, repair record, and decision log in our system is synthetic, generated programmatically from SAE J1939 and OBD-II standards. Third, fail-safe design: if the LLM returns something our parser can't interpret - malformed JSON, missing fields, anything unexpected - confidence defaults to low. Low confidence triggers escalation. The system always fails toward more human oversight, never less. And fourth, audit retention: our decision logs are structured to support seven-year retention, aligning with fleet maintenance compliance requirements. The AI makes recommendations. Humans make decisions. And everything is documented."

---

## SLIDE 13: Limitations & Honest Assessment
**Title:** What We Built, and What's Left to Build

**Visual suggestion:** Two-column layout. Left: "Current State" with honest limitation bullets. Right: "Production Path" with the corresponding solution for each limitation. Connected by arrows.

**Bullet points:**
- **Diagnostic depth**: Only P0191 has deep diagnostic logic. Other fault codes use a generic pipeline. *Path: expand to 10 most common codes, then full SAE library.*
- **Model accuracy**: Open-source LLMs (8B/7B params) are less accurate than GPT-4 class models. *Path: fine-tune on Cummins-specific repair data; upgrade to larger open models as hardware allows.*
- **Mobile interface**: Streamlit is a mobile-responsive web app, not a native mobile app. *Path: rebuild field tech UI as a native app with offline caching and camera integration for evidence photos.*
- **Cloud sync**: Sync engine uses a simulated local cloud database, not production infrastructure. *Path: migrate to Supabase or AWS with proper auth and encryption.*
- These are known limitations with clear paths to production.

**Speaker notes:**
"We want to be honest about where this prototype stands. Right now, only our P0191 demo scenario has deep, validated diagnostic logic. Other fault codes go through the same pipeline, but without the depth of evidence questions and calibrated confidence adjustments. Our open-source models are 7 to 8 billion parameters - they're remarkably capable, but they're not GPT-4. For production, we'd fine-tune on Cummins-specific repair data. Our UI is Streamlit - it's mobile-responsive and it works well for the demo, but for production, the field technician interface would be rebuilt as a native mobile app with offline caching and camera integration so techs can photograph evidence. And our sync engine currently writes to a second local SQLite file simulating a cloud database. For production, that becomes Supabase or AWS with proper authentication and encryption. We see these as known limitations with clear engineering paths, not fundamental blockers."

---

## SLIDE 14: Next Steps / Pilot Plan
**Title:** From Prototype to Pilot in 90 Days

**Visual suggestion:** A 90-day timeline with three phases. Phase 1 (Month 1): Setup & Integration. Phase 2 (Month 2): Controlled Deployment. Phase 3 (Month 3): Measure & Iterate. Below: key pilot parameters in a summary box.

**Bullet points:**
- **Pilot scope**: Single OEM fleet, 10-20 trucks, 2 senior engineers, 5 junior techs
- **Month 1**: Integrate with Cummins INSITE diagnostic data feed; expand to 10 most common fault codes with P0191-level diagnostic depth
- **Month 2**: Deploy to pilot fleet; collect real MTTR, FTFR, and technician satisfaction data
- **Month 3**: Measure against KPI targets; iterate on model accuracy and UX based on field feedback
- **Tech upgrades**: Migrate sync to Supabase/AWS, native mobile app development, SQLCipher encryption at rest

**Speaker notes:**
"Here's how we get from prototype to production. We're proposing a 90-day pilot with a single OEM fleet - ten to twenty trucks, two senior engineers on the approval side, and five junior technicians in the field. Month one, we integrate with Cummins INSITE to pull real diagnostic data instead of synthetic inputs, and we expand our deep diagnostic logic from one fault code to the ten most common codes in the fleet's history. Month two, we deploy to the pilot fleet and start collecting real data: actual MTTR, actual first-time fix rates, and technician satisfaction scores. Month three, we measure against our KPI targets and iterate based on what we learn in the field. In parallel, we upgrade the tech stack: migrate the sync engine to real cloud infrastructure, begin native mobile app development, and add encryption at rest with SQLCipher. The prototype proves the concept works. The pilot proves it works in the real world."

---

## SLIDE 15: Thank You / Q&A
**Title:** TRACE AI - Let's Talk

**Visual suggestion:** Clean slide with team names, contact info, and a QR code linking to the GitHub repo. The tagline in large font at the top.

**Bullet points:**
- "AI-powered diagnosis. Human-approved repairs. Every decision documented."
- Nhi Truong - Technical Lead | [contact]
- Zion Adedipe - Technical Lead | [contact]
- Campbell Lilian - Strategy & Research | [contact]
- GitHub: [repo link]
- We'd love your questions.

**Speaker notes:**
"TRACE AI gives junior technicians the diagnostic confidence of a 20-year veteran, keeps senior engineers in control of safety-critical decisions, and gives fleet managers a complete audit trail for every repair. AI-powered diagnosis. Human-approved repairs. Every decision documented. Thank you. We'd love your questions."

---
---

# BACKUP SLIDES

---

## BACKUP SLIDE B1: Prompt Engineering Deep Dive
**Title:** How We Talk to the AI

**Visual suggestion:** Side-by-side comparison showing a "bad prompt" vs. the actual TRACE triage prompt. Highlight the key techniques with labeled callout arrows: Persona, Structured Output, Negative Constraints, Grounding.

**Bullet points:**
- **Persona engineering**: "You are a certified Cummins diesel diagnostic expert with 20 years of field experience" - dramatically improves diagnostic quality vs. generic prompts
- **Structured JSON output**: We require exactly 3 root causes, each with: cause name, confidence %, explanation, urgency, estimated cost. Forces parseable, consistent output.
- **Negative constraints**: "Do NOT include generic causes. Do NOT exceed 3 causes. Do NOT recommend safety hazards without flagging." - prevents verbose, unsafe responses
- **Grounding in context**: We inject vehicle-specific data (mileage, last service, sensor readings) so the model reasons about actual data, not generic patterns
- **Chain-of-thought for escalation**: Step-by-step threshold checking reduces escalation errors by forcing explicit reasoning

**Speaker notes:**
"If anyone's curious about how we get reliable output from an 8-billion parameter model, it comes down to prompt engineering. We don't just ask 'what's wrong with this truck.' We give the model a specific persona - a Cummins-certified expert with twenty years on ISB 6.7L engines. We require structured JSON output with exactly three root causes, each with specific fields. We use negative constraints - 'do NOT include generic causes, do NOT recommend anything unsafe without flagging it.' And we ground the prompt in specific context: actual mileage, actual sensor readings, actual service history. The difference between a vague prompt and a well-engineered one is the difference between 'it might be the fuel system' and a ranked diagnosis with actionable confidence scores. We also use chain-of-thought prompting for escalation decisions, which forces the model to check each threshold step by step rather than pattern-matching to an answer."

---

## BACKUP SLIDE B2: Model License Details
**Title:** Open-Source, Commercially Clear

**Visual suggestion:** Three-row table with model name, license, and key terms. Green checkmarks for "commercial use OK."

**Bullet points:**
- **Llama 3.1 8B** (Meta Community License): Commercial use permitted for applications with fewer than 700 million monthly active users. No royalties. Redistribution requires license notice.
- **Mistral 7B** (Apache 2.0): Fully permissive. Commercial use, modification, distribution all permitted. No restrictions.
- **Ollama** (MIT License): Fully permissive. No restrictions on commercial use.
- No license blocks commercial deployment of TRACE at any realistic fleet scale
- Both models run locally - no third-party API terms of service apply

**Speaker notes:**
"We chose our models deliberately for license clarity. Llama 3.1 uses Meta's Community License, which allows commercial use for any application under 700 million monthly active users - we're targeting fleet maintenance, so that's not a concern. Mistral 7B uses Apache 2.0, which is fully permissive with no commercial restrictions at all. Ollama, which serves as our local inference runtime, is MIT licensed. Because both models run entirely on-device through Ollama, we're not subject to any third-party API terms of service. There are no license barriers to commercializing TRACE."

---

## BACKUP SLIDE B3: Detailed KPI Math
**Title:** ROI Calculation Walkthrough

**Visual suggestion:** A structured calculation table walking through each assumption and its dollar impact. Final row shows total quarterly savings and break-even point highlighted.

**Bullet points:**
- **Assumptions**: 50-truck fleet, $85/hr loaded tech rate, 2.5 repairs/truck/month, avg current MTTR of 6 hrs
- **MTTR savings**: 42% reduction = 2.5 hrs saved/repair x $85/hr = $212.50/repair. At 125 repairs/month = $26,562/month. Conservative 60% attribution to TRACE = ~$16,000/month
- **Parts waste reduction**: 30% fewer unnecessary part orders, avg part cost $150/incident. 125 repairs x 30% x $150 = $5,625/month
- **Return visit reduction**: FTFR from 60% to 78% = 18% fewer return visits. 125 x 18% x ($85 x 3 hrs) = $5,737/month
- **Total estimated savings**: ~$27,000/month (~$81k/quarter). Conservative estimate used in deck: $24k/quarter (applies 30% confidence discount)
- **Cost at $200/truck/month**: $10,000/month. Net savings: ~$14k-17k/month. Break-even: ~3-6 months

**Speaker notes:**
"Let me walk through the ROI math transparently. We assume a 50-truck fleet with a loaded technician rate of $85 per hour and an average of two and a half repairs per truck per month - that's 125 repairs per month across the fleet. On MTTR savings alone: a 42% reduction saves about two and a half hours per repair, which at $85 an hour is $212 per repair. Across 125 repairs, that's over $26,000 a month - but we conservatively attribute only 60% of that to TRACE, giving us about $16,000. Parts waste reduction from fewer misdiagnoses saves about $5,600 a month. And improving first-time fix rate from 60% to 78% eliminates about 22 return visits per month, saving another $5,700. The raw total is around $27,000 per month, but we apply a 30% confidence discount in our public numbers to account for real-world variability, which gives us the $24,000 per quarter figure in our main deck. At $200 per truck per month, the fleet's cost is $10,000 per month, so net savings are in the range of $14,000 to $17,000 monthly. Break-even within three to six months."

---

## BACKUP SLIDE B4: Sync Engine Technical Detail
**Title:** Offline Sync Under the Hood

**Visual suggestion:** Sequence diagram showing: (1) Tech works offline, writes to local.db (2) Connectivity detected (3) sync_to_cloud() pushes unsynced records (4) reconcile_from_cloud() pulls and merges (5) Conflict resolution via last-write-wins. Show sync_status field transitioning from "pending" to "synced."

**Bullet points:**
- **sync_to_cloud()**: Queries local SQLite for records with `sync_status = 'pending'`, pushes to cloud database, updates status to `'synced'` with timestamp
- **reconcile_from_cloud()**: Pulls records from cloud that don't exist locally, inserts them into local database. Uses **last-write-wins** for conflict resolution based on timestamps
- **sync_history table**: Tracks every sync event with direction (up/down), record count, timestamp, and success/failure status
- **Current implementation**: Cloud database is a second local SQLite file (cloud.db) for demo purposes. Production path: replace with Supabase or AWS RDS with the same sync interface
- **Resilience**: If sync fails mid-transfer, pending records remain marked as pending and retry on next sync cycle

**Speaker notes:**
"For those interested in the sync mechanics: when the technician works offline, all data writes go to a local SQLite database. Each record has a sync_status field that starts as 'pending.' When connectivity is detected, the sync_to_cloud function queries for all pending records, pushes them to the cloud database, and marks them as synced with a timestamp. The reconcile_from_cloud function does the reverse: it pulls any records from the cloud that don't exist locally and inserts them. For conflicts - cases where the same record was modified in both places - we use a last-write-wins strategy based on timestamps. Every sync event is tracked in a sync_history table with direction, record count, and success status. Currently, our 'cloud database' is a second local SQLite file called cloud.db, which lets us demonstrate the full sync workflow without requiring actual cloud infrastructure. For production, we'd replace cloud.db with Supabase or AWS RDS using the same interface - the sync logic itself doesn't change."

---

## BACKUP SLIDE B5: Commercialization Plan
**Title:** Path to Market

**Visual suggestion:** Go-to-market funnel: Target Buyer -> Channel -> Pricing -> 3-Year Projection. Include a simple revenue chart showing Year 1 through Year 3.

**Bullet points:**
- **Target buyer**: Fleet maintenance managers at Cummins-powered fleets (trucking, construction, mining, marine)
- **Channel**: Cummins dealer/distributor network - 600+ dealer locations as trusted point of sale. Co-marketing with Cummins Connected Solutions.
- **Pricing model**: SaaS subscription at $150-$250/truck/month, tiered by fleet size. Volume discounts above 100 trucks.
- **3-year projection** (conservative):
  - Year 1: 5 pilot fleets x 30 trucks avg = 150 trucks = $360k ARR
  - Year 2: 25 fleets x 40 trucks = 1,000 trucks = $2.4M ARR
  - Year 3: 80 fleets x 50 trucks = 4,000 trucks = $9.6M ARR
- **Key assumption**: 40% gross margin after hosting, support, and model compute costs

**Speaker notes:**
"Our go-to-market strategy centers on the Cummins dealer network. There are over 600 Cummins dealer locations that already have trusted relationships with fleet maintenance managers. We'd position TRACE as an add-on to Cummins Connected Solutions, sold through the existing channel. Our pricing model is SaaS: $150 to $250 per truck per month depending on fleet size, with volume discounts above 100 trucks. Conservatively, in year one we target five pilot fleets averaging 30 trucks each - that's 150 trucks at $200 per month, generating $360,000 in annual recurring revenue. By year two, we scale to 25 fleets and a thousand trucks for $2.4 million ARR. By year three, 80 fleets and 4,000 trucks gets us to $9.6 million ARR. We're assuming about 40% gross margin after hosting, technical support, and model compute costs. The key advantage is we're not building a sales channel from scratch - we're leveraging an existing one with built-in trust."

---

## BACKUP SLIDE B6: Security Posture
**Title:** Security by Design

**Visual suggestion:** Layered security diagram showing concentric rings: innermost = Data (SQLite, local), middle = Application (API key auth, role-based UI), outermost = Infrastructure (HTTPS, encryption at rest). Each layer has specific controls listed.

**Bullet points:**
- **Data stays local**: All inference and storage on-device. No data transmitted to external APIs. No cloud dependency for core operation.
- **API authentication**: FastAPI endpoints secured with API key validation via environment variables. No hardcoded secrets.
- **Role-based access**: UI presents different views by role - Technician sees chatbot only, Fleet Manager/Senior Tech sees Approval Dashboard. Role selected at entry.
- **HTTPS-ready**: Uvicorn supports SSL flags for encrypted transport in production deployment
- **Encryption at rest (production path)**: SQLCipher for encrypted SQLite databases. Drop-in replacement, no schema changes required.
- **No PII**: 100% synthetic data. No real customer, vehicle, or technician data in the system.

**Speaker notes:**
"Security was a design consideration from the start, not a bolt-on. The most important security feature is architectural: all data stays on the local device. No inference calls go to external APIs. No customer data is transmitted to the cloud unless the fleet operator explicitly enables sync. Our FastAPI endpoints use API key authentication managed through environment variables - no hardcoded secrets in the codebase. The UI implements role-based access: a technician only sees the chatbot interface, while a fleet manager or senior technician gets access to the Approval Dashboard. For production, we're ready for HTTPS through Uvicorn's SSL configuration, and for encryption at rest, SQLCipher is a drop-in replacement for SQLite that encrypts the database file with no schema changes. And fundamentally, our prototype contains zero real data - every fault code, repair record, and decision log was synthetically generated."

---

## BACKUP SLIDE B7: Competitive Landscape
**Title:** How TRACE Compares

**Visual suggestion:** Comparison matrix table. Rows: Cummins INSITE, Noregon JPRO, Decisiv SRM, TRACE AI. Columns: AI-Guided Diagnosis, Human-in-the-Loop, Works Offline, Full Audit Trail, Open-Source. TRACE has checkmarks in all columns; competitors have partial coverage.

**Bullet points:**
- **Cummins INSITE**: Industry-standard diagnostic reader. Reads fault codes and sensor data. No AI-guided diagnosis, no escalation workflow, no audit trail beyond basic logging. Requires connectivity for updates.
- **Noregon JPRO**: Multi-brand diagnostic tool. Provides fault code definitions and guided troubleshooting trees. Not AI-powered - static decision trees. No human approval workflow.
- **Decisiv SRM**: Cloud-based service relationship management. Manages repair workflows and communication between fleets and service providers. No on-device diagnostics, no AI triage, requires internet.
- **TRACE AI differentiators**: AI-ranked diagnoses (not static trees), mandatory human approval for high-risk repairs, fully offline operation, complete decision audit trail, built on open-source (no vendor lock-in)
- TRACE is not a replacement for these tools - it's a layer that adds AI intelligence and governance on top of existing diagnostic workflows

**Speaker notes:**
"The competitive landscape has established players, and we respect what they do. Cummins INSITE is the industry standard - it reads fault codes, displays sensor data, and provides reference information. But it doesn't tell a junior tech which of five possible root causes is most likely, and it doesn't prevent that tech from attempting a repair they shouldn't. Noregon JPRO offers guided troubleshooting, but through static decision trees, not AI-powered ranking. And it has no human approval workflow. Decisiv SRM manages repair workflows and fleet-service provider communication, but it's cloud-dependent and doesn't do on-device diagnostics. TRACE isn't trying to replace any of these tools. It's a layer that sits alongside them. INSITE gives you the fault code and sensor data. TRACE takes that data, uses AI to rank likely root causes, collects evidence to validate, ensures a human approves high-risk repairs, and logs everything for compliance. It's the intelligence and governance layer that doesn't exist in the current tool stack. And because it's built on open-source, there's no vendor lock-in."

---

*End of deck content. Total: 15 main slides + 7 backup slides.*

## TIMING GUIDE
| Slides | Content | Time |
|--------|---------|------|
| 1 | Title | 0:15 |
| 2-3 | Problem + User Story | 1:45 |
| 4 | Solution Overview | 0:30 |
| 5-6 | Architecture + Agents | 1:30 |
| 7-8 | Human-in-the-Loop + Offline | 1:15 |
| 9 | Audit Trail | 0:45 |
| 10 | Live Demo | 2:30 |
| 11 | Business Impact | 0:45 |
| 12-13 | Governance + Limitations | 1:00 |
| 14-15 | Next Steps + Close | 0:45 |
| **Total** | | **~10:00** |
