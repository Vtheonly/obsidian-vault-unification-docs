---
title: Feed-Forward Network
type: concept
aliases:
  - FFN
  - Feed-Forward Network Deep
  - position-wise feed-forward network
  - FFN sublayer
tags:
  - transformer
  - ffn
  - feed-forward-network
  - swiglu
  - geglu
  - activations
sources:
  - "05 - Feed-Forward Network (FFN) Deep Dive"
created_index: 25
---

The feed-forward network (FFN) is the "computation" half of every Transformer block, sitting next to attention as the "routing" half. It is a position-wise MLP — two linear layers with a nonlinearity in between — that expands each token's vector to roughly four times the model dimension before projecting it back, applied independently at every position. Modern LLMs have replaced the original ReLU FFN with gated variants such as SwiGLU and GEGLU, and about two-thirds of a Transformer's parameters live in these layers, which makes the FFN the primary target for quantization, pruning, and Mixture-of-Experts scaling.

> [!info] TL;DR
> The FFN sublayer is the "computation" half of every Transformer block (attention is the "routing" half): two linear layers with a nonlinearity in between, expanded to 4x the model dimension. Modern LLMs use SwiGLU or GEGLU instead of plain ReLU/GELU. ~2/3 of a Transformer's parameters live in FFNs.

## The standard FFN

For an input vector $\mathbf{x} \in \mathbb{R}^d$:

$$
\text{FFN}(\mathbf{x}) = \mathbf{W}_2 \, \sigma(\mathbf{W}_1 \mathbf{x} + \mathbf{b}_1) + \mathbf{b}_2
$$

Here $\mathbf{W}_1 \in \mathbb{R}^{d_{ff} \times d}$ projects up to the FFN hidden dimension, $\sigma$ is the activation — ReLU in the original Transformer, GELU in BERT/GPT, SwiGLU in Llama — and $\mathbf{W}_2 \in \mathbb{R}^{d \times d_{ff}}$ projects back to the model dimension, with $d_{ff} \approx 4d$ as the "expansion ratio."

The operation is applied **position-wise**: each token's vector goes through the same FFN independently. There is no cross-token interaction in the FFN — that is attention's job, and this division of labor is what makes the Transformer block work (see [[Transformer Block]]).

## Parameter count

For a Transformer with hidden dim $d_{model}$ and $d_{ff} = 4 d_{model}$, the attention sublayer contributes $\approx 4 d_{model}^2$ parameters (the Q, K, V, O projections), while the FFN contributes $2 \cdot d_{model} \cdot d_{ff} = 8 d_{model}^2$. The FFN is 2/3 of the parameters. This is why quantization and pruning of FFN layers has the most impact on model size.

## Activation choices

The choice of $\sigma$ is where the FFN has evolved most across model generations.

### ReLU (original Transformer)

$$
\text{FFN}(\mathbf{x}) = \mathbf{W}_2 \max(0, \mathbf{W}_1 \mathbf{x})
$$

Simple and fast, but can produce "dead" neurons.

### GELU (BERT, GPT-2)

$$
\text{FFN}(\mathbf{x}) = \mathbf{W}_2 \, \text{GELU}(\mathbf{W}_1 \mathbf{x})
$$

Smoother than ReLU (see [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]] for activations in general).

### SwiGLU (Llama, Mistral, Gemma, Qwen)

$$
\text{FFN}(\mathbf{x}) = \mathbf{W}_3 \, (\text{Swish}(\mathbf{W}_1 \mathbf{x}) \odot \mathbf{W}_2 \mathbf{x})
$$

Three weight matrices instead of two. The $\mathbf{W}_2 \mathbf{x}$ term is a "gate" that controls which dimensions of $\text{Swish}(\mathbf{W}_1 \mathbf{x})$ pass through, and empirically SwiGLU is better than GELU at scale. To keep the parameter count comparable, the hidden dim is reduced by factor $2/3$: $d_{ff} = \frac{8}{3} d_{model}$ (so $3 \cdot d \cdot \frac{8}{3}d = 8d^2$, the same as GELU's $2 \cdot d \cdot 4d$).

### GEGLU

Same as SwiGLU but with GELU instead of Swish:

$$
\text{FFN}(\mathbf{x}) = \mathbf{W}_3 \, (\text{GELU}(\mathbf{W}_1 \mathbf{x}) \odot \mathbf{W}_2 \mathbf{x})
$$

Comparable performance to SwiGLU; used in some models.

## Worked implementation

```python
import torch.nn as nn
import torch.nn.functional as F

class GELUFFN(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff)
        self.w2 = nn.Linear(d_ff, d_model)

    def forward(self, x):
        return self.w2(F.gelu(self.w1(x)))

class SwiGLUFFN(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        # d_ff should be 2/3 of 4*d_model for parameter parity with GELU
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)
        self.w3 = nn.Linear(d_model, d_ff, bias=False)  # the gate

    def forward(self, x):
        # Swish(W1 x) ⊙ W3 x, then W2
        return self.w2(F.silu(self.w1(x)) * self.w3(x))
```

The `GELUFFN` is the classic two-matrix form. The `SwiGLUFFN` uses three bias-free matrices; note that the code names the gate `w3` and the output projection `w2`, while the formula above calls the gate $\mathbf{W}_2$ and the output projection $\mathbf{W}_3$ — the semantics are identical (Swish of one projection, element-wise gated by a second, then projected down by the third).

## Why the FFN matters

### It is where knowledge is stored

Mechanistic interpretability work suggests that FFNs act as **key-value memories**: $\mathbf{W}_1$ detects patterns (keys) and $\mathbf{W}_2$ produces outputs (values). The model stores factual knowledge in FFN weights.

### It is the parameter bulk

Most of a Transformer's parameters are in FFNs. This is where quantization gives the biggest memory savings, where pruning has the most impact, and where MoE replaces one FFN with many — scaling parameters without scaling compute.

### It enables per-token computation

Attention routes information across tokens; the FFN transforms each token independently. This separation is what makes the Transformer block work — you need both.

## Mixture-of-experts FFN

In MoE models (Mixtral, DeepSeek-V3), the FFN is replaced by $E$ parallel FFN "experts" plus a router:

$$
\text{MoE}(\mathbf{x}) = \sum_{i=1}^{E} g_i(\mathbf{x}) \cdot \text{FFN}_i(\mathbf{x})
$$

where $g_i(\mathbf{x})$ is the router's gating for expert $i$. Typically only top-2 experts are activated per token, so compute is ~2 FFNs but parameters are $E$ FFNs. This decouples parameter count from compute — you can have 8x more parameters at the same compute cost. See [[Mixture of Experts]] for routing, load balancing, and the flagship MoE models.

## Production implications

The FFN is half of every Transformer block, so understanding it is essential; modern LLMs universally use SwiGLU or GEGLU, and these are the terms you meet when reading model configs. For inference cost, the FFN is the bulk of compute — optimizing it (quantization, MoE, sparsity) has the biggest impact. For interpretability, the FFN is where the model "stores" knowledge, which makes it the target of editing and unlearning research.

In practice, the SwiGLU FFN is standard for new model designs — don't use a plain ReLU FFN. FFN quantization gives the biggest memory savings; INT4 FFN weights with FP16 attention is a common pattern. MoE models are increasingly common (Mixtral, DeepSeek-V3) — they swap one FFN for many, getting more parameters at the same compute. Finally, the FFN is fully parallel across positions during prefill — unlike attention, there is no $n^2$ cost — which means prefill is mostly FFN-bound.

## Common pitfalls

Four traps recur. A wrong FFN hidden dimension for SwiGLU — it must be $\frac{2}{3} \cdot 4 d_{model}$ (rounded to a multiple of 256 or so) for parameter parity. Forgetting that the FFN is position-wise — if you accidentally mix positions, you break the architecture. Bias terms — modern LLMs (Llama, Mistral) often omit bias in the FFN, so match the model's choice. And not using fused kernels — naive PyTorch SwiGLU is slow; use fused implementations from vLLM / FlashAttention / PyTorch 2+.

## Further reading

- Shazeer (2020), *GLU Variants Improve Transformer* (SwiGLU, GEGLU).
- Geva et al. (2021), *Transformer Feed-Forward Layers Are Key-Value Memories* (interpretability).
- Shazeer et al. (2017), *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer* (MoE).

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]], [[The Transformer]]
- [[Mixture of Experts]], [[Normalization Layers]], [[GPT Family]]
- [[Embedding Layer]]
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[Activation Functions]]
- [[Mechanistic Interpretability]]
