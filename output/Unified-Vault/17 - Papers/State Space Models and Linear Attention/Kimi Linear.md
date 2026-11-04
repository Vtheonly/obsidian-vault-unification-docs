---
title: Kimi Linear
type: concept
aliases: [Kimi Linear 2025, Moonshot AI, Linear Attention Hybrid]
tags: [paper, kimi-linear, linear-attention, hybrid, long-context, mixture-of-experts]
sources:
  - "30 - Kimi Linear 2025"
created_index: 52
---

Kimi Linear is Moonshot AI's 2025 hybrid architecture that combines linear attention, for cheap long-context processing, with standard attention, for precise retrieval. Its key innovation is a hybrid attention pattern in which most layers use linear attention at $O(N)$ cost and only a few layers use full attention at $O(N^2)$ cost, enabling near-linear scaling to million-token contexts while preserving the retrieval quality that pure linear attention lacks. Kimi Linear represents the 2025 trend toward hybrid attention/SSM architectures, alongside [[Jamba]] and [[MiniMax-01]]. See [[Papers MOC]] for the papers index, and [[Mamba]] and [[Linear Attention]] for the two traditions it blends.

## Citation

Moonshot AI (2025). *Kimi Linear: Technical Report*. (Released as a technical report; specific arXiv identifier pending — check Moonshot AI's publications.)

> [!warning] Source status
> The Kimi Linear technical report is research-backed — the architecture is documented in Moonshot AI's official technical report, but full architectural details may not be completely disclosed. This note reflects publicly available information as of mid-2025.

## The problem being solved

By 2025 the LLM community faced a tension. Full attention, as used in Transformers, delivers excellent quality, but its $O(N^2)$ cost limits context length: 128K context is expensive, and 1M+ is prohibitive. Linear attention and SSMs (see [[Mamba]] and [[Linear Attention]]) cost $O(N)$ and scale to million-token contexts, but they are weaker on retrieval tasks — finding specific facts from far back in the context.

Pure linear models underperform on "needle in a haystack" retrieval, the exact retrieval that attention excels at, while pure attention is too expensive for very long contexts. The hybrid approach uses linear attention for most layers (cheap, captures general context) and full attention for a few layers (expensive but rare, handles precise retrieval), getting the best of both worlds — near-linear cost with attention-like retrieval quality. Kimi Linear is one of several 2025 hybrid architectures (alongside Jamba, Falcon-Mamba and MiniMax-01) that pioneered this approach.

## The architecture

### Hybrid layer pattern

Kimi Linear interleaves its two sequence-mixing types in a repeating pattern:

```text
[Linear, Linear, Linear, Attention, Linear, Linear, Linear, Attention, ...]
```

Typically there are 3–7 linear attention layers per 1 full attention layer, and the ratio is a key hyperparameter. More linear layers means cheaper compute but weaker retrieval; more attention layers means better retrieval but higher cost. The empirical sweet spot, from the Kimi Linear report and similar architectures, is ~75–85% linear layers and ~15–25% attention layers.

### Linear attention variant

Kimi Linear uses a specific linear attention formulation — similar to [[Performer]]-style linear attention but with modifications:

```text
Standard attention:
  O = softmax(Q K^T) V         # O(N² d)

Linear attention (kernel-based):
  O = φ(Q) (φ(K)^T V)          # O(N d r)
  where φ is a feature map
```

The feature map φ is chosen to approximate the softmax kernel while enabling the associativity rearrangement that makes the computation linear in N.

### Full attention layers

The full attention layers use standard scaled dot-product attention with FlashAttention-3 on Hopper GPUs (see [[FlashAttention-2 and FlashAttention-3]]). These layers handle the precise retrieval that linear attention misses.

### Positional encoding

Kimi Linear uses a hybrid positional scheme that decouples the two layer types. Linear attention layers carry no positional encoding at all — linear attention is permutation-equivariant, which is fine for general context mixing. Full attention layers use RoPE, for precise position-aware retrieval. This decoupling lets each attention type use the positional scheme that suits it.

### Mixture of experts

Kimi Linear is also an MoE model, with 256+ experts and ~8 active per token, plus auxiliary-loss-free load balancing as introduced by [[DeepSeek-V2 and V3|DeepSeek-V3]]. The MoE + hybrid attention combination gives both parameter efficiency (MoE) and computational efficiency (hybrid attention).

## Key results

Kimi Linear was evaluated on long-context benchmarks:

| Benchmark                          | Full attention baseline | Kimi Linear |
|------------------------------------|-------------------------|-------------|
| Needle-in-haystack (128K)          | 98%                     | 95%         |
| Needle-in-haystack (1M)            | OOM (out of memory)     | 90%         |
| LongBench (average)                | baseline                | -2%         |
| Inference throughput (1M context)  | OOM                     | 50 tokens/sec |
| Inference cost (1M context)        | OOM                     | `$X`        |

The key result: Kimi Linear handles 1M-token contexts that are completely infeasible for full-attention models, with only a small quality degradation on retrieval tasks.

### Where hybrid wins

- **Very long contexts (>256K)**: hybrid is the only feasible option; full attention OOMs or is too slow.
- **Mixed workloads** (some short, some long): hybrid handles both efficiently — short contexts use mostly the linear layers (cheap), long contexts use the attention layers for retrieval.
- **Cost-sensitive long-context applications**: hybrid's near-linear cost makes million-token context economically viable.

### Where full attention still wins

- **Short contexts (<32K)**: full attention is fast enough, and the quality advantage matters.
- **Retrieval-critical tasks**: if every query requires exact retrieval from the full context, full attention's precision is valuable.
- **Simple serving setups**: hybrid requires more engineering (mixed kernel types, careful layer placement).

## Why it worked

### Most layers don't need precise retrieval

The empirical finding behind the hybrid pattern is that most attention layers in a Transformer don't perform precise retrieval. They do general context mixing, which linear attention handles well. Only a few layers (often the later ones) do the "find this specific fact" retrieval that requires full attention.

### Hybrid captures the best of both

Linear attention is $O(N)$ and handles general context; full attention is $O(N^2)$ but handles retrieval. By using linear for most layers and full for a few, the model gets $O(N)$ total cost with most of the retrieval quality.

### MoE plus hybrid is multiplicative efficiency

MoE reduces active parameters (compute per token); hybrid attention reduces attention cost (compute per layer). Together they multiply: a 100B MoE with hybrid attention can be cheaper to serve than a 20B dense model with full attention.

### Decoupled positional encoding

Using RoPE only in the attention layers (not the linear ones) is cleaner. Linear attention doesn't need positional encoding for general context; attention layers need it for retrieval. Decoupling lets each layer type use what it needs.

## Limitations

### Implementation complexity

Hybrid models require two different attention kernel implementations (linear + full), careful layer placement (which layers should be attention?), different positional encoding schemes per layer type, and serving frameworks that support mixed attention — [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] added this in 2025. This is more complex than pure-attention or pure-linear models.

### Quality gap on hard retrieval

For tasks requiring exact verbatim retrieval ("copy the sentence from position 500K"), hybrid models still underperform full attention. The linear layers "smear" information, making exact retrieval harder.

### Limited theoretical understanding

Why does the hybrid pattern work? What's the optimal ratio of linear to attention layers? These questions don't have rigorous answers yet — the design is largely empirical.

### Kernel maturity

Linear attention kernels are less mature than FlashAttention. Performance varies across implementations, and the best kernel depends on the specific linear attention variant.

## Comparison to other hybrid architectures (2024–2025)

| Model           | Linear Component | Attention Component | MoE | Notes                          |
|-----------------|------------------|---------------------|-----|--------------------------------|
| Jamba (AI21)    | Mamba            | Full attention      | Yes | 7:1 Mamba:attention ratio      |
| Falcon-Mamba    | Mamba            | None (pure Mamba)   | No  | Pure Mamba, no attention       |
| MiniMax-01      | Linear attention | Sparse attention    | Yes | 456B params, hybrid            |
| Kimi Linear     | Linear attention | Full attention      | Yes | Moonshot's approach            |
| Zamba           | Mamba            | Shared attention    | No  | Single attention block shared  |

The 2025 consensus: pure attention is too expensive for very long contexts; pure linear is too weak for retrieval; hybrid is the practical answer.

## Impact and legacy

Kimi Linear and the broader hybrid architecture trend represent the 2025 direction for long-context LLMs:

1. **Hybrid as the default for long context.** For contexts >256K, hybrid is becoming the standard. Full attention is reserved for shorter contexts or retrieval-critical applications.
2. **Linear attention maturity.** The proliferation of hybrid models drove investment in linear attention kernels and theory. By 2025, linear attention is a mature technique with well-understood trade-offs.
3. **MoE + hybrid as the efficiency stack.** The combination of MoE (sparse compute) and hybrid attention (sparse attention) gives the maximum efficiency for frontier-scale models. Most 2025 frontier models use both.
4. **Million-token context as a product feature.** Hybrid architectures made 1M-token context economically viable, enabling new applications (full-codebase analysis, long-document research, multi-hour video understanding).
5. **Influenced closed-source labs.** Gemini 1.5's 1M context, Claude's 200K context, and GPT-4's 128K context all likely use hybrid or sparse attention techniques, though architectures are not disclosed.

For AI engineers, hybrid architectures matter when building applications with very long contexts (>256K tokens), when choosing a model for cost-sensitive long-context serving, and when understanding why some models handle long context better than others.

## Further reading

- Kimi Linear technical report: Moonshot AI publications (check moonshot.ai).
- Jamba: arXiv:2403.19887.
- MiniMax-01: arXiv:2501.08313 (technical report on arXiv).
- [[Mamba]] — the SSM that inspired the hybrid trend.
- [[Linear Attention]] — linear attention variants.

## See also

- [[Papers MOC]] — the papers index.
- [[Mamba]], [[Mamba-2]], [[H3]], [[Based]], [[Jamba]], [[MiniMax-01]], [[Titans]] — the SSM and hybrid family.
- [[Linear Attention]], [[Sparse Attention]], [[Sliding Window Attention]] — the attention variants hybrids draw on.
- [[SSMs Mamba and Frontiers]], [[Long-Context Architectures]] — research-frontier context.
