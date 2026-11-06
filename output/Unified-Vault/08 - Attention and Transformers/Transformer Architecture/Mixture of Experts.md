---
title: Mixture of Experts
type: concept
aliases:
  - MoE
  - MoE Transformer
  - Mixture-of-Experts
  - sparse MoE
  - conditional computation
tags:
  - transformer
  - moe
  - mixture-of-experts
  - routing
  - load-balancing
  - mixtral
  - deepseek
sources:
  - "15 - Mixture-of-Experts (MoE) Transformer"
created_index: 27
---

A Mixture-of-Experts (MoE) Transformer replaces each dense feed-forward network with multiple parallel FFN "experts" plus a router that sends each token to only a small subset of them — typically two. You get more parameters (more capacity) at the same compute cost, which is why the largest open models, Mixtral 8x7B and DeepSeek-V3, are MoE. The price is a set of new systems problems, above all load balancing across experts.

> [!info] TL;DR
> MoE Transformers replace each FFN with multiple parallel FFN "experts" plus a router. Each token activates only 2 experts — so you get more parameters (more capacity) at the same compute cost. Mixtral 8x7B and DeepSeek-V3 are flagship MoE LLMs.

## The idea

In a dense Transformer, each token goes through one FFN per layer. In an MoE Transformer, each token is routed to **a small subset** of $E$ parallel FFN "experts":

$$
\text{MoE}(\mathbf{x}) = \sum_{i=1}^{E} g_i(\mathbf{x}) \cdot \text{FFN}_i(\mathbf{x})
$$

where $g_i(\mathbf{x})$ is the router's gating for expert $i$. Typically only top-$k$ experts (usually $k=2$) have non-zero gates — so only $k$ FFNs are computed per token.

## The router

The router is a small linear layer followed by softmax/top-k:

$$
\mathbf{g}(\mathbf{x}) = \text{Softmax}(\text{TopK}(\mathbf{W}_g \mathbf{x}))
$$

Here $\mathbf{W}_g \in \mathbb{R}^{E \times d}$ maps the token to $E$ logits, TopK selects the top-$k$ (e.g., 2) experts, and softmax normalizes their gates (the other experts get gate 0). The router is the only MoE-specific learned component — the experts are just standard FFNs, exactly the ones described in [[Feed-Forward Network]].

## Parameter and compute scaling

For an MoE with $E$ experts, top-$k$ routing, and FFN hidden dim $d_{ff}$:

- **Parameters**: $E \cdot 2 \cdot d \cdot d_{ff}$ (E FFNs).
- **Compute per token**: $k \cdot 2 \cdot d \cdot d_{ff}$ (only k FFNs computed).

For Mixtral 8x7B ($E=8, k=2$): parameters are ~47B (8x the FFN), while compute is ~13B (2x the FFN). You get a 47B-capacity model at the compute cost of a 13B dense model.

## Load balancing

If the router sends all tokens to the same few experts, the others are wasted and the active experts are overworked. **Load balancing** ensures tokens are distributed evenly across experts, and it is the critical problem in MoE training.

### Auxiliary loss (original MoE)

Add a regularization term to the loss that penalizes imbalanced routing:

$$
L_{\text{aux}} = E \cdot \sum_{i=1}^{E} f_i \cdot P_i
$$

where $f_i$ is the fraction of tokens routed to expert $i$ and $P_i$ is the average gate probability for expert $i$. The loss is minimized when tokens are uniformly distributed. This works but has problems: the auxiliary loss competes with the main loss and can hurt quality.

### Auxiliary-loss-free balancing (DeepSeek-V3)

DeepSeek-V3 introduced a clever alternative: **per-expert bias** that's adjusted based on recent load. If an expert is overloaded, its bias is decreased (fewer tokens routed to it); if underloaded, increased. No auxiliary loss is needed. This is one of DeepSeek-V3's key innovations and a reason it's so efficient.

## Worked example (Mixtral-style)

```python
import torch.nn as nn
import torch.nn.functional as F

class MoELayer(nn.Module):
    def __init__(self, d_model, d_ff, n_experts=8, top_k=2):
        super().__init__()
        self.n_experts = n_experts
        self.top_k = top_k
        self.router = nn.Linear(d_model, n_experts, bias=False)
        self.experts = nn.ModuleList([
            SwiGLUFFN(d_model, d_ff) for _ in range(n_experts)
        ])

    def forward(self, x):
        # x: (B, T, d)
        B, T, D = x.shape
        x_flat = x.view(B * T, D)

        # Router logits and top-k selection
        router_logits = self.router(x_flat)  # (B*T, n_experts)
        gates, selected_experts = torch.topk(router_logits, self.top_k, dim=-1)
        gates = F.softmax(gates, dim=-1)  # (B*T, top_k)

        # Compute (in practice, this is batched by expert for efficiency)
        out = torch.zeros_like(x_flat)
        for i in range(self.top_k):
            for tok_idx in range(B * T):
                expert_idx = selected_experts[tok_idx, i].item()
                out[tok_idx] += gates[tok_idx, i] * self.experts[expert_idx](x_flat[tok_idx:tok_idx+1]).squeeze(0)
        return out.view(B, T, D)
```

The experts here are `SwiGLUFFN` instances, the standard modern FFN. Real implementations use grouped GEMM kernels and avoid the per-token Python loop.

## MoE models

| Model              | Experts | Active | Total Params | Notes                              |
|--------------------|---------|--------|--------------|------------------------------------|
| Mixtral 8x7B       | 8       | 2      | 47B          | Top-2 routing, dense experts       |
| Mixtral 8x22B      | 8       | 2      | 141B         | Bigger version                     |
| DeepSeek-V2        | 160     | 6      | 236B         | Fine-grained experts, shared experts |
| DeepSeek-V3        | 256     | 8      | 671B         | Aux-loss-free balancing, 37B active |
| DeepSeek-R1        | 256     | 8      | 671B         | Reasoning model on V3 base         |
| Qwen-MoE           | 60      | 4      | 14B (3B active) | Fine-grained experts            |

The trend across these releases is toward many fine-grained experts with a small number active per token, which keeps serving compute low while total capacity grows.

## Why this matters

MoE is **the** way to scale parameters without scaling compute — the biggest open models (DeepSeek-V3, Mixtral 8x22B) are MoE. The economics favor it too: MoE models are cheaper to **serve** than dense models of the same quality, because only a fraction of experts activate per token. MoE also creates new system challenges — load balancing, expert parallelism, sparse gradient updates — and the DeepSeek-V3 paper is essential reading for these. For inference, MoE models need careful **expert parallelism** (different experts on different GPUs) to fit in memory.

## Production implications

For high-quality open models, DeepSeek-V3 and Mixtral offer better quality-per-FLOP than dense models. **Memory**: MoE models need more total memory (all experts must be loaded) even though active compute is lower, so plan GPU memory accordingly. **Serving**: use vLLM or SGLang with MoE support; expert parallelism across multiple GPUs is essential for large MoE. **Fine-tuning MoE** is possible but more complex — LoRA on MoE is supported by PEFT, usually applied to attention layers (not experts). And routing bugs are silent: if the router collapses (always picks the same experts), quality degrades without an obvious error, so monitor expert utilization.

## Common pitfalls

Four traps recur. Forgetting to monitor expert load — if one expert gets 80% of tokens, your MoE is essentially a dense model with wasted parameters. Choosing the wrong expert count — too few experts means no benefit, too many means routing overhead and per-expert undertraining. An inefficient routing implementation — the naive per-token Python loop is 100x slower than grouped GEMM, so always use the framework's MoE kernel. And forgetting to handle tokens that need to be re-routed (when an expert is at capacity) — some MoE implementations drop tokens or re-route.

## Further reading

- Shazeer et al. (2017), *Outrageously Large Neural Networks: The Sparsely-Gated MoE Layer*.
- Fedus et al. (2022), *Switch Transformers*.
- Jiang et al. (2024), *Mixtral of Experts*.
- DeepSeek-AI (2024), *DeepSeek-V2 / DeepSeek-V3 Technical Reports*.

## See also

- [[Attention and Transformers MOC]]
- [[Feed-Forward Network]], [[GPT Family]], [[Transformer Block]]
- [[GQA MQA and MLA]] — DeepSeek also introduced MLA
- [[The Transformer]], [[Choosing the Right Architecture]]
- [[Interpretability and Research MOC]]
