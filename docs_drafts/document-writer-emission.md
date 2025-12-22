# Writer Task Emission Rules

## Inputs
- `DocumentTree`
- `ContentStore`

No other inputs participate in emission.

## Eligibility
A `DocumentNode` is eligible for a writer task iff:
- Its `id` is not present in `ContentStore.by_node_id`.
- It is a leaf node (has no children).

## Task Mapping
For each eligible node, emit a `DraftSectionTask` with:
- `section_name` = `DocumentNode.title`
- `purpose` = `DocumentNode.description`
- `requirements` = `[]` (empty)

No refine tasks are emitted.

## Traversal Policy
Traversal order is policy-driven by application code. Allowed policies:
- Depth-first
- Breadth-first
- Explicit node selection

Traversal policy is owned solely by application code.

## Authority and Ownership
- Supervisors do not emit writer tasks.
- Planners do not emit writer tasks.
- Writers do not choose nodes.
- Critics do not select structure.
- Application code is the sole owner of emission.

## Non-Goals
This spec does not define automation, parallelism, retries, scheduling, persistence, or refinement logic.
