from dataclasses import dataclass
from typing import Any, Self
from pydantic import BaseModel, ConfigDict, model_validator

from agentic_framework.agent_dispatcher import AgentDispatcher
from agentic_framework.protocols import AgentProtocol


class TransformControllerRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    document: str
    editing_policy: str
    intent: Any | None = None

    @model_validator(mode="after")
    def validate_inputs(self) -> Self:
        if not self.document or not self.document.strip():
            raise ValueError("TransformControllerRequest requires a non-empty document.")
        if not self.editing_policy or not self.editing_policy.strip():
            raise ValueError("TransformControllerRequest requires a non-empty editing_policy.")
        return self


class TransformControllerResponse(BaseModel):
    """Immutable result of a single transform execution."""

    model_config = ConfigDict(frozen=True)

    edited_document: str
    trace: list[dict] | None = None

    @model_validator(mode="after")
    def validate_output(self) -> Self:
        if not self.edited_document or not self.edited_document.strip():
            raise ValueError("TransformControllerResponse requires a non-empty edited_document.")
        return self


@dataclass(frozen=True)
class TransformController:
    dispatcher: AgentDispatcher
    agent: AgentProtocol

    def __call__(self, request: TransformControllerRequest) -> TransformControllerResponse:
        payload: dict[str, Any] = {
            "document": request.document,
            "editing_policy": request.editing_policy,
            "instruction": "Apply the editing policy exactly. Return the edited document only.",
        }
        if request.intent is not None:
            payload["intent"] = request.intent

        agent_input = self.agent.input_schema(**payload)

        original_retries = self.dispatcher.max_retries
        if original_retries != 1:
            self.dispatcher.max_retries = 1
        try:
            agent_output = self.dispatcher._call(self.agent, agent_input)
        finally:
            if self.dispatcher.max_retries != original_retries:
                self.dispatcher.max_retries = original_retries

        edited_document = getattr(agent_output, "edited_document", None)
        if not isinstance(edited_document, str) or not edited_document.strip():
            raise ValueError("TransformController requires non-empty edited_document output.")

        return TransformControllerResponse(edited_document=edited_document)
