# Step 1 — Define the Document State (authoritative)

This layer manipulates a document, not prose generation.

Minimum viable state:

class DocumentState(BaseModel):
    intent: WritingIntent
    outline: list[str]                 # ordered section names
    sections: dict[str, str]           # section_name → text
    completed: set[str]                # sections considered done


Rules:

sections may be empty or partial

outline is the source of truth for order

completed is editorial, not textual (critic-driven)

No LLM touches this directly.

# Step 2 — Define Editorial Actions (closed set)

This is the most important decision.

These are not writer ops.
These are document ops.

Start minimal:

class DocAction(Enum):
    DRAFT = "draft"        # create section text
    REFINE = "refine"      # improve existing section


That’s it.
Everything else (merge, split, reorder, delete) is outer-loop-only and should NOT be implemented yet.

Why:

You can derive all early behavior from these two

Tests already validate draft/refine semantics

You avoid premature structure mutations

# Step 3 — Define the Action Selector (the “middle brain”)

This component answers exactly one question:

“Given the current DocumentState, what is the next atomic action?”

Signature:

def select_next_action(state: DocumentState) -> WriterTask | None


Rules (deterministic, no LLM yet):

If a section in outline has no text → DRAFT

If a section has text but critic rejected → REFINE

If all sections are completed → None

This alone gives you a working middle loop.

# Step 4 — Map Document Action → WriterTask

This translation must be pure and boring.

WriterTask(
    section_name=section,
    operation="draft" | "refine",
    purpose=...,
    requirements=[...],
)


Key rule:

The middle layer never injects prose

It only supplies intent and constraints

# Step 5 — Update DocumentState (immutably)

After Supervisor returns:

def apply_result(
    state: DocumentState,
    task: WriterTask,
    result: WriterResult,
    decision: Decision,
) -> DocumentState


Rules:

ACCEPT → update sections, mark completed

REJECT → keep text, mark section incomplete

No retries here; retries are just repeated REFINE actions

This keeps loops explicit and testable.

# Step 6 — Only now introduce an LLM (optional)

Once this works deterministically:

You may replace select_next_action with an LLM-backed editor

But the action space stays identical

This is crucial:
LLMs choose actions, they do not invent mechanics.

What NOT to do yet

Do not:

implement merge/split/reorder/delete

let the writer see document state

let the editor emit prose

add planner logic to the writer

add another Supervisor prematurely

Those come after this loop is stable.

Mental model (keep this)

Writer: (task, optional text) → text

Editor: (document) → next action

Intent layer: (human text) → WritingIntent

Each layer is strictly less intelligent than the one above it.

Bottom line

You start the middle loop by:

Freezing document state

Defining a closed action set

Making action selection deterministic

Mapping actions to WriterTasks

Updating state immutably

Once that works, scaling outward is trivial.