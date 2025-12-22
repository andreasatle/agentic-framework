import json
from pathlib import Path
from typing import Any

import gradio as gr
import yaml
from pydantic import ValidationError

from agentic.agent_dispatcher import AgentDispatcher
from domain.document.api import analyze
from domain.document.content import ContentStore
from domain.document.planner import make_planner
from domain.document.schemas import DocumentPlannerOutput
from domain.document.types import DocumentNode, DocumentTree
from domain.intent.types import IntentEnvelope
from domain.writer import make_agent_dispatcher as make_writer_dispatcher, make_tool_registry as make_writer_tool_registry
from domain.writer.api import execute_document


def _to_none(value: str) -> str | None:
    value = value.strip()
    return value if value else None


def _list_from_text(value: str) -> list[str]:
    separators = [",", "\n"]
    items: list[str] = [value]
    for sep in separators:
        next_items: list[str] = []
        for item in items:
            next_items.extend(item.split(sep))
        items = next_items
    return [item.strip() for item in items if item.strip()]


def _assemble_markdown(node: DocumentNode, store: ContentStore, depth: int = 0) -> list[str]:
    lines: list[str] = []
    heading_prefix = "#" * (depth + 1)
    lines.append(f"{heading_prefix} {node.title}".strip())
    text = store.by_node_id.get(node.id)
    if text:
        text_lines = text.splitlines()
        filtered_lines: list[str] = []
        first_non_empty_seen = False
        for line in text_lines:
            if not first_non_empty_seen and line.strip():
                first_non_empty_seen = True
                if line == f"{node.title}:":
                    continue
            filtered_lines.append(line)
        lines.append("\n".join(filtered_lines).strip())
    for child in node.children:
        lines.extend(_assemble_markdown(child, store, depth + 1))
    return lines


def _collect_outline(node: DocumentNode, depth: int = 0) -> list[str]:
    prefix = "  " * depth + "- "
    entries = [f"{prefix}{node.title}"]
    for child in node.children:
        entries.extend(_collect_outline(child, depth + 1))
    return entries


def build_intent(
    document_goal: str,
    audience_choice: str,
    audience_custom: str,
    tone: str,
    required_sections: str,
    forbidden_sections: str,
    must_include: str,
    must_avoid: str,
    narrative_voice: str,
    formality: str,
    humor_level: str,
) -> tuple[str, str, str, dict[str, Any] | None]:
    audience_value = _to_none(audience_custom) if audience_choice == "Custom" else _to_none(audience_choice)
    data: dict[str, Any] = {
        "structural_intent": {
            "document_goal": _to_none(document_goal),
            "audience": audience_value,
            "tone": _to_none(tone),
            "required_sections": _list_from_text(required_sections),
            "forbidden_sections": _list_from_text(forbidden_sections),
        },
        "semantic_constraints": {
            "must_include": _list_from_text(must_include),
            "must_avoid": _list_from_text(must_avoid),
            "required_mentions": [],
        },
        "stylistic_preferences": {
            "narrative_voice": _to_none(narrative_voice),
            "formality": _to_none(formality),
            "humor_level": _to_none(humor_level),
        },
    }

    try:
        intent = IntentEnvelope.model_validate(data)
    except ValidationError as exc:
        return "", "", f"Validation error:\n{exc}", None

    dumped = intent.model_dump()
    pretty_yaml = yaml.safe_dump(dumped, sort_keys=False, default_flow_style=False)
    pretty_json = json.dumps(dumped, indent=2)
    return pretty_json, pretty_yaml, "", dumped


def save_yaml(yaml_text: str) -> str:
    path = Path("intent.yaml")
    path.write_text(yaml_text)
    return f"Saved to {path.resolve()}"


def run_document_writer(intent_state: dict[str, Any] | None) -> tuple[str, str, str, str, str]:
    if intent_state is None:
        return "", "", "", "", "No validated IntentEnvelope. Build it first."
    try:
        intent = IntentEnvelope.model_validate(intent_state)
    except ValidationError as exc:
        return "", "", "", "", f"Intent validation failed:\n{exc}"

    try:
        planner = make_planner(model="gpt-4.1-mini")
        dispatcher = AgentDispatcher(planner=planner, workers={}, critic=None)  # planner-only
        analysis = analyze(
            document_tree=None,
            tone=intent.structural_intent.tone,
            audience=intent.structural_intent.audience,
            goal=intent.structural_intent.document_goal,
            intent=intent,
            dispatcher=dispatcher,
        )
        planner_output = DocumentPlannerOutput.model_validate(analysis.plan)
        planned_tree: DocumentTree = planner_output.document_tree

        writer_dispatcher = make_writer_dispatcher(model="gpt-4.1-mini", max_retries=3)
        writer_tool_registry = make_writer_tool_registry()
        content_store = ContentStore()
        writer_result = execute_document(
            document_tree=planned_tree,
            content_store=content_store,
            dispatcher=writer_dispatcher,
            tool_registry=writer_tool_registry,
            intent=intent,
            applies_thesis_rule=bool(planner_output.applies_thesis_rule),
        )
    except Exception as exc:  # explicit surface for UI errors
        return "", "", "", "", f"Execution failed: {exc}"

    outline_text = "\n".join(_collect_outline(planned_tree.root))
    markdown_text = "\n\n".join(_assemble_markdown(planned_tree.root, content_store))
    audit_text = yaml.safe_dump(writer_result.intent_audit.model_dump(), sort_keys=False, default_flow_style=False)
    trace_text = yaml.safe_dump(analysis.trace or [], sort_keys=False, default_flow_style=False)
    return outline_text, markdown_text, audit_text, trace_text, ""


def main() -> None:
    with gr.Blocks(title="IntentEnvelope Builder") as demo:
        gr.Markdown("# IntentEnvelope Builder\nPure data capture for `IntentEnvelope` (no inference).")
        intent_state = gr.State()

        with gr.Group():
            gr.Markdown("## Structural Intent")
            document_goal = gr.Textbox(label="Document Goal", lines=3, placeholder="Overall goal (optional)")
            audience_choice = gr.Dropdown(
                label="Audience",
                choices=["", "general", "executives", "engineers", "researchers", "Custom"],
                value="",
            )
            audience_custom = gr.Textbox(label="Audience (Custom)", placeholder="Used when Audience=Custom")
            tone = gr.Dropdown(
                label="Tone",
                choices=["", "informative", "reflective", "technical", "narrative", "other"],
                value="",
            )
            required_sections = gr.Textbox(
                label="Required Sections",
                placeholder="Newline-separated list (optional)",
                lines=3,
            )
            forbidden_sections = gr.Textbox(
                label="Forbidden Sections",
                placeholder="Newline-separated list (optional)",
                lines=3,
            )

        with gr.Group():
            gr.Markdown("## Semantic Constraints")
            must_include = gr.Textbox(
                label="Must Include",
                placeholder="Comma or newline separated (optional)",
                lines=2,
            )
            must_avoid = gr.Textbox(
                label="Must Avoid",
                placeholder="Comma or newline separated (optional)",
                lines=2,
            )

        with gr.Group():
            gr.Markdown("## Stylistic Preferences")
            narrative_voice = gr.Dropdown(
                label="Narrative Voice",
                choices=["", "first-person", "third-person", "neutral"],
                value="",
            )
            formality = gr.Dropdown(
                label="Formality",
                choices=["", "informal", "neutral", "formal"],
                value="",
            )
            humor_level = gr.Dropdown(
                label="Humor Level",
                choices=["", "none", "light", "moderate"],
                value="",
            )

        build_button = gr.Button("Build IntentEnvelope")
        run_button = gr.Button("Run Document Writer")
        save_button = gr.Button("Save YAML")
        json_output = gr.Code(label="IntentEnvelope (JSON)", language="json")
        yaml_output = gr.Code(label="IntentEnvelope (YAML)", language="yaml")
        error_output = gr.Textbox(label="Validation Errors", lines=6)
        outline_output = gr.Textbox(label="Document Outline (titles only)", lines=8)
        markdown_output = gr.Textbox(label="Rendered Document (Markdown)", lines=12)
        audit_output = gr.Code(label="Intent Audit", language="yaml")
        trace_output = gr.Code(label="Trace", language="yaml")
        save_status = gr.Textbox(label="Save Status", interactive=False)

        build_button.click(
            build_intent,
            inputs=[
                document_goal,
                audience_choice,
                audience_custom,
                tone,
                required_sections,
                forbidden_sections,
                must_include,
                must_avoid,
                narrative_voice,
                formality,
                humor_level,
            ],
            outputs=[json_output, yaml_output, error_output, intent_state],
        )

        run_button.click(
            run_document_writer,
            inputs=[intent_state],
            outputs=[outline_output, markdown_output, audit_output, trace_output, error_output],
        )

        save_button.click(save_yaml, inputs=yaml_output, outputs=save_status)

    demo.launch()


if __name__ == "__main__":
    main()
