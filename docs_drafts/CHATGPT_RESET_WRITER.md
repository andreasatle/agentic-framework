We are building a new domain inside my multi-agent framework called the Writer Problem.

Goal:
Create a persistent, resumable article-writing system using Planner → Worker → Critic loops,
with a Supervisor that maintains ProjectState.

Core Rules:
- User input (topic, updates, constraints) is stored inside ProjectState.
- ProjectState represents the entire article-in-progress: topic, constraints, outline,
  completed sections, pending sections, last plan/result/decision, and history.
- Planner reads ProjectState and decides the next writing task (e.g., generate outline,
  write next section, revise a section).
- Worker writes only the requested section text.
- Critic evaluates whether the Worker satisfied the task requirements.
- Supervisor updates ProjectState after each accepted section.
- No tools are needed initially; writing is produced directly by the Worker.
- The system should be able to run for N iterations, save state, and resume later with
  updated constraints supplied by the user.

Key Principle:
All intent, progress, and memory live in ProjectState. The Planner must rely only on
ProjectState and the latest feedback. No hidden assumptions, no external context.

This is the authoritative design. Do not propose new architectures unless explicitly asked.
