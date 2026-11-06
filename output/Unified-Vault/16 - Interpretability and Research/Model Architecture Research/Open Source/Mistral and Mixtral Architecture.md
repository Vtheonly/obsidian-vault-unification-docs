---
title: Mistral and Mixtral Architecture
type: concept
aliases: [Mistral and Mixtral Architecture, Mistral Architecture, Mixtral Architecture]
tags: [model-architecture, mistral, mixtral, sliding-window, moe, open-source]
sources: ["04 - Mistral and Mixtral Architecture"]
created_index: 21
---

Mistral AI's models (Mistral 7B, Mixtral 8x7B, Mixtral 8x22B, Mistral Large) build on the Llama architecture with two key innovations: sliding window attention (SWA) for efficient long context, and mixture-of-experts (MoE) for sparse compute. Mixtral 8x7B was the first open-weights MoE to match Llama 2 70B quality at 4× faster inference. The line-up spans the dense 7B, the sparse Mixtral models, and the dense Mistral Large and Mistral Nemo.

> [!info] Source status
> All claims are **officially confirmed** — documented in Mistral AI's blog posts (mistral.ai), model cards, and the Mistral 7B paper.

## Mistral 7B (September 2023)

### Architecture

Mistral 7B introduced sliding window attention and GQA to the Llama baseline:

| Property | Llama 2 7B | Mistral 7B |
|----------|------------|------------|
| Parameters | 6.7B | 7.2B |
| Layers | 32 | 32 |
| d_model | 4096 | 4096 |
| Heads | 32 | 32 |
| KV heads | 32 (MHA) | 8 (GQA) |
| Context | 4096 | 8192 |
| Attention | Full | Sliding window (4096) |
| Vocab | 32K | 32K |

### Sliding window attention

Each token attends to the previous 4096 tokens, not all previous tokens. With 32 layers, the effective receptive field is 32 × 4096 = 131K tokens — far more than the 8K context window. See [[Sliding Window Attention]] for the technique and [[Mistral 7B]] for the paper note.

### GQA

Mistral 7B uses 8 KV head groups shared across 32 query heads. This reduces the KV cache by 4×, enabling larger batch sizes and longer contexts. See [[GQA MQA and MLA]].

### Rolling buffer KV cache

The KV cache is stored as a circular buffer of size `window_size`. Position `i` is stored at `i mod window_size`. This keeps the cache fixed-size regardless of sequence length. See [[KV Cache Mechanics]] for KV cache fundamentals.

### Why Mistral 7B mattered

Mistral 7B outperformed Llama 2 13B on all benchmarks despite being 2× smaller. This proved that architectural improvements (SWA + GQA) could substitute for scale. It established 7B as the practical sweet spot for open-weights models.

## Mixtral 8x7B (December 2023)

### Architecture

Mixtral 8x7B is Mistral 7B with mixture-of-experts:

| Property | Mixtral 8x7B |
|----------|--------------|
| Total parameters | 46.7B |
| Active per token | 12.9B |
| Layers | 32 |
| d_model | 4096 |
| Experts per layer | 8 |
| Active experts | 2 |
| Attention | SWA (4096) + GQA |
| Context | 32K |
| Vocab | 32K |

### How MoE works in Mixtral

Each layer's FFN is replaced by 8 parallel FFNs ("experts"). For each token, a router selects the top-2 experts (by learned affinity score). Only those 2 experts compute; the other 6 are idle for that token.

```python
# For each token:
router_scores = softmax(router(token))  # 8 scores
top_2_experts = argsort(router_scores)[-2:]  # pick top 2
output = sum(router_scores[i] * expert[i](token) for i in top_2_experts)
```

This gives 12.9B active parameters (2 experts × ~6.5B each + attention) out of 46.7B total. The model has the capacity of a 47B model but the inference cost of a 13B model. See [[Mixture of Experts]] for the general pattern.

### Load balancing

Mixtral uses an auxiliary loss to balance expert usage — if some experts are overused and others idle, the loss penalizes the imbalance. This ensures all experts learn and contribute. (DeepSeek-V3 would later eliminate this auxiliary loss — see [[DeepSeek-V2 and V3]].)

### Key results

Mixtral 8x7B matched or exceeded Llama 2 70B on most benchmarks while being 4× faster at inference (12.9B active vs 70B active). This established MoE as practical for open-weights, not just closed-source models.

## Mixtral 8x22B (April 2024)

### Architecture

A scaled-up Mixtral:

| Property | Mixtral 8x22B |
|----------|---------------|
| Total parameters | 141B |
| Active per token | 39B |
| Experts per layer | 8 |
| Active experts | 2 |
| Context | 64K |
| Vocab | 32K |

### Key results

Mixtral 8x22B approached GPT-4 quality on some benchmarks, making it the strongest open-weights MoE as of mid-2024 (before DeepSeek-V3).

## Mistral Large (2024)

### Architecture

Unlike Mixtral, Mistral Large is a dense model (not MoE):

| Property | Mistral Large |
|----------|---------------|
| Parameters | 123B |
| Architecture | Dense (no MoE) |
| Attention | GQA |
| Context | 128K |
| Vocab | 32K → 128K (v2) |

### Why dense

Mistral Large is closed-weights (API only). For closed models, the inference cost advantage of MoE is less critical (you're charging per token anyway), and dense models are simpler to serve. The dense architecture may also be easier to align.

## Mistral Nemo (2024)

### Architecture

Developed with NVIDIA, designed as a drop-in upgrade for Mistral 7B:

| Property | Mistral Nemo |
|----------|--------------|
| Parameters | 12B |
| Attention | GQA |
| Context | 128K |
| Vocab | 128K (Tekken tokenizer) |

### Key features

Mistral Nemo brings 128K context (vs Mistral 7B's 8K), the Tekken tokenizer (128K vocab, better multilingual), and was trained with NVIDIA on their infrastructure. It is positioned as the "best 12B model" — small enough to run on consumer hardware, large enough for serious applications.

## Architectural patterns across the family

### Consistent choices

All Mistral models keep pre-norm, RMSNorm, SwiGLU, and no bias — inherited from Llama. GQA is used by all Mistral models (Mistral 7B was an early GQA adopter), and RoPE is the standard positional encoding. See [[Llama Family Architecture]] for the baseline these inherit from.

### Variable choices

SWA is used by Mistral 7B and Mixtral, but not always by Mistral Large/Nemo. MoE is used by the Mixtral variants, not by Mistral 7B/Large/Nemo. Context length has grown across the family: 8K (Mistral 7B) → 32K (Mixtral 8x7B) → 64K (Mixtral 8x22B) → 128K (Large, Nemo).

## Why Mistral's architecture matters

### SWA as a standard technique

Mistral 7B popularized sliding window attention. While not universally adopted (Llama 3 uses full attention), SWA is now a standard option for efficient long-context models.

### MoE for open weights

Mixtral proved that MoE works for open-weights. Before Mixtral, MoE was primarily a closed-source technique (GShard, Switch Transformer were research; GPT-4's rumored MoE was closed). Mixtral's open weights let the community study and build on MoE.

### The 7B sweet spot

Mistral 7B's success established 7B as the practical size for open-weights models. Llama 3 8B, Qwen 2.5 7B, and Gemma 2 9B all target this tier — small enough for consumer hardware, large enough for serious applications.

### European AI sovereignty

Mistral AI (French) demonstrated that frontier-quality open-weights LLMs could be developed outside the US. This had geopolitical implications — the EU's AI sovereignty depends on having competitive models, and Mistral provides that.

## Comparison to other families

| Family   | MoE?        | SWA?              | Notable innovation         |
|----------|-------------|-------------------|----------------------------|
| Llama    | Llama 4 only | No               | Conservative baseline      |
| Mistral  | Mixtral     | Yes (7B, Mixtral) | SWA + MoE for open weights |
| Qwen     | Qwen 2.5 MoE | Some variants    | Multilingual, large vocab  |
| DeepSeek | V2+         | No                | MLA, auxiliary-loss-free MoE |
| Gemma    | No          | No                | GQA, large vocab           |

Mistral's contribution is SWA + MoE, both adopted by the broader community. See [[Llama Mistral Qwen Comparison]] for the cross-family view.

## Impact and legacy

Mistral's architectural influence shows in four ways. It popularized SWA and GQA: both became standard techniques after Mistral 7B's success. It validated MoE for open-weights: Mixtral proved MoE was practical and competitive, paving the way for DeepSeek-V3, Qwen MoE, and Llama 4. It established the 7B tier: Mistral 7B's quality at 7B parameters made this the default size for cost-effective open-weights models. And it built a European AI presence: Mistral AI became the leading European AI lab, demonstrating that frontier-quality LLMs could be developed outside the US.

For AI engineers, Mistral models are strong choices for cost-sensitive deployments. The architectural lessons (SWA, GQA, MoE) are now standard across the open-weights ecosystem.

## Further reading

Primary sources for the claims in this note:

- Mistral 7B paper: arXiv:2310.06825 — see [[Mistral 7B]]
- Mixtral: arXiv:2401.04088
- Mistral blog: mistral.ai/news/
- [[Llama Mistral Qwen Comparison]] — comparison note.

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[Llama Family Architecture]] — the baseline Mistral builds on.
- [[Qwen Family Architecture]] — the multilingual large-vocab family.
- [[Gemma Architecture]] — Google's local + global alternative.
- [[Llama Mistral Qwen Comparison]] — cross-family comparison.
- [[Mistral 7B]] — the paper note.
- [[Sliding Window Attention]] — SWA in depth.
- [[GQA MQA and MLA]] — grouped-query attention.
- [[Mixture of Experts]] — the MoE pattern Mixtral opened up.
- [[DeepSeek-V2 and V3]] — the auxiliary-loss-free MoE successor.
- [[KV Cache Mechanics]] — context for the rolling buffer cache.
