---
title: DeepSeek Architecture
type: concept
aliases: [DeepSeek Architecture, DeepSeek Architecture (V2/V3/R1), DeepSeek-V2, DeepSeek-V3, DeepSeek-R1]
tags: [model-architecture, deepseek, mla, moe, open-source]
sources: ["01 - DeepSeek Architecture"]
created_index: 15
---

DeepSeek's V2/V3/R1 line carries two of the most influential open-weights architecture innovations of the mid-2020s. DeepSeek-V2 introduced MLA (Multi-head Latent Attention), and V3 added auxiliary-loss-free MoE load balancing — together these innovations made DeepSeek-V3 (671B params, 37B active) cheaper to serve than dense 70B models. R1 is V3 with reasoning training. All of it is **Officially Confirmed** in DeepSeek technical reports.

## MLA: multi-head latent attention

Standard attention caches K and V per head, so the KV cache grows linearly with both sequence length and number of heads (see [[KV Cache Mechanics]]). GQA reduces this by sharing K/V across head groups ([[GQA MQA and MLA]]). MLA goes further.

### The compression trick

MLA compresses K and V into a **low-rank latent vector**:

$$
\mathbf{c}_t = \mathbf{W}_{DKV} \mathbf{x}_t \quad \text{(down-project to latent, dim } d_c \ll h \cdot d_k\text{)}
$$

The latent $\mathbf{c}_t$ is what's cached. At attention time, K and V are reconstructed:

$$
\mathbf{K}_t = \mathbf{W}_{UK} \mathbf{c}_t, \quad \mathbf{V}_t = \mathbf{W}_{UV} \mathbf{c}_t
$$

### The absorb trick

Reconstructing K every step is expensive. MLA's key insight: the K projection $\mathbf{W}_{UK}$ can be **absorbed into Q's projection** at the start of attention. The attention computation becomes:

$$
\text{scores} = (\mathbf{Q} \mathbf{W}_{UK}) \mathbf{c}_t^T = \mathbf{Q}' \mathbf{c}_t^T
$$

So you don't need to reconstruct K — just compute $\mathbf{Q}'$ once at the start and use the latent $\mathbf{c}_t$ directly.

### KV cache savings

For DeepSeek-V2: latent dim $d_c = 512$, vs full K/V which would be $128 \cdot 128 = 16k$ — roughly a 32x reduction in KV cache. This is what makes DeepSeek-V3 able to serve long contexts cheaply.

## DeepSeek-V3's MoE: auxiliary-loss-free load balancing

### The problem with standard MoE

Standard MoE uses an auxiliary loss to balance expert utilization ([[Mixture of Experts]]):

$$
L_{\text{aux}} = E \cdot \sum_i f_i \cdot P_i
$$

This competes with the main loss and can hurt quality.

### DeepSeek's solution: bias-adjusted routing

Instead of an auxiliary loss, DeepSeek-V3 adds a per-expert **bias** to the router logits:

$$
\text{router}(\mathbf{x}) = \text{Softmax}(\text{TopK}(\mathbf{W}_g \mathbf{x} + \mathbf{b}))
$$

The bias $\mathbf{b}$ is **dynamically adjusted** based on recent expert load: if expert $i$ is overloaded, $b_i$ decreases (making it less likely to be picked); if expert $i$ is underloaded, $b_i$ increases (making it more likely). This achieves load balancing without any auxiliary loss — and quality improves.

### Other V3 MoE innovations

Three further choices round out the recipe. **Fine-grained experts**: more, smaller experts (256 total) rather than fewer big ones. **Shared experts**: a few experts always active (routing goes to them plus the top-k fine-grained experts), capturing common patterns. **Multi-token prediction (MTP)**: predicting multiple future tokens during training improves data efficiency ([[Multi-Token Prediction]]).

## DeepSeek-R1: reasoning on V3

R1 is V3 with reasoning training, documented in two variants. **R1-Zero**: pure RL on verifiable rewards (math correctness, code tests) — no SFT first; the model spontaneously develops long chain-of-thought. **R1**: SFT on cold-start data, then RL — better readability and safety. R1 matches or beats o1 on most reasoning benchmarks, and the full weights and recipe are open (see [[DeepSeek-R1]], [[Reasoning Models]], and [[Test-Time Compute Scaling]]).

## Architecture summary (DeepSeek-V3)

| Property | Value |
|---|---|
| Total parameters | 671B |
| Active parameters | 37B (per token) |
| Layers | 61 |
| Hidden dim | 7168 |
| Attention | MLA (Multi-head Latent Attention) |
| MoE experts | 256 routed + 1 shared |
| Active experts | 8 routed + 1 shared |
| Positional | RoPE |
| Norm | RMSNorm (pre-norm) |
| Activation | SwiGLU |

## Worked example: loading R1

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "deepseek-ai/DeepSeek-R1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    attn_implementation="flash_attention_2",
)

# R1 produces reasoning_content + content
# Use the chat template
messages = [{"role": "user", "content": "Prove that √2 is irrational."}]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to(model.device)
outputs = model.generate(inputs, max_new_tokens=8000)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

Two practical notes on the snippet: R1 produces `reasoning_content` alongside `content`, so the chat template is applied; and `attn_implementation="flash_attention_2"` selects [[FlashAttention-2 and FlashAttention-3|FlashAttention-2]] kernels. For serving, use vLLM with `--model deepseek-ai/DeepSeek-R1` and MoE + MLA support ([[14 - Inference and Production/Inference/vLLM|vLLM]]).

## Why this matters for AI

DeepSeek-V3/R1 showed that **frontier-quality open models are achievable at low cost** — the V3 training cost was ~$5.6M, versus hundreds of millions for GPT-4 ([[GPT-4 Inferred Architecture]]). MLA is a major architectural innovation: the first serious alternative to GQA for KV cache reduction. Auxiliary-loss-free balancing is a cleaner MoE training recipe that other models are adopting. And R1's open recipe enabled a wave of open-source reasoning model research.

## Production implications

- **DeepSeek-V3 / R1** are extremely cost-effective for their quality; use them when serving cost matters.
- **MoE serving** requires expert parallelism across GPUs; [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[SGLang]] support this.
- **MLA support** requires recent vLLM or SGLang versions — check version compatibility.
- **Memory**: 671B params is too big for a single GPU; multi-GPU (8x H100 or equivalent) is required.

## Common pitfalls

- **Assuming MLA is the same as GQA** — it's fundamentally different (latent compression, not head sharing).
- **Forgetting to apply the absorb trick** — naive MLA is much slower.
- **Mixing up V3 base and R1** — R1 has reasoning training; V3 doesn't.
- **Trying to serve V3 on consumer GPUs** — it won't fit; use the API or a serious cluster.

## Further reading

- DeepSeek-AI (2024), *DeepSeek-V2 Technical Report* (MLA).
- DeepSeek-AI (2024), *DeepSeek-V3 Technical Report* (aux-loss-free MoE).
- DeepSeek-AI (2025), *DeepSeek-R1 Technical Report* (reasoning).

## See also

- [[Interpretability and Research MOC]] — the hub for this area.
- [[GQA MQA and MLA]] — the GQA/MQA/MLA attention family.
- [[Mixture of Experts]] — the MoE Transformer pattern.
- [[KV Cache Mechanics]] — what MLA compresses.
- [[DeepSeek-V2 and V3]] — the V2/V3 technical reports.
- [[DeepSeek-R1]] — the R1 reasoning paper.
- [[Multi-Token Prediction]] — the MTP training objective.
- [[Reasoning Models]] — the reasoning-model category.
- [[Test-Time Compute Scaling]] — the reasoning-training pattern.
- [[GLM 5.2 Architecture]], [[Qwen 3.8 Architecture]], [[MiniMax 3 Architecture]] — comparable open-weights families.
