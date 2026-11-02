---
title: Sparse Attention
type: concept
aliases:
  - Longformer
  - BigBird
  - Sparse Transformers
  - block sparse attention
tags:
  - attention
  - efficient-attention
  - sparse-attention
  - longformer
  - bigbird
  - long-context
sources:
  - "12 - Sparse Attention (Longformer, BigBird)"
created_index: 18
---

Sparse attention reduces the $O(n^2)$ cost of full attention by letting each token attend only to a structured subset of positions — typically a local window plus a few global tokens. Longformer (2020) and BigBird (2020) are the canonical variants, enabling $O(n \sqrt{n})$ or $O(n)$ attention for long documents. Although modern long-context models mostly pair full attention with FlashAttention, the local-plus-global pattern keeps resurfacing in sliding-window models, streaming attention, and hybrid architectures, so sparse attention remains essential background for reading 2020-era papers and for understanding why modern LLMs are built the way they are.

> [!info] TL;DR
> Sparse attention reduces the $O(n^2)$ cost of full attention by attending only to a subset of positions — typically local windows plus a few global tokens. Longformer (2020) and BigBird (2020) are the canonical variants. Enables $O(n \sqrt{n})$ or $O(n)$ attention for long documents.

## The problem: $O(n^2)$ doesn't scale

In full attention, every token attends to every other token. For a sequence length of 16k that is 256M attention scores per head per layer; for 128k it is 16B. Memory and compute grow quadratically with sequence length, so for long-document tasks (books, codebases, legal contracts) full attention is infeasible. **Sparse attention** reduces this cost by attending only to a structured subset of positions.

## The local + global pattern

The most common sparse pattern combines a banded local window with a handful of global tokens:

```
Position:  0 1 2 3 4 5 6 7 8 9 ...
Token 0:   [global] X X X X X X X X X    ← attends to everything
Token 1:   X X X . . . . . . .          ← attends to local window
Token 2:   X X X X . . . . . .
Token 3:   . X X X X . . . . .
Token 4:   . . X X X X . . . .
...
Token 9:   . . . . . . . X X X
```

The **local window** means each token attends to its $w$ neighbors on each side, capturing local context efficiently. The **global tokens** are a few designated tokens (e.g., `[CLS]`, the first token, or task-specific tokens) that attend to everything and are attended to by everything, providing the long-range information flow that a pure window would block. The resulting cost is $O(n \cdot w + n \cdot g)$, where $w$ is the window size and $g$ is the global count — linear in $n$ for fixed $w, g$.

## Longformer

Longformer (Beltagy et al. 2020) uses **sliding window** attention plus a **dilated sliding window** (skipping positions, like dilated CNNs) plus optional global tokens. The window size is typically 512, with dilated windows in higher layers giving a larger receptive field, and global tokens chosen for the task — `[CLS]` for classification or the question tokens for QA. It achieved SOTA on long-document tasks at the time.

## BigBird

BigBird (Zaheer et al. 2020) extends the local-plus-global recipe with random connections:

```
Pattern:   local window  +  global  +  random
```

The **random** connections are critical for theoretical reasons — they ensure the attention graph is a "random graph" with good spectral properties, which BigBird proves approximates full attention in theoretical limits. BigBird is also theoretically a universal approximator and Turing-complete (like the full Transformer), unlike some sparser patterns.

## BigBird's theoretical guarantee — why random connections matter

BigBird's pattern is **local window + global tokens + random connections**, and the random connections aren't just for empirical quality — they provide a theoretical guarantee. BigBird proves that this pattern is:

1. **A universal approximator**: it can approximate any sequence-to-sequence function to arbitrary precision (like the full Transformer).
2. **Turing complete**: it can simulate any Turing machine (like the full Transformer).
3. **A random graph with good spectral properties**: the random connections ensure the attention graph's eigenvalues are well-behaved, which is what makes it approximate full attention.

Without the random connections, local+global patterns (like Longformer without random) are NOT universal approximators — there exist functions they can't approximate. The random connections are theoretically essential, not just an empirical trick.

### Why this matters less in practice

In practice, BigBird's theoretical advantage doesn't translate to better quality than Longformer (which lacks random connections). The theoretical guarantee is about worst-case functions, not real-world text. This is also why FlashAttention (which is exact, not approximate) replaced both — it gives full attention quality without the $O(n^2)$ cost.

## Sparse Transformers (Child et al. 2019)

Sparse Transformers (Child et al. 2019) is an earlier pattern that uses a combination of local windows, strided patterns (attend every $k$-th token), and fixed column/row patterns. It was designed for image and audio generation, domains where long sequences are common.

## Block sparse attention

Block-sparse patterns (as in Mesh Transformer) divide the sequence into blocks and attend at block granularity: some blocks are fully attended, others are skipped, and the pattern can be fixed or learned. Block-sparse attention has been used in some long-context models — for example GPT-3 variants and some MoE models.

## Why sparse attention lost to FlashAttention and long-context scaling

In 2020, sparse attention was the only way to handle 16k+ context. By 2022–2023, two things changed:

1. **FlashAttention** made full attention 4–10× cheaper, so $O(n^2)$ became feasible for $n = 32k$ or even 128k.
2. **YaRN / NTK scaling** allowed RoPE models to extend context cheaply without retraining.

So modern LLMs (Llama 3 128k, Gemini 1.5 1M) use **full attention** with FlashAttention, not sparse attention: the $O(n^2)$ is manageable up to ~1M tokens with FlashAttention-3 (FA3) and careful memory management.

### When sparse attention still wins

Three cases still favor sparse patterns. **Extreme long context** (10M+ tokens): FlashAttention can't make $n^2$ tractable here. **Memory-constrained inference**: if you can't fit the KV cache, sparse patterns reduce it. And **specific structured data** (e.g., DNA sequences, where locality is strong).

For most 2026 use cases, **full attention + FlashAttention is preferred**. Sparse attention is a research area, not the default.

## Worked example: Longformer-style sliding window attention

```python
import torch.nn.functional as F

def sliding_window_attention(Q, K, V, window_size, is_causal=True):
    """Simplified sliding window attention. Real implementations use custom CUDA kernels."""
    B, H, N, D = Q.shape
    # Create a mask: token i attends to j if |i - j| <= window_size
    positions = torch.arange(N, device=Q.device)
    mask = (positions[None, :] - positions[:, None]).abs() <= window_size
    if is_causal:
        mask = mask & (positions[None, :] <= positions[:, None])
    mask = mask.unsqueeze(0).unsqueeze(0)  # (1, 1, N, N)
    
    scores = Q @ K.transpose(-2, -1) / math.sqrt(D)
    scores = scores.masked_fill(~mask, float('-inf'))
    attn = F.softmax(scores, dim=-1)
    return attn @ V
```

In practice, use the Longformer / BigBird implementations from HuggingFace or the dedicated libraries rather than rolling your own kernels.

## Why this matters

Sparse attention is the **historical answer** to long context: understanding it helps you read 2020-era papers and understand why modern LLMs do what they do. The **local + global pattern** recurs in modern forms — sliding window attention (Mistral), local + sink tokens (StreamingLLM), and block-sparse patterns (Mamba hybrids). And for **streaming / online applications**, sparse attention is still directly relevant, because you can't attend to future tokens you haven't seen.

## Production implications

For most long-context use cases, **use a full-attention model** (Llama 3, Qwen, etc.) with FlashAttention; don't use sparse-attention models unless you have a specific reason. For extreme long context (>1M tokens), watch for sparse-attention models or hybrid architectures. For **streaming / online ASR**, sparse attention with a sliding window is appropriate.

## Common pitfalls and failure modes

Four pitfalls cover most mistakes. **Treating sparse attention as equivalent to full attention** — it's an approximation, and quality can differ. **Wrong window size** — too small misses long-range dependencies, too large loses the efficiency benefit. **Forgetting the global tokens** — without them, information can't flow across the full sequence. **Incompatibility with FlashAttention** — most sparse patterns can't use FlashAttention's tiled kernel because the pattern doesn't fit the tile structure, though some libraries have specialized sparse FlashAttention kernels.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Quality worse than full attention | Sparse pattern too restrictive | Add more global tokens; or use full attention + FA |
| No long-range information flow | Missing global tokens | Always include a few global tokens (e.g., [CLS]) |
| Incompatible with FlashAttention | Sparse pattern doesn't fit tile structure | Use specialized sparse-FA kernels; or switch to full attention |

## Interview questions

1. **Q: Why does BigBird include random connections?**
   A: The theoretical guarantee. BigBird proves that local + global + random is a universal approximator and Turing complete. Without random connections, local+global patterns can't approximate all functions. The random connections ensure the attention graph has good spectral properties. In practice, this theoretical advantage doesn't translate to better quality than Longformer (which lacks random), which is why FlashAttention (exact) replaced both.

2. **Q: Why did sparse attention lose to FlashAttention?**
   A: Two changes in the 2022–2023 period. (1) FlashAttention made full attention 4-10× cheaper — $O(n^2)$ became feasible for 128K+. (2) YaRN/NTK scaling allowed RoPE models to extend context without retraining. Modern LLMs use full attention + FA, not sparse. Sparse still wins for extreme long context (10M+), memory-constrained inference, and structured data.

3. **Q: When would you use sparse attention in 2026?**
   A: Three cases. (1) **Extreme long context (10M+)** — FlashAttention can't make $n^2$ tractable. (2) **Memory-constrained inference** — sparse patterns reduce KV cache. (3) **Structured data** (DNA, where locality is strong). For most use cases (up to 1M tokens), full attention + FlashAttention is preferred.

## Further reading

- Beltagy, Peters, Cohan (2020), *Longformer: The Long-Document Transformer*.
- Zaheer et al. (2020), *Big Bird: Transformers for Longer Sequences*.
- Child et al. (2019), *Generating Long Sequences with Sparse Transformers*.

## See also

- [[Attention and Transformers MOC]]
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — what replaced sparse attention
- [[Linear Attention]] — the alternative efficiency approach
- [[Sliding Window Attention]] — modern local attention
- [[YaRN and NTK-Aware Scaling]] — cheap context extension for RoPE models
- [[GQA MQA and MLA]] — KV-cache reduction for memory-constrained inference
- [[Mixture of Experts]] — some MoE long-context models use block-sparse patterns
