from agentic.schemas import ProjectState, WorkerOutput


def update_state(prev_state: ProjectState, worker_output: WorkerOutput) -> ProjectState:
    """
    Domain-specific state update.
    MUST NOT modify prev_state in-place.
    Return a NEW ProjectState instance or prev_state unchanged.
    """
    return prev_state
