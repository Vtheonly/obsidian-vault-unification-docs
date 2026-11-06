---
title: Kimi K3 Architecture
type: concept
aliases: [Kimi K3, Moonshot K3]
tags: [model-architecture, kimi, moonshot, hybrid, long-context, 2026]
sources: ["11 - Kimi K3 Architecture"]
created_index: 11
---

Kimi K3 continues Moonshot AI's Kimi lineage (K1.5, K2, K3). K1.5 was a reasoning model trained with RL on verifiable rewards; K2 introduced a hybrid Mamba-Transformer backbone for million-token context, documented in the [[Kimi Linear]] paper; K3 represents the next generation. The source status is partially confirmed — Moonshot has not published a K3 technical report as of August 2026 — so the architectural claims here are extrapolated from the K1.5/K2 trajectory and labelled accordingly.

> [!info] Source status
> - K1.5 (reasoning model): **Officially Confirmed** in Moonshot technical report (2025).
> - K2 / Kimi Linear (hybrid SSM-attention): **Officially Confirmed** in Kimi Linear technical report (2025).
> - K3: **Strong inference** — extrapolated from the K1.5→K2 trajectory. No public K3 technical report found. Treat all K3-specific architectural claims as speculative until Moonshot releases a K3 paper or model card.

## The Kimi lineage

| Version | Release | Key architectural feature | Source status |
|---|---|---|---|
| Kimi 1.0 | 2023 | Standard decoder-only Transformer; long-context | Officially Confirmed |
| Kimi 1.5 | Early 2025 | Reasoning model; RL on verifiable rewards (math, code) | Officially Confirmed |
| Kimi K2 | Mid 2025 | Hybrid SSM-Transformer (Kimi Linear); million-token context | Officially Confirmed |
| Kimi K3 | Late 2025–2026 | Next generation; expected to extend hybrid + reasoning | Strong inference |

The K1.5→K2 trajectory shows two parallel innovations. The first is **reasoning capability** via RL on verifiable rewards (math, code) — the same recipe that produced o1 and R1. The second is a **linear-time hybrid architecture** via SSM-Transformer interleaving — the same recipe that produced [[Jamba]] and [[MiniMax-01]]. K3 is the natural synthesis: a hybrid-architecture model that also has reasoning training, and that synthesis is the 2026 frontier pattern.

## Architectural expectations for K3

> [!warning]
> The following are strong inferences, not confirmed facts.

### Hybrid SSM-Transformer backbone (strong inference)

K2 introduced Moonshot's hybrid architecture: a decoder-only stack interleaving SSM layers (linear-time, large state) with attention layers (exact retrieval, in-context learning). K3 is expected to continue this pattern. The SSM:attention ratio documented in K2 is roughly 7:1 (similar to Jamba), though K3 may revise this based on what K2's post-training analysis showed.

### Reasoning training (strong inference)

K1.5 demonstrated Moonshot's reasoning-RL recipe, and K3 as the successor is expected to inherit this training pipeline. The expectation is GRPO-style RL on verifiable rewards (math, code, scientific reasoning), with a separate "thinking" mode that produces long chain-of-thought before the final answer.

### Long context (strong inference)

K2 demonstrated million-token context via the hybrid SSM backbone — the [[KV Cache Mechanics|KV cache]] grows slowly because most layers are SSM. K3 is expected to retain or extend this, possibly to 2M+ tokens, matching the trajectory of frontier 2026 models like Gemini 1.5/2.0 (1M) and Claude 3.5 (200K–1M); see [[Gemini Architecture]] and [[Claude Architecture]] for those model lines.

### Multimodal capability (speculative)

Moonshot has not publicly released a Kimi-VL model. If K3 introduces multimodal capability, it would mark a major architectural extension. As of August 2026, this is **insufficient public evidence**.

## Why this note matters

Kimi's lineage is architecturally significant for two reasons. First, it demonstrated the **hybrid SSM-Transformer at frontier scale**: K2 was the second open-weights model (after Jamba) to show that the hybrid pattern works at frontier scale, and K3 is the next data point in this trajectory. Second, it points toward **reasoning on a hybrid backbone**: most [[Reasoning Models|reasoning models]] (o1, R1, Claude thinking) use standard Transformer backbones, so K3's combination of hybrid architecture plus reasoning training would be the first credible demonstration of reasoning capability on a non-Transformer-primary backbone. If successful, it validates the hybrid pattern as a foundation for reasoning, not just efficiency.

## Production implications (speculative)

If K3 inherits K2's hybrid architecture and K1.5's reasoning recipe, it would be the **first reasoning-capable model with linear-time inference** — a major cost reduction over attention-based reasoning models (o1, R1) that pay quadratic context costs during their long chain-of-thought. Three consequences follow for deployment planning:

- **Serving**: hybrid models require specialized kernels (a [[Mamba]] scan plus [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]). [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] added hybrid-model support in 2024–2025, so K3 serving should be production-ready by mid-2026.
- **Latency**: the SSM layers process context in $O(n)$ rather than $O(n^2)$; long-context reasoning queries that take 30s on R1 might take 10s on K3.
- **Memory**: hybrid models have a smaller KV cache (most layers are SSM with fixed-size state), so K3 could fit larger context windows on the same GPU.

## Common pitfalls

Three assumptions are worth avoiding when planning around K3:

- **Assuming K3 = K2 + thinking mode** — K3 may have a fundamentally different architecture (e.g., an MoE hybrid) that changes the serving characteristics.
- **Assuming K3 is open-weights** — K1.5 and K2 were open; K3 may be closed. Verify before assuming you can self-host.
- **Confusing K3's SSM with Mamba** — Moonshot's SSM may use a different formulation (their K2 paper introduces a custom selective scan variant).

## Verification checklist

- [ ] Locate K3 technical report or model card (Moonshot AI blog or arXiv).
- [ ] Confirm backbone type: pure Transformer, hybrid SSM-Transformer, or other.
- [ ] If hybrid, confirm the SSM:attention ratio.
- [ ] Confirm context length.
- [ ] Confirm reasoning training method (GRPO, PPO, or other RL variant).
- [ ] Confirm parameter count and (if MoE) active-parameter count.
- [ ] Confirm multimodal support (text-only vs native multimodal).
- [ ] Compare K3 benchmarks to K2 on standard reasoning evals (MMLU, GPQA, AIME, SWE-bench).

## See also

- [[Interpretability and Research MOC]] — the hub for this area.
- [[Kimi Linear]] — the K2 / Kimi Linear paper.
- [[DeepSeek Architecture]] — a comparable open-weights reasoning model.
- [[SSMs Mamba and Frontiers]] — SSM context.
- [[RWKV and RetNet]] — alternative hybrid approaches.
- [[Reasoning Models]] — the reasoning-model category.
- [[Long-Context Architectures]] — the long-context design space.
- [[Test-Time Compute Scaling]] — the reasoning-training pattern K3 is expected to inherit.
- [[Mamba]], [[Jamba]], [[MiniMax-01]] — the hybrid-architecture lineage.
