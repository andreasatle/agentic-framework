from pydantic import BaseModel

from agentic.schemas import ProjectState, WorkerOutput


class ProblemState(BaseModel):
    """
    Domain-specific persistent state.
    MUST NOT mutate in-place; always return a new instance from update().
    """

    content: str = ""

    def update(self, worker_output: WorkerOutput) -> "ProblemState":
        """
        Return a NEW ProblemState instance updated with accepted worker output.
        Default behavior: no change.
        """
        return self
