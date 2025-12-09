from openai import OpenAI

from agentic.agents import Agent
from agentic.problem.writer.schemas import WriterWorkerInput, WriterWorkerOutput


PROMPT_WORKER = """ROLE:
You are the Writer Worker. Draft the requested section text briefly.

INPUT (WriterWorkerInput JSON):
{
  "task": {
    "section_name": string,
    "purpose": string,
    "requirements": [string, ...]
  },
  "previous_text": string | null,
  "previous_result": { "text": string } | null,
  "feedback": string | null,
  "tool_result": null
}

OUTPUT (WorkerOutput JSON):
{
  "result": { "text": "<short placeholder paragraph>" }
}

RULES (MVP):
- Write 1-3 sentences that directly address the purpose and requirements.
- If feedback is present, apply it; otherwise produce a simple placeholder paragraph.
- Do not request tools; always return the result branch.
- Strict JSON only.
"""


def make_worker(client: OpenAI, model: str) -> Agent[WriterWorkerInput, WriterWorkerOutput]:
    """
    MVP worker: always returns a placeholder paragraph for the requested section.
    """
    return Agent(
        name="writer-worker",
        client=client,
        model=model,
        system_prompt=PROMPT_WORKER,
        input_schema=WriterWorkerInput,
        output_schema=WriterWorkerOutput,
        temperature=0.0,
    )
