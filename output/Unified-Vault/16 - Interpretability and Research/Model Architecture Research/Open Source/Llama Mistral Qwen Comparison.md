---
title: Llama Mistral Qwen Comparison
type: concept
aliases: ["Llama Mistral Qwen Architecture Comparison", "Llama, Mistral, Qwen Architecture Comparison", "Llama vs Mistral vs Qwen"]
tags: [model-architecture, open-source, llama, mistral, qwen, comparison]
sources: ["02 - Llama Mistral Qwen Comparison"]
created_index: 19
---

Llama (Meta), Mistral, and Qwen (Alibaba) are the three dominant open-weight LLM families, and they have converged on the same core recipe: RMSNorm, SwiGLU, RoPE, and grouped-query attention. The differences are in the details — Mistral adds sliding window attention, Qwen emphasizes multilingual training, and Llama is the lineage that popularized the recipe in the first place. Every architectural fact compared here is officially confirmed via technical reports, which makes these three families the best-documented corner of the open-weights landscape. The surrounding research area is indexed in [[Interpretability and Research MOC]].

> [!info] TL;DR
> The three dominant open-source LLM families (Llama, Mistral, Qwen) share the same core recipe (RMSNorm + SwiGLU + RoPE + GQA) but differ in details: Mistral adds sliding window attention; Qwen emphasizes multilingual; Llama popularized the recipe. All **officially confirmed** via technical reports.

## The common recipe

From 2024 onward, all three families have converged on the same component set:

- **Pre-norm** with **RMSNorm** (see [[Normalization Layers]]).
- **SwiGLU** FFN (with $d_{ff} \approx \frac{8}{3} d_{model}$).
- **RoPE** positional encoding (see [[RoPE]]).
- **GQA** attention (grouped-query) (see [[GQA MQA and MLA]]).
- **No bias** in linear layers.
- **Final norm** after the last block.

This is the **Llama recipe**, adopted by Mistral, Qwen, [[Gemma Architecture|Gemma]], and most modern open LLMs.

## Llama lineage (Meta)

### Llama 1 (February 2023)

Llama 1 shipped in four sizes — 7B / 13B / 33B / 65B — and introduced the modern recipe (RoPE, RMSNorm, SwiGLU) that the open-weights ecosystem then adopted. It used plain multi-head attention (MHA), with no GQA.

### Llama 2 (July 2023)

Llama 2 came at 7B / 13B / 70B, with the 70B model adopting GQA. It moved to a commercial license, and Llama 2 Chat was RLHF-aligned (see [[RLHF with PPO]] for the alignment recipe).

### Llama 3 (April 2024)

Llama 3 arrived at 8B / 70B / 405B, with all sizes using GQA. The RoPE base is 500000 (chosen for the 8k→128k extension), and the vocabulary is 128k (larger than Llama 2's 32k). The point releases each added one thing: Llama 3.1 brought 128k context, Llama 3.2 brought multimodality, and Llama 3.3 brought an improved 70B.

### Llama 4 (2025–2026, if released)

Llama 4, if released in the 2025–2026 window, is likely MoE (based on Meta research papers) and native multimodal. Both points are forward-looking expectations rather than announced specs.

## Mistral lineage

### Mistral 7B (September 2023)

Mistral 7B is a 7B-parameter model that runs **Sliding Window Attention** (window=4096) in all layers, alongside GQA and RoPE — see [[Sliding Window Attention]] for the mechanism. It is known for strong performance per parameter.

### Mixtral 8x7B (December 2023)

Mixtral 8x7B is a MoE model: 8 experts, top-2 routing, 47B total params, 13B active (see [[Mixture of Experts]]). It keeps SWA + GQA and ships under an Apache 2.0 license.

### Mixtral 8x22B (April 2024)

Mixtral 8x22B is the bigger MoE: 141B total, 39B active.

### Mistral Large, Nemo, and Small 3

Mistral Large / Nemo / Small 3 are commercial, dense models. Mistral Small 3 (2025) is competitive with Llama 3.3 70B at 24B params.

## Qwen lineage (Alibaba)

### Qwen 2 and 2.5 (2024)

Qwen 2 / 2.5 spans 0.5B / 1.5B / 7B / 14B / 32B / 72B, with strong multilingual coverage (Chinese, English, code, math). The architecture is the familiar GQA, RoPE, SwiGLU stack. The family also ships specialized variants: Qwen-Math, Qwen-Coder, and Qwen-VL.

### Qwen 2.5 Max and Qwen 3 (2025)

Qwen 2.5 Max brought MoE variants, while Qwen 3 (2025) pushes longer context (1M tokens in some variants) and reasoning models (QwQ).

## Comparison table

The table lines up the ~7–8B tier of each family:

| Feature              | Llama 3 8B  | Mistral 7B  | Qwen 2.5 7B |
|----------------------|-------------|-------------|-------------|
| Parameters           | 8B          | 7B          | 7B          |
| Layers               | 32          | 32          | 28          |
| Hidden dim           | 4096        | 4096        | 3584        |
| Attention            | GQA         | GQA + SWA   | GQA         |
| Q heads / KV heads   | 32 / 8      | 32 / 8      | 28 / 4      |
| RoPE base            | 500000      | 1000000     | 1000000     |
| Vocab                | 128k        | 32k         | 152k        |
| Context              | 128k (3.1+) | 32k (SWA-based) | 128k+  |
| Norm                 | RMSNorm     | RMSNorm     | RMSNorm     |
| FFN                  | SwiGLU      | SwiGLU      | SwiGLU      |

All three are **architecturally very similar**. Differences are in scale, hyperparameters, training data, and specific features (SWA, vocab size).

## Worked example

The convergence shows up directly in code — all three load the same way:

```python
# All three load the same way
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

for model_id in [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "Qwen/Qwen2.5-7B-Instruct",
]:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, device_map="auto",
        attn_implementation="flash_attention_2",
    )
    # Same API; same usage pattern.
```

Same API, same usage pattern — only the model ID and tokenizer change. The shared `attn_implementation="flash_attention_2"` option works across all three because each family uses a standard attention layout that [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] kernels can accelerate.

## Practical implications

### Choosing a family

The architectural convergence means you can swap between Llama / Mistral / Qwen with minimal code changes, so the choice comes down to quality, cost, license, and ecosystem. For **multilingual** work (especially Chinese), Qwen typically wins. For **maximum efficiency at small scale**, choose Mistral (SWA helps). For **broad ecosystem and tooling**, choose Llama (largest community). For **commercial use without restrictions**, Llama 3 has a permissive license (with caveats for >700M MAU).

### Production defaults and serving

A solid all-around default ladder is **Llama 3.1 8B** for small, **Llama 3.1 70B** for medium, and **Llama 3.1 405B** for large. For Chinese / Asian markets, use Qwen. For very long context with memory constraints, use Mistral (SWA) or Llama 3.1 (with [[YaRN and NTK-Aware Scaling|YaRN]]). For multi-tenant serving, all three work with [[14 - Inference and Production/Inference/vLLM|vLLM]], [[TGI]], and [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]]. Fine-tune compatibility is equally uniform: [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] / [[QLoRA]] / [[DPO]] all work the same across the three families.

## Common pitfalls

In practice, failures come from treating the three families as more interchangeable than they are:

- **Mixing up base and instruct versions** — base models don't follow instructions.
- **Wrong RoPE config** — each model has its own `rope_theta`. Don't mix.
- **Wrong chat template** — each model has its own. Use `tokenizer.apply_chat_template`.
- **Forgetting SWA on Mistral** — some serving frameworks default to full attention; explicitly enable SWA.
- **Vocab size differences** — tokenizers aren't interchangeable.

The RoPE, chat-template, and tokenizer pitfalls are all the same mistake in different guises: assuming one family's configuration transfers unchanged to another.

## Further reading

The primary sources are Touvron et al. (2023), the *Llama 2 paper*; Jiang et al. (2023), *Mistral 7B* (see [[Mistral 7B]]); and Bai et al. (2023), the *Qwen Technical Report*.

## See also

- [[Interpretability and Research MOC]]
- [[Llama Family Architecture]]
- [[Mistral and Mixtral Architecture]]
- [[Qwen Family Architecture]]
- [[Qwen 3.8 Architecture]]
- [[Gemma Architecture]]
- [[DeepSeek Architecture]]
- [[Frontier Model Synthesis 2026]]
- [[GPT Family]]
- [[GQA MQA and MLA]]
