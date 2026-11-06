---
title: YaRN and NTK-Aware Scaling
type: concept
aliases:
  - YaRN
  - NTK-aware Scaling
  - Yet another RoPE extensioN
  - NTK-aware scaled RoPE
tags:
  - attention
  - positional-encoding
  - rope
  - yarn
  - ntk-aware-scaling
  - long-context
  - context-extension
sources:
  - "10 - YaRN and NTK-aware Scaling"
created_index: 12
---

RoPE-trained models cannot naturally attend beyond their training context length, because past it the positional rotations wrap around and distinct positions become indistinguishable. NTK-aware scaling and YaRN repair this by rescaling RoPE's frequencies rather than uniformly compressing its positions, enabling 4–32× context extension without retraining — Llama 3's 128k context comes from YaRN-style scaling. The two methods differ in how they treat the frequency spectrum: NTK-aware scaling applies one compromise factor to all bands, while YaRN segments the spectrum and treats each band differently. This note develops why extrapolation fails, why naive interpolation also fails, how each method works, and what the practical extension limits are.

> [!info] TL;DR
> RoPE models can't naturally attend beyond their training context length — the rotations "wrap around." **NTK-aware scaling** and **YaRN** fix this by rescaling RoPE's frequencies, enabling 4–32x context extension without retraining. Llama 3's 128k context comes from YaRN-style scaling.

## The problem: RoPE length extrapolation

RoPE rotates Q and K by an angle proportional to position. For position $m$ and frequency $\theta_k$:

$$
\text{angle} = m \cdot \theta_k
$$

For high-frequency dimensions (large $\theta_k$), the angle wraps around past $2\pi$. After enough positions, two distinct positions look identical to that frequency — aliasing. For a model trained at length 4096, positions 5000+ produce aliased rotations, and attention quality collapses. The model literally cannot distinguish positions past its training length.

## The naive fix: interpolation

Compress positions to fit the training range:

$$
m \to m \cdot \frac{L_{\text{train}}}{L_{\text{target}}}
$$

For 8192 → 4096: divide all positions by 2. Position 8000 becomes position 4000 (in the trained range). The **problem**: this also compresses the high-frequency rotations. The model loses fine-grained local position information — nearby tokens become indistinguishable. Quality degrades, especially on tasks needing local precision.

## NTK-aware scaling

**NTK (Neural Tangent Kernel)-aware scaling**: instead of uniformly compressing all positions, scale the **frequencies** $\theta_k$ so that:

- High-frequency dimensions (local position) stay roughly the same.
- Low-frequency dimensions (long-range position) are stretched.

$$
\theta_k' = \theta_k \cdot s^{-2k/d}
$$

where $s = L_{\text{target}} / L_{\text{train}}$ is the scaling factor. This preserves local resolution (high freqs) while extending the long-range reach (low freqs). The "NTK" name comes from the theory of how neural networks respond to input scaling at initialization.

The appeal is practical. It is better than naive interpolation because it preserves local precision; it needs no retraining (just change the RoPE frequency calculation); and it is easy to implement (a one-line change in most RoPE code). The costs: quality still degrades somewhat at extreme extensions (16x+), and it is not optimal for any single frequency band — a uniform-ish compromise.

## YaRN (Yet another RoPE extensioN)

Peng et al. (2023) observed that different frequency bands behave differently and need different treatment:

- **High frequencies** (small wavelengths, local position): the model uses these for **local distance**. Interpolation hurts here; keep them as-is.
- **Low frequencies** (large wavelengths, long-range position): the model uses these for **absolute position**. Interpolation is fine here; stretch them.
- **Middle frequencies**: a transition regime.

YaRN segments the frequency range into these three bands and applies different scaling to each:

1. **High band**: no scaling (preserve local).
2. **Middle band**: smooth interpolation between no-scaling and full-scaling.
3. **Low band**: full interpolation (stretch).

Plus a temperature correction factor (because the rescaled rotations change the effective attention temperature).

### The three frequency bands

YaRN's key insight: different frequency bands serve different purposes and need different treatment.

| Band | Frequency range | Wavelength | What it captures | YaRN treatment |
|------|-----------------|------------|------------------|----------------|
| High | $\theta \approx 1$ | ~1-10 tokens | Fine local position (token-level distinctions) | **No scaling** — preserve local precision |
| Middle | $\theta \approx 0.01$ | ~100-1000 tokens | Medium-range structure | **Smooth interpolation** between no-scaling and full-scaling |
| Low | $\theta \approx 0.0001$ | ~10000+ tokens | Coarse long-range position (absolute position) | **Full interpolation** — stretch to extend reach |

Uniform NTK-aware scaling applies the same factor to all bands, which over-stretches high frequencies (losing local precision) and under-stretches low frequencies (not extending enough). YaRN's band-specific treatment gives the best of both: local precision preserved, long-range extended.

### The temperature correction

Rescaling rotations changes the effective softmax temperature. YaRN adds a temperature correction factor $t$ to compensate: multiply attention scores by $1/t$ before softmax. Without this, the rescaled rotations produce a slightly different attention distribution, causing quality degradation. The temperature is computed from the scaling factor and is typically close to 1 for small extensions (4×) and grows for larger extensions (16×+).

### YaRN in practice

4x extension: usually works zero-shot with minimal quality loss. 8x extension: works well with a small amount of fine-tuning. 16x+ extension: requires fine-tuning but is achievable. Llama 3 uses RoPE base 500000 (effectively a form of NTK-like scaling) to support 8k → 128k context.

## Practical extension limits

| Extension factor | Method | Quality (zero-shot) | Quality (with fine-tuning) | Use case |
|------------------|--------|---------------------|---------------------------|----------|
| 2×               | YaRN   | ~100% of original   | ~100%                     | Safe default |
| 4×               | YaRN   | ~95-98%             | ~100%                     | Common (32K → 128K) |
| 8×               | YaRN   | ~85-90%             | ~95-98%                   | Needs short fine-tune |
| 16×              | YaRN   | ~70-80%             | ~90-95%                   | Needs longer fine-tune |
| 32×+             | LongRoPE | ~50-70%           | ~85-90%                   | Search-based; significant fine-tune |
| 128×+            | LongRoPE + progressive | ~30-50% | ~80%+                | Extreme extension (2M tokens) |

**Zero-shot** means apply the scaling and test immediately. **Fine-tuned** means apply the scaling and fine-tune on long-context data for ~1B tokens.

## LongRoPE

For extreme extension (1M+ tokens), even YaRN has limits. LongRoPE (Microsoft, 2024) **searches** for non-uniform per-frequency scaling factors via evolutionary search, using a two-stage approach: extend to 256k via search, then to 2M via progressive extension. It achieves 2M-token context on Llama models. Production maturity is still developing, but it's the state of the art for extreme long context. For most use cases (128K or less), YaRN is sufficient and much simpler; at the frontier, models such as MiniMax-01 reach 1M context via different approaches.

## Worked example: NTK-aware scaling

```python
def ntk_aware_rope(dim, max_seq_len, base=10000.0, scaling_factor=4.0):
    """RoPE frequencies with NTK-aware scaling."""
    # Instead of base, use an effective base that scales frequencies
    effective_base = base * (scaling_factor ** (dim / (dim - 2)))
    inv_freq = 1.0 / (effective_base ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(max_seq_len).float()
    freqs = torch.outer(t, inv_freq)
    return freqs.cos(), freqs.sin()
```

Most modern serving frameworks (vLLM, TGI, HuggingFace) accept a `rope_scaling` config that handles this automatically:

```python
config = AutoConfig.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
config.rope_scaling = {"type": "yarn", "factor": 4.0}  # 32k → 128k
model = AutoModelForCausalLM.from_pretrained(..., config=config)
```

## Worked example: YaRN in HuggingFace

```python
from transformers import AutoModelForCausalLM, AutoConfig
import torch

# Load Llama 3 8B (trained at 8K context)
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
config = AutoConfig.from_pretrained(model_id)

# Extend to 128K context (16× extension)
config.rope_scaling = {
    "type": "yarn",
    "factor": 16.0,  # 8K → 128K
    "original_max_position_embeddings": 8192,
}
config.max_position_embeddings = 131072  # 128K

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    config=config,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # Required for long context
    device_map="auto",
)

# Test on long context
long_text = "Hello " * 100000  # ~100K tokens
inputs = model.tokenizer(long_text, return_tensors="pt")
print(f"Input length: {inputs['input_ids'].shape[1]} tokens")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=100)
print(model.tokenizer.decode(outputs[0]))
```

## Why this matters

Long context is one of the most important capabilities of modern LLMs, and RAG vs. long-context is a key architectural decision. YaRN/NTK enables "free" context extension — no retraining, just config changes — which is what makes 128k-context Llama 3 feasible. Understanding these methods lets you read modern model cards (which specify `rope_scaling`) and configure serving engines correctly. For multimodal models, the same techniques apply (vision tokens + text tokens in one long sequence).

## Production implications

Use the model's specified RoPE config — don't override it; wrong `rope_theta` or scaling means silent quality loss at long contexts. For context extension beyond training length, use YaRN (`rope_scaling={"type":"yarn","factor":N}`) and test on near-max-length sequences. Fine-tune for extreme extension — zero-shot YaRN past 8x usually degrades, and a short fine-tune on long-context data restores quality. Monitor long-context quality: perplexity should decrease (or stay flat) as context grows; if it increases, your RoPE config is wrong.

## Common pitfalls and failure modes

Four pitfalls cover most failures. A wrong scaling factor — too aggressive means quality collapse; too conservative means no extension. Mixing scaling methods — pick one (YaRN or NTK or LongRoPE) and be consistent. Forgetting to update attention's effective length — beyond RoPE, the KV cache must also extend. And assuming zero-shot works at extreme extensions — always validate.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Quality collapse at extended context | Scaling factor too aggressive | Reduce factor; or fine-tune on long-context data |
| NaN in attention at long context | Temperature correction missing | Ensure YaRN implementation includes temperature correction |
| Memory OOM at long context | KV cache too large | Use GQA model (smaller KV cache); quantize KV cache to INT8; use PagedAttention |
| Inconsistent results across batch | Position IDs not handled correctly | Pass explicit `position_ids`; ensure they match the extended range |

## Interview questions

1. **Q: What are YaRN's three frequency bands and why do they need different treatment?**
   A: **High** (wavelength ~1-10 tokens): captures fine local position. Interpolation hurts here; keep as-is. **Low** (wavelength ~10000+ tokens): captures coarse long-range position. Interpolation is fine; stretch them. **Middle**: transition regime with smooth interpolation. Uniform NTK-aware scaling over-stretches high frequencies (losing local precision) and under-stretches low frequencies. YaRN's band-specific treatment preserves local precision while extending long-range reach.

2. **Q: What is the temperature correction in YaRN and why is it needed?**
   A: Rescaling rotations changes the effective softmax temperature. The rescaled rotations produce a slightly different attention distribution, causing quality degradation. YaRN adds a temperature correction factor $t$ to compensate: multiply attention scores by $1/t$ before softmax. Without this, the model's attention would be too sharp or too flat at extended contexts. The temperature is computed from the scaling factor and is typically close to 1 for small extensions (4×) and grows for larger extensions (16×+).

3. **Q: When does YaRN work zero-shot vs. requiring fine-tuning?**
   A: Zero-shot (no fine-tuning needed): 2× extension (~100% quality), 4× extension (~95-98% quality). Short fine-tune (~1B tokens): 8× extension (~95-98% quality). Longer fine-tune: 16× extension (~90-95% quality). For 32×+, use LongRoPE (search-based) with significant fine-tuning. The rule of thumb: 4× is safe zero-shot; 8-16× needs fine-tuning; 32×+ needs search + fine-tuning.

4. **Q: How does YaRN compare to ALiBi for context extension?**
   A: YaRN extends RoPE-trained models; ALiBi is a different positional encoding that natively extrapolates. YaRN: works with existing RoPE models (Llama, Mistral, Qwen), 4× zero-shot, 8-16× with fine-tuning. ALiBi: native extrapolation (train on 1024, test on 2048+), but penalizes long-range attention (linear bias). In practice, YaRN won because (1) most models already use RoPE; (2) YaRN's extension is sufficient for most use cases (128K); (3) ALiBi's locality penalty hurts long-range reasoning.

5. **Q: What is LongRoPE and when would you use it?**
   A: LongRoPE (Microsoft, 2024) searches for non-uniform per-frequency scaling factors via evolutionary search. It achieves 2M-token context on Llama models. Use it when you need extreme extension (1M+ tokens) and can afford significant fine-tuning. LongRoPE uses a two-stage approach: extend to 256K via search, then to 2M via progressive extension. For most use cases (128K or less), YaRN is sufficient and much simpler.

6. **Q: How would you extend a Llama 3 8B model from 8K to 128K context?**
   A: Llama 3 8B is already trained with `rope_theta=500000` and supports 8K natively. To extend to 128K: (1) Set `config.rope_scaling = {"type": "yarn", "factor": 16.0, "original_max_position_embeddings": 8192}`. (2) Set `config.max_position_embeddings = 131072`. (3) Use FlashAttention (required for long context memory). (4) Use GQA (Llama 3 already does) to keep KV cache manageable. (5) Fine-tune on long-context data (~1B tokens at 128K) for best quality. (6) Test on needle-in-haystack at 128K to verify quality. Without fine-tuning, expect ~85-90% of original quality at 128K.

## Further reading

- Peng et al. (2023), *YaRN: Efficient Context Window Extension of Large Language Models*.
- Bloc97 (2023), *NTK-Aware Scaled RoPE* (blog post that introduced the technique).
- Chen et al. (2024), *LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens*.

## See also

- [[Attention and Transformers MOC]]
- [[RoPE]] — the foundation being extended
- [[ALiBi]] — the alternative with native extrapolation
- [[Positional Encoding]] — the broader family
- [[Sinusoidal and Learned Positional Encodings]] — why absolute encodings can't do this
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — required for long-context memory
- [[GQA MQA and MLA]] — keeping the KV cache manageable at length
- [[KV Cache Mechanics]]
