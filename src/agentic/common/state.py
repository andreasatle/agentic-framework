from __future__ import annotations
from pydantic import BaseModel


class StatelessProblemState(BaseModel):
    """
    Default domain-level state.
    Optional per-domain accumulation. Does nothing by default.
    """

    def update(self, task, result):
        """
        No-op state update for stateless domains.
        Must exist so that the supervisor can uniformly call update().
        """
        return self
