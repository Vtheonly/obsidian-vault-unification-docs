---
title: Jamba
type: concept
aliases: [Jamba, AI21 Jamba, Hybrid SSM-Transformer, Jamba 2024]
tags: [paper, jamba, hybrid, mamba, transformer, ai21, production, moe, long-context]
sources:
  - "41 - Jamba 2024"
created_index: 51
---

Jamba is the first production-grade hybrid SSM-Transformer model. Its architecture interleaves Mamba (selective state-space) blocks with Transformer (attention + MLP) blocks in a 1:7 ratio: every 8 blocks, 1 is a Transformer block and 7 are Mamba blocks. The combination aims to capture Mamba's linear-time long-context efficiency while preserving the Transformer's in-context learning and recall ability. With 52B total parameters (12B active due to MoE) and a 256K context window, Jamba demonstrated that hybrids can compete with pure Transformers on quality while being significantly faster on long contexts, and it established the "hybrid is the practical answer" consensus that influenced subsequent models (Falcon-Mamba, Zamba, Jamba-1.5).

## Citation

Lieber, O., Lenz, B., Bata, H., et al. (AI21 Labs) (2024). *Jamba: A Hybrid Transformer-Mamba Language Model*. arXiv:2403.19887.

## The problem being solved

By late 2023, the architecture landscape had two competing paradigms:

- **Transformers** (GPT, Llama, Mistral, Qwen) — excellent quality, in-context learning, and recall; but $O(n^2)$ attention makes long context expensive.
- **State Space Models** ([[Mamba]], Mamba-2) — linear-time inference, theoretically unlimited context, excellent on long sequences; but empirically weaker than Transformers on in-context learning, recall, and certain reasoning tasks.

Researchers noticed that Transformers and SSMs have complementary strengths:

- **Attention** is good at: in-context learning (ICL), exact recall, copying patterns, "induction head" behavior.
- **SSMs** are good at: long-context throughput, memory efficiency, handling very long sequences where attention's $O(n^2)$ blows up.

The natural question: can we get the best of both by **interleaving** them? A few layers of attention for ICL/recall, mostly SSM layers for efficiency. Jamba was the first model to demonstrate this at production scale (52B parameters, trained on 1.5T tokens).

## The architecture

Jamba's stack (per 8-block group):

```text
[Mamba] [Mamba] [Mamba] [Mamba] [Transformer] [Mamba] [Mamba] [Mamba]
                                               ↑
                                          1 in 8 is attention
```

Concretely, 7 Mamba blocks plus 1 Transformer block per group, with 8 groups (so 56 Mamba blocks + 8 Transformer blocks = 64 total). Some blocks contain MoE (Mixture-of-Experts) feed-forward layers. Total parameters are 52B, with 12B active parameters per token (due to MoE with 16 experts, top-2 routing).

### Why this ratio

The 1:7 attention-to-SSM ratio is empirical. AI21 tried:

- 1:3 (too much attention — slow on long context).
- 1:15 (too little attention — degraded ICL).
- 1:7 (sweet spot — preserved ICL while keeping long-context fast).

The placement (5th block in each group, not the 1st or 8th) was also empirical — placing attention early helps ICL but hurts efficiency; placing it late preserves efficiency but loses early-layer attention. The 5th position balanced both.

### Mamba blocks

Each Mamba block is a selective state-space layer (Mamba-1 architecture):

$$
h_t = A \cdot h_{t-1} + B \cdot x_t, \quad y_t = C \cdot h_t
$$

where $A, B, C$ are input-dependent (selective). This gives linear-time inference and constant memory per step.

### Transformer blocks

Each Transformer block is a standard attention + MLP layer with RoPE positional encoding. This is the "anchor" that preserves ICL and recall ability.

### Mixture of experts

About 1 in 2 layers uses MoE for the feed-forward network. Each MoE layer has 16 experts with top-2 routing. The total parameter count is 52B but only 12B active per token — this gives the quality of a 52B dense model with the inference cost of a 12B model.

## Why hybrid works

The intuition: different layers do different things.

- **Early layers** establish basic representations (token embeddings, local context). SSMs handle this fine.
- **Middle layers** do most of the "interesting" computation: ICL, recall, induction heads, syntactic/semantic processing. Attention helps here.
- **Late layers** integrate and produce output. SSMs handle this fine.

By sprinkling a few attention layers across the depth, the model gets the ICL/recall benefits of attention without paying $O(n^2)$ on every layer. The SSM layers handle the bulk of the sequence processing in linear time.

Empirically, Jamba's quality on standard benchmarks matched Llama-2 70B and Mistral 7B while being faster on long contexts.

## Empirical results

| Benchmark                  | Jamba (52B/12B) | Llama-2 70B | Mixtral 8x7B |
|----------------------------|-----------------|-------------|--------------|
| MMLU (5-shot)              | 67.4            | 68.9        | 71.3         |
| ARC-Challenge              | 71.6            | 67.6        | 70.1         |
| HellaSwag                  | 88.1            | 85.3        | 87.3         |
| GSM8K (5-shot)             | 53.4            | 56.8        | 59.2         |
| Long-context (256K)        | Strong          | N/A (4K)    | N/A (32K)    |

Quality is competitive with similar-size Transformers, not strictly better. The win is in **throughput on long contexts**:

| Sequence length | Jamba throughput (tok/s, A100) | Llama-2 70B throughput |
|-----------------|--------------------------------|------------------------|
| 4K              | 2,100                          | 2,400                  |
| 32K             | 1,800                          | 350 (5× slower)        |
| 128K            | 1,200                          | OOM                    |
| 256K            | 800                            | OOM                    |

Jamba's throughput degrades much more gracefully with sequence length — exactly the hybrid promise.

## Why Jamba mattered

Jamba was the **first production hybrid at scale**: it proved that SSM-Transformer hybrids can match pure-Transformer quality while winning on long-context efficiency, which killed the "SSMs aren't ready for production" narrative. It **established the hybrid recipe** — 1:7 attention-to-SSM ratio, MoE on top, 256K context — and subsequent hybrids (Falcon-Mamba, Zamba, Jamba-1.5, MiniMax-01) follow variations of this recipe. It **showed MoE + hybrid is compatible**: you can stack MoE on top of a hybrid SSM-Transformer backbone, which opened the design space for "MoE + linear attention + Transformer" combinations. And its **weights are open** (Apache 2.0), enabling research on production hybrids — important because most SSM research was at small scale, and Jamba let researchers study a 52B hybrid.

## Comparison with pure SSMs and pure Transformers

| Aspect                | Pure Transformer (Llama 3) | Pure SSM (Mamba-2) | Hybrid (Jamba) |
|-----------------------|---------------------------|--------------------|-----------------|
| Quality on standard benchmarks | Best              | 5–15% behind       | ~Transformer    |
| Long-context throughput | $O(n^2)$, degrades       | $O(n)$, constant   | $O(n)$ (mostly) |
| In-context learning | Strong                     | Weak (notably)     | Strong          |
| Exact recall        | Strong                     | Weak               | Strong          |
| Memory (KV cache)   | $O(n)$                     | $O(1)$ per step    | $O(n/8)$ (8× less) |
| Production maturity | Best                       | Emerging           | Production      |

The hybrid wins on long-context efficiency while matching Transformer quality. It doesn't beat Transformers on quality, but it doesn't have to — the use case is long-context applications where the Transformer's $O(n^2)$ is the bottleneck.

## Production patterns

Jamba shines when the context is genuinely long. For **long-context RAG**, it comes into its own above ~32K tokens; for short contexts (<8K), pure Transformers are typically faster (Jamba's MoE has routing overhead). For **document summarization at scale**, feeding a 100K-token document and asking for a summary works in one pass with Jamba's 256K context, where pure Transformers require chunking. For **code understanding**, large codebases (100K+ tokens) can be attended to as a whole, while Transformers are limited by their context window. And for **cost-sensitive long-context**, if you're paying per token for inference, Jamba's higher throughput on long contexts translates directly to lower cost.

## When not to use Jamba

- **Short-context applications** (chatbots, simple Q&A): Transformer models are typically faster and have richer ecosystems.
- **Cutting-edge quality**: pure Transformers (GPT-4, Claude 3.5, Llama 3.1 405B) still lead on quality benchmarks. Jamba is competitive but not SOTA.
- **Multimodal applications**: Jamba is text-only; multimodal hybrids are emerging but not yet productionized.
- **Tooling ecosystem**: HuggingFace, vLLM, TGI, and other tools have less mature Jamba support compared to Transformers. This is improving but still a friction point.

## Variants and successors

**Jamba-1.5** (AI21, 2024) offers updated versions (Mini 12B active, Large 94B total / 12B active) with improved quality, 256K context, and faster inference. **Falcon-Mamba** (TII, 2024) is a pure Mamba model (no attention) at 7B that demonstrated pure SSMs can match Transformer quality at 7B scale. **Zamba** (Zyphra, 2024) is a hybrid with shared attention layers (one attention block reused across depth) for further efficiency. **MiniMax-01** (2025) is a hybrid at 456B total / 45.9B active, with even more attention layers and a custom linear attention variant — see [[MiniMax-01]].

## Why this matters for AI

Jamba established the production hybrid paradigm: the consensus as of 2024–2025 is that for long-context applications, hybrids are the practical answer — pure Transformers are too expensive, pure SSMs are too weak, and Jamba was the proof. The 1:7 ratio became a default: many subsequent hybrids use similar attention-to-SSM ratios, and while the exact ratio varies (1:6, 1:8, 1:10), the order of magnitude is established. MoE + hybrid became the new frontier: combining MoE (for parameter efficiency) with a hybrid SSM-Transformer backbone (for long-context efficiency) gives the best of all worlds, and Jamba pioneered this combination. Finally, long-context is the use case: Jamba's 256K context isn't a marketing number — it's a real capability that pure Transformers struggle to match at reasonable cost, and as applications demand longer contexts (codebases, scientific papers, multi-document reasoning), hybrids become more attractive.

## Production implications

- **For long-context applications (>32K tokens), evaluate hybrids**. Jamba-1.5, MiniMax-01, and future hybrids offer better throughput than pure Transformers at these lengths.
- **For short-context applications, stick with Transformers**. The MoE and SSM overhead doesn't pay off below 8K tokens.
- **Watch the tooling**: vLLM, TGI, and HuggingFace are adding hybrid support, but it lags Transformer support. Check compatibility before committing.
- **Evaluate on your actual workload**: hybrid advantages are workload-dependent. Don't assume Jamba will be faster — benchmark on your specific long-context tasks.
- **For multimodal long-context**: as of 2026, no production hybrid is multimodal. If you need vision + long context, you're stuck with Transformers (Claude 3.5, Gemini 2.5).

## Common pitfalls

- **Assuming hybrid = always better**: hybrids win on long context, not on everything. For short context, pure Transformers are often faster.
- **Ignoring the MoE overhead**: Jamba's 16-expert MoE has routing overhead. For small batches, this overhead can outweigh the SSM efficiency gain.
- **Confusing context length with context quality**: Jamba's 256K context is real, but quality may degrade at the longest lengths. Benchmark on your actual long-context tasks.
- **Forgetting that Jamba is text-only**: don't try to use it for vision or audio tasks.
- **Expecting Transformer-level tooling**: Jamba support in HuggingFace, vLLM, etc. is improving but not as mature as Llama/Mistral.

## Further reading

- Lieber et al. (2024), *Jamba: A Hybrid Transformer-Mamba Language Model*. arXiv:2403.19887.
- AI21 Labs, *Jamba-1.5 technical report* (2024).
- Gu & Dao (2023), *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*. (The Mamba foundation.)
- Falcon-Mamba (TII, 2024), *Pure Mamba at 7B scale*.

## Interview questions

**Q: Why does Jamba interleave Mamba and Transformer blocks in a 1:7 ratio?**

A: The 1:7 ratio is empirical — AI21 tried 1:3 (too much attention, slow on long context), 1:15 (too little attention, degraded ICL), and found 1:7 to be the sweet spot. The intuition: attention is needed for in-context learning and exact recall (induction-head behavior), but you don't need it on every layer. Sprinkling 1 attention layer per 8 blocks is enough to preserve ICL while keeping most layers as linear-time Mamba. The placement (5th block in each group) was also tuned — placing attention early helps ICL but hurts efficiency; placing it late preserves efficiency but loses early-layer attention.

**Q: What does Jamba's MoE add on top of the hybrid architecture?**

A: MoE gives parameter efficiency: Jamba has 52B total parameters but only 12B active per token (16 experts, top-2 routing). This means the model has the quality of a 52B dense model but the inference cost of a 12B model. Combined with the hybrid SSM-Transformer backbone, Jamba achieves: (a) Transformer-level quality, (b) SSM-level long-context efficiency, (c) MoE-level parameter efficiency. The three combine multiplicatively — Jamba's effective "quality per FLOP" is much higher than any single paradigm alone.

**Q: When is Jamba faster than a pure Transformer, and when is it slower?**

A: Jamba is faster on long contexts (>32K tokens) — its throughput degrades much more gracefully than a pure Transformer's $O(n^2)$ attention. At 256K tokens, Jamba runs at ~800 tok/s while Llama-2 70B runs out of memory. Jamba is slower on short contexts (<8K tokens) because: (a) MoE has routing overhead that doesn't pay off for small batches, (b) the SSM blocks have constant overhead per step that doesn't benefit from short sequences. The crossover point is typically around 8K–16K tokens.

**Q: What did Jamba prove about the SSM-Transformer debate?**

A: Jamba proved that hybrids can match pure-Transformer quality at production scale. Before Jamba, the debate was "SSMs are theoretically efficient but empirically weak; can they ever replace Transformers?" Jamba's answer: not replace, but complement. The consensus after Jamba is that for long-context applications, hybrids are the practical answer — pure Transformers are too expensive, pure SSMs are too weak. Subsequent hybrids (Jamba-1.5, Falcon-Mamba, Zamba, MiniMax-01) follow the Jamba recipe with variations.

**Q: Why didn't Jamba replace Transformers entirely?**

A: Three reasons. (1) **Quality** — pure Transformers (GPT-4, Claude 3.5, Llama 3.1 405B) still lead on quality benchmarks; hybrids are competitive but not SOTA. (2) **Tooling ecosystem** — HuggingFace, vLLM, TGI have less mature hybrid support; the Transformer ecosystem is huge. (3) **Short-context use cases** — most applications don't need 256K context; for short contexts, Transformers are faster and simpler. Jamba's niche is long-context applications where the Transformer's $O(n^2)$ is the bottleneck.

**Q: How does Jamba's KV cache compare to a pure Transformer's?**

A: Jamba's KV cache is ~8× smaller than a pure Transformer's at the same context length, because only 1 in 8 layers has attention (the other 7 are Mamba, which has constant memory per step). For a 256K context, this is the difference between fitting on a single 80GB GPU vs needing 8 GPUs. The reduced KV cache is one of Jamba's main practical advantages — it makes long-context inference feasible on commodity hardware.

## See also

- [[Papers MOC]] — the papers hub for this note.
- [[Mamba]] — the SSM foundation of the Mamba blocks.
- [[Mamba-2]] — the successor SSM used in later pure-SSM comparisons.
- [[MiniMax-01]] — a later hybrid at larger scale (456B / 45.9B active).
- [[Kimi Linear]] — a later hybrid with even more attention layers.
- [[H3]], [[Based]] — the wider SSM and linear-attention family this note belongs to.
- [[Mixture of Experts]] — the routing technique stacked on the hybrid backbone.
- [[Decoder-Only Architecture]] — Jamba is decoder-only.
- [[SSMs Mamba and Frontiers]] — the chapter-24 overview of this model family.
- [[Mamba-2 and Structured Attention]] — the SSM/attention unification that followed.
- [[RWKV and RetNet]] — other hybrid and linear-time approaches.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — serving tooling with maturing hybrid support.
