---
title: Gemma Architecture
type: concept
aliases: [Gemma Architecture, Gemma 2 3, Google Open Weights]
tags: [model-architecture, gemma, google, open-source]
sources: ["06 - Gemma Architecture"]
created_index: 17
---

Gemma is Google's open-weights LLM family (2B, 7B, 9B, 27B), derived from the research and technology used for Gemini. Architecturally it is similar to Llama — decoder-only, GQA, RoPE, RMSNorm — but with distinctive choices: a very large vocabulary (256K), local attention with global periodic attention (Gemma 2), and logit soft-capping for training stability. Gemma 2 (2024) achieved strong quality for its size, making it competitive with Llama 3 and Mistral.

> [!info] Source status
> All claims are **officially confirmed** — documented in Google DeepMind's Gemma and Gemma 2 technical reports and model cards.

## The Gemma lineage

The family grew from a single February 2024 release into code-specialized, recurrent, and multimodal offshoots:

| Version        | Release    | Sizes       | Key features                                |
|----------------|------------|-------------|---------------------------------------------|
| Gemma 1        | Feb 2024   | 2B, 7B      | GQA, RoPE, 256K vocab                       |
| Gemma 2        | June 2024  | 2B, 9B, 27B | Local + global attention, logit soft-capping |
| CodeGemma      | April 2024 | 2B, 7B      | Code-specialized                            |
| RecurrentGemma | 2024       | 2B, 9B      | Griffin architecture (RNN + attention)      |
| Gemma 3        | 2025       | Multiple    | Multimodal, larger context                  |

## Gemma 1 (February 2024)

### Architecture

Gemma 1 is architecturally similar to Llama 2, with a few key differences:

| Property | Gemma 2B | Gemma 7B |
|----------|----------|----------|
| Parameters | 2.5B | 8.5B |
| Layers | 18 | 28 |
| d_model | 2048 | 3072 |
| Heads | 8 | 16 |
| KV heads | 1 (MQA) | 8 (GQA) |
| Context | 8K | 8K |
| Vocab | 256K | 256K |
| RoPE base | 10000 | 10000 |

### Key architectural choices

Gemma's 256K vocabulary was the largest among major open-weights LLMs at the time. It better supports multilingual text (SentencePiece-based tokenizer), better supports code (many tokens per language), and reduces sequence length for non-English text. The trade-off is a large embedding matrix (256K × d_model), which adds ~500M parameters for the 7B model.

The two sizes make opposite attention trade-offs. Gemma 2B uses multi-query attention (1 KV head) — the most aggressive KV cache reduction. This makes the 2B model very efficient to serve, at some quality cost. The 7B model uses GQA (8 KV heads) — a more balanced choice. See [[GQA MQA and MLA]] for the MQA/GQA spectrum.

For the feed-forward network, Gemma 1 uses GeGLU (a GELU-based gated linear unit) instead of SwiGLU. The difference is the activation function inside the gating: GeGLU uses GELU, SwiGLU uses Swish. Both are gated; the choice is largely empirical.

### Training

Gemma 1 was trained on 6T tokens of primarily English web data, code, and mathematical text, on TPUs (Google's hardware). The 2B variant was trained with knowledge distillation from larger Gemini models.

## Gemma 2 (June 2024)

### Architecture

Gemma 2 introduced several innovations beyond Gemma 1:

| Property | Gemma 2 2B | Gemma 2 9B | Gemma 2 27B |
|----------|------------|------------|-------------|
| Parameters | 2.6B | 9B | 27B |
| Layers | 26 | 42 | 46 |
| d_model | 2304 | 3584 | 4608 |
| Heads | 8 | 16 | 32 |
| KV heads | 4 (GQA) | 8 (GQA) | 16 (GQA) |
| Context | 8K | 8K | 8K |
| Vocab | 256K | 256K | 256K |

### Local and global attention pattern

Gemma 2 alternates between local attention (sliding window, 1024 tokens), where each token attends to a local window — cheap, and captures local patterns — and global attention, where every 6th layer uses full attention to capture long-range dependencies. This pattern gives most of the efficiency of sliding window attention while preserving some global context. It is a hybrid approach, similar in spirit to [[Longformer]] but with a different pattern. See [[Sliding Window Attention]] for the underlying mechanism.

### Logit soft-capping

Gemma 2 caps attention logits and final logits to a maximum value:

```text
logits = tanh(logits / cap) * cap
```

This prevents logits from growing unboundedly during training, which can cause instability. Soft-capping is a simple, effective stabilizer that became more common in 2024+ models.

### Knowledge distillation

Gemma 2 9B and 27B were trained with knowledge distillation from a larger (undisclosed) teacher model. The teacher's logits were used as a soft target, in addition to the standard next-token prediction loss. This improved quality significantly — Gemma 2 9B outperforms Gemma 1 7B despite being similar size.

### Larger sliding window

For the local attention layers, Gemma 2 uses a sliding window of 4096 (vs Longformer's 512). The larger window captures more local context per layer.

### Key results

Gemma 2 achieved strong quality. Gemma 2 9B is competitive with Llama 3 8B and Mistral 7B, and Gemma 2 27B is competitive with Llama 3 70B on some benchmarks despite being 2.5× smaller. The quality-per-parameter efficiency was notable — Gemma 2 models punch above their weight class, partly due to knowledge distillation.

## CodeGemma (April 2024)

CodeGemma is Gemma fine-tuned for code, in 2B and 7B variants. It was trained on a code-heavy corpus (500B+ tokens of code), supports code completion, generation, and understanding, and is strong on HumanEval, MBPP, and other code benchmarks. CodeGemma competes with CodeLlama, DeepSeek-Coder, and StarCoder2.

## RecurrentGemma (2024)

### Architecture

RecurrentGemma uses Google's Griffin architecture — a hybrid of RNN and attention. Most layers use recurrent gated attention (an RNN-like mechanism with attention-like expressivity); some layers use standard local attention. The goal is O(1) memory per token (like an RNN) with attention-like quality. RecurrentGemma is Google's answer to [[Mamba]] and the linear-time architecture trend.

### Why RecurrentGemma

RecurrentGemma offers efficient inference (O(1) memory per token, no KV cache growth), long context (it can handle arbitrarily long sequences because memory doesn't grow), and quality competitive with standard Gemma on many tasks. It is less popular than standard Gemma but represents Google's exploration of alternative architectures.

## Gemma 3 (2025)

> [!info] Source status
> Gemma 3 architecture details are **officially confirmed** in Google's announcements, but full technical details may not be completely published. This note reflects publicly available information as of mid-2025.

Key changes from Gemma 2 are native vision-language multimodality, a larger context (up to 128K), improved efficiency from a better attention implementation, and multiple sizes, including larger variants. Gemma 3 aligns with the 2025 trend toward multimodal, long-context open-weights models.

## Why Gemma matters

### Google's open-weights presence

Before Gemma, Google's LLMs (LaMDA, PaLM, Gemini) were closed. Gemma gave Google an open-weights presence, competing with Meta (Llama) and Mistral. This matters for the open-source ecosystem — more competition means better models for everyone.

### Architectural diversity

Gemma's choices (256K vocab, local + global attention, logit soft-capping, knowledge distillation) add diversity to the open-weights landscape. Not every model needs to follow the Llama template exactly; Gemma shows that variations can work.

### Knowledge distillation as a technique

Gemma 2's use of knowledge distillation (from a larger teacher) demonstrated that distillation can significantly improve small models. This technique is now widely used — distill a large model's knowledge into a smaller, deployable model.

### TPU ecosystem

Gemma is trained on TPUs, not just GPUs. This provides an alternative to the NVIDIA-dominated GPU ecosystem and gives Google independence from GPU supply constraints.

## Comparison to other families

| Family   | Vocab   | Distillation? | Attention pattern           |
|----------|---------|---------------|-----------------------------|
| Llama    | 32-128K | No            | Full (GQA)                  |
| Mistral  | 32K     | No            | Sliding window + GQA        |
| Qwen     | 151K    | No            | Full (GQA)                  |
| DeepSeek | 100K    | No            | Full (MLA)                  |
| Gemma 2  | 256K    | Yes           | Local + global alternating  |

Gemma's distinctive features are the largest vocab, knowledge distillation, and alternating local/global attention. See [[Llama Family Architecture]], [[Mistral and Mixtral Architecture]], and [[Qwen Family Architecture]] for the other families, and [[Llama Mistral Qwen Comparison]] for the cross-family view.

## Impact and legacy

Gemma's architectural influence shows in four ways. It validated knowledge distillation for open weights: Gemma 2's quality (punching above its weight) showed that distillation is practical for open-weights, not just closed models. It popularized logit soft-capping: the technique became more common after Gemma 2's success. It added architectural diversity: the local + global attention pattern and large vocabulary provided alternatives to the Llama template. And it signaled Google's open-weights commitment: Gemma showed that Google would participate in open-weights, not just closed APIs, which benefits the entire ecosystem.

For AI engineers, Gemma is a strong alternative to Llama/Mistral, especially for multilingual applications (large vocab) and cost-sensitive deployments (Gemma 2's efficiency). Understanding Gemma's architecture clarifies the design space beyond the Llama template.

## Further reading

Primary sources for the claims in this note:

- Gemma 1 technical report: arXiv:2403.08295
- Gemma 2 technical report: arXiv:2408.00118
- RecurrentGemma: arXiv:2404.18402
- Google DeepMind blog: deepmind.google/technologies/gemma/

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[Llama Family Architecture]] — the template Gemma varies.
- [[Mistral and Mixtral Architecture]] — the sliding window + MoE family.
- [[Qwen Family Architecture]] — the other large-vocabulary family.
- [[Llama Mistral Qwen Comparison]] — cross-family comparison.
- [[GQA MQA and MLA]] — the KV-head spectrum, whose both ends Gemma uses.
- [[Sliding Window Attention]] — the local half of Gemma 2's pattern.
- [[Longformer]] — the earlier local + global attention precedent.
- [[Mamba]] — the linear-time trend RecurrentGemma answers.
