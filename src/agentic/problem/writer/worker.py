from openai import OpenAI

from agentic.agents import Agent
from agentic.problem.writer.schemas import (
    WriterDomainState,
    WriterWorkerInput,
    WriterWorkerOutput,
)


PROMPT_WORKER = """ROLE:
You are the Worker in a Planner–Worker–Critic loop.

Your ONLY responsibility is to produce the content for the section specified
by the Planner’s JSON task. You do not design the workflow, you do not judge
quality, and you do not modify the task. You simply execute it faithfully.

You must write the section exactly as the Planner specifies:
- use the section name
- respect the purpose
- satisfy every requirement
- avoid adding unrequested topics
- avoid global structure planning
- avoid meta-commentary

The output should read as a polished, publication-ready section of a whitepaper
for GitHub or Medium, with a professional and academically neutral tone.

WORKER INPUT FORMAT (from Planner):
{
  "task": {
    "section_name": "<name>",
    "purpose": "<reason this section exists>",
    "requirements": ["...", "...", "..."]
  }
}

WORKER OUTPUT FORMAT (STRICT):
{
  "result": {
    "text": "<fully written section text>"
  }
}

RULES:
1. Your output MUST be valid JSON with exactly one key: "result".
2. The value of "result" MUST be the written prose of the section under the key "text".
3. You MUST satisfy every requirement in the Planner’s list.
4. You MUST NOT introduce content outside the scope defined by the Planner.
5. No explanations, no reasoning, no side notes. ONLY the JSON result.
6. No Markdown code fences; the Critic needs clean JSON.
7. Avoid repetition; ensure clarity and coherence.

Your task is execution, not planning. Wait for the Planner’s JSON.
When you receive a task, write the section accordingly.
"""

def make_worker(client: OpenAI, model: str) -> Agent[WriterWorkerInput, WriterWorkerOutput]:
    """
    MVP worker: always returns a placeholder paragraph for the requested section.
    """
    base_agent = Agent(
        name="writer-worker",
        client=client,
        model=model,
        system_prompt=PROMPT_WORKER,
        input_schema=WriterWorkerInput,
        output_schema=WriterWorkerOutput,
        temperature=0.0,
    )

    class WriterWorkerAgent:
        def __init__(self, agent: Agent[WriterWorkerInput, WriterWorkerOutput]):
            self._agent = agent
            self.name = agent.name
            self.input_schema = agent.input_schema
            self.output_schema = agent.output_schema
            self.id = agent.id

        def __call__(self, user_input: str) -> str:
            try:
                worker_input = WriterWorkerInput.model_validate_json(user_input)
            except Exception:
                worker_input = None

            raw_output = self._agent(user_input)
            try:
                output_model = WriterWorkerOutput.model_validate_json(raw_output)
            except Exception:
                return raw_output

            project_state = getattr(worker_input, "project_state", None) if worker_input else None
            section_name = getattr(worker_input.task, "section_name", None) if worker_input else None
            if project_state is not None:
                previous_state = project_state.domain_state.get("writer")
                outline = previous_state.outline if isinstance(previous_state, WriterDomainState) else None
                completed_sections = list(previous_state.completed_sections or []) if isinstance(previous_state, WriterDomainState) else []
                if section_name and section_name not in completed_sections:
                    completed_sections.append(section_name)
                project_state.domain_state["writer"] = WriterDomainState(
                    outline=outline,
                    completed_sections=completed_sections or None,
                )

            return output_model.model_dump_json()

    return WriterWorkerAgent(base_agent)  # type: ignore[return-value]
