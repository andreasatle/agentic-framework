from pydantic import BaseModel, Field


class WriterState(BaseModel):
    sections: dict[str, str] = Field(default_factory=dict)
