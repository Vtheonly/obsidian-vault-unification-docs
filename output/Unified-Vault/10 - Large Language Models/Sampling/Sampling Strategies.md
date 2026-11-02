---
title: Sampling Strategies
type: concept
aliases: [Decoding Strategies]
tags: [llm, inference, sampling, decoding]
sources: ["03 - Sampling Strategies"]
created_index: 7
---

> [!info] TL;DR
> How to turn an LLM's output logits into actual tokens. Covers greedy, beam search, temperature, top-k, top-p (nucleus), repetition penalties, and the modern defaults that most LLM APIs use.

At each generation step a language model emits a raw score for every token in its vocabulary, and something has to turn those scores into the single next token that continues the sequence. That conversion is the sampling strategy — also called a decoding strategy — and it dramatically affects output quality, diversity, and tone. This note covers the full menu: greedy decoding, beam search, temperature scaling, top-k, top-p (nucleus), min-p, repetition penalties, Mirostat, typical sampling, constrained decoding, and classifier-free guidance, along with the combined recipe, a worked comparison, and the defaults that production LLM APIs actually use. It is a core inference-side topic within [[Large Language Models MOC]].

## From logits to tokens

At each generation step, the LLM outputs a **logit vector** $\mathbf{z} \in \mathbb{R}^{|V|}$ over the vocabulary. To produce the next token, we need to convert this distribution into a single choice (or a sample).

The choice of conversion is the **sampling strategy**. Everything downstream of the model is a probability operation on that vector: softmax and sampling are probability operations, the softmax itself rests on an entropy and cross-entropy foundation, and nearly every knob below works by reshaping the distribution before a token is drawn.

## Greedy decoding

Greedy decoding picks the highest-probability token at every step:

$$
\hat{y}_t = \arg\max_{y} p(y \mid \hat{y}_{<t})
$$

It is deterministic, fast, and simple, which makes it the right choice when you need determinism (e.g., code generation with a fixed seed) or for short outputs. The price is diversity: greedy is prone to repetition loops ("I am I am I am...") and produces generic, low-diversity text — the classic "boring/generic output" failure that traces back to temperature=0. Most production LLM APIs default to **greedy when temperature=0**, and greedy also serves as the deterministic fallback when a rerun must reproduce exactly.

## Beam search

Beam search maintains $k$ "beams" (partial sequences) at each step, expands each by one token, and keeps the top $k$ by cumulative log-probability; at the end, it returns the highest-scoring beam. It is better than greedy for tasks with a clear objective (translation, summarization), where there is effectively one best answer to find. The costs: it is expensive ($k \times$ compute), still prone to generic outputs, and bad for open-ended generation. Its natural habitat is classical MT and summarization; it is rare in modern LLM chat.

Beam search has largely fallen out of favor for chat/agentic LLMs. Sampling-based methods produce more natural text, so the practical rule is beam search for clear-objective tasks and sampling for open-ended generation (chat, creative writing) where diversity matters — which is also why most modern APIs default to sampling (temperature + top-p).

## Temperature scaling

Temperature scaling divides the logits by a temperature $T$ before softmax:

$$
p(y) = \text{softmax}(\mathbf{z} / T)
$$

At $T = 1$ you get the original distribution. $T < 1$ (e.g., 0.7) gives a **sharper** distribution — more confident, less diverse — and is greedy in the limit $T \to 0$. $T > 1$ (e.g., 1.5) gives a **flatter** distribution — more random, more diverse. Temperature is the single most important sampling parameter, and most APIs expose it.

The key insight: $p = \text{softmax}(z/T)$ does not change which token is most likely — it changes the spread. Low temperature makes decoding more deterministic (T=0 is greedy, i.e., argmax); high temperature makes it more creative but potentially incoherent.

### Rule of thumb

Sensible temperatures cluster by task type:

| Task                        | Temperature |
|-----------------------------|-------------|
| Code generation             | 0.0–0.2     |
| Factual Q&A                 | 0.0–0.3     |
| Summarization               | 0.3–0.5     |
| General chat                | 0.7–0.9     |
| Creative writing            | 0.9–1.2     |
| Brainstorming               | 1.0–1.5     |

## Top-k sampling

Top-k sampling samples only from the top $k$ most likely tokens at each step:

1. Sort tokens by probability, keep top $k$.
2. Renormalize their probabilities to sum to 1.
3. Sample from this restricted distribution.

The benefit: it prevents sampling extremely unlikely tokens, which temperature alone allows. The drawback: $k$ is fixed — bad when the distribution is sharp (top 1 is enough) or flat (top 50 isn't enough). When only 1-2 tokens are genuinely good, $k = 50$ lets in noise. A typical $k$ is 40–50. Top-k earns its keep for code generation, where you want to limit the model to plausible completions.

## Top-p (nucleus) sampling

Top-p (nucleus) sampling samples from the smallest set of tokens whose cumulative probability $\geq p$:

1. Sort tokens by probability (descending).
2. Take tokens until cumulative probability $\geq p$.
3. Renormalize and sample from this set.

It is adaptive — a small set when the distribution is sharp, a large set when flat — at the cost of being slightly more expensive than top-k. A typical $p$ is 0.9–0.95. Top-p is generally preferred over top-k for chat applications, and most modern LLM APIs default to top-p = 0.9 or 1.0 with a temperature.

## Min-p sampling

Min-P (Minimum-P) sampling, a newer (2024) alternative to top-p, sets a minimum probability threshold relative to the top token:

$$
\text{threshold} = p_{\text{min}} \cdot \max_i p_i
$$

Only tokens with $p_i \geq \text{threshold}$ are kept. This is adaptive: when the distribution is sharp (one dominant token), the threshold is high (few tokens survive); when flat, the threshold is low (many tokens survive).

Its advantages over top-p: it is simpler to reason about — one parameter ($p_{\text{min}} = 0.05$) versus top-p's $p = 0.9$; it is better at avoiding bad tokens, because top-p can include unlikely tokens when the distribution is flat while min-p naturally excludes them; and it is more robust across different model sizes and vocabularies. Adoption is increasing — some local LLM libraries (llama.cpp) now support min-p. In one line: the cutoff is threshold = $p_{\text{min}} \cdot \max_i p_i$, and everything below it is masked out.

## Combining temperature, top-k, and top-p

In practice the filters stack rather than compete. The standard recipe:

1. Divide logits by temperature.
2. Apply top-k filter (if $k < |V|$).
3. Apply top-p filter (if $p < 1$).
4. Softmax the filtered logits (with $-\infty$ for excluded tokens).
5. Sample.

A complete implementation looks like this:

```python
def sample(logits, temperature=0.7, top_k=50, top_p=0.9):
    if temperature == 0:
        return logits.argmax(dim=-1)

    logits = logits / temperature

    # Top-k
    if top_k > 0:
        top_k = min(top_k, logits.size(-1))
        vals, _ = torch.topk(logits, top_k)
        thresh = vals[..., -1, None]
        logits = torch.where(logits < thresh, float('-inf'), logits)

    # Top-p
    if top_p < 1.0:
        sorted_logits, sorted_idx = torch.sort(logits, descending=True)
        cum_probs = F.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
        # Shift right so we always keep at least one token
        sorted_remove = cum_probs > top_p
        sorted_remove[..., 1:] = sorted_remove[..., :-1].clone()
        sorted_remove[..., 0] = False
        indices_to_remove = sorted_remove.scatter(-1, sorted_idx, sorted_remove)
        logits = logits.masked_fill(indices_to_remove, float('-inf'))

    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, num_samples=1).squeeze(-1)
```

Note how `temperature == 0` short-circuits to argmax — explicit handling of the greedy edge case, which matters because libraries disagree about what temperature zero means.

## Repetition penalties

To discourage repeating recent tokens, apply a penalty to tokens that already appeared. Three variants are in common use.

### Frequency penalty

Subtract a constant from each token's logit proportional to how many times it has appeared:

$$
z_i' = z_i - \lambda \cdot \text{count}(i)
$$

### Presence penalty

Subtract a constant from any token that has appeared at least once:

$$
z_i' = z_i - \lambda \cdot \mathbb{1}[\text{count}(i) > 0]
$$

### The original CTRL penalty

Multiply the log-probability by a factor $< 1$ for tokens that appeared:

$$
p_i' = p_i / \lambda^{\text{count}(i)}
$$

This is what HuggingFace's `RepetitionPenaltyLogitsProcessor` implements.

The API surface differs by vendor: OpenAI's API exposes `frequency_penalty` and `presence_penalty` (separately), while most local LLM libraries expose a single `repetition_penalty`.

The trade-offs deserve respect. All of these schemes discourage loops like "I am I am I am" by reducing the logit of tokens that already appeared, $z_i' = z_i - \lambda \cdot \text{count}(i)$. But a penalty that is too aggressive (>1.3) degrades output quality, because domain terms that legitimately repeat get suppressed. The frequency penalty (proportional to count) is more aggressive than the presence penalty (binary), and neither distinguishes between content words ("the") and meaningful repetitions (technical terms). Use them sparingly; the usual defaults sit at 1.1-1.2.

## Mirostat: adaptive surprise control

Mirostat (Basu et al., 2020) is an adaptive sampling algorithm that maintains a target "surprise" level (entropy). The key insight: text quality correlates with consistent surprise — too little surprise means repetitive text; too much means incoherent text. It is a good fit for keeping output diverse without going off the rails, which is why some local LLM libraries (llama.cpp) use it.

The algorithm:

1. Track the running average surprise $S$ of generated tokens.
2. Adjust temperature dynamically: if $S$ is below target $\tau$, increase temperature; if above, decrease.
3. Use a feedback loop: $\mu \leftarrow \mu - \eta (S - \tau)$, where $\mu$ controls the effective temperature.

Mirostat-3 (2024) improves on the original with better feedback control and supports top-k/top-p filtering alongside the adaptive temperature. It remains rare in API-based serving, because the per-token adaptation it requires doesn't batch well.

## Other strategies

### Typical sampling

Typical sampling (Meister et al., 2022) samples from tokens whose per-token information is close to the expected information. It is theoretically motivated but rare in production.

### Constrained decoding

Constrained decoding restricts the output to a formal grammar (regex, JSON schema, context-free grammar). It is the tool for structured output, implemented by Outlines, Guidance, lm-format-enforcer, and OpenAI's "structured outputs".

It composes with the stochastic knobs in a fixed order: constrained decoding masks invalid tokens to $-\infty$ before softmax, and temperature and top-p are applied after masking. The full sequence is (1) compute logits, (2) apply constraint mask, (3) divide by temperature, (4) apply top-k/top-p, (5) softmax, (6) sample. Because the constraint reduces the effective vocabulary, temperature may need to be lower than unconstrained — the model has fewer choices, so there is less need for randomness.

### Classifier-free guidance

For conditional generation (e.g., with a system prompt), classifier-free guidance (CFG) scales the difference between conditional and unconditional logits:

$$
\mathbf{z}' = \mathbf{z}_{\text{uncond}} + \alpha (\mathbf{z}_{\text{cond}} - \mathbf{z}_{\text{uncond}})
$$

Larger $\alpha$ → more "guidance" toward the condition. It is common in image diffusion, less common in LLMs, but gaining traction.

## The probability distribution view

All sampling strategies modify the same underlying distribution $p(y) = \text{softmax}(z / T)$. The modifications are:

| Strategy | Modification | Effect |
|----------|-------------|--------|
| Temperature | $z \to z / T$ | Sharpen (T<1) or flatten (T>1) |
| Top-k | $p_i = 0$ for $i \notin \text{top-}k$ | Truncate tail |
| Top-p | $p_i = 0$ for $i$ outside nucleus | Adaptive truncation |
| Min-p | $p_i = 0$ for $p_i < p_{\text{min}} \cdot \max_j p_j$ | Relative threshold |
| Repetition | $z_i \to z_i - \lambda \cdot \text{count}(i)$ | Penalize repeats |
| CFG | $z \to z_{\text{uncond}} + \alpha (z_{\text{cond}} - z_{\text{uncond}})$ | Amplify conditioning |

These are all **logit-level transformations** followed by softmax and sampling. The order matters: typically temperature → top-k → top-p → repetition penalty → sample.

## Worked example: comparing strategies

The script below applies each strategy to the same ten-token logit vector, printing the distribution that survives each filter:

```python
import torch
import torch.nn.functional as F

logits = torch.tensor([5.0, 3.0, 2.0, 1.5, 1.0, 0.5, 0.1, -0.5, -1.0, -2.0])

# Temperature
for T in [0.5, 1.0, 2.0]:
    probs = F.softmax(logits / T, dim=-1)
    print(f"T={T}: {probs.tolist()}")

# Top-k=3
vals, idx = torch.topk(logits, 3)
mask = torch.full_like(logits, float('-inf'))
mask[idx] = 0
print(f"Top-k=3: {F.softmax(logits + mask, dim=-1).tolist()}")

# Top-p=0.9
sorted_logits, sorted_idx = torch.sort(logits, descending=True)
cum_probs = F.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
sorted_remove = cum_probs > 0.9
sorted_remove[1:] = sorted_remove[:-1].clone()
sorted_remove[0] = False
indices_to_remove = sorted_remove.scatter(-1, sorted_idx, sorted_remove)
print(f"Top-p=0.9: {F.softmax(logits.masked_fill(indices_to_remove, float('-inf')), dim=-1).tolist()}")

# Min-p=0.05 (relative to max probability)
probs = F.softmax(logits, dim=-1)
threshold = 0.05 * probs.max()
min_p_mask = probs < threshold
print(f"Min-p=0.05: {F.softmax(logits.masked_fill(min_p_mask, float('-inf')), dim=-1).tolist()}")
```

## Why sampling choices matter

Sampling strategy is one of the **highest-leverage production knobs**. A bad choice can make a good model look terrible (greedy → repetitive; high temperature → incoherent). Different tasks need different strategies — don't use the same defaults for code, chat, and creative writing. Structured output (JSON, function calls) requires constrained decoding, and it is becoming a standard feature of LLM APIs. For agentic systems, sampling strategy affects reliability: slightly lower temperatures often improve tool-call correctness.

## Production guidance

The default recipe for chat is temperature 0.7, top_p 0.9, top_k 50, repetition_penalty 1.1 — most users won't tune these. For code and structured output, use temperature 0.0–0.2, with constrained decoding if applicable. For RAG, use temperature 0.0–0.3 — you want grounded, low-creativity answers. For agents, use temperature 0.0–0.5 for tool calling (reliability matters), but maybe 0.7+ for exploratory planning steps.

Operationally, streaming means sampling one token at a time and decoding incrementally — most APIs do this — and seeding (passing a seed for reproducibility) is the standard trick for testing.

Sampling also touches the rest of the stack: it happens after the KV cache lookup; benchmark evaluation uses temperature=0; sampling choices affect in-context learning consistency; gateways and routers carry per-request sampling params; speculative decoding requires the draft model to match the target's sampling; and self-consistency-style prompting samples multiple chains at T>0.

## Common pitfalls and failure modes

The recurring mistakes:

- **Temperature = 0 with sampling** — different libraries handle this differently. Some return argmax, some divide by zero. Be explicit.
- **Forgetting to apply the same chat template** that the model was trained with — produces silent quality loss.
- **Aggressive repetition penalty** (>1.3) — degrades output quality, makes it harder to use domain terms that legitimately repeat.
- **Top-p = 1.0 with high temperature** — can produce incoherent text because very unlikely tokens get sampled.
- **Mixing strategies inconsistently** across prompts in a batch — vectorized sampling assumes all sequences use the same parameters.

When output misbehaves, the symptom usually names the culprit knob:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Repetitive output | Temperature too low; or no repetition penalty | Increase T to 0.7+; add repetition penalty 1.1-1.2 |
| Incoherent output | Temperature too high; or top-p too permissive | Lower T to 0.3-0.7; set top-p=0.9 |
| Hallucinated tokens | Top-p=1.0 allows very unlikely tokens | Set top-p=0.9 or top-k=50 |
| Boring/generic output | Temperature=0 (greedy) | Increase T to 0.7+ for creative tasks |
| Cannot produce valid JSON | Free-form sampling includes invalid tokens | Use constrained decoding (JSON schema) |
| Different results on rerun | Stochastic sampling without seed | Set seed; or use temperature=0 for determinism |

## Further reading

The primary papers, one per strategy:

- Holtzman et al. (2019), *The Curious Case of Neural Text Degeneration* — nucleus sampling.
- Keskar et al. (2019), *CTRL: A Conditional Transformer Language Model for Controllable Generation* — repetition penalty.
- Meister et al. (2022), *Typical Decoding for Natural Language Generation*.
- Fan et al. (2018), *Hierarchical Neural Story Generation* — top-k sampling.

## See also

- [[Large Language Models MOC]] — the area orientation for this note.
- [[KV Cache Mechanics]] — sampling happens after the KV cache lookup.
- [[Decoder-Only Architecture]] — the autoregressive next-token setup that produces the logits being sampled.
- [[In-Context Learning]] — sampling affects in-context learning consistency.
- [[LLM Benchmarks]] — benchmark evaluation uses temperature=0.
- [[Hallucination]] — sampling very unlikely tokens is one route to hallucinated output.
- [[Constrained Decoding]] — restricting output to valid formats.
- [[Speculative Decoding]] — the draft model must match the target's sampling.
- [[Gateway and Router Patterns]] — per-request sampling params.
- [[Inference and Production MOC]] — the production-side companion area.
