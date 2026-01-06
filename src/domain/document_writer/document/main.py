from dotenv import load_dotenv
from domain.document_writer.document.planner import make_planner
from domain.document_writer.document.types import DocumentTree
from domain.document_writer.document.api import analyze
from domain.document_writer.intent.types import IntentEnvelope
from agentic.agent_dispatcher import AgentDispatcher
from agentic.logging_config import get_logger

logger = get_logger("domain.document_writer.document.main")


def _pretty_print_run(run: dict, trace: bool = False) -> None:
    """Render the analysis supervisor output in a readable diagnostic summary."""
    def _serialize(value):
        return value.model_dump() if hasattr(value, "model_dump") else value

    print("Document analysis supervisor run complete:")
    print(f"  PlannerInput: {_serialize(run.planner_input)}")
    print(f"  Plan: {_serialize(run.plan)}")
    if trace and run.trace:
        print("  Trace:")
        for entry in run.trace:
            print(f"    {_serialize(entry)}")


def main() -> None:
    load_dotenv(override=True)

    # --- Planner-only dispatcher ---
    planner = make_planner(model="gpt-4.1-mini")
    dispatcher = AgentDispatcher(
        planner=planner,
        workers={},      # REQUIRED: empty, analysis-only
        critic=None,     # type: ignore[arg-type]
    )

    # --- Initial document state ---
    # For now, start with no tree (first planning step).
    document_tree: DocumentTree | None = None
    intent = IntentEnvelope()

    run = analyze(
        document_tree=document_tree,
        intent=intent,
        dispatcher=dispatcher,
    )

    _pretty_print_run(run)


if __name__ == "__main__":
    main()
