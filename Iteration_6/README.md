# Iteration 6 – Supervisor-controlled tools (vendor-neutral)

## Goals

- Move **tool execution** out of the Worker/Agent and into the **Supervisor**.
- Keep **tool selection** (whether to request a tool) as an LLM decision via prompt.
- Make all contracts **vendor-neutral**:
  - Worker never sees OpenAI-specific tool_call ids.
  - Worker only emits JSON-conformant `WorkerOutput`:
    - `{"tool_request": {...}}` **or**
    - `{"result": {...}}`
- Preserve the Iteration 5 behavior:
  - Planner proposes `Task`.
  - Worker may use a deterministic `compute` tool.
  - Critic checks arithmetic correctness.
  - Supervisor orchestrates bounded retries + refinement.

## Key changes vs Iteration 5b

- `schemas.py` now includes:
  - `ToolRequest`
  - `WorkerOutput` with `(result | tool_request)` + validator.
- `agents.py`:
  - No OpenAI `tools=` / function calling.
  - All agents use `response_format={"type": "json_object"}`.
  - Worker prompt describes the tool protocol in JSON, but never executes it.
- `supervisor.py`:
  - Detects `tool_request`, executes matching Python tool (`compute`), and injects `tool_result` into `WorkerInput`.
  - Only Supervisor touches real Python functions.
  - Critic path unchanged except for updated schemas.

## Running

```bash
uv run python -m Iteration_6.main
