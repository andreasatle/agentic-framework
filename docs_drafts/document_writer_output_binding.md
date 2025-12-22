# Writer Output Binding Contract

This contract defines how Writer outputs are bound to document structure, how identity is maintained, and who owns persistence. It is declarative only; no new behavior is introduced.

## A. Section Identity and Binding

- Every Writer output is bound to exactly one `DocumentNode.id`.
- `DocumentNode.id` is the sole authoritative key for section identity; titles are human-readable only.
- Writer output must never exist without a node binding.
- Binding is explicit, not positional and not inferred from ordering.

## B. Writer Output Semantics

- A Writer output is a complete textual realization of a single node in the originating `DocumentTree`.
- It is valid only in the context of that tree and that node id.
- Once accepted by the Critic, the output is treated as immutable for that attempt.
- Output is not incremental state, not a patch, and is unaware of sibling sections.

## C. Persistence Responsibility

- Writer does not persist output and does not assemble documents.
- Persistence and storage are owned by the application layer or higher-level orchestration.
- Writer correctness excludes persistence; binding stops at `{DocumentNode.id → text}` handoff.

## D. Document Assembly Semantics

- Final assembly is a pure function of:
  - The `DocumentTree`
  - A mapping `{DocumentNode.id → text}`
- Ordering derives solely from tree traversal; Writer has no authority over ordering or formatting.

## E. Explicit Non-Goals

- Writer does not track completion state.
- Writer does not decide when a document is “done”.
- Writer does not manage retries globally.
- Writer does not coordinate multi-node workflows.
