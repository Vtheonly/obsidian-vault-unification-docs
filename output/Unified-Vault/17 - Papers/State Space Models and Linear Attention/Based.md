---
title: Based
type: concept
aliases: [Based, Based Paper, Simple Linear Attention]
tags: [paper, based, simple-linear-attention, hybrid, taylor-expansion, sliding-window-attention]
sources:
  - "47 - Based 2024"
created_index: 49
---

Based is a 2024 paper from Cartesia (Helbling, Peng et al.) demonstrating that a remarkably simple hybrid — mostly linear attention with a few sliding-window attention layers — can match Transformer quality at 1B–3B scale while being 4–8x faster at long context. Its contribution is simplicity: where Jamba and Mamba-2 use complex SSM formulations, Based uses a 3-line linear attention variant plus standard attention, making it the easiest hybrid to implement and reproduce. See [[Papers MOC]] for the papers index, and [[H3]] and [[Mamba-2]] for the more complex hybrids it simplified.

## Citation

Peng, B., Zhu, C., Chiu, C., Peng, H., Lin, J., Swaminathan, S., Sil, A., Viegas, E., Pfister, H., Weld, D. S., Crowell, J., Starnes, M., Naik, N., Zeng, E., Cartesia. (2024). *Simultaneously Enabling Model Scaling and Long Context Inference: A Case for Simpler Linear Attention-Based Hybrid Models*. arXiv:2412.01059.

## The problem being solved

By late 2024 the hybrid SSM-attention landscape had fragmented into increasingly complicated designs. Jamba combined complex MoE + SSM + attention and was hard to reproduce. Mamba-2's SSD framework is mathematically elegant but requires custom CUDA kernels. Kimi Linear uses a linear attention variant but is production-only and not reproducible. Based's question: can a maximally simple linear attention variant — implementable in 3 lines of PyTorch — achieve the same hybrid benefits?

## The architecture

Based combines three components.

### Linear attention (most layers)

Standard linear attention with a Taylor-expansion approximation to softmax:

$$\text{LinearAttn}(Q, K, V) = \phi(Q) (\phi(K)^T V)$$

where $\phi(x) = [1, x, x^2/2]$ (Taylor expansion of $e^x$ to second order). This is the entire linear attention implementation — no exotic kernel, no custom CUDA. The Taylor approximation captures the most important nonlinearity of softmax (the exponential) while remaining fully linear and parallelizable.

### Sliding window attention (few layers)

Standard sliding-window attention every 6th layer, with window size 1024 (see [[Sliding Window Attention]]). This handles the local retrieval that linear attention can't do well.

### Standard MLPs and RMSNorm

No changes from a typical Transformer — Based's goal is to be drop-in compatible with existing Transformer infrastructure.

## Key results

- **Quality**: matches a same-sized Transformer on Pile perplexity at 1B and 3B scales.
- **Long-context inference**: 4–8x faster than a Transformer at 32k+ context; constant memory for the KV cache (vs growing for a Transformer).
- **Implementability**: ~50 lines of PyTorch code in total for the entire hybrid model. Researchers can reproduce Based in an afternoon.
- **Quality at 32k context**: matches the Transformer while using 8x less memory.

## Why this paper matters

### Resetting the complexity bar

Before Based, the hybrid literature trended toward complex formulations (SSD, structured masks, custom kernels). Based showed that most of the benefit comes from the simple linear + sliding window combination, not from the exotic SSM machinery. This "less is more" result redirected the field toward simplicity.

### Reproducibility

Based is fully reproducible from the paper — no proprietary kernels, no special training infrastructure. This is rare in 2024 LLM research. The simplicity enabled many follow-up papers to use Based as a baseline.

### Practical inference wins

The 4–8x speedup at long context is enough to matter in production. Cartesia (the authors' company) shipped Based-based models for real-time voice applications where latency matters.

### Theoretical insight

Based's success with Taylor-expansion linear attention suggests that the exponential in softmax is largely for stability, not expressivity. A second-order Taylor approximation captures most of the benefit. This insight informs future linear-attention design.

## Limitations

In prose form: as of 2025 no open-weights model uses Based beyond 7B scale, with Jamba, Mamba-2 and Kimi Linear dominating production. At very long context (1M+ tokens) Based falls behind Titans and Kimi Linear, because the simple linear attention saturates faster than SSM-based approaches. On few-shot in-context learning benchmarks Based lags slightly behind Transformers — the linear attention's retrieval weakness shows up there. And the training-time speedup is modest: only ~1.2x faster than a Transformer during training, versus 4–8x at inference.

## Comparison with related architectures

| Model       | Hybrid Type                    | Implementation Complexity | Speedup vs Transformer (32k context) |
|-------------|--------------------------------|---------------------------|--------------------------------------|
| Transformer | Pure attention                 | Standard                  | 1x (baseline)                        |
| Jamba       | SSM + attention + MoE         | High (custom kernels)     | 3x                                   |
| Mamba-2     | SSD (linear attention variant)| Medium (custom kernel)    | 5x                                   |
| Based       | Taylor linear attention + SWA | Very low (3 lines)        | 4–8x                                 |
| Titans      | Attention + neural memory     | High (test-time training) | 10x+ at 1M+ context                  |

## Reception and follow-ups

Based was influential in the research community for its "less is more" demonstration. Academically, multiple 2025 papers cited Based as evidence that simple linear attention variants can match complex SSMs, and the paper reset the complexity bar for hybrid architectures. Cartesia (the authors' company) ships Based-based models for real-time voice applications where latency matters, which validated Based in production. Its ~50-line PyTorch implementation made it the easiest hybrid to reproduce, and many follow-up papers used Based as a baseline.

However, Based did not displace Mamba-2 or Jamba in mainstream LLM deployments. The production hybrid landscape in 2025–2026 is dominated by Mamba-2 (Jamba, Codestral Mamba) and Kimi Linear. Based's contribution is primarily methodological — showing that simplicity suffices.

## Limitations and open questions

The caveats above, restated with the open questions they raise:

- **No production model at scale**: as of 2025, no open-weights model uses Based at >7B scale. Jamba, Mamba-2, and Kimi Linear dominate production.
- **Quality gap at very long context**: at 1M+ tokens, Based falls behind Titans and Kimi Linear — the simple linear attention saturates faster than SSM-based approaches.
- **In-context learning**: Based lags slightly behind Transformers on few-shot ICL benchmarks; the linear attention's retrieval weakness shows up here.
- **Training throughput**: at training time, Based is only ~1.2x faster than a Transformer (vs 4–8x at inference). The training speedup is modest.
- **Open question**: is the Taylor-expansion approximation optimal, or are there better kernel functions for linear attention? Based uses 2nd-order Taylor; higher orders may give better quality at higher compute cost.
- **Open question**: can Based be combined with Mamba-2's SSD framework for the best of both? No paper has tried this yet.

## Interview questions

**Q: What is Based's key contribution?**

Based showed that a remarkably simple hybrid — Taylor-expansion linear attention (3 lines of PyTorch) + sliding window attention every 6 layers — matches Transformer quality at 1B–3B scale while being 4–8x faster at long context. The contribution is simplicity: where Jamba and Mamba-2 use complex SSM formulations, Based uses a 3-line linear attention variant. This "less is more" result redirected the hybrid literature toward simpler implementations.

**Q: Why does Taylor-expansion linear attention work?**

The standard softmax attention is `softmax(QK^T)V`. The exponential in softmax is what makes it expensive (no closed-form linearization). Based approximates the exponential with its 2nd-order Taylor expansion: `e^x ≈ 1 + x + x²/2`. This approximation is fully linear (no exp), so attention becomes `(Q + Q²) (K + K²)^T V` which can be computed in O(N) time via the linear attention trick `Q (K^T V)`. The 2nd-order Taylor captures the most important nonlinearity of softmax while remaining linear and parallelizable.

**Q: When would you choose Based over Mamba-2 or Jamba?**

Choose Based when: (1) you value implementability (3 lines vs a custom CUDA kernel); (2) you're at 1B–3B scale and don't need 1M+ context; (3) you want a reproducible baseline for research. Choose Mamba-2/Jamba when: (1) you need 1M+ context (Mamba-2's larger state wins); (2) you want production-ready infrastructure ([[14 - Inference and Production/Inference/vLLM|vLLM]], [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] support); (3) you're at >7B scale where Mamba-2's advantages compound. For most production deployments, Mamba-2/Jamba is the safer choice; Based is the simpler research baseline.

## See also

- [[Papers MOC]] — the papers index.
- [[H3]] — the earlier hybrid with a more complex SSM.
- [[Mamba-2]] — more expressive but harder to implement.
- [[Jamba]] — the production hybrid; more complex than Based.
- [[Titans]] — adds test-time learning, which Based doesn't.
- [[Kimi Linear]], [[Mamba]], [[MiniMax-01]] — the wider hybrid family.
- [[Linear Attention]], [[Sliding Window Attention]] — the components Based combines.
- [[RWKV and RetNet]] — alternative linear-time models.
- [[SSMs Mamba and Frontiers]] — research-frontier context.
