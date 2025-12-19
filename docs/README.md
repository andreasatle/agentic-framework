# Documentation Structure

This directory contains **two distinct classes of documentation** with different purposes and guarantees.

Understanding this split is essential to understanding the project.

---

## 1. `contracts/` — Normative, Enforced Documentation

The `contracts/` directory contains **authoritative documents** that define how the system is allowed to behave.

These documents are:

- Normative (they define rules, not ideas)
- Enforced by convention and review
- Stable and intentionally minimal
- Used as guardrails for future development

If code, prompts, or behavior conflict with anything in `contracts/`,
**the contract documents take precedence**.

Changes here represent architectural decisions.

Typical contents include:

- Document–Writer contracts
- Convergence and termination guarantees
- Authority and control boundaries

---

## 2. `_drafts/` — Exploratory, Non-Authoritative Material

The `_drafts/` directory is reserved for **working material**, such as:

- Task dumps
- Planning notes
- Iteration logs
- Prompt experiments
- Half-formed or superseded ideas

These documents:

- Are not normative
- May be inconsistent or incomplete
- May contradict each other or current behavior
- Exist to support thinking, not enforcement

### Important

Files under `_drafts/` are **not committed to the repository**.

They are intentionally excluded to prevent exploratory material from being
mistaken for architectural truth.

---

## Design Principle

This split exists to prevent loss of control under high-velocity,
agent-assisted development.

- **Contracts define what must be true**
- **Drafts capture how thinking evolved**

Only one of these is allowed to constrain the system.

---

If a rule or guarantee is not documented under `contracts/`,
it is not considered binding.

## Text Prompt Refiner (Contract)
The text prompt refiner exists solely to normalize messy human input into a cleaner version of the same text. It is semantic-preserving, advisory-only, and non-authoritative. It must not invent intent, extract intent, plan, execute, create structure, or generate documents; its role is distinct from intent extraction and limited to tidying input before downstream use.
