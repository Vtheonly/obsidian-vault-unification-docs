---
title: Pre-Norm vs Post-Norm
type: concept
aliases: [Pre-Norm, Post-Norm, Norm Placement, Sandwich-Norm]
tags: [transformer, architecture, normalization, pre-norm, post-norm, training-stability]
sources: ["Pre-Norm vs Post-Norm"]
created_index: 29
---

Where the normalization sits inside a Transformer block — before or after the residual addition — is a small wiring detail with outsized consequences for training stability. The original Transformer normalized after the residual (post-norm), which is unstable without careful warmup; modern Transformers normalize before the sublayer (pre-norm), which keeps the residual path clean and trains far more reliably. A third variant, sandwich-norm, exists but is rare.

> [!info] TL;DR
> Where you put the normalization in a Transformer block matters enormously. The original Transformer used **post-norm** (norm after the residual) — unstable to train without warmup. Modern Transformers use **pre-norm** (norm before the sublayer) — much more stable and the modern default. A third variant, **sandwich-norm**, exists but is rare.

## The two designs

Both designs wrap each sublayer of a [[Transformer Block]] in a residual connection; they differ only in where the normalization sits relative to the sublayer.

### Post-norm (the original Transformer)

$$
\mathbf{y} = \text{Norm}(\mathbf{x} + \text{Sublayer}(\mathbf{x}))
$$

The normalization is applied **after** adding the residual. This was the original design of Vaswani et al. (2017).

### Pre-norm (GPT-2 onwards)

$$
\mathbf{y} = \mathbf{x} + \text{Sublayer}(\text{Norm}(\mathbf{x}))
$$

The normalization is applied **before** the sublayer. The residual path is "clean" — no normalization in the skip connection.

## Why pre-norm won

The key difference: in pre-norm, the residual path is **uninterrupted**. Gradients can flow directly from the loss to any layer through the residual highway. In post-norm, every layer's output passes through a normalization, which breaks the clean gradient highway.

Concretely: in post-norm, gradients must pass through Norm's derivative at every layer, and Norm's derivative can amplify or attenuate gradients unpredictably, causing instability — deep post-norm Transformers (12+ layers) are very hard to train without careful warmup. In pre-norm, the residual is a clean identity path; gradients flow freely, and training is much more stable, especially for deep models. Xiong et al. (2020) showed formally that pre-norm's gradients are better-conditioned at initialization, explaining the empirical stability difference.

### The catch: pre-norm's lazy sublayers

A subtle downside of pre-norm: because the residual is the identity, the sublayer's contribution is "added on top" of an already-good representation. The sublayer can become **lazy** — learning only small corrections — and the model becomes effectively shallower than its layer count suggests. This is sometimes observed but is usually outweighed by the stability benefits.

## The third variant: sandwich-norm

Some recent models (e.g., Microsoft's Turing-NLG, some Megatron variants) use **sandwich-norm**:

$$
\mathbf{y} = \text{Norm}_2(\mathbf{x} + \text{Sublayer}(\text{Norm}_1(\mathbf{x})))
$$

Normalization is applied both before and after. This combines the stability of pre-norm with the regularization of post-norm, but it is rare in practice.

## Visual comparison

The wiring difference is easiest to see side by side:

```
Post-norm:                      Pre-norm:
  x ──┐                          x ──────────┐
      │                                       │
      v                                       v
  Sublayer                              Norm ──> Sublayer
      │                                       │
      v                                       v
      + <─── x                                 + <────────── x
      │                                       │
      v                                       │
    Norm                                       │
      │                                       │
      v                                       v
      y                                       y
```

## Worked implementation

The two blocks are identical except for the order of the calls inside `forward`:

```python
class PostNormBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.attn  = MultiHeadAttention(d_model, n_heads)
        self.ffn   = FeedForward(d_model, d_ff)
    
    def forward(self, x):
        # Norm AFTER residual
        x = self.norm1(x + self.attn(x))
        x = self.norm2(x + self.ffn(x))
        return x

class PreNormBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.attn  = MultiHeadAttention(d_model, n_heads)
        self.ffn   = FeedForward(d_model, d_ff)
    
    def forward(self, x):
        # Norm BEFORE sublayer; residual is clean
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x
```

The difference is just where `norm` is called — but it changes training dynamics completely.

## Which models use what?

The historical split is sharp: everything before GPT-2 is post-norm, essentially everything after is pre-norm (usually with RMSNorm rather than LayerNorm — see [[Normalization Layers]]).

| Model         | Norm placement |
|---------------|----------------|
| Original Transformer (2017) | Post-norm |
| BERT (2018)   | Post-norm      |
| GPT-2 (2019)  | **Pre-norm**   |
| GPT-3 (2020)  | Pre-norm       |
| Llama 1/2/3   | Pre-norm (RMSNorm) |
| Mistral       | Pre-norm (RMSNorm) |
| Gemma         | Pre-norm (RMSNorm) |
| Qwen          | Pre-norm (RMSNorm) |
| DeepSeek      | Pre-norm (RMSNorm) |

**Pre-norm is universal in modern LLMs.** Post-norm survives only in BERT-family models such as [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]], for historical reasons.

## Why this matters

If you train a Transformer from scratch, **always use pre-norm** — post-norm will likely fail to converge without extensive warmup and tuning. Understanding the difference also helps you read papers from the 2017–2019 era (which often used post-norm) without confusion. The choice of norm placement interacts with initialization, learning rate, and warmup length; pre-norm is more forgiving on all of them, which is one of the reasons modern LLMs train more reliably than the original Transformer.

## Production implications

For inference, pre-norm vs post-norm doesn't matter much (same compute, same memory) — the choice is a training-time decision. When fine-tuning a pretrained model, **preserve the original norm placement**; don't try to "fix" it. For distributed training, pre-norm's stability matters more, because large-batch training is inherently less stable and pre-norm helps.

## Common pitfalls

Three mistakes cover most norm-placement bugs:

- **Mixing pre-norm and post-norm in the same model** — would be very confusing and probably broken. Pick one.
- **Forgetting the final norm** in pre-norm models — most pre-norm Transformers have a final LayerNorm/RMSNorm after the last block, because the last block's residual output is unnormalized. Don't forget it.
- **Wrong initialization for post-norm** — if you must use post-norm, you need careful initialization and long warmup (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]).

## Further reading

Three papers cover the formal and empirical analysis:

- Xiong et al. (2020), *On Layer Normalization in the Transformer Architecture* — formal analysis.
- Nguyen & Salazar (2019), *Transformers without Tears* — empirical study.
- Liu et al. (2020), *Understanding the Difficulty of Training Transformers* — more on stability.

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]]
- [[Normalization Layers]]
- [[Residual Connections]]
- [[GPT Family]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
