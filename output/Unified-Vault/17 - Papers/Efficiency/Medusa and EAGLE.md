---
title: Medusa and EAGLE
type: concept
aliases: [Medusa, EAGLE, Draft and Verify, Medusa and EAGLE 2024]
tags: [paper, medusa, eagle, speculative-decoding, inference, efficiency, "2024"]
sources:
  - "49 - Medusa and EAGLE 2024"
created_index: 25
---

Medusa and EAGLE are 2024 papers that improve speculative decoding by replacing the separate "draft model" with **extra heads on the target model itself**. This eliminates the need to train and serve a second model, simplifies deployment, and achieves 2–4x speedup over autoregressive decoding with no quality loss. Medusa and EAGLE are now standard in production inference engines (vLLM, TensorRT-LLM, SGLang). See [[Papers MOC]] for the papers index and [[Speculative Decoding]] for the draft-and-verify framework they optimize.

## Citations

**Medusa**: Cai, T., Li, Y., Geng, Z., Peng, H., Lee, J. D., Chen, D., Dao, T. (2024). *Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads*. ICML 2024.

**EAGLE**: Li, Y., Yu, Y., Li, Q., Cui, T., Zhang, W., Yao, Z., He, Y. (2024). *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*. ICML 2024.

## The problem being solved

Standard speculative decoding (Leviathan et al., 2023) uses a small "draft model" to propose K tokens, then the large "target model" verifies them in parallel. Accepted tokens are appended; rejected tokens trigger re-verification from the rejection point. This achieves 2–3x speedup but has practical issues:

1. **Two models to serve**: you need to load both draft and target into GPU memory.
2. **Draft model must be trained**: a separate model for each target.
3. **Distribution mismatch**: if the draft model's distribution differs too much from the target, acceptance rate drops and speedup disappears.
4. **Tree-structured speculation is hard**: linear (single chain) is simple but limited; trees (multiple branches) give better speedup but are complex.

Medusa and EAGLE both eliminate the separate draft model by attaching **extra prediction heads** to the target model itself.

## Medusa's approach

### Multiple heads, one model

Medusa adds K extra prediction heads to the target model's final layer. Head 1 predicts the next token (t+1), head 2 predicts t+2, ..., head K predicts t+K. Each head is a small MLP trained on top of the frozen target model's hidden states.

### Tree-based speculation

At each step:

1. The target model's hidden state is computed once (forward pass).
2. Head 1 proposes top-K candidates for t+1; head 2 proposes top-K for t+2; etc.
3. These candidates form a **tree** of possible continuations.
4. The target model verifies the tree in a single forward pass (using attention masking to process all branches in parallel).
5. Accept the longest valid prefix; reject and re-verify from the rejection point.

### Training

Each Medusa head is trained independently with a simple cross-entropy loss: predict the token at position t+k given the hidden state at position t. The target model is frozen; only the heads are trained. ~1 hour on a single GPU.

## EAGLE's approach

### Feature-level prediction

EAGLE's insight: instead of predicting tokens (which is high-dimensional and noisy), predict the **hidden features** of future positions. A small autoregressive head processes the target model's hidden states and predicts the next hidden state, which is then mapped to a token.

### Why feature-level works better

- Hidden states are smoother and more predictable than token IDs.
- The target model's own vocabulary head can decode the predicted hidden state to a token, ensuring distribution alignment.
- This gives EAGLE higher acceptance rates (85–95%) than Medusa (70–85%).

### Tree-structured speculation

Like Medusa, EAGLE uses tree-structured speculation with a single forward pass for verification. EAGLE's tree structure is dynamically chosen based on the predicted probabilities.

## Key results

### Speedups (over autoregressive decoding)

- **Medusa-1**: 2.3–2.8x on Vicuna-7B/13B.
- **Medusa-2** (with distillation): 2.8–3.5x.
- **EAGLE-1**: 2.5–3.5x on Llama-2-7B/13B/70B.
- **EAGLE-2** (dynamic trees): 3.5–4.5x.

### Quality

Zero quality loss — the output distribution is provably identical to autoregressive decoding (rejection sampling preserves the target distribution).

### Acceptance rate

- Medusa: 70–85% per position.
- EAGLE: 85–95% per position.

EAGLE's higher acceptance rate translates directly to higher speedup.

## Why these papers matter

### Production adoption

Both Medusa and EAGLE are integrated into production inference engines:

- **vLLM**: supports Medusa and EAGLE since v0.5+.
- **TensorRT-LLM**: EAGLE-2 supported; ~3x throughput on Llama-3-70B.
- **SGLang**: native EAGLE support; benchmarks show 4x throughput.
- **HuggingFace TGI**: EAGLE supported.

This makes speculative decoding practical for production — no separate draft model to maintain.

### Eliminated the two-model problem

Previous speculative decoding required training and serving a draft model. Medusa/EAGLE's "heads on the target" approach means a single model artifact. Operational simplicity matters in production.

### Tree-based verification made practical

Tree-structured speculation was theoretical before Medusa/EAGLE. Their efficient tree-verification kernels (single forward pass with attention masking) made it practical. Modern speculative decoding is universally tree-based.

### Foundation for 2025–2026 speculative inference

EAGLE-2 and EAGLE-3 (2025) extended the approach with dynamic tree shapes and longer speculation lengths. The 2026 speculative decoding landscape (MTP — Multi-Token Prediction, used in DeepSeek-V3) builds on Medusa/EAGLE's insights.

## Limitations

- **Memory overhead**: the extra heads and tree verification require more GPU memory. For memory-constrained deployments, vanilla decoding is sometimes preferable.
- **Training cost**: each target model needs its own Medusa/EAGLE heads trained. ~1–4 GPU-hours per model.
- **Quality at K>5**: as K (speculation length) grows, acceptance rate drops. Practical K is 4–8; longer requires EAGLE-3's confidence-aware scheduling.
- **Batched inference**: tree-based speculation interacts poorly with large batch sizes; the speedup is best for batch=1 (interactive) and degrades at batch=64+.

## Comparison

| Method              | Draft Source         | Acceptance Rate | Speedup | Quality Loss |
|---------------------|----------------------|-----------------|---------|--------------|
| Vanilla             | N/A                  | N/A             | 1x      | None         |
| Speculative (Leviathan) | Separate draft model | 70–85%          | 2–3x    | None         |
| Medusa-2            | Heads on target      | 70–85%          | 2.5–3.5x| None         |
| EAGLE-1             | Feature head on target | 85–95%        | 2.5–3.5x| None         |
| EAGLE-2             | Dynamic tree         | 85–95%          | 3.5–4.5x| None         |
| EAGLE-3 (2025)      | Confidence-aware     | 90–97%          | 4–6x    | None         |
| MTP (DeepSeek-V3)   | Multi-token prediction | N/A (joint training) | 2–3x | None         |

## Reception and follow-ups

Medusa and EAGLE were rapidly adopted in production inference engines:

- **vLLM 0.5+** (2024): native Medusa and EAGLE support; production-ready.
- **TensorRT-LLM**: EAGLE-2 supported; ~3x throughput on Llama-3-70B.
- **SGLang**: native EAGLE support; benchmarks show 4x throughput.
- **HuggingFace TGI**: EAGLE supported.
- **EAGLE-2** (2024): dynamic tree shapes; 3.5–4.5x speedup.
- **EAGLE-3** (2025): confidence-aware scheduling; 4–6x speedup; 90–97% acceptance rate.
- **MTP (DeepSeek-V3, 2024)**: Multi-Token Prediction as a training-time alternative to spec decoding; no separate draft model needed.

By 2025, speculative decoding became the default for latency-sensitive LLM serving. Most production deployments of Llama-3, Mistral, and DeepSeek use EAGLE-2 or EAGLE-3.

## Limitations and open questions

- **Memory overhead**: the extra heads and tree verification require more GPU memory. For memory-constrained deployments, vanilla decoding is sometimes preferable.
- **Training cost**: each target model needs its own Medusa/EAGLE heads trained. ~1–4 GPU-hours per model.
- **Quality at K>5**: as K (speculation length) grows, acceptance rate drops. Practical K is 4–8; longer requires EAGLE-3's confidence-aware scheduling.
- **Batched inference**: tree-based speculation interacts poorly with large batch sizes; the speedup is best for batch=1 (interactive) and degrades at batch=64+.
- **Reasoning models**: spec decoding on CoT (but not final answers) is an emerging pattern; o1-style models benefit but the technique needs adaptation.
- **Open question**: can spec decoding be combined with continuous batching without throughput loss? Current implementations sacrifice one for the other.
- **Open question**: is there a theoretical limit to spec decoding speedup? EAGLE-3 achieves 6x; can we reach 10x? Information-theoretic analysis suggests ~8x may be the practical limit.

## Interview questions

1. **Q: How does EAGLE-2 achieve higher acceptance rate than Medusa?**
   A: Two key differences. (1) **Feature-level prediction**: Medusa predicts token IDs directly (high-dimensional, noisy); EAGLE predicts hidden features (smoother, more predictable) and uses the target model's own vocabulary head to decode them to tokens. This ensures distribution alignment. (2) **Dynamic trees**: Medusa uses a static tree structure (same shape every step); EAGLE-2 dynamically chooses the tree shape based on predicted probabilities (more branches where the draft is confident). Both improvements compound: EAGLE-2 gets 85–95% acceptance vs Medusa's 70–85%.

2. **Q: Why is spec decoding output bit-identical to vanilla decoding?**
   A: Spec decoding uses **rejection sampling** to preserve the target model's distribution. For each speculated token: (1) compute the target model's probability P_target(token) and the draft model's probability P_draft(token); (2) accept the token with probability min(1, P_target / P_draft); (3) if rejected, resample from the corrected distribution (P_target - P_draft, normalized). This procedure is provably equivalent to sampling from P_target directly — the output distribution is identical. No quality loss.

3. **Q: When does spec decoding HURT performance?**
   A: Five cases. (1) **Very short generations** (<50 tokens): draft overhead > speedup benefit. (2) **Low acceptance rate** (<50%): rejected drafts waste compute. (3) **Large batch sizes** (>32): tree verification has diminishing returns at high batch. (4) **Code generation**: draft models struggle with code's discrete structure; acceptance rate drops. (5) **Highly creative tasks** (poetry, brainstorming): draft models predict "safe" continuations that get rejected. For these cases, fall back to vanilla decoding. Adaptive routers (like the one in [[Build a Speculative Decoding Server]]) detect these cases and switch modes automatically.

## See also

- [[Papers MOC]] — the papers index.
- [[EAGLE-3]] — the 2025 successor with confidence-aware scheduling.
- [[Multi-Token Prediction]] — the training-time alternative used in DeepSeek-V3.
- [[DeepSeek-V2 and V3]] — DeepSeek-V3 uses MTP, a related idea.
- [[Speculative Decoding]] — the draft-and-verify chapter deep dive.
- [[Decoder-Only Architecture]] — the architecture being accelerated.
- [[KV Cache Mechanics]] — KV cache management in tree verification.
- [[14 - Inference and Production/Inference/vLLM|vLLM]], [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]], [[SGLang]] and [[TGI]] — engines integrating Medusa/EAGLE.
- [[Continuous Batching]] — the throughput-side counterpart.
