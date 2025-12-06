from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic.schemas import WorkerInput, CriticInput
from agentic.tool_registry import ToolRegistry
from agentic.logging_config import get_logger
from agentic.agent_dispatcher import AgentDispatcher

logger = get_logger("agentic.supervisor")


class _State(Enum):
    PLAN = "PLAN"
    WORK = "WORK"
    TOOL = "TOOL"
    CRITIC = "CRITIC"
    END = "END"


@dataclass
class Supervisor:
    dispatcher: AgentDispatcher
    tool_registry: ToolRegistry
    max_loops: int = 5

    def __call__(self) -> dict:
        """
        Explicit FSM over PLAN → WORK → TOOL/CRITIC → END.
        Each agent/tool invocation is a state transition.
        """
        context: dict[str, Any] = {"loops_used": 0}
        state = _State.PLAN

        while state != _State.END and context["loops_used"] < self.max_loops:
            if state is _State.PLAN:
                state = self._handle_plan(context)
            elif state is _State.WORK:
                state = self._handle_work(context)
            elif state is _State.TOOL:
                state = self._handle_tool(context)
            elif state is _State.CRITIC:
                state = self._handle_critic(context)
            else:
                raise RuntimeError(f"Unknown supervisor state: {state}")

            context["loops_used"] += 1

        if state != _State.END:
            raise RuntimeError("Supervisor exited without reaching END state.")

        return {
            "plan": context["plan"],
            "result": context["final_result"],
            "decision": context["decision"],
            "loops_used": context["loops_used"],
        }

    def _handle_plan(self, context: dict[str, Any]) -> _State:
        planner_response = self.dispatcher.plan()
        logger.debug(f"[supervisor] PLAN call_id={planner_response.call_id}")
        context["plan"] = planner_response.output.task
        context["worker_input"] = WorkerInput(task=context["plan"])
        return _State.WORK

    def _handle_work(self, context: dict[str, Any]) -> _State:
        worker_input = context.get("worker_input")
        if worker_input is None:
            raise RuntimeError("WORK state reached without worker_input in context.")

        worker_response = self.dispatcher.work(worker_input)
        worker_output = worker_response.output

        if worker_output.result is not None:
            context["worker_result"] = worker_output.result
            context["critic_input"] = CriticInput(
                plan=context["plan"], worker_answer=worker_output.result
            )
            return _State.CRITIC

        if worker_output.tool_request is not None:
            context["tool_request"] = worker_output.tool_request
            return _State.TOOL

        raise RuntimeError("WorkerOutput violated 'exactly one branch' invariant.")

    def _handle_tool(self, context: dict[str, Any]) -> _State:
        request = context.get("tool_request")
        plan = context.get("plan")
        if request is None or plan is None:
            raise RuntimeError("TOOL state reached without tool_request and plan.")

        if request.args.model_dump() != plan.model_dump():
            raise RuntimeError("Tool args do not match plan")

        tool_result = self.tool_registry.call(request.tool_name, request.args)
        context["tool_result"] = tool_result
        context["worker_input"] = WorkerInput(
            task=plan,
            previous_result=context.get("worker_result"),
            feedback=context.get("feedback"),
            tool_result=tool_result,
        )
        return _State.WORK

    def _handle_critic(self, context: dict[str, Any]) -> _State:
        critic_input = context.get("critic_input")
        if critic_input is None:
            raise RuntimeError("CRITIC state reached without critic_input in context.")

        critic_response = self.dispatcher.critique(critic_input)
        decision = critic_response.output
        context["decision"] = decision
        transitions = context["loops_used"] + 1

        if decision.decision == "ACCEPT":
            context["final_result"] = context["worker_result"]
            logger.info(f"[supervisor] ACCEPT after {transitions} transitions")
            return _State.END

        if decision.decision == "REJECT":
            context["feedback"] = decision.feedback
            context["worker_input"] = WorkerInput(
                task=context["plan"],
                previous_result=context.get("worker_result"),
                feedback=decision.feedback,
                tool_result=context.get("tool_result"),
            )
            logger.info(f"[supervisor] REJECT after {transitions} transitions")
            return _State.WORK

        raise RuntimeError("Critic decision must be ACCEPT or REJECT.")
