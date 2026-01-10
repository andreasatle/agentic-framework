from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from agentic_framework.agents.openai import OpenAIAgent


PROMPT_TITLE_SUGGESTER = """ROLE:
You suggest a short title for a blog post based only on the provided content.

INPUT (JSON):
{
  "content": "<markdown string>"
}

OUTPUT (JSON):
{
  "suggested_title": "<string>"
}

RULES:
1. Derive the title only from the content provided.
2. Keep it short and specific (<= 80 characters preferred).
3. No quotes, no markdown, no extra text.
"""


class TitleSuggestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        if not self.content or not self.content.strip():
            raise ValueError("content must be a non-empty string")
        return self


class TitleSuggestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggested_title: str

    @model_validator(mode="after")
    def validate_title(self) -> Self:
        if not self.suggested_title or not self.suggested_title.strip():
            raise ValueError("suggested_title must be a non-empty string")
        return self


_AGENT: OpenAIAgent[TitleSuggestInput, TitleSuggestOutput] | None = None


def _get_agent() -> OpenAIAgent[TitleSuggestInput, TitleSuggestOutput]:
    global _AGENT
    if _AGENT is None:
        _AGENT = OpenAIAgent(
            name="blog-title-suggester",
            model="gpt-4.1-mini",
            system_prompt=PROMPT_TITLE_SUGGESTER,
            input_schema=TitleSuggestInput,
            output_schema=TitleSuggestOutput,
            temperature=0.0,
        )
    return _AGENT


def suggest_title(content: str) -> str:
    payload = TitleSuggestInput(content=content)
    agent = _get_agent()
    raw_output = agent(payload.model_dump_json())
    output = TitleSuggestOutput.model_validate_json(raw_output)
    return output.suggested_title
