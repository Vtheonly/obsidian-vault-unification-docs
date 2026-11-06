---
title: ALiBi
type: concept
aliases:
  - "ALiBi"
  - "Attention with Linear Biases"
tags:
  - attention
  - positional-encoding
  - alibi
  - extrapolation
  - long-context
sources:
  - "09 - ALiBi (Attention with Linear Biases)"
created_index: 1
---

ALiBi (Attention with Linear Biases; Press et al., 2022) replaces positional encoding with a simple linear bias on attention scores based on relative distance. There are no learned positional parameters, and the method has **true extrapolation**: train on 1024 tokens, work on 2048 and beyond. Although RoPE ultimately dominated the open-source ecosystem, ALiBi remains the conceptually clean demonstration that length extrapolation is achievable, and its multi-scale head design appears throughout modern attention.

> [!info] TL;DR
> ALiBi (Press et al. 2022) replaces positional encoding with a simple linear bias on attention scores based on relative distance. No learned positional parameters. **True extrapolation** — train on 1024 tokens, work on 2048+.

## The idea

Instead of adding positional encoding to inputs (absolute) or rotating Q/K (RoPE), ALiBi **directly biases the attention scores** based on relative distance:

$$
e_{ij} = \mathbf{q}_i \cdot \mathbf{k}_j + m \cdot (j - i)
$$

where $m$ is a head-specific slope. There are no learned parameters for position — just a fixed linear bias.

The slope $m$ is different per head, geometrically spaced:

$$
m_h = \frac{1}{2^h} \quad \text{e.g., } \frac{1}{2}, \frac{1}{4}, \frac{1}{8}, \ldots
$$

Different heads attend to different distance scales — close neighbors (steep slope) versus far-away tokens (gentle slope).

## Why it works

The bias $m(j - i)$ penalizes attending to far-away positions: the further away, the larger the penalty. This creates a strong locality prior — tokens prefer to attend to nearby tokens unless there's strong evidence otherwise.

Because the bias is a simple linear function of relative distance, it works for any sequence length — there are no parameters to retrain. Extrapolation is automatic: positions 1025, 2048, 10000 all get sensible biases.

## Extrapolation: ALiBi's killer feature

Train an ALiBi model on 1024 tokens. Test on 2048, 4096, even longer contexts. Perplexity keeps improving (or stays flat) — it doesn't break.

This is **true length extrapolation**, which RoPE doesn't have out of the box (RoPE needs YaRN or NTK-aware scaling for length extrapolation; see [[YaRN and NTK-Aware Scaling]]).

## Why ALiBi enables extrapolation

ALiBi's extrapolation property comes from its **relative, parameter-free** nature.

**No learned positional parameters.** RoPE and learned positional embeddings have parameters (or fixed frequencies) that are fitted to the training context length. At inference beyond that length, the parameters are operating out of distribution. ALiBi has **no learned positional parameters** — the bias is a fixed function of relative distance, so there is nothing to be "out of distribution".

**The bias is well-defined for any distance.** The bias $m \cdot (j - i)$ is defined for any integer $(j - i)$, no matter how large. At position 10000, the bias is $m \cdot 10000$ — large but finite and well-defined. The softmax handles it gracefully (far-away tokens get near-zero attention, which is the desired locality behavior).

**The locality prior is universal.** The assumption that "nearby tokens matter more" is true at any scale — whether the context is 1024 or 1M tokens. ALiBi encodes this prior directly, without learning. RoPE's relative position encoding is more flexible but can learn non-local patterns that don't extrapolate.

**Why this doesn't fully solve long-context.** ALiBi's locality prior is a **prior** — it can be wrong. For tasks requiring long-range attention (e.g., "find the fact mentioned 100K tokens ago"), the linear penalty makes long-range attention exponentially unlikely. The model can override the prior if the dot-product $q_i \cdot k_j$ is large enough, but the prior biases toward locality. This is why ALiBi is good for **extrapolation** (train short, test long without breaking) but not necessarily good for **long-range reasoning** (the model may not attend to far-away tokens even when it should).

## The multi-scale head design

The geometric spacing of slopes $m_h = 1/2^h$ gives ALiBi a **multi-scale** property:

- Head 1: slope 1/2 — strong locality (penalizes far tokens heavily).
- Head 2: slope 1/4 — moderate locality.
- Head 4: slope 1/16 — weak locality (attends further).
- Head 8: slope 1/256 — very weak locality (almost global).

Different heads attend at different distance scales. This is conceptually similar to **multi-scale attention** (dilated attention, BigBird), where different heads operate at different scales; to **CNN multi-scale** design, where different kernel sizes capture different patterns; and to **wavelet transforms**, i.e. multi-resolution analysis. The geometric spacing (powers of 2) ensures coverage from very local to almost global, with logarithmic efficiency — a clever design that gives ALiBi more flexibility than a single-slope approach.

Why geometric spacing? It covers a wide range efficiently. With 8 heads, slopes 1/2 to 1/256 cover 8 octaves — from "attend mostly to the previous token" to "attend globally". Linear spacing (1/2, 1/3, 1/4, ...) would waste capacity on similar scales. Geometric is the standard for multi-scale designs.

## ALiBi versus RoPE

| Aspect                    | ALiBi                           | RoPE                            |
|---------------------------|---------------------------------|---------------------------------|
| Positional info type      | Relative (additive bias on scores) | Relative (rotary on Q, K)      |
| Learned parameters        | None (fixed bias)               | None (fixed rotation)          |
| Extrapolation             |  Native (train 1024, test 2048+) |  Needs YaRN/NTK for extrapolation |
| Long-range attention      |  Penalized (linear bias)       |  Possible (no penalty)        |
| Implementation complexity | Low (add bias to scores)        | Medium (rotate Q, K)           |
| Used by                   | BLOOM, MPT                      | Llama, Mistral, Qwen, Gemma    |
| Quality at training length| Slightly lower than RoPE        | Higher                          |
| KV cache compatibility    |  Bias added at query time      |  Rotation baked into Q, K     |

Because the bias is added at query time, ALiBi is KV-cache-friendly — the cached keys and values carry no positional modification.

### Why RoPE won

1. **Quality at training length**: RoPE matches or beats ALiBi when both are trained and evaluated at the same length, and most production use cases don't need extrapolation beyond the training length.
2. **Long-range attention**: RoPE doesn't penalize long-range attention — the model can learn to attend to far-away tokens when needed. ALiBi's linear penalty biases toward locality.
3. **YaRN solved extrapolation**: RoPE + YaRN extends 4-32× without retraining, which is usually sufficient, making ALiBi's native extrapolation less critical.
4. **Ecosystem**: Llama, Mistral, and Qwen all use RoPE — the open-source ecosystem converged on it.

### When ALiBi is still useful

- **Guaranteed extrapolation**: if you absolutely must train on 1024 and test on 10M, ALiBi is safer than RoPE+YaRN.
- **Simplicity**: ALiBi is simpler to implement and reason about (no frequency math, no YaRN tuning).
- **Streaming**: for streaming applications where context grows unboundedly, ALiBi's locality prior is natural.

## Why ALiBi didn't win

Despite the extrapolation advantage, ALiBi is less common than RoPE in modern LLMs, for three reasons. First, **slightly lower quality** at the training length: RoPE matches or beats ALiBi on most benchmarks when both are trained and evaluated at the same length. Second, **the locality prior is sometimes wrong**: for tasks requiring long-range attention (e.g., long-document Q&A), the linear penalty can be too aggressive. Third, **RoPE + YaRN/NTK scaling solves the extrapolation problem well enough**: with YaRN, RoPE models can extend 4–32× without retraining, which is usually sufficient. ALiBi is used in BLOOM, MPT, and a few other models, but RoPE dominates the open-source ecosystem.

## Implementation

The bias tensor itself is a few lines:

```python
def alibi_bias(seq_len, n_heads, device):
    """Returns the ALiBi bias tensor of shape (1, n_heads, seq_len, seq_len)."""
    # Head slopes: 1/2, 1/4, 1/8, ...
    slopes = 1.0 / (2 ** torch.arange(1, n_heads + 1, device=device).float())
    # Relative distances: (seq_len, seq_len), entry (i,j) = j - i
    positions = torch.arange(seq_len, device=device)
    relative_dist = positions[None, :] - positions[:, None]  # (seq_len, seq_len)
    # Bias: (n_heads, seq_len, seq_len)
    bias = -slopes[:, None, None] * relative_dist[None, :, :].float()
    return bias

# Use: add bias to attention scores before softmax
scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
scores = scores + alibi_bias(seq_len, n_heads, device)
attn = F.softmax(scores, dim=-1)
```

A complete attention module with ALiBi looks like this:

```python
import torch
import torch.nn.functional as F
import math

class ALiBiAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.W_q = torch.nn.Linear(d_model, d_model, bias=False)
        self.W_k = torch.nn.Linear(d_model, d_model, bias=False)
        self.W_v = torch.nn.Linear(d_model, d_model, bias=False)
        # ALiBi slopes: 1/2, 1/4, 1/8, ... (geometric)
        self.slopes = 1.0 / (2 ** torch.arange(1, n_heads + 1).float())

    def forward(self, x, mask=None):
        B, N, D = x.shape
        H, dk = self.n_heads, self.d_k

        Q = self.W_q(x).view(B, N, H, dk).transpose(1, 2)  # (B, H, N, dk)
        K = self.W_k(x).view(B, N, H, dk).transpose(1, 2)
        V = self.W_v(x).view(B, N, H, dk).transpose(1, 2)

        # Attention scores
        scores = Q @ K.transpose(-2, -1) / math.sqrt(dk)  # (B, H, N, N)

        # ALiBi bias: (H, N, N)
        positions = torch.arange(N, device=x.device)
        relative_dist = positions[None, :] - positions[:, None]  # (N, N)
        # Bias is negative for far-away tokens (penalize attention)
        alibi_bias = -self.slopes[:, None, None].to(x.device) * relative_dist[None, :, :].float()
        scores = scores + alibi_bias  # broadcast (H, N, N) over batch

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attn = F.softmax(scores, dim=-1)
        return (attn @ V).transpose(1, 2).reshape(B, N, D)

# Test extrapolation: train on 512, test on 2048
model = ALiBiAttention(d_model=512, n_heads=8)
# Train on sequences of length 512
# Test on sequences of length 2048 — ALiBi handles this natively
# (RoPE would need YaRN extension for this)
```

## Common pitfalls and failure modes

The classic mistakes: **applying ALiBi to value vectors** — it is a bias on attention scores, not values; **wrong slope direction** — the bias should be negative for far-away tokens (penalize attention), not positive; **mixing ALiBi with RoPE** — pick one, combining breaks the math; and **forgetting that slopes are head-specific** — using the same slope for all heads removes the multi-scale property.

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| ALiBi model doesn't attend to far-away tokens | Locality prior too strong | Use more heads with small slopes; or switch to RoPE |
| ALiBi + RoPE combined | Don't combine — breaks the math | Pick one positional encoding scheme |
| Wrong slope direction | Bias should be negative (penalize far) | Check sign: `bias = -slope * distance` |
| Same slope for all heads | Loses multi-scale property | Use geometric slopes: 1/2, 1/4, 1/8, ... |
| ALiBi not extrapolating | Implementation bug | Verify bias is added to scores, not values; check slope computation |

## Why this matters for AI

ALiBi is a **conceptually clean** positional encoding — no learned parameters, pure relative bias. It demonstrates that **extrapolation is achievable**, which matters for the long-context research direction. The geometric spacing of slopes (different heads at different distance scales) is an idea that appears in other contexts (e.g., multi-scale attention). And for applications where **training-time length must equal inference-time length**, ALiBi is a reasonable choice.

## Production implications

Most open-source models use RoPE, not ALiBi — stick with RoPE unless you have a specific reason. If you're training from scratch and want guaranteed extrapolation, ALiBi is a valid choice. ALiBi doesn't need any configuration at inference time (no `rope_theta` to set), which is simpler operationally. For very long contexts (1M+), ALiBi's linear penalty might be too aggressive — RoPE + YaRN is more flexible.

## Interview questions

1. **How does ALiBi encode positional information?** ALiBi adds a fixed linear bias to attention scores based on relative distance: $e_{ij} = q_i \cdot k_j + m \cdot (j - i)$, where $m$ is a head-specific slope (geometric: 1/2, 1/4, 1/8, ...). No learned positional parameters — just a fixed bias. The bias is negative for far-away tokens, penalizing attention to distant positions. This gives a locality prior: tokens prefer to attend to nearby tokens.

2. **Why does ALiBi extrapolate better than RoPE?** ALiBi has no learned positional parameters — the bias is a fixed function of relative distance, well-defined for any distance. RoPE has no learned parameters either, but its rotation frequencies are fitted to the training context; beyond that, the rotations are out of distribution. ALiBi's bias is always in distribution because it's just $m \cdot (j - i)$ — a simple linear function. RoPE needs YaRN/NTK scaling for extrapolation; ALiBi doesn't.

3. **Why did RoPE win over ALiBi despite ALiBi's extrapolation advantage?** Four reasons. (1) RoPE has higher quality at training length — most production use doesn't need extrapolation. (2) RoPE doesn't penalize long-range attention — the model can learn to attend to far-away tokens when needed; ALiBi's linear penalty biases toward locality, which hurts long-range reasoning. (3) YaRN solved RoPE's extrapolation — extends 4-32× without retraining, usually sufficient. (4) Ecosystem convergence: Llama, Mistral, Qwen all use RoPE.

4. **What is ALiBi's multi-scale head design, and why geometric slopes?** Different heads have different slopes: 1/2, 1/4, 1/8, ..., 1/2^H. This gives multi-scale attention — head 1 (slope 1/2) attends very locally; head H (slope 1/2^H) attends almost globally. Geometric spacing covers a wide range efficiently (logarithmic coverage). With 8 heads, slopes 1/2 to 1/256 cover 8 octaves — from "attend to previous token" to "attend globally". Linear spacing would waste capacity on similar scales.

5. **When would you choose ALiBi over RoPE?** Three cases. (1) Guaranteed extrapolation: if you must train on 1024 and test on 10M, ALiBi is safer than RoPE+YaRN. (2) Simplicity: ALiBi is simpler to implement (no frequency math, no YaRN tuning). (3) Streaming: for streaming applications where context grows unboundedly, ALiBi's locality prior is natural. For most production use cases (fixed or moderately extended context), RoPE is the better choice.

6. **Can you combine ALiBi with RoPE?** No — don't combine them. ALiBi adds a bias to attention scores; RoPE rotates Q and K. Combining gives two positional signals that can conflict. Pick one. If you need both extrapolation (ALiBi's strength) and long-range attention (RoPE's strength), use RoPE + YaRN — it gives extrapolation without the locality penalty. ALiBi + RoPE is an implementation bug, not a design choice.

## Further reading

- Press, Smith, Lewis (2022), *Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation* (ALiBi).
- Ofir Press's blog posts on ALiBi.

## See also

- [[Attention and Transformers MOC]]
- [[Positional Encoding]]
- [[RoPE]]
- [[YaRN and NTK-Aware Scaling]]
- [[Sinusoidal and Learned Positional Encodings]]
- [[Sliding Window Attention]] — another locality-based approach
- [[Scaled Dot-Product Attention]]
- [[Multi-Head Attention]]
