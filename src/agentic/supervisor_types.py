from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

from agentic.schemas import WorkerInput, WorkerOutput, CriticInput, ProjectState, Feedback


class SupervisorState(Enum):
    PLAN = auto()
    WORK = auto()
    TOOL = auto()
    CRITIC = auto()
    END = auto()


@dataclass
class SupervisorContext:
    plan: Any | None = None
    request_task: Any | None = None
    worker_id: str | None = None
    worker_input: WorkerInput | None = None
    worker_output: WorkerOutput | None = None
    worker_result: Any | None = None
    tool_request: Any | None = None
    tool_result: Any | None = None
    critic_input: CriticInput | None = None
    decision: Any | None = None
    loops_used: int = 0
    trace: list[Any] | None = None
    project_state: ProjectState | None = None
    domain_snapshot: dict | None = None
    pending_state_update: tuple[Any, Any] | None = None
