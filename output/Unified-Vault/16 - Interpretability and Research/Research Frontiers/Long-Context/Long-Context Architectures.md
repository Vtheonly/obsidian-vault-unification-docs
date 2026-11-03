---
title: Long-Context Architectures
type: concept
aliases: ["Long-Context Architectures", "Ring Attention", "Infini-Attention", "LongRoPE", "Million-Token Contexts"]
tags: [research, long-context, ring-attention, infini-attention, longrope, rope-scaling, hybrid-architectures]
sources: ["07 - Long-Context Architectures"]
created_index: 26
---

Long-context architectures extend LLMs to 1M+ token contexts. The four main approaches are Ring Attention (distribute attention across GPUs in a ring), Infini-Attention (compress old context into a fixed-size state), LongRoPE (extrapolate positional encodings to extreme lengths), and hybrid SSM/attention (use linear layers for long context). Each makes different trade-offs between quality, cost, and maximum context length, and together they enabled the 2024–2025 era of million-token LLMs. See [[Interpretability and Research MOC]] for the surrounding research area.

## The problem being solved

Standard LLMs have context limits of 4K–128K tokens, while many applications need more: full-codebase analysis (a large codebase can be 1M+ tokens), long-document research (scientific papers, legal cases, books), multi-hour video (transcripts + frames can be 1M+ tokens), and long conversations (a year of chat history).

Extending context is hard because attention is $O(N^2)$. For 1M tokens, the attention matrix has $10^{12}$ entries — completely infeasible. Long-context architectures solve this through various forms of sparsity, compression, or distribution.

## Ring Attention

Ring Attention (Liu et al., 2023) distributes the attention computation across multiple GPUs arranged in a ring. Each GPU holds a chunk of the sequence; attention is computed by passing KV blocks around the ring.

### How it works

The computation proceeds in four steps:

1. **Split the sequence**: each of P GPUs holds N/P tokens.
2. **Each GPU computes attention for its queries** against all keys/values.
3. **KV blocks are passed around the ring**: GPU 0 sends its KV to GPU 1, GPU 1 sends to GPU 2, etc.
4. **After P steps**, each GPU has seen all KV blocks and computed full attention.

The key insight: the communication (passing KV around the ring) overlaps with the computation (attention for the current KV block). This hides the communication latency.

### Trade-offs and adoption

On the plus side, Ring Attention computes exact attention (no approximation) and scales to any context length by adding GPUs. The costs: it requires many GPUs (P GPUs for N tokens, with each GPU holding N/P — for 1M tokens on 8 GPUs, each holds 125K, feasible but expensive), and it introduces communication overhead — if GPUs are slow to communicate, the ring stalls.

Ring Attention (or similar distributed attention) is used by frontier models for long contexts. Gemini 1.5's 1M context likely uses a variant (see [[Gemini Architecture]]).

## Infini-attention

Infini-Attention (Google, 2024) compresses old context into a fixed-size state, similar to an SSM. Recent context uses standard attention; old context is retrieved from the compressed state.

### How it works

The mechanism splits the context in two:

1. **Recent context** (last N tokens): standard attention.
2. **Old context** (beyond N): compressed into a fixed-size state via linear attention.
3. **The model attends to both**: recent tokens via attention, old tokens via the compressed state.

The compression is lossy — the state can't store all information from old context. But it's $O(1)$ per token (the state is fixed-size), so context length is unbounded.

### Trade-offs and adoption

Infini-attention's strengths are unbounded context length and $O(N)$ compute. The weaknesses: lossy compression (old information is degraded), and retrieval from the compressed state is weaker than from explicit KV.

Infini-attention is a Google research contribution. It influenced the design of models with "infinite" context, though production adoption is limited.

## LongRoPE

LongRoPE (Microsoft, 2024) extends RoPE (Rotary Position Embedding) to very long contexts (up to 2M tokens) by carefully scaling the positional frequencies.

### The problem with RoPE

RoPE encodes positions as rotations. Trained on N tokens, RoPE doesn't extrapolate well to >N tokens — the rotation angles become larger than seen in training, and the model behaves unpredictably (see [[RoPE]]).

### LongRoPE's solution

LongRoPE searches for the optimal scaling of RoPE frequencies for long contexts. Instead of a single scaling factor (like YaRN), it uses different scaling for different frequency bands:

- **Low frequencies** (long-range patterns): scale less aggressively.
- **High frequencies** (short-range patterns): scale more aggressively.

This non-uniform scaling allows extrapolation to 2M tokens from a model trained on 8K. The wider family of positional-extrapolation methods is covered in [[YaRN and NTK-Aware Scaling]].

### Trade-offs and adoption

LongRoPE's strengths: no architecture change, just a positional encoding tweak (easy to adopt), and it works with existing models (just change the RoPE implementation). The weaknesses: extrapolation quality degrades at extreme lengths (the model hasn't seen such long contexts during training), and it requires careful tuning of the scaling per model.

LongRoPE (and similar techniques like YaRN, NTK-aware scaling) is widely used to extend context for existing models. Llama 3's 128K context, Qwen 2.5's 128K context, and many community models use RoPE scaling (see [[Llama Family Architecture]] and [[Qwen Family Architecture]]).

## Hybrid SSM/attention

Hybrid architectures (Jamba, Kimi Linear, MiniMax-01) use SSM layers for most of the sequence mixing and attention layers for retrieval — the approach detailed from the SSM side in [[Mamba-2 and Structured Attention]] and [[Kimi Linear]].

### How it works

Most layers are SSMs (linear time, handling general context); a few layers are full attention (handling precise retrieval). The SSM layers make long context cheap; the attention layers maintain retrieval quality.

### Trade-offs and adoption

The approach gets $O(N)$ cost for most layers, enabling million-token contexts, and the attention layers preserve retrieval quality. It costs a more complex architecture (two kernel types), and there is still some retrieval quality loss vs. full attention.

Hybrid architectures are the 2025 trend for long-context models. Jamba, Zamba, MiniMax-01, and Kimi Linear all use this approach.

## Comparing the four approaches

| Approach           | Max Context | Quality     | Cost        | Complexity |
|--------------------|-------------|-------------|-------------|------------|
| Ring Attention     | Scales w/ GPUs | Exact    | $O(N^2)$ but distributed | High (distributed) |
| Infini-Attention   | Unbounded   | Lossy (old context) | $O(N)$ | Medium |
| LongRoPE           | ~2M         | Degrades at extremes | $O(N^2)$ but practical | Low (just RoPE tweak) |
| Hybrid SSM/Attn    | 1M+         | Near-attention | $O(N)$ | Medium |

## Why long context matters

### Enabling new applications

Million-token contexts enable applications that were previously impossible: full-codebase AI assistants (read the entire codebase, answer questions about any part), long-document research (upload 1000 papers, ask cross-document questions), video understanding (process multi-hour videos with full context), and long-term agents (agents that maintain context across days/weeks of operation).

### Reducing RAG dependence

With long enough context, you can put all relevant documents directly in the context, bypassing RAG retrieval. This is simpler (no retrieval pipeline) and often higher quality (no retrieval misses). The trade-off: long-context inference is expensive, so RAG remains cost-effective for high-volume applications (see [[RAG Pipeline Overview]]).

### Changing model design

Long-context requirements drive architectural innovation. The 2024–2025 trend toward hybrid SSM/attention models is largely motivated by long-context needs, and models designed for short contexts (standard Transformers) are being supplemented by long-context variants.

## Production considerations

### Cost of long context

Long context is expensive. A 1M-token prompt costs 1000× more than a 1K-token prompt (for input tokens). For closed-model APIs, this can be \$10+ per query; for self-hosted models, it requires significant GPU memory.

### Long context vs. RAG

Use long context when quality matters more than cost, when retrieval is hard (unstructured data), or when the task requires cross-document reasoning. Use RAG when cost matters, when the corpus is huge (can't fit in context), or when retrieval is reliable (structured data). Many production systems use both: RAG to find relevant chunks, long context to process them in detail.

### Latency

Long contexts have high latency — prefilling 1M tokens takes seconds to minutes. Streaming responses help perceived latency, but the first token is still slow. This makes long-context models unsuitable for real-time chat.

### Quality degradation

Models degrade at very long contexts, even when technically supported. "Lost in the middle" — information in the middle of a long context is recalled worse than information at the beginning or end. This is an active research area.

## Impact and legacy

Long-context architectures transformed the LLM landscape in 2024–2025 in five ways.

**Million-token context as a product feature.** Gemini 1.5 (1M), Claude (200K), GPT-4 (128K), Llama 3.1 (128K) — long context is now a standard capability.

**Enabled new application categories.** Code assistants (Cursor, Continue), research tools (Perplexity Pro), video understanding (Twelvelabs) all rely on long context.

**Drove architectural innovation.** The long-context requirement motivated hybrid SSM/attention models, Ring Attention, and positional extrapolation techniques.

**Shifted the RAG vs. long-context trade-off.** With long enough context, RAG becomes optional for some applications. This simplified architectures but increased costs.

**Highlighted "lost in the middle".** The discovery that models recall middle-of-context information poorly motivated research on attention patterns and training strategies.

For AI engineers, long-context architectures matter when designing applications with large inputs (codebases, documents, video), choosing between long context and RAG, reasoning about cost and latency for long-context queries, and understanding why 2025 models handle long context differently.

## Further reading

The primary sources for each approach:

- Ring Attention: arXiv:2310.01889
- Infini-Attention: arXiv:2404.07143
- LongRoPE: arXiv:2402.13753
- YaRN: arXiv:2309.00071

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[Mamba-2 and Structured Attention]] — the hybrid SSM/attention unification.
- [[SSMs Mamba and Frontiers]] — the state-space backbone of hybrid models.
- [[Hyena and Long Convolutions]] — sub-quadratic sequence mixing via FFT convolutions.
- [[RWKV and RetNet]] — the linear-time predecessors.
- [[Kimi Linear]] — a hybrid long-context model.
- [[Jamba]] — a hybrid long-context model.
- [[MiniMax-01]] — a hybrid long-context model.
- [[RoPE]] — the positional encoding LongRoPE scales.
- [[YaRN and NTK-Aware Scaling]] — the positional-extrapolation family.
- [[Sparse Attention]] — sparse attention for long sequences.
- [[Sliding Window Attention]] — windowed attention for long sequences.
- [[RAG Pipeline Overview]] — the alternative to long context.
