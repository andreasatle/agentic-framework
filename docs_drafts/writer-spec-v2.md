# Writer Application — Two-Level Supervisor Specification (v2)

## 1. Architectural Overview

The writer application consists of **two strictly separated supervisors**:

| Level                                       | Responsibility                       | Authority   |
| ------------------------------------------- | ------------------------------------ | ----------- |
| **Outer Supervisor (Structure Supervisor)** | Document structure and global intent | Absolute    |
| **Inner Supervisor (Writer Supervisor)**    | Produce text for one section         | Subordinate |

There is **no shared mutable state**.
All interaction occurs via **explicit request/response contracts**.

---

## 2. Global Writing Constraints (New)

Global constraints include:

* `topic`
* `audience`
* `tone`
* `length`
* `sentiment` (optional, domain-specific)
* any other document-wide intent

### Ownership rule

> **Global constraints are owned by the outer supervisor.**

They are:

* **declared once**
* **passed down read-only**
* **never invented or modified by the inner writer**

---

## 3. Outer Supervisor (Structure Level)

### Inputs

```python
StructureSupervisorRequest:
    document_id: str
    global_constraints:
        topic: str
        audience: str | None
        tone: str | None
        length: str | None
        sentiment: str | None
    previous_structure: StructureState | None
    previous_content: ContentIndex | None
```

Where:

```python
StructureState:
    sections: list[SectionSpec]

SectionSpec:
    section_id: str
    title: str
    intent: str
```

`ContentIndex` contains *references only*, never raw text.

---

### Outputs

```python
StructureSupervisorResponse:
    structure: StructureState
    tasks: list[StructureTask | WriterTask]
    rationale: str | None
```

---

### Structure Tasks (No Inner Loop)

```python
StructureTask =
    AddSection
  | RemoveSection
  | SplitSection
  | MergeSections
  | ReorderSections
```

Examples:

```python
RemoveSection(section_id="S3")
SplitSection(section_id="S4", into=["S4a", "S4b"])
MergeSections(source_ids=["S2", "S5"], target_id="S2")
```

**Rules:**

* Structural tasks **never invoke** the inner supervisor
* Structural tasks **may destroy content**
* Structural tasks **must be explicit**

---

### Writer Tasks (Delegated)

```python
WriterTask:
    section_id: str
    operation: "draft" | "refine"
    constraints:
        topic: str
        audience: str | None
        tone: str | None
        length: str | None
        sentiment: str | None
    input_text: str | None
```

**Important:**
These constraints are copied from the outer supervisor.
The inner supervisor cannot override them.

---

## 4. Inner Supervisor (Writer Level)

### Scope

> The inner supervisor completes **exactly one section**.

It:

* does not know the full document
* does not know future sections
* does not alter structure
* does not invent constraints

---

### Inputs

```python
WriterSupervisorRequest:
    section:
        section_id: str
        title: str
        intent: str
    operation: "draft" | "refine"
    constraints:
        topic: str
        audience: str | None
        tone: str | None
        length: str | None
        sentiment: str | None
    input_text: str | None
```

---

### Outputs

```python
WriterSupervisorResponse:
    section_id: str
    text: str
    decision: ACCEPT | REJECT
    feedback: str | None
```

---

### Invariants

* Inner supervisor:

  * **must obey** all provided constraints
  * **must not** invent audience, tone, or sentiment
  * **must not** reference other sections
* One request → one section → one result

---

## 5. Execution Model (Caller-Driven)

The caller (not a supervisor) orchestrates:

```text
for task in outer_response.tasks:
    if task is StructureTask:
        apply_structure_change(task)
    else if task is WriterTask:
        run_inner_supervisor(task)
```

### Critical rule

> A section removed by a `StructureTask` **must never** appear in a `WriterTask`.

---

## 6. Iteration Semantics (Second Pass and Beyond)

On iteration ≥ 2:

* Outer supervisor sees:

  * updated structure
  * content summaries (not raw text)
* It may:

  * remove sections
  * split or merge based on content quality
  * re-issue writer tasks with `refine`

**No implicit carry-over is allowed.**
Everything is explicit.

---

## 7. Sentiment, Audience, Length — Final Rules

| Constraint | Who decides | Who enforces |
| ---------- | ----------- | ------------ |
| Topic      | Outer       | Inner        |
| Audience   | Outer       | Inner        |
| Tone       | Outer       | Inner        |
| Length     | Outer       | Inner        |
| Sentiment  | Outer       | Inner        |
| Structure  | Outer       | N/A          |
| Content    | Inner       | Critic       |

The inner writer is **less flexible by design**.

---

## 8. Why This Holds

This design guarantees:

* Deterministic execution
* Replayability
* No hallucinated structure
* No silent content loss
* Clear audit trail

It also matches your existing **SupervisorRequest / SupervisorResponse** pattern exactly — just applied twice.

---

## Final Answer to the Question

> *“What about sentiment, audience, length, etc…?”*

They are **global constraints**:

* owned by the **outer supervisor**
* injected read-only into every inner request
* never decided by the writer
* never changed mid-section

This preserves authority **and** composability.
