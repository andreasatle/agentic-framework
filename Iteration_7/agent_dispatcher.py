from dataclasses import dataclass
from .schemas import (
    PlannerInput,
    PlannerOutput,
    WorkerInput,
    WorkerOutput,
    CriticInput,
    CriticOutput,
)
from .protocols import AgentProtocol, InputSchema, OutputSchema
from pydantic import ValidationError
from .logging_config import get_logger

logger = get_logger("agentic.dispatcher")

@dataclass
class AgentDispatcher:
    planner: AgentProtocol[PlannerInput, PlannerOutput]
    worker: AgentProtocol[WorkerInput, WorkerOutput]
    critic: AgentProtocol[CriticInput, CriticOutput]
    max_retries: int = 3

    def _call(self, agent: AgentProtocol[InputSchema, OutputSchema], input: InputSchema) -> OutputSchema:
        """Call agent, validate JSON, retry boundedly, return typed object."""
        last_err: Exception | None = None
        last_raw: str | None = None
        for attempt in range(1, self.max_retries + 1):
            raw = agent(input.model_dump_json())
            last_raw = raw
            logger.debug(f"[dispatcher] {agent.name} attempt {attempt}/{self.max_retries} payload={raw[:200]}")
            try:
                return agent.output_schema.model_validate_json(raw)
            except ValidationError as e:
                last_err = e
            except Exception as e:
                last_err = e
        raise RuntimeError(
            f"Agent '{agent.name}' failed after retries. "
            f"Last error: {last_err}. Last raw payload: {last_raw}"
        )

    def plan(self) -> PlannerOutput:
        return self._call(self.planner, PlannerInput())

    def work(self, args: WorkerInput) -> WorkerOutput:
        return self._call(self.worker, args)

    def critique(self, args: CriticInput) -> CriticOutput:
        return self._call(self.critic, args)
