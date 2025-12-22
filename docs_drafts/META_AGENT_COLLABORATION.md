# **Meta-Agent Collaboration Framework**

*A Deterministic Workflow for Human–LLM–Tool Systems*
**Author:** Andreas Atle
**Co-Author (Planner):** ChatGPT
**Year:** 2025

---

# **1. Overview**

This document describes a **deterministic, state-driven method** for collaborating with LLMs during complex software development.

The method establishes strict roles for:

* **Human (Meta-Supervisor)**
* **ChatGPT (Meta-Planner)**
* **Codex or equivalent (Worker Tool)**
* **Human + ChatGPT (Meta-Critic)**

It emerged naturally during development of a runtime **Planner → Worker → Critic → Supervisor** agent framework, and eventually **mirrored that architecture exactly**.

This whitepaper defines the methodology so it can be reproduced and reused in other projects.

---

# **2. Motivation**

Long-running LLM collaborations typically suffer from:

* context drift
* incorrect assumptions carried across sessions
* hallucinated architecture
* inconsistent role boundaries
* lack of deterministic grounding

This framework eliminates those failure modes by:

* externalizing all state
* enforcing strict role separation
* using deterministic iteration cycles
* mirroring proven agentic patterns at the meta-layer

---

# **3. Meta-Agent Roles**

## **3.1 Meta-Supervisor (Human)**

Responsibilities:

* define goals
* define constraints / invariants
* accept or reject work
* maintain the authoritative project snapshot
* execute tools (Codex, scripts)

Equivalent to runtime **Supervisor**.

---

## **3.2 Meta-Planner (ChatGPT)**

Responsibilities:

* read the **authoritative snapshot**
* reconstruct full context from code only
* generate deterministic patch tasks
* formulate Codex-ready prompts
* request tools, but never execute them

Equivalent to runtime **Planner**.

---

## **3.3 Worker (Codex or Code Transformer)**

Responsibilities:

* execute patches deterministically
* apply diffs or create code from Planner instructions
* produce exact, inspectable artifacts

Equivalent to runtime **Worker**.

---

## **3.4 Meta-Critic (Human + ChatGPT)**

Responsibilities:

* evaluate correctness
* check invariants
* detect drift
* request refinements

Equivalent to runtime **Critic**.

---

# **4. Explicit External State**

LLMs cannot maintain reliable state across sessions, so this framework uses a **single external state artifact**:

## **`combined_project.md`**

Generated regularly by a snapshot builder script.

Contents:

* Bootstrap Prompt for ChatGPT
* Authoritative state banner
* Entire concatenated source tree
* Deterministic, reproducible context

Sample header:

```text
# === AGENTIC PROJECT SNAPSHOT ===
# authoritative_state: true
# instruction: This file supersedes ALL prior sessions.
# instruction: ChatGPT must reconstruct its entire understanding SOLELY from this file.
```

This guarantees:

* no stale memory
* no hallucinated structure
* deterministic grounding for every session

---

# **5. Meta-Agent Control Loop**

This collaboration follows a precise, deterministic loop:

```
1. Supervisor (Human)
   → defines change
   → updates snapshot if needed

2. Planner (ChatGPT)
   → reads snapshot
   → generates structured patch tasks
   → issues Codex-ready instructions (tool requests)

3. Worker (Codex)
   → executes patch deterministically

4. Critic (Human + ChatGPT)
   → verifies correctness
   → enforces constraints
   → accepts or requests revision

5. Supervisor updates snapshot
   → loop continues
```

This mirrors the runtime cycle:

```
Planner → Worker → Critic → Supervisor
```

---

# **6. Emergent Self-Similarity (Corrected with Tool Semantics)**

A key discovery:
As the runtime system gained structure — especially **ProjectState** — the collaboration itself began to adopt identical structure at the meta-level.

### **Runtime tool semantics**

* Workers **request** tools
* Supervisor **executes** tools

### **Meta-level tool semantics**

* ChatGPT (Meta-Planner) **requests** Codex execution via patch instructions
* Human (Meta-Supervisor) **executes** Codex or scripts

This creates a perfect mapping:

| Concept              | Runtime                  | Meta-Level                         |
| -------------------- | ------------------------ | ---------------------------------- |
| Tool Request         | Worker → ToolRegistry    | ChatGPT → Codex-ready instructions |
| Tool Execution       | Supervisor executes tool | Human runs Codex / scripts         |
| Deterministic Output | tool output              | Codex patch                        |

This symmetry emerged naturally, not by design.

The introduction of ProjectState triggered the adoption of **full authoritative snapshots** in the meta-workflow. The architecture being built effectively “taught” the collaboration how to operate.

---

# **7. Tools**

### **7.1 Snapshot Builder Script**

Generates the authoritative project snapshot:

* concatenates all `.py` files under `src/`
* includes Bootstrap Prompt
* outputs a single Markdown file

Although ChatGPT wrote the script, **the Meta-Supervisor executes it**, preserving role boundaries.

---

### **7.2 Bootstrap Prompt**

Defines operational constraints for ChatGPT:

* enforce Planner–Worker–Critic boundaries
* avoid hallucinated refactors
* maintain domain independence
* interpret only the snapshot
* reject stale assumptions

This is conceptually similar to setting runtime agent prompts.

---

# **8. Benefits**

* deterministic LLM behavior
* reproducible sessions
* no hidden context
* reduced drift
* stable architectural development
* strong schema enforcement
* clean separation of responsibilities

---

# **9. Limitations**

* requires disciplined snapshot updates
* Worker quality affects convergence
* large projects need chunking strategies
* meta-criticism remains partially manual

---

# **10. Conclusion**

This methodology provides a robust, scalable, and deterministic approach to complex software development with LLMs.

By externalizing state and mirroring the runtime agent architecture at the meta-layer, the workflow achieves:

* stable progress,
* clear role boundaries,
* minimized hallucination,
* architecture-level coherence.

It is recommended for:

* agentic frameworks
* long-lived codebases
* structured refactoring pipelines
* multi-component systems
* any environment where LLM consistency is critical

