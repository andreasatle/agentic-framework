from openai import OpenAI

from agentic.agents import Agent
from agentic.problem.writer.schemas import WriterCriticInput, WriterCriticOutput


PROMPT_CRITIC = """ROLE:
You are the Writer Critic. Decide if the candidate text meets the task requirements.

INPUT (WriterCriticInput JSON):
{
  "task": {
    "section_name": string,
    "purpose": string,
    "requirements": [string, ...]
  },
  "candidate": { "text": string },
  "project_state": { ... } | null
}

OUTPUT (WriterCriticOutput JSON):
{
  "decision": "ACCEPT" | "REJECT",
  "feedback": string | null,
  "accepted": boolean
}

RULES (MVP):
- If candidate.text is missing or empty, REJECT with feedback requesting a short paragraph.
- Otherwise ACCEPT by default and set feedback = null.
- Ensure accepted boolean matches the decision.
- Strict JSON only.
"""


def make_critic(client: OpenAI, model: str) -> Agent[WriterCriticInput, WriterCriticOutput]:
    """
    MVP critic: accepts any non-empty text and mirrors the writer decision schema.
    """
    return Agent(
        name="WriterCritic",
        client=client,
        model=model,
        system_prompt=PROMPT_CRITIC,
        input_schema=WriterCriticInput,
        output_schema=WriterCriticOutput,
        temperature=0.0,
    )
