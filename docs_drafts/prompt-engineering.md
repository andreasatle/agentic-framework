Below is a **professional-grade specification document**, suitable for inclusion in your repository under `docs/prompt-engineering.md`.
It consolidates and formalizes the material you provided, removes redundancy, enforces structure, and reframes it in a way that is useful for both:

1. **LLM–API prompt engineering** (Planner/Worker/Critic, Codex refactoring, tool flows)
2. **ChatGPT-as-collaborator prompt engineering** (maximizing quality when interacting with *me*)

This is not a tutorial.
It is a **design specification** for engineering-quality prompting.

You can paste this directly into your docs.
If you want, I can also generate a version with a table of contents, cross-links, or examples.

---

# Prompt Engineering Specification

### A Unified Framework for LLM APIs and ChatGPT Interaction

## 1. Purpose and Scope

This document specifies a rigorous methodology for designing, testing, and maintaining prompts used in:

1. **Agentic workflows** implemented through LLM APIs (Planner/Worker/Critic loops, tool-enabled agents, strict JSON outputs).
2. **Interactive sessions with ChatGPT**, where the model functions as a reasoning engine or collaborator.

The goal is to produce **deterministic, auditable, and machine-reliable** results from LLMs while maintaining **high signal-to-noise** and **minimal drift** over long contexts.

This specification applies equally to OpenAI API calls and direct ChatGPT usage. Differences are documented explicitly in Section 10.

---

# 2. Conceptual Foundations

A prompt is not prose.
A prompt is an **interface contract**.

It defines:

1. **Task** – what the model must do.
2. **Constraints** – what the model must *not* do.
3. **Context** – the data and assumptions under which the task operates.
4. **Output Contract** – the exact structure, schema, and correctness conditions.
5. **Failure Handling** – what the model must do when unsure or when inputs are incomplete.

Prompt engineering is the discipline of **modelling a probabilistic language model as a deterministic program** and designing your prompts accordingly.

---

# 3. The I–C–E–O Model

A prompt succeeds or fails depending on four components:

### 3.1 Instructions (I)

Define the role, the scope, and the mandatory rules.

Characteristics:

* Narrow
* Explicit
* Non-overlapping
* Imperative (“You must…”, “You must not…”)
* Exclusive responsibilities (“Your only responsibility is…”)

### 3.2 Context (C)

Describe the environment and the data the model must operate on.

Rules:

* Never mix background with actionable tasks.
* Context should not contain goals unless strictly necessary.
* Keep context factual, not interpretive.

### 3.3 Examples (E)

Optional but powerful in controlling style and edge behavior.

Use when:

* The model repeatedly misinterprets a transformation.
* You need to align format, tone, or structure.
* You want negative examples to prevent specific failure modes.

### 3.4 Output Specification (O)

The most critical component for reliability.

The output must be:

* **Strict**
* **Machine-checkable**
* **Deterministic**
* **Singular** (one valid shape; everything else is invalid)

When outputs are structured (JSON, diff, code), include:

* Keys
* Allowed types
* No extra fields
* No commentary
* No Markdown unless intentionally required

---

# 4. Systematic Prompt Design Workflow

The most reliable workflow is:

### Step 1 — Define the task sharply

If you cannot describe the task in one sentence, the prompt will drift.

### Step 2 — List potential failure modes

Include only actionable failure-prevention rules in the prompt.

### Step 3 — Define the output contract

This is where you eliminate ambiguity.

### Step 4 — Provide minimal permissible freedom

Too much freedom → hallucinations
Too little freedom → brittle or low-quality

### Step 5 — Include a fallback policy

LLMs perform better when given explicit behavior for edge cases:

Examples:

* “If information is missing, ask a single clarifying question.”
* “If a field is not available, output `{"error": "insufficient information"}`.”
* “If unsure, choose the minimal safe interpretation.”

### Step 6 — Evaluate against real edge cases

Prompts must be tested on difficult examples before finalizing.

---

# 5. Engineering Patterns for Different Agent Roles

## 5.1 Planner Prompts

Purpose: **decompose goals**, not execute work.

Specifications:

* Must not produce solutions or final outputs.
* Must produce only a structured task.
* Must integrate feedback or project state **only if present**.
* Must produce deterministic JSON.

Template:

```
ROLE:
You are the Planner. Your ONLY responsibility is to decompose tasks. 
You do not solve tasks and you do not produce Worker outputs.

INPUT:
{ "goal": ..., "previous_task": ..., "feedback": ..., "project_state": ... }

OUTPUT (STRICT JSON):
{ "task": { ... }, "worker_id": "..." }

RULES:
1. Use only the input fields provided.
2. No explanations or commentary.
3. No fields other than those specified.
4. If feedback is present, revise the task minimally to satisfy it.
```

---

## 5.2 Worker Prompts

Purpose: **execute one atomic task or request a tool call.**

Workers require:

* Strict I/O schema
* Forcing branch exclusivity (`result` XOR `tool_request`)
* Deterministic or near-deterministic temperature (0.0–0.1)

Template:

```
OUTPUT (STRICT JSON):
Either:
    {"result": ...}
OR:
    {"tool_request": {"tool_name": "...", "args": {...}}}

RULES:
- Output EXACTLY one of the two keys.
- Do not include explanations.
- Do not produce extra keys.
```

---

## 5.3 Critic Prompts

Purpose: **verify**, not generate content.

Critics must:

* Produce ACCEPT/REJECT only.
* Give feedback only on REJECT.
* Never propose new content.
* Be deterministic (temperature 0.0).

Template:

```
OUTPUT (STRICT JSON):
{ "decision": "ACCEPT" | "REJECT", "feedback": string | null }

RULES:
1. Reject if any requirement fails.
2. Provide minimal actionable feedback.
3. Do not generate alternative content.
4. Do not modify the task.
```

---

# 6. Code-editing Prompts (Codex Mode)

Editing is different from generation.
The model must be forced into **surgical** behavior.

Guidelines:

* Define region boundaries explicitly.
* Forbid modifications outside target region.
* Specify whether the output is a **diff** or a **full file**.
* Force deterministic rewriting.

Example (diff mode):

```
OUTPUT (STRICT):
Return ONLY a unified git diff (no commentary, no explanations).
```

Example (whole-file mode):

```
OUTPUT (STRICT):
Return the entire modified file. No Markdown fences. No commentary.
```

---

# 7. Negative Instructions: How to Make Them Work

Negative rules work only when they are:

* Specific
* Grouped
* Paired with fallback behavior
* Never contradicted elsewhere

Wrong:

> “Don’t hallucinate.”

Correct:

```
If information is missing, do NOT infer or invent. 
Return: {"error": "insufficient information"}.
```

---

# 8. Ensuring Determinism

For high-reliability workflows:

* Planner: mild randomness (0.3–0.5) for creativity in task decomposition
* Worker: near-zero temperature
* Critic: zero temperature

Where drift is undesirable:

* Repeat the output format at the *end* of the prompt.
* Keep prompts short and structured.
* Place hard constraints in the final lines (recency bias).

---

# 9. Using Optional State Properly

State fields (project_state, domain_state) must follow:

* Never required
* Never assumed
* Used only as guidance
* Clean omission when empty (avoid `null` pollution)

Prompt additions should specify:

```
STATE (OPTIONAL):
If project_state is present, you MAY use it to improve decisions.
If absent, behave exactly as before.
You must never require it.
```

This enables optional memory *without breaking stateless domains*.

---

# 10. Using ChatGPT vs LLM APIs

### 10.1 Shared cognitive architecture

Both ChatGPT and the API models share the same inference engine:

* token-by-token generation
* instruction-following patterns
* recency bias
* sensitivity to role definition
* need for strict output specs

So the *same prompt structures* apply to both.

### 10.2 Key differences

#### A. Persistence

ChatGPT has **conversation history**; API calls do not.
This means:

* ChatGPT can drift if history contains conflicting instructions.
* APIs require full, fresh prompts per call.
* ChatGPT benefits from “context reset” blocks.

Pattern:

```
CONTEXT RESET:
Ignore all prior turns unless explicitly included below.
```

#### B. Determinism

API calls with fixed seed + low temperature
→ reproducible.

ChatGPT UI
→ less deterministic due to unknown sampling settings and unseen system prompts.

#### C. Invisible system layer

ChatGPT adds alignment layers beyond your prompt.
APIs obey you more literally.

Implication:
ChatGPT sometimes adds commentary unless forcefully forbidden.

#### D. Length constraints

API prompts can be longer and more structured.
ChatGPT sometimes compresses or omits due to UI heuristics.

---

# 11. Best Practices for Maximally Utilizing ChatGPT

### 11.1 Always specify role + scope + constraints

Example:

```
ROLE: You are a critic. Your ONLY job is to judge compliance.
```

### 11.2 Never interleave background and task

Separate:

* CONTEXT
* TASK
* OUTPUT FORMAT
* RULES

### 11.3 Leave the final lines for your hardest constraints

Models weight the final tokens heavily.

### 11.4 Do not write long, flowery prompts

Clarity > length.

### 11.5 Eliminate ambiguity

If the model can interpret a task in two ways, it will.

### 11.6 Use fallback behavior

Eliminates hallucinations.

### 11.7 When in doubt: structure, not prose

Use headings, lists, and schemas.

---

# 12. A Complete Template for Professional-Grade Prompts

```
ROLE:
<define agent identity and exclusive responsibility>

CONTEXT:
<provide relevant facts, no tasks here>

INPUT FORMAT (JSON):
<define structured input>

OUTPUT FORMAT (STRICT JSON):
<define exact output shape>

TASK:
- <enumerate required operations>
- <define scope limits>

RULES:
1. MUST <...>
2. MUST NOT <...>
3. FALLBACK: If <condition>, output <error JSON>.

STATE (OPTIONAL):
If project_state is present:
- MAY use it to improve decisions.
If absent:
- Behave as before.

BEGIN NOW.
```

---

# 13. Next Steps

I can:

1. Convert this doc into a smaller **“Prompt Engineering Quick Reference”**.
2. Rewrite all your **Planner/Worker/Critic prompts** to follow this spec exactly.
3. Produce a **Codex-specific** prompt-engineering supplement.
4. Generate a **testing harness** that validates all prompts across scenarios.

Tell me which direction you want next.
> ⚠️ Historical document  
> This document describes an earlier supervisor architecture that included
> `domain_state`. The current Supervisor is a pure one-pass executor and does
> not accept, inspect, or mutate state. State ownership and iteration now live
> entirely in application-level orchestration.
