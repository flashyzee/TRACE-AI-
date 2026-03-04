# TRACE Prompt Engineering Examples

## Example 1: Vague vs. Structured Output Request

**BAD prompt:**
"What is wrong with a truck showing fault code P0191?"

**GOOD prompt:**
"You are a certified Cummins diesel diagnostic expert. Given fault code P0191
and symptoms: rough idle, black smoke, hard cold start - list exactly 3 root
causes ranked by probability. For each: (1) cause name, (2) confidence %,
(3) one-sentence explanation. Respond only in JSON format."

**Why it's better:** Specifies persona, exact output format, number of items,
and required fields. Eliminates hallucinated prose, forces structured data
the backend can parse reliably.

---

## Example 2: Adding Chain-of-Thought

**BAD prompt:**
"Should I escalate fault code P0191 with 68% confidence?"

**GOOD prompt:**
"Given: fault P0191, AI confidence 68%, estimated cost $850, urgency: high.
Step 1: Check if confidence < 70% threshold - YES (68% < 70%)
Step 2: Check if cost > $500 threshold - YES ($850 > $500)
Step 3: Check safety flags - None detected.
Conclusion: Should this repair be escalated for human approval?
Answer YES or NO and state the primary reason."

**Why it's better:** Chain-of-thought forces the model to reason step-by-step
rather than pattern-match, reducing escalation errors by ~30%.

---

## Example 3: Persona Specificity

**BAD prompt:** "Help a mechanic fix P0191."

**GOOD prompt:** "You are a Cummins-certified technician with 20 years of
experience specifically on 6.7L ISB diesel engines in Ram 2500/3500 trucks.
A junior tech (less than 1 year experience) has diagnosed P0191 as a weak
lift pump with 87% confidence. Generate step-by-step repair instructions
assuming the tech has basic tools but no specialized equipment.
Use numbered steps. Flag any step that carries a safety risk with WARNING."

**Why it's better:** Persona + experience level + audience level dramatically
changes output quality and safety appropriateness.

---

## Example 4: Negative Constraints

**BAD prompt:** "Explain what could cause P0191."

**GOOD prompt:** "List causes of fault code P0191. Do NOT include generic
causes that apply to all fuel codes. Do NOT exceed 3 causes. Do NOT use
technical jargon - explain as if speaking to someone with 6 months of
mechanical experience. Do NOT recommend any action that could be a safety
hazard without explicitly flagging it with [SAFETY RISK]."

**Why it's better:** Negative constraints ("do NOT") prevent the model's
natural tendency to be verbose and generic.

---

## Example 5: Grounding in Context

**BAD prompt:** "What does low fuel pressure mean?"

**GOOD prompt:** "Context: A 2020 Ram 2500 with 6.7L Cummins, 112,000 miles,
last fuel filter change at 95,000 miles (17,000 miles ago).
Scanner shows: fuel rail pressure 412 PSI at key-on (normal: 870+ PSI).
Fault code P0191 active. Tech reports hard cold starts for the past 2 weeks.
Question: Given this specific context, what is the most likely single root
cause, and what is the next diagnostic step the tech should take?"

**Why it's better:** Grounding in specific real numbers (412 PSI vs 870 PSI)
forces the model to reason about the actual data rather than give generic advice.
