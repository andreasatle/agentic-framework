Below is a consolidated summary of what we discussed, followed by a start-to-finish implementation plan for a new “Legal PDF → Corrected Legal Description” project built in your controller-based agentic framework. I’m intentionally keeping this at the **intent/structure/plan** level (not writing OCR’d content), and I’m treating OCR as a **pre-agentic batch acquisition phase** with immutable evidence.

---

## Summary of our discussion

### 1) The architectural “line in the sand”

* **OCR is not agentic.** It is data acquisition: external, side-effecting, and often stochastic.
* Therefore, **OCR must run outside controllers** (and outside PWC loops).
* The agentic system should begin only after you have an **immutable EvidenceBundle** per PDF.

### 2) Why batch OCR first

Batching OCR first gives you:

* stable inputs (reproducibility)
* auditability (traceability to page/spans/confidence)
* separation of concerns (OCR failures vs reasoning failures)
* avoids “leakage” where worker becomes a hidden OCR engine

### 3) Multi-OCR can help, but only as parallel evidence

If you do multiple OCR passes (Textract, Tesseract, etc.), you should not “merge” outputs during OCR.

* Keep them as **separate evidence sources** with provenance.
* Any reconciliation/voting/selection is a **decision**, and belongs to planning/critique later.

### 4) Control and loops

* You have **controllers**, not supervisors: the loops live outside.
* The correction pipeline should be: precompute evidence → run controller(s) to decide what to do next → run worker(s) → critic validation → accept/reject/escalate.

---

## Goal and scope (the project definition)

### Inputs

* A directory of legal PDFs (scanned or mixed text + scanned).
* The target is **legal descriptions** (metes and bounds, lot/block, subdivision, exhibits, etc.).

### Outputs

For each PDF:

1. A **corrected legal description** (as clean text)
2. A **trace/audit package** explaining:

   * where the description came from (page numbers, OCR spans)
   * what was corrected and why
   * confidence / risk flags

### Non-goals (to keep it bounded)

* Not trying to “understand” the entire document.
* Not trying to do title chain logic.
* Not trying to build a full RAG over all docs initially.

---

## High-level architecture

### Phase 0 — Evidence acquisition (non-agentic)

* Iterate PDFs and run OCR (Textract recommended baseline).
* Optionally run a second OCR engine for ensemble evidence.
* Store per-PDF `EvidenceBundle`:

  * raw OCR text per page
  * bounding boxes (if available)
  * confidence scores (if available)
  * document metadata (file hash, page count, etc.)
  * provenance: engine name, version, timestamps

**Invariant:** Evidence is immutable and always preserved.

### Phase 1 — DocumentStructure planning (agentic P; no content writing yet)

* Use a planner/controller to:

  * locate candidate “legal description” regions
  * segment into spans (paragraph-level, line-level, or exhibit-level)
  * assign “risk flags” (low confidence, suspicious tokens, broken bearings, etc.)
  * decide whether the document is:

    * clearly contains a legal description
    * ambiguous
    * missing (needs escalation/manual review)

Output: a **DocumentStructure** (tree or list) describing where legal description likely lives and how it is partitioned.

### Phase 2 — Correction orchestration (agentic PWC or routed RWC)

* For each planned section/span:

  * Worker proposes a corrected version
  * Critic validates hard constraints (format, no hallucinated new parcels, numeric sanity checks, etc.)
  * If rejected, the planner refines the task for a retry (bounded retries)

### Phase 3 — Assembly + final audit

* Assemble accepted spans into a final corrected legal description.
* Produce an audit report:

  * diffs (before/after)
  * evidence citations (page numbers, OCR source)
  * confidence score / risk flags

### Phase 4 — Evaluation and continuous hardening

* Build a regression suite from a small curated set of PDFs.
* Add critics and deterministic validators until “publishable-grade” output is consistent.

---

## Data model and contracts (concrete but minimal)

You already have the philosophical separation: **intent/structure vs content**. Here’s how it maps here.

### A) Evidence schema (immutable)

`OcrEvidenceBundle` (per document)

* `doc_id` (hash of file contents)
* `pages: list[OcrPageEvidence]`

`OcrPageEvidence`

* `page_number`
* `sources: list[OcrSourceEvidence]`

`OcrSourceEvidence`

* `engine` (e.g., textract, tesseract)
* `text` (raw)
* optional `tokens/lines` with bounding boxes and confidences
* `engine_metadata` (version, settings)

**Important:** do not normalize away whitespace/punctuation at this stage; store raw.

### B) DocumentStructure schema (planner output)

A minimal structure could be:

`LegalDocPlan`

* `candidates: list[LegalDescriptionCandidate]`
* `decision: ACCEPT | REJECT | NEEDS_REVIEW`
* `notes/risk_flags`

`LegalDescriptionCandidate`

* `candidate_id`
* `page_range`
* `span_refs: list[SpanRef]` (references into evidence)
* `kind` (metes_bounds | lot_block | exhibit | unknown)
* `risk_flags`

`SpanRef`

* `page`
* `source_engine_preference` (optional advisory)
* `start_anchor / end_anchor` (string anchors or line indices)

This is your **lossy, stabilizing projection**: it’s not “content”; it’s a structured hypothesis about where content is.

### C) Writer tasks (worker input)

Your writer tasks already look right: `purpose`, `requirements`, `forbidden_terms`. For this domain you’ll want:

`DraftCorrectionTask`

* `node_id` / `span_id`
* `section_name`: e.g. “Legal Description — Span 1”
* `purpose`: “Produce corrected legal description text for this span”
* `requirements`: hard constraints (see critic section)
* `forbidden_terms`: optional

**What you feed the worker:** not the full document, but:

* the span’s OCR text (from evidence)
* optionally: a narrow context window around it (same page, ±N lines)
* plus requirements

### D) Worker result

`CorrectedSpanResult`

* `text` (corrected legal description for that span)
* optional `edits_summary` (structured list of changes) — helpful for audit

### E) Critics (hard validators)

There should be two kinds:

1. **Deterministic validators** (non-LLM)

   * numeric sanity checks (bearings format, degrees/minutes/seconds, distances)
   * balanced parentheses
   * no impossible tokens (e.g., “N 12° 60' 00"”)
   * detect suspicious OCR confusions: `0/O`, `1/I`, `S/5`, etc.

2. **LLM critic** (bounded)

   * checks the rewrite didn’t introduce new meaning
   * checks it stayed within scope (“no new parcels”)
   * checks it didn’t repeat other spans if it was told not to (span-local constraint)

---

## Handling repetition without letting content leak everywhere

You raised the central difficulty: if each section is written independently, how do you avoid overlap without feeding the whole document to the worker?

A disciplined way to do this without violating your separation:

### 1) Put anti-redundancy logic in structure, not in content

Before writing any span, compute a **SpanCoveragePlan**:

* identify which lines belong to which span
* ensure spans are disjoint or explicitly overlapping by design
* if a paragraph looks like a duplicate exhibit header, mark as “boilerplate” and exclude
* if two spans overlap heavily, merge them structurally

This is “optimization” at the **DocumentStructure level**, not post-hoc editing.

### 2) Use “previously accepted headings only” as context

If you want the writer to know “don’t reintroduce the framework” style constraints, you can provide a **thin outline context**:

* list of accepted section titles
* one-line “scope summary” per accepted section (not the full text)

That’s a controlled leakage: it’s still structure-level, not content-level.

### 3) Add a repetition critic that is evidence-based

A critic can compare:

* the candidate span output vs the input span text
* and/or vs other span outputs using hashing / similarity
  but you can keep it outside the worker context.

This way the worker remains a “monkey hitting keys,” and the system controls repetition via critics and structure.

---

## Start-to-finish execution flow

### Step 0 — CLI + artifacts

Create a new app, e.g.:

* `apps/legal_description_corrector`

  * `main.py` or Typer CLI
  * flags:

    * `--input-dir`
    * `--output-dir`
    * `--ocr-engine textract|tesseract|both`
    * `--cache-dir` (store evidence bundles)
    * `--trace`
    * `--print-intent` (like you already implemented for intent)
    * `--max-docs N` for iteration

### Step 1 — Evidence acquisition job

A batch runner:

* enumerates PDFs
* runs OCR engine(s)
* persists `EvidenceBundle` as JSON + raw text blobs
* stores doc hash, engine version, timestamp

This is the phase you can run overnight and rerun deterministically if needed.

### Step 2 — Planning controller (structure-only)

Input:

* `EvidenceBundle`
* top-level user goal:

  * “Extract and correct legal descriptions”

Output:

* `LegalDocPlan` (structure hypothesis: where the legal desc is)

Add `--print-plan` as YAML-like output (same concept as your `--print-intent`).

### Step 3 — Correction routing controller (RWC)

Loop outside controller:

* for each `SpanRef` in the plan:

  * create `DraftCorrectionTask`
  * call worker
  * call critic
  * if reject: create `RefineCorrectionTask` and retry (bounded)

Persist each accepted span result with provenance:

* which span
* which evidence source used
* critic decisions trace

### Step 4 — Assembly

Assemble spans according to plan:

* order by page then span order
* insert minimal separators if needed (blank line between paragraphs)

### Step 5 — Final critic (document-level)

A final pass:

* ensure output is cohesive
* ensure no major duplications across spans
* ensure no critical format errors remain
* produce risk score:

  * “needs human review” if high risk

### Step 6 — Output package

Write per PDF:

* `corrected_legal_description.txt`
* `audit.yaml` or `audit.json`
* `trace.jsonl` (optional)
* optionally: `diff.html` (nice for humans)

---

## Practical constraints and heuristics (domain-specific, high leverage)

Legal descriptions have structure that is ideal for *deterministic* checks. You should exploit that.

Examples of deterministic detectors:

* “Beginning at…” (metes and bounds)
* Bearings patterns: `N|S` … degrees … `E|W`
* Distances: `feet`, `ft`, `varas`, `meters`
* Lot/block: `Lot \d+`, `Block \w+`, `Subdivision`, `according to the map/plat`
* Exhibit markers: `Exhibit A`, `Schedule A`

Use these in the **planner** to find candidate spans and in the **critic** to validate.

This reduces the amount of “creative rewriting” the LLM must do.

---

## How to keep it “fully automatic” without hardcoding content

You said: “I don’t want to hardcode anything. It should be fully automatic.”

Interpretation that stays consistent with your architecture:

* You can hardcode **schemas, invariants, validators, and role contracts**.
* You should not hardcode **document-specific outlines, phrases, or fixed templates**.

So the system is automatic because:

* structure is inferred from evidence
* tasks are generated from structure + constraints
* validation is systematic and bounded

But it is still governed:

* by strict I/O schemas
* by deterministic checks
* by critics

That is exactly your “freedom from discipline” principle.

---

## How you bootstrap this project (recommended sequence)

Here is a practical staged plan that will converge quickly.

### Phase A — Minimal viable pipeline (1–2 days)

1. Implement EvidenceBundle ingestion for **one OCR engine** (Textract).
2. Implement a planner that outputs:

   * `decision: ACCEPT/REVIEW/REJECT`
   * `span_refs` for legal description candidates
3. Implement a worker that rewrites only one span at a time.
4. Implement a critic with:

   * “no hallucinated new parcels” instruction
   * basic format checks (presence of some expected keywords)
5. Save corrected output + audit.

### Phase B — Hardening and auditability (2–5 days)

1. Add deterministic validators (regex + numeric checks).
2. Add trace output showing:

   * which evidence span was used
   * which edits were made
3. Add “risk score” and “needs_review” output mode.

### Phase C — Multi-OCR ensemble (optional, later)

1. Add Tesseract as a second evidence source.
2. Planner flags disagreement regions.
3. Worker sees both OCR variants for the same span (explicitly labeled).
4. Critic requires:

   * choose one variant or reconcile explicitly
   * don’t invent content not supported by either

### Phase D — Regression suite

* Collect a small set of representative PDFs.
* Keep “gold” corrected descriptions (human verified).
* Run your pipeline and measure:

  * string similarity
  * number of critic retries
  * risk flags frequency

This is how you get to “publishable” reliably: not by one-off prompting, but by iterative hardening.

---

## What the “outermost layer” should do here

You wanted the “outer layer” to take sloppy input and produce organized intent/structure.

In this project, the outermost layer is:

**User request + EvidenceBundle → LegalDocPlan (structure)**

If the user prompt is sloppy (“fix legal descriptions”), the planner fills gaps by producing:

* target output type (corrected legal description)
* validation requirements
* scope boundaries (no new meaning)
* risk rules (escalate if low confidence)

And you can `--print-intent` / `--print-plan` to verify what the system inferred.

That fits your “shit in, organized shit out” requirement **without hardcoding content**.

---

## Deliverable plan (what you would implement, in order)

If you want a concrete checklist for Codex, these are the “top-level tasks”:

1. **Evidence Acquisition CLI**

   * Run OCR over directory
   * Persist EvidenceBundle per PDF
   * Deterministic doc_id hashing + caching

2. **LegalDoc Planner (structure-only)**

   * Input: EvidenceBundle
   * Output: LegalDocPlan with span_refs + risk flags
   * Add `--print-plan` YAML output

3. **Correction Orchestrator (outer loop) + RWC Controller**

   * For each span: build WriterTask → worker → critic → retry
   * Assemble final corrected description
   * Emit audit artifacts + risk scoring

That’s “start to finish” with a clean boundary at every layer.

---

If you restart a new prompt from scratch, you can paste the following single sentence as the top directive for the project:

> Build a controller-based pipeline that batch-OCRs a directory of legal PDFs into immutable EvidenceBundles, plans legal-description spans as a structure-only LegalDocPlan, then runs a bounded RWC loop per span to produce corrected legal descriptions with strict auditability and deterministic validation, without allowing evidence mutation or cross-section content leakage.

If you want, I can also write a single Codex execution prompt that implements those three top-level tasks in one pass (or split into three smaller prompts, depending on how you prefer to run Codex).
