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
