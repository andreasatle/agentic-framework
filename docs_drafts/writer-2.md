
# **Next Phase Task Plan**

---

## **T1 — Lock the Execution Contract**

### Goal

Ensure the supervisor is a stable, replayable execution primitive.

---

### Codex Prompt

```
TASK:
Add minimal safety checks to lock the SupervisorResponse execution contract.

CONSTRAINTS:
- Do NOT change Supervisor behavior
- Do NOT refactor existing code
- This task adds tests or assertions only

INSTRUCTIONS:
1. Add a test that asserts:
   json.dumps(SupervisorResponse.model_dump()) always succeeds
2. Add a test that:
   - takes a stored SupervisorResponse
   - rehydrates domain state from response.project_state
   - does not rely on live Supervisor objects
3. Do NOT introduce mocks or new abstractions

SUCCESS CRITERIA:
- SupervisorResponse is always JSON-serializable
- Replay from stored event data is possible
```

---

### Commit Message

```
test(supervisor): lock SupervisorResponse serialization and replay invariants
```

---

## **T2 — Externalize Writer Structure as User-Owned Data**

### Goal

The user owns structure. The writer executes structure.

---

### Codex Prompt

```
TASK:
Make writer structure explicit, user-provided, and read-only during execution.

CONSTRAINTS:
- Do NOT introduce a second supervisor
- Do NOT improve writing quality
- Do NOT allow structure invention by the planner

INSTRUCTIONS:
1. Define a passive StructureState model (data-only)
2. Require StructureState to be provided in writer domain_state
3. Update the writer planner so it:
   - selects the next incomplete section
   - errors if structure is missing or exhausted
4. Ensure SupervisorResponse only emits structure update suggestions
5. Do NOT mutate structure inside the supervisor

SUCCESS CRITERIA:
- Writer executes only user-provided structure
- No implicit or invented outlines
- Structure ownership is external
```

---

### Commit Message

```
feat(writer): externalize article structure as user-owned domain state
```

---

## **T3 — Multi-Task Execution with a Single Supervisor**

### Goal

Run multiple tasks deterministically without supervisor nesting.

---

### Codex Prompt

```
TASK:
Enable deterministic multi-task execution using a single Supervisor.

CONSTRAINTS:
- Do NOT introduce supervisor nesting
- Do NOT add orchestration logic inside Supervisor

INSTRUCTIONS:
1. Extend the relevant domain state to support multiple tasks
2. Allow the caller to iterate tasks and invoke Supervisor per task
3. Ensure each SupervisorResponse represents exactly one task execution
4. Do NOT modify SupervisorProtocol

SUCCESS CRITERIA:
- Multiple tasks execute sequentially
- Each task produces a separate immutable event
- Supervisor remains single-task and stateless
```

---

### Commit Message

```
feat(domain): support sequential multi-task execution via caller loop
```

---

## **T4 — Introduce a Pure Structure Driver (No LLM)**

### Goal

Separate structure evolution from execution logic.

---

### Codex Prompt

```
TASK:
Extract structure evolution into a pure function.

CONSTRAINTS:
- Do NOT introduce a supervisor
- Do NOT call LLMs
- Do NOT add side effects

INSTRUCTIONS:
1. Define a pure function:
   next_structure(structure_state, supervisor_response) -> StructureState
2. Apply structure updates only via returned data
3. Ensure function is deterministic and testable

SUCCESS CRITERIA:
- Structure evolution is explicit and inspectable
- No execution logic leaks into structure policy
```

---

### Commit Message

```
feat(structure): introduce pure structure driver for state evolution
```

---

## **T5 — Decision Gate (No Code)**

### Goal

Decide whether a second supervisor is actually required.

---

### Codex Prompt

```
TASK:
Evaluate whether supervisor-over-supervisor composition is required.

INSTRUCTIONS:
1. Review current structure driver and multi-task execution
2. Identify concrete limitations
3. Decide explicitly whether a second supervisor is justified

SUCCESS CRITERIA:
- Clear yes/no decision
- No speculative abstraction added
```

---

### Commit Message

```
docs(roadmap): evaluate need for multi-level supervisor composition
```

---

## **Why this works**

* Each task is **atomic**
* Each has a **single Codex invocation**
* Each produces **one commit**
* You can stop after any task without architectural debt

If you want, next I can:

* reorder tasks for *shortest feedback loop*
* mark which are “one evening” vs “multi-day”
* collapse T2–T4 into a single experimental branch

Just tell me how aggressive you want to be.
