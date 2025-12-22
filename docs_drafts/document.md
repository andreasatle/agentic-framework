# Corrected Understanding (Authoritative)

### Key clarification

* **DocumentSupervisor *is* an AnalysisSupervisor**
* It has:

  * ✅ a **Planner**
  * ❌ **no Worker**
  * ❌ **no Critic**
* Its role is **pure analysis / planning over document structure**
* It does **not** mutate document state
* It does **not** execute document operations
* It emits **document-level decisions**, not effects

Execution of those decisions happens **outside** the supervisor.

This is *intentional* and *correct*.

---

# Revised Mental Model (Very Explicit)

You now have **two kinds of supervisors**:

## 1. Execution Supervisors (full P–W–C)

Example:

* WriterSupervisor

Contract:

* Executes **one concrete task**
* Produces effects (text)
* Critic validates execution

## 2. Analysis Supervisors (planner-only)

Examples:

* DocumentSupervisor
* ParameterSupervisor (later)

Contract:

* Consumes state + context
* Emits **plans / decisions / intentions**
* Produces **no effects**
* No looping, no retries, no validation

This is **not a violation** of your Supervisor philosophy — it is a **specialized subclass**.

---

# Revised Plan for the Document Domain (Planner-only)

## Phase 0 — Accept the asymmetry

The Document layer is **not symmetric** with Writer.

That’s fine.

Trying to force symmetry is what caused earlier confusion.

---

## Phase 1 — Define the *DocumentTask* (planner output)

The DocumentSupervisor planner emits **document-level intentions**, not actions.

Example:

```python
class DocumentTask(BaseModel):
    op: Literal["init", "split", "merge", "reorder", "delete", "emit_writer_tasks"]
    target: str | None = None
    parameters: dict[str, Any] = {}
```

Important:

* These are **decisions**, not mutations
* They are **not executed** inside the supervisor

---

## Phase 2 — Define the DocumentSupervisor (AnalysisSupervisor)

### Inputs

* `DocumentState | None`
* Optional metadata (tone, audience, goal)
* Possibly previous decisions (if you choose)

### Planner responsibility

The planner:

* Looks at the **entire document state**
* Decides **what should happen next**
* Emits **exactly one DocumentTask** per call

Examples:

* First call (state = None):

  * `op="init"` with initial section list
* Later calls:

  * `op="split"` a section
  * `op="merge"` two sections
  * `op="emit_writer_tasks"` when structure is stable

---

## Phase 3 — What the DocumentSupervisorResponse contains

Because this is planner-only, the response is simpler and *different* from WriterSupervisorResponse.

Example:

```python
class DocumentSupervisorResponse(BaseModel):
    task: DocumentTask
    trace: list[dict] | None = None
```

No:

* worker_id
* worker_output
* critic_decision

This is **by design**, not a shortcut.

---

## Phase 4 — Where execution happens (outside the supervisor)

You already stated this correctly:

> “With the current architecture, we don’t call supervisors from inside other supervisors.”

So:

* The **caller**:

  * Receives `DocumentSupervisorResponse`
  * Applies the `DocumentTask` to `DocumentState`
  * Decides whether to:

    * Call DocumentSupervisor again
    * Or translate document structure into WriterTasks
    * Or stop

This is the **outer loop**, owned by application code.

---

## Phase 5 — Relationship to WriterSupervisor

When the DocumentSupervisor emits:

```python
op="emit_writer_tasks"
```

The caller:

* Converts current `DocumentState` into `WriterTask`s
* Calls **WriterSupervisor once per section**
* Collects results

The DocumentSupervisor never:

* Sees Writer output
* Calls WriterSupervisor
* Knows how writing works

Clean separation.

---

# Why this architecture is coherent (and not “going in circles”)

### You are doing **layered planning**, not recursive supervision

* Each layer:

  * Has a **single responsibility**
  * Emits **one decision**
  * Returns control immediately

No layer:

* Manages progress
* Manages iteration
* Calls another supervisor

That responsibility lives **outside**, intentionally.

---

# Answering your earlier questions directly

### “Do we have to replicate Supervisor?”

No.
You already did the right thing:

* `Supervisor` → execution
* `AnalysisSupervisor` → planning

They share concepts, not contracts.

---

### “Is DocumentSupervisor just a planner?”

Yes — and that is **not a weakness**.
It is a *design decision*.

Calling it an AnalysisSupervisor makes this explicit and honest.

---

### “Where does document mutation live?”

* Outside supervisors
* In plain Python
* Deterministic, testable, boring code

Exactly where it should be.

---

# Minimal next implementation step (revised)

**Do this next — nothing more:**

1. Define:

   * `DocumentTask`
   * `DocumentSupervisorResponse`
2. Implement `DocumentSupervisor` as:

   * Planner-only
   * Callable
   * Single-task output
3. Write **one test**:

   * Given `DocumentState=None`
   * Planner emits `init` with N sections

Stop there.

Once that works, everything else follows naturally.

---

If you want next, I can:

* Sketch the exact `DocumentSupervisor` code (planner-only)
* Help define `DocumentState` cleanly
* Help define how `emit_writer_tasks` should look

But the conceptual model is now solid — and aligned with what you intended.
