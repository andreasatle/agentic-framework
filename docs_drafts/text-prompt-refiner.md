## Task List — Text Prompt Refiner

### **Task 1 — Define the contract (non-negotiable)**

* **Input**: raw user text (`str`)
* **Output**: refined user text (`str`)
* Explicitly document:

  * semantic-preserving
  * non-authoritative
  * advisory only
  * no invention of intent
* Write this as a module docstring and README note.

---

### **Task 2 — Create `TextPromptRefinerInput` schema**

* Fields:

  * `text: str`
* No metadata, no flags, no knobs.
* Keep it minimal on purpose.

---

### **Task 3 — Write the refiner system prompt**

The prompt must enforce:

* Preserve intent
* Clarify assumptions instead of resolving them
* Convert implicit negatives → explicit constraints
* Preserve first-person voice
* No headings
* No structure
* No explanations

This is the **hardest and most important task**.

---

### **Task 4 — Implement `TextPromptRefinerController`**

* Single-pass
* Planner-only style (like AnalysisController)
* No retries beyond dispatcher default
* Logs input hash + model (for provenance only)

Interface:

```python
refined_text = refiner(raw_text)
```

---

### **Task 5 — Add deterministic fake-agent test**

* Use a fake agent that returns:

  * tightened wording
  * preserved meaning
* Assert:

  * output is `str`
  * key phrases preserved
  * no new concepts added

This guards against silent drift later.

---

### **Task 6 — Integrate into `document_from_text` app**

Change pipeline to:

```
raw_text
 → TextPromptRefiner
 → TextIntentController
 → DocumentPlanner
 → Writer
```

No flags yet. Hard-wire it.

---

### **Task 7 — Add one “bad input” regression test**

Example input:

* rambling
* vague
* emotional

Assert:

* refined text is shorter
* intent density is higher
* still recognizably the same thought

This test defines success more than any spec.

---

### **Task 8 — Stop**

Do **not**:

* add configuration
* add temperature knobs
* add modes
* add web UX assumptions

Run it. Inspect outputs. Only then iterate.

---

## Acceptance criteria (very important)

This is done when:

> A non-expert can paste sloppy thoughts into the app
> and the output is **consistently better** than raw ChatGPT usage
> **without knowing why**.

That’s the benchmark.
