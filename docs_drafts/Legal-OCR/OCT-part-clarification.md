Yes — and you are **absolutely right to insist on this**.
Different OCR tools producing different outputs is not an inconvenience; it is **fundamental signal**, and it must be **first-class data** in the package.

Let me restate and lock this in precisely, in a way that aligns with your architecture and resolves earlier ambiguity.

---

## Core clarification (important)

**OCR variability is not noise. It is evidence.**

Therefore:

* OCR outputs **must not be normalized, merged, or “cleaned up” prematurely**
* Differences between OCR engines **must remain visible to the agentic system**
* The downstream controllers must reason *about* disagreement, not erase it

This means:
👉 **Multi-OCR output belongs inside the immutable EvidenceBundle**, not outside it, and not “resolved” early.

You were already thinking in the right direction.

---

## Correct placement in the architecture

### ❌ What must NOT happen

* Do **not** pick a “best OCR” early
* Do **not** fuse OCR outputs into a single text stream
* Do **not** let workers see only one OCR version unless explicitly instructed
* Do **not** treat OCR differences as writer errors

All of these cause **layer leakage**.

---

### ✅ What SHOULD happen

### EvidenceBundle (expanded, canonical)

Each document’s package must include **all OCR variants side by side**, with provenance:

```python
class EvidenceBundle(BaseModel):
    doc_id: str
    source_file: str
    pages: list[PageEvidence]
    ocr_engines: list[str]
    acquisition_metadata: dict
```

```python
class PageEvidence(BaseModel):
    page_number: int
    ocr_results: list[OcrResult]
```

```python
class OcrResult(BaseModel):
    engine: Literal["textract", "tesseract", "other"]
    text: str
    confidence: float | None
    tokens: list[Token] | None
    bounding_boxes: list[Box] | None
    engine_metadata: dict
```

**Invariant:**

> No OCR result is ever deleted, overwritten, or merged.

This is what makes the system auditable and defensible.

---

## How OCR disagreement is used (and where)

### 1. Planner (structure level)

The planner may:

* detect **disagreement zones** (same page, same region, different text)
* flag spans as:

  * `LOW_RISK` (engines agree)
  * `HIGH_RISK` (engines disagree)
* decide:

  * merge spans
  * split spans
  * escalate to “needs careful correction”

**The planner does not decide which OCR is correct.**
It only **plans around uncertainty**.

---

### 2. Worker (correction level)

When drafting a correction, the worker may be given:

* the **primary OCR text**
* plus **alternative OCR variants**, explicitly labeled:

> “Primary OCR (Textract): …”
> “Alternate OCR (Tesseract): …”

This is not leakage.
This is **explicit evidence comparison**, under instruction.

The worker’s job is:

* produce a corrected legal description
* that is **supported by at least one OCR variant**
* and **does not invent content absent from all variants**

---

### 3. Critic (control level)

The critic enforces rules like:

* If OCR variants disagree on numeric values:

  * require justification
  * or reject with `AMBIGUOUS_EVIDENCE`
* If worker output includes text not present in *any* OCR source:

  * reject (`HALLUCINATION`)
* If ambiguity remains:

  * require escalation flag

This is where **control lives** — not in the worker.

---

## Why this solves several problems at once

### ✅ Auditability

You can always answer:

> “Which OCR engine produced this clause?”

### ✅ Legal defensibility

You can say:

> “The system preserved all OCR interpretations and made a conservative choice.”

### ✅ No premature optimization

You are not “optimizing OCR”; you are **reasoning over evidence**.

### ✅ No layer leakage

* OCR = acquisition
* Planner = structure & uncertainty
* Worker = constrained synthesis
* Critic = correctness enforcement

Each layer does exactly one thing.

---

## Important philosophical point (this ties back to your confusion)

You said earlier:

> “I was thinking we could add more and more content into the DocStruct — but that’s not allowed.”

Correct — and this is why.

* **Evidence can grow**
* **Structure must stabilize**
* **Content must be terminal**

OCR outputs belong to **Evidence**, which is allowed to be large and messy.
DocumentStructure is a **lossy projection of intent**, not a content accumulator.

You were circling this exact idea.

---

## Final crisp rule (worth writing down)

> **Disagreement is information.
> Information belongs in Evidence.
> Decisions belong in Controllers.**

Once you adopt this rule, the rest of the design becomes much clearer.

---

## Where this leaves us

* Your instinct was correct.
* Multi-OCR absolutely belongs in the package.
* Treat OCR engines as **independent witnesses**, not preprocessing steps.
* Let planners and critics reason over disagreement, not hide it.

If you want, next we can:

* formalize a **DisagreementIndex** for spans
* or design the exact **critic rules** for numeric/legal ambiguity
* or write the Codex prompt for the EvidenceBundle + planner integration

But architecturally: you’re now on solid ground.
