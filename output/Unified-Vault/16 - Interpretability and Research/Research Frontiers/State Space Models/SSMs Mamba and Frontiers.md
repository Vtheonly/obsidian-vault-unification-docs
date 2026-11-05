---
title: SSMs Mamba and Frontiers
type: concept
aliases: ["Mamba", "State Space Models", "SSMs", "Research Frontiers Overview"]
tags: [research, mamba, ssm, hybrid, reasoning, long-context]
sources: ["01 - SSMs Mamba and Frontiers"]
created_index: 31
---

The 2024–2026 research frontier challenges the Transformer's dominance from several directions at once: State Space Models (Mamba, Mamba-2) as attention alternatives, hybrid architectures (Jamba, Falcon-Mamba), test-time compute scaling (o1, R1), 1M+ token context, and Titans' neural memory. This note anchors the state-space thread — the SSM foundation and mathematics, the Mamba line, the fundamental attention-versus-SSM tradeoff, and the hybrid consensus — and surveys the adjacent frontiers of reasoning and long context. The dedicated sibling notes cover each frontier in depth.

## State space models

### The SSM foundation

SSMs model sequences via a hidden state that evolves linearly:

$$
\mathbf{h}_t = \mathbf{A} \mathbf{h}_{t-1} + \mathbf{B} \mathbf{x}_t
$$
$$
\mathbf{y}_t = \mathbf{C} \mathbf{h}_t
$$

The structured SSM (S4, Gu et al. 2022) showed these could match Transformers on Long Range Arena benchmarks with $O(n)$ scaling.

### Mamba: selective state spaces

[[Mamba]] (Gu & Dao, 2023) was the breakthrough SSM. Its key innovation is **selective** state spaces — the matrices $\mathbf{B}$ and $\mathbf{C}$ are input-dependent (not fixed), which lets the model "select" which inputs to remember. The practical profile: $O(n)$ compute and memory; a parallel scan for training (parallelizable across sequence length); $O(1)$ inference per token (the state is fixed-size, with no growing KV cache); and quality that matches Transformers on language modeling.

### Mamba-2 in brief

[[Mamba-2]] (Dao & Gu, 2024) improved Mamba with better hardware utilization (more matmul-friendly), an explicit connection to attention via the "structured masked attention" framework, and 2–8x faster training than Mamba-1 on H100. [[Mamba-2 and Structured Attention]] gives the detailed treatment.

## SSM mathematics

The classical state space model is a continuous-time linear system:

$$
\dot{\mathbf{h}}(t) = \mathbf{A} \mathbf{h}(t) + \mathbf{B} \mathbf{x}(t), \quad \mathbf{y}(t) = \mathbf{C} \mathbf{h}(t) + \mathbf{D} \mathbf{x}(t)
$$

Discretizing with step $\Delta$ via zero-order hold gives the discrete-time SSM:

$$
\overline{\mathbf{A}} = \exp(\Delta \mathbf{A}), \quad \overline{\mathbf{B}} = (\Delta \mathbf{A})^{-1} (\exp(\Delta \mathbf{A}) - \mathbf{I}) \cdot \Delta \mathbf{B}
$$

$$
\mathbf{h}_t = \overline{\mathbf{A}} \mathbf{h}_{t-1} + \overline{\mathbf{B}} \mathbf{x}_t, \quad \mathbf{y}_t = \mathbf{C} \mathbf{h}_t
$$

**S4 (Gu et al. 2022)** showed that structuring $\mathbf{A}$ in a specific way (HiPPO initialization) allows the SSM to capture long-range dependencies efficiently. The key trick: the recurrence can be unrolled into a convolution, allowing parallel training.

**Mamba's innovation (selective SSMs)** makes $\overline{\mathbf{B}}$ and $\mathbf{C}$ input-dependent:

$$
\mathbf{h}_t = \overline{\mathbf{A}}(\mathbf{x}_t) \mathbf{h}_{t-1} + \overline{\mathbf{B}}(\mathbf{x}_t) \mathbf{x}_t, \quad \mathbf{y}_t = \mathbf{C}(\mathbf{x}_t) \mathbf{h}_t
$$

This breaks the convolution form (you can't parallelize via FFT anymore) but enables a **parallel scan** algorithm that is still $O(n \log n)$ for training. The input-dependence is what makes Mamba "selective" — the model can choose what to remember based on the input.

## Mamba versus attention: the fundamental tradeoff

| Property                  | Attention               | Mamba (SSM)             |
|---------------------------|-------------------------|-------------------------|
| Compute per token         | $O(n)$ (with KV cache)  | $O(1)$ (fixed state)    |
| Training compute          | $O(n^2)$                | $O(n \log n)$ (parallel scan) |
| Memory (inference)        | $O(n)$ (grows with context) | $O(1)$ (fixed state) |
| Exact recall              | Yes (copy via attention) | Approximate (state compresses) |
| In-context learning       | Yes (induction heads)   | Limited (state compresses history) |
| Long-context efficiency   | Expensive past 100K     | Constant cost regardless of length |
| Quality on long-context   | Strong                  | Good but loses exact recall |

The key insight: **attention and SSMs are complementary**. Attention gives exact recall and in-context learning but is expensive; SSMs are cheap and scale linearly but compress history into a fixed state. That complementarity is why **hybrid architectures** (Jamba, Zamba) exist: a few attention layers for recall + ICL, many SSM layers for efficiency.

## Mamba-2: structured masked attention

Mamba-2 (Dao & Gu 2024) reframed SSMs as a special case of "structured masked attention," making the connection to attention explicit. The key insights: the SSM's state $\mathbf{h}_t$ can be written as $\mathbf{h}_t = \sum_{i \leq t} \overline{\mathbf{A}}^{t-i} \overline{\mathbf{B}} \mathbf{x}_i$; this is equivalent to attention with a structured mask ($\overline{\mathbf{A}}^{t-i}$ plays the role of the attention weight); and this enables hardware-efficient implementations that reuse [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]-style tiling. The result: Mamba-2 is 2-8× faster than Mamba-1 on H100 with no quality loss, and the connection to attention also enables hybrid attention-SSM layers (some heads attend, some are SSM) with unified infrastructure. See [[Mamba-2 and Structured Attention]] for the full treatment.

## Hybrid architectures

Attention has two big advantages over SSMs: **precise recall** (attention can copy exact tokens, while SSMs compress everything into a fixed-size state) and **in-context learning** (induction heads — see [[Mechanistic Interpretability]] — need attention). SSMs have two big advantages over attention: **$O(n)$ scaling** (no quadratic memory/compute) and **constant inference memory** (no KV cache growth). Hybrids combine attention's recall with SSMs' efficiency; most architectures use a few attention layers (for recall and ICL) plus many SSM layers (for efficiency).

### Jamba (AI21, 2024)

[[Jamba]] mixes Mamba layers with attention layers (e.g., a 1:7 ratio), is 52B params (12B active) with MoE, and combines Mamba's efficiency with attention's precision. It matches Llama 2 70B quality at 5× lower inference memory.

### Zamba (Zyphra, 2024)

Mamba + shared attention layers; higher quality than pure Mamba at small scale.

### Falcon-Mamba (TII, 2024)

Pure Mamba at 7B scale — showing that Mamba can stand alone for production LLMs.

### Why hybrids won (the 2024–2026 consensus)

Pure attention has scaling issues past ~1M tokens (KV cache size, $O(n^2)$ training cost), and pure SSMs lose exact recall and ICL. The empirical finding: **hybrids (1:7 attention:SSM ratio) get the best of both**. The pattern: at small scale (7B), pure Mamba can compete; at large scale (50B+), hybrids dominate because attention's recall matters more. Falcon-Mamba shows Mamba can stand alone, but hybrids are usually better.

## Test-time compute scaling

### The discovery and the scaling law

OpenAI o1 (Sep 2024) showed that **spending more compute at inference** (longer CoT) can dramatically improve reasoning — a new dimension of capability. Snell et al. (2024) showed that test-time compute scales: more thinking → better answers, with diminishing returns. o1 and DeepSeek-R1 (Jan 2025) demonstrated a new scaling law:

$$\text{Accuracy} \propto \log(\text{test-time tokens})$$

For hard problems (math olympiad, competitive programming), going from 1K to 100K thinking tokens can take accuracy from 30% to 80%. For easy problems, the curve saturates quickly.

### Why this matters

Pre-2024, capability came from (1) more parameters, (2) more training data, (3) more training compute. Test-time compute is a fourth dimension. A smaller model with more thinking can beat a larger model with less thinking, on hard problems.

### The recipe and the open-source reproduction

The recipe: train with RL on verifiable rewards (math, code); the model learns to produce long internal CoT; at inference, allow the model to think for thousands of tokens. [[DeepSeek-R1]] (Jan 2025) reproduced this recipe openly.

### Production implication: adaptive thinking budgets

Most reasoning-model deployments use **adaptive thinking budgets** — a short budget for easy queries, a long budget for hard ones, which requires a difficulty classifier or user-specified difficulty. The router-based hybrid pattern (cheap model for easy, reasoning model for hard) is the standard 2026 production pattern. [[Test-Time Compute Scaling]] covers the paradigm in full.

## Long context (1M+ tokens)

### The challenge

Full attention's $O(n^2)$ becomes infeasible past ~1M tokens. Even with [[FlashAttention-2 and FlashAttention-3|FlashAttention-3]], 10M tokens would need ~50TB of attention intermediates per layer.

### Approaches

| Approach                | Mechanism                                  | Max Context Tested | Quality at 1M | Implementation Cost |
|-------------------------|--------------------------------------------|--------------------|---------------|--------------------|
| Full attention          | Standard softmax attention                 | ~256K (with FlashAttn3) | Strong | Trivial (use vLLM) |
| YaRN / NTK scaling      | Interpolate RoPE frequencies              | 4-32× training length | Good | Low (modify RoPE) |
| LongRoPE                | Search for non-uniform RoPE scaling       | 2M                 | Good          | Medium (search)    |
| Ring Attention          | Distribute attention across GPUs           | 10M+ (with enough GPUs) | Strong | High (multi-node) |
| Sparse attention        | Longformer/BigBird patterns                | 1M+                | Decays with length | Medium |
| SSM hybrids             | Mamba layers for long context              | 1M+                | Good (no exact recall) | Medium |
| Titans (neural memory)  | Persistent learned memory                  | Effectively unlimited | TBD (research) | Very high (research) |

In prose: **YaRN / NTK scaling** extends RoPE models to 4–32× their training length without retraining ([[YaRN and NTK-Aware Scaling]]); **LongRoPE** searches for non-uniform frequency scaling and achieves 2M tokens; **Ring Attention** distributes attention across multiple GPUs, with each GPU handling a chunk of the sequence; **sparse attention** applies [[Longformer]]/[[BigBird]] patterns for extreme length; **SSM hybrids** use Mamba layers for long context and attention for short; and **Titans** add persistent learned memory (below).

### Models with 1M+ context

- Gemini 1.5 Pro: 2M tokens.
- Claude 3.5: 200k tokens.
- GPT-4 Turbo: 128k tokens.
- Llama 3.1: 128k tokens (extendable to 1M+ with YaRN).

The [[Gemini Architecture]], [[Claude Architecture]], [[GPT-4 Inferred Architecture]], and [[Llama Family Architecture]] notes cover what is known about each family.

### Production guidance for 2026

- Up to 128K: standard attention + [[FlashAttention-2 and FlashAttention-3|FlashAttention-3]] (Llama 3.1, Qwen 2.5).
- 128K-1M: YaRN-extended RoPE (Llama 3.1 extended, Qwen 2.5).
- 1M+: Gemini 2.5 (proprietary), Ring Attention (research), or accept SSM hybrid limitations.

## Titans and neural memory

[[Titans]] (Behrouz & Hashemi, Google, 2024) introduce a **neural long-term memory** module — a small neural network that learns to memorize and retrieve information across sequences. The architecture combines:

1. **Short-term component**: attention over recent context (standard Transformer).
2. **Long-term memory**: a learned memory module that persists across sequences. The memory is updated via gradient descent on a surprise metric — surprising inputs are memorized, expected inputs are forgotten.
3. **Persistent state**: the memory module's weights are the persistent state, surviving across sequences.

Conceptually, Titans revive the "memory-augmented network" idea from 2014–2017 (Neural Turing Machines, Differentiable Neural Computers) but with modern training; the surprise-based memory update is biologically inspired (the brain consolidates surprising events into long-term memory), and the design is a potential third way beyond attention and SSMs. Per the paper's claims, Titans outperform Transformers and Mamba on long-context tasks (1M+ tokens); independent replication is ongoing as of 2026. [[DeltaNet and Titans]] gives the full treatment.

## Other frontiers

Four more directions round out the frontier. **Continuous learning** aims at models that learn at inference without forgetting. **Neuro-symbolic** approaches combine LLMs with symbolic reasoning (knowledge graphs, theorem provers). **World models** learn a world simulation (Sora, Genie). And **hardware-aware architectures** are designs optimized for specific hardware (Blackwell, Cerebras, Groq).

## Why this matters for AI

The Transformer's dominance is no longer assured; SSMs and hybrids are credible alternatives. For practitioners, this matters when you need very long context (1M+ tokens) — Mamba hybrids may be more efficient; when you need streaming / online inference — SSMs' constant memory is valuable; and when you need maximum reasoning — test-time compute scaling (o1, R1) is the new frontier. The 2024–2026 research period is the most active since 2017's Transformer paper.

## Production implications

For most 2026 production use, Transformers + [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] + [[GQA MQA and MLA|GQA]] are still the right choice. Watch Mamba-based models (Jamba, Falcon-Mamba) for long-context / streaming use cases. Reasoning models (o1, R1) are the right choice for hard problems — accept the latency. And don't bet everything on Transformers; keep an eye on SSM and hybrid developments.

## Interview questions

- **What is the fundamental tradeoff between attention and SSMs?** Attention gives exact recall (it can copy any previous token) and supports in-context learning (via induction heads), but is $O(n^2)$ for training and $O(n)$ for inference (the KV cache grows). SSMs compress history into a fixed-size state, giving $O(n \log n)$ training and $O(1)$ inference, but lose exact recall and have weaker ICL. Hybrids combine both: a few attention layers for recall + ICL, many SSM layers for efficiency.

- **What makes Mamba "selective"?** In standard SSMs, the matrices $\mathbf{B}$ and $\mathbf{C}$ are fixed (input-independent). In Mamba, they are input-dependent — $\overline{\mathbf{B}}(\mathbf{x}_t)$ and $\mathbf{C}(\mathbf{x}_t)$. This lets the model "select" which inputs to remember based on the input itself. The selection mechanism is what enables Mamba to match Transformer quality on language modeling despite the fixed state size.

- **Why do hybrid architectures (Jamba, Zamba) outperform pure Mamba at scale?** At large scale, attention's exact recall and ICL matter more than at small scale. Pure Mamba compresses history into a fixed state, losing exact details. Hybrids add a few attention layers (1:7 ratio is common) for recall and ICL, while using many Mamba layers for efficiency. This gives most of Mamba's efficiency benefit with most of attention's capability benefit.

- **What is test-time compute scaling, and why is it a "new dimension" of capability?** Test-time compute = letting the model "think" longer at inference (longer CoT). Snell et al. (2024) showed accuracy scales as $\log(\text{tokens})$ — more thinking gives better answers, with diminishing returns. Pre-2024, capability came from parameters, data, and training compute. Test-time compute is a fourth dimension, and a smaller model with more thinking can beat a larger model with less thinking on hard problems.

- **How does YaRN extend RoPE to longer contexts?** YaRN (Yet another RoPE extensioN) interpolates the RoPE frequencies non-uniformly — higher frequencies are interpolated more aggressively, lower frequencies less. This extends RoPE models to 4-32× their training length without retraining. The non-uniform interpolation is critical: uniform interpolation (NTK-aware) loses high-frequency information, while YaRN preserves it. Used by Llama 3.1 to extend from 8K to 128K.

- **What are Titans, and how do they differ from attention and SSMs?** Titans (Behrouz & Hashemi 2024) introduce a neural long-term memory module that persists across sequences, updated via gradient descent on a "surprise" metric. Unlike attention (which has no persistent state) or SSMs (which have a fixed state), Titans learn what to memorize and what to forget. Conceptually a third way beyond attention and SSMs, reviving memory-augmented networks with modern training. The paper claims they outperform Transformers and Mamba on 1M+ context; independent replication is ongoing.

## Further reading

- [[Mamba]] — Gu & Dao (2023), *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*.
- [[Mamba-2]] — Dao & Gu (2024), *Transformers are SSMs*.
- [[Jamba]] — Lieber et al. (2024), *Jamba: A Hybrid Transformer-Mamba Language Model*.
- Snell et al. (2024), *Scaling LLM Test-Time Compute Optimally*.
- [[Titans]] — Behrouz & Hashemi (2024), *Titans: Learning to Memorize at Test Time*.

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[Mamba-2 and Structured Attention]] — the SSD unification in detail.
- [[DeltaNet and Titans]] — delta-rule fast weights and neural memory.
- [[Test-Time Compute Scaling]] — the reasoning-model paradigm.
- [[RWKV and RetNet]] — alternative hybrid architectures.
- [[Hyena and Long Convolutions]] — the long-convolution alternative.
- [[Long-Context Architectures]] — context extension techniques.
- [[Research Frontier Update 2026]] — the frontier since this overview.
- [[Reasoning Models]] — production reasoning models.
- [[Linear Attention]] — the conceptual ancestor of SSMs.
