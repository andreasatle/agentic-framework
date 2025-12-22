Below is a **clean, linear, surgical task list**—each item is intended to become a Codex prompt.
This list is **implementation-oriented**, minimal, and structured so you can feed tasks **one at a time** into Codex without overhauls or architectural drift.

This is the complete sequence required to finish the professional Writer domain (multi-section whitepapers/blog posts) on top of your current agentic framework.

When you say *“Generate Codex prompt for task X”*, I’ll produce the exact Codex-ready patch instruction.

---

# **FULL PROJECT TASK LIST (Codex-Facing)**

Ordered so each step builds on the previous without breaking runtime.

---

## **Task 1 — Add WriterState.section_order**

Modify `WriterDomainState`:

* Add field `section_order: list[str] | None = None`.
* Ensure `.snapshot_for_llm()` includes only minimal fields, not section content.
* No behavior change yet.

---

## **Task 2 — Planner: Allow and pass through `section_order` in Planner output**

Modify `WriterPlannerOutput` schema:

* Add optional field `section_order: list[str] | None = None`.
* Planner agent wrapper: **first run** must emit section_order.
* Preserve backward compatibility: if Planner doesn’t emit it, output schema still validates.

---

## **Task 3 — Supervisor: Capture section_order from Planner and persist it**

Modify Supervisor’s PLAN handler:

* If `planner_output.section_order` is not None **and** the domain state has no `section_order`, then:

```
context.project_state.domain_state.section_order = planner_output.section_order
```

* Do not override if section_order already exists.

---

## **Task 4 — Planner behavior: Conditional section_order generation**

Modify WriterPlannerAgent wrapper logic:

* On first run: detect `project_state.domain_state.section_order is None`.
* Inject `section_order` into JSON before returning.
* Keep Planner logic stateless otherwise.

---

## **Task 5 — Store completed sections in WriterState.sections**

WriterState already has `sections: dict[str,str]`.
Modify Supervisor’s ACCEPT-handling in _handle_critic:

```
section = task.section_name
state.sections[section] = result.text
```

Do not overwrite unless refine_draft is used.

---

## **Task 6 — Worker accepts ‘operation’: draft vs refine**

Update `WriterWorkerInput`:

* Add field `operation: Literal["draft","refine"]` (or reuse existing WriterTask.operation).
* Worker logic:

  * draft → use LLM output as-is.
  * refine → prepend/merge with previous stored text.
* Remove old refine/ finalize logic from previous code.

---

## **Task 7 — Planner selects operation (draft/refine) based on state**

Modify WriterPlannerAgent:

* If section not in `state.sections`: operation = "draft"
* Else: operation = "refine"

Only the Planner decides operation from now on.

---

## **Task 8 — Critic stays single-section only**

Minimal patch:

* Validate that worker_answer.text is non-empty.
* ACCEPT everything else (MVP).
* Later upgrades allowed.

This ensures fast iteration without blocking.

---

## **Task 9 — WriterMain assembles final article**

Modify `domain/writer/main.py`:

After run completes:

```
state = updated_state
order = state.section_order or sorted(state.sections.keys())
sections = [state.sections[name] for name in order if name in state.sections]

article = "\n\n".join(sections)
print(article)
```

This prints the actual article.

---

## **Task 10 — Add argparse to writer/arithmetic/sentiment/coder mains**

Replace all `input()` calls with:

```
parser = argparse.ArgumentParser(...)
parser.add_argument("--topic", ...)
...
args = parser.parse_args()
```

Must apply uniformly, avoiding breaking tests.

---

## **Task 11 — Clean up writer_worker fallback logic**

* Remove unnecessary text wrapping.
* Keep JSON-only output.
* Ensure refine mode merges correctly.

---

## **Task 12 — Ensure all schema types validate under strict rules**

* Validate WriterPlannerOutput includes `"task"` and optional `"section_order"`.
* Validate WorkerOutput stays XOR-valid.
* Fix any incidental alignment bugs.

---

## **Task 13 — Add end-of-run save() for WriterState**

Replace:

```
updated_state = run.project_state.state
```

with:

```
updated_state = run.project_state.domain_state
```

Then:

```
updated_state.save()
```

Make uniform across domains.

---

## **Task 14 — Implement a “continue writing until all sections complete” mode**

(Optional, but recommended for full automatic article writing.)

Add loop in WriterMain:

```
while not state.all_sections_done():
    run = supervisor()
```

But only after everything above is stable.

---

# **This is the entire roadmap for a fully working multi-section professional Writer agent.**

If you want, I will now generate **Codex prompts** for each task one by one, starting with Task 1.


---
---
---
# Revised Iteration 2 Task List (Codex-ready)

Here is the cleaned, authoritative version I recommend you commit to:

## Writer — Iteration 2 (Correctness & Control)
### W2-1 — Topic-scoped writer state (hard requirement)

Add topic: str | None to WriterDomainState.

Persist writer state under a topic-derived key (slug or hash).

Implement:

WriterDomainState.load(topic=...)

WriterDomainState.save(topic=...)

Acceptance

Writing about “Fibonacci” never sees “War and Peace” sections

Re-running with the same topic resumes correctly

### W2-2 — Explicit fresh start flag

Add CLI flag --fresh.

If set:

Bypass loading persisted state

Start from an empty WriterDomainState

Still save at end under the topic scope

Do not delete or overwrite existing persisted state

Acceptance

--fresh guarantees a clean slate

Old state remains intact on disk

### W2-3 — Planner prompt hard topic guard

Add exactly one rule to PROMPT_PLANNER:

“If content does not directly follow from the topic, it must not be introduced.”

No other planner changes.

Acceptance

Planner does not introduce frameworks unless the topic implies them

### W2-4 — Critic enforces topic adherence

Extend WriterCritic:

Reject output if text is semantically off-topic

Use feedback kind: TOPIC_VIOLATION

Do not critique style, tone, completeness, or quality

Acceptance

Well-written but off-topic prose is rejected

On-topic prose is not rejected for stylistic reasons

### W2-5 — Single authoritative content state

Introduce WriterContentState as the only holder of:

sections

section_order

Refactor:

WriterDomainState holds metadata only (topic, version, timestamps)

No duplicate section storage anywhere

Acceptance

Exactly one content store

No structural ambiguity

No guessing which state holds text

### W2-6 — Remove remaining writer-specific isinstance

After W2-5:

Remove writer-specific isinstance checks from:

writer/main.py

writer/worker.py

Replace with typed contracts only

Acceptance

Writer code contains zero structural guessing

Type errors surface immediately, not implicitly

---
---
---
Below are the 3–5 highest-leverage features to add next. These are not cosmetic. Each one upgrades the writer from “LLM that produces text” to professional authoring system.

1. Explicit document contract (outline as law)

Problem today
The planner proposes sections, but nothing binds the document to a stable structure.

Professional behavior
Writers do not improvise structure mid-document.

Add

DocumentOutline (explicit, ordered, immutable once accepted)

Planner may propose outline

Supervisor locks it after first acceptance

All future plans must reference an existing section or explicitly request an outline revision

Why it matters

Prevents drift

Enables reviewers, editors, exports

Makes “document” a first-class object

2. Section lifecycle state machine

Problem today
Sections are just strings in a dict.

Professional behavior
Sections have status.

Add
Each section has a lifecycle:

PLANNED → DRAFTED → REVIEWED → REVISED → FINAL


Critic enforces transitions:

Can’t revise a section that was never drafted

Can’t finalize without review

Can’t create new sections without planner approval

Why it matters

Enables real editorial control

Allows partial completion

Makes refinement meaningful, not accidental

3. Topic + scope enforcement (hard constraint, not prompt-only)

Problem today
Topic discipline relies on prompt + critic judgment.

Professional behavior
Off-topic content is structurally impossible, not just discouraged.

Add

Explicit topic_scope in domain state:

keywords

exclusions

allowed abstractions

Critic enforces violations deterministically

Worker output rejected if scope violated, regardless of quality

Why it matters

Eliminates “beautiful nonsense”

Makes the system usable for clients

Separates writing skill from instruction fidelity

4. Revision intent separation (edit vs extend vs rewrite)

Problem today
“refine” is overloaded.

Professional behavior
Editors distinguish intent.

Add
Explicit operation types:

DRAFT – first creation

EXTEND – add content without modifying existing text

EDIT – improve clarity/style without adding ideas

REWRITE – structural change

Planner must choose one.
Critic verifies compliance.

Why it matters

Prevents silent semantic drift

Enables deterministic rewrites

Makes iterative editing sane

5. Deterministic final assembly & export

Problem today
Final text is implicitly assembled.

Professional behavior
Documents are compiled.

Add

Explicit assemble() step:

respects outline order

validates completeness

fails on missing sections

Export targets:

Markdown

PDF-ready Markdown

HTML

Why it matters

Turns writing into a pipeline

Enables automation

Makes “done” objectively defined

What you do NOT need yet

Do not add:

style guides

tone classifiers

grammar tools

embeddings

RAG

citations

Those come after editorial correctness.
> ⚠️ Historical document  
> This document describes an earlier supervisor architecture that included
> `domain_state`. The current Supervisor is a pure one-pass executor and does
> not accept, inspect, or mutate state. State ownership and iteration now live
> entirely in application-level orchestration.
