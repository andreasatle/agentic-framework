from __future__ import annotations

from pydantic import BaseModel, Field


class WriterTask(BaseModel):
    """Unit of writing work produced by the planner."""

    section_name: str = Field(..., description="Human-readable label for the section.")
    purpose: str = Field(..., description="Brief intent for the section.")
    requirements: list[str] = Field(
        ..., description="Specific constraints or bullets the worker must satisfy."
    )


class WriterResult(BaseModel):
    """Text produced by the worker for a single writing task."""

    text: str = Field(..., description="Completed prose for the section.")


class WriterState(BaseModel):
    sections: dict[str, str] = Field(default_factory=dict)

    def update(self, task: WriterTask, result: WriterResult) -> WriterState:
        new_sections = dict(self.sections)
        new_sections[task.section_name] = result.text
        return WriterState(sections=new_sections)
