---
title: Speculative Decoding
type: concept
aliases: [Speculative Decoding, Speculative Sampling, Draft-Model Speculative Decoding]
tags: [inference, speculative-decoding, acceleration, llm, serving]
sources: ["Speculative Decoding"]
created_index: 11
---

Speculative decoding accelerates autoregressive LLM inference by letting a small "draft" model propose multiple tokens and having the large "target" model verify them all in a single forward pass. Because the accept/reject step is an importance-sampling correction, the output distribution is provably identical to sampling from the target model alone, so the 2–3x speedup comes with no quality loss. This note covers why decoding is slow, the algorithm and its guarantee, the speedup arithmetic, the full menu of draft-model choices, tree-based speculation, a reference implementation sketch, and the production caveats that decide when the technique pays off.

> [!info] TL;DR
> Speculative decoding accelerates autoregressive LLM inference by using a small "draft" model to propose multiple tokens, then having the large "target" model verify them in a single forward pass. Accepted tokens come free (one forward pass produces multiple tokens); rejected tokens are resampled. 2–3x speedup with no quality loss.

## The problem: autoregressive decoding is slow

During decode, each new token requires a full forward pass through the model. For a 7B model at batch size 1, this is ~5 ms per token (memory-bound on weights). Generating 1000 tokens takes ~5 seconds.

The key observation: during decode at batch size 1, the GPU is **massively underutilized**. The weights are read once per token, but only a tiny amount of compute is done. There's room to do more work per weight read.

## The insight: draft cheaply, verify in one pass

If we had a smaller "draft" model that's 5–10x faster, it could propose the next few tokens cheaply. The large "target" model could then verify all those tokens in **one forward pass** (which costs the same as generating one token). If the draft's tokens match what the target would have produced: accept them all — got 4 tokens for the price of 1. If the draft's tokens mismatch: reject and resample from the target's distribution.

Because verification can be done in parallel (just compute the target's distribution at each position), this is much faster than serial generation.

## The algorithm

```text
1. Draft model generates k candidate tokens: y_1, y_2, ..., y_k
2. Target model runs ONE forward pass over (prompt + y_1, ..., y_k)
   → produces distributions p_1, p_2, ..., p_k at each position
3. For each i from 1 to k:
   - If y_i was sampled from draft's q_i with probability q_i(y_i)
   - And target's p_i(y_i) > q_i(y_i) → accept y_i
   - Else: accept with probability p_i(y_i) / q_i(y_i)
     - If accepted: continue
     - If rejected: resample from adjusted distribution and stop
4. If all k accepted: bonus sample one more from p_k (free!)
5. Repeat
```

The acceptance criterion (step 3) is **importance sampling**. The math guarantees that the final distribution is **exactly the same** as sampling from the target model alone — no quality loss.

### Why no quality loss

The acceptance/rejection resampling is mathematically equivalent to sampling from $p$ directly: accept token $y_i$ with probability $\min(1, p(y_i)/q(y_i))$, where $p$ is the target's distribution and $q$ is the draft's. If rejected, resample from the adjusted distribution $(p - q)_+$ normalized. The draft model only affects speed (how often tokens are accepted), not the output distribution. This is the key result from Leviathan et al. (2023) and Chen et al. (2023).

## Speedup analysis

If the draft model has acceptance rate $\alpha$ (fraction of tokens accepted) and proposes $k$ tokens per round, the expected tokens per target forward pass is $\frac{1 - \alpha^{k+1}}{1 - \alpha}$ (geometric series). Concretely:

- If $\alpha = 0.7, k = 4$: ~2.5 tokens per target pass — **2.5x speedup**.
- If $\alpha = 0.5, k = 4$: ~1.94 tokens per target pass — ~2x speedup.
- If $\alpha = 0.9, k = 7$: ~4.5 tokens per target pass — **4.5x speedup**.

The same arithmetic extended downward shows where the technique stops paying: with $k=4$ draft tokens, acceptance rate $\alpha = 0.7$ gives ~2.5x speedup, $\alpha = 0.5$ gives ~2x, and $\alpha = 0.3$ gives ~1.3x (barely worth it). Below 30% acceptance, the draft overhead exceeds the verification savings. A good draft model (same family, smaller) typically achieves 60-80% acceptance. The key is having a good draft model — high acceptance rate is what drives speedup.

## Draft model choices

The draft model is a genuine architectural choice, and there are six established families, each trading off acceptance rate, draft speed, and engineering cost.

### Same family, smaller version

Target: Llama 3 70B, Draft: Llama 3 8B. The pros are the same tokenizer, same training distribution, and high acceptance rate; the con is that 8B is still relatively large for a draft.

### Distilled draft

Train a small model to mimic the target's output distribution. Small, fast, and it can be very accurate, but it requires training and is per-target.

### N-gram draft (lookahead)

Use simple statistics (e.g., n-gram frequencies from the prompt) to predict the next tokens. No model is needed and it is very fast, but the acceptance rate is low for non-repetitive text. In more detail: build an n-gram model on-the-fly from the prompt (count n-gram frequencies), and use it to predict the next $k$ tokens. The n-gram model is essentially free ($O(N)$ to build, $O(1)$ to query). Hit rate: 30-60% for repetitive content (code, structured output). No separate model to load — just prompt statistics. Used by some vLLM configurations.

### Self-speculation (layer skip)

Use the target model itself but skip early — only run the first $L'$ layers, then predict. No separate draft model is needed, but this requires model architecture support (e.g., Medusa heads).

### Medusa heads

Add extra "tree" heads to the target model that predict multiple future tokens directly. No separate draft model, and high acceptance — but it requires fine-tuning the target.

### EAGLE

A learned draft model that takes the target's hidden states as input, achieving higher acceptance than vanilla spec decoding (which uses a separate small model). EAGLE-2 and EAGLE-3 improve further with dynamic draft trees: EAGLE-2 adds dynamic draft trees (the tree structure adapts based on context), and EAGLE-3 further improves with better feature extraction. EAGLE typically achieves 3-5x speedup vs 2-3x for vanilla.

## Tree-based speculation

Modern speculative decoding (EAGLE, Medusa) uses **tree-structured** drafts instead of linear sequences. The draft proposes multiple candidate continuations in a tree, and the target verifies all of them in parallel using a single attention mask:

```text
Linear: y_1 → y_2 → y_3 → y_4

Tree:
       y_1
      / | \
    y_2 y_2' y_2''
    /   |    \
  y_3  y_3'  y_3''
```

The linear case proposes one sequence $y_1 \to y_2 \to y_3 \to y_4$; if $y_2$ is rejected, $y_3$ and $y_4$ are wasted. A tree proposes multiple branches at each position, so if one branch is rejected, another may succeed — the draft can hedge its bets, and the target's forward pass handles all branches via a custom attention mask. This hedges bets in one verification pass — much more efficient, and it is why EAGLE-2/3 achieve 3-5x speedup vs 2-3x for linear.

## Implementation sketch

The following sketch (both models at temperature 0.7) shows the full loop — drafting, one batched target pass, acceptance, resampling on rejection, and the bonus token:

```python
def speculative_decode(target_model, draft_model, prompt, max_tokens, k=4):
    generated = prompt
    while len(generated) < max_tokens:
        # 1. Draft k tokens
        draft_tokens = []
        draft_dists = []
        context = generated
        for _ in range(k):
            logits = draft_model(context)
            next_dist = F.softmax(logits[:, -1] / 0.7, dim=-1)
            next_token = torch.multinomial(next_dist, 1)
            draft_tokens.append(next_token)
            draft_dists.append(next_dist)
            context = torch.cat([context, next_token], dim=-1)

        # 2. Target forward pass over all k+1 positions (parallel)
        target_logits = target_model(context)  # one forward pass
        target_dists = F.softmax(target_logits[:, -k-1:-1] / 0.7, dim=-1)

        # 3. Accept/reject
        accepted = 0
        for i in range(k):
            y = draft_tokens[i]
            q = draft_dists[i][..., y]
            p = target_dists[i][..., y]

            if p >= q or torch.rand(1) < p / q:
                # Accept
                accepted += 1
            else:
                # Reject; resample from (p - q)_+ normalized
                adjusted = (target_dists[i] - draft_dists[i]).clamp(min=0)
                adjusted = adjusted / adjusted.sum()
                new_token = torch.multinomial(adjusted, 1)
                generated = torch.cat([generated] + draft_tokens[:accepted] + [new_token], dim=-1)
                break
        else:
            # All accepted; bonus sample from p_k
            bonus = torch.multinomial(target_dists[-1], 1)
            generated = torch.cat([generated] + draft_tokens + [bonus], dim=-1)

    return generated
```

Three structural requirements are visible in the code: the draft and target run at the same temperature (the acceptance criterion is only correct when both distributions are computed under it), verification happens in one batched forward pass over all $k+1$ positions, and rejection resamples from the adjusted distribution $(p - q)_+$ normalized.

## When speculative decoding does not help

There are four situations where the technique loses. First, high batch sizes: the GPU is already compute-bound, and the extra draft work just adds load — spec decoding helps most at batch size 1, which is memory-bound. Second, a bad draft model: if the acceptance rate is <30%, it's slower than no speculation. Third, short sequences: the setup cost exceeds the speedup. Fourth, non-repetitive text: acceptance is lower than for repetitive or code text.

## Why this matters

Speculative decoding is **the** inference acceleration technique for memory-bound (batch-size-1) generation. It's increasingly standard in production. The "no quality loss" guarantee is critical — you get speedup without changing model behavior. The draft model is a new architectural choice: as of 2026, most open models ship with a recommended draft model (e.g., Llama 3 70B + Llama 3 8B as draft). Spec decoding also interacts with batching in complex ways — at high batch sizes the GPU becomes compute-bound and spec decoding helps less (or hurts), while at low batch sizes it's pure win.

## Production implications

For interactive (batch size 1) generation, spec decoding gives 2–3x speedup — always enable it if you have a good draft model. For batched (high-throughput) generation, spec decoding may not help: the GPU is already compute-bound, and the extra draft work just adds load. Use vLLM or TGI's built-in spec decoding — they handle the implementation correctly, including tree-based speculation. Draft model choice matters more than the algorithm: a bad draft (low acceptance) gives no speedup. And there is a memory cost — you need to load both target and draft in GPU memory; for a 70B + 8B pair, that's ~150 GB in fp16 — multi-GPU required.

## Common pitfalls

> [!warning]
> The two correctness traps: forgetting to verify (just accepting the draft tokens without verification produces wrong outputs — the draft's distribution, not the target's), and a wrong temperature in the draft (the draft and target must use the same temperature for the acceptance criterion to be correct).

The recurring failure modes:

- **Bad draft model** — if acceptance rate is < 30%, spec decoding is slower than no spec decoding.
- **Forgetting to verify** — a common bug is to just accept the draft tokens without verification. This produces wrong outputs (the draft's distribution, not the target's).
- **Wrong temperature in draft** — the draft and target must use the same temperature for the acceptance criterion to be correct.
- **Non-deterministic verification** — must verify in a single batched forward pass; per-token verification loses the speedup.
- **Token-by-token attention** — must use causal attention across all draft tokens in a single pass; this requires careful mask construction.

## Further reading

For primary sources, see Leviathan, Kalman, and Matias (2023), *Fast Inference from Transformers via Speculative Decoding*; Chen et al. (2023), *Accelerating Large Language Model Decoding with Speculative Sampling*; Cai et al. (2024), *Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads*; and Li et al. (2024), *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[PagedAttention]] — draft and target share prefix blocks.
- [[KV Cache Mechanics]] — what makes decode memory-bound in the first place.
- [[Sampling Strategies]] — draft and target must use the same temperature.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — supports speculative decoding.
- [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — also supports speculative decoding.
- [[N-Gram Language Models]] — the statistics behind n-gram drafts.
- [[Continuous Batching]] — the batching regime that decides when speculation pays off.
