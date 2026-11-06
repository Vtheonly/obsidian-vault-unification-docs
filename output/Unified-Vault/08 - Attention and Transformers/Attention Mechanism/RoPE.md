---
title: RoPE
type: concept
aliases:
  - RoPE
  - Rotary Position Embedding
  - Rotary embeddings
tags:
  - attention
  - positional-encoding
  - rope
  - rotation
  - long-context
  - transformers
sources:
  - "RoPE (Rotary Position Embedding)"
created_index: 8
---

RoPE (rotary position embedding) gives attention its sense of position by rotating query and key vectors rather than adding a positional signal to the input embedding. Each two-dimensional subspace of a head rotates by an angle proportional to its token's position, with the consequence that the query–key dot product depends only on the relative offset between two tokens. RoPE is therefore a relative positional encoding that requires no extra parameters and adds no compute to attention itself, and it is the dominant positional scheme in modern decoder LLMs — Llama, Mistral, Gemma, Qwen, DeepSeek, and GLM all use it. This note develops the rotation mathematics, the `rotate_half` implementations used in practice, the frequency-base knob `rope_theta`, and the scaling tricks that extend RoPE past its training length.

> [!info] TL;DR
> RoPE rotates each query and key vector in 2D subspaces by an angle proportional to its position. The dot product $Q \cdot K$ then depends only on the **relative** position of the two tokens — making RoPE a relative positional encoding that requires no extra parameters and adds no compute to attention itself. The dominant positional encoding in modern LLMs (Llama, Mistral, Gemma, Qwen, DeepSeek, GLM).

## The core idea

For a 2D query $\mathbf{q} = (q_0, q_1)$ at position $i$, RoPE applies a rotation:

$$
R_i \mathbf{q} = \begin{pmatrix} \cos i\theta & -\sin i\theta \\ \sin i\theta & \cos i\theta \end{pmatrix} \begin{pmatrix} q_0 \\ q_1 \end{pmatrix}
$$

For a $d$-dimensional vector, pair up the dimensions and apply a different rotation frequency $\theta_k$ to each pair:

$$
\theta_k = 10000^{-2k/d}, \quad k = 0, 1, \ldots, d/2 - 1
$$

Each pair of dimensions rotates at a different frequency — the first pair rotates fast (capturing local position), the last pair rotates slowly (capturing long-range position).

## Why it works: the dot-product property

The key insight: if we rotate $\mathbf{q}_i$ by $i\theta$ and $\mathbf{k}_j$ by $j\theta$, their dot product is:

$$
(R_i \mathbf{q}) \cdot (R_j \mathbf{k}) = \mathbf{q} \cdot R_{j-i} \mathbf{k}
$$

— the dot product depends only on the **relative position** $j - i$, not on the absolute positions. This is the mathematical heart of RoPE: attention scores become shift-invariant, so what the model learns about a pair of tokens depends on how far apart they are, never on where they sit in the sequence.

### Derivation for one 2D pair

Let $\mathbf{q} = (q_0, q_1)$ and $\mathbf{k} = (k_0, k_1)$. In complex form, let $q = q_0 + i q_1$, $k = k_0 + i k_1$.

RoPE at position $m$ multiplies by $e^{im\theta}$:

$$
q_m = q \cdot e^{im\theta}, \quad k_m = k \cdot e^{im\theta}
$$

The dot product $\text{Re}(\bar{q}_m k_n)$ (real part of conjugate product) is:

$$
\text{Re}\left(\overline{q e^{im\theta}} \cdot k e^{in\theta}\right) = \text{Re}\left(\bar{q} k \cdot e^{i(n-m)\theta}\right)
$$

— depends only on $n - m$, the relative position. ∎

## The complex-number formulation

RoPE also has an elegant complex-number reading, and it is the one worth internalizing. View each 2D pair $(q_0, q_1)$ as a complex number $q = q_0 + i q_1$. Rotating by angle $\theta$ is multiplication by $e^{i\theta} = \cos\theta + i\sin\theta$. For position $m$, rotate by $m\theta$. The dot product $\bar{q}_m k_n$ (conjugate of $q$ at position $m$ times $k$ at position $n$) has real part $\text{Re}(\bar{q} k e^{i(n-m)\theta})$ — depends only on $n - m$, the relative position. The conjugate absorbs one rotation and cancels the other, which is exactly why the absolute positions drop out.

## Implementation

A standard implementation precomputes the cos/sin tables once and applies them element-wise:

```python
import torch

def precompute_rope(dim, max_seq_len, base=10000.0):
    """Precompute the cos/sin tables for RoPE."""
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(max_seq_len).float()
    freqs = torch.outer(t, inv_freq)  # (max_seq_len, dim/2)
    # Repeat to match dim
    emb = torch.cat([freqs, freqs], dim=-1)  # (max_seq_len, dim)
    return emb.cos(), emb.sin()

def rotate_half(x):
    """Rotate the second half of x to the first half: [-x2, x1] for each pair."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat([-x2, x1], dim=-1)

def apply_rope(q, cos, sin):
    """
    q: (batch, n_heads, seq_len, head_dim)
    cos, sin: (seq_len, head_dim)
    """
    # Broadcast cos/sin to q's shape
    cos = cos.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, head_dim)
    sin = sin.unsqueeze(0).unsqueeze(0)
    return q * cos + rotate_half(q) * sin
```

In real implementations (e.g., HuggingFace Llama), the rotation is applied in 2D subspaces via `reshape` rather than `rotate_half`, but the math is identical.

### The rotate_half trick

The heart of the implementation is `rotate_half`, which turns a complex rotation into real arithmetic:

```python
def rotate_half(x):
    """Rotates the second half to the first: [-x2, x1] for each pair."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat([-x2, x1], dim=-1)

def apply_rope(q, cos, sin):
    return q * cos + rotate_half(q) * sin
```

`rotate_half(x)` splits $x$ into $[x_1, x_2]$ and returns $[-x_2, x_1]$; then `apply_rope(q, cos, sin) = q * cos + rotate_half(q) * sin`. This is mathematically equivalent to the complex-number rotation but uses real arithmetic (faster on GPUs). Different implementations pair dimensions differently — adjacent pairs `[0,1], [2,3]` vs interleaved `[0,d/2], [1,d/2+1]` — match the model's convention or quality degrades.

### A complete module

```python
import torch
import torch.nn as nn
import math

class RoPE(nn.Module):
    def __init__(self, head_dim, max_seq_len, base=10000.0):
        super().__init__()
        inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2).float() / head_dim))
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer('cos', emb.cos())
        self.register_buffer('sin', emb.sin())

    def forward(self, q, k):
        seq_len = q.shape[2]
        cos = self.cos[:seq_len].unsqueeze(0).unsqueeze(0)
        sin = self.sin[:seq_len].unsqueeze(0).unsqueeze(0)
        q_rot = self._apply(q, cos, sin)
        k_rot = self._apply(k, cos, sin)
        return q_rot, k_rot

    def _apply(self, x, cos, sin):
        d = x.shape[-1]
        x1 = x[..., :d//2]
        x2 = x[..., d//2:]
        rotated = torch.cat([-x2, x1], dim=-1)
        return x * cos + rotated * sin
```

The module rotates both Q and K with the same tables and hands the rotated pair to [[Scaled Dot-Product Attention]].

## Frequency bands and rope_theta

The frequencies $\theta_k = 10000^{-2k/d}$ span a huge range. For $d = 128$ (typical head dim in Llama 70B): $\theta_0 = 1$ (one full rotation per token), $\theta_{63} \approx 0.0001$ (one full rotation every ~10000 tokens). This means:

- **Low-index dimensions** (high frequency) capture fine-grained local position.
- **High-index dimensions** (low frequency) capture coarse long-range position.

Different heads/layers naturally use different frequency bands for different purposes. The result is a multi-scale positional encoding: high frequencies (small $k$) capture fine local position; low frequencies (large $k$) capture coarse long-range position. The `rope_theta` (base, default 10000) determines rotation rates through $\theta_k = \text{base}^{-2k/d}$:

| Model         | rope_theta | Training context | Notes                                  |
|---------------|------------|------------------|----------------------------------------|
| Llama 2       | 10,000     | 4K               | Original base                          |
| Llama 3       | 500,000    | 8K → 128K        | Higher base for long context           |
| Qwen 2.5      | 1,000,000  | 32K → 128K       | Very high base for long context        |
| DeepSeek-V3   | 10,000     | 4K → 128K        | Standard + YaRN for extension          |

Higher base → slower rotations → positions distinguishable over longer ranges, but fine local distinctions are lost. Always pass the model's `rope_theta` — wrong value causes silent quality degradation.

## Why RoPE won

Compared to alternatives:

| Property                       | Sinusoidal | Learned Absolute | Shaw Relative | Transformer-XL | **RoPE**            |
|--------------------------------|------------|------------------|---------------|----------------|---------------------|
| Relative                       | No         | No               | Yes           | Yes            | **Yes**             |
| No extra params                | Yes        | No               | No            | No             | **Yes**             |
| No extra attention compute     | Yes        | Yes              | No            | No             | **Yes**             |
| Extrapolates                   | Theoretically | No            | To a limit    | To a limit     | **With scaling**    |
| Simple to implement            | Yes        | Yes              | Medium        | No             | **Yes**             |

RoPE hits the sweet spot: relative encoding, no extra params, no extra compute, simple to implement, and extensible with scaling tricks. ALiBi has native extrapolation but penalizes long-range attention; learned embeddings can't extrapolate at all. RoPE + YaRN is the best of all worlds.

## Context extension: the base trick

The original RoPE has a fixed frequency base (10000). For positions beyond the training length, the rotations "wrap around" — positions $i$ and $i + 2\pi/\theta_k$ become indistinguishable for frequency $k$. This causes the well-known context-length cliff.

The **scaling trick**: increase the base (e.g., 10000 → 500000) to slow the rotations and "interpolate" to longer positions. This is the basis of three families of methods:

- **NTK-aware scaling** — scales frequencies so the high-frequency rotations stay roughly the same and the low frequencies are stretched.
- **YaRN** — segments the frequency range and applies different scaling per segment; see [[YaRN and NTK-Aware Scaling]].
- **LongRoPE** — searches for non-uniform per-frequency scaling, achieving 2M-token context.

Llama 3 uses a RoPE base of 500000 to support 8k → 128k context. This is set at training time and baked into the model.

## Worked example: rotations by hand

For $d = 4$ (two pairs), base = 10000, position 3, the two pairs rotate by very different amounts: $\theta_0 = 10000^0 = 1$ gives a rotation by $3 \cdot 1 = 3$ radians, while $\theta_1 = 10000^{-2/4} = 10000^{-0.5} \approx 0.01$ gives a rotation by only $3 \cdot 0.01 = 0.03$ radians. For position 100 the contrast is starker: pair 0 rotates by 100 radians (wraps many times — high-frequency) while pair 1 rotates by 1 radian (slow).

## Why RoPE does not apply to V

RoPE only rotates Q and K, not V. The dot-product property $(R_i q) \cdot (R_j k) = q \cdot R_{j-i} k$ depends on both vectors being rotated by the *same* frequency. V isn't part of the dot product — it's what gets aggregated after the softmax. Rotating V wouldn't add positional information; it would just rotate the output, which the next layer would have to unrotate. So RoPE on V is pointless.

## Why this matters

RoPE is the **dominant positional encoding** in modern decoder LLMs. Every model you use — Llama, Mistral, Gemma, Qwen, DeepSeek, GLM — uses RoPE. Understanding it is essential for four everyday tasks: reading model cards and configs (the `rope_theta` parameter); extending context length (YaRN, NTK, LongRoPE); debugging "model gets confused at long context" issues, which are often a RoPE config problem; and implementing long-context inference efficiently.

## Production implications

Always pass the correct `rope_theta` when loading a model — a wrong value causes silent quality degradation. For context extension, use YaRN or NTK-aware scaling; both are supported in vLLM, TGI, and HuggingFace. Position IDs matter: RoPE depends on the position IDs you pass, so for padded batches ensure position IDs skip padding (most tokenizers handle this). And when you change a RoPE config, run long-context quality testing on near-max-length sequences — the model may look fine at 4k tokens but break at 32k.

## Common pitfalls and failure modes

The most common RoPE bug is a wrong base frequency — always check the model card. The other recurring mistakes: applying RoPE to V, which the dot-product property doesn't support; forgetting to scale during context extension, where naive scaling without YaRN/NTK degrades quality sharply; using the wrong rotation pairing, since different implementations pair dimensions differently (adjacent pairs `[0,1], [2,3]` vs interleaved `[0,d/2], [1,d/2+1]`) and you must match the model's expected convention; and off-by-one position IDs, where position 0 vs position 1 can matter and you must match the model's training convention.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Wrong `rope_theta` | Mismatched with model card | Always pass the model's `rope_theta` |
| Applying RoPE to V | Misunderstanding | RoPE only rotates Q and K, not V |
| Wrong rotation pairing | Adjacent vs interleaved pairs | Match the model's convention |
| Quality degrades at long context | RoPE extrapolation failure | Use YaRN or NTK-aware scaling |
| Off-by-one in position IDs | Position 0 vs 1 | Match the model's training convention |

## Interview questions

1. **Q: Explain the complex number formulation of RoPE.**
   A: View each 2D pair $(q_0, q_1)$ as a complex number $q = q_0 + i q_1$. Rotating by $\theta$ is multiplication by $e^{i\theta}$. For position $m$, rotate by $m\theta$. The dot product $\bar{q}_m k_n$ has real part $\text{Re}(\bar{q} k e^{i(n-m)\theta})$ — depends only on $n-m$, the relative position. This is the mathematical heart of RoPE: relative encoding via complex rotation.

2. **Q: Why doesn't RoPE apply to V?**
   A: The dot-product property depends on both vectors being rotated by the same frequency. V isn't part of the dot product — it's what gets aggregated after the softmax. Rotating V wouldn't add positional information; it would just rotate the output, which the next layer would have to unrotate. So RoPE on V is pointless.

3. **Q: What is `rope_theta` and how does it affect context length?**
   A: `rope_theta` (base frequency, default 10000) determines rotation rates: $\theta_k = \text{base}^{-2k/d}$. Higher base → slower rotations → positions distinguishable over longer ranges, but fine local distinctions are lost. Llama 2 uses 10000 (4K context); Llama 3 uses 500000 (128K context); Qwen 2.5 uses 1000000 (128K context). Always pass the model's `rope_theta` — wrong value causes silent quality degradation.

4. **Q: Why did RoPE win over ALiBi and learned positional embeddings?**
   A: Four reasons. (1) Relative encoding with no parameters. (2) No extra compute (cheap element-wise rotation). (3) Quality at training length matches or beats alternatives. (4) Extensible — YaRN/NTK scaling extends to longer contexts without retraining. ALiBi has native extrapolation but penalizes long-range attention; learned embeddings can't extrapolate at all. RoPE + YaRN is the best of all worlds.

5. **Q: How does the `rotate_half` implementation work?**
   A: `rotate_half(x)` splits x into $[x_1, x_2]$ and returns $[-x_2, x_1]$. Then `apply_rope(q, cos, sin) = q * cos + rotate_half(q) * sin`. This is mathematically equivalent to the 2D rotation matrix applied to each pair, but uses real arithmetic (faster on GPUs than complex). Different implementations pair dimensions differently — match the model's convention or quality degrades.

6. **Q: How would you extend a RoPE-trained model to longer context?**
   A: Three approaches: (1) **YaRN** — set `rope_scaling={"type":"yarn","factor":N}`. Zero-shot for 4×; needs fine-tuning for 8-16×. (2) **NTK-aware scaling** — increase `rope_theta` by a factor. Simpler but less precise. (3) **LongRoPE** — search for non-uniform per-frequency scaling. Achieves 2M-token context but requires significant fine-tuning. Always test on near-max-length sequences.

## Further reading

- Su et al. (2021), *RoFormer: Enhanced Transformer with Rotary Position Embedding*.
- Blog: EleutherAI's "Rotary Embeddings: A Relative Revolution".
- Peng et al. (2023), *YaRN*.
- Llama 2/3 technical reports — RoPE base choices.

## See also

- [[Attention and Transformers MOC]]
- [[Positional Encoding]] — the broader family of approaches
- [[Sinusoidal and Learned Positional Encodings]] — the absolute schemes RoPE displaced
- [[ALiBi]] — the alternative with native extrapolation
- [[YaRN and NTK-Aware Scaling]] — extending RoPE past its training length
- [[Self-Attention]] — where the rotated Q and K live
- [[Multi-Head Attention]] — per-head rotation tables
- [[Queries Keys and Values]] — why the rotation targets Q and K
- [[Transformer Block]] — where RoPE sits in the architecture
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — efficient kernels for long-context inference
