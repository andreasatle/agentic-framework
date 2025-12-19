"""
Text Prompt Refiner Contract

- Input: raw user text (str).
- Output: refined user text (str).
- Transformation is semantic-preserving, non-authoritative, and advisory-only.
- The refiner MUST NOT invent intent or meaning; it only normalizes the supplied text.
- The refiner does NOT plan, execute, extract intent, create structure, or generate documents.
"""
from pydantic import BaseModel


class TextPromptRefinerInput(BaseModel):
    """Raw user text input for the Text Prompt Refiner; sole, authority-free input."""

    text: str


PROMPT_TEXT_REFINER = """ROLE:
You rewrite raw user text into a clearer version of the same intent.

RULES (DO):
- Preserve meaning exactly; rephrase only to clarify.
- Expose ambiguities explicitly instead of guessing.
- Preserve first-person voice, uncertainty, and tone.

RULES (DO NOT):
- Do NOT add goals, ideas, opinions, or examples.
- Do NOT remove core concerns or resolve ambiguity by guessing.
- Do NOT plan, decide structure, extract intent, or generate articles.
- Do NOT explain concepts or define terminology.
- Do NOT use headings, lists, or structured formats.

OUTPUT:
- Return ONLY refined plain prose of the same intent; no commentary or metadata."""
