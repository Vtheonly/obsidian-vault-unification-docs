---
title: MiniMax 3 Architecture
type: concept
aliases: [MiniMax 3 Architecture, MiniMax-3, MiniMax 03]
tags: [model-architecture, minimax, hybrid, long-context, open-source, 2026]
sources: ["09 - MiniMax 3 Architecture"]
created_index: 20
---

MiniMax 3 continues MiniMax's lineage (abab-6 → abab-6.5 → MiniMax-Text-01 → MiniMax-M1 → MiniMax 3). MiniMax-01 (2025) was the first open-weights model to demonstrate million-token context using a hybrid lightning-attention + softmax-attention architecture, and MiniMax 3 is the 2026 successor. The source status is partially confirmed: MiniMax published a MiniMax-01 technical report (January 2025), but no MiniMax 3 technical report was found as of August 2026, so the architectural claims here are extrapolated from the MiniMax-01 trajectory and labelled accordingly.

> [!info] Source status
> - MiniMax-Text-01 (2025): **Officially Confirmed** in MiniMax technical report (456B total, 45.9B active, 1M context, hybrid lightning+softmax attention).
> - MiniMax-M1 (2025): **Officially Confirmed** — reasoning variant, MoE + lightning attention.
> - MiniMax 3 (2026): **Strong inference** — extrapolated from MiniMax-01/M1. No public MiniMax 3 technical report found.

## The MiniMax lineage

| Version | Release | Key architectural feature | Source status |
|---|---|---|---|
| abab-6 | 2023 | Standard Transformer; MoE | Officially Confirmed |
| abab-6.5 | 2024 | Larger MoE | Officially Confirmed |
| MiniMax-Text-01 | Jan 2025 | Hybrid lightning+softmax attention; 1M context; 456B MoE | Officially Confirmed |
| MiniMax-M1 | Mid 2025 | Reasoning variant; hybrid attention + test-time scaling | Officially Confirmed |
| MiniMax 3 | 2026 | Next generation; details not fully public | Strong inference |

The verified generations establish the family's two signatures — linear-time lightning attention for million-token context, and MoE at frontier scale — with M1 adding reasoning capability via test-time scaling ([[Test-Time Compute Scaling]]).

## What is known about MiniMax-01 (verified generation)

These are **Officially Confirmed** from the MiniMax-01 technical report (January 2025).

### Hybrid lightning + softmax attention

MiniMax-01 introduced a hybrid attention pattern: most layers use **lightning attention** — a linear-attention variant with a specific kernel-friendly formulation — with periodic **softmax attention** layers for retrieval. The ratio is roughly 7:1 (lightning:softmax), similar to Jamba's SSM:attention ratio ([[Jamba]]).

### MoE architecture

MiniMax-01 is a 456B-total / 45.9B-active MoE with 32 experts, 2 active per token (plus shared experts). Load balancing is auxiliary-loss-free — the same innovation as DeepSeek-V3 ([[DeepSeek Architecture]]).

### 1M token context

MiniMax-01 was the first open-weights model to support 1M token context natively. This is enabled by the hybrid attention: lightning attention is $O(n)$, so context grows linearly, while softmax attention is $O(n^2)$ but used sparingly.

### Open weights

MiniMax-01 weights are released under a permissive license (MiniMax's own license, similar to Llama's — see [[Llama Family Architecture]]). This makes MiniMax-01 the first open-weights frontier hybrid-attention model.

## Architectural expectations for MiniMax 3

> [!warning]
> The following are strong inferences, not confirmed facts.

### Refinement of hybrid attention (strong inference)

MiniMax 3 is expected to retain the hybrid lightning+softmax attention backbone. Possible refinements include a different ratio of lightning to softmax layers (e.g., 9:1 if 7:1 proved too attention-heavy), an improved lightning attention formulation, and dynamic scheduling that uses softmax attention only when needed.

### Larger MoE (strong inference)

MiniMax-01 was 456B/45.9B (total/active); MiniMax 3 is expected to grow this — potentially to 600B+ total parameters with similar activation sparsity.

### Reasoning training (strong inference)

MiniMax-M1 already demonstrated reasoning capability via RL on verifiable rewards, similar to DeepSeek-R1 ([[DeepSeek-R1]]). MiniMax 3 is expected to inherit this — possibly as a unified base model with thinking mode rather than a separate "M" variant.

### Native multimodal (speculative)

MiniMax-Text-01 was text-only, and MiniMax has separate vision models (MiniMax-VL). MiniMax 3 may consolidate vision into the base model, making it natively multimodal like Gemini ([[Gemini Architecture]]).

## Why MiniMax 3 matters architecturally

Four considerations make MiniMax 3 a distinctive data point. First, it is the **open-weights frontier hybrid**: MiniMax-01 was the first open-weights model to demonstrate million-token context via hybrid attention, and MiniMax 3 represents the next iteration. Second, **lightning attention specifically**: MiniMax's lightning attention is a distinct linear-attention formulation, different from Mamba-2's SSD and from Kimi Linear's hybrid ([[Mamba-2]], [[Kimi Linear]]), so MiniMax 3's attention recipe is a unique architectural data point. Third, the **Chinese open-weights frontier**: MiniMax is one of the leading Chinese AI labs (alongside DeepSeek, Qwen/Alibaba, Moonshot/Kimi, Zhipu/GLM), and MiniMax 3 represents another open-weights alternative in the Chinese ecosystem. Fourth, **reasoning + hybrid + long-context**: MiniMax-M1 already demonstrated reasoning on a hybrid backbone, and MiniMax 3 is the next data point on whether hybrid-attention backbones can match pure-Transformer backbones for reasoning quality.

## The MiniMax-01 architecture (reference for MiniMax 3)

### MoE configuration

| Property | MiniMax-Text-01 |
|---|---|
| Total parameters | 456B |
| Active per token | 45.9B |
| Experts | 32 |
| Active experts | 2 |
| Shared experts | 0 |
| Context | 1M (4M extended) |
| Attention | Hybrid (lightning + softmax, 7:1 ratio) |
| Positional | RoPE |
| Norm | RMSNorm (pre-norm) |
| Activation | SwiGLU |

The rest of the stack is conventional — RoPE positions, pre-norm RMSNorm, SwiGLU activations — with the hybrid attention schedule doing the long-context work.

### Hybrid attention schedule

MiniMax-01 uses a periodic full-attention schedule: roughly 1 in every 8 layers uses full softmax attention, and the other 7 use lightning attention. The exact pattern is documented in the MiniMax-01 technical report.

## Production implications (speculative)

If MiniMax 3 continues the MiniMax-01 pattern, deployment planning looks like this:

- **Serving**: MiniMax-01 is supported in [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] with hybrid attention kernels; MiniMax 3 serving should follow the same pattern.
- **Cost**: MiniMax-01's 45.9B active parameters per token is competitive with DeepSeek-V3's 37B and Qwen 3 235B-A22B's 22B ([[DeepSeek Architecture]], [[Qwen Family Architecture]]); MiniMax 3 should remain cost-competitive.
- **Long context**: MiniMax-01 was the first open-weights model with 1M context, and MiniMax 3 may push this further — potentially to 4M+ tokens.
- **Open weights**: if MiniMax 3 retains the open-weights pattern, it provides another open-weights alternative alongside DeepSeek-V3/R1, Qwen 3, and GLM 4.5/5 ([[GLM 5.2 Architecture]]).

## Common pitfalls

Three assumptions are worth avoiding when planning around MiniMax 3:

- **Confusing MiniMax-01 with MiniMax 3** — they may have different architectures or hybrid ratios; verify before assuming continuity.
- **Assuming "MiniMax 3" is the official name** — MiniMax may release under a different name (e.g., "MiniMax-02" or "MiniMax-Text-02"); the "3" label is an informal planning label rather than an announced product name.
- **Assuming lightning attention = standard linear attention** — lightning attention is a specific MiniMax formulation with custom kernels; it differs from Mamba-2's SSD and from generic linear attention.

## Verification checklist

Until MiniMax publishes a MiniMax 3 technical report, these are the claims to verify:

- [ ] Locate MiniMax 3 technical report (MiniMax blog or arXiv).
- [ ] Confirm architecture: hybrid attention retained? MoE config?
- [ ] Confirm total and active parameter counts.
- [ ] Confirm lightning attention formulation (same as MiniMax-01?).
- [ ] Confirm context length (1M, 4M, longer?).
- [ ] Confirm reasoning capability and training method.
- [ ] Confirm multimodal support (text-only or native multimodal?).
- [ ] Compare benchmarks to MiniMax-01 and MiniMax-M1.

## See also

- [[Interpretability and Research MOC]] — the hub for this area.
- [[MiniMax-01]] — the MiniMax-01 paper.
- [[Kimi Linear]] — comparable hybrid attention model.
- [[DeepSeek Architecture]] — comparable open-weights MoE.
- [[SSMs Mamba and Frontiers]] — context for linear/hybrid attention.
- [[Long-Context Architectures]] — the long-context design space.
- [[Jamba]] — the hybrid-ratio precedent.
- [[Mamba-2]] — the SSD formulation lightning attention differs from.
- [[Test-Time Compute Scaling]] — the M1 reasoning pattern.
- [[Qwen 3.8 Architecture]] and [[GLM 5.2 Architecture]] — sibling 2026 open-weights notes.
