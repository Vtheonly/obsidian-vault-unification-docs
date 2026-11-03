---
title: Qwen 3.8 Architecture
type: concept
aliases: [Qwen 3.8 Architecture, Qwen3.8, Alibaba Qwen 3.8]
tags: [model-architecture, qwen, alibaba, open-source, moe, 2026]
sources: ["08 - Qwen 3.8 Architecture"]
created_index: 22
---

Qwen 3.8 continues Alibaba's Qwen family lineage (Qwen → 1.5 → 2 → 2.5 → 3 → 3.5 → 3.8). Qwen 3 (2025) introduced MoE as the default architecture and hybrid attention, and Qwen 3.8 is the 2026 mid-cycle update. The source status is partially confirmed: Alibaba has released Qwen 3 with technical reports, but no Qwen 3.8-specific technical report was found as of August 2026, so the architectural claims here are extrapolated from the Qwen 3 trajectory and labelled accordingly. This note keeps the generation-specific expectations separate from the family-wide survey in [[Qwen Family Architecture]].

> [!info] Source status
> - Qwen 1, 1.5, 2, 2.5: **Officially Confirmed** — Alibaba technical reports and model cards.
> - Qwen 3 (2025): **Officially Confirmed** — Alibaba announcements and partial technical report; MoE as default, hybrid attention.
> - Qwen 3.5 / 3.8 (2026): **Strong inference** — extrapolated from Qwen 3. No public Qwen 3.8 technical report found.

## The Qwen lineage

| Version | Release | Key architectural feature | Source status |
|---|---|---|---|
| Qwen 1 | 2023 | MHA, 32K vocab, RoPE, SwiGLU | Officially Confirmed |
| Qwen 1.5 | Early 2024 | GQA, 151K vocab, larger context | Officially Confirmed |
| Qwen 2 | Mid 2024 | GQA, 151K vocab, up to 128K context | Officially Confirmed |
| Qwen 2.5 | Late 2024 | GQA, MoE variants, up to 128K context | Officially Confirmed |
| Qwen 3 | 2025 | MoE default, hybrid attention, larger sizes | Officially Confirmed |
| Qwen 3.5 | Early 2026 | Mid-cycle update | Strong inference |
| Qwen 3.8 | 2026 | Mid-cycle update | Strong inference |

The trajectory shows two clear inflection points: GQA replaced MHA at Qwen 1.5 while the vocabulary grew from 32K to 151K, and MoE-plus-hybrid-attention became the default at Qwen 3. Everything from Qwen 3.5 onward is extrapolation rather than documentation.

## What is known about Qwen 3 (verified generation)

The following are **Officially Confirmed** from Alibaba's Qwen 3 announcements and model cards.

### MoE as default

Qwen 3 made MoE the default architecture — not just a variant, as it still was in Qwen 2.5. All flagship Qwen 3 models are MoE; only the smaller models (e.g., Qwen 3 4B) are dense.

### Hybrid attention

Qwen 3 introduced hybrid attention: most layers use a linear/sparse attention variant, with periodic full-attention layers for retrieval and in-context learning. This is the same pattern as [[Kimi Linear]], [[MiniMax-01]], and GLM-4.5 (see [[GLM 5.2 Architecture]]).

### Reasoning variant (Qwen3-Thinking)

Qwen 3 released a "thinking" variant trained with RL on verifiable rewards — Qwen's answer to R1 and o1 (see [[DeepSeek-R1]]).

### Multimodal variants

Qwen 3 has separate vision-language (Qwen3-VL), audio (Qwen3-Audio), and code (Qwen3-Coder) variants rather than a single consolidated multimodal base.

## Architectural expectations for Qwen 3.8

> [!warning]
> The following are strong inferences, not confirmed facts.

### Refinement of the Qwen 3 architecture (strong inference)

Qwen 3.8 is expected to be a refinement of Qwen 3, not a fundamentally new architecture. Mid-cycle updates typically adjust expert counts and active-expert ratios, refine the hybrid attention schedule (more or fewer full-attention layers), extend context length, and improve the reasoning training recipe.

### Reasoning capability (strong inference)

Qwen 3-Thinking will likely be carried forward into Qwen 3.8-Thinking, or thinking mode may be built into the base Qwen 3.8. The reasoning recipe — GRPO on verifiable rewards — is by now standard across Chinese open-weights labs (DeepSeek-R1, Kimi K1.5, Qwen-Thinking).

### Multimodal consolidation (speculative)

Qwen 3 has separate VL, audio, and code variants. Qwen 3.8 may consolidate these into the base model, making it natively multimodal — the 2026 frontier pattern.

### Longer context (strong inference)

Qwen 3 supports 128K–256K context. Qwen 3.8 is expected to extend this to 512K–1M tokens, matching Gemini 1.5/2.0 and Kimi Linear (see [[Gemini Architecture]], [[Kimi Linear]], and [[Long-Context Architectures]]).

## The Qwen 3 architecture (reference for 3.8)

### MoE configuration

| Property | Qwen 3 30B-A3B (MoE) | Qwen 3 235B-A22B (MoE flagship) |
|---|---|---|
| Total parameters | 30B | 235B |
| Active per token | 3B | 22B |
| Experts | 128 | 94 |
| Active experts | 8 | 8 |
| Shared experts | 0 | 4 |
| Context | 128K | 128K |
| Vocab | 151K | 151K |
| RoPE base | 1000000 | 1000000 |

Both documented configurations activate 8 experts per token over a 151K vocabulary with a RoPE base of 1000000; the flagship adds 4 shared experts that the 30B model lacks.

### Hybrid attention schedule

Qwen 3 uses a periodic full-attention schedule: roughly 1 in every 4 layers uses full attention, and the other 3 use sparse/linear attention. The exact pattern is documented in the Qwen 3 technical report.

## Why Qwen 3.8 matters architecturally

Four considerations make this refinement worth tracking. First, the **Chinese open-weights frontier**: Qwen is Alibaba's flagship, alongside DeepSeek (DeepSeek-V3/R1) and Zhipu (GLM-4.5), so Qwen 3.8 represents another data point in the Chinese open-weights MoE-plus-hybrid landscape ([[DeepSeek Architecture]], [[GLM 5.2 Architecture]]). Second, **aggressive MoE sparsity**: Qwen 3 30B-A3B has a 10:1 sparsity ratio, and the flagship 235B-A22B has ~11:1 — approaching DeepSeek-V3's 18:1 and much more aggressive than Mixtral 8x22B's 3.25:1 ([[Mistral and Mixtral Architecture]]). Third, **hybrid attention at scale**: Qwen 3's hybrid attention schedule is the most aggressive among major open-weights models, so Qwen 3.8's specific recipe — if disclosed — would be a major reference for the 2026 hybrid-attention landscape. Fourth, **multilingual strength**: Qwen's 151K vocabulary supports Chinese, Arabic, Korean, Japanese, and other non-Latin scripts natively, and Qwen 3.8 is expected to retain this strength.

## Production implications (speculative)

If Qwen 3.8 follows the Qwen 3 pattern, deployment planning looks like this:

- **Serving**: Qwen 3 is supported in [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] with MoE + hybrid attention kernels; Qwen 3.8 serving should follow the same pattern.
- **Cost**: Qwen 3 30B-A3B is extremely cost-effective (only 3B active per token), and Qwen 3.8's small variant should retain this advantage.
- **Multilingual**: Qwen 3.8 should remain the strongest open-weights model for Chinese-language applications.
- **Open weights**: Alibaba has consistently released Qwen weights openly, and Qwen 3.8 should follow this pattern.

## Common pitfalls

Three assumptions are worth avoiding when planning around Qwen 3.8:

- **Confusing Qwen 3.8 with Qwen 3** — they may have different MoE configurations or hybrid attention schedules; verify before assuming continuity.
- **Assuming "Qwen 3.8" is the official name** — Alibaba may release under a different name (e.g., "Qwen 4" or "Qwen 3.5"); the "3.8" label is an informal planning label rather than an announced product name.
- **Assuming multimodal is consolidated** — Qwen 3 has separate VL/audio/code variants, and Qwen 3.8 may or may not consolidate them.

## Verification checklist

Until Alibaba publishes a Qwen 3.8 technical report, these are the claims to verify:

- [ ] Locate Qwen 3.8 technical report (Alibaba DAMO blog or arXiv).
- [ ] Confirm MoE configuration (experts, active experts, shared experts).
- [ ] Confirm hybrid attention schedule.
- [ ] Confirm context length.
- [ ] Confirm reasoning variant (Qwen 3.8-Thinking?).
- [ ] Confirm multimodal consolidation (if any).
- [ ] Compare benchmarks to Qwen 3 on standard evals (MMLU, GPQA, AIME, SWE-bench).

## See also

- [[Interpretability and Research MOC]] — the hub for this area.
- [[Qwen Family Architecture]] — the Qwen family overview.
- [[DeepSeek Architecture]] — comparable Chinese open-weights MoE.
- [[GLM 5.2 Architecture]] — comparable Chinese open-weights MoE.
- [[Kimi Linear]] — comparable hybrid attention.
- [[MiniMax-01]] — comparable hybrid attention at frontier scale.
- [[MiniMax 3 Architecture]] — the sibling 2026 hybrid-attention open-weights note.
- [[Long-Context Architectures]] — the long-context design space.
- [[Mistral and Mixtral Architecture]] — the Mixtral sparsity baseline behind the ratios above.
- [[DeepSeek-R1]] — the reasoning-RL recipe that Qwen3-Thinking answers.
