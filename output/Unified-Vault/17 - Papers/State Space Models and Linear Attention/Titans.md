---
title: Titans
type: concept
aliases: [Titans, Titans Paper, Google Titans, Neural Memory Titans, Titans 2024]
tags: [paper, titans, neural-memory, test-time-training, long-context, attention]
sources:
  - "46 - Titans 2024"
created_index: 56
---

Titans is Google's 2024 architecture that augments attention with a neural memory module that learns online at test time. The key insight: attention is excellent at recent context but forgets distant information, and a learnable long-term memory module that is updated per-token at inference can extend effective context to millions of tokens without growing the attention matrix. Titans beat Transformers and hybrid SSMs on long-context benchmarks while staying quadratic only over a short local window.

## Citation

Behrouz, A., Zhong, P., Mirrokni, V. (Google DeepMind). (2024). *Titans: Learning to Memorize at Test Time*. arXiv:2501.00663.

## The problem being solved

Attention has two well-known limitations:

1. **Quadratic cost**: O(N²) in sequence length limits practical context to ~100k tokens.
2. **Information loss**: even with long context, models exhibit "lost in the middle" — they forget information in the middle of the context.

Existing solutions (sparse attention, sliding window, SSM hybrids) reduce cost but don't fundamentally solve the memory problem — they still compress history into a fixed-size state or a sparse subset.

Titans asks: **what if the long-term memory itself was a neural network that learns at test time?** Instead of compressing history into a vector, train a small "memory MLP" on the fly to store associations, then query it as a third module alongside attention.

## The architecture: three memory types

Titans combines three parallel memory mechanisms.

### Short-term memory: attention

Standard sliding-window attention over a local context (e.g., 2048 tokens). Handles recent, fine-grained patterns. Quadratic cost is bounded by the window size.

### Long-term memory: neural memory module

A small MLP (`M`) that's updated at test time using a surprise-driven learning rule. At each token:

- Compute "surprise" = prediction error of the memory MLP on the current input.
- Update `M`'s weights via gradient descent on the surprise.
- The output of `M` at the current token is the "retrieved" long-term memory.

This is essentially **test-time training** — the model adapts to the current context at inference. The memory module learns associations from the current document and can retrieve them later in the same document.

### Persistent memory: static parameters

Standard transformer weights (frozen at test time) that encode general knowledge from training.

### Combining the three

For each token, the output is:

$$y = \text{Attention}(x_{\text{local}}) + \text{NeuralMemory}(x) + \text{PersistentMemory}(x)$$

The three streams are added (or gated) to produce the final output. Each handles a different time scale.

## Key results

- **Long-context benchmarks**: Titans outperforms Transformers, Mamba, and Jamba at 2M-token context. Specifically on the "needle in a haystack" retrieval task at 1M+ tokens.
- **Quality at short context**: matches or slightly beats same-size Transformer on standard benchmarks (Pile perplexity, MMLU).
- **Throughput**: linear in sequence length beyond the local attention window — the neural memory is O(1) per token.
- **Memory module analysis**: visualizations show the neural memory learns to store specific facts (e.g., "the user's name is Alice") and recall them many tokens later.

## Why this paper matters

### Test-time compute as memory

Titans belongs to the 2024–2025 wave of "test-time compute" papers (o1, DeepSeek-R1, Titans). The insight: instead of doing all computation upfront at training, do some at inference, adapting to the specific input. Titans applies this to memory rather than reasoning.

### Bridging neural memory and attention

The paper explicitly cites the analogy to human memory: attention is working memory (small, fast, current); neural memory is episodic memory (large, slow, learned). Persistent weights are semantic memory (large, slow, learned over training). This cognitive-science framing makes the architecture intuitive.

### A practical long-context solution

Unlike SSM hybrids (which compress history into a fixed-size state), Titans' neural memory module can grow in capacity during a single document. This makes it effective for tasks like reading a 500k-token legal contract and answering questions about any specific clause.

### Surprise-driven learning

The "surprise = prediction error" learning rule is biologically plausible (dopamine-like surprise signals) and has been validated in computational neuroscience. This gives Titans a theoretical grounding beyond just empirical performance.

## Variants and extensions

### MAC (memory as context)

The original Titans paper places the neural memory as a parallel module. A variant, MAC (Memory as Context), feeds the memory output back into the attention's key-value store, making it "contextual" rather than "additive". MAC performs slightly better on multi-hop reasoning but is more complex.

### MAG (memory as gate)

Another variant, MAG (Memory as Gate), gates the three memory streams with a learned gate (instead of summing). MAG adapts the relative importance of short/long/persistent memory per token.

## Comparison with related architectures

| Model       | Short-term    | Long-term             | Persistent | Test-Time Learning |
|-------------|---------------|------------------------|------------|---------------------|
| Transformer | Attention     | None                   | Weights    | No                  |
| Mamba       | SSM state     | SSM state (compressed) | Weights    | No                  |
| Jamba       | Attention+SSM | SSM state              | Weights    | No                  |
| Titans      | Attention     | Neural Memory MLP      | Weights    | Yes (per-token GD)  |
| Memorizing Transformers | Attention | kNN over past KV | Weights | No (retrieval only)  |

## Reception and follow-ups

Titans was influential in the test-time compute research wave (2024–2025) alongside o1 (OpenAI) and DeepSeek-R1. While not as widely adopted as Mamba-2 or Jamba in production, it influenced:

- **Test-time compute scaling** literature: Titans is cited as a memory-side analog to reasoning-side test-time compute (o1).
- **Neural memory follow-ups**: multiple 2025 papers extend Titans' neural memory idea (e.g., memory-augmented Transformers, learned retrieval).
- **Long-context benchmarks**: Titans set new state-of-the-art on 1M+ token retrieval benchmarks, pushing the field to evaluate at longer contexts.

As of 2025–2026, Titans remains mostly a research architecture — no major open-weights model uses it. The test-time compute overhead (~30%) and memory stability concerns limited production adoption. However, the core idea (neural memory that learns at test time) is considered promising for future long-context systems.

## Limitations and open questions

- **Compute cost of test-time updates**: every token triggers a gradient step on the memory MLP. This adds ~30% inference latency vs a pure Transformer. Throughput vs attention alone depends on context length: at 1M+ tokens, Titans is faster; at 4k tokens, slower.
- **Memory stability**: the online gradient updates can be unstable for adversarial inputs. The paper adds normalization but doesn't fully solve this.
- **Limited open-source adoption**: as of mid-2025, no major open-weights model uses Titans. Jamba, Mamba-2, and Kimi Linear dominate the production hybrid landscape. Titans remains mostly a research architecture.
- **Memory capacity ceiling**: the neural memory MLP has a fixed parameter count; for very long contexts (10M+ tokens), it eventually saturates and can't store more.
- **Open question**: what's the optimal balance between attention, neural memory, and persistent weights? Titans uses equal weighting; future work may find better schedules.
- **Open question**: can the surprise-driven learning rule be improved? Biological plausibility is nice, but engineered alternatives might work better.

## Interview questions

**Q: What is the key innovation in Titans?**

A: Titans adds a **neural memory module** — a small MLP that's updated via gradient descent at test time, per token. The "surprise" (prediction error) drives the learning: when the memory MLP is surprised by the current input, it updates its weights to better predict similar inputs in the future. This gives the model a form of test-time learning, distinct from attention (which retrieves from fixed KV) and SSMs (which compress into fixed state).

**Q: How does Titans relate to test-time compute scaling (o1, DeepSeek-R1)?**

A: Titans is a memory-side analog to reasoning-side test-time compute. o1/DeepSeek-R1 spend test-time compute on **reasoning** (generating long CoT). Titans spends test-time compute on **memory** (updating the neural memory MLP). Both are part of the 2024–2025 "test-time compute" paradigm: do more computation at inference to improve quality, rather than relying solely on upfront training.

**Q: Why hasn't Titans been adopted in production like Jamba or Mamba-2?**

A: Three reasons. (1) **Compute overhead**: the per-token gradient step adds ~30% latency; production systems are latency-sensitive. (2) **Stability concerns**: online gradient updates can be unstable for adversarial inputs; production needs rock-solid stability. (3) **Engineering complexity**: implementing test-time gradient descent efficiently is harder than deploying a Mamba-2 hybrid. Titans is influential in research but the production-ready alternatives (Jamba) are simpler and "good enough".

## See also

- [[Papers MOC]] — the papers hub for this note.
- [[Mamba]] — the alternative linear-time model (no test-time learning).
- [[Jamba]] — the production hybrid without test-time learning.
- [[Mamba-2]] — the production SSM without test-time learning.
- [[Kimi Linear]] — the production hybrid that dominates alongside Jamba and Mamba-2.
- [[H3]], [[Based]] — the wider SSM and linear-attention family this note belongs to.
- [[DeltaNet and Titans]] — the research-frontier deep dive on Titans.
- [[Test-Time Compute Scaling]] — the paradigm Titans belongs to.
- [[DeepSeek-R1]] — the reasoning-side test-time compute analog.
- [[Chain of Thought]] — another form of test-time compute.
- [[Memory Types]] — the cognitive-science taxonomy Titans draws from.
- [[MemGPT and Letta]] — the agent-level analog (test-time memory operations).
- [[Long-Context Architectures]] — the long-context design space.
- [[SSMs Mamba and Frontiers]] — the research-frontier overview.
- [[Interpretability and Research MOC]] — the research hub covering this frontier.
