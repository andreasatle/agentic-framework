from document_writer.domain.intent import load_intent_from_yaml
from document_writer.domain.intent.types import IntentEnvelope


def test_text_intent_controller_returns_intent_envelope():
    fake_output = {
        "structural_intent": {"document_goal": "Explain system", "audience": "Engineers", "tone": "concise"},
        "semantic_constraints": {"must_include": ["architecture"], "must_avoid": [], "required_mentions": []},
        "stylistic_preferences": {"humor_level": None, "formality": "medium", "narrative_voice": None},
    }
    yaml_text = "\n".join(
        [
            "structural_intent:",
            "  document_goal: Explain system",
            "  audience: Engineers",
            "  tone: concise",
            "semantic_constraints:",
            "  must_include:",
            "    - architecture",
            "  must_avoid: []",
            "  required_mentions: []",
            "stylistic_preferences:",
            "  humor_level: null",
            "  formality: medium",
            "  narrative_voice: null",
        ]
    )
    intent = load_intent_from_yaml(yaml_text)
    assert isinstance(intent, IntentEnvelope)
    assert intent.structural_intent.document_goal == "Explain system"
    assert "architecture" in intent.semantic_constraints.must_include
    # Ensure no structural artifacts are injected
    assert intent.structural_intent.required_sections == []
    assert intent.structural_intent.forbidden_sections == []
