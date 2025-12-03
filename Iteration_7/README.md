## Iteration 7 — Stable Boundaries, Heterogeneous Tools

### Goal

Evolve the swarm **in-place** from demo tasks to workflows that can:

* **dispatch ≥1 heterogeneous tools via a registry**, not direct calls
* maintain **Supervisor as single orchestration authority**
* maintain **ToolRegistry as tool-vocabulary + arg-schema owner**
* treat **ToolProtocol as static callability contract**, enforced at registration boundaries only
* keep **agents blind to tool internals and ambient failure taxonomy**

### Current state

We moved from:

* Iteration 5: Tool logic co-located with provider-specific agent/toolbox
* Iteration 6: Validation responsibility briefly experimented inside agents, but reverted for hygiene

Now we have:

* `Worker` **declares tool calls** (`tool_name + args`), never executes them
* `Supervisor` **validates output**, routes decisions, **executes tools exactly once**
* Tools return `Result` objects directly for clarity
* `ToolRegistry` encapsulates call shape and schema ownership
* Old iterations are **frozen snapshots** for tracking, not runtime branching

### Architecture contracts

| Component    | Responsibility                                                                      |
| ------------ | ----------------------------------------------------------------------------------- |
| Planner      | Produce `Task` (bounded plan)                                                       |
| Worker       | Produce `Result` or `ToolRequest`                                                   |
| Critic       | Produce `Decision` (`ACCEPT/REJECT`)                                                |
| Supervisor   | Validate, route, retry, invoke tools via registry                                   |
| ToolRegistry | Store `(description, function, arg_type)` per tool                                  |
| ToolProtocol | Static contract `tool(args: BaseModel) -> BaseModel`, enforced at registration only |

### Decisions locked

* **Single validation boundary in Supervisor, single dispatch boundary in ToolRegistry**
* **No tuple indexing at system edges; prefer named unpacking/getters**
* **One failure signal object concept (future), not multiple tool taxonomies today**
* **No crypto/tool suggestion interference in this roadmap**

### Next steps (to iteration 8)

1. Add a **2nd heterogeneous tool in `tests/`** to surface potential boundary breaks early
2. Replace any **direct `compute(...)` calls in Supervisor** with **`registry.call(name, args)`**
3. Ensure `ToolRegistry.call()` does **one validation pass into correct args model**, then invokes via stored callable

### Success metric for iteration 7

The supervisor stays **readable and domain-agnostic** while tool signatures are enforced **only at registration time**, enabling smooth expansion later without refactoring orchestration logic.
