Understood. I will be **deliberate, structured, and non-compressing**.
Below is a **direct conversion** of the task plan into **actionable sections**, each with:

1. **Description** (what/why, no implementation drift)
2. **Codex prompt** (long-form, explicit, constraint-heavy, suitable for copy–paste)
3. **Commit message** (precise, future-proof)

No abstraction creep, no controller changes unless explicitly stated.

---

# D1 — Fix Document Planner `init` Contract

## 1) Description

The document analysis pipeline currently fails because the **document planner emits an invalid `DocumentTask`** for `op="init"`.

The domain contract is authoritative:

* `DocumentTask(op="init")` **requires** `parameters.root`
* `parameters.root` **must be a `DocumentNode`**
* Emitting `parameters.sections` is invalid and must stop

This is not a runtime bug; it is a **planner prompt mismatch**.

The goal of this step is to:

* Make the planner emit a **fully-formed `DocumentNode` tree**
* Keep all schemas, controllers, and dispatchers unchanged
* Enforce structure *before* execution

This step is **blocking** for all downstream work.

---

## 2) Codex Prompt

```
You are fixing a contract violation in the document planner.

AUTHORITATIVE CONSTRAINTS (DO NOT VIOLATE):
- DO NOT modify DocumentTask
- DO NOT modify DocumentNode
- DO NOT modify AnalysisController
- DO NOT modify AgentDispatcher
- DO NOT weaken schema validation
- This is a PROMPT-ONLY change

PROBLEM:
The document planner currently emits this invalid shape for op="init":

{
  "op": "init",
  "parameters": {
    "sections": [...]
  }
}

This violates the DocumentTask contract.

REQUIRED CONTRACT:
For op="init", the planner MUST emit:

{
  "op": "init",
  "target": null,
  "parameters": {
    "root": DocumentNode
  }
}

Where DocumentNode is defined as:
- id: str (stable, opaque)
- title: str
- description: str
- children: list[DocumentNode]

TASK:
Update the document planner system prompt so that:

1. For op="init":
   - The planner emits a complete DocumentNode tree
   - parameters.sections MUST NOT appear
   - parameters.root MUST always be present

2. The root node:
   - title: overall document title
   - description: overall document purpose
   - children: list of section nodes

3. Each child section node:
   - title: section title
   - description: what the section should cover semantically
   - children: empty list (for now)

4. The prompt MUST:
   - Explicitly describe the DocumentNode schema
   - Explicitly state that emitting sections without a root is invalid
   - Include a JSON example of a valid op="init" payload

FILES TO MODIFY:
- src/domain/document/planner.py (planner prompt only)

EXPECTED RESULT:
- document-planner emits valid DocumentTask
- agentic-document runs without retries
- No schema or controller changes
```

---

## 3) Commit Message

```
Fix document planner init output to emit DocumentNode root

Enforce DocumentTask init contract by updating planner prompt to
emit parameters.root as a DocumentNode tree instead of a sections list.
No schema, controller, or dispatcher changes.
```

---

# D2 — Declare DocumentTree as Analysis Output

## 1) Description

Document analysis currently produces a `DocumentTask` but does not expose a **stable, explicit analysis result**.

We introduce a **pure data wrapper** (`DocumentTree`) to:

* Make the analysis output explicit
* Provide a stable handoff boundary to the writer
* Avoid leaking planner or task semantics downstream

This step adds **structure only**, no behavior.

---

## 2) Codex Prompt

```
You are introducing an explicit analysis output type for the document domain.

CONSTRAINTS:
- DO NOT add behavior or traversal logic
- DO NOT modify Controller or Dispatcher
- DO NOT introduce mutation helpers
- This is a data-modeling change only

TASK:
1. Introduce a new Pydantic model:

   class DocumentTree(BaseModel):
       root: DocumentNode

2. Ensure:
   - DocumentTree is used as the return type of document analysis
   - Analysis APIs return DocumentTree, not raw tasks or planner outputs
   - DocumentNode remains unchanged

3. No logic should be added to DocumentTree
   - No methods
   - No validation beyond schema

FILES TO MODIFY (as needed):
- src/domain/document/types.py
- src/domain/document/api.py
- Any analysis return typing

EXPECTED RESULT:
- Document analysis produces a DocumentTree
- Writer domain can consume it without planner knowledge
```

---

## 3) Commit Message

```
Introduce DocumentTree as explicit document analysis output

Add a pure data wrapper for document structure to stabilize
analysis-to-writer handoff without adding behavior.
```

---

# D3 — Freeze Writer Domain Inputs

## 1) Description

Before implementing writer logic, we **freeze the writer’s input contract**.

The writer must:

* Consume structure (`DocumentTree`)
* Consume accumulated content (`ContentStore`)
* Never receive planner state, document nodes, or analysis artifacts inside tasks

This prevents semantic bleed and future rewrites.

---

## 2) Codex Prompt

```
You are freezing the writer domain input contract.

CONSTRAINTS:
- DO NOT change controller behavior
- DO NOT add traversal logic
- DO NOT embed DocumentNode in writer tasks

TASK:
1. Ensure writer domain inputs are strictly:
   - DocumentTree
   - ContentStore

2. Ensure WriterTask variants:
   - Refer to sections ONLY by node id
   - Do NOT contain DocumentNode or children
   - Do NOT carry structural data

3. Enforce via schema validation where possible.

FILES TO MODIFY:
- src/domain/writer/types.py
- src/domain/writer/schemas.py (if needed)

EXPECTED RESULT:
- Writer tasks are structure-agnostic
- Structure lives exclusively in DocumentTree
```

---

## 3) Commit Message

```
Freeze writer input contract to DocumentTree and ContentStore

Prevent structural data from leaking into writer tasks by
enforcing node-id-only references.
```

---

# D4 — Implement Writer Task Emission (Pure)

## 1) Description

This is the **bridge** between document analysis and writer execution.

We implement **pure, deterministic task emission**:

* No controllers
* No LLM calls
* No mutation
* No retries

This is where convergence logic begins.

---

## 2) Codex Prompt

```
You are implementing pure writer task emission logic.

CONSTRAINTS:
- No controller calls
- No LLM calls
- No side effects
- Deterministic output

TASK:
1. Implement a function:

   emit_writer_tasks(
       tree: DocumentTree,
       store: ContentStore
   ) -> list[WriterTask]

2. Rules:
   - Traverse DocumentTree in preorder
   - For each node:
     - If no content exists in ContentStore → emit DraftSectionTask
     - If content exists and refinement is allowed → emit RefineSectionTask

3. WriterTask must include:
   - node_id
   - purpose / requirements
   - NO structure

FILES TO MODIFY:
- src/domain/writer/emission.py (or equivalent)

EXPECTED RESULT:
- Given empty store → N draft tasks
- Given partial store → mix of draft/refine tasks
- Fully testable without controllers
```

---

## 3) Commit Message

```
Add pure writer task emission from DocumentTree and ContentStore

Introduce deterministic traversal-based task emission with no
controllers or side effects.
```

---

# D5 — Execute Writer Tasks in Batches (Outer Loop)

## 1) Description

Execution happens **outside** the controller.

The controller remains single-pass; the application code owns:

* batching
* retries
* convergence

This is intentional.

---

## 2) Codex Prompt

```
You are wiring writer task execution in application code.

CONSTRAINTS:
- DO NOT modify Controller
- DO NOT add loops inside Controller
- All iteration happens in app code

TASK:
1. In writer application logic:
   - Emit writer tasks
   - For each task:
     - Invoke writer controller once
     - On ACCEPT → write to ContentStore
     - On REJECT → emit refine task (bounded)

2. Ensure:
   - No state inside Controller
   - ContentStore is updated only in app code

FILES TO MODIFY:
- src/domain/writer/main.py
- src/domain/writer/api.py

EXPECTED RESULT:
- Full document drafted after finite passes
```

---

## 3) Commit Message

```
Execute writer tasks in bounded outer loop using controller

Move batching and convergence logic into application code
while keeping controller single-pass.
```

---

# D6 — Convergence and Stop

## 1) Description

We **explicitly stop** once:

* No new writer tasks are emitted

No optimization, no abstraction.

---

## 2) Codex Prompt

```
You are adding a convergence condition to the writer pipeline.

TASK:
1. Detect when emit_writer_tasks returns an empty list
2. Stop execution
3. Log final DocumentTree + ContentStore

CONSTRAINTS:
- No retries beyond bounds
- No new abstractions

EXPECTED RESULT:
- Writer pipeline terminates cleanly
- Final content is stable
```

---

## 3) Commit Message

```
Add explicit convergence condition to document writer pipeline

Stop execution when no further writer tasks are emitted.
```

---

### Final note (important)

This plan is **intentionally finite**.
When D6 is done, you stop — *even if ideas remain*.

That’s how you avoid derail.

If you want, next we can:

* Start with **D1 Codex execution only**
* Or mark these as a checklist in a roadmap doc

Just say the word.
