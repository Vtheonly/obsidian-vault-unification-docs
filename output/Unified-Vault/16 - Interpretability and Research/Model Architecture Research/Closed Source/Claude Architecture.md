---
title: Claude Architecture
type: concept
aliases: [Claude Architecture, Claude 3 3.5 4 Architecture]
tags: [model-architecture, claude, anthropic, closed-source, inferred]
sources: ["08 - Claude Architecture"]
created_index: 7
---

Anthropic has not officially disclosed Claude's architecture. Public statements indicate Claude uses a Transformer-based architecture with Constitutional AI (RLAIF) alignment, while specific details — parameter count, dense vs MoE, attention variants — are not publicly disclosed. This note summarizes what's known, what's inferred, and what's speculative, keeping the evidence levels separate throughout.

> [!warning] Source status
> **Most architectural claims about Claude are strongly inferred or speculative.** Anthropic has published the Constitutional AI method (see [[Constitutional AI]]) and general capabilities, but not Claude's specific architecture. Treat all architectural details as unverified.

## What's officially confirmed

Anthropic has publicly stated that Claude is a Transformer-based LLM (no specific architecture details); that Claude is trained with Constitutional AI (RLAIF) — Anthropic's alignment method; that Claude supports long context (200K tokens for Claude 3, 3.5; longer for some variants); that Claude 3.7+ has an "extended thinking" mode (controllable reasoning length); and that Claude is multimodal (vision-language) starting from Claude 3. The Constitutional AI paper describes the alignment method but not the base model architecture.

## What's strongly inferred

### Transformer-based, likely decoder-only

Evidence: all major LLMs since 2018 are Transformer-based; decoder-only is the dominant architecture (GPT, Llama, Mistral, Qwen all use it); and Claude's generation quality and style are consistent with decoder-only models. Inference: Claude is a decoder-only Transformer, likely with components similar to other frontier LLMs (pre-norm, RMSNorm, RoPE or similar, SwiGLU, GQA).

### Parameter scale (hundreds of billions)

Evidence: Claude 3 Opus's capability is comparable to GPT-4 (which is inferred to be ~1.7T MoE — see [[GPT-4 Inferred Architecture]]); Claude 3 Opus's pricing is similar to GPT-4's, suggesting similar compute per token; and Claude 3 Sonnet and Haiku are smaller (cheaper, faster), suggesting a family of sizes. Inference: Claude 3 Opus is likely in the 500B–1T+ parameter range (either dense or MoE). Sonnet and Haiku are smaller. Specific numbers are not confirmed.

### Possible mixture-of-experts

Evidence: Claude 3 Opus's cost is higher than a typical dense model of similar capability, similar to GPT-4; MoE has become standard for frontier-scale models (GPT-4 inferred, DeepSeek-V3 confirmed); and the capability-per-cost ratio suggests sparse computation. Inference: Claude 3 Opus may use MoE, but this is more speculative than for GPT-4. Anthropic has not indicated this.

### Constitutional AI as the alignment method

Evidence: Anthropic published the Constitutional AI paper; Anthropic's public statements emphasize the constitutional approach; and Claude's behavior (thoughtful, harm-averse) is consistent with constitutional alignment. Inference: Claude is aligned using Constitutional AI (RLAIF), possibly combined with traditional RLHF. The specific constitution (set of principles) is partially public but may have evolved.

### Long context via efficient attention

Evidence: Claude 3 supports 200K context, comparable to GPT-4 Turbo (128K) and Gemini 1.5 (1M) — see [[Gemini Architecture]]. This requires efficient attention techniques (sliding window, sparse attention, Ring Attention, or similar). Inference: Claude uses some form of efficient or distributed attention for long contexts. The specific technique is not disclosed. See [[Long-Context Architectures]] for the design space.

## What's speculative

### Specific parameter counts

Any specific number (e.g., "Claude 3 Opus is 820B parameters") is speculative. Anthropic has not disclosed any parameter counts.

### Specific architecture components

Whether Claude uses GQA, MLA, sliding window, or other specific techniques is not known. Inferences based on capability patterns are speculative.

### Training data

Claude's training data is not disclosed. Anthropic has stated it uses web data, books, and code, but specific datasets and proportions are not public.

### "Extended thinking" mechanism

Claude 3.7's extended thinking mode (similar to o1's reasoning) is not architecturally described. It could be RL-trained extended chain-of-thought (like o1/R1); a prompting technique that elicits longer reasoning; or a separate reasoning model combined with Claude. The mechanism is not officially disclosed. See [[Reasoning Models]] for the category and [[Test-Time Compute Scaling]] for the test-time-compute view.

## The Claude family

### Claude 1 (March 2023)

Anthropic's first public model. 9K context. Trained with Constitutional AI. Architecture not disclosed.

### Claude 2 (July 2023)

100K context (significant jump). Improved capability. Architecture not disclosed.

### Claude 3 (March 2024)

Three sizes: Haiku (small/fast), Sonnet (medium), Opus (large/frontier). 200K context. Multimodal (vision). Architecture not disclosed.

### Claude 3.5 (October 2024)

Improved Sonnet and Haiku. Computer use capability (can interact with desktops). Architecture not disclosed.

### Claude 3.7 (February 2025)

"Extended thinking" mode (controllable reasoning length). Hybrid reasoning: standard or extended thinking, selectable per request. Architecture not disclosed.

### Claude 4 (2025)

Latest generation. Improved capability and reasoning. Architecture not disclosed. The successor tier is covered in [[Opus 5 Architecture]].

## Why Anthropic doesn't disclose architecture

Anthropic's stated reasons are safety (Anthropic is a safety-focused company and believes architecture disclosure could enable misuse), competitive pressure (disclosure helps competitors), and research focus (Anthropic publishes research — Constitutional AI, interpretability — but keeps product architecture private). In practice, Anthropic is more transparent than OpenAI about research (publishing the Constitutional AI paper, interpretability research) but equally opaque about product architecture.

## Comparison to other closed models

| Model  | Architecture disclosure | Alignment method          |
|--------|-------------------------|---------------------------|
| GPT-4  | None                    | RLHF (outcome + process?) |
| Claude | None                    | Constitutional AI (RLAIF) |
| Gemini | Partial (papers)        | RLHF + other              |

Claude's distinctive feature is Constitutional AI — the alignment method is public even though the architecture isn't. See [[Gemini Architecture]] for the partial-disclosure case.

## Implications for AI engineers

### You don't need Claude's architecture

For most applications, Claude's API contract (input → output) is what matters, not the internal architecture. You can build production applications without knowing the architecture.

### Constitutional AI is the key differentiator

Claude's behavior (thoughtful, harm-averse, honest) is largely due to Constitutional AI, not the base architecture. Understanding Constitutional AI (see [[Constitutional AI]]) tells you more about Claude's behavior than architecture details would.

### Open models for architecture research

If you need architectural transparency (interpretability, custom training, architecture research), use open models. Claude is unsuitable for these purposes. See [[Llama Family Architecture]] for the open-weights path.

### Claude's strengths are behavioral

Claude is known for long, thoughtful responses; strong harm avoidance; good instruction following; and excellent coding and reasoning. These are behavioral properties, not architectural ones, and you can evaluate them through the API without knowing the architecture.

## Future disclosure

Anthropic is unlikely to disclose Claude's architecture in the near future. However, Anthropic publishes research on interpretability and alignment, which may eventually reveal architectural details; as open models catch up, the competitive sensitivity of disclosure decreases; and regulatory pressure (e.g., EU AI Act) may eventually require more transparency.

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[Constitutional AI]] — Claude's alignment method.
- [[GPT-4 Inferred Architecture]] — comparison to GPT-4.
- [[Gemini Architecture]] — comparison to Gemini.
- [[Opus 5 Architecture]] — the next-generation tier.
- [[Llama Family Architecture]] — open-weights alternative.
- [[Reasoning Models]] — the category extended thinking belongs to.
- [[Test-Time Compute Scaling]] — the test-time compute view of extended thinking.
- [[Long-Context Architectures]] — the efficient-attention design space behind 200K context.
