"""
Iteration 6 Supervisor.

Responsibilities:
1. Call agents.
2. Validate JSON + schema using Pydantic.
3. Execute tools (supervisor-controlled).
4. Retry boundedly on failure.
5. Loop boundedly until Critic ACCEPT.

Agents are untrusted. The Supervisor is trusted.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from .schemas import (
    PlannerInput,
    PlannerOutput,
    WorkerInput,
    WorkerOutput,
    Compute,
    ToolRequest,
    CriticInput,
    CriticOutput,
)
from .protocols import AgentProtocol, AgentInput, AgentOutput
from .logging_config import get_logger
from .tool_registry import ToolRegistry

logger = get_logger("agentic.iteration6.supervisor")


@dataclass
class Supervisor:
    planner: AgentProtocol[PlannerInput, PlannerOutput]
    worker: AgentProtocol[WorkerInput, WorkerOutput]
    critic: AgentProtocol[CriticInput, CriticOutput]
    tool_registry: ToolRegistry
    max_retries: int = 3
    max_loops: int = 5

    def safe_call(
        self,
        agent: AgentProtocol[AgentInput, AgentOutput],
        input: AgentInput,
    ) -> AgentOutput:
        """
        Call an agent and validate its output against a Pydantic schema.
        Retries on malformed JSON or schema mismatch.
        """
        logger.debug(f"Calling agent {agent.name} with input: {input.model_dump()}")
        last_err: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            raw = agent(input.model_dump_json())
            logger.debug(f"Raw output from {agent.name}: {raw}")
            try:
                return agent.output_schema.model_validate_json(raw)
            except ValidationError as e:
                last_err = e
                logger.info(
                    f"[safe_call] retry {attempt}/{self.max_retries} "
                    f"— invalid {agent.output_schema.__name__}: {e.errors()}"
                )

        raise RuntimeError(
            f"Agent {agent.name} failed schema {agent.output_schema.__name__} "
            f"after {self.max_retries} retries. Last error: {last_err}"
        )

    def _handle_worker_tool_request(
        self,
        planner_output: PlannerOutput,
        tool_request: ToolRequest[Compute],
    ) -> WorkerInput:
        """
        Execute the requested tool and build a new WorkerInput
        with tool_result filled in.
        """
        tool = self.tool_registry.get(tool_request.tool_name)
        if tool is None:
            raise RuntimeError(f"Unknown tool requested: {tool_request.tool_name}")

        # Enforce that the tool request matches the original plan

        if tool_request.args.model_dump() != planner_output.model_dump():
            raise RuntimeError("Tool request arguments do not match planner output")

        # ✅ Call the tool
        tool_result = self.tool_registry.call("compute", tool_request.args)

        logger.info(
            f"[supervisor] tool '{tool_request.tool_name}' executed with "
            f"{tool_request.args.model_dump()} -> {tool_result.value}"
        )

        # Build new WorkerInput for the Worker agent with tool_result injected
        return WorkerInput(
            task=planner_output,
            previous_result=None,
            feedback="used tool result",
            tool_result=tool_result,
        )


    def __call__(self) -> dict:
        """
        One full Plan -> Act -> Check loop with bounded refinement.
        Returns a structured record of the accepted run.
        """
        planner_input = PlannerInput()
        planner_output: PlannerOutput = self.safe_call(self.planner, planner_input)
        worker_input: WorkerInput = WorkerInput(task=planner_output)

        for loop_idx in range(1, self.max_loops + 1):
            worker_output: WorkerOutput = self.safe_call(self.worker, worker_input)

            if worker_output.tool_request is not None:
                worker_input = self._handle_worker_tool_request(
                    planner_output=planner_output,
                    tool_request=worker_output.tool_request,
                )
                logger.info(
                    f"[supervisor] loop {loop_idx}/{self.max_loops} "
                    f"— tool executed, retrying Worker"
                )
                continue

            if worker_output.result is None:
                raise RuntimeError("WorkerOutput missing result in non-tool branch")

            critic_input = CriticInput(
                plan=planner_output,
                worker_answer=worker_output.result,
            )
            critic_output: CriticOutput = self.safe_call(self.critic, critic_input)

            if critic_output.decision == "REJECT":
                worker_input = WorkerInput(
                    task=planner_output,
                    previous_result=worker_output.result,
                    feedback=critic_output.feedback,
                    tool_result=worker_input.tool_result,
                )
                logger.info(
                    f"[supervisor] loop {loop_idx}/{self.max_loops} "
                    f"— REJECT, retrying Worker"
                )
            elif critic_output.decision == "ACCEPT":
                return {
                    "plan": planner_output,
                    "result": worker_output,
                    "decision": critic_output,
                    "loops_used": loop_idx,
                }

        raise RuntimeError(f"Supervisor hit max_loops={self.max_loops} without ACCEPT.")
