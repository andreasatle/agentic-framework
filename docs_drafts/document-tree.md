Good. Then we switch **out of philosophy** and back into **controlled execution**, without pretending the exploration didn’t matter.

Below is a **clean, ordered task list** for the **Document Tree** work, written to preserve optionality and avoid premature lock-in.

No decisions are smuggled in. Each task is atomic.

---

## Phase D — Document Structure (Tree-first, content-agnostic)

### **D1 — Introduce DocumentNode (no behavior)**

**Goal:** Define the structural unit.

Create:

* `DocumentNode`

  * `id: str` (stable, opaque)
  * `title: str`
  * `description: str`  ← semantic obligation for writers
  * `children: list[DocumentNode]`

Constraints:

* No content field
* No state flags
* No methods beyond validation
* Pure data

---

### **D2 — Replace DocumentState with DocumentTree**

**Goal:** Make structure explicit and future-proof.

Actions:

* Remove `DocumentState`
* Introduce `DocumentTree`

  * `root: DocumentNode`
* Update document planner input/output schemas accordingly

Constraints:

* Tree is immutable per supervisor call
* No mutation helpers
* No persistence

---

### **D3 — Update DocumentPlanner contracts**

**Goal:** Make planners operate on structure, not sections.

Actions:

* Planner input sees:

  * `document_tree: DocumentTree | None`
* Planner output emits:

  * `DocumentTask` that *transforms* a tree
    (init / split / merge / reorder / delete)

Constraints:

* Planner does **not** emit writer tasks
* Planner does **not** apply transformations
* Planner outputs intent only

---

### **D4 — Define tree transformation semantics**

**Goal:** Make structural intent explicit and inspectable.

Actions:

* Tighten `DocumentTask` schema:

  * Each `op` declares:

    * required fields
    * legal targets
* No implicit behavior

Constraints:

* Application code applies transformations
* Supervisor remains single-shot

---

### **D5 — Introduce ContentStore (outside supervisors)**

**Goal:** Separate obligation from fulfillment.

Create:

* `ContentStore`

  * `by_node_id: dict[str, str]`

Constraints:

* Not passed to supervisors
* Not visible to planners
* Writers receive only:

  * `node_id`
  * `description`
  * requirements

---

### **D6 — Define WriterTask emission rule (application-level)**

**Goal:** Decide *when* writing happens.

Specify (no code yet):

* Given:

  * `DocumentTree`
  * `ContentStore`
* Emit `DraftSectionTask` for:

  * nodes with no content
  * based on traversal policy (DFS/BFS/explicit)

Constraints:

* This logic lives **outside** supervisors
* No automation yet — just define the rule

---

### **D7 — Align WriterCritic to node.description**

**Goal:** Make evaluation semantic, not procedural.

Actions:

* Critic checks:

  * text satisfies `DocumentNode.description`
  * scope matches node
* No structural knowledge beyond the node

---

### **D8 — Remove all remaining domain_state references**

**Goal:** Finish the cleanup.

Actions:

* Delete:

  * `DomainStateProtocol`
  * `StatelessProblemState`
  * `LoadSaveMixin` usage in document path
* Update docs + tests accordingly

---

## Important meta-rule (do not violate)

Until **D4** is complete:

* Do **not** optimize writer behavior
* Do **not** add persistence
* Do **not** introduce iteration

Structure first. Behavior later.

---

## Your move

Pick **one**:

* Start with **D1** (pure modeling)
* Start with **D2** (replace existing state)
* Start with **D3** (planner semantics)

Say the task ID.

I’ll respond with **one** Codex-ready prompt for exactly that task.
