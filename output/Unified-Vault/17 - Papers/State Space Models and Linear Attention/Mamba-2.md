---
title: Mamba-2
type: concept
aliases: [Mamba-2, Mamba 2, SSD, Structured State Space Duality]
tags: [paper, mamba-2, ssm, ssd, state-space-model, linear-attention]
sources:
  - "45 - Mamba-2 2024"
created_index: 53
---

Mamba-2 unifies state-space models with linear attention via Structured State Space Duality (SSD) — a proof that selective SSMs are a special case of linear attention with a structured mask. This theoretical bridge enabled larger state sizes (256→8k), hardware-efficient implementations built on the linear-attention kernel ecosystem, and adoption in production models like Jamba. Mamba-2 is to SSMs what FlashAttention was to attention: a faster, more hardware-friendly reformulation that preserves the math. See [[Papers MOC]] for the papers index, and [[Mamba]] for the predecessor it generalizes.

## Citation

Dao, T., & Gu, A. (2024). *Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality*. ICML 2024. arXiv:2405.21060.

## The problem being solved

Mamba-1 (2023) introduced selective SSMs and achieved Transformer-competitive quality at linear time complexity, but it had two practical limitations. First, the state size was limited to ~256: Mamba-1's recurrence used a 16×N state matrix, where N (the state size) was capped at ~256 because larger states exceeded GPU shared memory during the parallel scan. Second, a custom CUDA kernel was required: Mamba-1's `mamba_ssm` package ships with a hand-tuned CUDA kernel that's hard to maintain and port, while the linear-attention ecosystem (FlashAttention-2, xformers) had mature kernels that Mamba-1 couldn't leverage.

Mamba-2's question: can we reformulate SSMs so they share the linear-attention kernel ecosystem and remove the state-size limit?

## The key idea: Structured State Space Duality (SSD)

Mamba-2 proves that selective SSMs are mathematically equivalent to a specific form of linear attention with a **structured mask**:

$$\text{SSM}(A, B, C) \equiv \text{LinearAttention}(Q, K, V, M_{\text{structured}})$$

Where $Q$, $K$, $V$ come from the inputs (just like attention), and $M_{\text{structured}}$ is a lower-triangular mask with a specific decay structure derived from the SSM's $A$ matrix.

This duality means that any SSM can be computed as a linear-attention operation; that any linear-attention kernel (FlashLinearAttention, etc.) can compute SSMs; and that the state size is no longer limited — it's a function of the kernel's workspace, not a fixed constant.

## Key architectural changes from Mamba-1

### Larger state size

Mamba-2 supports state sizes up to 8192 (vs Mamba-1's 256). Larger state means more memory capacity and better long-context retrieval.

### Multi-input SSM (MIS)

Mamba-2 processes multiple input "heads" in parallel within a single SSM, similar to multi-head attention. This improves throughput and lets the model learn head specialization.

### Hardware-efficient algorithm

The SSD formulation enables a block-parallel algorithm that achieves 2–8x speedup over Mamba-1's CUDA kernel on H100 GPUs. The algorithm reuses FlashAttention-2's tiling and memory hierarchy.

### Group-normalized output

Mamba-2 adds group normalization (similar to Grouped-Query Attention) to stabilize training with larger states.

## Key results

- **Quality**: Mamba-2 matches or slightly beats Mamba-1 on language modeling at equal parameter count.
- **Throughput**: 2–8x faster than Mamba-1 on H100; 1.5x faster than FlashAttention-2 at sequence length 8k (where attention is still quadratic).
- **State capacity**: 8192 state size (vs 256) — 32x more "memory" per layer.
- **Adoption**: Mamba-2 is the backbone of Jamba (2024), Codestral Mamba, and several other production models.

## Why this paper matters

### Theoretical unification

Before Mamba-2, the SSM and linear-attention literatures were separate. Mamba-2's SSD proof showed they're the same thing — a single framework that includes both as special cases. This unification lets researchers transfer insights between the two fields.

### Practical speedups

By leveraging the linear-attention kernel ecosystem, Mamba-2 gets free performance improvements as those kernels improve. Mamba-1's custom kernel had to be hand-maintained.

### Production adoption

Jamba (AI21, 2024) is a 52B-parameter hybrid model (1:7 attention:SSM ratio) built on Mamba-2. Its existence validated Mamba-2 as production-ready. Codestral Mamba (Mistral, 2024) extended this to code generation.

### Reopened long-context questions

With 8192 state size, Mamba-2 made SSM-based million-token context viable. Kimi Linear (2025) and MiniMax-01 (2025) pushed this further with hybrid attention+SSM architectures at million-token scale.

## Limitations

Mamba-2 still has no in-context retrieval: like Mamba-1, it fails synthetic induction-head tasks when used purely, which is why hybrids (Jamba) add periodic attention to fix this. Training is memory-hungry — the larger state size means more activation memory, despite the kernel improvements. And its inference cache is different from a Transformer's: Mamba-2's state is constant-size (not growing with context length), but it's incompatible with vLLM's PagedAttention infrastructure, so custom inference engines are needed.

## Comparison with Mamba-1 and attention

| Property            | Mamba-1      | Mamba-2               | Attention                |
|---------------------|--------------|------------------------|---------------------------|
| Time complexity     | O(N)         | O(N)                   | O(N²)                     |
| State size          | ~256         | Up to 8192             | Up to context length      |
| Kernel ecosystem    | Custom CUDA  | Linear-attention kernels | FlashAttention-2/3      |
| In-context retrieval| Fails        | Fails (pure)           | Excellent                 |
| Long-context cost   | Linear       | Linear                 | Quadratic                 |
| Production models   | Rare         | Jamba, Codestral Mamba | Most LLMs                 |

## Reception and follow-ups

Mamba-2 was widely adopted in 2024–2025 production systems. Key adoptions: Jamba (AI21, 2024), a 52B-parameter hybrid (1:7 attention:SSM) built on Mamba-2; Codestral Mamba (Mistral, 2024), a code generation model using Mamba-2; Falcon-Mamba (TII, 2024), a 7B pure Mamba-2 model; [[14 - Inference and Production/Inference/vLLM|vLLM]] 0.6+ (2024), which added native Mamba-2 inference support; and [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]], which supports Jamba (Mamba-2 hybrid) inference.

The SSD framework also influenced academic research: multiple 2024–2025 papers extended SSD (e.g., Mamba-2 for vision, Mamba-2 for speech). The theoretical unification of SSMs and linear attention opened new research directions in efficient sequence modeling.

## Limitations and open questions

The caveats in detail, together with the questions that remain open:

- **Still no in-context retrieval**: Mamba-2 (like Mamba-1) fails synthetic induction-head tasks when used purely. Hybrids (Jamba) add periodic attention to fix this.
- **Memory during training**: larger state size means more activation memory; Mamba-2 training is memory-hungry despite the kernel improvements.
- **Inference KV cache different**: Mamba-2's state is constant-size (not growing with context length), but it's incompatible with vLLM's PagedAttention infrastructure. Custom inference engines are needed.
- **Adoption gap**: despite technical advantages, Mamba-2 has not displaced Transformers in mainstream LLM deployments. Most 2026 frontier models (GPT-5, Claude 4, Gemini 3) are still Transformer-based. Mamba-2 dominates the hybrid niche but not the mainstream.
- **Open question**: can a pure SSM (no attention) ever match Transformer quality on in-context learning? H3 says no; Titans (2024) says yes with neural memory; the question remains open.

## Interview questions

**Q: What is Structured State Space Duality (SSD) and why does it matter?**

SSD is Mamba-2's proof that selective SSMs are mathematically equivalent to linear attention with a structured mask. This unification matters because: (1) it lets SSMs reuse the mature linear-attention kernel ecosystem (FlashLinearAttention); (2) it enables larger state sizes (8192 vs 256) by removing the GPU shared memory bottleneck; (3) it provides theoretical clarity — SSMs and linear attention are the same thing, just with different masks.

**Q: Why does Mamba-2 support 32x larger state size than Mamba-1?**

Mamba-1's parallel scan algorithm required the state matrix to fit in GPU shared memory during the scan, capping state size at ~256. Mamba-2's SSD formulation enables a block-parallel algorithm that processes the state in tiles, allowing states up to 8192. Larger state means more memory capacity and better long-context retrieval (though still not matching attention's exact retrieval).

**Q: When would you choose Mamba-2 vs a Transformer?**

Choose Mamba-2 (or a Mamba-2 hybrid like Jamba) when: (1) long context (>32k tokens) where the Transformer's O(N²) cost is prohibitive; (2) streaming/real-time applications where constant-memory-per-token matters; (3) cost-sensitive deployments where linear-time inference saves GPU hours. Choose a Transformer when: (1) context is short (<8k); (2) in-context learning is critical (pure SSMs fail this); (3) you need the mature Transformer ecosystem ([[14 - Inference and Production/Inference/vLLM|vLLM]], [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]], fine-tuning tools). For most 2026 production deployments, hybrids (Jamba) are the best of both worlds.

## See also

- [[Papers MOC]] — the papers index.
- [[Mamba]] — the predecessor; Mamba-2 generalizes Mamba-1.
- [[H3]] — anticipated the SSM-attention duality.
- [[Jamba]] — the production Mamba-2 hybrid.
- [[MiniMax-01]], [[Kimi Linear]] — linear-attention hybrids with Mamba-2 insights.
- [[Based]], [[Titans]] — other hybrids in the family.
- [[Linear Attention]] — the concepts Mamba-2 builds on.
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — the kernel ecosystem Mamba-2 leverages.
- [[FlashAttention-2 and FlashAttention-3]] — the kernels whose tiling SSD reuses.
- [[PagedAttention]] — the KV-cache infrastructure Mamba-2's constant state doesn't fit.
- [[Mamba-2 and Structured Attention]] — chapter deep dive.
- [[SSMs Mamba and Frontiers]], [[Long-Context Architectures]] — research-frontier context.
