# Iteration 6 — **Explicit Control Plane with Built-in Tools**

## Core Goal

Build a **Supervisor-controlled multi-agent pipeline** where:

* **Inputs and outputs are clearly contracted in code** (imported from one stable `schemas` module).
* **The Supervisor owns the call graph** and decides:

  * Which agent to call
  * When to call tools
  * How to route tool results back into agents
  * When to stop looping (on ACCEPT)
* **Agents never decide the orchestration** (they only solve or request a tool, nothing more).
* **Minimal edits when schema changes** — if you edit a contract in `schemas`, it propagates everywhere by import, **no duplicated edits**.

---

## Specific Agent Responsibilities

### Planner

* Emit **1 single Task** describing a bounded arithmetic operation.
* Never call tools.
* Never explain outside JSON.
* Only job:
  `"" → LLM → {"op":"ADD|SUB|MUL","a":int,"b":int}`

### Worker

* Accept a Task + optional retry fields (`previous_result`, `feedback`, `tool_result`).
* **Always solve via the built-in compute tool** (never compute internally in the LLM).
* First emission MUST be a tool request:
  `{"tool_request":{"tool_name":"compute","task":{...}}}`
* After receiving tool result from Supervisor, emit:
  `{"result":{"value":Z}}`

### Critic

* Take a Task + Worker’s numeric Result.
* Recompute correctness using the built-in compute tool.
* Emit **1 deterministic Decision**:

  * `"ACCEPT"` if correct
  * `"REJECT"` + feedback if incorrect
* **Critic never loops or calls agents**, it just judges arithmetic correctness deterministically.

---

## Global Pipeline Constraints

* **Supervisor exclusively handles tool execution**.
* **Supervisor never trusts agent outputs until validated by Pydantic**.
* **Tool calls are never recursive from Worker/Critic** — recursion is only allowed if the Supervisor explicitly orchestrates it and knows the path of execution.
* **No accidental fan-out** — the pipeline must do exactly one thing per stage and stop when a result is ACCEPTed.
* **Everything is JSON objects, not Python dicts in prompts** — the LLM only sees JSON structures (`Task`, `Result`, `Decision`, `ToolRequest`), never arbitrary dictionaries.

---

## Success Criteria for Iteration 6

You will consider the iteration correct when:

1. You can modify `Task` or `Result` in `schemas.py` **only once**, and no other files need edits.
2. Worker and Critic **always use the built-in compute tool for arithmetic**, no internal reasoning on math.
3. Supervisor cleanly handles **tool routing and retries** without letting agents own orchestration.
4. Critic produces **deterministic decisions** instead of probabilistic ones.
5. Outputs and inputs stay **semantic + explicit** and *never ambiguous*.

---

### TL;DR (crisp elevator version)

* **Planner:** generate 1 bounded Task (no tools).
* **Worker:** always request `compute` first, emit result after tool_result.
* **Critic:** deterministically judge arithmetic correctness using `compute` again.
* **Supervisor:** owns orchestration and all tool execution, validates both agent output shape and logic, loops until ACCEPT or hits bound.

