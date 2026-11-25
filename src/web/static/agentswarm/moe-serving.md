# Serving One Mixture-of-Experts Model to Many Users: Batching, Expert Utilization, Prefill/Decode, Expert Layouts and Single-Machine Offloading

## The serving problem: why MoE changes the memory/compute balance

A mixture-of-experts (MoE) model replaces the feed-forward block of each transformer layer with a sparse MoE layer made of a router, also called a gate network, and a set of experts, each of which is a neural network[^1].
The router is a learned network that scores the experts for each token, and only a selected subset of them runs on that token[^1].
Alongside these routed experts, DeepSeek-V3 has shared experts, which are applied to every token regardless of what the router selects[^2].
In DeepSeek-V3, each token is sent to the top $K_r$ routed experts, so a token passes through the shared experts and a small set of routed ones[^2].
Total parameters are everything stored in the model, and active parameters are those used to process one token[^3].
DeepSeek-V3 has 671B total parameters with 37B activated for each token[^2].
Nemotron 3.5 Lightning activates 3B of its 30B total parameters per token[^3].
Memory cost follows total parameters, because all experts must be loaded into VRAM, while compute per token follows active parameters[^3].
Mixtral 8x7B, for example, needs enough VRAM to hold a dense 47B-parameter model, yet with two experts per token its inference speed is like that of a 12B model[^1].

Serving an MoE model therefore raises two questions.
The first is who pays for the memory: every expert must be resident, so the memory cost is paid whether or not a given expert is used[^3].
The second is how to keep the compute units busy, since each token touches only a few experts and a small batch can leave most stored experts idle[^1].
This tutorial asks how many experts a batch touches, how that changes the cost per user, when load imbalance hurts, and which technique fits a given load and memory budget.

The sources differ in what they establish, and the tutorial keeps that difference visible.
The DeepSeek-V3 report is a primary source that states its own architecture and parameter counts[^2].
The NVIDIA post is a vendor blog whose throughput and latency comparisons depend on hardware, precision, framework, and model design, so they are observations rather than general laws[^3].
Its advice that deployment choice depends on memory budget, concurrency, fine-tuning, and quantization rather than parameter count alone is the author's opinion, not a measured result[^3].

## How batching shares one copy of the experts

A decode step produces one token per request, and every step must stream the weights of the layers it touches from GPU memory[^3].
For one token that step does little arithmetic per byte streamed, so the step waits on memory bandwidth rather than on compute.
At batch size 1 decoding is therefore bound by available memory rather than compute, which is why MoE helps here because it reads fewer weight bytes per token[^3].
Batching changes this balance, because one weight read can be applied to many tokens at once, so arithmetic per byte loaded, the arithmetic intensity, grows with batch size.

An MoE layer changes what a batch shares: a router sends each token to the top k of E experts, and all experts must be held in memory at once[^1][^3].
Because every user's tokens read the same stored copy of each expert, a batch from many users shares one set of expert weights instead of each user holding a private model.
The Hugging Face explainer warns, however, that batch sizes inside an MoE are effectively reduced as tokens scatter to different experts, leaving uneven batches and underutilization[^1].

To estimate how many experts a batch touches, the tutorial uses its own illustrative model, which is not from any source: each token picks k of E experts uniformly at random, independently of other tokens.
Under this assumption one token misses a given expert with probability $1-k/E$, so a batch of $B$ tokens misses it with probability $(1-k/E)^B$.
The expected number of distinct experts touched is E minus the expected number missed, which gives the formula below.

$$
\mathbb{E}[N_{\text{touched}}(B)] = E\left[1-\left(1-\frac{k}{E}\right)^{B}\right]
$$

Here $E$ is the number of routed experts in a layer, $k$ is the number of experts each token activates, $B$ is the batch size in tokens, and $N_{\text{touched}}$ is the count of distinct experts that receive at least one token.
Each touched expert receives on average $Bk/E$ tokens, since the batch sends $Bk$ token-expert pairs across $E$ experts, and this count sets how much arithmetic each loaded weight byte supports.
Take $E=256$ and $k=8$ as an illustrative configuration for the arithmetic below, a choice of this tutorial rather than a value stated in the cited passage.
At $B=1$ the formula gives exactly $k=8$ experts touched, each receiving $0.03$ tokens on average, so one token loads 8 expert weight sets to serve itself.
At $B=16$ about $256[1-(31/32)^{16}] \approx 103$ experts are touched, with about $0.5$ tokens per expert.
At $B=256$ about $256[1-(31/32)^{256}] \approx 256$ experts are touched, nearly all of them, with an average of $8$ tokens per expert.
At $B=4096$ each expert receives on average $128$ tokens, so each expert's weights are read once and reused across many tokens.

At small $B$ few experts are used and each loaded expert serves very few tokens, so bytes moved per token stay high; at large $B$ nearly every expert is loaded once and applied to many tokens, raising arithmetic intensity much as batching does for dense layers.
The NVIDIA post describes the same trend in practice: as the batch grows, tokens collectively use most experts, the throughput advantage persists, but the latency margin over a well-optimized dense model narrows at high concurrency[^3].
A per-user replica would pay the full memory of all experts and read them alone, whereas a shared deployment reads each expert once per step for the whole batch.
The cost of sharing is memory: all experts must sit in GPU memory at once, which leaves less room for the KV cache than a dense model of comparable size would leave[^3].

The uniform model is a simplification, and real routers are skewed, so some experts receive far more tokens than the average $Bk/E$.
The SC '25 benchmark reports that MolmoE-1B concentrates activations on certain experts far more than DeepSeek-VL2 models, which were trained with an auxiliary balancing loss; this is an observation on the task dataset, not a proof for all workloads[^4].

The same benchmark reports that throughput consistently decreases as the number of active experts per token increases, with a drop of roughly 15-20% for batches of 64 and 128 and 5-8% for batches of 1 and 16 when DeepSeek-V2-Lite goes from 1 to 32 active experts[^4].
This is an experiment on NVIDIA H100 GPUs for specific models, so it shows a trend for those settings rather than a general proof.
The benchmark also reports that moving from batch size 1 to 128 increases throughput by roughly two orders of magnitude[^4].

## Expert utilization versus traffic and batch size

The utilization question has two regimes, and the same stored experts behave very differently in each.
At low load, the memory that holds the experts is paid for whether or not those experts receive tokens, since idle experts still pay the memory required to store them[^3].
NVIDIA notes that at batch size 1, decoding is bound by available memory rather than compute, and MoE performs well because it reads fewer weight bytes per token[^3].

MoE-Infinity, a system for personal machines that run at batch size one, reports that during decoding a small set of experts is reused frequently[^5].
This is experimental evidence from trace analysis, not a proof: the authors found that a consumer-grade GPU's memory is often sufficient to hold the most frequently used experts during decoding, even with long-context inputs[^5].
The same authors observe that this skew exists only within a single request; after many requests, reuse counts even out and all experts tend to be activated uniformly[^5].
So a cache sized to the hot set suits one user, but the batch-size-one result cannot be carried over unchanged to a busy server.

At high load, many experts are active, and MoE holds a throughput advantage across batch sizes[^3].
NVIDIA states that as batch size grows, tokens collectively use most of the experts, and the MoE latency margin compresses at high concurrency[^3].
All experts must live in GPU memory at once, which leaves less room for the KV cache than a dense model of comparable size would typically have[^3].

At scale, the main threat to utilization is load imbalance among experts, the MoE analogue of stragglers in an HPC job.
In a synchronous step, the most loaded expert finishes last, so the step time is set by the hottest expert rather than by the average; this is the tutorial's own illustrative derivation.
The DeepSeek-V3 report states that for MoE models an unbalanced expert load leads to routing collapse and diminishes computational efficiency in scenarios with expert parallelism[^2].

The first remedy is applied during training: DeepSeek-V3 adds a bias term $b_i$ to each expert's affinity score $s_{i,t}$ when selecting the top-K experts, while the gating value still uses the original score[^2].
After each training step, the bias of an overloaded expert is decreased by $\gamma$ and that of an underloaded expert is increased by $\gamma$, where $\gamma$ is the bias update speed[^2].
In the report's ablations, removing auxiliary losses and adding this strategy consistently achieved better performance on most benchmarks, an experimental result on the stated setup rather than a proof[^2].
The report observes that the auxiliary-loss-free model demonstrates greater expert specialization patterns, based on expert-load records across three domains of the Pile test set[^2].

The second remedy acts at serving time, where the expert layout can change without retraining.
DeepSeek-V3's inference framework deploys redundant copies of heavily loaded experts to address domain-shift imbalance[^2].
The rebalancing policy, called EPLB (the serving-time expert load balancer that replicates hot experts and rearranges placement from load statistics), is treated in the section on large-scale expert layouts.
Redundancy has a cost: each extra copy uses GPU memory that could otherwise hold KV cache.

The MoE inference benchmark, run mainly on H100 GPUs with models from 2B to 70B parameters, reports several findings[^4].
Throughput generally decreases as the number of active experts per token increases, and single-expert configurations delivered 50 to 80 percent higher throughput than eight-expert ones[^4].
On H100 GPUs, imbalanced token-to-expert routing makes some experts bottlenecks and reduces parallel efficiency even when compute is available[^4].

- Proven: the bottleneck argument above follows from the synchronous structure of a step, and is the tutorial's own derivation rather than a result any source proves for every system.
- Experiment: MoE-Infinity's trace analysis at batch size one, DeepSeek-V3's ablations on auxiliary-loss-free balancing, and the MoE-Inference-Bench throughput results[^5][^2][^4].
- Hypothesis: the authors' explanation that balancing yields expert specialization, supported by expert-load records but not proven[^2].

## Prefill versus decode: two workloads in one service

Serving a model to many users involves two different kinds of work, and the SGLang team treats them as separate phases of every request[^6].
Prefill processes the whole input prompt, and the team describes it as computation-intensive because it handles the entire input sequence at once[^6].
Decode is memory-intensive because it manages the key-value (KV) cache for token generation[^6].
During prefill, the DeepSeek-V3 deployment uses 32-way expert parallelism (EP32), which ensures that each expert processes a sufficiently large batch size, thereby enhancing computational efficiency[^2].
During decode, the batch size per expert is relatively small (usually within 256 tokens), and the bottleneck is memory access rather than computation[^2].

Decode is also where users feel latency, and a common measure is time per output token (TPOT)[^5].
The SGLang report also uses time to first token (TTFT) and inter-token latency (ITL), and reports TTFT of 2 to 5 seconds and ITL of about 100 ms for its throughput-focused setup[^6].

A conventional unified engine runs prefill and decode batches in one scheduler, and the SGLang team reports three problems with that design[^6].
First, incoming prefill batches frequently interrupt ongoing decode batches, which causes substantial delays in token generation[^6].
Second, under data-parallel attention one worker may process a prefill batch while another handles a decode batch, which increases decode latency[^6].
Third, DeepEP uses different dispatch modes for prefill and decode, and its auto mode cannot support normal dispatch for prefill and low-latency dispatch for decode in the same communication group, so unified scheduling is incompatible with it[^6].
The two phases also differ in expert use: the team's case study found that prefill and decode distributions share similarities but have notable differences, which supports distinct expert placements for each phase[^6].

Prefill-decode (PD) disaggregation addresses this by running the two phases on separate servers, a Prefill Server and a Decode Server[^6].
In the SGLang design, the two servers first pair through a handshake, the Decode Server pre-allocates the KV cache, the Prefill Server computes the KV caches, and the data then transfers to the Decode Server, which runs the iterative token generation[^6].
The transfer runs in a background thread so the scheduler's event loop is not interrupted, and it uses RDMA, a direct memory-to-memory transfer over the network[^6].
Prefill can then use normal dispatch and decode can use low-latency dispatch, both under DP attention, so each phase gets a dispatch mode suited to it[^6].

As a worked example, suppose a service is decoding 64 requests and a user submits a prompt of 8,000 tokens.
In a unified engine, that prefill can be scheduled between decode steps, which delays the next token for the decoding users, the interruption the SGLang team describes[^6].
With PD disaggregation, the long prompt is prefilled on the Prefill Server while the Decode Server keeps emitting tokens for the active requests, and the KV cache is handed over once it is ready[^6].
The 8,000-token prompt and the 64 requests are illustrative numbers of the tutorial, not measurements from the sources.

DeepSeek-V3 also uses multi-token prediction (MTP), an objective that extends prediction to multiple future tokens at each position[^2].
The report notes that the MTP modules can be discarded at inference or reused for speculative decoding to improve generation latency[^2].
The SGLang team reports that its MTP support lacks full integration with DP attention, which reduces efficiency in mixed parallelism configurations[^6].

## How large providers lay out experts: DeepSeek-V3 and large-scale expert parallelism

Expert parallelism (EP) splits the experts of an MoE layer across GPUs, so each GPU holds only a share of them[^2].
DeepSeek-V3's deployment uses 32-way EP for the MoE part in prefill and 320-way EP in decode, and in decode each GPU hosts one expert[^2].
The report says 32-way EP ensures that each expert processes a sufficiently large batch size, thereby enhancing computational efficiency[^2].
This is the high-load regime from the utilization discussion, made a deliberate design choice, because pooling many users' tokens across GPUs gives each expert enough tokens per step.
Because each GPU holds only a slice of the experts, more of its memory remains free for the KV cache, the per-request store of attention keys and values that decoding reads at every step.

Large layouts combine several kinds of parallelism, so the terms need defining: tensor parallelism splits one layer's matrices across GPUs, data parallelism replicates a layer and splits the requests, sequence parallelism splits the tokens of one sequence, and expert parallelism splits the experts.
In the notation below, TP4 is 4-way tensor parallelism, DP8 is 8-way data parallelism, and EP32 is 32-way expert parallelism.
DeepSeek-V3 runs prefill and decode on separate units, each with its own layout[^2].
The prefill unit has a minimum deployment of 4 nodes with 32 GPUs, using TP4 with sequence parallelism and DP8 for attention, and EP32 for the MoE part[^2].
The decode unit has a minimum deployment of 40 nodes with 320 GPUs, using EP320 for the MoE part, and 64 of those GPUs host redundant and shared experts[^2].
Dispatch and combine in decode use direct point-to-point transfers over InfiniBand to achieve low latency, and the report further leverages IBGDA (NVIDIA, 2022) to minimize latency[^2].

Imbalance is handled by redundant experts: the report duplicates high-load experts, detects them from online statistics, and adjusts the set periodically, for example every 10 minutes[^2].
In prefill, 32 redundant experts are added so each GPU hosts one extra expert beyond its original 8, and experts are rearranged within a node without increasing cross-node traffic[^2].
To hide communication latency, prefill processes two micro-batches with similar workloads at once, overlapping the attention and MoE of one with the dispatch and combine of the other[^2].
While one micro-batch waits on all-to-all communication, the GPU computes the other, so communication time is overlapped with computation.
In decode, the report notes that per-expert batches are usually within 256 tokens and the bottleneck is memory access rather than computation, so it can give few SMs to communication, a claim the report presents as reasoning rather than measurement[^2].

SGLang reproduced this kind of system on 96 H100 GPUs, 12 nodes with 8 GPUs each, and reported nearly on-par performance with DeepSeek's profile[^6].
It reported 52.3k input tokens and 22.3k output tokens per second per node for 2000-token inputs, measured on its own setup[^6].
SGLang gives attention, dense feed-forward layers, and sparse expert layers separate parallelism schemes, and it moves the LM head to data parallelism to reduce memory overhead[^6].
DeepEP's normal dispatch suits long prefill inputs but cannot be captured by CUDA Graph, while its low-latency dispatch supports CUDA Graph at the cost of preallocated memory[^6].
SGLang also includes two-batch overlap (TBO), which overlaps computation (e.g., attention and MLP phases) with DeepEP Combine and Dispatch communication[^6].
Its expert load balancer, EPLB, takes expert statistics and arranges experts to minimize imbalance; adding 32 redundant experts to the original 256 gives a pool of 288, which allows parallelism sizes such as 12 or 72[^6].

The TBO ablation gave a 27% to 35% throughput increase over the vanilla setup at the same token count per device, and allowed batches of 16,384 tokens per device where the vanilla setup ran out of memory beyond 8,192[^6].
EPLB gave speedups of 1.49x in prefill and 2.54x in decode at large scale, which the authors attribute to reduced imbalance across GPUs as the number of ranks grows[^6].
Against DeepSeek's profile, SGLang with default imbalance was 20% slower, and simulated perfect EPLB narrowed the gap to 6%[^6].
The authors also report that most experts are rarely used while a small subset is heavily used, and that prefill and decode distributions differ, which they cite as support for PD disaggregation with phase-specific placements[^6].

The SGLang authors list their own limitations: time to first token is 2 to 5 seconds and inter-token latency about 100 ms, the 96-GPU setup limits sequence length, EPLB was tested only on in-distribution data, and flexible tensor parallelism sizes for dense layers are not supported[^6].
DeepSeek's report is the source of the layouts and minimum deployment units, while SGLang's numbers come from its own reproduction[^2][^6].

## What a single machine can do: offloading experts to CPU memory

The personal machine is the opposite of the cloud server: it usually has a single consumer-grade GPU with limited memory, typically 24 to 48 GB, and it serves one user at a time[^5].
Some MoE models exceed 100 GB, so they cannot fit on such a GPU, and the common answer is offloading: the full model stays in host memory, and only the activated experts, those that receive tokens for processing, are fetched into the GPU when needed[^5].
The MoE-Infinity authors argue that the single-user setting makes this workable, because with a batch size of one an MoE model activates only a small subset of experts per token[^5].
Hugging Face's introduction makes the memory point directly: all parameters must be loaded in RAM, so memory requirements are high, even though inference is much faster than for a dense model with the same number of parameters[^1].

The bottleneck in this regime is the PCIe link between host memory and the GPU, not the arithmetic.
The MoE-Infinity evaluation uses a single NVIDIA A5000 with 24 GB, connected through PCIe 4.0 at 24 GB/s, and it reports time-per-output-token (TPOT) in its latency table[^5].
In its table for DeepSeek-V2-Lite, MoE-Infinity reaches a TPOT of 51 ms, against 254 ms for vLLM and 754 ms for Mixtral-Offloading, which the authors summarise as a 3.1 to 16.7 times latency reduction[^5].
These numbers are experimental evidence for one model, one GPU and one PCIe generation, and they should not be read as a general speedup.
The authors attribute the poor baselines to high-volume but inaccurate prefetching, which blocks GPU fetches when they are needed, and to a low GPU cache hit rate[^5].
Blocking matters because a cache miss stalls the decode step until the expert arrives over PCIe.
BrainStorm, a system for dynamic neural networks, illustrates inaccurate prediction: the authors say it handles control-flow patterns in classification rather than MoE routers during autoregressive decoding, and its TPOT of 934 ms was worse than the 485 ms of on-demand vLLM[^5].
vLLM also moves KV-cache data over the same link, so long contexts make expert fetches contend with KV traffic, in the authors' account[^5].

MoE-Infinity's idea is to decide what to fetch and what to keep by tracing expert activity[^5].
For each request, it records an expert activation matrix (EAM), which the sources show as a per-layer, per-expert count of activations, as in the Figure 6 example[^5].
For the current request, the system finds the most similar historical EAM, on the reasoning that a matching trace has a similar overall activation pattern[^5].
The matched trace then drives eviction: when the cache is full, the expert with the lowest priority, computed from the predicted likelihood of reuse with a layer decay, is replaced by the expert fetched on demand[^5].

The design rests on an observed property: with a batch size of one, GPU memory is often sufficient to hold the most frequently used experts during decoding, even with long-context inputs[^5].
Experts also show skewed reuse within a single request, and after processing multiple requests the skew disappears and experts are activated uniformly[^5].
The authors' explanation, that experts with similar expertise are reactivated within the same context, is a hypothesis they state rather than a proven result[^5].

The bandwidth arithmetic below is the tutorial's own illustrative model, not a figure from the sources.
If an expert occupies $S$ bytes and the PCIe link delivers $B_{\text{PCIe}}$ bytes per second, a cache miss costs about $t_{\text{miss}} = S / B_{\text{PCIe}}$ seconds.

$$
\mathbb{E}[t_{\text{stall}}] \approx (1-h)\,\frac{S}{B_{\text{PCIe}}}
$$

Here $h$ is the cache hit rate, the fraction of expert uses served from GPU memory, so the hit rate dominates TPOT once misses are frequent.
For example, an expert of 0.5 GB over a 24 GB/s link costs about 21 ms per miss, so a decode step that misses several experts per layer is dominated by transfers rather than matrix multiplication.

The approach has clear limits.
It targets batch size one, and the authors' analysis says the cache's benefit comes from a small working set of experts during each decoding iteration[^5].
As batches grow, more experts are touched per iteration, the working set grows, and a fixed GPU cache holds a smaller fraction of what is needed, so the hit rate falls and the gains shrink.
The authors also note that an excessively large expert cache would trigger excessive I/O bandwidth usage and slow inference through frequent offloading[^5].

## Side-by-side comparison of the approaches

The four approaches differ mainly in who holds the experts and how many users share them.

| Approach | Target traffic and batch | Where experts live | Dominant bottleneck | What is shared across users | Utilization behavior | Main technique | Evidence type | Main limitation |
|---|---|---|---|---|---|---|---|---|
| Dense-style, all experts resident on one GPU | Single user, batch about 1 | All experts in GPU memory | Memory paid up front | One resident copy | Idle experts still occupy memory | Keep all experts in GPU memory | Vendor blog observation | Less room for KV cache[^3] |
| Single-machine CPU offloading with sparsity-aware cache | Personal machine, batch size one | Full model in CPU memory, active experts fetched over PCIe | Expert fetch cost on cache misses | Little, since one user | Few experts reused per request | Expert activation tracing and cache | Single-machine experiment | Designed for batch size one; no batch-size sweep reported[^5] |
| Batched multi-user serving on one node | Moderate concurrency | Resident copy on the node's GPUs | Throughput falls as active experts rise | One expert copy for all users' tokens | Utilization rises with batch size | Batching and active-expert choice | Benchmark on H100 GPUs | Throughput drops with more active experts[^4] |
| Large-scale expert parallelism with PD disaggregation | Very high traffic | Sharded across many GPUs and nodes | Communication and load imbalance | Expert batches aggregated across GPUs | Large aggregate batch per expert | Expert parallelism, redundant experts, PD disaggregation | Authors' report; SGLang reproduction | Large minimum deployment unit[^2][^6] |

Start from the memory budget: the memory footprint tracks total parameters, and all experts must live in GPU memory at once, which leaves less room for the KV cache than a dense model of comparable size would have[^3].
CPU offloading with an expert cache is what the single-machine experiment supports when the weights do not fit and one user runs on a personal machine[^5].
After processing multiple requests, the skew in expert reuse disappears and all experts tend to be activated uniformly, which weakens the cache's ability to predict reuse[^5].
Throughput drops sharply as the number of active experts increases, so batched serving on one node is sensitive to the active-expert choice[^4].
Deployment choice depends on memory budget, concurrency needs, fine-tuning plans, and quantization behavior rather than raw parameter count alone[^3].
Large-scale expert parallelism with PD disaggregation suits very high traffic, and its minimum deployment unit is 4 nodes with 32 GPUs for prefilling and 40 nodes with 320 GPUs for decoding[^2].

## Summary and check-your-understanding questions

An MoE model separates its total parameters from the parameters it activates per token, and its memory bill follows the total[^3].
A 30B MoE model that activates 3B parameters per token needs roughly as much memory as a 30B dense model, while its per-token compute tracks the 3B active parameters[^3].
Batching lets tokens from many requests share one stored copy of the experts, so the memory is paid once.
Utilization depends on batch size: at batch size one, decoding reads fewer weight bytes per token, and the MoE advantage narrows as tokens collectively use most experts[^3].
Prefill is compute-intensive and decode is memory-intensive, which is why SGLang separates the two phases[^6].
On a personal machine at batch size one, experts can sit in host memory and be fetched on demand, with a sparsity-aware cache deciding what stays on the GPU[^5].

- Question 1: With $E=256$ experts, $k=8$ active experts per token, and a batch of $B=16$ tokens under the tutorial's uniform-routing model, how many distinct experts does the batch touch, and how many tokens does each touched expert serve on average?
- Question 2: Why does a low-load MoE server leave much of its resident expert memory idle, and what changes as traffic grows?
- Question 3: Why does PD disaggregation help when a long prefill in a unified scheduler can delay decode steps[^6]?
- Question 4: Why does a redundant copy of a hot expert help load balance, and what cost limits how often the expert arrangement can be updated[^6]?
- Question 5: Why does offloading help at batch size one but lose its advantage as batches grow and touch more experts?
- Question 6: How would you estimate the cost of a cache miss over PCIe, given an expert's size in bytes and the link bandwidth?

## References

[^1]: huggingface.co (2023). [*Mixture of Experts Explained*](https://huggingface.co/blog/moe). huggingface.co (guide).
[^2]: DeepSeek-AI, Liu, A., Feng, B., Xue, B., Wang, B., Wu, B., Lu, C., Zhao, C., Deng, C., Zhang, C., et al. (2024). [*DeepSeek-V3 Technical Report*](https://arxiv.org/pdf/2412.19437). arxiv.org (scholarly). Cited at pages 1, 9, 10, 11, 18, 19, 20, 27, 28.
[^3]: developer.nvidia.com (2026). [*Dense vs. MoE Models: Active Parameters, Throughput, and When to Choose Each*](https://developer.nvidia.com/blog/dense-vs-moe-models-active-parameters-throughput-and-when-to-choose-each). developer.nvidia.com (official).
[^4]: dl.acm.org (n.d.). [*MoE-Inference-Bench: Performance Evaluation of Mixture of Expert Large Language and Vision Models | Proceedings of the SC '25 Workshops of the International Conference for High Performance Computing, Networking, Storage and Analysis*](https://dl.acm.org/doi/10.1145/3731599.3767706). dl.acm.org (scholarly).
[^5]: Xue, L., Fu, Y., Lu, Z., Mai, L., Marina, M. (2024). [*MoE-Infinity: Efficient MoE Inference on Personal Machines with Sparsity-Aware Expert Cache*](https://ar5iv.labs.arxiv.org/html/2401.14361). ar5iv.labs.arxiv.org (scholarly). Cited at pages 1, 2, 3, 4, 6, 8.
[^6]: lmsys.org (n.d.). [*Deploying DeepSeek with PD Disaggregation and Large-Scale Expert Parallelism on 96 H100 GPUs*](https://www.lmsys.org/blog/2025-05-05-large-scale-ep). lmsys.org (institutional).
