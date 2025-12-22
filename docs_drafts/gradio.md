Yes — this is a **very good instinct**, and it fits *perfectly* with everything you’ve been building.

You are essentially saying:

> “Free-text → LLM → IntentEnvelope” is *too implicit*.
> I want **explicit user authority** at the boundary.

That is exactly the right move.

Below is a **clear, staged task list** that keeps you in control, does *not* introduce new agent magic, and cleanly replaces the first layer with a Gradio-driven, explicit intent builder.

---

# Phase 5 — Explicit User Intent Interface (Gradio)

## Goal (restate crisply)

Replace the “free text interpreted by an LLM” entry point with a **structured, inspectable, user-driven IntentEnvelope builder**, implemented as a Gradio UI.

No inference.
No planning.
No authority leaks.

The UI becomes the **only place where ambiguity is resolved**.

---

## Architectural Positioning (important)

**Current pipeline (good):**

```
IntentEnvelope (structured)
        ↓
Document Planner (authoritative)
        ↓
Writer (realization)
```

**New pipeline (better):**

```
Gradio UI (explicit controls)
        ↓
IntentEnvelope (pure data)
        ↓
Document Planner
        ↓
Writer
```

The UI does **not** replace intent — it *constructs it deterministically*.

---

## Task List

### Task 5.1 — Define UI ↔ IntentEnvelope Mapping (No UI yet)

**Purpose:**
Lock down exactly how UI elements map to IntentEnvelope fields.

**Actions:**

* Create a short doc: `docs/intent_ui_contract.md`
* For each field in `IntentEnvelope`, specify:

  * UI control type (textbox, dropdown, multiselect, checkbox)
  * Required vs optional
  * Default behavior
  * Validation rules (if any)

**Example mapping (conceptual):**

| Intent Field                            | UI Control          |
| --------------------------------------- | ------------------- |
| `structural_intent.document_goal`       | Multiline text      |
| `structural_intent.audience`            | Dropdown + “custom” |
| `structural_intent.required_sections`   | Editable list       |
| `semantic_constraints.must_include`     | Tag input           |
| `semantic_constraints.must_avoid`       | Tag input           |
| `stylistic_preferences.narrative_voice` | Dropdown            |
| `stylistic_preferences.formality`       | Dropdown            |

**Rules:**

* UI never invents fields
* UI never infers missing values
* Empty == None / empty list

**Deliverable:**

* `docs/intent_ui_contract.md`

---

### Task 5.2 — Build IntentEnvelope Builder Function (No Gradio yet)

**Purpose:**
Decouple UI from construction logic.

**Actions:**

* Implement a pure function:

```python
def build_intent_envelope(
    document_goal: str | None,
    audience: str | None,
    tone: str | None,
    required_sections: list[str],
    forbidden_sections: list[str],
    must_include: list[str],
    must_avoid: list[str],
    narrative_voice: str | None,
    formality: str | None,
) -> IntentEnvelope
```

**Rules:**

* No defaults beyond schema defaults
* No normalization beyond trimming strings
* Raise validation errors immediately (Pydantic)

**Deliverable:**

* `domain/intent/ui_builder.py`
* Unit tests: input → IntentEnvelope

---

### Task 5.3 — Gradio UI: Intent Builder (Standalone)

**Purpose:**
Create a *pure intent editor* with no execution.

**Actions:**

* Create `apps/intent_builder/gradio_app.py`
* UI sections aligned with IntentEnvelope:

  1. Structural Intent
  2. Semantic Constraints
  3. Stylistic Preferences
* Add:

  * “Preview Intent (YAML)”
  * “Save intent.yaml”
  * “Load intent.yaml”

**Important:**

* No document planning
* No writer execution
* No LLM calls

This is a **form editor**, not an agent.

**Deliverable:**

* Gradio app that round-trips intent.yaml

---

### Task 5.4 — Integrate Gradio UI into Document Writer App

**Purpose:**
Make the UI a first-class entry point.

**Actions:**

* Add a mode to `agentic-document-writer`:

  * `--ui` launches Gradio
  * On submit:

    * Build IntentEnvelope
    * Call existing document + writer pipeline
* Preserve CLI usage:

  * CLI with `--intent intent.yaml` still works

**Rule:**

* UI produces the *same IntentEnvelope* as YAML loader
* No special-case logic downstream

**Deliverable:**

* Unified app: CLI + UI share the same pipeline

---

### Task 5.5 — Explicit Authority Guarantees (Hardening)

**Purpose:**
Make sure intent never silently mutates.

**Actions:**

* Add assertions / logging:

  * IntentEnvelope is passed unchanged from UI → document → writer
* Trace includes:

  * `intent_source: "ui" | "yaml" | "none"`
* Document and writer continue to treat intent as advisory only

**Deliverable:**

* Trace proof that UI intent does not gain authority

---

## What This Buys You (Important)

* **You regain the driver’s seat** at the *only* place ambiguity belongs: user intent
* No more “did the LLM interpret me correctly?”
* Intent becomes:

  * Inspectable
  * Versionable
  * Testable
* You can later add:

  * Presets
  * Templates
  * Organization-specific defaults
  * Validation profiles

Without touching planner or writer logic.

---

## Strong Recommendation (based on your concerns)

Do **not** add:

* “Free text → LLM → intent” *inside* this UI

If you ever want that, make it:

* A **separate optional helper**
* That outputs YAML
* Which the user must review and accept

This keeps **human authority explicit**.

---

If you want, next step I can:

* Write **Task 5.1 doc content**
* Or write a **Codex prompt for Tasks 5.2 + 5.3**
* Or sketch the Gradio layout (exact components)

Just tell me how deep you want to go next.
