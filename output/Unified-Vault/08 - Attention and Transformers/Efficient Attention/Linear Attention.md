---
title: Linear Attention
type: concept
aliases:
  - Linear Attention
  - Performer
  - Linformer
tags:
  - attention
  - efficient-attention
  - linear-attention
  - performer
  - linformer
  - kernel-trick
sources:
  - "13 - Linear Attention (Performer, Linformer)"
created_index: 16
---

Linear attention is the family of approximations that reduce attention's $O(n^2)$ cost to $O(n)$ or $O(n \cdot k)$ by replacing the softmax kernel with a decomposable feature map (Performer) or by low-rank projection along the sequence dimension (Linformer). In 2020 these were the most promising path to long context; after FlashAttention made exact attention cheap, they were largely superseded in practice. The core idea survives, though, as the conceptual ancestor of modern state space models like Mamba.

> [!info] TL;DR
> Linear attention approximates the $O(n^2)$ attention with $O(n)$ or $O(n \cdot k)$ compute by replacing the softmax kernel with a decomposable one or by low-rank projection. Performer (2020) and Linformer (2020) are the main variants. Largely superseded by FlashAttention in practice, but the ideas influence modern SSMs.

## The idea

Standard attention, in its inline form $\text{Attn}(Q, K, V) = \text{softmax}(QK^T / \sqrt{d}) V$:

$$
\text{Attn}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d}}\right) V
$$

The $Q K^T$ and the softmax-weighted $V$ multiplication are both $O(n^2 d)$. If we could **decompose** the softmax into a feature map $\phi$ such that $\text{softmax}(QK^T) \approx \phi(Q) \phi(K)^T$, we could rearrange:

$$
\text{softmax}(QK^T) V \approx \phi(Q) \big(\phi(K)^T V\big)
$$

Now $\phi(K)^T V$ is $d \times d$ — independent of $n$. Multiplying by $\phi(Q)$ gives $O(n \cdot d^2)$ — **linear in $n$**.

## The kernel trick in detail

Linear attention replaces softmax with a **decomposable kernel** $\phi$:

$$\text{Attn}(Q, K, V) = \phi(Q) (\phi(K)^T V)$$

Now $\phi(K)^T V$ is $d \times d$ — independent of $n$ — and multiplying by $\phi(Q)$ gives $O(n \cdot d^2)$, **linear in $n$** for $d \ll n$.

### The catch: approximation quality

The kernel $\phi$ must approximate the softmax kernel $\exp(q \cdot k)$. Performer uses random Fourier features (RFF):

$$\phi(x) = \frac{1}{\sqrt{m}} \exp\left(-\frac{\|x\|^2}{2}\right) [\exp(\omega_1 \cdot x), \ldots, \exp(\omega_m \cdot x)]$$

where $\omega_i$ are random Gaussian vectors. As $m \to \infty$, $\phi(Q)\phi(K)^T \to \exp(QK^T)$. But for finite $m$, there's approximation error, and the $m$ needed for good quality grows with $d$. For typical LLM dims ($d = 4096$) you need $m \approx 4096$, which means the linear attention is $O(n \cdot d^2) = O(n \cdot 16M)$ — not better than full attention $O(n^2 \cdot d) = O(n^2 \cdot 4096)$ until $n > 4000$. And FlashAttention's constants are smaller. This is why linear attention lost.

## Performer (Choromanski et al. 2020)

Performer uses **random Fourier features** (RFF) to approximate the softmax kernel:

$$
\phi(\mathbf{x}) = \frac{1}{\sqrt{m}} \exp\left(-\frac{\|\mathbf{x}\|^2}{2}\right) \left[\exp(\mathbf{\omega}_1 \cdot \mathbf{x}), \ldots, \exp(\mathbf{\omega}_m \cdot \mathbf{x})\right]
$$

where $\mathbf{\omega}_i$ are random Gaussian vectors. As $m \to \infty$, $\phi(Q) \phi(K)^T$ converges to the true softmax kernel.

Its strengths: $O(n \cdot m \cdot d)$ compute with $m$ the feature dimension, an unbiased approximation, and applicability to any softmax-based attention. Its weaknesses: approximation error means quality is slightly worse than full attention, the $m$ needed for good approximation grows with $d$, and in practice FlashAttention often beats Performer because the constants are smaller.

## Linformer (Wang et al. 2020)

Linformer takes a different approach: project $K$ and $V$ along the **sequence dimension** to a fixed low rank:

$$
\tilde{K} = E K \quad \text{where } E \in \mathbb{R}^{k \times n}
$$
$$
\tilde{V} = F V \quad \text{where } F \in \mathbb{R}^{k \times n}
$$

or, compactly, $\tilde{K} = E K, \quad \tilde{V} = F V$ where $E, F \in \mathbb{R}^{k \times n}$. Now $Q \tilde{K}^T$ is $n \times k$ instead of $n \times n$. For $k \ll n$, this is $O(n \cdot k \cdot d)$ — linear in $n$.

Linformer is simple and fast, and the projections $E, F$ can be learned or fixed (random). But it has two structural weaknesses. First, it **loses position-dependent structure**: the projections $E, F$ mix positions, so the model loses the ability to attend to specific positions — for tasks needing precise position information (e.g., "attend to the 5th token"), Linformer is worse than full attention, while for tasks where global patterns suffice (e.g., document classification), it is fine. Second, it is **not extrapolatable**: $k$ is fixed at training time, and at inference with $n > n_{\text{train}}$ the projection matrices $E, F$ are undefined. This is worse than RoPE (which extrapolates with YaRN) and limits Linformer's applicability.

## Why linear attention lost to FlashAttention

In 2020, linear attention was the most promising path to long context. By 2022, FlashAttention changed the calculus:

- FlashAttention is **exact** — no approximation, no quality loss.
- FlashAttention's constants are small — for typical $n$ (4k–128k), it's faster than linear attention.
- Linear attention requires choosing $m$ or $k$ — for high enough quality, you need $m, k \approx n$, defeating the purpose.

So linear attention is now mostly of **historical / theoretical interest**, though the ideas survive in modified forms.

## Linear attention's legacy: SSMs and Mamba

The "decompose the kernel, rearrange the multiplication" idea reappears in **state space models** (S4, Mamba). Mamba computes a linear-attention-like recurrence but with **selective** gating (input-dependent $B, C$ matrices), which fixes the quality issues that linear attention lacks the power to solve — linear attention without selectivity is too weak to match Transformer quality. The state-space formulation enables $O(n)$ training (parallel scan) and $O(1)$ inference per token (vs $O(n)$ for attention's KV cache). In short, Mamba is "linear attention + selectivity + hardware-efficient scan", which makes linear attention the conceptual ancestor of modern SSMs.

The idea also lives on in linear-attention-like modern architectures such as RWKV and RetNet, in hybrids with a linear-time component such as Jamba (2024), and in production use: MiniMax-01 (2025) is a hybrid combining linear attention with softmax attention.

## Worked example: conceptual Performer

```python
def performer_attention(Q, K, V, n_features=256):
    """Simplified Performer with random Fourier features."""
    d = Q.size(-1)
    omega = torch.randn(n_features, d) / math.sqrt(d)
    
    # Feature map
    def phi(x):
        # (B, n, d) → (B, n, m)
        return F.softmax(torch.exp(x @ omega.T / math.sqrt(d)) - 0.5 * (x ** 2).sum(-1, keepdim=True), dim=-1)
    
    phi_Q = phi(Q)
    phi_K = phi(K)
    
    # Linear attention: phi(Q) @ (phi(K)^T @ V)
    K_V = phi_K.transpose(-2, -1) @ V  # (B, m, d)
    return phi_Q @ K_V  # (B, n, d)
```

## Why it matters

Linear attention is the **conceptual bridge** between Transformers and SSMs — understanding it helps you understand why Mamba works. For **streaming applications** where $n$ grows indefinitely (online ASR, real-time transcription), linear attention's $O(n)$ is genuinely valuable, since full attention can't keep up. For most production use cases in 2026, though, **FlashAttention with full attention is the right choice**, and linear attention is niche.

## Production implications

Don't use Performer or Linformer in production — FlashAttention is better in almost all cases. Watch for **Mamba / hybrid models** if you need linear-time sequence modeling; they're the modern successors. For extreme long-context (>10M tokens), linear attention or hybrid attention may be necessary.

## Common pitfalls and failure modes

The main pitfalls: **treating linear attention as equivalent to full attention** (quality differences matter for some tasks); **forgetting that Linformer's projection breaks position info** (bad for tasks needing precise position); **using too small a feature dimension** (quality degrades silently); and **comparing FLOPs without measuring wall-clock** (linear attention's smaller FLOPs often don't translate to wall-clock wins because of constants).

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Quality worse than full attention | Approximation error in $\phi$; or $k$ too small | Increase $m$ (Performer) or $k$ (Linformer); or use full attention + FA |
| Position information lost | Linformer's projection mixes positions | Use Performer (preserves position); or use full attention |
| Can't extrapolate | Linformer's fixed $k$ | Use RoPE + YaRN for extrapolation |
| Slower than expected | Constants are large; FA is faster | Benchmark against FA; don't assume linear is faster |

## Interview questions

**How does linear attention reduce the $O(n^2)$ cost to $O(n)$?** Standard attention computes $\text{softmax}(QK^T)V$ — the softmax requires the full $n \times n$ matrix. Linear attention replaces softmax with a decomposable kernel $\phi$: $\text{Attn} = \phi(Q)(\phi(K)^T V)$. Now $\phi(K)^T V$ is $d \times d$ (independent of $n$), and multiplying by $\phi(Q)$ gives $O(n \cdot d^2)$ — linear in $n$ for $d \ll n$. The catch: the kernel $\phi$ must approximate softmax, and for good quality you need $m \approx d$, so the speedup only kicks in for $n > d^2 / d = d$. For typical LLM dims ($d = 4096$), that's $n > 4096$.

**Why did linear attention lose to FlashAttention?** Three reasons. (1) **Approximation error** — linear attention approximates softmax; quality is slightly worse. (2) **Constants matter** — for the $m$ needed for good quality, linear attention's $O(n \cdot m \cdot d)$ isn't faster than FA's $O(n^2 \cdot d)$ until $n > m$, which is often $n > 4096$. (3) **FA is exact** — no approximation, no quality loss. FA made full attention cheap enough that the linear approximation wasn't worth the quality loss. Linear attention survives in Mamba/SSMs (which add selectivity) and in MiniMax-01 (hybrid linear + softmax).

**How does linear attention relate to Mamba and state space models?** Mamba is the modern successor of linear attention. The key idea — decompose the kernel to avoid $n^2$ — is preserved. The difference: Mamba adds **selective gating** (input-dependent $B, C$ matrices), which linear attention lacks. This selectivity is what makes Mamba match Transformer quality — linear attention without selectivity is too weak. Mamba also uses a parallel scan for $O(n)$ training and $O(1)$ inference per token. Conceptually, Mamba is "linear attention + selectivity + hardware-efficient scan".

## Further reading

- Choromanski et al. (2020), *Rethinking Attention with Performers*.
- Wang et al. (2020), *Linformer: Self-Attention with Linear Complexity*.
- Katharopoulos et al. (2020), *Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention*.

## See also

- [[Attention and Transformers MOC]]
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — what replaced linear attention in practice.
- [[Sparse Attention]] — the other family of attention approximations.
- [[Sliding Window Attention]] — constant-cache alternative for long context.
- [[From RNNs to Attention]] — the recurrence view that linear attention reconnects to Transformers.
- [[RoPE]] and [[YaRN and NTK-Aware Scaling]] — the extrapolation route Linformer lacks.
- [[Scaled Dot-Product Attention]]
- [[Mamba]]
