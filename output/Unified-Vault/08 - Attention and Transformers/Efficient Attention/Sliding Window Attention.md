---
title: Sliding Window Attention
type: concept
aliases:
  - SWA
  - Sliding-Window Attention
  - CNN-style local attention
tags:
  - attention
  - efficient-attention
  - sliding-window
  - local-attention
  - kv-cache
  - long-context
sources:
  - "15 - Sliding Window Attention"
created_index: 17
---

Sliding window attention (SWA) restricts each token to attend only to a fixed window of recent tokens (e.g., the last 4096) instead of the full sequence. Because no token ever needs K/V older than its window, the KV cache becomes a constant-size ring buffer — $O(w)$ instead of $O(n)$ — which makes very long contexts cheap. Mistral 7B popularized the pattern, and Gemma 2, Mixtral, and Jamba all use it in some form.

> [!info] TL;DR
> Sliding Window Attention (SWA) restricts each token to attend to a fixed window of recent tokens (e.g., last 4096). Used by Mistral 7B, Gemma, and others. Reduces KV cache to $O(w)$ instead of $O(n)$, enabling very long contexts at low memory.

## The pattern

Each token attends to the previous $w$ tokens (plus itself):

```
Token 0: attends to [0]
Token 1: attends to [0, 1]
Token 2: attends to [0, 1, 2]
...
Token w: attends to [0, 1, ..., w]
Token w+1: attends to [1, 2, ..., w+1]   ← drops token 0
Token w+2: attends to [2, 3, ..., w+2]
...
```

Once the sequence is longer than the window, the window slides: token $w+1$ drops token 0 from its receptive set. This is essentially [[Sparse Attention]] with only the local window — no global tokens.

## The trick: the KV cache stays small

For full attention, the KV cache grows linearly with sequence length $n$: $O(n)$ per layer. For SWA with window $w$, each token only needs K/V for the last $w$ tokens, so the cache can be a **ring buffer** of size $w$ — old entries are overwritten.

Concretely, for MHA with full attention at 32k context the cache holds 32k tokens' worth of K/V per layer; with SWA at $w=4096$ over the same 32k context, only 4096 tokens' worth is retained — an **8x reduction**. This is what makes very long contexts (100k+) feasible even on consumer GPUs.

## The trade-off: no "true" long context

SWA's limitation is that a token at position 100k cannot directly attend to a token at position 50k. Information must propagate through the layers' receptive field:

- Layer 1: each token sees $w$ tokens before.
- Layer 2: each token sees $w + w = 2w$ tokens before (via layer 1).
- Layer $L$: each token sees $L \cdot w$ tokens before.

For a 32-layer model with $w = 4096$, the effective receptive field is ~131k tokens — long enough for most contexts, but information degrades through the layers, since each hop is a soft attention. In practice SWA models handle long context reasonably well, but full-attention models (Llama 3, Qwen 2.5) often do better on tasks requiring precise long-range retrieval.

## Complexity analysis

For sequence length $n$ and window size $w$:

| Attention type | Compute per layer | Memory (KV cache) |
|----------------|-------------------|-------------------|
| Full attention | $O(n^2 \cdot d)$ | $O(n \cdot d)$ |
| Sliding window | $O(n \cdot w \cdot d)$ | $O(w \cdot d)$ |
| Sparse (Longformer) | $O(n \cdot (w + g) \cdot d)$ | $O(n \cdot d)$ |

For $n = 32\text{K}$ and $w = 4\text{K}$: full attention is $n^2 = 10^9$ operations, while SWA is $n \cdot w = 1.3 \times 10^8$ — 8× less compute. The KV cache is 8× smaller too.

### Effective receptive field through layers

The key insight: stacking $L$ SWA layers gives an effective receptive field of $L \cdot w$. Each layer attends to $w$ previous tokens; after $L$ layers, information from $L \cdot w$ tokens back can reach the current token. For Mistral 7B (32 layers, $w = 4096$), the effective receptive field is $32 \times 4096 = 131\text{K}$ tokens — matching the model's 128K context. This is why Mistral 7B can handle 128K context despite each layer only attending to 4K tokens.

### Information propagation

```
Layer 1: token t attends to [t-4095, t]
Layer 2: token t attends to [t-4095, t] (after layer 1)
         But layer 1 already incorporated info from [t-8190, t-4096]
         So layer 2 effectively has info from [t-8190, t]
...
Layer 32: token t has info from [t-131040, t]
```

This is the same principle as CNNs — stacking local operations gives a global receptive field. SWA is "CNN-style local attention" applied to sequences.

## Mistral 7B's SWA

Mistral 7B (2023) popularized SWA. Its window size is 4096, and with 32 layers the effective receptive field is ~131k. It combined SWA with GQA and FlashAttention for fast inference, and showed that SWA gives a strong quality/speed/memory trade-off. The context limit is "soft": the model can technically process 100k tokens, but only the last ~131k are "in scope" for any given prediction.

## Gemma and other models

Gemma 2 uses SWA in alternating layers — some layers full attention, others SWA — capturing the best of both: full attention's quality plus SWA's efficiency. Mixtral (Mistral's MoE) also uses SWA.

## SWA in modern models

- **Mistral 7B** (2023): $w = 4096$, 32 layers → 131K effective receptive field.
- **Mixtral 8x7B**: SWA + MoE.
- **Gemma 2** (2024): SWA + global attention (alternating layers).
- **Jamba** (2024): SWA + Mamba (hybrid).

### SWA variants

- **Pure SWA**: every layer uses sliding window (Mistral 7B).
- **Alternating SWA + global**: some layers SWA, some global (Gemma 2). Balances local efficiency with global reach.
- **Dilated SWA**: window with gaps (like dilated CNNs) — wider receptive field at same compute.
- **SWA + sink tokens**: attend to first few tokens (sink) plus window — preserves global information (StreamingLLM).

### The StreamingLLM insight

A key finding (Xiao et al. 2023): LLMs need to attend to the **first few tokens** (sink tokens) to maintain stable generation. Pure SWA loses the sink tokens when the window slides past them. The fix: attend to sink tokens + sliding window. This enables **infinite-length generation** — the model can generate forever without quality degradation, as long as it attends to the first few tokens plus recent context.

## Sliding window vs. full attention: quality trade-off

Where SWA matches full attention: **local patterns** — most language phenomena are local (subject-verb agreement, local syntax, entity references within a paragraph); **generation quality** — for autoregressive generation, the next token usually depends on recent context, which SWA captures; and **throughput** — SWA is faster and uses less memory, enabling larger batch sizes.

Where SWA loses to full attention: **long-range dependencies** — if token $t$ needs to attend to token $t - 100\text{K}$ (e.g., a character mentioned 100K tokens ago), SWA can't do it directly, and information propagated through $L$ layers loses fidelity; **"needle in a haystack" retrieval** — finding a specific fact mentioned far away, where SWA struggles and full attention handles it; and **cross-document reasoning** — comparing two documents 50K tokens apart can't be done in one attention step.

Empirically, Mistral 7B with SWA matches or beats Llama 2 7B (full attention) on most benchmarks. The 8× KV cache reduction enables longer contexts and larger batch sizes, which often matters more than the rare long-range dependency. For most production use cases, SWA's quality is sufficient.

## Worked example: SWA implementation

```python
import torch
import torch.nn.functional as F
import math

class SlidingWindowAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads, window_size):
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.window_size = window_size
        self.W_q = torch.nn.Linear(d_model, d_model, bias=False)
        self.W_k = torch.nn.Linear(d_model, d_model, bias=False)
        self.W_v = torch.nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):
        B, N, D = x.shape
        H, dk, w = self.n_heads, self.d_k, self.window_size

        Q = self.W_q(x).view(B, N, H, dk).transpose(1, 2)  # (B, H, N, dk)
        K = self.W_k(x).view(B, N, H, dk).transpose(1, 2)
        V = self.W_v(x).view(B, N, H, dk).transpose(1, 2)

        # Full attention scores
        scores = Q @ K.transpose(-2, -1) / math.sqrt(dk)  # (B, H, N, N)

        # Create sliding window mask: token i attends to [max(0, i-w+1), i]
        positions = torch.arange(N, device=x.device)
        relative_dist = positions[None, :] - positions[:, None]  # (N, N)
        # Mask: 1 if within window and not future (causal), 0 otherwise
        mask = (relative_dist >= 0) & (relative_dist < w)  # (N, N)
        scores = scores.masked_fill(~mask[None, None, :, :], float('-inf'))

        attn = F.softmax(scores, dim=-1)
        return (attn @ V).transpose(1, 2).reshape(B, N, D)

# Mistral 7B: 32 layers, w=4096
# At layer 32, effective receptive field = 32 * 4096 = 131K tokens
# This is why Mistral 7B can handle 128K context
```

## SWA + KV cache: the ring buffer

At inference the KV cache for SWA is a **ring buffer** — when the cache is full, the oldest entries are overwritten, keeping memory at $O(w)$ regardless of sequence length:

```python
class RingBufferKVCache:
    def __init__(self, window_size, n_layers, n_heads, head_dim):
        self.w = window_size
        # Allocate window_size slots per layer/head
        self.cache = torch.zeros(n_layers, n_heads, window_size, head_dim)
        self.ptr = 0  # next position to write
        self.size = 0  # how many tokens currently stored

    def append(self, k, v):
        # k, v: (n_layers, n_heads, 1, head_dim) for one new token
        self.cache[:, :, self.ptr] = k.squeeze(2)
        self.ptr = (self.ptr + 1) % self.w
        self.size = min(self.size + 1, self.w)

    def get(self):
        # Return last `size` tokens in order
        if self.size < self.w:
            return self.cache[:, :, :self.size]
        # Wrap-around: concatenate two halves
        return torch.cat([self.cache[:, :, self.ptr:], self.cache[:, :, :self.ptr]], dim=2)
```

This is more complex than a simple growing cache but uses constant memory. A production-style variant with separate K and V caches and multi-token updates looks like this:

```python
class RingBufferKVCache:
    def __init__(self, window_size, n_layers, n_heads, head_dim, dtype=torch.float16):
        self.window_size = window_size
        # Pre-allocate cache of size w
        self.k_cache = torch.zeros(n_layers, window_size, n_heads, head_dim, dtype=dtype)
        self.v_cache = torch.zeros(n_layers, window_size, n_heads, head_dim, dtype=dtype)
        self.pos = 0  # current write position

    def update(self, new_k, new_v):
        """Add new K, V to cache, overwriting oldest if full."""
        n_new = new_k.size(1)
        for i in range(n_new):
            self.k_cache[:, self.pos] = new_k[:, i]
            self.v_cache[:, self.pos] = new_v[:, i]
            self.pos = (self.pos + 1) % self.window_size
```

## Why it matters

SWA is one of the **practical answers** to long context — not as flexible as full attention, but far cheaper in memory. For **streaming applications** (chatbots that should remember "recent" history but not all of it), SWA is conceptually perfect. Understanding it also helps you read Mistral / Gemma model cards and reason about their effective context.

## Production implications

For Mistral 7B / Mixtral, use the model's specified SWA window — vLLM, TGI, and llama.cpp all handle it correctly. The **long-context quality** of SWA models is worse than full-attention models for tasks needing precise retrieval of early-context info, so test carefully. Combine SWA with **prefix caching** for system prompts (which are still fully attended via the prefix). For new model training, SWA is a reasonable choice if memory is the binding constraint; otherwise full attention + GQA + FlashAttention is preferred.

## Common pitfalls and failure modes

The main pitfalls: **treating SWA as equivalent to full attention** (quality differs for long-range tasks); **wrong window size** (too small loses context, too large loses the memory benefit); **forgetting the ring buffer semantics** (a naive growing cache defeats the purpose); and the **SWA + RoPE interaction** — positions past the window still need correct RoPE rotations for the in-window tokens, so match the model's config.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Model can't retrieve far-away facts | SWA limits receptive field | Use full attention; or alternate SWA + global layers |
| Quality degrades on long generation | Lost sink tokens | Use StreamingLLM (sink + window); keep first few tokens |
| KV cache grows unboundedly | Not using ring buffer | Implement ring buffer; overwrite oldest entries |
| SWA + RoPE mismatch | Position past window has wrong RoPE | Match RoPE positions to in-window tokens |
| Throughput not improving | Not using specialized kernel | Use FlashAttention with SWA support; or custom CUDA kernel |

## Interview questions

**How does sliding window attention reduce KV cache size?** Each token attends to only the previous $w$ tokens (plus itself), so the KV cache only needs to store $w$ entries — $O(w)$ instead of $O(n)$ for full attention. For $w = 4096$ and $n = 128\text{K}$, that's a 32× reduction. Use a ring buffer: when the cache is full, overwrite the oldest entries. Memory stays at $O(w)$ regardless of sequence length.

**How does stacking SWA layers give a global receptive field?** Each layer attends to $w$ previous tokens. After $L$ layers, information from $L \cdot w$ tokens back can reach the current token (through layer-by-layer propagation). For Mistral 7B: 32 layers, $w = 4096$ → effective receptive field = 131K tokens, matching the 128K context. This is the same principle as CNNs — stacking local operations gives global reach.

**When does SWA lose to full attention?** When the task requires direct long-range attention: (1) retrieving a specific fact mentioned 100K tokens ago ("needle in a haystack"); (2) comparing two documents 50K tokens apart; (3) cross-document reasoning. SWA can propagate information through layers, but with fidelity loss. For most language tasks (local syntax, entity references, generation), SWA's quality is sufficient — Mistral 7B matches Llama 2 7B on most benchmarks.

**What is the StreamingLLM insight, and why does it matter?** LLMs need to attend to the first few tokens (sink tokens) to maintain stable generation. Pure SWA loses the sink tokens when the window slides past them, causing quality degradation on long generation. The fix: attend to sink tokens + sliding window. This enables infinite-length generation — the model can generate forever without quality loss, as long as it attends to the first few tokens plus recent context.

**How would you choose between SWA and full attention?** Use SWA when: (1) long context (128K+) with memory constraints — SWA's $O(w)$ cache enables it; (2) local patterns dominate (most language tasks); (3) throughput matters more than rare long-range retrieval. Use full attention when: (1) long-range retrieval is critical; (2) memory is not the bottleneck; (3) quality on "needle in a haystack" tasks matters. Many modern models (Gemma 2) alternate SWA and global layers to get both.

**How does SWA relate to CNNs?** SWA is "CNN-style local attention". A CNN applies a fixed kernel to local windows; SWA applies input-dependent attention to local windows. Both stack local operations to build a global receptive field. The difference: CNN weights are fixed (learned once); SWA weights are input-dependent (computed per position). Sliding window attention generalizes convolution — a conv is "local attention with fixed weights". This is why CNN-inspired patterns appear in efficient attention.

## Further reading

- Jiang et al. (2023), *Mistral 7B* (paper).
- Beltagy et al. (2020), *Longformer* — same idea, earlier application.

## See also

- [[Attention and Transformers MOC]]
- [[Sparse Attention]] — the broader family of restricted attention patterns.
- [[GQA MQA and MLA]] — orthogonal KV cache reduction.
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — complementary efficiency optimization (and fast SWA kernels).
- [[RoPE]] — positional encoding whose in-window positions must stay correct.
- [[Long-Range Dependencies]] — the capability SWA trades away.
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — the stacking-local-operations principle SWA borrows.
- [[KV Cache Mechanics]]
