# Why Lean Makes AI Agents Effective at Mathematics, and What Other Fields Would Need to Match It

## The question and the thesis: what is a verifier worth?

Why do AI agents advance fastest where answers can be checked mechanically, as in mathematics and code?
One answer is asymmetry of verification: some tasks are much easier to check than to solve[^1].
Wei's verifier's rule says the ease of training AI to solve a task is proportional to how verifiable it is, but this is the author's argument, not a theorem or an experiment[^1].
Lean supplies a formal proof exhaustively checked down to the foundations of mathematics and the fundamental rules of logic[^2].
Trust sits in the kernel, the small checker that accepts or rejects the elaborated proof, so Lean proofs should never be believed until the kernel has checked them[^2].
A soundness bug is a kernel defect that lets the checker accept a proof of False, and hence of any proposition, which makes it the most disastrous kind of bug in a proof assistant[^2].
A human audit is still needed to confirm that the stated theorem is the intended one[^2].

The thesis is that a cheap, trustworthy verifier supplies a training signal, guides search, and supports trust in the result.
Each field must ask what plays the verifier role there, and how cheap, trustworthy and hard to game it is.
Each claim is labelled as proven, shown by experiment, or the authors' hypothesis.

## What Lean actually gives an agent

Lean is one system that serves as both a general-purpose programming language and a mathematical language[^2].
A formal proof is a mathematical proof that has been checked at the level of the foundations of mathematics and the fundamental rules of logic[^2].
Proof scripts are parsed and elaborated, a compilation-like step, and then the kernel, the small trusted core that checks the elaborated output, accepts or rejects them[^2].
Proofs should never be believed until the kernel has checked them[^2].

A user builds a proof by applying tactics, which are small programs that manipulate the proof state, the set of hypotheses and goals[^3].
The illustration below is the tutorial's own, not a source quote: the state shows a hypothesis and a goal, the tactic is simp, and a failing tactic returns an error naming the goal it could not close.

$$
\begin{array}{ll}\text{state:} & n : \mathbb{N} \\ \text{goal:} & n + 0 = n \\ \text{tactic:} & \texttt{simp} \\ \text{result:} & \text{goal closed} \\ \text{failure, e.g.:} & \text{error: unsolved goal } n + 0 = n\end{array}
$$

LeanDojo turns Lean into a gym-like environment in which the prover can observe the proof state, run tactics and receive feedback on errors or on proof completion[^4].
Repository tracing extracts theorems, proof states, tactics and premises from Lean repositories as structured training data[^4].
Agents can use whole-proof generation, which produces a complete proof at once, or proof search, which generates tactics one at a time while interacting with the state[^4].
Mathlib holds nearly 300,000 theorems, and any result in it can be cited when proving further theorems[^2].
AlphaProof auto-formalized about 1 million natural-language problems into around 80 million formal Lean problems, each a valid problem that can be attempted[^3].

Lean guarantees that an accepted proof is valid for the theorem as stated[^3].
It does not guarantee that the stated theorem is the right one, so a human must audit statement fidelity[^2].
Even the trusted core has had soundness bugs, which Tao reports were repaired in 2026[^2].

## Asymmetry of verification: why checking beats solving

Asymmetry of verification is the idea that some tasks are much easier to verify than to solve[^1].
Sudoku and crossword puzzles take long to solve, because one must try many candidates against constraints, yet checking a given solution is trivial[^1].
Some tasks are near-symmetric, such as adding two 900-digit numbers, where checking takes about as much work as solving[^1].
Others are harder to verify than to propose, such as fact-checking every statement in an essay[^1].

Wei's verifier's rule states that the ease of training AI to solve a task is proportional to how verifiable the task is, so tasks that are possible to solve and easy to verify will be solved by AI[^1].
Verifiability is judged by five properties: objective truth, fast verification, scalable verification, low noise and continuous reward[^1].
The rule predicts where reinforcement learning will succeed, because the ability to verify solutions is equivalent to the ability to create an RL environment[^1].
This is the author's argument, not a theorem or a controlled experiment.

Applied to mathematics, a formal proof is checked exhaustively at the level of the foundations and the rules of logic, generally by computer[^2].
Finding a proof is the hard part, while checking a formal proof is cheap, since the kernel verifies each step mechanically[^2].
The checker is itself software, however, and soundness bugs have been found in Lean[^2].

## Verifiable rewards: turning a checker into a learning signal

Reinforcement learning with verifiable rewards (RLVR) is a paradigm in which an LLM acts as a policy, generating a chain of thought (CoT) as a sequence of actions and receiving feedback on answer correctness from deterministic verifiers[^5].
The paradigm promises that models learn from experience through free exploration[^5].

Wen et al. set the reward as binary and determined solely by answer correctness: $R(y_i)=I_{\mathrm{Ans}}(a_i)$, where $y_i$ is a sampled response, $a_i$ its final answer, and $I_{\mathrm{Ans}}(a_i)$ is 1 if the answer is correct and 0 otherwise[^5].
Answers are verified programmatically, whereas chains of thought are hard to verify[^5].

Group relative policy optimisation (GRPO) scores each response against a group of $G$ samples for the same prompt[^5].
The group-relative advantage is $\hat{A}(y_i)=(R(y_i)-\mu_Y)/\sigma_Y$, where $\mu_Y$ is the group mean reward and $\sigma_Y$ is the group standard deviation of rewards[^5].
If every response in a group is correct, then $\sigma_Y=0$ and the normalised advantage is undefined, so the prompt teaches nothing[^5].

Pass@k is the chance that at least one of $K$ sampled attempts is correct, computed per prompt as $1-\binom{G-C}{K}/\binom{G}{K}$, where $C$ is how many of the $G$ samples have a correct answer[^5].
The debate arises from conflicting observations, and Yue et al. hypothesise that RLVR only reweights reasoning paths already in the base model[^5].
To separate lucky answers from sound reasoning, Wen et al. introduce CoT-Pass@K, which counts a sample only when both its chain of thought and its final answer are correct[^5].

Theorem 1 assumes a logic prior, meaning correct chains are more likely to yield correct answers: $\alpha=P(I_{\mathrm{Ans}}=1\mid I_{\mathrm{CoT}}=1)>\beta=P(I_{\mathrm{Ans}}=1\mid I_{\mathrm{CoT}}=0)$[^5].
Under this assumption the expected advantage is positive for correct chains and negative for incorrect ones, so the policy gradient raises the probability of correct chains; this is a theoretical result about the expected update for large groups, not a guarantee of generalisation[^5].

Shown by experiment, DAPO-Qwen-32B keeps a CoT-Pass@K gap over its base model on AIME 2024 and AIME 2025, which are competition mathematics problem sets, up to K=1024[^5].
On code, AceReason-Nemotron-7B improves Pass@K over DeepSeek-R1-Distill-Qwen-7B on most LiveCodeBench versions[^5].
The authors conjecture that distilled models gain little on math Pass@K because they already master what answer rewards can teach[^5].

AlphaProof applies a formal verifier to the same loop: Lean-verified outcomes give grounded feedback, and each tactic earns a reward of $-1$, so the agent is pushed toward short verified proofs[^3].
A formal reward cannot be fooled by a lucky final answer, because the Lean kernel verifies that the generated proof term is a valid construction[^3].
The check confirms only the formal statement that was written, so the statement itself must be right.

## Search against a verifier: from best-first search to test-time RL

Proof search in Lean can be seen as a tree, where each node is a tactic state and each edge is a tactic applied to it, and the Lean checker accepts or rejects each move[^3].
A policy proposes candidate tactics, and a value function estimates the expected return from a state[^3].
In AlphaProof the return is the negative number of tactics still needed, so the value is a count of remaining steps[^3].
These outputs guide a specialized tree search that executes sequences of tactics and evaluates their consequences[^3].

Best-first search (BFS) expands the highest-scoring open node next, and BFS-Prover applies it to LLM-based Lean proving as an alternative to the value-function and MCTS approaches of earlier systems[^6].
A path's probability is the product of its tactic probabilities, so its log-probability is the sum of one negative term per tactic.
A raw sum therefore favours the shortest path, and dividing by the number of tactics gives a per-step average that compares paths of different depth.
BFS-Prover uses this length normalisation to encourage exploration of deeper proofs[^6].

Expert iteration is a loop in which the current prover attempts problems, keeps the proofs the checker verifies, retrains, and repeats.
BFS-Prover's data filtering excludes problems solvable by beam search node expansion, to focus each round on harder cases[^6].
Direct Preference Optimization (DPO) is applied to state-tactic pairs annotated with compiler error feedback, refining the policy to prioritize productive expansions[^6].
BFS-Prover reports 72.95 on the MiniF2F test set, a benchmark result shown by experiment rather than a guarantee[^6].

AlphaProof learns by reinforcement learning from Lean-verified outcomes, trained on about 80 million auto-formalized problems, which addresses the scarcity of human formal data[^3].
Test-time RL handles hard problems by generating synthetic variants of one target problem and learning from them at inference time[^3].
At the 2024 IMO, AlphaProof solved three of five non-geometry problems, a single-competition result at multi-day compute cost[^3].
The authors note that the bespoke learning phase is likely beyond the reach of most academic research groups[^3].

## Discovery without proofs: evaluators in program-search systems

FunSearch and AlphaEvolve pair a language model that proposes candidates with an automatic evaluator that scores them, so the score, not a proof, decides what survives[^7][^8].
FunSearch uses a frozen, pretrained LLM for creative proposals, while the evaluator guards against confabulations and incorrect ideas[^7].
Programs that fail within time and memory limits, or give invalid outputs, are discarded, and the rest return to prompts through an evolving programs database[^7].
An evaluation cascade prunes weak candidates: test cases of increasing difficulty are applied in stages, and a solution advances only if it does well in earlier ones[^8].

The candidate is a program and the evaluator a function returning scores[^7].
Examples include cap sets, bin-packing heuristics, data-centre scheduling and kernel tiling for training Gemini[^7][^8].
Here the verifier checks a score or a construction, not a general proof, and the FunSearch authors note that proof generation falls outside their scope because it is unclear how to provide a rich enough scoring signal[^7].

Shown by experiment, FunSearch found a 512-cap in dimension 8 and raised the cap set capacity lower bound from 2.2180 to 2.2184[^7].
AlphaEvolve matched the best known constructions on about 75% of over 50 mathematical problems and surpassed them on about 20% of them[^8].
A scheduling heuristic recovered on average 0.7% of Google's fleet-wide compute, and a tiling heuristic gave an average 23% kernel speed-up[^8].

The condition is that the evaluator must be automatable[^8].
AlphaEvolve's authors state that its automated evaluation metric is a limitation, because it puts tasks that require manual experimentation out of scope[^8].

## When the verifier is imperfect: specification gaps and reward hacking

Checking a claim against a specification is only as useful as the specification itself.
In Lean, a compiled proof shows that the stated theorem holds, but the source says a human audit must still confirm statement fidelity, asking whether the verified theorem is what we think it is and whether the Lean definitions match what they should be[^2].
The same post calls this check generally massively easier than checking the proof itself[^2].
The Lean kernel is itself a trusted component of several thousand lines of C++, and a soundness bug in it would let a false statement pass[^2].

The reported Riemann hypothesis claim illustrates verification in practice: its author wrote a Lean proof, and other mathematicians then checked it[^9].
Reporters state that a joint Lean and Mathlib statement certified the statement and proof, and that an independent researcher compiled the proof with only the three standard axioms[^9].
These confirmations come from a news report on a developing story, so they are reported rather than established by this tutorial[^9].

Reward hacking occurs when optimising a proxy lowers true performance[^10].
The survey separates verifier failure, where the grader credits criteria a reference panel rejects, from rubric under-specification, where even a perfect grader optimises an incomplete rubric[^10].
Mitigations include stronger verifiers, rubric dropout at 30 to 50 per cent, and cross-family reference panels, with divergence between training and reference scores as a detection signal[^10].
The survey's practitioner checklist is a synthesis and set of recommendations, not an empirically validated protocol[^10].

## Software: tests, benchmarks and formal checks as verifiers

In software, the verifier is usually a test suite run by execution.
In SWE-bench, a model receives an issue and a codebase and must produce a patch, which is applied and judged by the repository's tests; an issue counts as resolved only if the patch applies and all associated tests pass[^11].
The best model at publication, Claude 2, resolved only 1.96% of the 2,294 instances[^11].
A test-based signal is weaker than a proof, because tests check only the behaviours they exercise.
Model-generated patches that applied correctly were shorter than gold patches (30.1 lines against 74.5) and rarely edited more than one file[^11].

One route to a stronger check is to verify an agent's reasoning rather than only its final output.
The method extracts a formal representation of the agent's response and uses formal verification and program analysis tools to check its reasoning steps[^12].
On 20 uninitialized-variable errors the verifier validated the reasoning in 13 cases, and on program equivalence queries it caught 6 of 8 cases where the agent hallucinated[^12].
These small-scale results show feasibility only, not that the approach scales to large codebases[^12].
The results come from a secondary Emergent Mind summary of an arXiv preprint, not from the paper itself[^12].

Verification-first engineering treats verifiability as a first-class design objective, with problems decomposed into explicit, testable behavioural claims, and it exploits solve-verify asymmetry by identifying tasks where checking is much easier than solving[^13].
This is the authors' position, not a measured result.

Wei's lens asks whether a task has objective truth, is fast and scalable to verify, has low noise and offers a continuous reward[^1].
Under it, a program with ample test cases is easy to verify, while a long essay can be hard to verify, since it can take longer to fact-check all its statements than to write the essay[^1].
Wei's verifier's rule is his argument, not a theorem or an experiment[^1].

## Side-by-side comparison of the main approaches

The table compares six approaches by what each verifier checks, how much trust it earns, what its feedback costs, how it is used, where it fails and what kind of evidence supports it.

- Lean (BFS-Prover, AlphaProof): formal proofs are checked by the Lean kernel, so a proof is valid for the stated theorem, and the feedback is tactic-level, with compiler errors per step[^6][^3].
- Answer-checking RLVR (math and code): the reward checks only the final answer, is cheap and binary, and fails when a lucky answer is rewarded[^5].
- Program search (FunSearch, AlphaEvolve): the evaluator scores a candidate construction, and the scores are used for evolution and filtering, with the main limit that the evaluation must be automatable[^7][^8].
- Software repair (SWE-bench): the patch is judged by the repository's tests, and a patch can apply yet remain incomplete[^11].
- Formal code-reasoning verification: formalised agent reasoning steps are checked after the fact, and the main failure mode is missing predicates or code, with small-scale experiments only[^12].
- Rubric/LLM-judge rewards: weighted criteria are judged by an LLM, the main failure modes are leniency and omitted requirements, and the evidence is surveyed experiments plus a proposed checklist[^10].

Formal guarantees concern the formalised claim, not automatically the intended task[^3].
Rubric recommendations remain hypotheses rather than a validated protocol[^10].

## What would other fields need? Science, engineering and law

The checklist below turns the earlier principles into questions to ask of any field before expecting agents to improve there.

- Is there a checkable specification, so that everyone agrees what a good solution is[^1]?
- Is the checker cheap, so that many candidates can be checked at once[^1]?
- Does the checker give graded feedback, so that many candidates for one problem can be ranked by a continuous reward[^1]?
- Is the reward resistant to gaming, since optimizing a proxy hard enough can make true performance worse[^10]?
- Can many problems be generated, and does program search apply where candidates can be automatically evaluated[^8]?

In science, FunSearch pairs a frozen LLM with an evaluator that guards against confabulations and incorrect ideas[^7].
Its cap set and bin-packing results are experimental evidence, not a general theorem[^7].
Physical experiments and simulators cost more and are less faithful than a scoring function, so their verifiers are slower; this caveat is the tutorial's extrapolation.

In engineering, the verification-first argument separates tasks that can be verified automatically from those needing judgement, and proposes physics-based simulation and digital twins as verifiers[^13].
This is the authors' argument and hypothesis, not a demonstrated result[^13].

Law is not covered by any source, so what follows is the tutorial's own extrapolation.
Rules can be partly formalised, but the interpretive core lacks a mechanical checker.
Rubric or human judgement would stand in, and LLM judges carry the lenient-judge risk described above[^10].

## Summary and questions to check your understanding

A cheap, trustworthy verifier gives a reward for reinforcement learning, a target for search, and grounds for trust[^5][^6][^3].
The reward role appears in the RLVR paper, which uses deterministic verifiers giving answer-correctness rewards[^5].
The search role appears in BFS-Prover, which runs tree search over Lean proofs and uses compiler error feedback in DPO[^6].
Verification is often much easier than solving, which predicts where such a verifier helps most; this is the author's argument, not a theorem[^1].
Imperfect verifiers are exploited, so a specification gap can become a reward-hacking route[^10].

- Why does length normalisation matter in best-first search[^6]?
- Why can answer-only rewards still encourage correct reasoning, and what is evidence versus theory there[^5]?
- What would you need to build a verifier in your own field, and how might it be gamed[^10][^1]?

## References

[^1]: jasonwei.net (2025). [*Asymmetry of verification and verifier’s rule — Jason Wei*](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law).
[^2]: terrytao.wordpress.com (n.d.). [*What mathematicians should know about the Lean Theorem Prover: questions of reliability and AI*](https://terrytao.wordpress.com/2026/10/09/what-mathematicians-should-know-about-the-lean-theorem-proverquestions-of-reliability-and-ai). terrytao.wordpress.com (blog).
[^3]: nature.com (n.d.). [*Olympiad-level formal mathematical reasoning with reinforcement learning | Nature*](https://www.nature.com/articles/s41586-025-09833-y). nature.com (scholarly).
[^4]: leandojo.org (n.d.). [*LeanDojo: AI-Assisted Theorem Proving in Lean*](https://leandojo.org/leandojo.html). leandojo.org (institutional).
[^5]: arxiv.org (2025). [*[2506.14245] Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs*](https://arxiv.org/abs/2506.14245). arxiv.org (scholarly). Cited at pages 1, 3, 4, 5, 6, 7, 8, 16, 17.
[^6]: aclanthology.org (n.d.). [*BFS-Prover: Scalable Best-First Tree Search for LLM-based Automatic Theorem Proving - ACL Anthology*](https://aclanthology.org/2025.acl-long.1565). aclanthology.org (scholarly).
[^7]: nature.com (2024). [*Mathematical discoveries from program search with large language models | Nature*](https://www.nature.com/articles/s41586-023-06924-6).
[^8]: arxiv.org (2025). [*AlphaEvolve: A coding agent for scientific and algorithmic discovery*](https://arxiv.org/pdf/2506.13131). Cited at page 4.
[^9]: scientificamerican.com (2026). [*The AI Riemann hypothesis proof is true, independent mathematicians confirm | Scientific American*](https://www.scientificamerican.com/article/the-ai-riemann-hypothesis-proof-is-almost-certainly-true-independent-mathematicians-attest).
[^10]: huggingface.co (n.d.). [*A Survey and Practitioner Framework for Reward Hacking in Rubric ...*](https://huggingface.co/datasets/sarathkavuru/anthroly-research/resolve/main/papers/reward-hacking-rubric-rl/main.pdf). huggingface.co (commercial).
[^11]: arxiv.org (2023). [*SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*](https://arxiv.org/pdf/2310.06770). Cited at pages 1, 3, 7.
[^12]: emergentmind.com (n.d.). [*Verified Code Reasoning with LLMs*](https://emergentmind.com/papers/2509.26546). emergentmind.com (reference).
[^13]: computer.org (n.d.). [*Engineering Agentic Systems: Toward Verification-First AIware Engineering*](https://www.computer.org/csdl/magazine/so/2026/05/11679552/2jAnqH0PHKE). computer.org (institutional).
