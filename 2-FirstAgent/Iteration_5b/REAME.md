# Iteration 5b – Built-in Tools Takeover

**Goal:** Learn tool orchestration without ambiguity, with minimal schema overhead.

**What changed from 5a:**

* I **removed my custom tool schema layer** and switched to **built-in OpenAI tool calling**
* Arithmetic is no longer computed or validated via hand-rolled dictionaries
* The Supervisor routes directly between trusted `Task → tool.run() → Result → Critic`, with **zero meta-plumbing**
* The payload surface is strictly **JSON + clean semantic types**, no free-floating dictionaries
* Less boilerplate, fewer failure modes, clearer control plane

---

## Why switch to built-in tools?

* Eliminated redundant validation layer I had built “just in case”
* No need for equality or disambiguation helpers for arithmetic
* No need for tool call wrappers or namespace branching logic
* No need for string parsing of tool outputs – the Supervisor receives well-typed objects directly
* Faster iteration and easier mental model alignment

---

## Lessons learned

1. **Type clarity beats tool generality** when learning orchestration
2. **Built-in tools are simpler, but not more powerful** – they just remove scaffolding
3. **Agents remain untrusted** – Supervisor is the only trusted layer
4. Fewer dictionaries = **fewer derailment vectors**
5. When the task space is atomic arithmetic, **custom tools add cost/errors instead of value**
6. This switch validates the chaining contract:

   ```
   validated_input_json → LLM → tool invocation → validated_output_json
   ```

---

## Current control flow

```
Planner emits:     Task
Supervisor calls:  compute(...)
Worker emits:      Result  OR  ToolRequest (1st turn)
Supervisor loops → Critic judges: Decision
Supervisor halts when ACCEPT
```

---

## Known constraints (by design)

* One single branch must be emitted at a time (`Result` or `ToolRequest`)
* Arithmetic Operations constrained to: `"ADD" | "SUB" | "MUL"`
* Operands constrained to: `1 ≤ a,b ≤ 20`
* Results constrained to: `-10,000 ≤ value ≤ 10,000`
* All outputs must be valid JSON objects (`json_object` only)

---

## What will break if changed incorrectly?

| Change                            | Breaks                                       |
| --------------------------------- | -------------------------------------------- |
| Return non-JSON                   | Supervisor `model_validate_json` throws      |
| Emit both result and tool_request | `WorkerOutput.exactly_one_branch` throws     |
| Change op/a/b in retries          | Critic recompute mismatch loop errors        |
| Unknown tool_name                 | Supervisor routing failure                   |
| Reject without feedback           | `Decision.require_feedback_on_reject` throws |

