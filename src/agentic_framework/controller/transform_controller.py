from typing import Any, Self
from pydantic import BaseModel, ConfigDict, model_validator


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
