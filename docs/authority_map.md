# Authority Map

## Core Principle
Control is intentionally distributed. No single component is in charge of the entire system. Authority is constrained by explicit contracts, not by perceived intelligence or initiative.

## Component Authority Table

| Component            | May Decide Tasks         | May Loop                | May Execute            | May Reject | May Terminate |
|----------------------|--------------------------|-------------------------|------------------------|------------|---------------|
| Document Planner     | ✓                        | ✓ (structural)          | ✗                      | ✗          | ✗             |
| Writer Planner       | ✓ (local)                | ✓ (local)               | ✗                      | ✗          | ✗             |
| Writer Worker        | ✗                        | ✗                       | ✓                      | ✗          | ✗             |
| Critic               | ✗                        | ✗                       | ✗                      | ✓          | ✗             |
| Controller           | ✗                        | ✗                       | ✓ (single-pass)        | ✗          | ✗             |
| Dispatcher / App     | ✗                        | ✓                       | ✗                      | ✗          | ✓             |

- Loops (retries, orchestration) are external application concerns, never internal agent loops.
- Execution is atomic per call.
- Rejection does not grant retry authority; retries belong to the orchestrator.

## Forbidden Behaviors (Hard Rules)
- Controllers MUST NOT loop or own retry policy.
- Writers (planner/worker/critic) MUST NOT invent or modify document structure.
- Planners MUST NOT execute tasks or call tools.
- Critics MUST NOT modify content or structure; they only judge.
- Workers MUST NOT terminate runs or decide routing.

## Why This Exists
High-speed agentic development makes authority drift easy. Clear boundaries prevent accidental “intelligence creep” and unintended control shifts. This map protects maintainers, not the model.

## How to Use This Document
Consult this map when adding domains, registering tools, designing controller generators, or refactoring planners/critics. Any change to authority must align with these constraints.
