---
title: MiniMax-01
type: concept
aliases: [MiniMax-01, MiniMax 01, MiniMax-Text-01]
tags: [paper, minimax-01, hybrid, lightning-attention, linear-attention, moe, long-context]
sources:
  - "43 - MiniMax-01 2025"
created_index: 55
---

MiniMax-01 is a hybrid linear-attention + Transformer MoE model released in January 2025 by MiniMax, a Chinese AI startup. With 456B total parameters and 45.9B active parameters under top-2 expert routing, it was the first open-weights model to natively support 1M-token context in production. The architecture uses Lightning Attention — a linear-attention variant optimized for hardware efficiency — for roughly 87% of attention layers and standard softmax attention for the remaining ~13%. The key insight is that linear attention can scale to million-token contexts efficiently, but a few softmax attention layers are still needed for quality: MiniMax-01 demonstrated that linear-attention hybrids can match pure-Transformer quality at scale while enabling 1M-token inference at reasonable cost.

## Citation

MiniMax (2025). *MiniMax-01: Scaling Foundation Models with Lightning Attention*. arXiv:2501.08493. (Technical report from MiniMax, January 2025.)

## The problem being solved

By late 2024, the long-context frontier was:

- **Gemini 1.5 Pro** (Google): 1M tokens, closed-source, native multimodal. Architecture not publicly disclosed.
- **Claude 3.5** (Anthropic): 200K tokens, closed-source. Architecture not disclosed.
- **GPT-4 Turbo** (OpenAI): 128K tokens, closed-source. Architecture not disclosed.
- **Llama 3.1** (Meta): 128K tokens, open-weights, but quality degrades significantly at the longest contexts (the "needle in a haystack" failure rate at 128K is ~10–30% depending on the test).
- **Jamba** (AI21): 256K tokens, hybrid SSM-Transformer, open-weights.

The open-source community needed a model that could genuinely handle 1M tokens with good quality, and three challenges stood in the way:

1. **Attention's $O(n^2)$ scaling** — at 1M tokens, the attention matrix is $10^{12}$ entries. Even [[17 - Papers/Efficiency/FlashAttention|FlashAttention]] can't make this practical.
2. **KV cache memory** — at 1M tokens, the KV cache for a 70B model is ~100 GB. Most GPUs can't hold this.
3. **Quality degradation** — naive context extension (YaRN, NTK) works up to ~8×, but quality degrades beyond that. Going from 8K to 1M is 128× — well beyond naive extension.

MiniMax-01 addressed all three with a hybrid linear-attention + Transformer architecture.

## The architecture

MiniMax-01's stack:

- **456B total parameters, 45.9B active** (MoE with 32 experts, top-2 routing).
- **80 layers**, of which 7 are softmax attention and 73 are Lightning Attention (linear attention).
- **Lightning Attention**: a linear-attention variant optimized for hardware efficiency. The key idea: linear attention computes $O_t = (Q_t \cdot K^T) V$ where the "kernel" $Q \cdot K^T$ can be computed in linear time via a right-product trick.
- **RoPE positional encoding** on the softmax attention layers.
- **SwiGLU** feed-forward, **RMSNorm**.
- **1M token context** natively (trained at 1M, not extended from shorter).

### Lightning attention

Standard (softmax) attention:

$$
O = \text{softmax}(QK^T) V
$$

The softmax makes this $O(n^2)$ — you need to compute the full $n \times n$ matrix before normalization.

Linear attention removes the softmax:

$$
O = Q (K^T V)
$$

This can be computed as $Q (K^T V)$ instead of $(QK^T) V$ — same math, but the inner product $K^T V$ is $d \times d$ instead of $n \times n$. For $n \gg d$ (long sequences), this is a massive speedup: $O(n d^2)$ instead of $O(n^2 d)$.

The catch: without softmax, the attention weights can be unbounded, leading to instability. Linear attention variants address this with kernel tricks (e.g., $Q' = \phi(Q)$, $K' = \phi(K)$ where $\phi$ is a non-linear feature map) but quality is typically worse than softmax attention. The general technique is covered in [[Linear Attention]].

Lightning Attention is MiniMax's variant: it uses a specific $\phi$ (ELU + 1) and is implemented with block-wise tiling for hardware efficiency. The key innovation is the tiling: instead of materializing the full $K^T V$ product, it's computed in blocks that fit in SRAM, similar to FlashAttention's tiling. This makes linear attention practical at scale.

### Why the hybrid

Linear attention alone has quality issues — the lack of softmax normalization means the model can't selectively ignore irrelevant tokens as well. Pure linear attention models (e.g., [[Performer]]) underperform Transformers on ICL and recall.

MiniMax's solution: use linear attention for most layers (efficiency) but keep a few softmax attention layers (7 out of 80) for quality. The softmax layers act as "anchors" that preserve the model's ability to do exact recall and ICL.

This is conceptually similar to [[Jamba]]'s 1:7 Mamba-to-Transformer ratio, but with linear attention instead of Mamba. The differences:

- **Jamba**: Mamba (selective SSM) + Transformer.
- **MiniMax-01**: Lightning Attention (linear attention) + Transformer.

Both are "mostly linear-time, occasionally softmax" hybrids. The difference is the linear-time primitive (SSM vs linear attention), which have different mathematical properties.

## Empirical results

On standard benchmarks (4K–8K context):

| Benchmark            | MiniMax-01 (456B/45.9B) | Llama 3.1 405B | Claude 3.5 Sonnet |
|----------------------|-------------------------|----------------|-------------------|
| MMLU                 | 85.2                    | 85.0           | 88.3              |
| GPQA                 | 53.6                    | 51.1           | 59.4              |
| MATH                 | 67.2                    | 73.8           | 71.1              |
| HumanEval            | 85.0                    | 89.0           | 92.0              |

Quality is competitive with Llama 3.1 405B (slightly behind on coding/math, slightly ahead on knowledge). Not SOTA, but solid.

The real differentiator is long-context:

| Context length | MiniMax-01 needle-in-haystack | Llama 3.1 405B | Gemini 1.5 Pro |
|----------------|-------------------------------|----------------|-----------------|
| 32K            | 100%                          | 99%            | 100%            |
| 128K           | 100%                          | 92%            | 100%            |
| 512K           | 99%                           | N/A            | 99%             |
| 1M             | 96%                           | N/A            | 97%             |

MiniMax-01 maintains near-perfect needle-in-haystack performance up to 1M tokens — competitive with Gemini 1.5 Pro and far ahead of any other open-weights model.

## Training details

Training used **15T tokens** of data (English, Chinese, code). Crucially, the model was **pretrained at 1M context** — not extended from shorter. This is a key decision: the model learned to handle long contexts during pretraining, not via post-hoc extension (YaRN, NTK).

Lightning Attention training required custom CUDA kernels — standard PyTorch/Triton implementations were too slow. MiniMax open-sourced these kernels, making them reusable for other labs. For **MoE load balancing**, MiniMax used a "group-wise balanced loss" to ensure experts are used evenly. **Training cost** is estimated at ~$50–100M (large but not unprecedented for a frontier model).

## Why MiniMax-01 mattered

MiniMax-01 mattered for four reasons. It was the **first open 1M-token model**: prior to MiniMax-01, 1M context was the exclusive domain of closed-source Gemini 1.5 Pro, and MiniMax-01 made million-token inference available to anyone with the GPU budget. It **validated linear-attention hybrids at scale**: Jamba (Mamba + Transformer) was the first production hybrid, and MiniMax-01 (linear attention + Transformer) showed that linear attention — previously considered inferior to SSMs — can also work in production hybrids. It **open-sourced the Lightning Attention kernels**, so other labs can build on them. And it **pushed the open-weights context frontier**: 1M context is now an open-weights capability, putting pressure on closed-source models to differentiate in other ways (multimodal, reasoning, agentic).

## Comparison with other hybrids

| Aspect                | Jamba (2024)             | MiniMax-01 (2025)         | Kimi Linear (2025)        |
|-----------------------|--------------------------|---------------------------|---------------------------|
| Linear primitive      | Mamba (selective SSM)    | Lightning Attention       | Linear attention (custom) |
| Attention ratio       | 1:7 (12.5% attention)    | 7:80 (8.75% attention)    | Hybrid (varies per layer) |
| Total parameters      | 52B                      | 456B                      | ~MoE, not disclosed       |
| Active parameters     | 12B (MoE)                | 45.9B (MoE)               | Not disclosed             |
| Max context           | 256K                     | 1M                        | 2M+                       |
| Positional encoding   | RoPE                     | RoPE                      | RoPE (modified)           |
| Open weights          | Yes                      | Yes                       | Yes                       |
| Notable for           | First production hybrid  | First open 1M context     | Largest open context      |

The three hybrid models represent different points in the design space: Jamba proved hybrids work; MiniMax-01 pushed to 1M context; Kimi Linear pushed to 2M+ with even more aggressive linearization.

## When to use MiniMax-01

MiniMax-01 shines in genuinely long-context settings, where the hybrid architecture pays off:

- **Genuinely long contexts (>256K tokens)**: this is where MiniMax-01 shines. Pure Transformers struggle; Jamba maxes out at 256K; Gemini 1.5 Pro is closed-source.
- **Document-heavy applications**: legal contracts, scientific papers, codebases — anywhere you need to feed entire documents or corpora as context.
- **Multi-document reasoning**: comparing or synthesizing across many long documents.
- **Long-form generation**: writing long documents where the model needs to maintain coherence over many tokens.

## When not to use MiniMax-01

- **Short contexts (<32K)**: pure Transformers (Llama 3.1, Qwen 2.5) are typically faster and have richer ecosystems.
- **Multimodal applications**: MiniMax-01 is text-only.
- **Coding tasks**: Llama 3.1 405B and Claude 3.5 Sonnet are stronger on coding benchmarks.
- **Math reasoning**: Llama 3.1 405B and DeepSeek-R1 are stronger on math.
- **Tooling ecosystem**: HuggingFace, vLLM, TGI support for MiniMax-01 is improving but less mature than for Llama.

## Production patterns

For RAG with long documents, feed the entire document as context (no chunking needed) — MiniMax-01 can retrieve facts from anywhere in a 1M-token document, a pattern that removes most of the machinery of [[RAG]] pipelines. For agentic workflows, the long context can hold the entire conversation history, agent state, and tool outputs — no summarization or truncation needed. For batch processing, process multiple long documents in parallel; the MoE keeps per-token inference cost reasonable (~$0.10 per million input tokens for the API).

> [!tip]
> For evaluation, always test on needle-in-haystack at your target context length. MiniMax-01's quality at 1M is high but not perfect — verify it works for your use case.

## Common pitfalls

- **Assuming linear attention = same quality as softmax**: MiniMax-01's quality is competitive with pure Transformers but slightly behind on some benchmarks (coding, math). Don't expect SOTA on everything.
- **Ignoring the MoE routing overhead**: at small batch sizes, the MoE routing adds latency. For low-latency single-user use, a smaller dense model may be faster.
- **Forgetting that 1M context needs 1M tokens**: just because the model supports 1M context doesn't mean every query needs 1M tokens. Use the context you need, not the maximum.
- **Expecting Gemini-level multimodal**: MiniMax-01 is text-only. Don't try to use it for vision, audio, or video.
- **Miscalculating cost**: 1M input tokens at $0.10/M = $0.10 per query. That's cheap per query but adds up at scale — 10M queries/month = $1M/month.

## Variants and successors

MiniMax-Text-01 is the text-only model described here. MiniMax-VL-01 is a vision-language variant (separate release) that uses a different architecture for vision. A MiniMax-02, if released, is expected to improve quality and possibly extend context further.

## Why this matters for AI

Open-weights 1M context is now real: this changes the design space for RAG, agents, and document processing — applications that previously required chunking and retrieval can now feed entire corpora as context. Linear attention is production-viable: MiniMax-01 proved that linear attention (not just SSMs) can be the "linear primitive" in a hybrid, which opens the design space for future hybrids. The hybrid recipe is consolidating: Jamba (Mamba + Transformer), MiniMax-01 (linear attention + Transformer), Kimi Linear (linear attention + Transformer) — the pattern is "mostly linear, occasionally softmax", and this is becoming the standard for long-context models. Finally, this puts pressure on closed-source long-context: Gemini's 1M context was a differentiator, and with MiniMax-01 and Kimi Linear offering open 1M+ context, closed models need to differentiate in other ways (multimodal, reasoning, agentic capabilities).

## Production implications

- **Evaluate MiniMax-01 for any long-context use case** (>256K tokens). It may be the best open-weights option.
- **Benchmark on your actual workload**: MiniMax-01's quality varies by task. Test on your specific long-context tasks before committing.
- **Watch the tooling**: [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] have added MiniMax-01 support; HuggingFace Transformers support is improving. Check compatibility before deploying.
- **Cost model**: 1M input tokens at $0.10/M = $0.10 per query. Compare to closed-source alternatives (Gemini 1.5 Pro: ~$1.25/M input tokens).
- **For multimodal long-context**: no open option exists as of 2026. Use Gemini 1.5 Pro or Claude 3.5 Sonnet if you need vision + long context.

## Further reading

- MiniMax (2025), *MiniMax-01: Scaling Foundation Models with Lightning Attention*. arXiv:2501.08493.
- Katharopoulos et al. (2020), *Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention*. (The original linear attention paper.)
- Kasai et al. (2021), *Finetuning Pretrained Transformers into RNNs*. (Linear attention variants.)
- Jamba (AI21, 2024), *Hybrid Transformer-Mamba Language Model*. (The competing hybrid approach.)

## Interview questions

**Q: What is Lightning Attention and how does it differ from standard softmax attention?**

A: Lightning Attention is MiniMax's variant of linear attention. Standard softmax attention computes $O = \text{softmax}(QK^T) V$, which is $O(n^2 d)$ because the softmax requires the full $n \times n$ matrix. Linear attention removes the softmax: $O = Q (K^T V)$, which can be computed in $O(n d^2)$ time because the inner product $K^T V$ is $d \times d$ instead of $n \times n$. For long sequences ($n \gg d$), this is a massive speedup. Lightning Attention uses a specific feature map $\phi$ (ELU + 1) and is implemented with block-wise tiling similar to FlashAttention, making it hardware-efficient. The catch: without softmax normalization, quality is typically worse than standard attention — hence the hybrid (a few softmax layers for quality).

**Q: Why does MiniMax-01 use a hybrid of linear and softmax attention?**

A: Linear attention is efficient (linear time) but has quality issues — the lack of softmax normalization means the model can't selectively ignore irrelevant tokens as well. Pure linear attention models underperform Transformers on in-context learning and recall. MiniMax's solution: use linear attention for ~87% of layers (efficiency) and softmax attention for ~13% (quality). The softmax layers act as "anchors" that preserve ICL and recall ability. This is conceptually similar to Jamba's Mamba-to-Transformer ratio but with linear attention as the linear primitive. The result: MiniMax-01 can handle 1M-token contexts efficiently while maintaining competitive quality.

**Q: How does MiniMax-01 achieve 1M-token context?**

A: Three factors. (1) **Linear attention for most layers** — Lightning Attention's $O(n d^2)$ scaling means long contexts are computationally feasible. (2) **Small KV cache** — only 7 of 80 layers have softmax attention, so the KV cache is ~8× smaller than a pure Transformer's. (3) **Native 1M training** — the model was pretrained at 1M context, not extended from shorter via YaRN/NTK. This means the model learned to handle long contexts during pretraining, not as a post-hoc patch. The combination makes 1M-token inference feasible on commodity hardware.

**Q: How does MiniMax-01 compare to Jamba as a hybrid architecture?**

A: Both are "mostly linear, occasionally softmax" hybrids, but with different linear primitives. Jamba uses Mamba (selective state-space model); MiniMax-01 uses Lightning Attention (linear attention). Mamba and linear attention have different mathematical properties — Mamba is input-dependent (selective), linear attention is not (without modifications). MiniMax-01 also has a lower attention ratio (8.75% vs Jamba's 12.5%) and is much larger (456B/45.9B vs 52B/12B). MiniMax-01 also natively supports 1M context (vs Jamba's 256K) because it was trained at 1M from the start.

**Q: When would you choose MiniMax-01 over Llama 3.1 or Gemini 1.5 Pro?**

A: Choose MiniMax-01 when: (1) you need open-weights (vs Gemini's closed), (2) you need genuinely long context (>256K tokens, where Llama 3.1's quality degrades), (3) you need 1M-token context and don't want to pay Gemini's closed-source pricing. Don't choose MiniMax-01 when: (1) you need multimodal (it's text-only), (2) you need SOTA coding/math quality (Llama 3.1 405B and Claude 3.5 are stronger), (3) you need short-context latency (smaller dense models are faster), (4) you need mature tooling (Llama's ecosystem is more developed).

**Q: What did MiniMax-01 prove about linear attention?**

A: Two things. (1) **Linear attention is production-viable at scale** — prior to MiniMax-01, linear attention was considered inferior to SSMs for production hybrids. MiniMax-01 showed that with the right implementation (Lightning Attention's tiling) and the right hybrid ratio (87% linear, 13% softmax), linear attention can match Mamba-based hybrids. (2) **Linear attention can scale to 1M context** — MiniMax-01 was the first open-weights model with native 1M context, and it used linear attention to get there. This opened the design space for future long-context hybrids (Kimi Linear, etc.).

## See also

- [[Papers MOC]] — the papers hub for this note.
- [[Jamba]] — the competing hybrid (Mamba + Transformer) and the first production hybrid.
- [[Kimi Linear]] — the successor pushing to 2M+ context.
- [[Mamba]] — the SSM alternative to linear attention.
- [[Mamba-2]], [[H3]], [[Based]] — the wider SSM and linear-attention family this note belongs to.
- [[Linear Attention]] — the topical deep dive on linear attention.
- [[Performer]] — the earlier pure linear-attention model that underperformed on ICL and recall.
- [[Mixture of Experts]] — the routing technique stacked on top of the hybrid backbone.
- [[Long-Context Architectures]] — MiniMax-01 is a key example.
- [[RWKV and RetNet]] — other linear-time approaches.
- [[SSMs Mamba and Frontiers]] — the research-frontier overview of this model family.
- [[RAG]] — long-document retrieval without chunking.
- [[DeepSeek-R1]] — the stronger math-reasoning alternative referenced in use-case comparisons.
- [[MiniMax 3 Architecture]] — later generations from the same lab.
