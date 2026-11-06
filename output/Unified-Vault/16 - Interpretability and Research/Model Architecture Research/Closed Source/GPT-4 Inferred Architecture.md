---
title: GPT-4 Inferred Architecture
type: concept
aliases: [GPT-4 Architecture, GPT-4 Inferred Architecture]
tags: [model-architecture, gpt-4, closed-source, inferred]
sources: ["07 - GPT-4 Inferred Architecture"]
created_index: 9
---

OpenAI has never officially disclosed GPT-4's architecture. Based on inference costs, capability patterns, and community analysis — most notably the "semi-analysis" leak — GPT-4 is strongly inferred to be a Mixture-of-Experts model with ~1.7T total parameters and ~280B active per token, using 16 experts. This note separates what is publicly known, what is inferred, and what is speculative, and it treats every specific number as unverified.

> [!warning] Source status
> **Most claims in this note are strongly inferred or speculative.** OpenAI has not officially disclosed GPT-4's architecture. The inferences below are based on GPT-4's inference cost (much higher than a dense model of similar capability), capability patterns (specialized strengths suggesting expert specialization), community analysis (notably the "semi-analysis" report, 2023), and comparison to known MoE models (Mixtral, DeepSeek-V3). Treat all specific numbers as unverified.

## What is officially confirmed

OpenAI's GPT-4 technical report (March 2023) — see [[GPT-4 Technical Report]] — disclosed almost no architectural details. The only confirmed facts are that GPT-4 is a Transformer-based model; that it can process images as well as text (multimodal); that it was trained with RLHF; that it passes professional exams at human-expert level; and that it has a knowledge cutoff (originally September 2021, later updated). Everything else — parameter count, architecture (dense vs MoE), training data, training compute — is not officially disclosed.

## What is strongly inferred

### Mixture-of-experts architecture

The strongest inference is that GPT-4 is a MoE model (see [[Mixture of Experts]] for the pattern). The evidence: GPT-4's inference cost is ~10–30× GPT-3.5's, despite not being 10–30× more capable — consistent with a large MoE where only a fraction of parameters are active per token. The 128K context variant (GPT-4 Turbo) is expensive, suggesting large per-token compute. And Mixtral 8x7B (see [[Mistral and Mixtral Architecture]]) and DeepSeek-V3 (see [[DeepSeek Architecture]]) demonstrated that MoE matches dense quality at lower active compute, so GPT-4 likely uses the same approach. Inference: GPT-4 is a MoE model. The number of experts and the routing mechanism are not confirmed.

### Parameter count (~1.7T total, ~280B active)

The "semi-analysis" report (July 2023), based on analysis of GPT-4's behavior and costs, estimated 1.7T total parameters across 16 experts, with 2 experts active per token (~280B active). This is consistent with the inference cost: 280B active is ~4× GPT-3.5's ~175B, matching the ~4× cost premium at launch. The 16-expert, 2-active design mirrors Mixtral (8 experts, 2 active) at larger scale. Three caveats apply: the "semi-analysis" report is not peer-reviewed or officially confirmed; the numbers may have changed with GPT-4 Turbo (2023), GPT-4o (2024), and subsequent versions; and OpenAI has never confirmed or denied these estimates.

### Multimodal training

The original GPT-4 could process images from launch (March 2023), and its image understanding is fluent (not bolted-on), suggesting the model was trained on image-text data, not just text. GPT-4o (2024) extended to audio, suggesting native multimodal training. Inference: GPT-4 was trained on image-text pairs (and possibly audio for GPT-4o), with vision and language integrated in the same model (not a separate vision encoder).

### RLHF with process reward models

GPT-4's reasoning quality (multi-step math, code) exceeds what outcome-only RLHF typically achieves. OpenAI's research on process reward models — which evaluate intermediate reasoning steps, not just final answers — was published around GPT-4's development, and the strong reasoning suggests PRM-based RLHF, not just outcome-based RLHF. Inference: GPT-4's alignment used process reward models (evaluating reasoning steps), not just outcome reward models (evaluating final answers). This is not confirmed.

## What is speculative

### Specific expert count and routing

The "16 experts, 2 active" claim is unverified. Other estimates — 8 experts with 4 active, or 32 experts with 2 active — are also plausible. Without official disclosure, the exact configuration is speculative.

### Training data composition

GPT-4's training data is not disclosed. Inferences about specific datasets (CommonCrawl, books, code, proprietary data) are speculative.

### Training compute

Estimated at ~10²⁵ FLOPs (based on inference cost and capability), but this is a rough estimate. The actual compute is not disclosed.

### Specific architectural components

Whether GPT-4 uses GQA, MLA, sliding window attention, or other specific techniques is not known. Inferences based on capability patterns are speculative.

## Why the architecture isn't disclosed

OpenAI's stated reasons for non-disclosure are competitive concerns (disclosing architecture helps competitors replicate GPT-4), safety concerns (disclosing capabilities helps bad actors understand what the model can do), and commercial strategy (mystery about architecture maintains perceived value). Critics counter on three fronts: non-disclosure hinders research (without architecture, academic research on frontier models is limited), concentrates power (only OpenAI knows how GPT-4 works, creating an information asymmetry), and amounts to safety theater (the safety benefits of non-disclosure are questionable).

## Comparison to known MoE models

If GPT-4 is indeed a ~1.7T MoE with ~280B active, it compares to the confirmed MoE models as follows:

| Model             | Total Params | Active Params | Experts | Active Experts |
|-------------------|--------------|---------------|---------|----------------|
| Mixtral 8x7B      | 46.7B        | 12.9B         | 8       | 2              |
| Mixtral 8x22B     | 141B         | 39B           | 8       | 2              |
| DeepSeek-V3       | 671B         | 37B           | 256     | 8              |
| GPT-4 (inferred)  | ~1.7T        | ~280B         | ~16     | ~2             |

GPT-4's inferred design (large total, large active) would explain both its capability (large total capacity) and its cost (large active compute).

## How this compares to open-weights

By 2024–2025, open-weights models (Llama 3.1 405B, DeepSeek-V3) matched or exceeded GPT-4 on many benchmarks. The open models have known architectures (dense 405B for Llama; MoE 671B/37B for DeepSeek). This suggests that GPT-4's capability is no longer unique — open models have caught up — and that the inferred ~280B active compute is consistent with DeepSeek-V3's 37B active (both are MoE, though at different scales).

## Open-weights comparables to GPT-4 (2024-2026)

By late 2024, several open-weights models matched or exceeded original GPT-4 on common benchmarks. These serve as architectural reference points:

| Model          | Architecture      | Total / Active params | Notable Features                                 |
|----------------|-------------------|------------------------|--------------------------------------------------|
| Llama 3.1 405B | Dense decoder-only | 405B / 405B            | GQA, RoPE, 128K context, SwiGLU                  |
| DeepSeek-V3    | MoE decoder-only   | 671B / 37B             | MLA, 256 experts (8 active), auxiliary-loss-free routing |
| Qwen2.5-72B    | Dense decoder-only | 72B / 72B              | GQA, RoPE, 128K context, YaRN extension          |
| Mixtral 8x22B  | MoE decoder-only   | 141B / 39B             | GQA, 8 experts (2 active), sliding window + global |
| Kimi K2        | MoE decoder-only   | ~1T / ~32B (inferred)  | MLA, sparse attention, long context              |

If GPT-4 is ~1.7T total / ~280B active (the semi-analysis estimate), it would be ~4× larger than Llama 3.1 405B (dense) and ~2.5× larger total than DeepSeek-V3, but ~7.5× larger active. The active compute (280B) is significantly larger than DeepSeek-V3's 37B — explaining GPT-4's higher cost.

## Why GPT-4 Turbo and GPT-4o changed the picture

GPT-4 Turbo (Nov 2023) and GPT-4o (May 2024) likely changed the underlying architecture, which means the "GPT-4" architecture is not a single fixed thing — it is a moving target, and inferences made about the original GPT-4 (Mar 2023) may not apply to GPT-4o (May 2024) or o1 (Sep 2024). The inferred changes: GPT-4 Turbo brought 128K context (vs the original 32K) at a lower price (~3× cheaper than original GPT-4); the lower price suggests either smaller active compute or improved serving efficiency, and the longer context suggests YaRN-style RoPE extension or a separate long-context variant (see [[Long-Context Architectures]]). GPT-4o is natively multimodal (text + image + audio in one model), 2× faster than GPT-4 Turbo, and 50% cheaper; the speed improvement suggests architectural changes (possibly smaller active parameters or better attention efficiency), and the native multimodality suggests the model was trained end-to-end on text, image, and audio tokens, not bolted-on encoders. o1/o3 are reasoning models, almost certainly a different training recipe (RL on verifiable rewards) on top of a GPT-4-class base — the architecture may be similar; the training and inference differ (see [[Test-Time Compute Scaling]]).

## How to infer architecture without disclosure

The methodology behind "inferring" closed-model architectures is itself instructive. Five primary signals are used, each with strengths and weaknesses.

### Inference cost vs capability

A dense model's inference cost grows linearly with parameter count. If a model is 10× more expensive than a smaller dense model but only 2× more capable, the gap is consistent with a MoE where the total parameter count is large but the active count is moderate. This was the primary signal for GPT-4: cost ~10–30× GPT-3.5 with capability ~2× GPT-3.5, consistent with a large MoE. Strength: directly observable from pricing. Weakness: pricing is a business decision, not a pure cost reflection — OpenAI could price GPT-4 at a margin unrelated to its actual compute cost.

### Capability asymmetries

If a model excels at certain subtasks (e.g., code generation) but is mediocre at others (e.g., creative writing), this suggests expert specialization — different experts may have learned different domains. This is a weak signal because capability differences can also arise from training data composition, not architecture.

### Behavioral patterns

Specific behavioral quirks (e.g., the model "loses" information at certain context lengths, or has characteristic failure modes) can hint at architectural choices. For example, RoPE-based models have characteristic failure modes at lengths exceeding the training context, and sliding-window models lose long-range dependencies beyond the window. These patterns can be tested via targeted probes.

### Leakage from employees and partners

Occasionally, employees or partners leak architectural details. The "semi-analysis" report on GPT-4 was based on partial information from people with knowledge of the system. This is the most direct signal but also the least verifiable — leaks can be wrong, partial, or outdated.

### Comparison to open models with similar capability

If an open model with known architecture (e.g., DeepSeek-V3, MoE 671B/37B) matches GPT-4's capability, it is reasonable to infer GPT-4 has roughly similar active compute. This is the "anchoring" approach — use open models as calibration points for closed ones.

The combination of all five signals gives the community's best estimate, but the uncertainty is large. Treat any specific number (parameter count, expert count) as ±50% accurate.

## Implications for AI engineers

### You don't need GPT-4's architecture

For most applications, you don't need to know GPT-4's exact architecture. You need to know its capabilities (well-documented in the technical report), its API behavior (well-documented in OpenAI's docs), and its cost and latency (well-documented in pricing).

### Open models are catching up

Llama 3.1 405B and DeepSeek-V3 match GPT-4 on many benchmarks, with known architectures. If you need architectural transparency, use open models.

### Closed-model inference is valid

Even without knowing the architecture, you can build production applications on GPT-4. The API contract (input → output) is stable regardless of internal architecture.

### For research, use open models

If you're doing interpretability, architecture research, or capability analysis, you need open weights. GPT-4 is unsuitable for these purposes because you can't inspect its internals.

## How to build production systems without knowing GPT-4's architecture

For most AI engineers, GPT-4's architecture is irrelevant: you interact with it via API, and the contract is input → output. Build systems that follow five rules. First, don't depend on architectural assumptions — if you assume GPT-4 has a 128K context and OpenAI releases a 256K version, your system should benefit, not break. Second, pin the model version: use `gpt-4o-2024-08-06`, not `gpt-4o`, which protects against silent architectural changes. Third, have fallbacks: if GPT-4 is unavailable, fall back to Claude or an open model — architectural diversity across providers is itself a form of resilience. Fourth, treat the model as a black box: benchmark on your task, and if the model is good enough, use it; don't try to predict quality from architecture. Fifth, for research use open weights — interpretability, capability analysis, and architecture research require inspectable models, and GPT-4 is unsuitable for these.

## The disclosure debate

The non-disclosure of closed-model architectures is a live debate in 2026. Arguments for disclosure: it enables academic research on frontier models; it allows auditors to assess safety properties; it reduces information asymmetry between providers and the public; and open models with disclosed architectures (Llama, DeepSeek) demonstrate that disclosure doesn't prevent commercial success. Arguments against disclosure: it helps competitors replicate the model; it helps adversaries find vulnerabilities; disclosed capabilities may be over-interpreted by regulators; and most users don't need the architecture — the API contract is sufficient.

The current equilibrium: closed providers (OpenAI, Anthropic) disclose system cards (high-level capabilities and safety properties) but not architectures, while open providers (Meta, DeepSeek, Mistral, Qwen) disclose architectures fully. This equilibrium is likely to persist — the commercial pressure to disclose is low, and the research community can use open models.

## Future disclosure

OpenAI is unlikely to disclose GPT-4's architecture. However, GPT-4o, o1, and GPT-5 (if released) may have different architectures, and old architectures may become less sensitive to disclose over time. OpenAI might disclose GPT-4's architecture years after release (as Google did for some old models), and the open-source community's reverse-engineering will continue to refine the inferences.

## Interview questions

**What can you infer about GPT-4's architecture from its API behavior?** Five main inferences: (1) MoE (from the cost/capability gap), (2) ~1.7T total / ~280B active (from semi-analysis), (3) multimodal training (from fluent image understanding), (4) RLHF with PRMs (from reasoning quality), (5) RoPE-based positional encoding (from context-length behavior). All inferences are unconfirmed; treat them as ±50% accurate.

**How would you validate an inference about a closed model's architecture?** Behavioral probes. Test the model's context-length scaling (RoPE vs ALiBi vs learned), test for sliding-window behavior (long-range dependency failures), test for MoE routing (capability asymmetries across subtasks), and measure latency vs input length (linear → dense; sublinear → MoE). No single probe is conclusive; combine many.

**Why does the AI community care about GPT-4's architecture if open models match it?** Three reasons: (1) GPT-4 set the capability benchmark for years, and understanding how it works informs architecture research. (2) Closed models still lead on some benchmarks (especially reasoning with o1/o3), and the architecture behind this lead is valuable to understand. (3) For interpretability and safety research, knowing the architecture of deployed models matters — most users interact with closed models.

**If you needed to replicate GPT-4's capability with open tools in 2026, what would you use?** DeepSeek-V3 (MoE 671B/37B) or Llama 3.1 405B (dense) for base capability. Add RLHF (DPO or GRPO) for alignment. For reasoning capability, fine-tune with the R1 recipe (RL on verifiable rewards). For multimodal, add a vision encoder (SigLIP-2) and projector. The resulting system would match GPT-4 on most benchmarks at lower inference cost (DeepSeek-V3's 37B active vs GPT-4's inferred 280B active).

**What are the risks of treating closed-model architectures as "unknown black boxes" in production?** Three risks: (1) Provider drift — silent model updates can break your system; pin versions to mitigate. (2) Capability regressions — a new model version may be worse on your specific task; maintain regression evals. (3) Vendor lock-in — if your system depends on a closed model's specific behavior, switching is hard; use open models or maintain multi-provider abstraction.

**How does source-labelling apply to closed-model architectural claims?** Every claim must be tagged: Officially Confirmed (rare — only what the provider states), Research-Backed (published analysis), Strongly Inferred (technical evidence but no confirmation), or Speculative (insufficient evidence). For GPT-4, most claims are Strongly Inferred. Mixing these levels without tagging misleads readers.

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[GPT-4 Technical Report]] — the official paper.
- [[Claude Architecture]] — comparison to Claude.
- [[Gemini Architecture]] — comparison to Gemini.
- [[Opus 5 Architecture]] — the 2026 closed-source tier.
- [[Llama Family Architecture]] — open-weights alternative.
- [[DeepSeek-V2 and V3]] — open MoE comparison.
- [[Mistral and Mixtral Architecture]] — the MoE model family that anchors the inference.
- [[Mixture of Experts]] — the MoE concept.
- [[Long-Context Architectures]] — the context-extension design space.
- [[Test-Time Compute Scaling]] — the o1/o3 reasoning recipe.
