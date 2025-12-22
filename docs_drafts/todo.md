Below is a **single, copy-paste Codex execution prompt** to clean up the remaining inconsistencies **without altering architecture or semantics**.

This prompt is surgical, test-driven, and aligned with your constraints.

---

### **CODEX EXECUTION PROMPT — CLEANUP PASS (NO ARCHITECTURAL CHANGES)**

You are modifying an existing multi-agent framework.
The architecture is **frozen**.
Your task is to **eliminate remaining inconsistencies, legacy artifacts, and interface mismatches** so that all tests pass and naming is internally consistent.

#### **STRICT CONSTRAINTS**

* ❌ Do NOT introduce new abstractions
* ❌ Do NOT add new state or workflow logic
* ❌ Do NOT change Supervisor semantics
* ❌ Do NOT invent new fields or schemas
* ❌ Do NOT re-introduce removed “meta” state
* ✅ Fix only mismatches, stale names, and broken call sites
* ✅ Prefer minimal diffs
* ✅ Tests are the oracle

---

### **PRIMARY ISSUES TO FIX**

#### **1. AgentDispatcher constructor mismatch**

Tests and call sites previously passed `domain_name=...` to `AgentDispatcher`.
That parameter no longer exists.

**Action**

* Remove `domain_name` from all `AgentDispatcher(...)` instantiations
* Do NOT add it back
* Ensure all dispatcher factories (`make_agent_dispatcher`) align with the current constructor signature

---

#### **2. Supervisor protocol drift**

`Supervisor` is now callable via `__call__`, but some protocol references still expect `.handle(...)`.

**Action**

* Update `SupervisorProtocol` to match the callable interface:

  ```python
  def __call__(self, request: SupervisorRequest) -> SupervisorResponse
  ```
* Do NOT add alias methods
* Do NOT reintroduce `handle`

---

#### **3. Remove dead ProjectState expectations**

Some tests and legacy paths still expect:

```python
response["project_state"]
```

or similar artifacts.

**Action**

* Remove any remaining expectations of `project_state` from:

  * tests
  * supervisor responses
  * trace entries
* SupervisorResponse must remain:

  * immutable
  * serializable
  * domain-agnostic

---

#### **4. Naming consistency audit**

Ensure naming is consistent across:

* `SupervisorRequest`
* `SupervisorResponse`
* `SupervisorDomainInput`
* Dispatcher methods (`plan`, `work`, `critique`)

**Rules**

* “task” means **domain task**
* “plan” means **planner output**
* “worker_output” is the **WorkerOutput**
* “decision” is **Critic output**
* No “meta”, no “iteration”, no “project_state”

Fix mismatches only if they cause ambiguity or test failures.

---

#### **5. Writer domain correctness**

Ensure writer semantics are **idempotent and append-safe**:

* `refine` appends exactly once
* `draft` replaces only if empty
* No duplicate section writes
* No planner bypass
* No manual task injection

Fix only what tests flag.

---

### **VALIDATION**

After changes:

* `pytest` must pass with zero failures
* No new warnings introduced
* No unused imports
* No legacy compatibility shims

---

### **OUTPUT**

* Modify files in place
* Do NOT explain changes
* Do NOT add comments
* Produce only code diffs

---

If you want next:

* a **commit message**
* a **post-cleanup invariants checklist**
* or a **“what remains dangerous” review**

say so explicitly.
