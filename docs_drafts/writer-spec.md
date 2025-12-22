# Writer Application — Formal Specification

## 1. Purpose

The Writer application produces a document **strictly according to an externally supplied structure**.
It does **not** invent structure, ordering, or completion semantics.

Writing is executed as a sequence of **independent, single-task supervisor runs**, coordinated by a deterministic controller.

---

## 2. Architectural Roles

### 2.1 Structure Supervisor (Outer Loop)

**Responsibility**

* Define document structure and task decomposition.
* Own section ordering and task list.
* Decide when the document is complete.

**Non-Responsibilities**

* Does not write content.
* Does not execute writing tasks.
* Does not call other supervisors.

**Interface**

```python
StructureSupervisorRequest
StructureSupervisorResponse
```

**Output Contract**

* Emits a **StructureState** containing an ordered list of writing tasks.
* Structure is immutable and authoritative.

---

### 2.2 Writer Supervisor (Inner Loop)

**Responsibility**

* Execute **exactly one** writing task.
* Validate the result via Critic.
* Emit one immutable execution event.

**Non-Responsibilities**

* Does not invent sections.
* Does not choose the next task.
* Does not loop.
* Does not decide completion.

**Interface**

```python
WriterSupervisorRequest
WriterSupervisorResponse
```

Each invocation corresponds to **one task only**.

---

### 2.3 Orchestrator (Non-LLM Controller)

**Responsibility**

* Coordinate execution between supervisors.
* Iterate over structure-defined tasks.
* Persist and rehydrate document state.

**Properties**

* Deterministic.
* No LLM calls.
* No schema ambiguity.
* No creative authority.

---

## 3. Core Data Models

### 3.1 StructureState (Read-Only)

```python
StructureState:
  sections: list[str]
  tasks: list[WriterTask]
  metadata: optional
```

**Rules**

* Created only by Structure Supervisor.
* Passed read-only to the Writer layer.
* Cannot be mutated by Writer Supervisor or agents.

---

### 3.2 WriterTask (Atomic Unit of Work)

```python
WriterTask:
  section_name: str
  operation: "draft" | "refine"
  purpose: str
  requirements: list[str]
```

**Rules**

* Fully specifies what the Writer must do.
* No optional semantics.
* No structural authority.

---

### 3.3 WriterResult

```python
WriterResult:
  text: str
```

---

### 3.4 DocumentState (External, Persistent)

```python
DocumentState:
  sections: dict[str, str]
  completed_sections: set[str]
```

**Rules**

* Owned and mutated only by the orchestrator.
* Updated only after ACCEPT decisions.
* Passed to Writer Supervisor as context only.

---

## 4. Execution Flow

### 4.1 High-Level Flow

```text
StructureSupervisor
        ↓
   StructureState
        ↓
Orchestrator
        ↓
for each WriterTask:
    WriterSupervisor(task)
        ↓
   WriterSupervisorResponse
        ↓
Orchestrator updates DocumentState
```

---

### 4.2 Writer Supervisor Semantics

* Input: exactly one `WriterTask` + partial document state.
* FSM executes: PLAN → WORK → CRITIC → END.
* Output:

  * ACCEPT → emits result event.
  * REJECT → emits failure event.
* No retries across tasks.
* No awareness of document completion.

---

## 5. Hard Constraints (Non-Negotiable)

### Structure Ownership

* Writer **must not** invent structure.
* Writer **must not** reorder sections.
* Writer **must not** decide what comes next.

### Supervisor Semantics

* One supervisor run == one task.
* No nested supervisors.
* No sentinel tasks (e.g., `"writer-complete"`).

### State Discipline

* Domain state is **read-only during execution**.
* All mutation occurs via accepted response events.
* SupervisorResponse is immutable.

---

## 6. Explicitly Forbidden Behaviors

The following are architectural violations:

* Writer planner choosing next section.
* Writer supervisor looping over multiple tasks.
* Planner inventing outlines or section orders.
* Structure encoded implicitly in prompts.
* Completion logic inside the writer supervisor.
* Supervisor-over-supervisor calls.

---

## 7. Supported Capabilities

This design **natively supports**:

* Partial documents
* Resume after interruption
* Deterministic re-runs
* Refinement passes (via new WriterTasks)
* Multiple writers or executors
* Non-LLM executors

Without modifying the supervisor core.

---

## 8. Design Principle (Invariant)

> **Structure is data, not behavior.**
> **Supervisors execute; controllers decide flow.**
> **LLMs never own control flow.**

This is the final invariant the Writer application must preserve.
