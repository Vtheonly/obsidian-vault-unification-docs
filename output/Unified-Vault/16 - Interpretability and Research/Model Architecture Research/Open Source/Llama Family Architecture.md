---
title: Llama Family Architecture
type: concept
aliases: [Llama Family Architecture, Llama Architecture, Llama 1 2 3 4 Architecture]
tags: [model-architecture, llama, open-source, officially-confirmed]
sources: ["03 - Llama Family Architecture"]
created_index: 18
---

The Llama family (1, 2, 3, 4) is the most influential open-weights LLM lineage. Architecturally conservative — a decoder-only Transformer with pre-norm, RMSNorm, RoPE, SwiGLU, and no bias — Llama's design became the template for nearly all open-weights LLMs. Evolution across versions brought a larger context (2K → 128K), a better tokenizer (32K → 128K vocab), GQA adoption (Llama 2+), and MoE + multimodal (Llama 4).

> [!info] Source status
> All claims in this note are **officially confirmed** — documented in Meta's Llama papers (Llama 1, Llama 2), model cards (Llama 3, 3.1, 4), and technical blog posts.

## The Llama design philosophy

Llama's architecture is deliberately conservative. Rather than inventing new components, Meta combined the community's best-practice consensus into a single clean design:

- **Decoder-only** (not encoder-decoder) — simpler, supports generation.
- **Pre-norm** (not post-norm) — more stable training.
- **RMSNorm** (not LayerNorm) — slightly faster, same quality.
- **RoPE** (not sinusoidal or learned absolute) — better length generalization.
- **SwiGLU** (not GELU or ReLU) — better FFN quality.
- **No bias terms** — simpler, slightly faster.

This "best practices" approach made Llama a reference implementation. Most subsequent open-weights models (Mistral, Qwen, Gemma, DeepSeek) use variations of the same recipe. See [[Normalization Layers]] for norm placement, [[RoPE]] for positional encoding, and [[Feed-Forward Network]] for the FFN.

## Llama 1 (February 2023)

### Architecture

| Property            | 7B    | 13B   | 33B   | 65B   |
|---------------------|-------|-------|-------|-------|
| Layers              | 32    | 40    | 60    | 80    |
| d_model             | 4096  | 5120  | 6656  | 8192  |
| Heads               | 32    | 40    | 52    | 64    |
| d_head              | 128   | 128   | 128   | 128   |
| Context             | 2048  | 2048  | 2048  | 2048  |
| Vocab               | 32K   | 32K   | 32K   | 32K   |
| Attention           | MHA   | MHA   | MHA   | MHA   |
| Positional encoding | RoPE  | RoPE  | RoPE  | RoPE  |
| Norm                | RMSNorm | RMSNorm | RMSNorm | RMSNorm |
| Activation          | SwiGLU | SwiGLU | SwiGLU | SwiGLU |

### Training data

Llama 1 was trained on 4.7T tokens of public data (CommonCrawl, C4, GitHub, Wikipedia, Books, ArXiv, StackExchange), with a 2K context and no instruction tuning (base model).

### Key architectural choices

Llama 1 uses RoPE with base 10000, no bias in any projection, and pre-norm with RMSNorm, and runs efficient attention via `xformers`. See [[LLaMA]] for the full paper note.

## Llama 2 (July 2023)

### Architecture changes from Llama 1

Context grew from 2K to 4K (Llama 2), with 16K for Llama 2 long and some variants, and larger context (16K) for chat variants. The 70B model moved to GQA (8 KV head groups, reducing KV cache by 8×). Chat variants (Llama-2-Chat) added RLHF.

| Property | 7B        | 13B       | 70B       |
|----------|-----------|-----------|-----------|
| Layers    | 32        | 40        | 80        |
| d_model   | 4096      | 5120      | 8192      |
| Heads     | 32        | 40        | 64        |
| KV heads  | 32 (MHA)  | 40 (MHA)  | 8 (GQA)   |
| Context   | 4096      | 4096      | 4096      |
| Vocab     | 32K       | 32K       | 32K       |

### Training data

Llama 2 was trained on 2.0T tokens — less than Llama 1's 4.7T, because Meta found diminishing returns beyond this for the architecture. Chat variants added instruction-following data and RLHF with safety and helpfulness rewards.

### Key results

Llama 2 70B Chat was the first open-weights model to approach GPT-3.5 quality, making it the default for open-source chatbot deployment in 2023.

## Llama 3 (April 2024) and Llama 3.1 (July 2024)

### Architecture changes from Llama 2

Context grew from 4K to 8K (Llama 3) and then 128K (Llama 3.1). GQA was extended to all sizes (not just 70B). A new tokenizer brought a 128K vocabulary (up from 32K), BPE-based, with better multilingual and code support. Training data grew to 15T tokens (up from 2T), and the RoPE base increased to 500000 for better long-context extrapolation.

| Property | 8B       | 70B      | 405B     |
|----------|----------|----------|----------|
| Layers    | 32       | 80       | 126      |
| d_model   | 4096     | 8192     | 16384    |
| Heads     | 32       | 64       | 128      |
| KV heads  | 8 (GQA)  | 8 (GQA)  | 8 (GQA)  |
| Context   | 128K     | 128K     | 128K     |
| Vocab     | 128K     | 128K     | 128K     |

### Training data

15T tokens of curated data (significantly more and better filtered than Llama 2), with multilingual coverage (50+ languages with significant data), code data from GitHub, and mathematical and scientific content.

### Key results

Llama 3.1 405B was the first open-weights model to match GPT-4 on many benchmarks. This was a watershed moment — it proved that open-source could match closed-source at the frontier. See [[GPT-4 Technical Report]] for the closed-source reference point.

### The 128K context extension

Llama 3.1 extended context from 8K to 128K via RoPE scaling (YaRN-style, with carefully tuned parameters), continued pretraining on long-context data, and an attention implementation that handles 128K efficiently (FlashAttention-2/3). See [[YaRN and NTK-Aware Scaling]] and [[FlashAttention-2 and FlashAttention-3]].

## Llama 4 (2025)

> [!info] Source status
> Llama 4 architecture details are **officially confirmed** in Meta's announcements, but full technical details may not be completely published. This note reflects publicly available information as of mid-2025.

Llama 4 is the first Llama to use mixture-of-experts, adds native multimodal (vision-language) capability, and uses an early-fusion architecture (vision and text processed together from the start). It represents Meta's shift from the conservative dense architecture to MoE + multimodal, aligning with the broader 2025 trend toward MoE + hybrid architectures. See [[Mixture of Experts]].

## Why the Llama architecture became standard

### Best-practices consensus

Llama's components (pre-norm, RMSNorm, RoPE, SwiGLU, no bias) were each the community's best-practice choice by 2023. Combining them gave a clean, well-understood design.

### Open weights enabled adoption

Because the weights were open, researchers could study, modify, and build on Llama. This drove adoption of the architectural choices — fine-tunes and derivatives inherited the architecture.

### Simplicity

The architecture is simple — no exotic components, no complex routing, no special training tricks. This makes it easy to implement, debug, and serve.

### Proven at scale

Llama 1, 2, 3, and 4 demonstrated that the architecture scales predictably from 7B to 405B+. The scaling laws are well-understood, giving confidence in the design. See [[Scaling Laws (Kaplan and Chinchilla)]].

## Comparison to other families

| Family   | Architecture highlights                                    |
|----------|------------------------------------------------------------|
| Llama    | Conservative: MHA/GQA, RoPE, SwiGLU, RMSNorm              |
| Mistral  | + Sliding window attention (Mistral 7B)                    |
| Qwen     | + GQA, larger vocab, multilingual focus                    |
| DeepSeek | + MLA (V2+), MoE (V2+), auxiliary-loss-free balancing (V3) |
| Gemma    | + GQA, larger vocab, RoPE with longer base                 |

Llama is the most conservative; other families add innovations on top of the Llama baseline. See [[Llama Mistral Qwen Comparison]] for the cross-family view.

## Impact and legacy

Llama's architectural influence shows in four ways. It standardized open-weights LLM design: nearly every open-weights LLM uses Llama's architectural choices (with minor variations). It proved Chinchilla scaling works: Llama's "train smaller models on more data" strategy validated Chinchilla's predictions and became standard. It enabled the open-source ecosystem: without Llama's open weights, the fine-tune, quantization, and serving ecosystems wouldn't exist. And it pushed closed-source labs: Llama 3.1 405B matching GPT-4 put competitive pressure on OpenAI and Anthropic, accelerating their development.

For AI engineers, Llama is the reference architecture. If you're building a custom LLM or understanding how open-weights models work, Llama's design is the starting point.

## Further reading

Primary sources for the claims in this note:

- Llama 1 paper: arXiv:2302.13971 — see [[LLaMA]]
- Llama 2 paper: arXiv:2307.09288
- Llama 3 model card: huggingface.co/meta-llama/Meta-Llama-3-8B
- [[Llama Mistral Qwen Comparison]] — comparison note.

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[LLaMA]] — the Llama 1 paper note.
- [[Mistral and Mixtral Architecture]] — SWA + MoE on the Llama baseline.
- [[Qwen Family Architecture]] — the multilingual branch.
- [[Gemma Architecture]] — Google's variation on the template.
- [[Llama Mistral Qwen Comparison]] — cross-family comparison.
- [[DeepSeek Architecture]] — the MLA/MoE branch of the family tree.
- [[GQA MQA and MLA]] — attention variants across Llama generations.
- [[RoPE]] — the positional encoding throughout.
- [[Normalization Layers]] — RMSNorm vs LayerNorm.
- [[Feed-Forward Network]] — the SwiGLU-gated FFN.
- [[Scaling Laws (Kaplan and Chinchilla)]] — the scaling story behind the training recipe.
