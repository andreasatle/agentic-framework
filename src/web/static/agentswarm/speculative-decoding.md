# Speculative decoding: how a small draft model makes a large model faster with identical output

## Why decoding is slow, and the slack speculative decoding uses

Standard autoregressive decoding is sequential: each new token is sampled from a forward pass that depends on the previous token, so one token needs one full pass through the model[1].
Each pass streams the model's weights from high-bandwidth memory (HBM) into the compute units, and at batch size 1 that data movement dominates the cost while the tensor cores sit largely idle[2, 3].
Arithmetic intensity is the ratio of floating-point operations to bytes moved, and a workload with low intensity is memory-bound[2].
At batch size 1, a decoding step is a matrix-vector product: each weight loaded from memory is used in roughly one multiply-add for one token, so the intensity is only about one FLOP per byte (for 16-bit weights, about one FLOP per two bytes).
Scoring $K$ tokens in one pass turns this into a matrix-matrix product: each loaded weight is reused for all $K$ positions, so the FLOPs grow roughly $K$-fold while the bytes moved stay about the same, and the intensity rises roughly by $K$[2].
For a 70B model on an H100, producing one token takes roughly 30 to 50 milliseconds of work, and most of that time is memory movement rather than arithmetic[3].
Because the linear layers stay memory-bound for small $K$, computing the logits of a short continuation of $K$ tokens in parallel takes a similar time to sampling a single token[1].
The technique rests on two assumptions: processing several draft tokens concurrently is as fast as processing one, and enough draft tokens are validated to advance by more than one token per pass[4].
The first is a first-order approximation that holds only while the pass stays memory-bound, and the second is an empirical property of the drafter and the workload.

## The draft-then-verify algorithm and why the output is provably identical

Speculative decoding runs a cheap drafter ahead of a large target model and lets the target check the drafts in one pass[5].
Write $M_p$ for the target model, with distribution $p(x)$ over the next token, and $M_q$ for the drafter, with distribution $q(x)$; both are conditioned on the prefix, which is omitted from the notation[5].
One step of the algorithm first samples $\gamma$ draft tokens $\tilde{x}_1,\dots,\tilde{x}_\gamma$ from $q$, then scores all $\gamma+1$ positions with the target in one parallel run[5, 6].
A draft token $\tilde{x}_i$ is accepted with probability $\min(1, p(\tilde{x}_i)/q(\tilde{x}_i))$, the ratio of target to draft probability, which is the form the proof below uses[5].
At the first rejection, a replacement is drawn from the residual distribution $p'(x)=\mathrm{norm}(\max(0, p(x)-q(x)))=\frac{\max(0,p(x)-q(x))}{\sum_{x'}\max(0,p(x')-q(x'))}$[5].
The overall acceptance probability is $\beta=\sum_x \min(p(x),q(x))$, and the normalizing constant of the residual is $1-\beta$[5].
If every draft is accepted, one extra token is sampled from the target's own distribution, so each step emits between one and $\gamma+1$ tokens[5, 1].
Losslessness is proven: for a token $x$, the probability of emitting it is the accepted mass $q(x)\min(1, p(x)/q(x)) = \min(p(x), q(x))$ plus the rejection mass $(1-\beta)\,p'(x)$[5].
Since $(1-\beta)p'(x) = p(x)-\min(p(x),q(x))$, the sum is $\min(p(x),q(x)) + p(x) - \min(p(x),q(x)) = p(x)$, so the emitted token is distributed exactly as $p$[5].
The guarantee holds within hardware numerics, because different computation graphs can produce slightly different logits[1].
The acceptance rate is $\alpha = \mathbb{E}[\beta]$, and the identity behind the paper's formula is a short calculation: $|p(x)-q(x)| = p(x)+q(x)-2\min(p(x),q(x))$, so summing and halving gives $\frac12\sum_x|p(x)-q(x)| = 1-\sum_x\min(p(x),q(x))$[5].
Writing $D_{LK}(p,q)=\tfrac12\sum_x|p(x)-q(x)|$ for the total variation distance, this gives $\beta = 1-D_{LK}(p,q)$ and therefore $\alpha = 1-\mathbb{E}[D_{LK}(p,q)]$[5].
Toy example: take a vocabulary of three tokens with $p=(0.5,0.3,0.2)$ and $q=(0.2,0.5,0.3)$.
Then $\min(p,q)=(0.2,0.3,0.2)$, so $\beta=0.7$, and the drafter's token 2 is accepted with probability $0.3/0.5=0.6$.
The residual is $\max(0,p-q)=(0.3,0,0)$, which normalizes to $(1,0,0)$, so every rejection resamples token 1.
Under the simplifying assumption that acceptances are i.i.d. with probability $\alpha$, the number of tokens per step is a capped geometric variable, and its expectation is $\mathbb{E}[\text{tokens}] = \frac{1-\alpha^{\gamma+1}}{1-\alpha}$[5].
With drafter cost ratio $c$, meaning one drafter run costs $c$ times one target run, the expected walltime improvement is $\frac{1-\alpha^{\gamma+1}}{(1-\alpha)(\gamma c+1)}$[5].
Raising $\gamma$ adds tokens per step with diminishing returns and adds drafter cost $\gamma c$, so the best $\gamma$ is found numerically for given $\alpha$ and $c$[5].
Measured results: on T5-XXL the method gave 2.6x (temperature 1) and 3.4x (temperature 0) on translation, and the authors report 2X-3X speed-ups with identical outputs[5].
An independent implementation on Chinchilla 70B reported 2X-2.5X speed-ups[5, 1].
Greedy verification is the temperature-0 special case: the draft is accepted only if it equals the target's argmax, which the survey notes guarantees outputs identical to greedy decoding of the target[6].
The survey frames every method as draft-then-verify: draft several tokens cheaply, verify them in parallel with the target, and keep the accepted prefix plus one corrected token[6].
Per the NVIDIA overview, the rejection step keeps the target's output quality, since any draft diverging from what the target would generate is discarded[7].

## Separate draft models: choosing, training, distilling, and what alignment buys

A small model from the same family and tokenizer can serve as a drafter because hard language-modeling tasks contain easier subtasks that efficient models approximate well[5].
Under the i.i.d. assumption, the token-level acceptance rate equals one minus the total variation distance (TVD) between the draft and target next-token distributions, so a drafter closer to the target is accepted more often[8].

DistillSpec trains the draft with white-box knowledge distillation, which uses the target's logits as the training signal[8].
Its two design choices are on-policy data, meaning training sequences sampled from the draft model itself, and a divergence tailored to the task and decoding strategy[8].
Distillation targets the quantity that drives acceptance, the TVD between draft and target, so training the draft to shrink that distance on its own outputs is a principled route to higher acceptance[8].
The on-policy choice is supported by experiments, not by a proven bound on acceptance.
DistillSpec yielded 10 to 45% speed-ups over standard speculative decoding across benchmarks, with greedy and non-greedy sampling (measured, experiments)[8].
Directly minimizing TVD did not give the best results in most settings, so the authors treat the divergence as a task-dependent hyperparameter[8].

Speed-up depends heavily on the draft model, and draft latency is the key bottleneck[9].
A larger drafter does not necessarily help, because draft accuracy on language modeling correlates weakly with speculative performance[9].
In LLaMA setups, a wider, shallower drafter with the same parameter count gave higher throughput than a deeper one (measured)[9].
Identifying a compact draft model that is well-aligned with the target model is challenging, which is the problem that motivates DistillSpec[8].

## Dropping the separate drafter: Medusa heads and tree attention

Medusa keeps a single model and changes where the drafts come from[2].
It adds several extra decoding heads to the last hidden state of the original model, and the k-th head predicts a token further ahead[2].
Because the heads sit on the target's own representations, no second model must be trained, served, or aligned[2].
Medusa-1 freezes the backbone and trains only the heads, while Medusa-2 trains the heads and backbone jointly with a recipe that protects the backbone's next-token ability[2].
When training data is unavailable or the model has undergone RLHF, the authors propose self-distillation, in which the model generates its own training data[2].

The top-k predictions of the heads are combined into a tree of candidate continuations[2].
Tree attention verifies all candidates in one pass, with a mask that lets each token attend only to its predecessors on its own branch[2].
A tree beats a single chain because each extra branch gives another chance that some candidate matches the target[2].
Extra candidates are cheap only while the pass stays memory-bound; the authors' FLOP analysis reports that linear layers shift from memory-bandwidth-bound to compute-bound as candidate tokens grow, and that speed falls past a point[2].

SpecInfer also verifies a token tree in one pass, but its tree comes from small speculative models[10].
Its depth-first traversal reuses one key-value cache across all token sequences of the tree, and its topology-aware causal mask fuses the tree's attention into a single kernel[10].

Medusa's typical acceptance keeps a candidate token when the original model's probability for it is high enough relative to an entropy-dependent threshold, rather than sampling exactly from the target distribution[2].
The authors state that it is typically unnecessary to match the distribution of the original model[2].
Relaxed acceptance gives up the strict identical-distribution guarantee, while the rejection-sampling variants keep it[2].

At batch size one on Vicuna-7B and 13B, the authors measure speed-ups of 2.18x and 2.33x for Medusa-1 and 2.83x for Medusa-2 on MT-Bench[2].
Quality results are GPT-4 scores on MT-Bench, reported as the authors' own experiments[2].

## EAGLE and successors: drafting in feature space

EAGLE changes what the drafter predicts: it autoregresses over the target's second-to-top-layer features, the hidden state just before the LM head, instead of over tokens[11].
The drafter predicts the next feature, and the target's own LM head then turns that feature into a token distribution from which the token is sampled[11].
Sampling makes the next feature ambiguous, since the prefix "I" can be followed by "always" or "am", and each choice leads to a different feature sequence[11].
EAGLE therefore feeds in the token sequence advanced by one step, which supplies the sampled choice that the feature cannot determine[11].
The drafter reuses the target's embedding and LM head and adds one trainable autoregression head, so the target is unchanged and the output distribution is preserved[11].

EAGLE-2 starts from the observation that a static draft tree assumes acceptance depends only on position, whereas the authors found acceptance also varies with context at the same position (authors' empirical finding)[12].
The drafter's confidence approximates acceptance well: tokens with confidence below 0.05 were accepted about 4% of the time, and those above 0.95 about 98% (authors' empirical finding)[12].
EAGLE-2 therefore grows and reranks the tree by confidence-based values, reaching 3.05x to 4.26x speedup on MT-bench in its comparison table[12].

EAGLE-3 addresses a scaling limit: adding training data helped EAGLE little, which the authors attribute to the feature-prediction loss constraining the drafter (authors' hypothesis)[13].
EAGLE-3 drops feature prediction, predicts tokens directly, fuses low, middle and high-level target features, and uses training-time test to simulate the drafter's own multi-step inputs during training[13].
At test time the drafter consumes its own earlier guesses, which training on true features never shows, so training-time test trains on those guesses too[13].
In an ablation on MT-bench with LLaMA-Instruct 3.1 8B, removing the feature constraint and then adding fused features raised speedup from 3.16x to 4.40x and acceptance length from 4.05 to 6.13[13].
Medusa-style relaxed acceptance is excluded from this lossless comparison, because those methods do not guarantee the output distribution[12].

## No drafter at all: lookahead decoding and prompt lookup

Lookahead decoding removes the drafter by treating decoding as solving a nonlinear system $f(y_i, y_{1:i-1}, x^0)=0$, where $f = y_i - \arg\max P_M(y_i \mid y_{1:i-1}, x^0)$ is zero exactly when the token is the greedy choice[14].
Jacobi iteration, a fixed-point method, updates all positions in parallel from the previous pass's guesses until they stop changing[14].
Plain Jacobi decoding rarely saves steps, because tokens often land in the wrong positions and correct ones are overwritten[14].
The lookahead branch keeps a fixed-size two-dimensional window: the window size $W$ sets how many future positions are decoded in parallel, and the n-gram size $N$ sets how many past Jacobi steps are looked back on to form n-grams[14].
Generated n-grams are cached in an n-gram pool, and a verification branch checks pool candidates in the same step, with $G$ capping how many are checked[14].
Verification is exact for greedy and sampling decoding, while the claim that steps fall roughly linearly in log FLOPs is the authors' scaling argument, not a proof[14].
Measured on A100 GPUs with LLaMA-2 models, greedy speedups are 1.5x to 2.3x[14].
Prompt lookup works like retrieval from a document store: it takes the last few generated tokens, finds the same span earlier in the prompt or previous output, and proposes the tokens that followed it[4].
TensorRT-LLM exposes this as its NGram option, which copies spans from the prompt and previous output as draft tokens, and it gains most where input and output overlap, such as summarization, document QA, multi-turn chat and code editing[4].
The survey measures prompt lookup at about 2.4x on summarization but only 1.1x to 1.3x on translation and question answering[6].
On novel text with few repeated spans, the match finds little to propose, so the method falls back toward ordinary decoding (design reasoning, not a measured result).

## When the speed-up disappears

Speculative decoding saves time only while scoring several drafted tokens in one target pass costs about the same as scoring one, and enough drafted tokens are accepted to pay for drafting[15].
The conditions below break one or both of these.

Large batch size is the first condition: as batch grows the linear layers become compute-bound, which makes verification more expensive[15].
In SGLang on one H100 with LLaMA-Instruct 3.1 8B, EAGLE lost throughput from batch size 24 upward, while EAGLE-3 still gained about 1.38x at batch size 64[13].

Low acceptance is the second condition, read through the expected tokens per verification step[15].
Here $\alpha$ is the acceptance rate, $\gamma$ is the number of tokens the drafter proposes per step, and $\Omega(\gamma,\alpha)=\frac{1-\alpha^{\gamma+1}}{1-\alpha}$ is the expected number of generated tokens per step[15].
Here $T_D$ is the time for one draft pass, $T_V(\gamma)$ is the time to verify $\gamma$ drafted tokens in one pass, and $T_T$ is the time for one ordinary target decoding step[15].
The speed-up is $\Omega(\gamma,\alpha)$ divided by $\gamma T_D/T_T+T_V(\gamma)/T_T$, with the draft-to-target cost ratio $T_D/T_T$ among its factors[15].
Acceptance falls for out-of-distribution tasks, poor alignment, high temperature, and novel text for n-gram drafters[3].

Draft overhead is a further condition, and it is discussed in the section on separate draft models.
At low batch size, a small draft with compressed KV cache can beat self-speculation[15].

Long context with large batch is another condition, where the KV cache dominates the cost of inference[15].
MagicDec's critical sequence length is a theoretical prediction, not a measurement[15].
Measured on 8xA100 with LLaMA-3.1-8B, speed-up rose with batch size beyond about 4000 tokens, and a sparse-KV self-drafter reached up to 2.51x on 8xH100[15].

Hardware and serving setup is another condition: a higher FLOPS-to-bandwidth ratio lowers verification cost, and the H100 gave higher speed-up than the A100 and L40 in the same setting[15].
Batching already amortizes weight loading across requests, so speculation has less memory efficiency left to recover[3].

As a rule of thumb, deploy the technique for low-load latency workloads where the GPU is underutilized, and disable it for workloads that saturate the GPU with concurrent requests[3].
Sources disagree on thresholds, and their numbers come from different hardware and models[3, 15].

## Side-by-side comparison of the main approaches

The table compares the main approaches on the attributes the sources report, though their speed-ups come from different hardware, models and setups and are not directly comparable[6].

| Approach | Draft source | Extra training or model | Verification | Output exactly preserved | Main strength | Main weakness | Reported speed-up (setup-dependent) |
|---|---|---|---|---|---|---|---|
| Separate draft model | Smaller model from the same family | A second model | Chain | Yes, by rejection sampling | Works with any target | Hard to find or align a drafter | Leviathan et al. report results on T5-XXL; Chen et al.'s separate implementation reports 1.9x to 2.5x on Chinchilla 70B[5, 6] |
| Medusa heads | Extra heads on last hidden state | Frozen backbone (Medusa-1) or joint training (Medusa-2) | Tree | No under typical acceptance (relaxed) | No second model | Draft accuracy about 0.6 | About 2.3x to 2.8x at batch size 1[2, 11] |
| EAGLE, EAGLE-2, EAGLE-3 | Features (EAGLE, EAGLE-2); tokens (EAGLE-3) | Lightweight head on the target; EAGLE-2 needs none | Tree | Yes | Draft accuracy about 0.8 | A trained head per target | EAGLE 2.7x to 3.5x on LLaMA2-Chat 70B; EAGLE-2 3.05x to 4.26x[11, 12] |
| Lookahead decoding | Jacobi iteration and n-gram pool | None | N-gram candidates in parallel | Yes, greedy and sampling | No draft model | Gains depend on spare compute | Up to 1.8x on MT-Bench[14] |
| Prompt lookup and n-gram | Recent tokens matched in prompt | None | Chain | Yes under lossless verification | Free and strong on copying | Fails on novel text | About 2.4x on summarization[6, 4] |

For low-batch chat, a trained EAGLE-style head is the strongest measured option, while Medusa's typical acceptance gives up the exact-distribution guarantee[11, 2].
For copy-heavy tasks such as summarization or code editing, prompt lookup can be a simple choice[4].
For high-throughput, long-context serving, sparse-KV drafting (MagicDec) is the approach the sources report as keeping speed-up at large batch sizes, so the workload should be validated directly[15, 13].

## In practice: vLLM, TensorRT-LLM and how it is benchmarked

vLLM sets speculative decoding through one JSON object whose method key names the approach, such as draft_model, ngram, eagle3 or mtp[16].
TensorRT-LLM covers draft-target models, NGram, Medusa, ReDrafter, EAGLE and lookahead decoding, and limits Medusa to Vicuna[4].
Acceptance length $\tau$ is reported alongside speed-up in the ablation tables[13].
Latency at batch size 1 and throughput at large batch can rank methods differently, because spare compute absorbs drafts at batch 1 while extra verification work competes with real tokens at large batch[13].
EAGLE-3's throughput gains shrink as batch size grows[13].
EAGLE-3 results are reported on MT-Bench and GSM8K[13].
SpecInfer reports up to 1.8x over sequence-based decoding at large batch sizes[10].
Vendor blog figures such as the NVIDIA example are illustrative hypothetical timings, not measurements[7].

## Summary and questions to check your understanding

Speculative decoding spends idle compute to cut memory traffic, and it verifies drafts by rejection sampling so that the output keeps the target's distribution[5, 1].
The variants differ mainly in where their drafts come from[11].

- Why is a single-token step of a large model memory-bound, and what does that imply for scoring several tokens at once? (See the section on why decoding is slow[1].)
- Why is the residual distribution $\mathrm{norm}(\max(0, p-q))$ needed after a rejection? (See the section on the draft-then-verify algorithm[5].)
- With acceptance rate $\alpha = 0.8$ and $\gamma = 4$, what is the expected number of tokens per target call under i.i.d. acceptance? (See the section on the draft-then-verify algorithm[5].)
- Why can a tree of candidate continuations beat a single chain of the same depth? (See the section on Medusa heads and tree attention.)
- What does EAGLE condition on that Medusa does not, and why does that help? (See the section on EAGLE and its successors[11].)
- When would speculative decoding slow a high-batch, short-context service down? (See the section on when the speed-up disappears[15].)

## References

1. Chen, C., Borgeaud, S., Irving, G., Lespiau, J., Sifre, L., Jumper, J. (2023). *Accelerating Large Language Model Decoding with Speculative Sampling*. arXiv preprint 2302.01318. Cited at pages 1, 2, 3, 5, 6.
2. Cai, T., Li, Y., Geng, Z., Peng, H., Lee, J. D., Chen, D., Dao, T. (2024). *Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads*. arXiv preprint 2401.10774. Cited at pages 1, 3, 4, 5, 6, 7, 8, 24.
3. GMI Cloud (2026). [*Speculative Decoding for Faster LLM Inference*](https://www.gmicloud.ai/en/blog/speculative-decoding-for-llm-inference-how-draft-models-cut-latency-without-quality-loss). gmicloud.ai (commercial).
4. nvidia.github.io (n.d.). [*Speculative Sampling*](https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html). nvidia.github.io (official).
5. Leviathan, Y., Kalman, M., Matias, Y. (2022). *Fast Inference from Transformers via Speculative Decoding*. arXiv preprint 2211.17192. Cited at pages 1, 2, 3, 4, 5, 6, 7, 8, 11.
6. Xia, H., Yang, Z., Dong, Q., Wang, P., Li, Y., Ge, T., Liu, T., Li, W., Sui, Z. (2024). *Unlocking Efficiency in Large Language Model Inference: A Comprehensive Survey of Speculative Decoding*. arXiv preprint 2401.07851. Cited at pages 4, 5.
7. Li, J. (2025). [*An Introduction to Speculative Decoding for Reducing Latency in AI Inference*](https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference). developer.nvidia.com (official).
8. Zhou, Y., Lyu, K., Rawat, A. S., Menon, A. K., Rostamizadeh, A., Kumar, S., Kagy, J., Agarwal, R. (2023). *DistillSpec: Improving Speculative Decoding via Knowledge Distillation*. arXiv preprint 2310.08461. Cited at pages 1, 5, 8.
9. Yan, M., Agarwal, S., Venkataraman, S. (2024). *Decoding Speculative Decoding*. arXiv preprint 2402.01528. Cited at pages 1, 2, 7.
10. Miao, X., Oliaro, G., Zhang, Z., Cheng, X., Wang, Z., Zhang, Z., Wong, R. Y. Y., Zhu, A., Yang, L., Shi, X., et al. (2023). *SpecInfer: Accelerating Generative Large Language Model Serving with Tree-based Speculative Inference and Verification*. arXiv preprint 2305.09781. Cited at pages 1, 7, 12.
11. Li, Y., Wei, F., Zhang, C., Zhang, H. (2024). *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*. arXiv preprint 2401.15077. Cited at pages 2, 4.
12. Li, Y., Wei, F., Zhang, C., Zhang, H. (2024). *EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees*. arXiv preprint 2406.16858. Cited at pages 3, 4, 7.
13. Li, Y., Wei, F., Zhang, C., Zhang, H. (2025). *EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test*. arXiv preprint 2503.01840. Cited at pages 2, 4, 8.
14. Fu, Y., Bailis, P., Stoica, I., Zhang, H. (2024). *Break the Sequential Dependency of LLM Inference Using Lookahead Decoding*. arXiv preprint 2402.02057.
15. Sadhukhan, R., Chen, J., Chen, Z., Tiwari, V., Lai, R., Shi, J., Yen, I. E., May, A., Chen, T., Chen, B. (2024). *MagicDec: Breaking the Latency-Throughput Tradeoff for Long Context Generation with Speculative Decoding*. arXiv preprint 2408.11049.
16. docs.vllm.ai (n.d.). [*Speculative Decoding*](https://docs.vllm.ai/en/stable/features/speculative_decoding). docs.vllm.ai (official).
