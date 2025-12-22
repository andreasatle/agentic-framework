Yes. Below is a **clean, minimal, explicit plan** to make the writer **fully stateless**, aligned with what you just concluded.

No prose, no options, no ambiguity.

---

## Goal (non-negotiable)

**Writer domain becomes a pure execution unit**:

* accepts a `WriterTask`
* returns a `WriterResult`
* has **zero knowledge** of:

  * document structure
  * section ordering
  * accumulated content
  * persistence
* planner is a **router only**
* all document concerns move out

---

## Target end-state (definition)

**Writer sees only:**

```text
DraftSectionTask | RefineSectionTask → WriterResult
```

**Document layer owns:**

* structure
* content
* section order
* draft vs refine decision
* state transitions

---

# Task batch: “Make writer stateless”

### **WS1 — Remove WriterDomainState from writer domain**

**What**

* Delete `WriterDomainState`
* Remove all references to it from:

  * writer schemas
  * writer API
  * writer planner input
  * supervisor wiring

**Why**

* It is document state, not writer state.

**Codex prompt**

```
Remove WriterDomainState entirely from the writer domain.

Steps:
1. Delete WriterDomainState definition.
2. Remove WriterDomainState imports/usages from:
   - domain/writer/schemas.py
   - domain/writer/api.py
   - domain/writer/planner.py
   - domain/writer/main.py
3. Ensure writer planner input no longer accepts any domain or project state.
4. Adjust types so writer operates only on WriterTask → WriterResult.

Do not modify supervisor or document domain.
```

**Commit message**

```
Remove WriterDomainState to make writer stateless
```

---

### **WS2 — Make WriterPlanner a pure router**

**What**

* Planner:

  * accepts a `WriterTask`
  * returns `{ task, worker_id }`
* No validation against structure
* No state inspection
* No inference

**Why**

* Planner is not a decision maker anymore.

**Codex prompt**

```
Simplify WriterPlanner to a pure router.

Steps:
1. Update planner input schema to accept only WriterTask.
2. Remove all logic inspecting structure or state.
3. Planner must:
   - validate task schema only
   - emit exactly one task unchanged
   - select worker_id based on task kind:
       - draft_section → draft worker
       - refine_section → refine worker
4. Planner must not fail based on document concerns.

Do not modify worker logic.
```

**Commit message**

```
Convert writer planner into pure task router
```

---

### **WS3 — Split writer workers explicitly (draft vs refine)**

**What**

* Two workers:

  * `writer-draft`
  * `writer-refine`
* Each with:

  * its own prompt
  * its own input schema
* No branching inside workers

**Why**

* No mode flags
* No shared logic
* Tight prompts

**Codex prompt**

```
Split writer worker into two explicit workers.

Steps:
1. Create separate worker implementations:
   - DraftSectionWorker
   - RefineSectionWorker
2. Each worker:
   - accepts only its specific task type
   - rejects any other input
3. Remove any conditional logic based on task kind.
4. Register workers with dispatcher under distinct IDs.

Do not change planner routing logic beyond worker_id selection.
```

**Commit message**

```
Split writer into draft and refine workers
```

---

### **WS4 — Move all document logic out of writer API**

**What**

* Writer `run()`:

  * no longer accepts domain/document state
  * only takes:

    * task
    * dispatcher
    * tool registry
* No persistence
* No structure handling

**Why**

* Writer is not an application.

**Codex prompt**

```
Strip writer API down to pure task execution.

Steps:
1. Update writer run() signature to accept only:
   - task
   - dispatcher
   - tool_registry
2. Remove any document orchestration logic.
3. Ensure run() executes exactly one supervisor cycle.
4. Return raw supervisor result.

Do not introduce new abstractions.
```

**Commit message**

```
Remove document logic from writer API
```

---

### **WS5 — Enforce statelessness with tests**

**What**
Add tests asserting:

* writer does not accept state
* workers reject unexpected fields
* planner never inspects structure
* writer can run without any document context

**Codex prompt**

```
Add tests enforcing writer statelessness.

Add tests that assert:
1. Writer workers reject any state-like fields.
2. Writer planner accepts only WriterTask.
3. Writer execution succeeds with no document state.
4. No writer component imports document-layer code.

Tests must fail if state is reintroduced.
```

**Commit message**

```
Add tests enforcing stateless writer invariants
```

---

## Sanity check (answering your concern)

> “Is this another thing that will fail?”

No — because now:

* **Writer is dumb**
* **Document layer is smart**
* **LLMs are minimized**
* **Responsibilities are atomic**

This architecture is *stable*, because:

* nothing “helpful” is allowed
* nothing implicit exists
* nothing is shared accidentally

You are no longer building a clever system —
you are building a **controllable one**.

If you want, next step after this:

* validate the document layer design *before* writing code
