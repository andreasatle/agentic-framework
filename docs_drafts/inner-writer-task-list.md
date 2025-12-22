Below is the **exact, linear task list**, rewritten cleanly, with **one Codex prompt and one final commit message per task**.

This is a **mechanical transformation plan**.
No design debate, no speculation, no demolition.

---

# **Inner Writer Refactor — Canonical Task List**

---

## **T1 — Prohibit Planner Structure Invention**

### Goal

Planner must not invent or infer document structure.

### Codex Prompt

```
TASK:
Prohibit planner from inventing document structure.

INSTRUCTIONS:
1. If structure is missing in project_state.domain, planner MUST raise an error.
2. Remove any fallback logic that creates default sections.
3. Planner must only select from explicitly provided structure.

CONSTRAINTS:
- Do NOT add new structure logic.
- Do NOT modify Supervisor.

SUCCESS CRITERIA:
- Planner fails fast if structure is missing.
- No implicit or generated sections exist.
```

### Commit Message

```
writer(planner): prohibit implicit structure invention
```

---

## **T2 — Remove Planner Ownership of Section Order**

### Goal

Planner must not emit or modify section ordering.

### Codex Prompt

```
TASK:
Remove planner responsibility for section ordering.

INSTRUCTIONS:
1. Remove section_order from PlannerOutput.
2. Ensure planner does not compute or emit ordering.
3. Preserve existing schema compatibility where required.

CONSTRAINTS:
- Do NOT change worker behavior.
- Do NOT modify SupervisorResponse.

SUCCESS CRITERIA:
- Section order is external-only.
```

### Commit Message

```
writer(planner): remove section_order authority
```

---

## **T3 — Replace Topic/Tone/Audience with Opaque Instructions**

### Goal

Inner writer must not interpret semantic intent.

### Codex Prompt

```
TASK:
Replace topic/tone/audience with opaque task instructions.

INSTRUCTIONS:
1. Remove topic, tone, audience, length from planner logic.
2. Introduce a single `instructions: str` field.
3. Planner must treat instructions as opaque text.

CONSTRAINTS:
- Do NOT add interpretation logic.
- Do NOT infer intent.

SUCCESS CRITERIA:
- Planner operates only on explicit instructions.
```

### Commit Message

```
writer: collapse semantic inputs into opaque instructions
```

---

## **T4 — Enforce Single-Task Planning**

### Goal

Planner must produce exactly one task.

### Codex Prompt

```
TASK:
Enforce single-task planning.

INSTRUCTIONS:
1. Remove any logic emitting completion sentinels.
2. Planner must emit exactly one task per invocation.
3. No looping or exhaustion logic allowed.

CONSTRAINTS:
- Do NOT introduce multi-task outputs.
- Supervisor loop remains unchanged.

SUCCESS CRITERIA:
- One request produces one task.
```

### Commit Message

```
writer(planner): enforce single-task planning
```

---

## **T5 — Define WriteOp Schema**

### Goal

Formalize the inner writer task contract.

### Codex Prompt

```
TASK:
Define WriteOp schema.

INSTRUCTIONS:
1. Create a new model WriteOp with fields:
   - op: draft | refine | merge | split
   - target_section
   - source_sections
   - instructions
2. Do NOT reuse WriterTask.
3. No behavioral logic inside schema.

CONSTRAINTS:
- Schema only.
- No supervisor changes.

SUCCESS CRITERIA:
- WriteOp exists and validates strictly.
```

### Commit Message

```
writer: introduce WriteOp schema
```

---

## **T6 — Adapter: Map WriterTask → WriteOp**

### Goal

Preserve backward compatibility during transition.

### Codex Prompt

```
TASK:
Introduce adapter from WriterTask to WriteOp.

INSTRUCTIONS:
1. Map existing WriterTask fields into WriteOp.
2. Adapter must be explicit and isolated.
3. No logic beyond field mapping.

CONSTRAINTS:
- Do NOT alter existing tests.
- Temporary compatibility only.

SUCCESS CRITERIA:
- Existing flows still execute.
```

### Commit Message

```
writer: add adapter from WriterTask to WriteOp
```

---

## **T7 — Require WriteOp in SupervisorRequest**

### Goal

Supervisor must execute externally provided tasks.

### Codex Prompt

```
TASK:
Require WriteOp in SupervisorRequest.

INSTRUCTIONS:
1. SupervisorRequest must include an explicit task.
2. Domain state must not influence task selection.
3. Remove planner autonomy over task creation.

CONSTRAINTS:
- Do NOT change Supervisor FSM.
- No orchestration logic added.

SUCCESS CRITERIA:
- Supervisor executes only provided tasks.
```

### Commit Message

```
supervisor: require explicit WriteOp
```

---

## **T8 — Remove Remaining Planner Branching Logic**

### Goal

Planner becomes a validator/echoer or is inert.

### Codex Prompt

```
TASK:
Remove remaining planner decision logic.

INSTRUCTIONS:
1. Eliminate conditional routing or branching.
2. Planner may validate task shape only.
3. No decision-making remains.

CONSTRAINTS:
- Keep interface intact.
- No behavior added.

SUCCESS CRITERIA:
- Planner cannot influence execution.
```

### Commit Message

```
writer(planner): remove residual decision logic
```

---

## **T9 — Make WriterDomainState Fully Passive**

### Goal

Domain state must not drive control flow.

### Codex Prompt

```
TASK:
Make WriterDomainState passive.

INSTRUCTIONS:
1. Remove any logic selecting next steps.
2. Domain state is snapshot-only.
3. Updates occur only via SupervisorResponse.

CONSTRAINTS:
- Do NOT change persistence format.

SUCCESS CRITERIA:
- Domain state cannot influence planning.
```

### Commit Message

```
writer(state): enforce passive domain state
```

---

## **T10 — Prohibit Structure Mutation in Inner Loop**

### Goal

Inner writer cannot alter structure.

### Codex Prompt

```
TASK:
Prohibit structure mutation inside inner writer.

INSTRUCTIONS:
1. Remove structure updates from domain update logic.
2. Structure must be treated as read-only.
3. Inner loop may only emit content.

CONSTRAINTS:
- Outer orchestration untouched.

SUCCESS CRITERIA:
- No structure changes from inner writer.
```

### Commit Message

```
writer: prohibit structure mutation in inner loop
```

---

## **T11 — Harden SupervisorResponse as Immutable Event**

### Goal

Ensure clean event boundary.

### Codex Prompt

```
TASK:
Harden SupervisorResponse immutability.

INSTRUCTIONS:
1. Ensure SupervisorResponse is frozen.
2. Ensure all fields are JSON-serializable.
3. No domain objects leak through response.

CONSTRAINTS:
- No Supervisor FSM changes.

SUCCESS CRITERIA:
- Response safe for replay and nesting.
```

### Commit Message

```
supervisor: harden immutable SupervisorResponse boundary
```

---

## **T12 — Add Op-Specific Inner Writer Tests**

### Goal

Lock execution semantics.

### Codex Prompt

```
TASK:
Add op-specific tests for inner writer.

INSTRUCTIONS:
1. Test draft, refine, merge, split independently.
2. Each test executes exactly one task.
3. Validate output shape strictly.

CONSTRAINTS:
- No supervisor nesting.

SUCCESS CRITERIA:
- All ops validated deterministically.
```

### Commit Message

```
writer: add op-specific inner execution tests
```

---

## **T13 — Enforce One Task per Supervisor Execution**

### Goal

Prevent hidden batching.

### Codex Prompt

```
TASK:
Enforce one task per supervisor execution.

INSTRUCTIONS:
1. Reject multi-task inputs.
2. Ensure one response corresponds to one task.
3. Add validation where necessary.

CONSTRAINTS:
- Supervisor FSM unchanged.

SUCCESS CRITERIA:
- One request → one immutable event.
```

### Commit Message

```
supervisor: enforce single-task execution invariant
```

---

## **T14 — Rename Domain Entrypoint to Inner Writer**

### Goal

Make architecture explicit.

### Codex Prompt

```
TASK:
Rename writer domain to inner_writer.

INSTRUCTIONS:
1. Rename entrypoints and CLI.
2. Update imports and references.
3. No behavior changes.

CONSTRAINTS:
- Backward compatibility optional.

SUCCESS CRITERIA:
- Intent is explicit in naming.
```

### Commit Message

```
writer: rename domain to inner_writer for clarity
```

---

## **Final Note**

This list **does not destroy** prior work.
It **locks it into a reusable inner executor** that any outer supervisor can drive.

When you are ready, the **outer supervisor** becomes trivial.

If you want:

* Codex prompts batched by phase
* A dependency graph
* Or a graduation checklist for other domains

Say so.
---
---
---
Remaining Writer Tasks

## Task 6 — Single WriterTask correctness (BLOCKING)

Goal: One WriterTask executes correctly end-to-end.

Non-empty requirements

Worker output satisfies requirements

Critic returns ACCEPT

WriterDomainState.update() is called exactly once

Result is stored in content.sections[section_name]

No retry loops

Status: ❌ Not verified

## Task 7 — Deterministic refine semantics

Goal: operation="refine" behaves correctly.

Previous section text is visible to worker

Worker output appends/refines previous text

No duplication on repeated ACCEPTs

Critic still evaluates only current task

Status: ❌ Not verified

## Task 8 — Domain state snapshot fidelity

Goal: Writer state passed to LLM is minimal and correct.

snapshot_for_llm() exposes only:

completed sections

structure section order

No full prose leakage

Snapshot is present but optional

Status: ❌ Not verified

## Task 9 — Planner re-entry on REJECT

Goal: REJECT cycles behave correctly.

Critic feedback routed back into planner

Planner emits corrected WriterTask

No section advancement on REJECT

No state mutation before ACCEPT

Status: ❌ Not verified

## Task 10 — Remove temporary structure bootstrap

Goal: Eliminate stabilization hack cleanly.

Structure must come from:

persisted state, or

explicit CLI / domain input

Guard remains

No silent defaults

Status: ❌ Not started

## Task 11 — Section ordering correctness

Goal: Final article assembly order is deterministic.

section_order respected

Default to structure order if unset

Refinements do not reorder sections

Status: ❌ Not verified

## Task 12 — Writer domain test coverage

Goal: Lock behavior.

Add tests for:

single task ACCEPT

refine flow

REJECT → retry → ACCEPT

state persistence

Status: ❌ Not done

## Task 13 — Remove legacy planner bypass

Goal: Planner is the only task source.

No manual WriterTask injection

Planner chooses next section based on state

Supervisor treats writer like other domains

Status: ❌ Not started

## Task 14 — Writer correctness checkpoint

Goal: Declare writer “hardened”.

No TODOs in writer domain

No temporary hacks

Supervisor untouched

Writer behaves like arithmetic/sentiment/coder

Status: ❌ Not started


---
---
---

# Inner Writer Cleanup — Iteration Plan
### Iteration 1 — Eliminate Planner as Task Source (BLOCKING)
Targets

Closes: T7, T8 (code-level), T13 (structural precondition)

Changes

Inject WriterTask explicitly

CLI constructs WriterTask

Pass task via planner_defaults or equivalent field

Planner becomes router-only

Validate task shape

Emit same task unchanged

Route to "writer-worker"

Guardrails

No Supervisor FSM changes

Planner emits exactly one task

No domain state consulted

Exit Criteria

Planner cannot invent or modify tasks

Supervisor executes externally supplied task

One supervisor run == one task

### Iteration 2 — Make Domain State Fully Passive
Targets

Closes: T9, stabilizes T11

Changes

Remove remaining_sections() usage from CLI control flow

Remove any “what’s next” logic from domain state

Domain state becomes:

snapshot provider

immutable updater on ACCEPT only

Guardrails

Persistence format unchanged

No state-driven loops

Exit Criteria

Domain state cannot advance execution

All control lives outside inner writer

### Iteration 3 — Schema Hygiene & Router Hardening
Targets

Closes: T3, completes T8

Changes

Remove legacy semantic fields from WriterPlannerInput

topic

tone

audience

length

Restrict planner input to:

instructions

task

project_state

Planner validates only:

task exists

task is well-formed

Guardrails

No interpretation logic

No new schema branches

Exit Criteria

Planner input is minimal and opaque

Planner is a pure router/validator

### Iteration 4 — Enforce Single-Task Execution Invariant
Targets

Closes: T13, strengthens T11

Changes

Reject multi-task payloads explicitly

Add assertion:

one SupervisorResponse corresponds to one WriterTask

Ensure no retries create additional tasks

Guardrails

FSM unchanged

No batching

Exit Criteria

One task in → one immutable event out

### Iteration 5 — Deterministic Writer Semantics
Targets

Closes: Remaining Writer Tasks 6–9

Changes

Verify draft semantics

Verify refine semantics

Ensure REJECT does not advance state

Ensure ACCEPT updates state exactly once

Guardrails

No planner changes

No new behaviors

Exit Criteria

Deterministic behavior for each operation

No duplicate or skipped updates

### Iteration 6 — Lock with Tests
Targets

Closes: T12, Remaining Task 12

Changes

Add tests for:

single-task ACCEPT

refine flow

REJECT → retry → ACCEPT

persistence round-trip

Guardrails

No supervisor nesting

One task per test

Exit Criteria

Writer semantics locked

Regression surface minimized

### Iteration 7 — Naming & Finalization
Targets

Closes: T14, Remaining Task 14

Changes

Rename domain/entrypoint to inner_writer

Remove TODOs and temporary scaffolding

Declare writer hardened

Guardrails

No behavior changes

Optional backward compatibility

Exit Criteria

Inner writer is reusable executor

Ready for outer supervisor


---
---
---

Below is a **concrete, prioritized task list for the writer domain**, scoped to *where the code actually is today* (single-task writer, no full document orchestration), and aligned with your stated Option A direction.

I am deliberately **not** proposing redesigns—this is cleanup, alignment, and hardening.

---

## Writer Tasks (Actionable, Ordered)

### **W1 — Remove legacy “full document” assumptions**

**Status:** Required
**Effort:** Small
**Why:** You already identified this as leftover complexity.

Tasks:

* Remove any remaining logic that assumes:

  * multi-section document ownership
  * writer being responsible for advancing document structure
* Ensure writer only ever:

  * receives **one WriterTask**
  * produces **one WriterResult**
* Confirm writer does *not* infer next sections or structure changes.

Outcome:

> Writer = pure task executor, nothing more.

---

### **W2 — Eliminate special-case plumbing from Supervisor**

**Status:** Required
**Effort:** Small–Medium
**Why:** `worker_kwargs` exists solely because writer was special.

Tasks:

* Remove `worker_kwargs` from `SupervisorDomainInput`
* Remove all Supervisor logic that conditionally injects writer state
* Move all writer-specific context preparation into:

  * `domain.writer.api.run(...)`
  * or the writer planner input

Outcome:

> Supervisor remains 100% domain-independent again.

---

### **W3 — Standardize WriterWorkerInput**

**Status:** Required
**Effort:** Small
**Why:** Writer input should look like every other WorkerInput.

Tasks:

* Decide explicitly:

  * Does writer *need* prior state?
    (Likely **no**, given task-only model.)
* If no:

  * Remove `writer_state` from `WriterWorkerInput`
  * Remove all code that passes or consumes it
* If yes:

  * Make it explicit, typed, and consistent (no kwargs injection)

Outcome:

> No hidden channels into the worker.

---

### **W4 — Tighten WriterPlanner contract**

**Status:** Required
**Effort:** Small
**Why:** Planner must not “helpfully” invent structure.

Tasks:

* Enforce in planner logic:

  * If required structure is missing → fail fast
* Ensure planner:

  * emits exactly one WriterTask
  * does not infer sections or reorder content
* Align test expectations with this behavior.

Outcome:

> Planner failure modes are explicit and deterministic.

---

### **W5 — Remove writer-only state persistence unless justified**

**Status:** Optional but recommended
**Effort:** Medium
**Why:** State persistence made sense for full documents, not tasks.

Tasks:

* Re-evaluate `WriterDomainState.load/save`
* If writer is task-based:

  * make state ephemeral
  * or move persistence responsibility outside writer
* If persistence remains:

  * document exactly *why* and *what is persisted*

Outcome:

> State exists only where it adds value.

---

### **W6 — Harden invariants with tests**

**Status:** Recommended
**Effort:** Small
**Why:** Prevent regressions like the one you just fixed.

Add tests asserting:

* Writer planner cannot run without required structure
* Writer worker:

  * never receives unexpected fields
  * never mutates state
* Writer execution does not require API keys unless invoked

Outcome:

> Future refactors won’t silently reintroduce special cases.

---

### **W7 — Documentation cleanup (last)**

**Status:** Optional
**Effort:** Small
**Why:** Your future self.

Tasks:

* Update writer README / docstrings to state explicitly:

  * writer is a **single-task executor**
  * not a document manager
* Remove any language suggesting otherwise.

Outcome:

> No ambiguity about writer’s role.

---

## Summary (one line)

> The writer needs **de-specialization, not expansion**.

If you want, next I can:

* turn this into a **Codex execution plan** (chunked prompts), or
* help you **decide W3 (state vs no state)** decisively, or
* map these tasks directly to commits.

Just tell me which.


---
---
---

Yes. Below is a **clean, linear plan** with **atomic tasks**.
Each task includes: **what**, **Codex prompt**, **commit message**.
No prose beyond what’s necessary.

---

## **W8 — Split writer into atomic workers (draft / refine)**

### **Task W8.1 — Define atomic task types**

**What**

* Replace `WriterTask(operation=...)` with:

  * `DraftSectionTask`
  * `RefineSectionTask`
* No `operation` field anywhere.

**Codex prompt**

```
GOAL:
Introduce atomic writer task types.

CHANGES:
- Add DraftSectionTask and RefineSectionTask models.
- Remove operation field from writer tasks.
- Update typing to reflect two distinct task types.

CONSTRAINTS:
- No behavior changes yet.
- Do not modify Supervisor.
- Keep schemas strict.

OUTPUT:
- Code changes only.
```

**Commit message**

```
Split WriterTask into DraftSectionTask and RefineSectionTask
```

---

## **Task W8.2 — Add two writer workers**

**What**

* Add:

  * `writer-draft-worker`
  * `writer-refine-worker`
* Each worker:

  * accepts only its task type
  * has one prompt
  * no branching

**Codex prompt**

```
GOAL:
Create separate writer workers for draft and refine.

CHANGES:
- Implement writer-draft-worker handling DraftSectionTask.
- Implement writer-refine-worker handling RefineSectionTask.
- Each worker has a single responsibility and prompt.

CONSTRAINTS:
- No shared logic between workers.
- No conditional branching.
- No state access.

OUTPUT:
- Code changes only.
```

**Commit message**

```
Add separate writer workers for draft and refine
```

---

## **Task W8.3 — Make writer planner a pure router**

**What**

* Planner:

  * validates task + structure
  * routes by task type
  * does **not** modify tasks

**Codex prompt**

```
GOAL:
Reduce writer planner to validator + router.

CHANGES:
- Planner must not decide operations or content.
- Route DraftSectionTask -> writer-draft-worker.
- Route RefineSectionTask -> writer-refine-worker.
- Validate section exists in structure.

CONSTRAINTS:
- Do not change Supervisor.
- Do not modify tasks.
- No inference.

OUTPUT:
- Code changes only.
```

**Commit message**

```
Make writer planner a pure router by task type
```

---

## **Task W8.4 — Update writer API + CLI**

**What**

* CLI / API must:

  * accept explicit task type
  * never infer draft vs refine
* Remove any legacy `operation` handling.

**Codex prompt**

```
GOAL:
Align writer API and CLI with atomic task model.

CHANGES:
- Update writer API to accept DraftSectionTask or RefineSectionTask.
- Remove all operation-based logic.
- Fail fast on ambiguous input.

CONSTRAINTS:
- No defaults.
- No inference.
- No persistence.

OUTPUT:
- Code changes only.
```

**Commit message**

```
Update writer API and CLI for atomic draft/refine tasks
```

---

## **Task W8.5 — Harden invariants with tests**

**What**

* Tests asserting:

  * draft worker never accepts refine task
  * refine worker requires prior content
  * planner routes purely by type
  * no shared behavior

**Codex prompt**

```
GOAL:
Lock atomic writer invariants with tests.

CHANGES:
- Add tests for worker/task exclusivity.
- Add planner routing tests.
- Ensure no cross-contamination.

CONSTRAINTS:
- Tests only unless production bug found.
- No weakening of validation.

OUTPUT:
- Test code only.
```

**Commit message**

```
Add invariant tests for atomic writer workers
```

---

## **Task W8.6 — Documentation cleanup**

**What**

* Update writer README + docstrings:

  * explain atomic workers
  * explain router planner
  * remove operation language

**Codex prompt**

```
GOAL:
Document atomic writer architecture.

CHANGES:
- Update src/domain/writer README and docstrings.
- Describe draft/refine as separate workers.
- State planner is router only.

CONSTRAINTS:
- Documentation only.
- No code changes.

OUTPUT:
- Doc changes only.
```

**Commit message**

```
Document atomic draft/refine writer architecture
```

---

## **End state (locked)**

* Two tasks
* Two workers
* Planner = validator + router
* No branching
* No shared prompts
* No spaghetti
* LLMs do only transformation

If you want, next I can:

* collapse this into **one Codex mega-prompt**, or
* help you sequence execution order safely.
