# Local Coding Models in 2026: A Tutorial on Running, Choosing and Trusting Them

## Why run a coding model locally, and the one number that decides everything

This tutorial uses 'local coding model' to mean an open-weight model that runs on your own GPU or unified-memory machine, is served by an inference engine, and is called by an editor or an agent.
The first question is not which brand to buy but how many bytes the model needs, because that number decides which hardware is eligible[1].
At batch size 1, decoding reads nearly all model weights for every generated token, so it is memory-bandwidth-bound and compute sits idle[1].
A 70B model at 4 bits stores 0.5 bytes per parameter, about 35 GB per token; 800 GB/s divided by 35 GB gives a ceiling of about 22.9 tokens/s[1].
The practitioner measured about 12 tokens/s on a Mac Studio M2 Ultra, roughly 53% of that ceiling[1].
The roadmap covers memory arithmetic, quantization, engines, efficiency techniques, integration, evaluation, trust and model choice.
The bandwidth ceiling and memory formulas are derivations, while the prices and measured speeds come from one practitioner blog[1].

## Hardware: memory arithmetic, bandwidth and what it costs

Before any engine or model is chosen, the reader needs one number: how many bytes the model occupies once loaded[1].
The blog treats hardware selection as a sequence that starts from model size, not from brand or budget[1].

The blog gives the memory of weights as parameters times bytes per parameter, namely 0.5 bytes for 4-bit and 1.0 byte for 8-bit weights[1].
Writing $P$ for the parameter count and $b$ for the bits per weight, the rule is as follows.

$$
M_{\text{weights}} = P \times \frac{b}{8}\ \text{bytes}
$$

For a 32B model, 16-bit weights need $32\times10^9 \times 2 = 64$ GB, while 4-bit weights need $32\times10^9 \times 0.5 = 16$ GB.
The blog's own figure is that a 32B model can take 60+ GB in its default form[2].
The 16 GB and 64 GB figures are this section's arithmetic and exclude the KV cache.

At batch size 1, each generated token reads essentially all active weights from memory while doing little compute, so decoding is bandwidth-bound in the Roofline sense[1].
If $B$ is memory bandwidth in GB/s and $W_{\text{tok}}$ is the bytes read per token in GB, the blog's ceiling is bandwidth divided by model bytes in GB[1].
For a mixture-of-experts model, only the active parameters $P_{\text{active}}$ are read per token[1].

$$
\text{tokens/s} \lesssim \frac{B}{W_{\text{tok}}}, \qquad W_{\text{tok}} \approx P_{\text{active}} \times \frac{b}{8}
$$

For a 70B model at 4 bits, $W_{\text{tok}}=35$ GB, so an 800 GB/s Apple M2 Ultra has a ceiling of about 22.9 tokens/s[1].
The blog reports about 12 tokens/s for a 70B 4-bit model on a Mac Studio M2 Ultra, or 53% of the ceiling[1].
This bound ignores KV-cache reads, attention compute and framework overhead[1].

Weights are not the only resident data: in the vLLM paper's layout for a 13B model on an NVIDIA A100 40GB, parameters take about 65% of memory and the KV cache close to 30%, with the figure labelled above 30%[3].
For OPT-13B the paper gives about 800 KB of KV cache per token, so one 2048-token request can need 1.6 GB[3].
The blog adds a KV-cache budget of 5–15 GB depending on context length, plus 30% headroom[1].

| Platform | Capacity | Bandwidth | Model fit and reported 70B Q4 decode |
|---|---|---|---|
| RTX 5090 (32 GB VRAM) | 32 GB | 1,792 GB/s | Fits models up to ~30B at 4 bits; a 70B model does not fit[1] |
| RTX Pro 6000 Blackwell (single card) | 96 GB | 1,792 GB/s | 15–18 tok/s decode[1] |
| Two RTX Pro 6000 over NVLink | 192 GB | ~3.5 TB/s | 20–30 tok/s decode, 2–3x system cost[1] |
| Mac Studio M3 Ultra (unified) | up to 256 GB | lower than discrete GPUs | 12–14 tok/s decode, 250–300 W[1] |
| DGX Spark | 128 GB | 273 GB/s | Below Apple M2/M3 Ultra bandwidth[1] |

The blog proposes bandwidth per $1,000 among platforms that fit the model as the procurement metric[1].
The RTX 5090 MSRP is $1,999, and at a $2,700 average street price in April 2026, bandwidth per dollar drops to about 664 GB/s per $1k[1].
The blog is a practitioner write-up that argues from vendor specifications and calculations, not a controlled measurement, and it recommends benchmarking before buying[1].

## Quantization: trading bits for bytes, and what it costs on code

Quantization stores each weight in fewer bits, and the simplest form is uniform round-to-nearest (RTN), which picks a step size and maps each weight to the nearest level on a fixed grid[2].
For $b$-bit symmetric RTN with zero-point 0, the step is $\Delta = \max(|W|)/(2^{b-1}-1)$, each weight is stored as $\text{round}(W/\Delta)$, and it is recovered as $\Delta \cdot \text{round}(W/\Delta)$[2].
Rounding bounds each weight's error by half a step, $|\delta| \le \Delta/2$, so one outlier that inflates $\max(|W|)$ enlarges the step for every weight in its group.
Group-wise quantization gives each group of about 128 weights its own scale and zero-point, trading extra storage for local adaptation[2].
NF4 places its 16 levels at quantiles of a normal distribution, so more levels lie near zero where most weights sit, while FP4 spaces its levels uniformly in log scale[2].
Naive RTN degrades at low bits because it treats all weights alike, although a small fraction of weights matters much more to the output[4].
On OPT-6.7B at INT3 with group size 128, RTN raises WikiText-2 perplexity to 23.54 from 10.86 at FP16[4].

GPTQ quantizes weights column by column and adjusts the not-yet-quantized weights to offset each error, using second-order (Hessian) information[2, 5].
The AWQ authors argue that this reconstruction can overfit the calibration set and distort features on out-of-distribution domains[4].

AWQ observes that keeping 0.1% to 1% of salient weights in FP16 greatly reduces error, and that salience is better read from activation magnitudes than from weight magnitudes[4].
Let $w$ be a weight, $x$ its input activation, and $Q(w)=\Delta\cdot\text{Round}(w/\Delta)$ the same RTN quantizer as above[4].
Scaling the weight by $s>1$ and dividing the input by $s$ leaves the product unchanged before quantization, giving $Q(ws)(x/s)$[4].
Assuming the expected rounding residual stays near 0.25 of a step and that $\Delta'\approx\Delta$, the ratio of the scaled error to the original error is roughly $1/s$, so the relative error of a salient weight falls with $s$ without mixed precision[4].
This step rests on the two empirical assumptions and is an approximation, not a proof.
Large $s$ is harmful because it enlarges $\Delta$ for other channels; on OPT-6.7B perplexity was best at $s=2$ (11.92)[4].
AWQ therefore searches $s = s_X^\alpha$ over $\alpha \in [0,1]$ by grid search, where $s_X$ is the mean activation magnitude per channel, and it uses no backpropagation[4].

GGUF is a file format from the llama.cpp project rather than a quantization algorithm, and its K-quants use 256-weight blocks with 32-weight sub-blocks[2].
A Q4_K block takes 144 bytes for 256 weights, which is 4.5 bits per weight once scales and minimums are counted[2].
BitsAndBytes quantizes on the fly at load time with NF4 blocks of size 64 and needs no calibration[2].
QuIP# applies rotation-based incoherence processing, and AQLM uses vector quantization with learned codebooks[5].

On LLaMA and Llama-2 at INT4 with group size 128, AWQ's WikiText-2 perplexities stay close to FP16, for example 5.60 against 5.47 for LLaMA-7B[4].
On one H200 GPU, the Jarvislabs blog reports Qwen2.5-32B-Instruct HumanEval pass@1 of 56.1% at FP16, 51.8% for AWQ, GGUF Q4_K_M and BitsAndBytes, and 46.3% for GPTQ, where pass@1 is the share of problems whose first generated solution passes all unit tests[2].
With 164 problems the standard error is about 0.039, and the blog covers one model on one GPU[2].
Afrin et al. compared six 4-bit methods (GPTQ, AWQ, QuIP#, AQLM, BitsAndBytes, GGUF Q4_K_M) on Qwen2.5-Coder-7B-Instruct and CodeLlama-7B-Instruct, using McEval and CoderEval with pass@1[5].
Across benchmarks, 4-bit quantization largely preserved pass@1, AQLM matched or exceeded the full-precision baseline, and QuIP# produced the only significant correctness losses, notably on BigCodeBench-Python[5].
Security was unchanged, AWQ significantly increased Java maintainability issues with a medium effect, and the study covers 7B models, two languages, three benchmarks and one 4-bit precision[5].

## Inference engines and runtimes: what differs and why

An inference engine loads the model's weights and manages the key-value (KV) cache of past attention states, which it keeps in GPU memory while a request is served[3].
The engines discussed here differ along three axes: single-user latency versus multi-user throughput, the weight formats they read, and the hardware they target.
At batch size 1 decoding is memory-bandwidth-bound, and compute sits idle while waiting for data[1].

llama.cpp is an inference runtime that reads models stored in GGUF files, the quantized format the Jarvislabs guide describes[2].
GGUF files for large models often come split into multiple parts that must be merged before use[2].
Ollama is a local server that the reader can start and query with a single command, and it is the common local path the quantization study targets[1, 5].
The quantization study loads its models through Hugging Face transformers, so its numbers do not measure either tool's speed[5].
vLLM stores the KV cache in fixed-size blocks that need not be contiguous, as an operating system pages virtual memory, and the authors report 2-4 times higher serving throughput than earlier systems on their workloads[3].
The Jarvislabs guide, a practitioner blog on one H200 with Qwen2.5-32B-Instruct and not a controlled study, reports that the Marlin kernel raised AWQ throughput from 68 to 741 tokens/s with the weights unchanged[2].
The same guide reports that GGUF ran at 93 tokens/s in vLLM and advises llama.cpp for GGUF models[2].

MLX is Apple's open-source array framework, optimised for Apple Silicon and offered with C++, Python and Swift frontends[6].
LM Studio 0.3.4 added an MLX engine built on mlx-lm, Outlines and mlx-vlm, which can enforce JSON output by masking tokens that would violate a schema-derived regex[6].
LM Studio runs MLX and llama.cpp models behind one UI and an OpenAI-like local server, and it can load several models at once[6].
Its blog reports about 250 tokens/s for Llama 3.2 1B on an M3 Max, a vendor figure with no stated protocol[6].

The hardware target follows the engine: MLX is optimised for Apple Silicon, while CUDA-based frameworks such as llama.cpp with CUDA and Ollama favour NVIDIA hardware[1].
The sources give little head-to-head benchmarking of engines and little on llama.cpp or Ollama internals.
The LM Studio and vLLM material is docs-level or blog evidence rather than controlled measurement[6, 2].

## Efficiency techniques: KV cache, mixture-of-experts, long context, speculative decoding

During decoding, each new token attends to the keys and values of every earlier token, so the engine stores them in a KV cache instead of recomputing them[3].
In the generation phase, the key and value vectors at earlier positions are cached, and only the new key and value vectors for the current iteration are computed[3].

$$
M_{\text{KV}} = 2 \times L \times H_{kv} \times d_h \times T \times B \times b
$$

Here $L$ is the number of layers, $H_{kv}$ the number of KV heads, $d_h$ the head dimension, $T$ the tokens per sequence, $B$ the batch size and $b$ the bytes per element; this form is my derivation from the per-token count, not a formula the source states.
The source's worked example is for OPT-13B in FP16, where the per-token count is 2 (key and value vectors) × 40 (layers) × 5120 (hidden size) × 2 bytes, giving 800 KB per token[3].
Since OPT can generate sequences up to 2048 tokens, one request can need up to 1.6 GB of KV cache[3].
Earlier systems reserved one contiguous chunk per request for its maximum length, and only 20.4% to 38.2% of the KV cache held actual token states[3].
PagedAttention splits the cache into fixed-size blocks that need not be contiguous, with a block table mapping logical to physical blocks, as operating-system paging does[3].
The authors report 2-4× higher serving throughput across various models and workloads, with larger gains for longer sequences and complex decoding[3].
Most of this benefit comes from batching many requests, so a single-user local session gains little from paging alone; this is my inference, not a reported result.

A mixture-of-experts (MoE) model routes each token to a few expert sub-networks, so it has a total parameter count and a smaller active count per token[7].
Memory must hold all experts, so the footprint follows the total count, while the weights read per generated token follow the active count.
On a 24 GB GPU an 80B model cannot keep all its weights resident: 80 × 10^9 × 4/8 bytes = 40 GB at 4 bits, which exceeds 24 GB before any cache is added.
Qwen3-Coder-Next has 80 billion parameters, activates 3 billion per forward pass, and uses hybrid attention with MoE[8].
GLM-4.5 has 355 billion total and 32 billion activated parameters, and GLM-4.5-Air has 106 billion total parameters[9].
Qwen3-30B-A3B has 128 experts, of which 8 are activated per token, while Qwen3-14B and Qwen3-32B are dense models[7].
A large-memory Mac can hold the full set, and the 3B active count then governs per-token speed.

Hybrid attention mixes different attention mechanisms across a model's layers, and the sources do not name the specific mechanisms Qwen3-Coder-Next uses[8].
Qwen3 dense models list a 32K or 128K context length in the architecture table, with 32K for the two smallest models and 128K for 4B to 32B[7].
Long context is costly for local agents because the KV cache grows with every tool call and observation.
RULER, a long-context retrieval benchmark, shows that Qwen3 in thinking mode slightly degraded at extreme lengths, which the authors attribute to thinking content interfering with retrieval[7].
The sources do not report measured 128K limits for agent runs.

The sources do not explain speculative decoding; the only mention is that GLM-4.5 adds a multi-token prediction layer to support it during inference[9].

## Using a local model in the editor and in agents

A local coding model serves three uses: autocomplete proposes the next lines at the cursor, chat answers questions about selected code, and an agent edits files and runs commands over many steps[8].
An agent scaffold is the harness that runs the model in a loop, issuing tool calls and reading their results until the task ends.
Tool calling means the model emits a structured request to run a named function with arguments.

Fill-in-the-middle (FIM) is a technique where a model predicts the missing parts of a code block[10].
A left-to-right model sees only the text before the cursor, so FIM trains it to fill a gap using the text after the cursor as well.
The Qwen2.5-Coder report implements FIM with the special tokens <|fim_prefix|>, <|fim_suffix|> and <|fim_middle|>[10].
File-level pretraining uses a maximum training sequence length of 8,192 tokens, with next-token prediction and FIM as objectives[10].
Repo-level pretraining extends the context to 32,768 tokens, using repository-name and file-separator tokens to concatenate files[10].
The report states that the model supports input lengths of up to 128K tokens[10].

Repository context is the editor's counterpart of retrieval: the model sees only what is selected, so file choice matters as much as the model.
In SWE-bench, the 'oracle' setting retrieves the files edited by the reference patch, an approach the authors call less realistic because an engineer may not know those files in advance[11].
The realistic setting instead uses BM25 sparse retrieval to fill a context limit with files[11].
The original paper reports that models struggle to localize the code to change as context grows[11].

Devstral-Small is a dense 24B model tuned for agent scaffolds, evaluated with the OpenHands scaffold and only bash and file-edit tools[12].
Its authors describe it as fast and deployable on local devices, but this is their claim, not a measurement[12].
The Qwen3-Coder-Next report trained on many tool chat templates, and in its experiments SWE-bench Verified rose with template count at fixed data volume, an experimental result from the vendor[8].
Its authors also found that trajectories from one scaffold transferred poorly to another[8].

A local-agent case study ran eight open-weight models on 20 longitudinal data-preparation tasks inside a closed local environment[13].
The agent used SmolAgents, which does not require a model with native tool-calling capabilities, so smaller open-weight models could run on consumer hardware[13].
Gemma 4 31B scored highest on balanced variable performance (85.9%) and completed 75% of tasks[13].
The weakest model's failures were silent: its scripts ran without warnings but contained recoding errors[13].

## How coding models are evaluated, and how big the gap to frontier models is

HumanEval and MBPP-style benchmarks focus on natural language-to-code tasks, so they overlook broader code capabilities[14].
Pass@1 is the fraction of problems for which a single generated program passes all tests[14].
These benchmarks saturate: fine-tuned open models scored well on HumanEval+ but poorly on LiveCodeBench, which the authors read as overfitting to HumanEval[14].

LiveCodeBench addresses this with live updates: problems from LeetCode, AtCoder and CodeForces contests carry release dates, so a newer model can be scored only on problems released after its cutoff[14].
DeepSeek models dropped sharply on LeetCode problems released after August 2023, which the authors read as likely contamination[14].
Its scenarios are generation, self-repair, code execution and test output prediction, and Pass@1 correlates above 0.88 across them, although relative differences between models vary[14].

SWE-bench gives a model a GitHub issue and a codebase, and the model must produce a patch that passes the repository's tests[11].
The original benchmark has 2,294 task instances from 12 popular Python repositories, and the best model at release, Claude 2, resolved 1.96% of issues with BM25 retrieval[11].
With an oracle setting that supplies the files edited by the reference patch, Claude 2 resolved 4.8%, a setting the authors call less realistic than retrieval[11].

Later reports use variants such as SWE-bench Verified, a human-filtered subset of 500 instances, evaluated by GLM-4.5 with OpenHands, a scaffold (the agent loop and tool setup wrapped around the model), and a 128K context limit[9].
Qwen3-Coder-Next reports SWE-Bench Verified, Multilingual and Pro, each with the SWE-Agent scaffold, plus Terminal-Bench 2.0 and Aider[8].

GLM-4.5 reports 64.2% on SWE-bench Verified, against 1.96% for Claude 2 on the original benchmark, though these are different subsets and scaffolds[9, 11].
In GLM-4.5's vendor report it outperforms GPT-4.1 and Gemini-2.5-Pro on SWE-bench Verified, and Claude Sonnet 4 on Terminal-Bench[9].
These gap figures are vendor reports, and the sources give no independent replication of them.

## How far can the numbers be trusted?

A benchmark score is a measurement taken under a specific setup, so the setup should be checked before two numbers are compared.
Each claim below is labelled with one of three tags: measured means a result from an experiment the source reports, inferred means a conclusion the source's authors or this tutorial draw from such a result, and vendor claim means a figure or finding that a model's developer reports about its own model.

- Contamination (measured): LiveCodeBench scores models only on problems released after each model's cutoff, because the DeepSeek model dropped sharply on LeetCode problems released after its cutoff[14].
- Contamination (measured, then inferred): the localization task asks a model to name the files a fix must touch, given only the issue text, and is scored on whether the named files match the ground truth[15].
- Contamination (measured, then inferred): Prathifkumar et al. report that two Claude models localized files on SWE-Bench-Verified far better than on BeetleBox and SWE-rebench when given issue text alone, and that the gap is about six times for all-ground-truth-file localization against BeetleBox[15].
- BeetleBox and SWE-rebench are other benchmarks built from popular open-source Python projects[15].
- The memorization explanation is the authors' interpretation of that gap (inferred), not a direct test of memorization[15].
- Self-reported scores (vendor claim): the GLM-4.5 report ran SWE-bench Verified with OpenHands, a 100-iteration limit, history truncation to a 128K context and temperature 0.6[9].
- Agent setup (measured, vendor-reported): Qwen3-Coder-Next reports in its own experiments that training on one scaffold transfers poorly to another, with OpenHands-specialized training transferring badly to SWE-Agent[8].
- Variance (measured): in 584 runs on an XGBoost task, identical runs of one agent-model pairing varied more than the pairings differed, so a few runs ranked agents unreliably[16].
- Rule-breaking (measured): ten of 312 runs broke the task's data rules, and they included the seven highest scores; removing them lowered the best score from 0.8293 to 0.7695[16].
- Quantization (measured in a separate study): quantizing a model changes its code-generation scores, so a score on a quantized copy needs its own check[5].

Practical rules follow from these failure modes.
Prefer fresh benchmarks whose problems postdate the model's cutoff, as LiveCodeBench does[14].
State the scaffold, step and context limits, and sampling settings with every score, since the same model's result depends on them[9].
Repeat runs and report the spread, because a few runs can misorder agents[16].
Report compliance beside quality, and reject non-compliant runs before choosing the best one[16].
Test on your own tasks, since in the same study a later-year holdout kept only about a third of the measured gain[16].

## Which open-weight coding models matter in 2026, and what fits where

The choice of open-weight coding model comes down to a few families, and each family matches a different hardware class.
The first split is dense versus mixture-of-experts (MoE): an MoE model routes each token through only a few experts, so it activates only a subset of its parameters per token[7].
Memory is paid for total parameters in both cases, while per-token bandwidth is paid for active parameters.

For a single 24 GB GPU, the small dense models are the natural fit.
The Qwen2.5-Coder series spans six sizes, from 0.5B to 32B parameters[10].
Devstral-Small is a dense 24B model with a 128k-token context, which its authors describe as fast and deployable on local devices[12].
At 4 bits, 24 × 4 / 8 = 12 GB of weights leaves room for the KV cache on a 24 GB card; this fit estimate is the writer's arithmetic, not a measured result.

For large-memory Macs, or a GPU plus system RAM, MoE models with few active parameters are the main option.
Qwen3-Coder-Next has 80 billion total parameters, activates 3 billion per forward pass, and uses hybrid attention and MoE[8].
Qwen3-30B-A3B has 30 billion total and 3 billion activated parameters, with 128 experts of which 8 are active per token[7].
Because every expert must stay resident, an 80B model at 4 bits needs roughly 40 GB for weights, so it suits a large-memory Mac or server rather than a 24 GB card; this is the writer's arithmetic.

For servers, the large MoE models are the comparison points.
GLM-4.5 has 355B total and 32B activated parameters, and GLM-4.5-Air has 106B total parameters[9].
The GLM-4.5 authors report 64.2% on SWE-bench Verified[9].
The sources do not cover DeepSeek-V3.2, MiniMax M2.1 or GLM-4.7 as deployable models; they appear only as comparison bars in the Qwen3-Coder-Next figure[8].
Gemma coder specifics are not covered by these sources.

Licensing is stated for two families: all Qwen3 models are released under Apache 2.0, and Qwen2.5-Coder is described by its authors as permissively licensed[7, 10].

The one local case study gives the most direct evidence for on-premise use.
Eight open-weight models ran entirely on local infrastructure on 20 data-preparation tasks, and the best, Gemma 4 31B, completed 75% of tasks with 85.9% of 102 variables correctly derived[13].
The authors report that performance generally rose with parameter count, and that correctness was the main differentiator[13].
The study used R and a single agent responsible for interpreting metadata, writing code, executing it, and debugging errors[13].

## Local versus cloud: privacy, latency, cost, licensing

Local deployment is a trade-off with a decision rule, not a verdict.
Governance requirements typically prohibit data transmission to external services, and locally deployable open-weight models keep sensitive data in the local environment[13].
At batch size 1, decoding is memory-bandwidth-bound, so a single user's tokens per second are set by how fast the hardware reads the weights[1].
The sources give no per-token cloud prices and only limited hardware prices.
Local use has a fixed hardware outlay and no per-query cost[13].
The blog's energy figures are one of three correction factors in its total-cost step: at 8 hours of use per day and $0.15/kWh, three-year energy costs are about $400 to $500 for a Mac Studio and $1,000 to $1,400 for a GPU workstation[1].
The evaluated open-weight models were released under the Apache 2.0 license, and Qwen2.5-Coder is described as permissively licensed; the sources do not cover API terms[13, 10].
In a fully autonomous run, the best local model completed 75% of data-preparation tasks, and weaker models produced silent errors[13].
Identical runs of one agent and model varied more than the differences between pairings, so a few runs rank agents unreliably[16].
Human review is advisable with smaller models because silent errors can materially affect downstream results[13].
Choose local when governance forbids transmission and you can accept more review and repeated runs.
Choose cloud when data may leave and peak capability or throughput matters more than control.

## Side-by-side comparison of the main approaches

The quantization rows come from different studies, so read them as separate evidence rather than one ranking.

| Method | Idea | Calibration | Typical bits | Engines supporting it | Evidence on code |
|---|---|---|---|---|---|
| RTN | Uniform grid per group | No | 4, 8 | Not stated in the sources | MBPP pass@1 37.51 against 38.53 at FP16, CodeLlama-7B, INT4-g128[4] |
| GPTQ | Hessian-based error compensation, column by column | Yes, 128 to 1024 samples | 4, 8 | vLLM (with Marlin kernel) | Qwen2.5-Coder-7B McEval-Java pass@1 0.45 to 0.32[2, 5] |
| AWQ | Scale salient channels before quantization | Yes, small calibration set | 4 | Not stated in the sources | Matches baseline on Qwen McEval-Java (0.45)[4, 5] |
| GGUF k-quants | Block and sub-block scales in a file format | Not stated | About 4.5 to 5.5 | llama.cpp | Q4_K_M gives 0.51 on Qwen McEval-Java against 0.45 at FP16[2, 5] |
| BitsAndBytes NF4 | Normal-fitted levels per block of 64 | No, on the fly | 4 | Hugging Face transformers; vLLM | Best Qwen McEval-Java result in one study (0.60 against 0.45), not uniform across models[2, 5] |
| QuIP# and AQLM | Incoherence transforms; vector codebooks | Calibrated on WikiText-2 in the study | 2 to 4 | Not stated in the sources | AQLM matches or exceeds full precision; QuIP# shows the largest correctness degradation[5] |

| Engine | Hardware | Formats | Strength | Weakness |
|---|---|---|---|---|
| llama.cpp | CPU and GPU | GGUF files | Runs quantized files locally | Internals not covered in the sources[5] |
| Ollama | Local machines | Quantized checkpoints | Lightweight local framework | Internals not covered in the sources[5] |
| LM Studio | Apple MLX and llama.cpp | MLX and GGUF models | One UI and local server; JSON output; several models at once | No head-to-head benchmarks[6] |
| MLX | Apple Silicon | MLX-format models | About 250 tokens/s for Llama 3.2 1B on M3 Max (vendor blog) | Not benchmarked against other engines[6] |
| vLLM | NVIDIA GPUs | AWQ, GPTQ, Marlin, GGUF and other checkpoints | PagedAttention; 2-4x throughput on the authors' workloads | Gains larger with longer sequences, larger models and complex decoding[3, 2] |

| Model class | Memory | Speed | Quality | Fit |
|---|---|---|---|---|
| Small dense | All weights read each token | Bandwidth-bound | Scales with parameters (Gemma 4 31B led in one local study) | Single 24 GB GPU[13] |
| Small-active MoE (80B, 3B active) | All 80B resident | 3B active per pass | Competitive for its size (vendor-reported) | Large-memory Mac or GPU plus RAM[8] |
| Large MoE | Hundreds of billions resident | Active share sets cost | Vendor-reported leaders; no local measurements | Servers[9] |

| Axis | Local | Cloud |
|---|---|---|
| Privacy | Data stays on premises | Data is sent to third parties[13] |
| Latency and throughput | Single-user decoding bounded by memory bandwidth | Batched serving on datacenter hardware[3] |
| Cost | Hardware purchase price, energy and total cost of ownership; RTX 5090 MSRP $1,999 | Not covered in the sources[1] |
| Licensing | Apache 2.0 for Qwen3 | Not covered in the sources[7] |
| Capability and reliability | Run-to-run variance across identical runs | Not covered in the sources[16] |

## Summary and self-check questions

Memory feasibility depends on weights, the key–value cache and other runtime data, which the vLLM paper breaks down for a serving setup in which parameters take about 65% of GPU memory and the KV cache over 30%[3].
For single-user decoding, memory bandwidth provides a speed ceiling, not a guarantee[1].
Quantization reduces weight storage, but code accuracy needs testing[5].
AWQ identifies salient channels using activation statistics[4].
Mixture-of-experts models distinguish total parameters from those active per token[8].
Engine choice depends on hardware and supported formats[6].
Agent scaffolds also affect reported performance[8].
Benchmark trust requires checking contamination and repeating runs, not simply comparing headline scores[15, 16].

- For a hypothetical 32-billion-parameter model at 4 bits, would weights plus 6 GB of cache and overhead fit in 24 GB[2]?
- If each token requires reading 16 GB at 800 GB/s, what is the bandwidth-only speed ceiling, and what does it omit[1]?
- Why can AWQ's equivalent channel scaling reduce quantization error[4]?
- Why does an 80B-total, 3B-active mixture-of-experts model still need storage for 80B parameters[8]?
- What two failure modes could make SWE-bench Verified scores overstate practical ability[15, 16]?
- How would you compare two agents while controlling scaffold, sampling, context, quantization and run-to-run variation[16, 5, 8]?

## References

1. Hannecke, M. (2026). [*How to Choose Hardware for Local LLM Inference*](https://medium.com/@michael.hannecke/how-to-choose-hardware-for-local-llm-inference-163632d93dcb). medium.com (blog).
2. Jarvislabs (2026). [*The Complete Guide to LLM Quantization with vLLM: Benchmarks & Best Practices*](https://jarvislabs.ai/blog/vllm-quantization-complete-guide-benchmarks). jarvislabs.ai (commercial).
3. Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C. H., Gonzalez, J. E., Zhang, H., Stoica, I. (2023). *Efficient Memory Management for Large Language Model Serving with PagedAttention*. arXiv preprint 2309.06180. Cited at pages 1, 2, 3, 4, 5, 6.
4. Lin, J., Tang, J., Tang, H., Yang, S., Chen, W., Wang, W., Xiao, G., Dang, X., Gan, C., Han, S. (2023). *AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration*. arXiv preprint 2306.00978. Cited at page 8.
5. Afrin, S., Haque, M. Z., Mastropaolo, A. (2026). *Quantize with Confidence? An Empirical Study of Quantization for Code Generation*. arXiv preprint 2607.14181. Cited at pages 1, 2, 5, 6.
6. Burowski, Y., Coghlan, A., Mehta, N., Clayton, M. (2024). [*LM Studio 0.3.4 ships with Apple MLX*](https://lmstudio.ai/blog/lmstudio-v0.3.4). lmstudio.ai (official).
7. Yang, A., Li, A., Yang, B., Zhang, B., Hui, B., Zheng, B., Yu, B., Gao, C., Huang, C., Lv, C., et al. (2025). *Qwen3 Technical Report*. arXiv preprint 2505.09388. Cited at pages 3, 23.
8. Cao, R., Chen, M., Chen, J., Cui, Z., Feng, Y., Hui, B., Jing, Y., Li, K., Li, M., Lin, J., et al. (2026). *Qwen3-Coder-Next Technical Report*. arXiv preprint 2603.00729. Cited at pages 1, 5.
9. GLM-4. 5 Team, :, Zeng, A., Lv, X., Zheng, Q., Hou, Z., Chen, B., Xie, C., Wang, C., Yin, D., et al. (2025). *GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models*. arXiv preprint 2508.06471. Cited at pages 1, 2, 16, 17.
10. Hui, B., Yang, J., Cui, Z., Yang, J., Liu, D., Zhang, L., Liu, T., Zhang, J., Yu, B., Lu, K., et al. (2024). *Qwen2.5-Coder Technical Report*. arXiv preprint 2409.12186.
11. Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., Narasimhan, K. (2023). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*. arXiv preprint 2310.06770. Cited at pages 1, 2, 5, 6.
12. Rastogi, A., Yang, A., Jiang, A. Q., Liu, A. H., Sablayrolles, A., Héliou, A., Martin, A., Agarwal, A., Ehrenberg, A., Lo, A., et al. (2025). *Devstral: Fine-tuning Language Models for Coding Agent Applications*. arXiv preprint 2509.25193.
13. Nixon, M., Wright, L., Kovalchuk, Y., Wu, A. F., Danka, M., Boyd, A., Bann, D. (2026). *Agentic coding without the cloud: evaluating open-weight large language models on longitudinal data preparation tasks*. arXiv preprint 2607.21482. Cited at pages 1, 2, 12, 19, 20, 21, 23.
14. Jain, N., Han, K., Gu, A., Li, W., Yan, F., Zhang, T., Wang, S., Solar-Lezama, A., Sen, K., Stoica, I. (2024). *LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code*. arXiv preprint 2403.07974. Cited at pages 2, 3, 4, 5, 7, 11, 12.
15. Prathifkumar, T., Mathews, N. S., Nagappan, M. (2025). *Does SWE-Bench-Verified Test Agent Ability or Model Memory?*. arXiv preprint 2512.10218.
16. Rubia, E. A. d. l., Pafka, S. (2026). *Identical Runs, Different Results: Benchmarking AI Coding Agents on Open-Weight Models*. arXiv preprint 2609.33812. Cited at pages 1, 8, 13.
