---
title: Mamba-2 and Structured Attention
type: concept
aliases: ["Mamba-2", "Structured Attention", "SSD", "Structured State Space Duality"]
tags: [research, mamba-2, structured-attention, ssm, linear-attention]
sources: ["02 - Mamba-2 and Structured Attention"]
created_index: 30
---

Mamba-2 (2024) unified state space models (SSMs) with attention by showing that the SSM's recurrent computation can be expressed as a **structured attention matrix** — a semiseparable matrix. This "structured state space duality" (SSD) lets SSMs leverage attention's efficient kernels and enables hybrid SSM/attention architectures. Mamba-2 also scaled the state dimension dramatically (from 16 to 256+), improving retrieval quality, and the unification clarified when SSMs and attention are preferable — inspiring the hybrid models that followed (Jamba, Zamba). The paper is Dao & Gu (2024), *Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality* (ICML 2024, arXiv:2405.21060).

## The problem being solved

[[Mamba]] (2023) demonstrated that selective state space models could match Transformer quality at linear cost. But Mamba had two limitations. First, **limited state dimension**: Mamba's state was small (typically 16 dimensions per channel), which limited its ability to store detailed information for retrieval — this caused Mamba to underperform attention on "needle in a haystack" tasks. Second, **no connection to attention theory**: Mamba and attention looked like completely different architectures, and there was no theoretical framework for understanding when SSMs or attention were preferable, or how to combine them.

Mamba-2 addressed both: a **larger state dimension** (scaled to 128–256+) and **structured state space duality (SSD)** — a theoretical framework showing that SSMs are equivalent to attention with a structured (semiseparable) attention matrix.

## SSMs are structured attention

### The SSM recurrence

A selective state space model computes:

```text
h_t = A_t · h_{t-1} + B_t · x_t    # state update
y_t = C_t · h_t                     # output
```

Unrolled over a sequence, the output at position `t` depends on all previous inputs through a chain of matrix multiplications. This can be written as:

```text
y_t = Σ_{j≤t} C_t · (A_{t} · A_{t-1} · ... · A_{j+1}) · B_j · x_j
```

### The attention formulation

Standard attention computes:

```text
y_t = Σ_j softmax(Q_t · K_j / sqrt(d)) · V_j
```

### The connection

Mamba-2 showed that the SSM recurrence is equivalent to attention with a specific attention matrix:

```text
y_t = Σ_j M_{t,j} · V_j
```

where `M` is a **semiseparable matrix** — a structured matrix where each lower-triangular block can be factored as `C_t · (A_{t} · ... · A_{j+1}) · B_j`.

This means **SSMs are attention with a semiseparable attention matrix**, and **attention is the special case where the matrix is unstructured (any values)**. The semiseparable structure is what makes SSMs O(N) — the structure allows efficient computation that doesn't require materializing the full N×N matrix.

### Implications of the unification

First, **SSMs can use attention kernels**: the structured attention matrix can be computed using modified attention kernels (like [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]), giving SSMs the same hardware efficiency as attention. Second, **hybrid architectures are principled**: combining SSM layers (semiseparable attention) with attention layers (unstructured attention) is now a principled choice — you're mixing two structured attention variants. Third, **design trade-offs are clearer**: attention's unstructured matrix can represent arbitrary token-token interactions (good for retrieval), while the SSM's semiseparable matrix is more constrained (good for efficiency, weaker for exact retrieval).

## The larger state dimension

Mamba (2023) used a state dimension of 16 per channel — small enough that the state couldn't store much information. This caused Mamba to underperform on retrieval tasks (finding specific facts from far back in the context). Mamba-2 scaled the state dimension to 128–256+ per channel, an 8–16× increase. This dramatically improved retrieval quality: **needle-in-haystack (Mamba, state=16)**: 60% accuracy at 32K context; **needle-in-haystack (Mamba-2, state=128)**: 90% accuracy at 32K context. The larger state gives the model more "memory" to store information for later retrieval, closing much of the gap with attention.

### The hardware efficiency trick

Naively, a 128-dimensional state would be expensive to compute (the state matrices are 128×128, and the recurrence involves matrix multiplications). Mamba-2 uses the SSD connection to compute this efficiently using a modified FlashAttention kernel — the semiseparable structure allows the same tiling and IO-awareness as FlashAttention.

## Key results

Mamba-2 achieved results competitive with attention-based models:

| Benchmark         | Mamba (state=16) | Mamba-2 (state=128) | Transformer |
|-------------------|------------------|---------------------|-------------|
| The Pile (PPL)    | 2.97             | 2.85                | 2.88        |
| Needle-in-haystack| 60%              | 90%                 | 98%         |
| Inference speed (32K) | 1.0×          | 0.95×               | 0.3× (slower)|

Mamba-2 closed most of the quality gap with Transformers while maintaining the inference speed advantage. The remaining gap (needle-in-haystack: 90% vs 98%) is the motivation for hybrid architectures.

## Why it worked

### The unification enables hardware co-design

By expressing SSMs as structured attention, Mamba-2 can use attention's optimized kernels. The same hardware (tensor cores, FlashAttention-style tiling) works for both, which makes SSMs as fast to train and serve as attention.

### Larger state fixes the retrieval weakness

Mamba's small state was the main quality bottleneck. Scaling it (enabled by the efficient kernel) fixed most of the retrieval weakness; the remaining gap is small enough that hybrid architectures can close it.

### Semiseparable structure is the right abstraction

Semiseparable matrices are well-studied in numerical linear algebra, with efficient algorithms for factorization and inversion. Mamba-2 leveraged this existing theory rather than inventing new mathematics.

## Limitations

### Still below attention on hard retrieval

Even with a larger state, Mamba-2 (90% on needle-in-haystack) trails attention (98%). For retrieval-critical applications, attention is still preferred.

### Larger state increases memory

A 128-dimensional state uses 8× more memory than a 16-dimensional state. For very long contexts, this can offset some of the efficiency advantage.

### Hybrid architectures are more complex

While the unification makes hybrids principled, implementing a model with both SSM and attention layers requires supporting both kernel types. This adds engineering complexity.

### Theoretical gaps remain

The unification explains the connection between SSMs and attention, but doesn't fully predict when each is preferable. Empirical evaluation is still needed.

## Hybrid architectures (2024–2025)

The SSD unification enabled principled hybrid architectures.

### Jamba (AI21, 2024)

[[Jamba]] interleaves Mamba-2 layers and attention layers (typically 7:1 ratio), uses a MoE architecture (52B total, 12B active), combines Mamba-2's efficiency with attention's retrieval quality, and was one of the first production hybrid models.

### Zamba (Zyphra, 2024)

Mamba blocks with a single shared attention block (repeated). More parameter-efficient than full interleaving, it demonstrates that even minimal attention (1 in 8 layers) significantly improves retrieval.

### Falcon-Mamba (TII, 2024)

Pure Mamba-2 (no attention layers) — demonstrating that for some workloads, pure SSM is sufficient.

### MiniMax-01 (2025)

[[MiniMax-01]] is a hybrid of linear attention + sparse attention, 456B parameters (MoE), scaling to 1M+ context.

The 2025 consensus: pure SSMs work for many tasks, but attention remains necessary for retrieval-heavy workloads. Hybrids offer the best of both worlds.

## Impact and legacy

Mamba-2's influence on the field runs in five directions. It **unified SSM and attention theory**: the SSD framework gave researchers a common language for SSMs and attention, enabling principled comparisons and hybrids. It **enabled efficient SSM training**: the attention-kernel-based computation made Mamba-2 as fast to train as Transformers, removing a major adoption barrier. It **catalyzed hybrid architectures**: Jamba, Zamba, and other 2024–2025 hybrids build directly on the SSD framework — the era of pure-attention LLMs is ending, and hybrids are the future. It **clarified the SSM/attention trade-off**: SSMs trade retrieval precision for efficiency, a fundamental trade-off, not a limitation to be "fixed". And it **influenced closed-source labs**: the hybrid trend ([[Gemini Architecture|Gemini 1.5]]'s 1M context, [[Claude Architecture|Claude]]'s 200K context) likely uses SSM/attention hybrids, though those architectures are not disclosed.

For AI engineers, Mamba-2 matters when choosing between SSM, attention, or hybrid for a new model; when understanding why 2025 LLMs handle long context differently; and when reasoning about the efficiency/quality trade-off in attention design.

## Further reading

- Original paper: arXiv:2405.21060.
- Mamba-2 code: github.com/state-spaces/mamba.

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[SSMs Mamba and Frontiers]] — the SSM foundation and frontier overview.
- [[DeltaNet and Titans]] — the memory-augmented frontier beyond Mamba-2.
- [[Mamba]] — the original Mamba paper.
- [[Mamba-2]] — the paper.
- [[Jamba]] — the production hybrid built on Mamba-2.
- [[MiniMax-01]] — the large-scale hybrid.
- [[Kimi Linear]] — a later linear-attention architecture.
- [[Linear Attention]] — the conceptual ancestor.
- [[Self-Attention]] — the other side of the duality.
- [[RWKV and RetNet]] — alternative hybrids.
- [[Hyena and Long Convolutions]] — the long-convolution alternative.
