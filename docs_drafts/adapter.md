## Text → IntentEnvelope Adapter — Task List

### 1. Define the adapter contract

* **Input**: plain user text (string)
* **Output**: `IntentEnvelope`
* Explicitly document:

  * lossy transformation
  * non-authoritative
  * advisory-only semantics

*No planning, no execution, no structure.*

---

### 2. Create a dedicated controller

* New controller (e.g. `TextIntentController`)
* Single-pass
* No looping
* No workflow advancement
* Traceable input → output

This is a **projection controller**, not a planner.

---

### 3. Design the LLM prompt (narrow)

* Task: *extract intent signals only*
* Explicitly forbid:

  * structural decisions
  * section ordering
  * task creation
* Allow:

  * goal inference
  * audience inference
  * must_include / must_avoid extraction
  * stylistic preferences

Output must match `IntentEnvelope` schema exactly.

---

### 4. Enforce strict schema validation

* Pydantic validation on output
* Fail fast on:

  * unknown fields
  * missing required structure
* No auto-repair beyond retry

Invalid intent is better than silent drift.

---

### 5. Add provenance metadata (lightweight)

* Log:

  * source = `"text-adapter"`
  * original text hash
  * timestamp / model
* Do **not** store raw text unless explicitly requested

This preserves epistemic traceability.

---

### 6. Expose a new entrypoint

* New CLI / API entrypoint:

  * e.g. `agentic-document-from-text`
* Flow:

  1. Text → Intent controller
  2. Call existing `agentic-document-writer` pipeline unchanged

No branching inside the writer app.

---

### 7. Allow power-user override

* If user supplies:

  * YAML intent → bypass adapter
* Document this clearly:

  * “Text adapter is convenience, not authority”

---

### 8. Add one golden-path test

* Input: short paragraph
* Assert:

  * valid `IntentEnvelope`
  * no structural fields leaked
  * no execution behavior triggered

One test is enough to lock the contract.

