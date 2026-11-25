# Shrinking the Memory Footprint of Large Language Models: A Tutorial on Quantization, KV-Cache Compression, Low-Rank Methods, Sparsity and Offloading

## Where the memory goes: a transformer for a numerical analyst

A transformer turns each token into a vector of numbers and passes these vectors through stacked layers of attention and feed-forward matrix products[^1].
One token is approximately four English characters[^1].

A parameter is one learned number in these matrices, and nearly all parameters in a transformer block come from four linear layers with sizes $(h_d, 3h_d)$, $(h_d, h_d)$, $(h_d, 4h_d)$ and $(4h_d, h_d)$, where $h_d$ is the hidden dimension[^2].
Summing the four layer sizes gives $3h_d^2 + h_d^2 + 4h_d^2 + 4h_d^2 = 12h_d^2$ per block, so for $n_l$ transformer layers the total parameter count is approximately $12 n_l h_d^2$[^2].

$$
\text{parameters} \approx 12\, n_l\, h_d^2
$$

For mixed-precision training with the Adam optimizer, the parameters and gradients are stored in FP16, and the optimizer states consist of FP32 momentum, variance, parameters, and gradients[^2].
In total, each parameter requires 20 bytes of memory for model states[^2].
Activations, the intermediate results of the forward pass kept for the backward pass, form a separate residual term that depends on batch size and sequence length[^2].
Regular 16-bit finetuning of a LLaMA 65B model requires more than 780 GB of GPU memory[^3].

At inference, the two main contributors are the model weights and the KV cache, which stores the keys and values of past tokens so they need not be recomputed[^1].
A 7-billion-parameter model in 16-bit precision takes roughly 14 GB for its weights, since $7 \times 10^9 \times 2$ bytes is about 14 GB[^1].
Prefill processes the input tokens in parallel as a matrix-matrix operation that saturates the GPU, while decode generates one token at a time as a matrix-vector operation that is memory-bound[^1].

Model size has outgrown GPU memory: the largest dense models grew over 1000x in three years, while GPU memory grew only 5x, from 16 GB to 80 GB, which the authors call the GPU memory wall[^2].
The later sections follow one map: quantization stores weights in fewer bits, low-rank adapters train a small set of parameters while the full model stays fixed, and offloading moves state to CPU or NVMe memory with a bandwidth concern[^3][^2].

## Quantization: trading bits for rounding error

Quantization maps a high-precision value into discrete levels[^4].
The integer uniform quantizer used in SmoothQuant is $\bar{X}_{\mathrm{INT8}} = \lceil X_{\mathrm{FP16}}/\Delta \rfloor$ with $\Delta = \max(|X|)/(2^{N-1}-1)$, where $X$ is the floating-point tensor, $\bar{X}$ its quantized counterpart, $\Delta$ the step size, $\lceil\cdot\rfloor$ the rounding function and $N$ the number of bits[^4].
For an asymmetric tensor, such as one after ReLU, a zero-point is added to shift the grid[^4].
Kuzmin et al. define the rounding error as $R(w)=Q(w)-w$, and their expected quantization error splits into a rounding term plus clipping terms outside the quantization range[^5].

Weights are the easier target because they are fixed after training and their distribution is flat and uniform[^1][^4].
Activations are harder because a few fixed channels carry outliers about 100 times larger than most values, so one per-tensor scale leaves non-outlier channels only 2 to 3 effective levels[^4].

For a linear layer $Y = XW$, the input is $X\in\mathbb{R}^{T\times C_i}$ with $T$ tokens and $C_i$ input channels, and the weight is $W\in\mathbb{R}^{C_i\times C_o}$ with $C_o$ output channels[^4].
Integer GEMM kernels need both operands in INT8 to run at hardware speed, which is why W8A8 quantizes activations as well as weights[^4].

SmoothQuant rests on the identity $Y = (X\,\mathrm{diag}(s)^{-1})(\mathrm{diag}(s)\,W) = \hat{X}\hat{W}$, where $s\in\mathbb{R}^{C_i}$ is one smoothing factor per input channel, so the output is unchanged in exact arithmetic[^4].
The factor is set as $s_j = \max(|X_j|)^{\alpha}/\max(|W_j|)^{1-\alpha}$, where $\alpha$ is the migration strength; a larger $\alpha$ moves more difficulty to the weights[^4].
Shown experimentally, $\alpha=0.5$ balanced OPT and BLOOM, $\alpha=0.75$ suited GLM-130B, and an OPT-175B ablation found a sweet spot of about 0.4 to 0.6[^4].
On PyTorch with OPT models, SmoothQuant-O3 gave up to 1.51 times speedup and 1.96 times memory saving, whereas the mixed-precision LLM.int8() baseline was usually slower than FP16[^4].

LLM.int8() keeps outliers in FP16 and uses INT8 for the rest, which the SmoothQuant authors describe as hard to implement efficiently on hardware[^4].
The sources do not describe GPTQ or AWQ in detail; SmoothQuant mentions GPTQ only as a weight-only method[^4].
The step-size formula, the SmoothQuant identity and the rounding error are derived results, while the speedups and accuracy figures are experimental results on particular models and hardware.
The SmoothQuant authors report that the approach applies to various LLM designs, with tests on OPT, BLOOM, GLM-130B, MT-NLG 530B, LLaMA and instruction-tuned OPT-IML[^4].

## Going to 4 bits: NormalFloat, double quantization and paged optimizers

Uniform integer quantization maps values onto an evenly spaced grid scaled by the tensor's absolute maximum, so one large outlier leaves many bins unused[^3].
Pretrained weights are roughly zero-centred normal, so the authors rescale them into one fixed distribution and use levels that are normal quantiles, giving each bin an equal expected number of values[^3].
The authors call the result 4-bit NormalFloat (NF4) and argue it is information-theoretically optimal for zero-mean normal data; this is a design argument, not a measured result[^3].
The levels are $q_i=\tfrac12\left(Q_X\left(\tfrac{i}{2^k+1}\right)+Q_X\left(\tfrac{i+1}{2^k+1}\right)\right)$, where $Q_X$ is the quantile function of $N(0,1)$ and $k$ is the bit width[^3].

Quantizing the tensor in independent blocks, each with its own quantization constant, is the common approach to prevent the outlier problem[^3].
With 32-bit constants and blocksize 64, the constants cost $32/64=0.5$ bits per parameter[^3].
Double quantization quantizes these constants again, using 8-bit floats with blocksize 256 plus second-level 32-bit constants, so the cost becomes $8/64+32/(64\cdot 256)\approx 0.127$ bits per parameter, a saving of about 0.373 bits per parameter[^3].
The authors put this saving at about 3 GB for a 65B model[^3].

Paged optimizers use NVIDIA unified memory to move optimizer states to CPU RAM when the GPU runs out of memory and back when the update needs them, targeting memory spikes on long sequences during gradient checkpointing[^3].
The authors did not measure paging directly; at batch size 16 on 65B models with 48GB GPUs, paged optimizers matched regular optimizer speed[^3].
Experimentally, NF4 with double quantization matches BFloat16 mean 5-shot MMLU accuracy for LLaMA 7B to 65B, while FP4 trails by about one percentage point[^3].

## The KV cache: why it grows and how to shrink it

During decoding, a model produces one token at a time, and each new token depends on the keys and values of all previous tokens[^1].
The scaled dot-product attention operation maps query and key-value pairs to an output[^1].
Recomputing these keys and values at every step would be prohibitively expensive, so they are stored in a KV cache and reused[^6].

In the notation of the KVQuant paper, with $n$ layers, $h$ heads of dimension $d$, $e$ bytes per element, batch size $b$ and sequence length $l$, the cache holds $2 \cdot n \cdot h \cdot d \cdot e \cdot b \cdot l$ bytes, where the factor 2 counts keys and values[^6].
Since $h \cdot d$ is the model's hidden size, the cache grows linearly with both batch size and sequence length[^1][^6].

$$
M_{\mathrm{KV}} = 2 \cdot n \cdot h \cdot d \cdot e \cdot b \cdot l
$$

As a worked example, a Llama 2 7B model in 16-bit precision with batch size 1 has a cache of about 2 GB at sequence length 4096[^1].
Going to 128K tokens is 32 times longer, so at the same batch size the cache grows by the same factor, from about 2 GB to about 64 GB.
The KVQuant authors report a 64.0 GB fp16 cache for LLaMA-7B at sequence length 128K, a size they estimate for their own assumptions[^6].

Multi-query attention shares one set of keys and values across all heads, which reduces the cache but may cost accuracy and requires training or fine-tuning with it enabled[^1].
Grouped-query attention shares keys and values within groups of query heads, balancing memory and quality[^1].
PagedAttention addresses waste rather than size: it stores each cache in fixed-size, non-contiguous blocks, which removes fragmentation from static over-provisioning and allows larger batches[^1].

KVQuant lowers the precision of cached keys and values, since the cache dominates memory for long contexts[^6].
Keys have outlier channels with large average magnitude, so the authors quantize keys per channel and values per token, a 3.82 perplexity gain over per-token quantization for 3-bit LLaMA-7B[^6].
Rotary position embedding (RoPE) mixes channel pairs by position-dependent angles, so the authors quantize keys before RoPE and apply the rotation after dequantization, a further 0.82 perplexity gain at 3 bits[^6].
These are the authors' measurements on LLaMA-family and Mistral models, not general theorems[^6].

The sources do not cover eviction or token-selection methods in depth.

## Low-rank methods: updating a model without storing its optimizer state

LoRA keeps the pretrained weights fixed and trains only a small set of adapter parameters, augmenting a linear projection through an additional factorized projection[^3].
For a pretrained matrix $W \in \mathbb{R}^{d\times k}$, the update is factorized as $BA$, with $B \in \mathbb{R}^{d\times r}$ and $A \in \mathbb{R}^{r\times k}$, and the rank $r$ is small relative to $d$ and $k$[^7].
The adapter therefore has $r(d+k)$ trainable parameters instead of $dk$; for a $4096\times 4096$ matrix with $r=8$, this is about 65 thousand instead of 16.8 million, a ratio of roughly 256 to 1 (a derived calculation).
Because the base weights are frozen, gradients and optimizer state are stored only for the adapters, and the QLoRA paper reports that for a 7B LLaMA model the LoRA parameters take 26 MB while the 4-bit base model takes 5,048 MB[^3].
QLoRA keeps the base model frozen in 4-bit NormalFloat, dequantizes it to BFloat16 for each matrix multiplication, and computes weight gradients only for the 16-bit adapters[^3].
The authors report that this allows finetuning a 65B parameter model on a single 48GB GPU, where regular 16-bit finetuning needs more than 780 GB[^3].
Their finding that 4-bit QLoRA with NF4 and double quantization matches 16-bit LoRA on MMLU is a measured result, not a proof[^3].

LoRAMoE treats LoRA adapters as experts in a mixture-of-experts layer, where a router weights the experts' outputs in each feed-forward layer, with the backbone frozen during training[^7].
Its motivation is world-knowledge forgetting: the authors observe that large-scale instruction finetuning lowers closed-book QA performance and hypothesize that this comes from parameter changes to the pretrained model[^7].
Its localized balancing constraint splits the experts into one group for downstream tasks and one for aligning world knowledge, and balances experts only within each group[^7].
In the authors' experiments on one model and one data mixture, LoRAMoE avoided the closed-book QA collapse seen under plain finetuning, which is experimental evidence only[^7].
Mixture of LoRA Experts (MoLE) addresses composing several separately trained LoRAs[^8].
Linear arithmetic composition sums the updates, and the authors observe that composing four or more LoRAs can disorder outputs, while normalizing the weights dilutes each adapter's characteristics[^8].
MoLE instead treats each layer of trained LoRAs as an expert and learns a gating function per layer, with all other parameters frozen[^8].
These experts mainly address composition and forgetting; their memory benefit comes from the frozen backbone and the small adapters.
The sources do not cover gradient projection methods in depth, so this section mentions them only as a method the sources leave out.

## Sparsity and pruning: removing parameters, and when quantization wins

Sparsity removes parameters by setting them to zero, and it is a different operation from quantization[^9].
Zeroing weights alone saves neither memory nor latency, because the dense tensor still holds the zeros and a matrix multiply computes with them[^9].
Real savings therefore need a compressed storage layout and sparse kernels that skip the pruned elements[^9].

- Unstructured sparsity gives every element its own mask, the most flexible pattern, but it needs sparsity above 98% before performance benefits appear[^9].
- Semi-structured N:M sparsity keeps at most N nonzero values in every group of M consecutive values; 2:4 keeps two nonzero values in every group of four, fixing the level at 50%[^9].
- For 2:4 sparsity, the source reports matrix multiplication up to 1.7x faster with no numerical loss[^9].

Mixture-of-experts models are a form of conditional sparsity, since a router selects only some experts for a given token, but all experts must still reside in memory.

Kuzmin et al. compare the two methods analytically using the signal-to-noise ratio in decibels, $\mathrm{SNR}_{\mathrm{dB}} = 10\log_{10}\left(E[W^2]/E[(W-F(W))^2]\right)$, where $W$ is a weight and $F(W)$ is the weight after quantization or pruning[^5].
Compression is measured against FP16, and 50% pruning is compared with INT8 and 75% pruning with INT4[^5].
For a standard normal distribution the authors report 19.1 dB SNR for INT4 quantization against 5.6 dB for 75% pruning[^5].
Heavy tails hurt quantization, so pruning wins only at very high compression, roughly 2 to 3 bits per value[^5].

The authors argue that unstructured pruning bounds all pruning methods, so where quantization beats unstructured pruning it also beats (semi-)structured pruning[^5].
In post-training layer experiments, quantization mostly outperforms pruning at moderate compression, and the methods become more comparable at higher compression ratios[^5].
An unstructured mask needs at least 1 bit per weight, a 6.25% overhead on 16-bit weights, whereas INT8 needs only a scaling factor per tensor or channel[^5].

## Offloading to CPU and NVMe: trading bandwidth for capacity

The idea of offloading is to keep model data in CPU memory or on NVMe storage and move each piece to the GPU only when it is needed[^2].
The cost is bandwidth: a single GPU reaches only about 12 GB/s over PCIe to CPU or NVMe memory[^2].

The authors model efficiency with arithmetic intensity $ait$, the ratio of total computation to the data the computation requires, achievable peak compute $peak_{tp}$, and bandwidth $bw$, assuming no compute and communication overlap[^2].
Letting $C$ be the total computation and $D$ the data moved, compute time is $t_c = C/peak_{tp}$ and communication time is $t_m = D/bw$[^2].
Efficiency is $t_c/(t_c+t_m)$, which gives the following form[^2].

$$
\text{efficiency} = \frac{ait \times bw}{ait \times bw + peak_{tp}}
$$

Efficiency rises with $ait$ and $bw$, and a higher compute peak demands more bandwidth for the same efficiency.
The authors use a peak of 70 TFlops per GPU, measured on a V100 DGX-2 box with non-GPU communication turned off[^2].

- Parameters and gradients: over 70 GB/s is needed, and at that bandwidth transfer can in theory be fully overlapped with computation[^2].
- Optimizer states: about 4x the bandwidth of parameters and gradients is needed for 50% efficiency, and they cannot be overlapped[^2].
- Activation checkpoints: about 2 GB/s sustains over 50% efficiency at hidden size 2K[^2].

A single PCIe link at about 12 GB/s is well below the 70 GB/s needed for parameters and gradients, so the design has to aggregate links or overlap transfers[^2].
Large batches hide transfer cost because they raise arithmetic intensity[^2].
ZeRO-Infinity partitions parameters across all data parallel processes so that all PCIe links are active in parallel[^2].
It trains models of up to 20 trillion parameters on 512 GPUs, with throughput of up to 49 TFlops/GPU[^2].
These bandwidth figures come from one V100 DGX-2 configuration and are illustrations, not general laws[^2].
The evaluation concerns training, and the sources do not analyze offloading for inference[^2].

## Side-by-side comparison and accuracy-versus-memory evidence

The table compares the main approaches on what they target, what they risk, and the kind of evidence behind them.

| Approach | Memory targeted | Training or inference | What is lost or risked | Hardware needs | Evidence kind |
|---|---|---|---|---|---|
| Weight-only INT8 quantization | Weights | Inference | Weights converted back to higher precision for matmul | Dequantization support | Discussed as prior work[^4] |
| SmoothQuant (W8A8) | Weights, activations | Inference | Activation outliers; accuracy depends on migration strength | INT8 GEMM kernels | Derived identity; shown experimentally[^4] |
| KV-cache quantization (KVQuant) | KV cache | Inference | Perplexity loss, under 0.1 at 3-bit | Custom CUDA kernels | Shown experimentally[^6] |
| MQA/GQA and paging | KV cache | Inference | Possible accuracy drop with MQA | Standard serving stack | Sources give no measurement[^1] |
| LoRA / QLoRA | Gradients, optimizer state, weights | Training | NF4 with LoRA matches 16-bit LoRA on MMLU | Single 48GB GPU for 65B (authors' report) | Shown experimentally[^3] |
| Low-rank experts (MoLE) | Frozen backbone, small adapters | Training and inference | Normalized composition weakens each adapter's traits | Frozen backbone, small gating | Shown experimentally[^8] |
| Unstructured pruning | Weights | Inference | Accuracy; mask storage overhead | Sparse storage and kernels | Derived bound; shown experimentally[^5] |
| Structured and N:M (2:4) sparsity | Weights | Inference | Accuracy; speedup only for supported patterns | Hardware support for the pattern | Argued from unstructured bound[^5][^9] |
| Offloading (ZeRO-Infinity) | Parameters, gradients, optimizer state | Training | Bandwidth; optimizer states need about 4x more | CPU or NVMe and fast links | Analytical model; throughput measured[^2] |

QLoRA composes quantization with low rank, using a 4-bit NF4 base with 16-bit LoRA adapters, and its paged optimizers address memory spikes during gradient checkpointing[^3].
Weight quantization alone does not shrink optimizer state, and LoRA does not reduce the frozen base weights, which is why the two are combined.
Paging and MQA/GQA target the KV cache and do not help weights or optimizer state[^1].
Quantization usually beats pruning at equal compression, except at very high compression[^5].
Evidence gaps remain: the sources give no measured accuracy for MQA, GQA or paging, and they do not describe GPTQ or AWQ in detail[^1][^4].

## Summary and check-your-understanding questions

The central principle is to identify the dominant memory term first, because a technique helps only when it attacks the component that fills the GPU[^6].
Reduce precision where the error is tolerable.
Once activation outliers are smoothed, INT8 weights and activations can nearly halve GPU memory usage compared with FP16[^4].
Low-rank adapters keep adapter memory small, though most finetuning memory goes to activation gradients rather than adapter parameters[^3].
Exploit sparsity only when the hardware can use it.
Trade bandwidth for capacity: offloading keeps the GPU busy when each byte moved supports enough computation, or when overlap hides the transfer[^2].

- Why does an activation outlier ruin per-tensor INT8, and what does SmoothQuant change?
- For a rank-$r$ LoRA update of a $d \times k$ matrix, how many parameters are saved relative to full finetuning?
- How does the KV cache size scale with sequence length and batch size, and which methods reduce it?
- Why does unstructured pruning not automatically save memory?
- When does offloading keep the GPU busy, and what limits it?

## References

[^1]: Verma, S. (2023). [*Mastering LLM Techniques: Inference Optimization*](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization). developer.nvidia.com (commercial).
[^2]: Rajbhandari, S., Ruwase, O., Rasley, J., Smith, S., He, Y. (2021). [*ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning*](https://arxiv.org/pdf/2104.07857). arxiv.org (scholarly). Cited at pages 1, 3, 6.
[^3]: Dettmers, T., Pagnoni, A., Holtzman, A., Zettlemoyer, L. (2023). [*QLoRA: Efficient Finetuning of Quantized LLMs*](https://arxiv.org/abs/2305.14314). arxiv.org (scholarly). Cited at pages 1, 2, 3, 4, 5, 6, 7, 8.
[^4]: Xiao, G., Lin, J., Seznec, M., Hao, W., Demouth, J., Han, S. (2023). [*SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models*](https://proceedings.mlr.press/v202/xiao23c/xiao23c.pdf). International Conference on Machine Learning. Cited at pages 1, 2, 3, 4, 6, 7, 8, 12.
[^5]: Kuzmin, A., Nagel, M., van Baalen, M., Behboodi, A., Blankevoort, T. (2023). [*Pruning vs Quantization: Which is Better?*](https://ar5iv.labs.arxiv.org/html/2307.02973). ar5iv.labs.arxiv.org (scholarly). Cited at pages 2, 3, 6, 9.
[^6]: stat.berkeley.edu (2024). [*KVQuant: Towards 10 Million Context Length LLM*](https://www.stat.berkeley.edu/~mmahoney/pubs/neurips-2024-kvquant.pdf). stat.berkeley.edu (scholarly).
[^7]: Dou, S., Zhou, E., Liu, Y., Gao, S., Zhao, J., Shen, W., Zhou, Y., Xi, Z., Wang, X., Fan, X., et al. (2023). *LoRAMoE: Alleviate World Knowledge Forgetting in Large Language Models via MoE-Style Plugin*. arXiv preprint 2312.09979. Cited at pages 1, 4, 10, 11.
[^8]: Wu, X., Huang, S., Wei, F. (2024). *Mixture of LoRA Experts*. arXiv preprint 2404.13628. Cited at pages 1, 2, 4.
[^9]: PyTorch Contributors (n.d.). [*Sparsity Overview*](https://docs.pytorch.org/ao/stable/contributing/sparsity.html). docs.pytorch.org (official).
