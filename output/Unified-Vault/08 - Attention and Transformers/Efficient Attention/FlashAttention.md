---
title: FlashAttention
type: concept
aliases:
  - FlashAttention-2
  - FlashAttention-3
  - FA
  - FA2
  - FA3
  - IO-aware exact attention
tags:
  - attention
  - efficient-attention
  - flashattention
  - gpu
  - memory-hierarchy
  - online-softmax
sources:
  - "11 - FlashAttention"
created_index: 14
---

FlashAttention (Dao et al. 2022, Dao 2023, Shah et al. 2024) is an IO-aware *exact* attention algorithm: it computes precisely the same result as standard attention but tiles the computation so intermediate matrices stay in GPU SRAM, avoiding round-trips to slow HBM. It is 2–4x faster than naive attention with no quality loss, and it is the default in every modern LLM. Long-context training and serving at 32k–128k and beyond exist because of it.

> [!info] TL;DR
> FlashAttention (Dao et al. 2022, Dao 2023, Shah et al. 2024) is an IO-aware exact attention algorithm. It tiles the computation to keep intermediate matrices in GPU SRAM, avoiding HBM round-trips. **2–4x faster than naive attention with no quality loss.** The default in every modern LLM.

## The problem: naive attention is memory-bound

Standard attention computes:

$$
S = QK^T \quad (\text{seq\_len} \times \text{seq\_len})
$$

$$
P = \text{softmax}(S) \quad (\text{seq\_len} \times \text{seq\_len})
$$

$$
O = PV \quad (\text{seq\_len} \times d)
$$

The intermediate $S$ and $P$ are each $O(n^2)$ memory. For seq_len=8192 and bf16, that's 256 MB per attention head per layer; for a 32-layer model with 32 heads, the attention intermediates alone are ~256 GB — far more than GPU memory. Worse, every step reads/writes the full $n \times n$ matrix to HBM (the slow main GPU memory). **Most of the time is spent moving memory, not computing.**

## The insight: tiling

GPUs have a memory hierarchy:

- **HBM** (main memory): 40–80 GB, ~3 TB/s bandwidth.
- **SRAM** (on-chip, per-streaming-multiprocessor): ~20 MB total, ~19 TB/s bandwidth.

SRAM is ~6x faster than HBM, so keeping the attention computation entirely in SRAM would be much faster — but the $n \times n$ matrix doesn't fit in SRAM for $n > 1024$ or so. FlashAttention's solution: **tile** the computation. Process Q, K, V in blocks; for each block of Q, iterate over blocks of K, V, computing partial softmax statistics. The full $n \times n$ matrix is never materialized — only block-sized intermediates.

## The algorithm (conceptual)

```
for each block Q_i of Q:
    Initialize O_i = 0, m_i = -inf  # output, running max
    for each block K_j, V_j of K, V:
        S_ij = Q_i @ K_j.T          # block-sized scores
        m_new = max(m_i, rowmax(S_ij))
        P_ij = exp(S_ij - m_new)    # numerically stable
        # Rescale running sum
        O_i = exp(m_i - m_new) * O_i + P_ij @ V_j
        m_i = m_new
    O_i = O_i / rowsum(P_ij)  # final normalization
```

The trick is the **online softmax**: compute softmax incrementally without ever materializing the full $P$ matrix. Each block's contribution is accumulated with proper rescaling.

## The online softmax algorithm in mathematical detail

The key algorithmic insight: compute softmax incrementally without materializing the full $N \times N$ matrix. For each block of queries $Q_i$, maintain a running maximum $m_i$ and sum $l_i$:

```
# Initialize for query block i
m_i = -inf  # running max of scores
l_i = 0     # running sum of exp(scores - m_i)
O_i = 0     # running output

for each key block K_j, V_j:
    S_ij = Q_i @ K_j.T / sqrt(d)     # (block_size, block_size) scores
    m_new = max(m_i, rowmax(S_ij))   # update running max
    # Rescale running sum and output by exp(m_i - m_new)
    l_i = l_i * exp(m_i - m_new) + rowsum(exp(S_ij - m_new))
    O_i = O_i * exp(m_i - m_new) + exp(S_ij - m_new) @ V_j
    m_i = m_new

# Final normalization
O_i = O_i / l_i
```

This is **mathematically exact** — the output is identical to naive attention (up to floating-point error). The trick is that softmax can be computed block-by-block with proper rescaling, never materializing the full $N \times N$ matrix. This reduces memory from $O(N^2)$ to $O(N)$ (just the output and running statistics).

## Why it's a big deal

FlashAttention is **exact** — same output as naive attention (up to floating-point error), no approximation. It is **2–4x faster** in practice for typical sequence lengths, uses **10x less memory** (never materializes the $n \times n$ matrix), and provides **long-context enablement**: without FlashAttention, 32k+ context is impractical; with it, 128k is routine.

## FlashAttention-2 (2023)

Dao's update improved on v1 with better work distribution across GPU threads (less warp divergence), reduced non-matmul FLOPs (matmuls are 2x faster than other ops on Tensor Cores), and better support for different head dimensions and sequence lengths. Practically: 2x faster than v1, ~50% MFU (model FLOPs utilization) on A100 for typical workloads.

## FlashAttention-3 on Hopper (2024)

FlashAttention-3 (Shah, Funk, Dao et al. 2024) is Hopper-architecture-specific, with three key optimizations.

### Asynchronous warpgroups (WGMMA)

Hopper introduces **Warp Group Matrix Multiply Accumulate** (WGMMA) — an asynchronous matmul instruction that lets one warpgroup compute while another loads data. FA3 overlaps the GEMM (matmul) with the softmax computation, hiding the softmax latency. On H100, this gives ~50% MFU (vs ~35% for FA2).

### FP8 support

Hopper supports FP8 (E4M3 and E5M2) with Tensor Cores. FA3 uses FP8 for the QK^T and PV matmuls, doubling throughput vs FP16. The challenge: FP8 has limited range and precision, so the softmax (which needs numerical stability) stays in FP32. FA3 uses a hybrid: FP8 matmuls + FP32 softmax + FP8 accumulation with periodic rescaling.

### Low-precision softmax

FA3 computes the softmax in FP32 for stability but uses a fused kernel that minimizes FP32→FP8 conversion overhead. The result: ~1.2 PFLOPs/s on a single H100 (vs ~500 TFLOPs/s for FA2 in FP16).

Practically, FA3 is 1.5–2x faster than v2 on H100, and its FP8 mode can reach 1.2 PFLOPs/s on a single H100. For Blackwell (B200, 2024+), further optimizations are possible with second-gen Tensor Cores and NVLink.

## When FlashAttention helps most (and when it doesn't)

| Scenario | FA speedup vs naive | Notes |
|----------|---------------------|-------|
| Training, long context (8K+) | 4-8× | The main use case |
| Training, short context (<512) | 1.2-1.5× | Overhead dominates |
| Inference, prefill (long prompt) | 3-5× | Same as training |
| Inference, decode (single token) | 1.1-1.3× | No N² to eliminate; helps via memory |
| Causal masking | Same as non-causal | Masked blocks are skipped (no extra cost) |
| Sliding window | 1.5-2× | Less parallelism; but still faster than naive |

The speedup grows with $n$: at $n = 512$ it is modest, at $n = 8192$ it is 4–8x. The backward pass in training benefits more than the forward (3x speedup typical). Causal masking costs nothing extra — FlashAttention just skips masked blocks. (The exact crossover for "short" varies with the backend: overhead dominates below $n < 256$, the short-context row above uses <512, and the failure-mode table below fixes a <128 threshold for switching to the math backend — read them as one band, roughly 128–512, rather than a single cutoff.)

When it doesn't help much: **very short sequences** ($n < 256$) — overhead dominates — and **single-token decoding** (autoregressive generation), where there is no $n^2$ to eliminate; FlashAttention-2/3 still help via better memory access patterns, but the speedup is smaller. This is why speculative decoding (which adds prefill-like compute) benefits more from FA than plain decode.

## Using FlashAttention in practice

In PyTorch 2.0+:

```python
import torch.nn.functional as F

# Old way (slow, materializes n×n):
attn = F.softmax(Q @ K.transpose(-2, -1) / math.sqrt(d_k), dim=-1)
out = attn @ V

# New way (FlashAttention, fast, never materializes):
out = F.scaled_dot_product_attention(Q, K, V, is_causal=True)
# This dispatches to FlashAttention (or memory-efficient attention) automatically.
```

In HuggingFace Transformers:

```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    attn_implementation="flash_attention_2",  # or "sdpa" for PyTorch built-in
    torch_dtype=torch.bfloat16,
)
```

For full control, three methods in production:

```python
import torch
from transformers import AutoModelForCausalLM

# Method 1: PyTorch built-in SDPA (dispatches to FA automatically)
import torch.nn.functional as F
Q, K, V = torch.randn(3, 8, 1024, 64).to('cuda')  # (batch, heads, seq, dim)
out = F.scaled_dot_product_attention(Q, K, V, is_causal=True)
# This uses FA2 on Ampere+, FA3 on Hopper (if PyTorch >= 2.2)

# Method 2: HuggingFace with explicit FA2
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    attn_implementation="flash_attention_2",  # or "sdpa" for built-in
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Method 3: Direct flash-attn library
from flash_attn import flash_attn_func
out = flash_attn_func(Q, K, V, causal=True)  # Most control
```

## Why it matters

FlashAttention is **non-negotiable in modern LLM training and inference**. Without it, training a 70B model on 8k context would be 4x slower and 10x more memory-hungry. Long-context LLMs (128k, 1M+) exist **because** of FlashAttention — the naive $O(n^2)$ memory would make them impossible. Understanding FlashAttention helps you read performance benchmarks (which now always specify FlashAttention), diagnose "why is my training OOMing" (you're not using FlashAttention), and understand why kernels and kernel fusion matter.

## Production implications

Always use FlashAttention (or `sdpa`, which dispatches to it) — never naive `softmax(Q @ K.T) @ V` in production. For Hopper GPUs (H100), use FlashAttention-3 for a significant speedup over v2; for Blackwell (B200), watch for v3 extensions and new FP4 modes. In training, FA3's FP8 mode can double throughput, but watch for accuracy — verify the loss curve matches FP16/BF16 baselines. In inference, FA helps more on prefill than decode; decode is memory-bound on weights, not attention.

## Common pitfalls and failure modes

The recurring mistakes: a **head dimension not a multiple of 8** (Tensor Cores require it — FlashAttention may fall back to a slow path); a **causal mask applied separately** (pass `is_causal=True` to the FA call; applying a mask separately defeats the optimization); the **wrong dtype** (FA-2 requires fp16/bf16; FA-3 supports fp8 but with specific layouts); a **backward pass not using FA** (some libraries implement FA only for forward — make sure training uses FA both ways); and **forgetting to set `attn_implementation`** (HuggingFace defaults to "eager", i.e. naive, in some cases — explicitly set "flash_attention_2" or "sdpa").

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| FA not used (falls back to eager) | Head dim not multiple of 8; or wrong dtype | Ensure head_dim % 8 == 0; use bf16/fp16; check `attn_implementation` |
| Quality regression with FA3 FP8 | FP8 precision insufficient | Use FA2 in FP16/BF16; or validate that FP8 quality is acceptable |
| Slow on short sequences | FA overhead dominates | Use `math` backend for seq_len < 128 (`attn_implementation="eager"`) |
| OOM on long context | KV cache too large | Use GQA; quantize KV cache; use PagedAttention |

## Interview questions

**Explain the online softmax algorithm that makes FlashAttention work.** FA computes softmax block-by-block. For each query block, maintain a running max $m_i$ and sum $l_i$. When processing a new key block: (1) compute block scores $S_{ij} = Q_i K_j^T / \sqrt{d}$; (2) update running max $m_{new} = \max(m_i, \text{rowmax}(S_{ij}))$; (3) rescale running sum and output by $\exp(m_i - m_{new})$; (4) add the new block's contribution. After all blocks, normalize by $l_i$. This is mathematically exact — identical to naive attention. The trick: softmax can be computed incrementally with proper rescaling, never materializing the full $N \times N$ matrix. Memory drops from $O(N^2)$ to $O(N)$.

**What are the Hopper-specific optimizations in FlashAttention-3?** Three optimizations. (1) **Asynchronous warpgroups (WGMMA)** — overlap GEMM with softmax computation, hiding softmax latency; ~50% MFU on H100. (2) **FP8 support** — use FP8 for QK^T and PV matmuls, doubling throughput; softmax stays in FP32 for stability. (3) **Low-precision softmax** — a fused kernel minimizes FP32→FP8 conversion overhead. Result: ~1.2 PFLOPs/s on a single H100 (vs ~500 TFLOPs/s for FA2 in FP16).

**When does FlashAttention NOT help much?** Two cases. (1) **Short sequences (<512)** — the tiling overhead dominates; naive attention is comparable. (2) **Decode (single-token generation)** — there's no $N^2$ to eliminate (each step produces one token); FA helps via better memory access patterns but only 1.1-1.3×. For prefill and training (where $N^2$ is real), FA gives 4-8× speedup.

**Is FlashAttention exact or approximate?** **Exact**. The output is identical to naive attention up to floating-point error. The online softmax algorithm computes the exact same mathematical result — it just does so block-by-block with careful rescaling, never materializing the full $N \times N$ matrix. This is different from approximate methods ([[Linear Attention]]'s Performer and Linformer) which trade quality for speed. FA trades memory for compute (recomputes during backward) but not quality.

**How would you enable FlashAttention in a HuggingFace model?** Set `attn_implementation="flash_attention_2"` in `from_pretrained`. Or use `"sdpa"`, which dispatches to FA automatically via PyTorch's `scaled_dot_product_attention`. Requirements: (1) head_dim must be a multiple of 8; (2) dtype must be fp16 or bf16; (3) model must be on CUDA. If requirements aren't met, it silently falls back to eager (naive) attention. Always check the logs for the actual implementation used.

**How does FlashAttention interact with causal masking and sliding windows?** **Causal masking**: FA handles it for free — just skip blocks that are entirely masked; no extra cost vs non-causal. **Sliding window**: FA can handle it but with less parallelism (fewer blocks per query); still 1.5-2× faster than naive sliding window. The key: FA's tiling naturally aligns with block-sparse patterns, so masked blocks are skipped without compute. This is why FA works well with Mistral's sliding window attention and similar patterns.

## Further reading

- Dao, Fu, Ermon, Rudra, Ré (2022), *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*.
- Dao (2023), *FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning*.
- Shah, Funk, Dao (2024), *FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision*.
- Tri Dao's blog and GitHub: https://github.com/Dao-AILab/flash-attention

## See also

- [[Attention and Transformers MOC]]
- [[Self-Attention]] — what FA optimizes.
- [[Multi-Head Attention]] — FA works per-head.
- [[Scaled Dot-Product Attention]] — the operation being fused.
- [[Sparse Attention]] — alternative efficiency approach (approximate).
- [[Linear Attention]] — approximate $O(n)$ methods FA displaced.
- [[Sliding Window Attention]] — block-sparse pattern FA kernels accelerate.
- [[GQA MQA and MLA]] — KV-cache-side efficiency, complementary to FA.
- [[PagedAttention]]
- [[Inference and Production MOC]]
