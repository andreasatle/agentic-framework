# Document–Writer Contract

This document defines the authoritative interface between the Document layer and the Writer layer. It is a protocol, not a tutorial.

## What Document guarantees to Writer

- **Complete structure**: A fully formed `DocumentTree` is provided before any writer work begins. Structure does not evolve mid-run.
- **Stable identifiers**: Every `DocumentNode.id` is present, unique within the tree, and stable for the duration of a writer run.
- **Section identity**: `DocumentNode.title` is a human-readable label for the section; it is not used for control flow.
- **Semantic obligation**: `DocumentNode.description` is the authoritative intent of the section and is the primary input to writer planning and critique.
- **Isolation**: Writer never sees partial or incrementally changing structure; the tree is immutable input for the run.

## What Writer guarantees to Document

- **One section per node**: Writer produces exactly one section output per `DocumentNode` that requires content.
- **Mapping by id**: Outputs are keyed by `DocumentNode.id`; no other identifiers are used for storage or lookup.
- **No structural authority**: Writer must not invent new sections, modify structure, reorder nodes, or emit structural intents.
- **Deterministic convergence**: Each node follows a bounded path of draft → refine (at most N attempts as configured by the application). No unbounded retries.
- **Immutable structure**: Writer treats the provided tree as read-only input.

## Explicit non-goals

- Writer does **not** decide or alter document structure.
- Writer does **not** manage persistence.
- Writer does **not** orchestrate workflows or scheduling.
- Writer does **not** guarantee stylistic quality beyond structural correctness and section-level obligations.
