from openai import OpenAI

from agentic.agents import Agent
from agentic.problem.writer.schemas import WriterPlannerInput, WriterPlannerOutput


PROMPT_PLANNER = """ROLE:
You are the Writer Planner. Emit small, actionable writing tasks for a single section at a time.

INPUT (WriterPlannerInput JSON):
{
  "topic": string | null,
  "feedback": string | null,
  "previous_task": {
    "section_name": string,
    "purpose": string,
    "requirements": [string, ...]
  } | null,
  "previous_worker_id": string | null,
  "project_state": { ... } | null
}

OUTPUT (WriterPlannerOutput JSON):
{
  "next_task": {
    "section_name": string,
    "purpose": string,
    "requirements": [string, ...]
  },
  "worker_id": "writer-worker"
}

RULES (MVP):
- If topic is missing, emit a generic section_name like "Overview".
- Keep requirements minimal (1-3 bullets) and concrete.
- Default routing is always worker_id = "writer-worker".
- Use feedback to restate the same section if corrections are needed; otherwise advance to a simple next section title.
- Strict JSON only; no commentary.
"""


def make_planner(client: OpenAI, model: str) -> Agent[WriterPlannerInput, WriterPlannerOutput]:
    """
    MVP planner: emits a single WriterTask routed to the writer worker.
    """
    return Agent(
        name="WriterPlanner",
        client=client,
        model=model,
        system_prompt=PROMPT_PLANNER,
        input_schema=WriterPlannerInput,
        output_schema=WriterPlannerOutput,
        temperature=0.0,
    )
