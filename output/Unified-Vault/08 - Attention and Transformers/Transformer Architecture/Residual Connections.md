---
title: Residual Connections
type: concept
aliases: [Skip Connection, Residual Stream, Identity Shortcut]
tags: [transformer, architecture, residual, skip-connection, gradient-flow]
sources: ["Residual Connections"]
created_index: 30
---

A residual (skip) connection adds the input of a sublayer to its output, giving gradients a direct path backward and making deep stacks trainable — without them, Transformers beyond roughly 10 layers don't converge. Introduced with ResNet in computer vision, residuals also turn out to be the model's memory architecture: the channel through which every sublayer reads and writes information.

> [!info] TL;DR
> A residual (skip) connection adds the input of a sublayer to its output: $\mathbf{y} = \mathbf{x} + \text{Sublayer}(\mathbf{x})$. This gives gradients a direct path backward, making deep networks trainable. Without residuals, Transformers beyond ~10 layers don't converge.

## Definition

A residual connection (He et al., 2016 — ResNet) wraps a sublayer as:

$$
\mathbf{y} = \mathbf{x} + \text{Sublayer}(\mathbf{x})
$$

In Transformers, both sublayers (attention and FFN) are wrapped in residuals (see [[Transformer Block]]):

$$
\mathbf{h} = \mathbf{x} + \text{MHA}(\text{Norm}(\mathbf{x}))
$$

$$
\mathbf{y} = \mathbf{h} + \text{FFN}(\text{Norm}(\mathbf{h}))
$$

The idea came out of ResNet in computer vision — see [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]].

## Why residuals matter

### Gradient highway

In a deep network without residuals, the gradient must pass through every layer's derivative. By the chain rule, this multiplies many Jacobians:

$$
\frac{\partial L}{\partial \mathbf{x}_0} = \frac{\partial L}{\partial \mathbf{x}_N} \prod_{l=1}^{N} \frac{\partial \mathbf{x}_l}{\partial \mathbf{x}_{l-1}}
$$

If each $\frac{\partial \mathbf{x}_l}{\partial \mathbf{x}_{l-1}}$ has norm < 1, the product → 0 (vanishing gradient). If > 1, it → ∞ (exploding gradient) — the classic failure modes of deep recursion (see [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]).

With residuals, $\mathbf{x}_l = \mathbf{x}_{l-1} + \text{Sublayer}(\mathbf{x}_{l-1})$, so $\frac{\partial \mathbf{x}_l}{\partial \mathbf{x}_{l-1}} = I + \frac{\partial \text{Sublayer}}{\partial \mathbf{x}_{l-1}}$. The identity $I$ gives gradients a direct path backward, bypassing the sublayer's derivative.

### Incremental learning

The sublayer learns the **delta** from the input — what to add. This is easier to learn than the full transformation. Early in training, sublayers can be near-identity (small weights) and the network behaves like a shallow model; as training progresses, sublayers learn richer transformations.

### Identity initialization is natural

A network of pure residual blocks initialized with zero sublayer weights is the identity function. Training then "adds complexity" incrementally, which is a much better starting point than a random initialization.

## Visual

The wiring difference is one extra arrow — the difference between a trainable and an untrainable deep stack:

```
Without residual:              With residual:

  x → Sublayer → y              x ──────────────┐
                                                v
                                Sublayer → +  → y
                                            ^
                                            │
                                            └─ (from x)
```

## Worked implementation

```python
# A residual block in PyTorch
class ResidualBlock(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.norm = nn.LayerNorm(d)
        self.sublayer = SomeSublayer(d)
    
    def forward(self, x):
        # Pre-norm residual
        return x + self.sublayer(self.norm(x))
```

## Variants

The standard additive form dominates; several variants appear in the literature.

### Standard residual

$$
\mathbf{y} = \mathbf{x} + \text{Sublayer}(\mathbf{x})
$$

### Gated residual (rare)

$$
\mathbf{y} = \mathbf{x} + g \cdot \text{Sublayer}(\mathbf{x})
$$

where $g$ is a learned gate (scalar or per-channel). This lets the model turn a sublayer off. It is rare in Transformers.

### Multi-scale residual (rare)

Residuals that combine multiple skip lengths. Used in some computer vision architectures; not common in NLP Transformers.

### Dense connections (DenseNet-style)

Concatenate the input with the output instead of adding. Used in some encoder designs; not in standard Transformers.

## The residual stream as memory

A useful way to think about a Transformer, from Anthropic's interpretability work: the **residual stream** is a memory bus running through the model. Each **attention head** reads from the stream (Q, K, V projections) and writes to it (output projection); each **FFN** reads from the stream and writes to it. The model's computation is a sequence of read-modify-write operations on this shared memory.

This perspective explains why residual connections are so important — they're not just a training trick, they're the model's memory architecture. Mechanistic interpretability treats the residual stream as the "main memory" of the network and each sublayer as a "read-modify-write" operation on that memory — a powerful conceptual frame.

## Why this matters

Residuals are **essential** for training deep Transformers. The deepest current LLMs have 100+ layers; without residuals, none would train. The residual highway is also where **information accumulates** across layers — token representations "evolve" by adding successive sublayer contributions.

## Production implications

Residual connections add **zero parameters** and negligible compute (just an addition), so always include them. For inference, residuals are easy to fuse with adjacent operations in custom kernels. **Gradient checkpointing** works by recomputing the residual sublayer's output during the backward pass; the residual itself is trivially recomputable (just save the input). **Speculative decoding** exploits the residual stream structure too — when a draft model's prediction matches the target, you can skip ahead through the residual stream computation.

## Common pitfalls

Three mistakes account for most residual-related failures:

- **Forgetting the residual** — a "Transformer block" without residuals is just an MLP+attention MLP, and it won't train past a few layers.
- **Wrong dimension** — the sublayer's output must match the input's dimension for the addition. Always check shapes.
- **Adding normalization in the residual path** — in pre-norm, the residual is clean (no norm). Putting a norm in the residual path is "post-norm" or "sandwich-norm", which is a different architecture. Be intentional (see [[Pre-Norm vs Post-Norm]]).

## Further reading

Three references trace the idea from origin to modern interpretation:

- He et al. (2016), *Deep Residual Learning for Image Recognition* (ResNet) — the original.
- Veit et al. (2016), *Residual Networks Behave Like Ensembles of Relatively Shallow Networks*.
- Anthropic's "Mathematical Framework for Transformer Circuits" — residual stream as memory.

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]]
- [[Pre-Norm vs Post-Norm]]
- [[Normalization Layers]]
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Backpropagation/Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]] — residuals give gradients a shortcut
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]
- [[Backpropagation]]
