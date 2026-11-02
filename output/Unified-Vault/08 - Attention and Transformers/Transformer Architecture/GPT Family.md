---
title: GPT Family
type: concept
aliases:
  - GPT
  - GPT Family Evolution
  - GPT lineage
  - decoder-only LLM
  - Llama
  - Mistral
tags:
  - transformer
  - decoder-only
  - gpt
  - llama
  - mistral
  - large-language-models
sources:
  - "09 - GPT Family Evolution"
created_index: 26
---

GPT (Generative Pre-trained Transformer) is the decoder-only architecture that powers modern LLMs. The lineage runs from GPT-1 (2018, 117M params) through GPT-4 (2023, ~1T params estimated) to the modern open models (Llama 3, Mistral, DeepSeek, Qwen), and along the way it converged on a standard recipe: RMSNorm + SwiGLU + RoPE + GQA + pre-norm. This note traces that evolution generation by generation and records the converged recipe that now spans every major model family.

> [!info] TL;DR
> GPT (Generative Pre-trained Transformer) is the decoder-only architecture that powers modern LLMs. From GPT-1 (2018, 117M params) to GPT-4 (2023, ~1T params estimated) to modern open models (Llama 3, Mistral, DeepSeek, Qwen), the architecture has converged on a standard recipe: RMSNorm + SwiGLU + RoPE + GQA + pre-norm.

## The GPT recipe

A modern decoder-only LLM has:

- **Token embeddings** (often untied from the output).
- **N Transformer blocks**, each with:
  - Pre-norm (RMSNorm in modern models).
  - Causal multi-head self-attention (GQA in modern models).
  - Residual.
  - Pre-norm.
  - SwiGLU FFN.
  - Residual.
- **Final norm**.
- **Output projection** (linear to vocab).

On top of this skeleton sit three architectural choices that define the modern recipe: **RoPE** positional encoding (not learned absolute), **no bias terms** in the linear layers (Llama, Mistral), and **GQA** for inference efficiency. Each block is detailed in [[Transformer Block]]; the components live in [[Feed-Forward Network]], [[Normalization Layers]], [[RoPE]], and [[GQA MQA and MLA]]. This recipe was popularized by Llama (2023) and is now the default.

## The GPT lineage

### GPT-1 (2018, 117M params)

12 layers, 768 dim, 12 heads, learned positional embeddings, pre-norm, and GELU activation. GPT-1 demonstrated that pretraining + fine-tuning works for many tasks.

### GPT-2 (2019, 1.5B params)

48 layers, 1600 dim, 25 heads, and pre-norm (vs the original Transformer's post-norm). GPT-2 demonstrated zero-shot task transfer — no fine-tuning needed for some tasks — and was initially deemed "too dangerous to release" by OpenAI.

### GPT-3 (2020, 175B params)

Same architecture as GPT-2, just bigger. GPT-3 demonstrated **few-shot in-context learning** — the model learns new tasks from a few examples in the prompt, without weight updates — and defined the "scale is all you need" era.

### GPT-3.5 / InstructGPT (2022)

Same base architecture, but aligned with **RLHF** (PPO). This is the model behind ChatGPT (launched Nov 2022), and it demonstrated that alignment transforms a base LM into a useful chatbot.

### GPT-4 (2023, architecture not officially disclosed)

Strong evidence of **MoE** (not officially confirmed), **multimodal** (vision input), tool use, function calling, structured outputs, and significantly stronger reasoning than GPT-3.5.

### GPT-4o / o1 / o3 (2024–2025)

GPT-4o is native multimodal (audio + vision + text in one model). o1 is a **reasoning model** — extended internal CoT via test-time compute. o3 brings further reasoning improvements.

## Open-source LLMs

### Llama family (Meta)

**Llama 1** (Feb 2023): 7B/13B/33B/65B, with RoPE, RMSNorm, and SwiGLU — the kick-off of the open LLM era. **Llama 2** (Jul 2023): same architecture, more data, commercial license; the 70B model uses GQA. **Llama 3** (Apr 2024): 8B/70B/405B, with GQA across all sizes and RoPE base 500000 for the 8k→128k context extension. **Llama 3.1/3.2/3.3** (2024): multilingual, multimodal, longer context.

### Mistral

**Mistral 7B** (Sep 2023) introduced SWA (sliding window attention) and GQA. **Mixtral 8x7B** (Dec 2023) is MoE, with 8 experts and top-2 routing. **Mixtral 8x22B** (Apr 2024) is a bigger MoE. **Mistral Large / Nemo** are commercial models.

### DeepSeek

**DeepSeek-V2** (2024) introduced MLA (Multi-head Latent Attention) and MoE. **DeepSeek-V3** (2024) has 671B params (37B active) with auxiliary-loss-free MoE load balancing. **DeepSeek-R1** (Jan 2025) is an open-source reasoning model trained with RL on verifiable rewards.

### Qwen (Alibaba)

**Qwen 2 / 2.5** (2024) are strong multilingual, code, and math models. **Qwen 3** (2025, planned) is rumored to add linear attention hybrids.

### Gemma (Google)

**Gemma 1 / 2 / 3** (2024–2025) are Google's open weights, derived from Gemini research. Gemma 2 uses alternating SWA + full attention.

## Architectural evolution

| Feature                | GPT-2 (2019) | GPT-3 (2020) | Llama 2 (2023) | Llama 3 (2024) | DeepSeek-V3 (2024) |
|------------------------|--------------|--------------|----------------|----------------|---------------------|
| Norm                   | LayerNorm    | LayerNorm    | RMSNorm        | RMSNorm        | RMSNorm             |
| Norm placement         | Pre-norm     | Pre-norm     | Pre-norm       | Pre-norm       | Pre-norm            |
| Activation             | GELU         | GELU         | SwiGLU         | SwiGLU         | SwiGLU              |
| Positional             | Learned abs  | Learned abs  | RoPE           | RoPE           | RoPE                |
| Attention              | MHA          | MHA          | GQA (70B)      | GQA            | MLA                 |
| Bias in linear layers  | Yes          | Yes          | No             | No             | No                  |
| Architecture type      | Dense        | Dense        | Dense          | Dense          | MoE                 |

The trend: simpler (no bias), more efficient (GQA, MLA), better positional encoding (RoPE with longer context), more parameters via MoE.

## Worked example (loading a modern LLM)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

inputs = tokenizer("Hello!", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

A few lines load a Llama 3 instruct model in bfloat16 with FlashAttention-2, generate 50 tokens, and decode them — the whole modern stack (RoPE, GQA, RMSNorm, SwiGLU) is hidden behind a single `from_pretrained` call.

## Why this matters

The GPT family is **the** lineage of modern LLMs — every chat model you use is descended from this lineage. The architectural convergence (RMSNorm + SwiGLU + RoPE + GQA) means a single recipe works across many model families: you can switch between Llama, Mistral, Qwen, and Gemma with minimal code changes. Understanding the evolution helps you read model cards and configs — `rope_theta`, `num_key_value_heads`, and `hidden_act` all make sense once you know the architecture. And for inference, the modern recipe (GQA especially) is what makes consumer-GPU inference feasible.

## Production implications

Default to a modern Llama-family model (Llama 3.1, Mistral, Qwen 2.5) for most applications — they're well-supported, efficient, and competitive. Use **DeepSeek-V3** for cost-sensitive MoE workloads — it is extremely cheap per token. Use **GPT-4 / Claude / Gemini** for the closed-source quality peaks. For new model training, **follow the Llama recipe** unless you have a specific reason to deviate.

## Common pitfalls

Four mistakes recur. Mixing up base vs instruct models — base models don't follow instructions, so use the `-Instruct` variants for chat. Forgetting the chat template — each model has its own, and the tokenizer's `apply_chat_template` applies it correctly. Setting the wrong `rope_theta` when extending context — use the model's specified value. And assuming GPT-4 is open — it's not; the open-source alternatives are Llama, Mistral, DeepSeek, and Qwen.

## Further reading

- Radford et al. (2018), *Improving Language Understanding by Generative Pre-Training* (GPT-1).
- Radford et al. (2019), *Language Models are Unsupervised Multitask Learners* (GPT-2).
- Brown et al. (2020), *Language Models are Few-Shot Learners* (GPT-3).
- Touvron et al. (2023), *LLaMA* and *Llama 2*.
- DeepSeek-AI (2024), *DeepSeek-V3 Technical Report*.

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Decoder Block]], [[Transformer Block]], [[The Transformer]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]], [[T5 and BART]], [[BERT vs GPT vs T5]]
- [[Feed-Forward Network]], [[Normalization Layers]], [[Mixture of Experts]]
- [[GQA MQA and MLA]], [[RoPE]], [[Sliding Window Attention]], [[YaRN and NTK-Aware Scaling]]
- [[Embedding Layer]]
