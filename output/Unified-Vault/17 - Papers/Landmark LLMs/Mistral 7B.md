---
title: Mistral 7B
type: concept
aliases: [Mistral 7B 2023, Jiang 2023]
tags: [paper, mistral, sliding-window, open-source]
sources:
  - "26 - Mistral 7B 2023"
created_index: 36
---

Mistral 7B demonstrated that a 7B-parameter model, with the right architectural choices (sliding window attention, GQA, SWA + global buffer), could outperform Llama 2 13B on all benchmarks while using fewer parameters. Mistral 7B established that careful architecture matters as much as scale, and that 7B was the sweet spot for open-weights models runnable on consumer hardware. The subsequent Mixtral 8x7B (MoE) extended this to match Llama 2 70B with faster inference. See [[Papers MOC]] for the surrounding area.

## Citation

Jiang, A. Q., Sablayrolles, A., Mensch, A., Bamford, C., Chaplot, D. S., Casas, D. d. l., et al. (2023). *Mistral 7B*. arXiv:2310.06825.

## The problem being solved

By late 2023, Llama 2 had established 7B and 13B as standard open-weights model sizes. Llama 2 13B was the quality leader at the "runs on a consumer GPU" tier, but it was still relatively expensive to serve. The question: could a 7B model match Llama 2 13B quality through better architecture, rather than more parameters?

Mistral's bet: architectural improvements (sliding window attention, grouped-query attention, better attention buffering) could close the gap. The result: Mistral 7B outperformed Llama 2 13B on all evaluated benchmarks while being 2× smaller. This was a significant moment — it showed that architecture still mattered, not just scale.

## The architecture

Mistral 7B is a [[Decoder-Only Architecture|decoder-only Transformer]] with several key innovations over Llama 2:

| Property            | Llama 2 7B   | Mistral 7B           |
|---------------------|--------------|----------------------|
| Parameters          | 6.7B         | 7.2B                  |
| Layers              | 32           | 32                    |
| d_model             | 4096         | 4096                  |
| Heads               | 32           | 32                    |
| KV heads            | 32 (MHA)     | 8 (GQA)               |
| Context window      | 4096         | 8192                  |
| Attention           | Full         | Sliding window (4096) |
| RoPE                | Yes          | Yes                   |
| RMSNorm             | Yes          | Yes                   |
| SwiGLU              | Yes          | Yes                   |
| Activation          | SwiGLU       | SwiGLU                |

### Sliding window attention (SWA)

Each token attends to the previous 4096 tokens (the window size), rather than all previous tokens. This makes attention $O(N \times w)$ instead of $O(N^2)$ — linear in sequence length for fixed window size.

With stacked layers, the effective receptive field grows: layer 2 can see tokens 2×4096 = 8192 positions back, layer 3 sees 3×4096, and so on. A 32-layer model has an effective receptive field of 32×4096 = 131K tokens — far more than the 8K context window. See [[Sliding Window Attention]] for details.

### Grouped-query attention (GQA)

Mistral uses 8 KV heads shared across 32 query heads. This reduces the [[KV Cache Mechanics|KV cache]] size by 4× compared to MHA, enabling larger batch sizes and longer contexts. See [[GQA]].

### Rolling buffer cache

Mistral uses a clever cache layout: the KV cache for position `i` is stored at `i mod window_size`. This means the cache is a fixed-size buffer (window_size × d_model) rather than growing with sequence length. For sequences longer than the window, old KV entries are overwritten — this is fine because SWA only looks back window_size tokens anyway.

### Pre-fill and chunking

For long prompts (>8K tokens), Mistral processes the prompt in chunks of window_size tokens. Each chunk attends to the previous chunk's KV cache. This enables efficient processing of long contexts without materializing the full attention matrix.

## Key results

Mistral 7B outperformed Llama 2 13B on all benchmarks:

| Benchmark         | Llama 2 13B | Mistral 7B |
|-------------------|-------------|------------|
| MMLU (5-shot)     | 54.8        | 60.1       |
| Commonsense Reasoning | 69.2    | 71.5       |
| World Knowledge   | 67.3        | 70.9       |
| Reading Comprehension | 71.4    | 74.3       |
| Math              | 14.6        | 28.4       |
| Code              | 17.8        | 30.5       |

The most striking improvements were on math (almost 2× improvement) and code (1.7× improvement) — suggesting that the architectural improvements (especially longer effective context via SWA) particularly helped reasoning tasks.

Mistral 7B also approached Llama 1 65B quality on many benchmarks despite being 9× smaller — a remarkable efficiency result.

### Instruction-tuned variant

Mistral 7B Instruct (fine-tuned with supervised learning on instruction data) outperformed Llama 2 13B Chat on MT-Bench and other chat benchmarks. This made Mistral 7B Instruct the default choice for open-weights chatbot deployment in late 2023.

## Why it worked

### Sliding window attention captures long context cheaply

SWA gives Mistral a 131K effective receptive field (32 layers × 4096 window) at $O(N \times w)$ cost. Full attention would be $O(N^2)$ — far more expensive for long sequences. SWA captures most of the benefit of long context at a fraction of the cost.

### GQA reduces memory

By sharing KV heads, Mistral reduces the KV cache size by 4×. This enables larger batch sizes (more requests served concurrently) and longer contexts. The quality impact of GQA is minimal — the model learns to compensate for the shared KV.

### 8K context matters

Llama 2's 4K context was limiting for many applications (long documents, multi-turn conversations). Mistral's 8K context (extendable to 32K with SWA) was a practical improvement that made the model more useful for real applications.

### Architecture over scale

Mistral 7B's key lesson: better architecture can substitute for more parameters. A 7B model with SWA + GQA beat a 13B model with standard attention. This influenced subsequent open-weights design — architecture matters, not just scale.

## Limitations

### 7B quality ceiling

Despite outperforming Llama 2 13B, Mistral 7B still trailed Llama 2 70B and [[GPT-4 Technical Report|GPT-4]] on complex reasoning. For frontier-quality tasks, larger models remained necessary.

### SWA loses exact long-range attention

Sliding window means tokens beyond the window cannot attend to each other directly (only indirectly through stacked layers). For tasks requiring exact long-range retrieval (e.g., "find the exact sentence from 50K tokens ago"), SWA underperforms full attention.

### License

Mistral 7B was released under Apache 2.0 (commercial-friendly), which was a significant advantage over Llama 2's more restrictive license. This accelerated adoption in commercial applications.

## Successors

### Mixtral 8x7B (December 2023)

- Mixture of Experts: 8 experts, 2 active per token.
- 46.7B total parameters, 12.9B active per token.
- Matches Llama 2 70B quality with 4× faster inference.
- Established MoE as a practical architecture for open-weights LLMs.

### Mixtral 8x22B (April 2024)

- Larger MoE: 8 experts, 141B total parameters, 39B active.
- Approaches GPT-4 quality on some benchmarks.
- Apache 2.0 license.

### Mistral Large (2024)

- Dense model, 123B parameters.
- Closed-weights (API only).
- Approaches GPT-4 quality.

### Mistral Nemo (2024)

- 12B parameters, developed with NVIDIA.
- 128K context.
- Designed as a drop-in upgrade for Mistral 7B.

### Mistral Small (2024)

- 22B parameters.
- Cost-optimized for high-throughput serving.

### Codestral (2024)

- 22B parameters, fine-tuned for code generation.
- Specialized for programming tasks.

## Impact and legacy

Mistral 7B's influence on the open-weights LLM ecosystem:

1. **Established 7B as the practical sweet spot**. Mistral 7B proved that a 7B model, well-architected, could serve most production needs. This size became the default for open-weights releases (Llama 3 8B, Qwen 2.5 7B, Gemma 2 9B all target this tier).

2. **Popularized sliding window attention**. SWA became a standard technique, used in modified form by Gemma, Qwen, and other models. The general lesson — restrict attention to local windows for efficiency — became part of the standard toolkit.

3. **Popularized GQA**. After Mistral 7B (and the GQA paper), GQA became the default attention variant for open-weights LLMs. Llama 3, Qwen 2.5, and Gemma 2 all use GQA.

4. **Validated MoE for open weights**. Mixtral 8x7B demonstrated that [[Mixture of Experts|MoE]] was practical for open-weights, not just closed-source models (like GPT-4's rumored MoE). This influenced [[DeepSeek-V2 and V3|DeepSeek-V3]], Qwen 2.5 MoE, and the broader MoE trend.

5. **European AI presence**. Mistral AI (French) became the leading European AI lab, demonstrating that frontier-quality open-weights LLMs could be developed outside the US. This had geopolitical implications for AI sovereignty.

For AI engineers, Mistral 7B remains a strong choice for cost-sensitive deployments. The architectural lessons (SWA, GQA, 8K+ context) are now standard across the open-weights ecosystem.

## Further reading

- Original paper: arXiv:2310.06825
- Mixtral 8x7B: arXiv:2401.04088
- Mistral AI blog: mistral.ai/news/announcing-mistral-7b/

## See also

- [[LLaMA]] — the Llama 2 models Mistral 7B outperformed at 2× fewer parameters
- [[GQA]] — the KV-cache-sharing attention variant Mistral popularized
- [[Sliding Window Attention]] — the windowed attention mechanism
- [[Longformer]] and [[BigBird]] — the earlier windowed/sparse attention lineage
- [[Mistral and Mixtral Architecture]] and [[Llama Mistral Qwen Comparison]] — architecture-focused treatments
- [[Papers MOC]]
- [[GQA MQA and MLA]]
