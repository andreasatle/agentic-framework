Yes. And you are right to pause here — this is exactly the point where projects either become *powerful* or *unrecoverable*.
Below is a **deliberately ordered, minimal, authority-preserving task list** that gets you where you want **without collapsing layers or losing control**.

I am not speculating; this follows directly from your current architecture.

---

# Roadmap: Controlled User Intent → Deterministic Document Writing

## Phase 4 — Intent & Control (Structure First, Then Convenience)

### **Task 4.1 — Formalize the Intent Envelope (Layer 2, internal only)**

**Goal**
Create a *single authoritative container* for everything the user wants — including fuzzy, placement-agnostic constraints — **without leaking any of it to Document or Writer directly**.

**Actions**

* Introduce `IntentEnvelope`
* No UI, no parsing yet
* No behavior changes

**Deliverables**

* `domain/intent/types.py`
* Clear separation between:

  * structural intent
  * semantic constraints
  * stylistic / global constraints

**Invariant**

> IntentEnvelope is *not executable* and *not consumed directly* by any agent.

---

### **Task 4.2 — Define the Document Projection (Layer 2 → Layer 3 boundary)**

**Goal**
Make explicit what **Document is allowed to know**.

**Actions**

* Define `DocumentIntentView`
* Write a **pure projection function**:

  ```python
  def project_to_document_intent(envelope: IntentEnvelope) -> DocumentIntentView
  ```
* Projection must:

  * discard placement-agnostic constraints
  * discard writing tricks
  * preserve only structural signals

**Deliverables**

* Projection function
* Docstring stating what is intentionally lost

**Invariant**

> DocumentIntentView must be derivable *without* an LLM.

---

### **Task 4.3 — Harden Document Against Raw Intent**

**Goal**
Make it impossible to “accidentally” pass user intent to Document.

**Actions**

* Update `DocumentPlannerInput` to accept **only** `DocumentIntentView`
* Add validation that rejects:

  * raw strings
  * extra fields
  * envelopes

**Deliverables**

* Schema enforcement
* One failing test (then fixed)

**Invariant**

> Document never sees raw user language.

---

### **Task 4.4 — Introduce Global Writing Constraints (Layer 2 → Writer)**

**Goal**
Support requirements like:

* “tell my favorite joke at least once”
* “mention X somewhere”
* “avoid Y entirely”

**Actions**

* Define `GlobalWriterConstraints`
* These are:

  * placement-agnostic
  * non-structural
  * enforced holistically

**Deliverables**

* Schema only
* No execution yet

**Invariant**

> Constraints describe *what must be true*, not *where it goes*.

---

### **Task 4.5 — Constraint Distribution Strategy (Not Implementation)**

**Goal**
Decide *how* constraints are enforced without violating authority boundaries.

**Actions**

* Specify (in docs):

  * Which constraints are:

    * injected into Writer tasks
    * checked by the Writer Critic
    * verified post-hoc
* No code yet

**Deliverables**

* `docs/constraint_enforcement.md`

**Invariant**

> Writers are not trusted to remember global intent.

---

### **Task 4.6 — Writer Completeness Checkpoint**

**Goal**
Ensure the final document satisfies **global constraints**, not just per-section quality.

**Actions**

* Introduce a **Document-level Critic** (read-only)
* Input:

  * `DocumentTree`
  * `ContentStore`
  * `GlobalWriterConstraints`
* Output:

  * ACCEPT / REJECT + missing constraints

**Deliverables**

* Schema + stub
* No iteration yet

**Invariant**

> Section correctness ≠ document correctness.

---

### **Task 4.7 — Only Now: User Input Adapters (Layer 1)**

**Goal**
Make it user-friendly *after* control is guaranteed.

**Actions**

* Define adapters:

  * CLI
  * YAML
  * Gradio
* All adapters must emit **IntentEnvelope**
* No adapter may bypass it

**Deliverables**

* One adapter (CLI or YAML first)

**Invariant**

> UI is a convenience layer, never an authority layer.

---

## Mental Model (Lock This In)

```
User Input (messy, human)
        ↓
IntentEnvelope (authoritative, rich)
        ↓  [projection]
DocumentIntentView (structural only)
        ↓
DocumentTree
        ↓
WriterTasks + GlobalConstraints
        ↓
Sections
        ↓
Document-level validation
```

---

## Why this order matters

You asked whether to start with “layer 2” first.

**Yes. Absolutely. Non-negotiable.**

If you start with UI:

* you hard-code assumptions
* you leak intent
* you lose authority

If you start with projection:

* everything else becomes mechanical
* restrictions *force* correctness
* you stay in the driver seat

---

If you want, next I can:

* Turn this into numbered GitHub issues
* Write Task 4.1 as a Codex prompt + commit message
* Draw the authority diagram (who may see what)

Say which.
