# Domain Graduation Rule: Atomic → Structured

## Definition

A domain **graduates from Atomic to Structured** when **task execution correctness depends on an explicit, persistent structure that cannot be safely inferred within a single supervisor run**.

---

## Atomic Domain (No Structure Supervisor)

A domain is **Atomic** if **all** of the following are true:

1. **Single-shot correctness**

   * One Supervisor execution produces a complete, valid result

2. **No partial completion**

   * There is no meaningful “half-done” state that must be resumed

3. **Order independence**

   * Tasks do not depend on a global ordering or hierarchy

4. **Non-destructive execution**

   * No task requires removal, merging, or splitting of prior results

5. **Local decision sufficiency**

   * All decisions can be made using only the current request and response

### Examples

* Arithmetic
* Sentiment classification
* Simple extraction
* Single function generation

**Rule:**

> Atomic domains use exactly **one supervisor**, forever.

---

## Structured Domain (Requires Structure Supervisor)

A domain is **Structured** if **any one** of the following is true:

### S1 — Persistent structure exists

* The domain has an outline, plan, DAG, hierarchy, or file layout
* Structure must persist across multiple executions

---

### S2 — Partial completion is meaningful

* Work can be paused and resumed
* “Incomplete but valid” states exist

---

### S3 — Execution order matters

* Tasks must run in a specific sequence
* Reordering tasks changes correctness

---

### S4 — Destructive edits are required

* Sections, files, or components can be:

  * removed
  * split
  * merged
  * reordered

---

### S5 — Global constraints exist

* Audience, tone, length, compliance rules, or architecture
* These constraints apply across multiple tasks

---

### S6 — Decisions exceed one task

* Whether to continue, stop, revise, or restructure
* Requires reasoning over multiple prior results

**Rule:**

> If **any** of S1–S6 is true, the domain **must** graduate to Structured.

---

## Graduation Consequences (Mandatory)

When a domain becomes Structured:

1. **Two supervisors are required**

   * Outer: structure & task planning
   * Inner: deterministic execution of one task

2. **Structure ownership moves outward**

   * Inner supervisor may not invent or mutate structure

3. **Iteration moves to the caller**

   * Supervisors remain single-execution units

4. **SupervisorResponse remains immutable**

   * All state changes are explicit events

---

## Canonical Examples

| Domain         | Graduation Reason |
| -------------- | ----------------- |
| Writer         | S1, S2, S4, S5    |
| Coder (large)  | S1, S3, S4        |
| Research paper | S1, S2, S5        |
| Legal contract | S1, S4, S5        |
| Arithmetic     | none              |
| Sentiment      | none              |

---

## Non-Negotiable Rule

> **Structure must exist outside the inner supervisor before correctness depends on it.**

Violating this rule causes:

* hidden authority leaks
* irreproducible behavior
* non-replayable execution

---

## One-Line Test (Put This in Your Head)

> *If correctness cannot be judged from a single SupervisorResponse, the domain is Structured.*

---

## Status of Your Current Domains

| Domain          | Classification   |
| --------------- | ---------------- |
| Arithmetic      | Atomic           |
| Sentiment       | Atomic           |
| Writer          | Structured       |
| Coder (current) | Atomic (for now) |
| Coder (future)  | Structured       |

---
---
---

# Writer System — Structural Skeleton Specification

## 0. Design Principle (Non-Negotiable)

* **Outer layer owns structure**
* **Inner layer owns execution of exactly one task**
* **No layer mutates state it does not own**
* **All communication is request/response**
* **All responses are immutable events**

---

## 1. Core Domain Objects

### Document (authoritative artifact)

```python
class Document(BaseModel):
    id: str
    structure: DocumentStructure
    content: DocumentContent
    metadata: DocumentMetadata
```

* Exists across iterations
* Never partially mutated
* Replaced via functional updates

---

### DocumentStructure (outer authority)

```python
class DocumentStructure(BaseModel):
    sections: list[SectionSpec]
```

```python
class SectionSpec(BaseModel):
    section_id: str
    title: str
    intent: str
    constraints: list[str]
```

Properties:

* Order matters
* IDs are stable
* Titles and intent are authoritative
* Constraints are **binding** on the inner writer

---

### DocumentContent (inner result aggregation)

```python
class DocumentContent(BaseModel):
    sections: dict[str, str]  # section_id → text
```

Rules:

* Missing section_id = not yet written
* Inner writer only produces content for **one** section_id

---

### DocumentMetadata (cross-cutting, read-only to inner)

```python
class DocumentMetadata(BaseModel):
    topic: str | None
    audience: str | None
    tone: str | None
    length: str | None
```

* Set once (CLI / user / outer loop)
* Never modified by inner writer

---

## 2. Outer Supervisor (Structure Authority)

### Outer Request

```python
class StructureSupervisorRequest(BaseModel):
    document: Document
```

### Outer Response (Immutable Event)

```python
class StructureSupervisorResponse(BaseModel):
    decision: Literal["NO_CHANGE", "STRUCTURE_UPDATED"]
    operations: list[StructureOperation]
```

---

### Structure Operations (Only outer may emit)

```python
class StructureOperation(BaseModel):
    op: Literal["ADD", "REMOVE", "SPLIT", "MERGE", "REORDER"]
    payload: dict
```

Examples:

* ADD → new SectionSpec
* REMOVE → section_id
* SPLIT → section_id → [new SectionSpec…]
* MERGE → [section_id…] → new SectionSpec

**Important**:

* These operations modify *structure only*
* They do **not** invoke inner execution directly

---

## 3. Task Derivation (Pure Function)

After structure is finalized for an iteration:

```python
def derive_tasks(
    structure: DocumentStructure,
    content: DocumentContent
) -> list[WriterTask]:
    ...
```

Rule:

* One task per section **missing or marked incomplete**
* Order strictly follows `structure.sections`

---

## 4. Inner Writer Supervisor (Execution Authority)

### Inner Request (Single Task)

```python
class WriterTask(BaseModel):
    section_id: str
    title: str
    intent: str
    constraints: list[str]
```

```python
class WriterSupervisorRequest(BaseModel):
    task: WriterTask
    document_snapshot: DocumentSnapshot
```

```python
class DocumentSnapshot(BaseModel):
    structure: DocumentStructure
    metadata: DocumentMetadata
    existing_text: str | None
```

Rules:

* Snapshot is **read-only**
* Inner writer sees *context*, not authority

---

### Inner Response (Exactly One Section)

```python
class WriterSupervisorResponse(BaseModel):
    section_id: str
    text: str
```

Rules:

* No structural info
* No suggested changes
* No cross-section output

---

## 5. Integration Loop (Orchestration, Not a Supervisor)

This is **not** a supervisor — just deterministic control flow.

```python
def writer_pipeline(document: Document) -> Document:
    # 1. outer structure pass
    structure_event = structure_supervisor(document)

    document = apply_structure_ops(document, structure_event)

    # 2. derive tasks
    tasks = derive_tasks(document.structure, document.content)

    # 3. inner execution loop
    for task in tasks:
        response = writer_supervisor(
            WriterSupervisorRequest(
                task=task,
                document_snapshot=make_snapshot(document, task)
            )
        )
        document = apply_content_update(document, response)

    return document
```

Key property:

* **Outer and inner never call each other**
* The loop coordinates them, not the supervisors

---

## 6. Authority Matrix (Hard Boundary)

| Concern           | Owner                       |
| ----------------- | --------------------------- |
| Section existence | Outer                       |
| Section order     | Outer                       |
| Section intent    | Outer                       |
| Content text      | Inner                       |
| Tone / audience   | Metadata (read-only)        |
| Split / merge     | Outer                       |
| Remove section    | Outer (no inner call)       |
| Rewrite text      | Inner (only if task issued) |

---

## 7. What This Buys You

* You **do not lose** the 20 writer hardening tasks
* They now apply **cleanly to the inner supervisor**
* The outer supervisor is a *new capability*, not a rewrite
* Domains like coder/sentiment remain valid — they simply lack an outer layer

---

## 8. Graduation Rule (Formal)

A domain **graduates to structured** when:

> Tasks have identity, ordering, and lifecycle beyond a single execution.

Arithmetic: ❌
Sentiment: ❌
Coder (future): ⚠️
Writer: ✅

---

## 9. What We Do *Next* (One Choice Only)

You should pick **one**:

1. Formalize `StructureOperation` schemas
2. Define `derive_tasks()` rules precisely
3. Lock the `DocumentSnapshot` contract
4. Map existing writer code → inner supervisor only

Say the number.
