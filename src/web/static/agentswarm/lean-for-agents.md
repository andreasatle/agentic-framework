# Lean for Engineers: From Lean 1 to Lean 4 and mathlib, and Why Proof Assistants Suit Agents

## Opening case: a claimed Lean proof of the Riemann Hypothesis

In November 2026, Levent Alpöge, a mathematician at Anthropic, claimed that he had, working with Claude, discovered a proof of the Riemann Hypothesis[^1].
He posted the proof coded in Lean, a programming language and proof assistant that checks the mathematical correctness of each argument[^1].
The Lean proof was re-checked by the Lean kernel, which is Lean's small trusted checker that accepts or rejects a finished proof, with only the three standard axioms, which are the base assumptions the proof is allowed to rely on, as Sutherland reports[^2].
This is a claim, reported by news outlets, not a settled result[^1].

Alpöge initially checked the work by writing it out in Lean, and a Lean-coded proof that compiles error-free is usually taken as confirmation that each step's logic is correct[^2].
Andrew Sutherland of MIT independently compiled the result in Lean without issues[^2].
Hector Pasten and Carlo Pagano judged the impact conditionally, saying 'if the proof is correct' or 'if true'[^1].

The open questions concern something else.
Kevin Buzzard of Imperial College London asked what the statement of the theorem in the Lean code is, and whether it corresponds to the actual theorem[^2].
A comparator run, an independent re-check that the code does not redefine the meaning of symbols in the statement, was still awaited when the report was written[^2].

This case raises the tutorial's central questions.
What does 'it compiles in Lean' guarantee, and what does it leave unchecked, such as whether the Lean statement says the intended theorem?
Why would a machine-checkable format change how we trust AI-generated mathematics, when a fluent informal argument can look convincing without being checked?

## What a proof assistant is and why you can trust its output

A formal proof is a mathematical proof that has been exhaustively checked at the level of the foundations of math and the fundamental rules of logic, and this is generally done by computer[^3].
An informal proof is the prose argument mathematicians write and referees read.
Lean is both an interactive theorem prover, based on dependent type theory, and a pure functional programming language[^4].
Lean is primarily implemented in itself, and its elaborator turns source text into core terms that the kernel checks[^4][^3][^4][^3].
The proof scripts in Lean are parsed and go through a process called elaboration, described as a sort of compilation process for mathematics, and then the Lean kernel checks the output of elaboration[^3].
For a programmer, the closest picture is a compiler that elaborates source text and then hands the result to a small checker[^3].

Consider $\forall (p\,q : \mathrm{Prop}), p \land q \to q \land p$, where $\mathrm{Prop}$ is the type of propositions, and this statement is itself a type.
A term of that type is a proof of the proposition, so checking a proof is type checking.
A term $\lambda\, p\, q\, h \Rightarrow \langle h.2, h.1\rangle$ of that type is a proof that conjunction commutes: $h$ is a proof of $p \land q$, and the angle brackets build a proof of $q \land p$ from its two halves.
The kernel never needs to know how the term was found[^4].

The core of Lean is a minimal kernel that does nothing other than check proof terms[^4].
The kernel is several thousand lines of C++, and it is the part that must reject any false proof[^3].

Tactics are proof-search commands written inside a proof.
Each tactic produces a term in the core type theory that the kernel then checks, so bugs in tactics do not threaten the soundness of Lean as a whole[^4].
This is like a compiler whose optimizer may be wrong while its type checker still rejects invalid output.

The tactic language is user-extensible, and tactics are written in Lean itself and can be used immediately upon definition, without rebuilding the prover[^4].

Theorem Proving in Lean 4 begins with dependent type theory, then covers propositions and proofs, quantifiers and equality, and tactics[^5].
It then moves to interacting with Lean, inductive types, induction and recursion, structures, and type classes, and ends with axioms and computation[^5].

## What Lean checks and what it does not: the statement problem and reliability

A Lean-coded proof that compiles error-free is usually taken as confirmation that the logic of each step is correct, but compilation does not settle whether the formal statement is the intended one[^2].
Buzzard asks what the statement of the theorem in the Lean code is, and whether it corresponds to the actual theorem statement[^2].
Hales holds that a Lean proof should not be accepted until a human audit confirms statement fidelity, a task he calls generally much easier than checking the proof itself[^3].
A verified proof, a correct formalization of a statement and a mathematical insight are three different things, and the kernel certifies only the first.

Errors can hide in definitions, axioms and trusted components such as the kernel and runtime[^3].
The kernel does nothing other than check proof terms, and each tactic produces a term that the kernel checks, so a buggy tactic does not by itself threaten soundness[^4].
Hales calls a soundness bug, a kernel bug that allows a proof of False, the most disastrous kind of bug in a proof assistant[^3].
Hales's assessments are presented as expert opinion, such as his statement that in his view a result of fundamental importance must be given in full before it is accepted[^3].

The following is an illustration, not a case taken from a source: suppose a file defines a symbol `double` as `n + n` but the author meant `n * n`, and then proves the theorem `double 3 = 9`.
The checker accepts only proofs of what is stated, and $3 + 3 = 6 \neq 9$, so this false claim is rejected, but a theorem about a symbol defined differently from its intended meaning can still be accepted, so the reader must read the definition to see what was proved.

- Read the theorem statement and compare it with the intended mathematical claim[^2].
- Check each definition the statement uses, such as the reals, derivatives and measures[^3].
- Check for unauthorized axioms, which the comparator tool can inspect[^3].
- Check for redefined symbols and compilation with several kernels in a comparator run, which is still awaited[^2].

## How Lean evolved: from Lean 1 to Lean 4

The title promises a Lean 1, but the sources do not describe a Lean 1 edition, so this section starts with the work they do describe.
Lean began in 2013 as an interactive theorem prover based on the Calculus of Inductive Constructions[^6].
In 2017, using Lean 3, a community of users started the mathlib library[^6].
The early editions of Theorem Proving in Lean were written for Lean 2, and the current edition assumes Lean 4, specifically version 4.33.0[^5].

The authors credit Lean 3's success mainly to its extensibility and metaprogramming[^6].
Users could not modify many parts of the system without changing the C++ source code[^6].
Many Lean 3 automation metaprograms were not competitive with tools written for efficient compilers, mainly because of virtual machine interpretation overhead[^6].

Lean 4 is a reimplementation of Lean in Lean itself, which the authors say addresses many shortcomings of the previous versions[^6].
Users can modify the parser, the elaborator, the tactics, and the code generator[^6].
Its hygienic macro system, which avoids accidental name capture, was custom-built for interactive theorem provers[^6].
A prover that is also a general-purpose language can host its own automation, because a tactic is ordinary Lean code that can be compiled efficiently[^6].

The mathlib authors describe a backward-only instance search that can explore the whole structure hierarchy[^7].
They said Lean 4 is expected to make improvements in efficient graph traversal[^7].
Lean 4's authors report a new tabled type class resolution procedure, which they present as addressing these performance problems[^6].

The sources separate expectation from delivery: the 2020 mathlib paper says Lean 4 is expected to improve graph traversal, while the Lean 4 system description reports the new type class procedure as implemented[^7][^6].
The Lean 4 paper says it was released at the beginning of 2021 and that the community was already porting mathlib[^6].
The Lean community site states that mathlib has grown by more than an order of magnitude since the 2020 article[^8].

## mathlib: a shared library of mathematics and why it matters

Every major proof assistant has at least one library that can serve as a base for further formalizations, though these libraries differ widely in contents, organization and purpose[^7].
mathlib is a community-driven effort to build a unified library of mathematics formalized in Lean, and it also contains definitions useful for programming[^8].
Its design rests on dependent types, a focus on classical mathematics, an extensive hierarchy of structures, large- and small-scale automation, and a distributed organization[^7].

Type classes are predicates or extra data attached to types, inferred by a Prolog-like backtracking search[^7].
Here $\alpha$ is a type variable, standing for any type, and $\texttt{has\_mul}\ \alpha$ is the class asserting that $\alpha$ has a multiplication operation.

The worked case is in the discussion of problems with type classes: given $G : \texttt{group}\ \alpha$ in the context, a search for $\texttt{has\_mul}\ \alpha$ may explore upward through the entire structure hierarchy, looking for $\texttt{monoid}\ \alpha$, $\texttt{ring}\ \alpha$, $\texttt{field}\ \alpha$ and $\texttt{normed\_field}\ \alpha$, prompting a search for $\texttt{has\_norm}\ \alpha$, before eventually failing and attempting $\texttt{group}\ \alpha$ instead[^7].
Instance searches are performed exclusively backward, reasoning from the goal back through instances, and they can take hundreds of thousands of steps through mathlib's thousands of instances[^7].
The authors propose that reasoning forward from $\texttt{group}\ \alpha$ to $\texttt{monoid}\ \alpha$, $\texttt{semigroup}\ \alpha$ and $\texttt{has\_mul}\ \alpha$, and then working backward from the goal, would find the solution quickly, and they expect Lean 4 to improve graph traversal[^7].
Diamonds are common, because the structure hierarchy is far from being a tree[^7].

The library is organized as an open-source community project with 11 maintainers, and many of its contributors come from pure mathematics[^7].
The library has grown by more than an order of magnitude since the 2020 article appeared[^8].
Whether a single unified library makes AI training feasible is an inference from this design, not a result these sources report.

## Evidence that it scales: Liquid Tensor, Fermat's Last Theorem and beyond

In December 2020 Fields Medallist Peter Scholze challenged the computer proof community to formally verify a new theorem of himself and Dustin Clausen, the Liquid Tensor Experiment[^9].
In 2022 Johan Commelin, assisted by Adam Topaz and others, announced that the Lean formalisation was complete[^9].
Buzzard, who was personally involved, gives his account on his blog and says it is his personal take, not the position of all the authors or of the Lean and mathlib communities[^9].
He reports that formalising the statement of Theorem 9.4 took about one month and its proof about five months[^9].

The Fermat's Last Theorem project, led by Buzzard at Imperial College London, formalises a 21st-century version of the proof that incorporates later developments[^10].
It is organised with Patrick Massot's blueprint software, which creates a map of the theorem and LaTeX documentation of the proof[^10].
The Liquid Tensor project's blueprint, written by Commelin and Massot, is a hybrid part-Lean, part-LaTeX document that goes into much of the detail of the proof[^9].
In the dependency map, clicking a rectangle (definition) or an oval (theorem) shows a LaTeX statement and a link to the corresponding Lean code[^9].
Buzzard reports that different people can work on different areas of a formalisation without knowing what others are working on[^9].

Thomas Hales, in a guest post on Terence Tao's blog, lists formalized theorems including the Kepler conjecture, the four-colour theorem, the Feit-Thompson theorem and Fermat's Last Theorem[^3].
These are reports by project participants, so they show what the teams say they built rather than an independent audit.

## Why Lean suits agentic workflows

An agent that writes Lean code can run a simple loop: it proposes a step, asks Lean to check it, reads the feedback, and tries again[^11].
The check is the valuable part, because Lean's verdict is exact and automatic, with no human grader needed[^11][^4].
Each tactic produces a term that the kernel checks, so a faulty tactic cannot make Lean accept a false theorem[^4].

The sources treat proving as a decision problem: the agent observes the tactic state, the hypotheses and open goals at a point in the proof, and proposes a tactic as a text string[^11].
The environment executes the tactic and moves to a new state, so each (state, tactic) pair records a situation and the tactic tried in it[^11].
AlphaProof received a reward of $-1$ per tactic, so a longer proof accumulates a more negative total and shorter proofs score higher[^11].

AlphaProof, which its authors describe as an AlphaZero-inspired agent, was trained by reinforcement learning on about 80 million auto-formalized Lean problems, formal statements produced by AI translation of informal problems[^11].
Each learner batch was 10% from the Mathlib supervised dataset and 90% from a replay buffer of proofs and disproofs collected from the actors[^11].
The policy head, the part of the network that suggests the next tactic, was trained with a cross-entropy loss[^11].
For hard problems, test-time RL trains on a curriculum of synthetic problem variants, such as simplifications or generalizations, generated around the target problem[^11].

Reported experimentally: at the 2024 IMO, AlphaProof solved three of the five non-geometry problems, including P6, and AlphaGeometry 2 solved the geometry problem[^11].
The combined system scored 28 of 42 points, one below the gold threshold, with multi-day computation[^11].
The authors hypothesize that research mathematics requires theory building, a considerable next step beyond competition problems[^11].

Autoformalization is needed because formal problems written by humans are far scarcer than natural-language ones[^11].
It can fail on fidelity: the authors note that each auto-formalized statement is a valid formal problem regardless of how faithful it is to the original[^11].
Hales argues that a human audit of statement fidelity is needed beyond kernel checking[^3].

The Riemann Hypothesis claim is an agent-produced artifact of this kind, reported as a Lean-coded proof built with Claude[^1].
Lean can check such an artifact mechanically, but a passing check shows only that the proof matches the stated theorem, not that the formal statement matches the intended one[^3].

## Side by side: approaches compared

This section compares five approaches on trust basis, cost, scalability, failure modes, and what each adds beyond the one before.
Design facts are separated from the authors' claims.

- Informal proof checked by human referees: trust rests on expert reading, and the Lean sources give no figure for its failure rate or referee cost.
- LLM-generated informal proof with no formal check: AlphaProof's authors say such text lacks the formal verification needed to guarantee correctness, a claim by the authors[^11].
- Lean-checked proof: the kernel checks proof terms, a design fact, and each tactic produces a term that the kernel checks, so tactic bugs do not threaten soundness[^4].
- Lean-checked proof, caveat: a human audit of statement fidelity is still needed before acceptance, and Tao's post presents that audit as generally much easier than checking the proof itself[^3].
- RL agents trained against Lean: AlphaProof's main RL phase used about 80,000 TPU days, and its TTRL solutions took 2–3 days each, both reported costs; Lean-verified outcomes serve as grounded feedback[^11].
- Lean and mathlib versus other systems: the 2020 paper claims mathlib uniquely combines dependent types, classical mathematics, a large structure hierarchy and automation, though its automation is still incipient[^7].

The Riemann Hypothesis case shows the limit of this comparison: Lean compilation was checked by Sutherland and others, yet the statement check remained open, as Scientific American reported[^2].

## Summary and check-your-understanding questions

Lean's kernel is a small trusted program, and each tactic produces a term that the kernel checks, so bugs in tactics do not threaten soundness[^4].
A compiled proof shows that the proof is correct for the stated theorem, not that the stated theorem is the one you intended[^3].
Tao says a Lean proof should not be accepted until a human audit checks statement fidelity[^3].
Lean 4 reimplements Lean in itself, which the authors say addresses many shortcomings of earlier versions[^6].
Mathlib's type classes and deep hierarchy of algebraic structures let results be reused and automated[^7].
Participants report the Liquid Tensor Experiment and the Fermat's Last Theorem formalization as large-scale successes[^9][^10].
AlphaProof reports olympiad-level results from reinforcement learning against Lean[^11].

- Why can a buggy tactic not make Lean accept a false theorem?
- What does a compiled Lean proof not tell you about whether it proves the intended statement?
- Why did Lean 4 reimplement Lean in itself?
- Why does a unified library help automation and learning?
- What makes a Lean verifier a good reward signal, and what are its limits?

## References

[^1]: scientificamerican.com (2026). [*Anthropic mathematician claims to prove Riemann hypothesis, most famous problem in all of math | Scientific American*](https://www.scientificamerican.com/article/anthropic-mathematician-claims-to-prove-riemann-hypothesis-most-famous-problem-in-all-of-math/).
[^2]: scientificamerican.com (n.d.). [*The AI Riemann hypothesis proof is almost certainly true, independent mathematicians attest | Scientific American*](https://www.scientificamerican.com/article/the-ai-riemann-hypothesis-proof-is-almost-certainly-true-independent-mathematicians-attest). scientificamerican.com (press).
[^3]: terrytao.wordpress.com (n.d.). [*What mathematicians should know about the Lean Theorem Prover: questions of reliability and AI*](https://terrytao.wordpress.com/2026/10/09/what-mathematicians-should-know-about-the-lean-theorem-proverquestions-of-reliability-and-ai). terrytao.wordpress.com (blog).
[^4]: lean-lang.org (n.d.). [*The Lean Language Reference*](https://lean-lang.org/doc/reference/latest). lean-lang.org (official).
[^5]: leanprover.github.io (n.d.). [*Theorem Proving in Lean 4*](https://leanprover.github.io/theorem_proving_in_lean4). leanprover.github.io (institutional).
[^6]: lean-lang.org (n.d.). [*The Lean 4 Theorem Prover and Programming ...*](https://lean-lang.org/papers/lean4.pdf). lean-lang.org (institutional).
[^7]: The mathlib Community (2020). *The Lean Mathematical Library*. CPP '20 (arXiv preprint 1910.09336). Cited at pages 1, 3, 4, 5, 6, 10.
[^8]: leanprover-community.github.io (n.d.). [*Lean community*](https://leanprover-community.github.io/).
[^9]: xenaproject.wordpress.com (n.d.). [*Beyond the Liquid Tensor Experiment | Xena*](https://xenaproject.wordpress.com/2022/09/12/beyond-the-liquid-tensor-experiment). xenaproject.wordpress.com (blog).
[^10]: lean-lang.org (n.d.). [*Formalizing Fermat's Last Theorem in Lean: A Landmark Mathematical Project — Lean Lang*](https://lean-lang.org/use-cases/flt). lean-lang.org (official).
[^11]: nature.com (n.d.). [*Olympiad-level formal mathematical reasoning with reinforcement learning | Nature*](https://www.nature.com/articles/s41586-025-09833-y). nature.com (scholarly).
