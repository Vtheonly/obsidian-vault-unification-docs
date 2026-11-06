---
title: Luong Attention
type: concept
aliases:
  - "Luong Attention"
  - "Multiplicative Attention"
tags:
  - attention
  - luong
  - multiplicative-attention
  - seq2seq
  - alignment
sources:
  - "Luong Attention"
created_index: 3
---

Luong et al. (2015) simplified Bahdanau's additive attention into **multiplicative** (dot-product) attention — the form the Transformer uses today. The paper proposed four alignment score functions, a distinctive combine step that fuses the context with the decoder state, and the global-versus-local attention distinction whose local mode is the ancestor of modern sliding-window attention. This note works through the mechanism, the arithmetic, a PyTorch implementation, and the hardware argument for why multiplicative attention won.

> [!info] TL;DR
> Luong et al. (2015) simplified Bahdanau's additive attention into **multiplicative** (dot-product) attention. This is the form the Transformer uses today. Luong also introduced global vs local attention.

## Setup

The setup is the same as Bahdanau's: the source sequence is encoded into hidden states $\mathbf{h}_1^{enc}, \ldots, \mathbf{h}_{T_x}^{enc}$, and the decoder hidden state at step $t$ is $\mathbf{h}_t^{dec}$.

The key difference from Bahdanau: Luong uses the **current** decoder state $\mathbf{h}_t^{dec}$ (after computing it), not the previous one $\mathbf{h}_{t-1}^{dec}$.

## Alignment functions

Luong proposed several alignment functions, all simpler than Bahdanau's MLP.

### Dot product

$$
e_{ti} = \mathbf{h}_t^{dec} \cdot \mathbf{h}_i^{enc}
$$

This requires the encoder and decoder to have the same hidden dimension.

### General

$$
e_{ti} = \mathbf{h}_t^{dec} \, \mathbf{W}_a \, \mathbf{h}_i^{enc}
$$

This allows different dimensions; $\mathbf{W}_a$ is learned.

### Concat (a.k.a. "Bahdanau-style")

$$
e_{ti} = \mathbf{v}_a^T \tanh(\mathbf{W}_a [\mathbf{h}_t^{dec}; \mathbf{h}_i^{enc}])
$$

The same form as Bahdanau, but using $\mathbf{h}_t^{dec}$ instead of $\mathbf{h}_{t-1}^{dec}$.

### Location-aware

$$
e_{ti} = \mathbf{v}_a^T \tanh(\mathbf{W}_a [\mathbf{h}_t^{dec}; \mathbf{h}_i^{enc}] + \mathbf{U}_a \boldsymbol{\alpha}_{t-1, i})
$$

This adds the previous attention weights as input — useful for monotonic tasks like ASR.

The **dot** and **general** forms are by far the most used. The Transformer uses the dot product (with scaling — see [[Self-Attention]] and [[Scaled Dot-Product Attention]]).

## The mechanism

The Luong computation proceeds in six steps:

1. Compute the decoder state $\mathbf{h}_t^{dec}$ normally.
2. Compute alignment scores $e_{ti} = a(\mathbf{h}_t^{dec}, \mathbf{h}_i^{enc})$.
3. Softmax: $\alpha_{ti} = \text{softmax}(e_{ti})$.
4. Context: $\mathbf{c}_t = \sum_i \alpha_{ti} \mathbf{h}_i^{enc}$.
5. **Combine** the context with the decoder state: $\tilde{\mathbf{h}}_t = \tanh(\mathbf{W}_c [\mathbf{h}_t^{dec}; \mathbf{c}_t])$.
6. Use $\tilde{\mathbf{h}}_t$ for the output (softmax over vocabulary).

The combine step (5) is a Luong-specific detail. Bahdanau instead fed $\mathbf{c}_t$ into the RNN.

## The combine step: Luong's distinctive feature

Luong's distinctive contribution (beyond the alignment function) is the **combine step**:

$$
\tilde{\mathbf{h}}_t = \tanh(\mathbf{W}_c [\mathbf{h}_t^{dec}; \mathbf{c}_t])
$$

The decoder state $\mathbf{h}_t^{dec}$ and the context $\mathbf{c}_t$ are concatenated and projected through a linear layer with $\tanh$. This combined vector $\tilde{\mathbf{h}}_t$ is then used for the output (softmax over vocabulary).

Bahdanau's approach is different: the context $\mathbf{c}_t$ is fed into the RNN as input, so the decoder state already incorporates the context. Luong's combine step is a post-hoc fusion — the decoder state is computed normally, then combined with the context for the output. The combine step gives the model explicit control over how to use the context: the $\tanh$ non-linearity lets it selectively emphasize or suppress the context. In practice, the combine step gives a small quality improvement over Bahdanau's approach.

## Global versus local attention

Luong introduced two attention modes.

### Global

Attend over **all** source positions. This is the same as Bahdanau, and is best for tasks where any source word might be relevant at any time (e.g., general MT).

### Local

Attend only to a **window** around a predicted alignment position $p_t$:

$$
\alpha_{ti} = \text{softmax}(e_{ti}) \cdot \text{gauss}(i; p_t, \sigma)
$$

where $p_t$ is predicted from the decoder state (either monotonic — $p_t = t$ — or "predictive" — learned) and $\sigma$ is a window width. Local attention is cheaper (only a small window is scored) and works well for monotonic tasks like ASR and speech synthesis. It is the precursor of modern **sliding-window attention** used in Mistral and others.

## Why multiplicative attention won

Multiplicative attention has several advantages over additive. It has **fewer parameters** — no MLP, just a dot product (or a single matrix $\mathbf{W}_a$). It is **faster** — dot products map directly to matrix multiplications, which GPUs are heavily optimized for. It is **better empirically** — at scale, multiplicative matches or beats additive. And it is **simpler** — easier to implement, debug, and reason about. The Transformer (Vaswani et al., 2017) chose multiplicative attention, and that is the form every modern LLM uses.

## Why multiplicative is faster than additive

Multiplicative attention ($\mathbf{q} \cdot \mathbf{k}$) maps directly to a matrix multiplication: $Q K^T$. GPUs are heavily optimized for matmuls (cuBLAS achieves >50% of peak FLOP/s). Additive attention (an MLP) requires separate projections per (query, key) pair, which doesn't fuse into a single matmul efficiently.

For a sequence of length $N$ with hidden dim $d$: the **multiplicative** path computes $Q K^T$ as one matmul of shape $(N, d) \times (d, N) = (N, N)$, costing $O(N^2 d)$ FLOPs, all in matmul. The **additive** path, for each $(i, j)$ pair, computes $\mathbf{W}_a \mathbf{q}_i + \mathbf{U}_a \mathbf{k}_j + \tanh + \mathbf{v}^T$ — effectively $N^2$ separate MLP calls, with the same $O(N^2 d)$ FLOPs but poor hardware utilization.

In practice, multiplicative is 2-5× faster on GPUs. This is also why FlashAttention (which fuses the entire attention computation into a single tiled kernel) requires multiplicative attention — additive would be much harder to fuse.

## The four alignment variants side by side

| Variant          | Formula                                          | Parameters                  | Notes                                          |
|------------------|--------------------------------------------------|-----------------------------|------------------------------------------------|
| Dot              | $\mathbf{h}_{dec} \cdot \mathbf{h}_{enc}$          | 0                           | Requires enc_dim == dec_dim                    |
| General          | $\mathbf{h}_{dec} \mathbf{W}_a \mathbf{h}_{enc}$   | $d_{dec} \times d_{enc}$    | Allows different dims                          |
| Concat           | $\mathbf{v}^T \tanh(\mathbf{W}_a [\mathbf{h}_{dec}; \mathbf{h}_{enc}])$ | $\mathbf{W}_a, \mathbf{v}$ | Same as Bahdanau but uses current $\mathbf{h}_{dec}$ |
| Location-aware   | $\mathbf{v}^T \tanh(\mathbf{W}_a [\mathbf{h}_{dec}; \mathbf{h}_{enc}] + \mathbf{U}_a \alpha_{t-1})$ | More | Adds previous attention as input — for monotonic tasks |

The **dot** and **general** variants are by far the most used; the Transformer uses the dot product (with scaling). The **location-aware** variant is important for ASR (where alignment is monotonic — the decoder position roughly tracks the encoder position) and is the conceptual ancestor of modern sliding-window attention.

## A worked example

Suppose $\mathbf{h}_t^{dec} = (1, 0)$, and the encoder states are $\mathbf{h}_1^{enc} = (1, 0)$, $\mathbf{h}_2^{enc} = (0, 1)$, $\mathbf{h}_3^{enc} = (1, 1)$.

Dot-product scores:

- $e_1 = 1 \cdot 1 + 0 \cdot 0 = 1$
- $e_2 = 1 \cdot 0 + 0 \cdot 1 = 0$
- $e_3 = 1 \cdot 1 + 0 \cdot 1 = 1$

Softmax: $\alpha \approx (0.42, 0.16, 0.42)$.

Context: $0.42 (1, 0) + 0.16 (0, 1) + 0.42 (1, 1) = (0.84, 0.58)$.

The decoder state has high alignment with both $\mathbf{h}_1$ and $\mathbf{h}_3$, and the context reflects that blend.

## Implementation

A minimal PyTorch sketch of the scoring and context computation:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class LuongAttention(nn.Module):
    def __init__(self, method, enc_dim, dec_dim):
        super().__init__()
        self.method = method
        if method == 'general':
            self.W_a = nn.Linear(dec_dim, enc_dim, bias=False)
        elif method == 'concat':
            self.W_a = nn.Linear(enc_dim + dec_dim, attn_dim, bias=False)
            self.v_a = nn.Linear(attn_dim, 1, bias=False)
        # 'dot' needs no parameters
    
    def score(self, h_dec, h_encs):
        # h_dec: (batch, dec_dim), h_encs: (batch, T, enc_dim)
        if self.method == 'dot':
            return torch.bmm(h_encs, h_dec.unsqueeze(-1)).squeeze(-1)
        elif self.method == 'general':
            return torch.bmm(h_encs, self.W_a(h_dec).unsqueeze(-1)).squeeze(-1)
        # ... 'concat' similar to Bahdanau
    
    def forward(self, h_dec, h_encs):
        scores = self.score(h_dec, h_encs)  # (batch, T)
        weights = F.softmax(scores, dim=-1)
        context = torch.bmm(weights.unsqueeze(1), h_encs).squeeze(1)  # (batch, enc_dim)
        return context, weights
```

The full version adds the concat branch, an optional mask, the combine step, and a smoke test:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class LuongAttention(nn.Module):
    def __init__(self, method, enc_dim, dec_dim, attn_dim=None):
        super().__init__()
        self.method = method
        if method == 'general':
            self.W_a = nn.Linear(dec_dim, enc_dim, bias=False)
        elif method == 'concat':
            self.W_a = nn.Linear(enc_dim + dec_dim, attn_dim, bias=False)
            self.v_a = nn.Linear(attn_dim, 1, bias=False)
        # 'dot' needs no parameters
        # Combine step
        self.W_c = nn.Linear(enc_dim + dec_dim, dec_dim)

    def score(self, h_dec, h_encs):
        # h_dec: (batch, dec_dim), h_encs: (batch, T, enc_dim)
        if self.method == 'dot':
            return torch.bmm(h_encs, h_dec.unsqueeze(-1)).squeeze(-1)  # (batch, T)
        elif self.method == 'general':
            return torch.bmm(h_encs, self.W_a(h_dec).unsqueeze(-1)).squeeze(-1)
        elif self.method == 'concat':
            # Same as Bahdanau but uses current h_dec
            batch, T, _ = h_encs.shape
            h_dec_expanded = h_dec.unsqueeze(1).expand(-1, T, -1)
            combined = torch.cat([h_dec_expanded, h_encs], dim=-1)  # (batch, T, dec+enc)
            return self.v_a(torch.tanh(self.W_a(combined))).squeeze(-1)

    def forward(self, h_dec, h_encs, mask=None):
        scores = self.score(h_dec, h_encs)  # (batch, T)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        weights = F.softmax(scores, dim=-1)
        context = torch.bmm(weights.unsqueeze(1), h_encs).squeeze(1)  # (batch, enc_dim)
        # Combine step (Luong's distinctive feature)
        combined = torch.tanh(self.W_c(torch.cat([h_dec, context], dim=-1)))
        return combined, weights

# Test
attn = LuongAttention('general', enc_dim=16, dec_dim=16)
h_dec = torch.randn(2, 16)
h_encs = torch.randn(2, 5, 16)
out, weights = attn(h_dec, h_encs)
print(f"Output: {out.shape}, Weights: {weights.shape}")  # (2, 16), (2, 5)
```

## Common pitfalls and failure modes

**Forgetting to scale** in dot-product attention — Luong's original paper didn't scale. The Transformer added scaling by $\sqrt{d_k}$ to prevent softmax saturation (the derivation is in [[Scaled Dot-Product Attention]]). **Mixing up global and local attention** — local attention can be much faster but only works when alignment is roughly monotonic. **Treating dot product as similarity without normalization** — for unnormalized vectors, the dot product confuses magnitude with alignment; use cosine similarity if you care about direction.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Dot product attention has poor quality | Encoder/decoder dims differ; or vectors not normalized | Use 'general' variant (adds a learned projection); or normalize vectors |
| Softmax saturates (one weight ~1.0, rest ~0) | Dot products too large (no scaling) | Scale by $\sqrt{d_k}$ (the Transformer trick) |
| Local attention misses long-range deps | Window too small; or wrong alignment position | Increase window; or use global attention for non-monotonic tasks |
| Combine step doesn't help | Context and decoder state carry redundant info | Skip the combine step; or use a smaller projection |

## Why this matters for AI

The Transformer's attention is **scaled multiplicative Luong attention**, applied self-referentially (Q, K, V all come from the same sequence). Every modern LLM uses some variant — MHA, GQA, MQA, MLA — and all are multiplicative. The dot-product form is what makes **FlashAttention** possible (it is a tiled matrix multiplication); additive attention would be much harder to fuse. And local attention is the ancestor of modern **sliding-window attention** (Mistral 7B, Gemma 2). The key idea — attend only to nearby positions for efficiency, with a few global tokens for long-range information — is the same; Luong's contribution was showing this works for sequence-to-sequence tasks, not just classification.

## Production implications

For modern models, you don't implement Luong attention directly — but the underlying pattern (Q × K → softmax → × V) is everywhere. The choice of attention variant (MHA, GQA, MQA) affects inference latency and memory; see [[GQA MQA and MLA]].

## Interview questions

1. **What are the four Luong alignment variants?** (1) **Dot**: $\mathbf{h}_{dec} \cdot \mathbf{h}_{enc}$ — no parameters, requires equal dims. (2) **General**: $\mathbf{h}_{dec} \mathbf{W}_a \mathbf{h}_{enc}$ — allows different dims, one learned matrix. (3) **Concat**: $\mathbf{v}^T \tanh(\mathbf{W}_a [\mathbf{h}_{dec}; \mathbf{h}_{enc}])$ — same as Bahdanau but uses the current decoder state. (4) **Location-aware**: adds previous attention weights as input — for monotonic tasks like ASR. The dot and general variants are most used; the Transformer uses dot product with scaling.

2. **Why is multiplicative attention faster than additive?** Multiplicative ($\mathbf{q} \cdot \mathbf{k}$) maps to a single matmul $Q K^T$, which GPUs are heavily optimized for (cuBLAS achieves >50% peak FLOP/s). Additive (MLP) requires $N^2$ separate MLP calls per (query, key) pair — same FLOPs but poor hardware utilization. In practice, multiplicative is 2-5× faster. This is why FlashAttention (a fused tiled kernel) requires multiplicative attention — additive would be much harder to fuse.

3. **What is Luong's combine step and why does it matter?** The combine step: $\tilde{\mathbf{h}}_t = \tanh(\mathbf{W}_c [\mathbf{h}_t^{dec}; \mathbf{c}_t])$. The decoder state and context are concatenated and projected through a linear + tanh. This gives the model explicit control over how to use the context — the tanh lets it selectively emphasize or suppress. Bahdanau's approach feeds the context into the RNN as input, so the decoder state already incorporates it; Luong's combine step is a post-hoc fusion. In practice, it gives a small quality improvement.

4. **How does Luong's local attention relate to modern sliding window attention?** Luong's local attention attends only to a window around a predicted alignment position $p_t$, with a Gaussian falloff. It's the direct ancestor of modern sliding-window attention (Mistral 7B, Gemma 2). The key idea — attend only to nearby positions for efficiency, with a few global tokens for long-range information — is the same. Luong showed this works for sequence-to-sequence tasks (ASR, where alignment is monotonic). Modern sliding-window attention generalizes it to causal language modeling.

5. **Why does the Transformer scale the dot product by $\sqrt{d_k}$?** For large $d_k$, dot products grow large (variance $\approx d_k$), pushing softmax into saturation (one weight ~1.0, rest ~0). Saturated softmax has vanishing gradients, so the model can't learn. Scaling by $\sqrt{d_k}$ keeps the variance at 1, preventing saturation. Luong's original paper didn't scale — at small dims (256-512), it's not needed. The Transformer introduced scaling because it used larger dims (64 per head, but with multi-head). Modern LLMs always scale.

6. **When would you use location-aware attention?** For monotonic tasks where the decoder position roughly tracks the encoder position — primarily ASR (speech recognition) and speech synthesis. In ASR, the decoder produces output frames in order, and the attention should move forward through the encoder (audio frames) without going backward or jumping. Location-aware attention uses the previous attention weights as input, penalizing attention that jumps backward. For non-monotonic tasks (translation, summarization), location-aware attention is too restrictive — use global attention instead.

## Further reading

- Luong, Pham, Manning (2015), *Effective Approaches to Attention-based Neural Machine Translation*.
- Vaswani et al. (2017), *Attention Is All You Need* — scaled dot-product attention.

## See also

- [[Attention and Transformers MOC]]
- [[Origins of Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- [[Self-Attention]]
- [[Multi-Head Attention]]
- [[Scaled Dot-Product Attention]]
- [[Queries Keys and Values]]
- [[Sliding Window Attention]]
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]
- [[GQA MQA and MLA]]
