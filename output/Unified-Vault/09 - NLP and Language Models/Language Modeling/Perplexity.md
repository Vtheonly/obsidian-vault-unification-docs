---
title: Perplexity
type: concept
aliases: [PPL, Perplexity]
tags: [nlp, language-modeling, perplexity, evaluation, cross-entropy]
sources: ["Perplexity"]
created_index: "04"
---

Perplexity (PPL) is the standard intrinsic evaluation metric for language models: the exponentiated average negative log-likelihood that the model assigns to a held-out sequence. Intuitively, it is the "effective vocabulary size" the model is choosing among at each step, so lower is better. It needs nothing more than forward passes on held-out text — no human judgment, no expensive benchmarks — which is why it has been the reference metric from classical [[N-Gram Language Models]] to modern Transformer LMs. This note covers the definition and the derivation behind the intuition, worked examples and code, what the metric does and does not measure, and how it is used — and misused — in practice.

> [!info] TL;DR
> Perplexity is the **exponentiated average negative log-likelihood** — the "effective vocabulary size" the model is choosing from at each step. Lower is better.

## Definition

For a language model $p_\theta$ and a held-out sequence $w_1, \ldots, w_N$:

$$
\text{PPL} = \exp\left( -\frac{1}{N} \sum_{t=1}^{N} \log p_\theta(w_t \mid w_{<t}) \right)
$$

In words: average the negative log-probability the model assigns to each actual next token, then exponentiate. PPL is monotonic in cross-entropy (`PPL = exp(cross-entropy)`), so minimizing the standard training loss and minimizing perplexity are the same optimization — the metric just re-expresses the loss on a more interpretable scale.

## Intuition

If the model is choosing uniformly between $V$ options at every step, its perplexity is $V$. So perplexity = "how confused is the model, on a scale of vocabulary size?" A model with PPL 1 is certain at every step (overfitting / cheating). A model with PPL = vocab size is guessing uniformly (terrible). Real LMs on real text have PPL in the range 5–50, depending on the dataset. Lower PPL = the model is more confident in the right next token = better language model (intrinsic measure).

## Worked example

Suppose the model assigns these probabilities to the actual next tokens in a 3-token sequence: $0.5, 0.25, 0.1$.

$$
\text{NLL} = -\frac{1}{3} (\log 0.5 + \log 0.25 + \log 0.1) = -\frac{1}{3} (-0.693 - 1.386 - 2.303) = 1.461
$$

$$
\text{PPL} = e^{1.461} \approx 4.31
$$

On average, the model is "choosing between ~4.3 options" at each step.

## Why perplexity is the "effective vocabulary size"

The connection between perplexity and "effective vocabulary size" is not just intuition — it's mathematical. For a uniform distribution over $V$ tokens, the probability of each token is $1/V$. The cross-entropy is:

$$
H = -\log(1/V) = \log V
$$

The perplexity is:

$$
\text{PPL} = e^H = e^{\log V} = V
$$

So a model that guesses uniformly over a vocabulary of size $V$ has perplexity exactly $V$. A model with PPL = 10 is, on average, "as confused as if choosing uniformly among 10 options" — even if the actual vocabulary is 50,000.

### Lower bound: entropy of the language

The theoretical lower bound on perplexity is the **true entropy of the language** — $e^{H(\text{language})}$. For English, estimates range from 5-15 bits/word (depending on the corpus), giving a theoretical PPL lower bound of $e^{5} \approx 148$ to $e^{15} \approx 3.3$M. That is huge — but this is per-**word**, and modern tokenizers split words into multiple tokens, making per-token PPL much lower. One units caveat when quoting such bounds: the 5–15 estimates are entropy in *bits*, while the $e^H$ formula above exponentiates natural units (nats), so informal figures like these mix the two conventions; the qualitative conclusion — the per-word bound sits far above modern per-token PPLs — holds either way.

### Real-world PPL ranges

| Model and eval set | Perplexity |
| --- | --- |
| GPT-2 (2019) on WikiText-103 | ~17-20 |
| GPT-3 (2020) on The Pile validation | ~10-12 |
| Llama 3 8B (2024) on held-out web text | ~5–8 |
| Llama 3 70B | ~4–6 |
| Random model (uniform over 50K vocab) | 50,000 |

The trend: PPL has dropped ~100× from 2019 to 2024. Each halving of PPL corresponds to a significant quality improvement in generation.

## Calculating PPL in code

In PyTorch, perplexity is one exponential on top of the standard cross-entropy loss: shift the logits and labels for next-token prediction, compute the mean cross-entropy (the average NLL), and exponentiate.

```python
import torch
import torch.nn.functional as F

def perplexity(logits, labels):
    """
    logits: (batch, seq, vocab)
    labels: (batch, seq)
    """
    # Shift for next-token prediction
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    
    # Cross-entropy loss = average NLL
    loss = F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.view(-1),
        reduction='mean'
    )
    return torch.exp(loss)
```

## What PPL measures (and doesn't)

On the positive side, PPL measures how well the model fits the distribution of the test text. It is a fast, cheap, automatic intrinsic evaluation — no human judgment needed — and it is comparable across models trained on the same tokenizer and test set.

It does not measure everything, though. It is not **generation quality**: a model with low PPL can still produce repetitive, biased, or hallucinated text. It is not **reasoning ability**: PPL doesn't test logical inference. It is not **instruction-following**: PPL measures text fitting, not task completion. And it does not support **cross-tokenizer comparison**: different tokenizers produce different PPL on the same text — **PPL is only meaningful within the same tokenizer**.

## Relation to other metrics

PPL is monotonic in cross-entropy: `PPL = exp(cross-entropy)`. **Bits-per-character (BPC)** = `cross-entropy / log(2) / num_chars_per_token`; it is used to compare across tokenizers but is rare in modern LLM evaluation (details below). **Downstream task accuracy** (MMLU, HumanEval, etc.) is orthogonal to PPL: a model can have great PPL and poor task accuracy (or vice versa).

## PPL in practice

### For base models

PPL on a held-out corpus (e.g., WikiText-103, The Pile validation set) is the standard "is this model a good language model?" metric.

### For instruction-tuned and chat models

PPL is less useful — these models are optimized for downstream tasks, not raw text fitting. A chat model may have slightly worse PPL than its base version because instruction tuning shifts the distribution.

### For long-context models

PPL is computed on a long document and used to verify that the model "actually uses" the context. If PPL on token $t$ doesn't decrease as more preceding context is added, the model isn't using long context effectively. This is the basis of "needle in a haystack" tests and PPL-vs-position plots.

### For fine-tuning evaluation

Track PPL on a held-out set during fine-tuning. If PPL increases, you're overfitting.

## PPL for long-context evaluation

Modern long-context models (128K-2M tokens) claim to use long context effectively. PPL-vs-position plots verify this:

```python
def ppl_vs_position(model, input_ids, window_size=1000):
    """Compute PPL at each position in a long document."""
    model.eval()
    ppls = []
    with torch.no_grad():
        for start in range(0, len(input_ids) - window_size, window_size // 2):
            end = start + window_size
            chunk = input_ids[start:end]
            logits = model(chunk.unsqueeze(0)).logits
            # PPL for tokens in the second half of the chunk
            # (so they have full preceding context)
            mid = window_size // 2
            shift_logits = logits[0, mid-1:-1]
            shift_labels = chunk[mid:]
            loss = F.cross_entropy(shift_logits, shift_labels)
            ppls.append({
                "position": end - mid,
                "ppl": torch.exp(loss).item(),
            })
    return ppls
```

A well-functioning long-context model shows PPL decreasing as more context is added — the model "uses" the context. If PPL plateaus or increases, the model isn't using long context (common with naive [[RoPE]] extension past training length; see the failure-modes table below for the RoPE-config and YaRN-extension fixes).

### Needle-in-a-haystack tests

The "needle in a haystack" test: insert a specific fact ("the magic number is 42") at a specific position in a long document, then ask the model to retrieve it. Plot retrieval accuracy vs. position. A well-functioning model has uniform accuracy across positions; a broken model has a U-shaped curve (good at start/end, bad in the middle — the "lost in the middle" phenomenon).

## Bits-per-character for cross-tokenizer comparison

PPL is tokenizer-dependent — a model with a finer tokenizer (more tokens per word) will have lower per-token PPL. To compare across tokenizers, use **bits-per-character (BPC)**:

$$
\text{BPC} = \frac{\text{cross-entropy}}{\log 2 \cdot \text{chars-per-token}}
$$

BPC normalizes by character count, making it comparable across tokenizers. However, BPC is rarely used in modern LLM evaluation because (1) modern LLMs use similar BPE tokenizers with similar token-per-word ratios, (2) downstream benchmarks (MMLU, HumanEval) are more relevant than intrinsic PPL/BPC, and (3) character count varies by language (Chinese: 1 char = 1 token; English: ~4 chars = 1 token).

## PPL in modern AI practice

### Pretraining evaluation

Every pretrained model reports PPL on standard corpora (WikiText-103, The Pile, C4). PPL curves during training are diagnostic: loss decreasing indicates healthy training; a loss plateau means the model is at capacity or the learning rate is too high/low; a loss spike means gradient instability.

### Fine-tuning evaluation

Track held-out PPL during SFT/DPO. If PPL increases significantly, the model is overfitting or the fine-tuning distribution is too different from pretraining. For instruction-tuned chat models, PPL is less meaningful (the distribution shifts from pretraining text to instruction-response pairs).

### Contamination detection

If a model has suspiciously low PPL on a benchmark's test set, the test set may be in the pretraining data (contamination). Compare PPL on the benchmark to PPL on similar-but-non-contaminated text — if the benchmark PPL is much lower, it's likely contaminated.

### Anomaly detection in production

Sample production traffic, compute PPL. A sudden PPL spike indicates distribution shift (users are sending different types of queries), a tokenizer issue (new characters or languages), or model degradation (provider updated the model).

## Common pitfalls

Five pitfalls account for most bad PPL numbers. **Comparing PPL across tokenizers** is meaningless: a tokenizer that splits text into 2x more tokens will have lower per-token PPL just because each token is easier to predict. **Comparing PPL across datasets** is equally meaningless — PPL on simple English children's books will be lower than PPL on math papers, regardless of the model. **Forgetting to use `model.eval()` and `torch.no_grad()`** will affect dropout and use memory for gradients. **Computing PPL on training data** is an overfitting indicator — always use held-out text. Finally, **reporting raw PPL without context** makes the number uninterpretable: always state the dataset, tokenizer, and sequence length.

## Why PPL matters

PPL is the **single most-used intrinsic evaluation** for language models. Every model card reports it. It is **cheap** — you don't need human evaluators or expensive benchmarks, just forward passes on held-out text. It is **sensitive** — small architecture changes show up as small PPL changes, which can be hard to detect with downstream benchmarks. And it is the **basis of compression-based anomaly detection** — a sudden PPL spike in production traffic can flag distribution shift.

## Production implications

Monitor PPL on production traffic (sampled): a spike indicates either distribution shift or a tokenizer/config issue. Use PPL for model selection during fine-tuning — save the checkpoint with lowest held-out PPL. Calibrate expectations: a 1% PPL improvement is significant; 10% is large; be skeptical of massive improvements, which usually indicate a methodology bug (e.g., test set contamination). For long-context models, plot PPL at each position in a long document — if PPL doesn't decrease as context grows, your model's "long context" claim is suspect.

## Common failure modes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| PPL much lower than expected | Test set contamination in training data | Check for contamination; use truly held-out data |
| PPL varies wildly across runs | Non-deterministic evaluation | Set seeds; use `model.eval()`; disable dropout |
| PPL increases during fine-tuning | Overfitting; distribution shift | Reduce LR; fewer epochs; check eval set |
| PPL on long context doesn't improve | Model not using long context | Check RoPE config; use YaRN extension; verify attention |
| PPL comparison across tokenizers | Meaningless | Use BPC or downstream benchmarks instead |
| PPL very low but generation is bad | Model overfits text but can't do tasks | Use downstream benchmarks; PPL ≠ capability |

## Interview questions

**Q: What is perplexity, and how is it related to cross-entropy?**
A: PPL = exp(cross-entropy) = exp(average NLL). It's the "effective vocabulary size" — a model with PPL = 10 is, on average, as confused as if choosing uniformly among 10 options. For a uniform distribution over $V$ tokens, PPL = $V$ exactly. Lower PPL = better language model (intrinsic measure).

**Q: Why can't you compare PPL across different tokenizers?**
A: PPL is per-token. A tokenizer that splits text into 2× more tokens will have lower per-token PPL just because each token is easier to predict (shorter, more common). To compare across tokenizers, use bits-per-character (BPC) = cross-entropy / (log 2 × chars-per-token), which normalizes by character count. Or use downstream benchmarks, which are tokenizer-independent.

**Q: How would you use PPL to detect test set contamination?**
A: Compute PPL on the benchmark's test set and on similar-but-non-contaminated text (same domain, same era). If the benchmark PPL is much lower (e.g., 50% lower), the test set is likely in the pretraining data — the model has memorized it. This is a standard contamination detection technique, used in GPT-3, Llama, and other model evaluations.

**Q: How does PPL-vs-position evaluation verify long-context claims?**
A: Plot PPL at each position in a long document. A well-functioning long-context model shows PPL decreasing as more preceding context is added — the model "uses" the context. If PPL plateaus or increases past the training length, the model isn't using long context (common with naive RoPE extension). The "needle in a haystack" test is a related retrieval-based evaluation.

**Q: Why is PPL less meaningful for instruction-tuned chat models?**
A: Instruction tuning shifts the distribution from pretraining text (web, books, code) to instruction-response pairs. A chat model may have slightly worse PPL on raw text because it's optimized for task completion, not text fitting. PPL measures text fitting, not task completion. Use downstream benchmarks (MMLU, HumanEval, MT-Bench) for chat model evaluation.

**Q: A model has PPL 5 on your eval set. Is it a good model?**
A: Can't say without context. PPL is only meaningful relative to (1) the same tokenizer, (2) the same eval set, (3) similar model sizes. PPL 5 on WikiText-103 with a 50K BPE tokenizer and a 70B model is good. PPL 5 on simple children's books with a 1K word-level tokenizer and a 100M model is mediocre. Always report PPL with: dataset, tokenizer, model size, and context length.

## Further reading

Goodfellow et al., *Deep Learning* — Chapter 3.13 (Information Theory) — grounds the entropy view. The GPT-2 paper (Radford et al., 2019) reports PPL on multiple datasets, and the Llama 3 paper reports PPL on long-context benchmarks.

## See also

- [[NLP and Language Models MOC]] — area overview
- [[N-Gram Language Models]] — early PPL benchmarks
- [[Tokenization Overview]] — PPL depends on the tokenizer
- [[BPE]] — the modern tokenizer most PPL numbers assume
- [[GPT Family]] — PPL is the training objective of decoder-only autoregressive LMs
- [[RoPE]] — naive extension past training length hurts long-context PPL
- [[YaRN and NTK-Aware Scaling]] — long-context PPL evaluation and extension schemes
