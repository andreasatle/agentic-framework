
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class WriterTask(BaseModel):
    """Unit of writing work produced by the planner."""

    section_name: str = Field(..., description="Human-readable label for the section.")
    purpose: str = Field(..., description="Brief intent for the section.")
    operation: Literal["draft", "refine"]
    requirements: list[str] = Field(
        ..., description="Specific constraints or bullets the worker must satisfy."
    )


class WriterResult(BaseModel):
    """Text produced by the worker for a single writing task."""

    text: str = Field(..., description="Completed prose for the section.")


class WriteOp(BaseModel):
    """Data-only write operation schema."""

    model_config = ConfigDict(extra="forbid")

    op: Literal["draft", "refine", "merge", "split"]
    target_section: str | None
    source_sections: list[str]
    instructions: str


def writer_task_to_write_op(task: WriterTask) -> WriteOp:
    return WriteOp(
        op=task.operation,
        target_section=task.section_name,
        source_sections=[],
        instructions=" ".join(task.requirements),
    )
