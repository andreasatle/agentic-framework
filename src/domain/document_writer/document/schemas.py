from typing import Any

from pydantic import BaseModel

from domain.document_writer.document.types import DocumentTree
from domain.document_writer.intent.types import IntentEnvelope


class DocumentPlannerInput(BaseModel):
    """Planner input; intent is advisory and read-only. Planner retains structural authority."""
    document_tree: DocumentTree | None = None
    intent: IntentEnvelope


class DocumentPlannerOutput(BaseModel):
    document_tree: DocumentTree
    applies_thesis_rule: bool | None = None
