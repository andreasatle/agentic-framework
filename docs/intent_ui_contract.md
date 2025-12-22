# IntentEnvelope UI Contract

## Purpose & Scope
This document defines the authoritative mapping from UI controls to `IntentEnvelope` fields. It covers data capture only. No inference, planning, or execution occurs here. The UI is a pure form that produces `IntentEnvelope` instances for downstream consumers.

## Global Rules
- UI never invents fields or values.
- UI never infers missing values.
- Empty input maps to `null` (for scalars) or `[]` (for lists).
- UI cannot bypass schema validation; all submissions must validate against `IntentEnvelope`.
- All authority remains downstream; this form is advisory-only.
- Only the controls and fields listed here are permitted.

## Mapping Tables

### StructuralIntent
| Intent Field (fully qualified) | UI Control Type | Required / Optional | Default / Empty Behavior | Validation Rules (if any) |
| --- | --- | --- | --- | --- |
| structural_intent.document_goal | Multiline text | Optional | Empty → `null` | Plain text only; trim surrounding whitespace |
| structural_intent.audience | Single-line text | Optional | Empty → `null` | Plain text only; trim surrounding whitespace |
| structural_intent.tone | Single-line text | Optional | Empty → `null` | Plain text only; trim surrounding whitespace |
| structural_intent.required_sections | Tag input (multiselect) | Optional | Empty → `[]` | Each tag is plain text; trim per tag |
| structural_intent.forbidden_sections | Tag input (multiselect) | Optional | Empty → `[]` | Each tag is plain text; trim per tag |

### GlobalSemanticConstraints
| Intent Field (fully qualified) | UI Control Type | Required / Optional | Default / Empty Behavior | Validation Rules (if any) |
| --- | --- | --- | --- | --- |
| semantic_constraints.must_include | Tag input (multiselect) | Optional | Empty → `[]` | Each tag is plain text; trim per tag |
| semantic_constraints.must_avoid | Tag input (multiselect) | Optional | Empty → `[]` | Each tag is plain text; trim per tag |
| semantic_constraints.required_mentions | Tag input (multiselect) | Optional | Empty → `[]` | Each tag is plain text; trim per tag |

### StylisticPreferences
| Intent Field (fully qualified) | UI Control Type | Required / Optional | Default / Empty Behavior | Validation Rules (if any) |
| --- | --- | --- | --- | --- |
| stylistic_preferences.humor_level | Dropdown + “custom” text | Optional | Empty → `null` | If dropdown uses custom, accept provided text; otherwise selected option |
| stylistic_preferences.formality | Dropdown + “custom” text | Optional | Empty → `null` | If dropdown uses custom, accept provided text; otherwise selected option |
| stylistic_preferences.narrative_voice | Dropdown + “custom” text | Optional | Empty → `null` | If dropdown uses custom, accept provided text; otherwise selected option |

## Notes on Extensibility
- Adding new intent fields requires updating this contract before UI support.
- The UI may not capture or submit undocumented fields.
- Control types must follow this contract; no silent deviations are allowed.
