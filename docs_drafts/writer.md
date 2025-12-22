# **Writer Domain Specification — With Revisit/Refinement Enabled**

Below is the canonical, unambiguous behavior we will implement.

---

# **1. Planner Responsibilities**

The Planner must:

### **1.1 Produce a stable ordered table of contents (TOC)**

This list defines the *final* document order:

```
["Introduction", "Origin of Framework", "Architecture Overview", "Use Cases", "Conclusion"]
```

Stored in state as:

```
WriterState.section_order: list[str]
WriterState.sections: dict[str, str]  # Each keyed by section name
```

### **1.2 Choose the next section for writing or refinement**

For each cycle, Planner decides:

* a section name (may be newly written or previously written)
* an operation: `"draft"` or `"refine"`

Planner may pick **any** section at **any** time.

Examples of valid plans:

* “Start with Use Cases”
* “Refine Introduction again”
* “Write Conclusion”
* “Return to Origin after finishing Architecture”

### **1.3 Provide a clear Worker task**

PlannerOutput must include:

```
{
  "operation": "draft" | "refine",
  "section_name": "<string>",
  "requirements": [...]
}
```

---

# **2. Worker Responsibilities**

Worker takes the Planner’s request and:

### **2.1 For draft operations**

Produce a first version of a section.

### **2.2 For refine operations**

Receive:

* the **current version** of the section from WriterState
* the Planner’s refinement instructions
* contextual cues (other section summaries, if we choose later)

Worker outputs refined text.

### **2.3 Worker never concatenates sections**

Worker deals with **one** section at a time.

Concatenation is done only at the end.

---

# **3. Critic Responsibilities**

Critic evaluates **only the current section** draft/refinement.

If:

* ACCEPT → Supervisor stores section text into WriterState
* REJECT → Worker revisits immediately (according to your existing loop)

Critic does *not* judge the whole document.

---

# **4. Supervisor Responsibilities**

Supervisor must:

### **4.1 Maintain global WriterState instance**

WriterState includes:

```
section_order: list[str]
sections: dict[str, str]
```

### **4.2 Update the specific section when Critic ACCEPTs**

Supervisor assigns:

```
state.sections[current_section_name] = worker_output.text
```

### **4.3 Continue until Planner produces a “finalize_document” plan**

This is useful once we implement multi-cycle iterative refinement.

But for now you may stop when Planner indicates completion or after a fixed number of loops.

---

# **5. Final Assembly**

WriterMain should output:

* final ordered article assembled as:

```
"\n\n".join(state.sections[name] for name in state.section_order)
```

* plus the final WriterState if needed for persistence.

---

# **6. This architecture supports your long-term goal**

You want:

* professional-grade articles
* iterative refinement
* multi-pass writing
* section revisiting
* Planner-driven structure

This specification gets you there.

---
---
---

# **WRITER DOMAIN — FINAL SPEC (Planner Stateless, Sections Revisitable)**

---

# **1. WriterState**

```
class WriterState(LoadSaveMixin):
    section_order: list[str]
    sections: dict[str, str]   # name -> text
```

Properties:

* No completeness %, no iteration counters.
* The *text itself* is the only source of truth.
* Planner decides what to refine based on the existence or quality of content.

---

# **2. Planner Behavior (Stateless)**

Planner sees:

* current WriterState snapshot
* last_plan, last_result
* user-specified topic (optional)

Planner must:

### **2.1 Produce stable section_order once**

On the first cycle only, Planner outputs:

```
section_order = [...]
```

Supervisor writes these into WriterState if empty.

### **2.2 Choose section and operation each cycle**

Planner determines:

```
"operation": "draft" | "refine"
"section_name": <one of the TOC items>
"requirements": [specific instructions]
```

Rules:

* If section missing → must choose "draft".
* If section exists → may choose "refine" or choose a different section.
* Planner may revisit earlier sections indefinitely.
* Planner should attempt refinement cycles until quality is high.

### **2.3 Planner is not allowed to concatenate the entire article**

That's Supervisor's job at the end.

---

# **3. Worker Behavior**

Worker receives:

* operation
* section_name
* requirements
* previous_text (if refining)

Worker must:

### **3.1 When drafting**

Produce a new standalone section.

### **3.2 When refining**

Improve previous_text based on requirements.

Worker output schema:

```
{
  "result": {
      "text": "<section text>"
  }
}
```

---

# **4. Critic Behavior**

Critic evaluates:

* the single section text
* the Planner’s requirements

Critic rules:

* ACCEPT → Supervisor writes text into WriterState
* REJECT → Worker must retry (your existing retry loop already handles this)

Critic does *not* judge global coherence.

Later we can add a final pass to fix global flow.

---

# **5. Supervisor Behavior**

Supervisor must:

### **5.1 Maintain WriterState across cycles**

Does **not** create new states internally.
Uses the provided `domain_state` (WriterState).

### **5.2 During PLAN → WORK transition**

Store last_plan in project_state.

### **5.3 During WORK → CRITIC → STORE transition**

When ACCEPT:

```
state.sections[section_name] = worker_text
```

### **5.4 Stop condition**

Right now: fixed max loops or Planner plan field `"operation": "finalize"`.

---

# **6. Final Output (Writer Main)**

After Supervisor returns:

```
article = "\n\n".join(state.sections[name] for name in state.section_order)
```

Printed to stdout.

Domain state saved via LoadSaveMixin if desired.


---
---
---

# **FINAL WRITER ARCHITECTURE (Planner Stateless, Planner Controls section_order)**

## **1. WriterState**

```
class WriterState(LoadSaveMixin):
    section_order: list[str] | None = None
    sections: dict[str, str] = {}
```

* `section_order` is created exactly **once** by the first planner output.
* `sections` maps `section_name -> text`.

Supervisor writes to this state only when Critic ACCEPTs.

---

## **2. Planner — Stateless Deterministic Behavior**

### **2.1 First Plan — Must Output section_order**

On the first supervisor run where:

```
project_state.domain_state.section_order is None
```

Planner MUST output:

```
{
  "section_order": ["Introduction", "Origin Story", "Framework Fundamentals", ...],
  "task": { ... }
}
```

This is the only time section_order is created.

Supervisor extracts `section_order` and writes it into WriterState.

### **2.2 All Later Plans**

Planner inputs:

* snapshot.project_state.domain_state.sections
* snapshot.project_state.domain_state.section_order
* snapshot.last_plan
* snapshot.last_result

Planner must:

1. Choose a section to work on.
2. Decide between `"draft"` vs `"refine"`:

   * If section missing: `"draft"`
   * If exists: `"refine"`
3. Output one task:

```
{
  "task": {
    "section_name": "...",
    "operation": "draft" | "refine",
    "purpose": "<why this section exists>",
    "requirements": ["...", "..."]
  }
}
```

Planner **never** produces full text.
Planner **never** produces Markdown or metadata.
Planner **never** writes prose.
Planner **only** decomposes structure.

### **2.3 Planner Must Not Produce Global Content**

Planner does not assemble the final article.
This responsibility belongs to WriterMain.

---

## **3. Worker — Executes Only the Task**

Worker receives:

* section_name
* purpose
* operation ("draft" | "refine")
* requirements
* previous_text (if exists)

Worker must:

### **Draft Mode**

Produce stand-alone section text.

### **Refine Mode**

Improve previous_text using the new requirements.

Worker output schema unchanged:

```
{
  "result": {
    "text": "<section prose>"
  }
}
```

---

## **4. Critic — Single-Section Validation Only**

Critic checks:

* relevance to section_name
* purpose alignment
* all requirements satisfied
* no scope drift

Returns:

* ACCEPT (feedback null)
* REJECT (feedback.kind + message)

Critic does **not** enforce global article quality.
This allows iterative refinement.

---

## **5. Supervisor — Transition Rules**

### **PLAN → WORK**

* Capture last_plan in project_state.last_plan.
* If Planner output contains `"section_order"` **and** WriterState.section_order is None:

  * Persist that into WriterState.

### **WORK → CRITIC**

WorkerOutput.result → project_state.last_result.

### **ACCEPT → SAVE SECTION**

```
writer_state.sections[section_name] = result.text
```

### **Stop Condition**

Currently max_loops.
Optional later: Planner may output `"operation": "finalize"` to signal a global pass.

---

## **6. Final Article Assembly (WriterMain)**

After supervisor run:

```
article = "\n\n".join(
    state.sections[name] 
    for name in state.section_order 
    if name in state.sections
)
```

Output to stdout.

---

# **Your Architecture Is Now Internally Consistent**

* Planner remains stateless.
* Planner owns section_order.
* Supervisor owns persistence.
* Worker only writes text.
* Critic only judges local compliance.
* ProjectState stays minimal and generalizable.
* DomainState stays confined to WriterState.

This is exactly the architecture needed to scale to professional, multi-section article generation.
> ⚠️ Historical document  
> This document describes an earlier supervisor architecture that included
> `domain_state`. The current Supervisor is a pure one-pass executor and does
> not accept, inspect, or mutate state. State ownership and iteration now live
> entirely in application-level orchestration.

