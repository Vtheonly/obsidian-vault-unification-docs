---
title: Quantization
type: concept
aliases: [Quantization, GPTQ, AWQ, GGUF, INT8, INT4, FP8, SmoothQuant]
tags: [inference, quantization, int8, int4, gptq, awq, gguf, fp8]
sources: ["03 - Quantization (INT8, INT4, GPTQ, AWQ, GGUF, FP8)"]
created_index: 10
---

Quantization reduces model precision — FP16 → INT8 → INT4 — to cut memory and increase inference speed. It is the biggest single inference optimization: a 70B model goes from 140GB to 35GB at INT4, turning multi-GPU serving problems into single-GPU ones. Modern methods (GPTQ, AWQ, GGUF, FP8) preserve quality well at 4-bit, which is why most local LLM use is INT4 and why FP8 has become the standard on Hopper-generation hardware. This note covers why quantization pays, the precision spectrum, the main methods, what to quantize (weights, activations, KV cache, optimizer state), quality impact, worked examples, production patterns, common pitfalls, and a decision framework.

> [!info] TL;DR
> Quantization reduces model precision (FP16 → INT8 → INT4) to cut memory and increase speed. Modern methods (GPTQ, AWQ, GGUF, FP8) preserve quality at 4-bit. **The biggest single inference optimization** — a 70B model goes from 140GB to 35GB at INT4.

## Why quantize

A 70B model in FP16: 140 GB of weights. Doesn't fit on a single 80GB H100.

- INT8: 70 GB. Fits on one H100.
- INT4: 35 GB. Fits on a 48GB GPU with room for KV cache.

Plus: lower memory bandwidth → faster inference. INT4 matmuls are 4× faster than FP16 (on supporting hardware).

The three benefits, in order of how often they drive the decision:

1. **Memory reduction**: lower precision = fewer bytes per parameter. Enables larger models on available GPUs.
2. **Speed improvement**: lower precision = faster matrix multiplications. Tensor Cores on H100 reach ~989 TFLOPs in FP8 vs ~1979 TFLOPs in FP4 (with sparsity).
3. **Energy reduction**: lower precision = less energy per operation. Important for large-scale deployment and edge inference.

### The trade-off

Quantization reduces precision, which can hurt model quality. The art is finding the right balance: too high precision wastes memory and compute, too low precision degrades quality unacceptably, and the sweet spot is 4-8 bits for most use cases. Modern quantization methods (GPTQ, AWQ, FP8) preserve quality well at 4-8 bits, making the trade-off favorable for most production deployments.

## The precision spectrum

| Precision | Bytes/param | 70B model size | 7B model size | Hardware support        |
|-----------|-------------|----------------|---------------|-------------------------|
| FP32      | 4           | 280 GB         | 28 GB         | All                     |
| FP16/BF16 | 2           | 140 GB         | 14 GB         | All GPUs                |
| FP8 (E4M3)| 1           | 70 GB          | 7 GB          | Hopper (H100)+, Ada     |
| INT8      | 1           | 70 GB          | 7 GB          | Most modern GPUs        |
| INT4      | 0.5         | 35 GB          | 3.5 GB        | Hopper, Ada, some older |
| INT3      | 0.375       | 26 GB          | 2.6 GB        | Limited                 |
| INT2      | 0.25        | 18 GB          | 1.8 GB        | Experimental            |

### Floating-point formats

- **FP32**: 1 sign + 8 exponent + 23 mantissa = 32 bits. The training default.
- **FP16**: 1 + 5 + 10 = 16 bits. Range ~6e-5 to ~65504. Requires loss scaling.
- **BF16**: 1 + 8 + 7 = 16 bits. Same range as FP32, lower precision. No loss scaling needed.
- **FP8 E4M3**: 1 + 4 + 3 = 8 bits. More precision, less range. Used for forward pass.
- **FP8 E5M2**: 1 + 5 + 2 = 8 bits. More range, less precision. Used for backward gradients.
- **FP4 E2M1**: 1 + 2 + 1 = 4 bits. Very low precision; experimental on Blackwell.

### Integer formats

- **INT8**: 8-bit signed integer, range -128 to 127. Requires a scale factor to map to FP16 range.
- **INT4**: 4-bit signed integer, range -8 to 7. Even more aggressive scaling required.
- **INT2**: 2-bit, range -2 to 1. Mostly experimental.

Integer quantization requires a **scale factor** per tensor (or per group) that maps the integer range to the floating-point range. The scale is typically computed from the tensor's absmax.

The FP8-versus-INT8 distinction matters in practice: INT8 is a signed integer (-128 to 127) with a scale factor, while FP8 is a floating-point format (E4M3 or E5M2) with exponent and mantissa. FP8 has better dynamic range and precision for the same 8 bits, but requires hardware support (Hopper+).

## Quantization methods

### Naive round-to-nearest (RTN)

Just round FP16 weights to INT8/INT4. Fast, simple, but loses significant quality at INT4.

```python
def quantize_rtn(weights, bits=8):
    """Naive round-to-nearest quantization."""
    if bits == 8:
        scale = weights.abs().max() / 127
        q = (weights / scale).round().clamp(-128, 127).to(torch.int8)
    elif bits == 4:
        scale = weights.abs().max() / 7
        q = (weights / scale).round().clamp(-8, 7).to(torch.int8)
    return q, scale

def dequantize(q, scale):
    return q.float() * scale
```

RTN is the baseline; everything else improves on it. At INT8, RTN is often acceptable. At INT4, RTN loses significant quality — it just rounds, losing information about which weights matter, which is exactly what the calibration-based methods below fix.

### GPTQ (Frantar et al., 2022)

**Post-training quantization** that uses second-order information to compensate for quantization error. Quantizes weights layer-by-layer, using the input activations to determine optimal quantization.

How it works:

1. For each layer, compute the Hessian of the loss with respect to the weights (using a calibration dataset).
2. Quantize weights one column at a time, using the Hessian to predict and compensate for the quantization error.
3. The compensation updates the remaining (not-yet-quantized) weights to offset the error introduced.

Properties: one-shot quantization (no training needed); excellent quality at INT4 — near-FP16 perplexity; supported by AutoGPTQ, vLLM, HuggingFace; slow to apply (~hours for 70B).

Use case: production serving where quality matters and you can afford the upfront quantization time.

### AWQ (Lin et al., 2023)

**Activation-aware Weight Quantization**. Observes that not all weights are equally important — those that produce large activations matter more. AWQ scales these "salient" weights up before quantization (and scales them back at inference).

How it works:

1. Run the model on a calibration dataset and observe activation magnitudes.
2. Identify "salient" weight channels (those that produce large activations).
3. Scale these channels up before quantization (so they're better represented in INT4).
4. At inference, scale activations down to compensate.

Properties: one-shot quantization; better than GPTQ on some benchmarks, comparable on others; faster to apply than GPTQ; supported by vLLM, HuggingFace.

Use case: production serving, especially when GPTQ is too slow to apply.

### GGUF (formerly GGML)

Format for **llama.cpp** — quantization designed for CPU and consumer GPU inference. Multiple precision options (Q4_K_M, Q5_K_M, Q8_0, etc.) with different quality/speed tradeoffs.

Properties: block-wise quantization with per-block scales; multiple variants: Q4_0 (basic 4-bit), Q4_K_M (4-bit with k-quant, mixed precision), Q5_K_M, Q8_0; designed for CPU inference (SIMD-optimized); works on consumer GPUs (CUDA, Metal, ROCm).

Use case: local / consumer-GPU inference. Ollama, LM Studio, and most local LLM tools use GGUF.

### FP8 (Hopper, Blackwell)

Native hardware support on H100 and B200. Two formats: E4M3 (more precision) and E5M2 (more range). Almost FP16 quality at half the memory.

Properties: native hardware support (no software emulation); used in training (FP8 training) and inference; requires Hopper+ hardware; supported by vLLM, TensorRT-LLM, TransformerEngine; per-tensor or per-channel scaling for stability.

Use case: H100+ deployments where quality is critical. The new standard for Hopper-based production.

### SmoothQuant (Xiao et al., 2022)

For INT8 quantization of activations + weights. Smooths activation outliers (which cause quantization issues) by migrating difficulty from activations to weights.

How it works: activations have outliers (a few very large values) that make INT8 quantization hard. SmoothQuant scales down the outlier channels in activations and scales up the corresponding weights. Result: both activations and weights are "smoother" and quantize better.

Use case: when you need to quantize activations (not just weights). Common for INT8 weight+activation quantization.

### QLoRA's NF4

4-bit NormalFloat — a quantization designed for normally-distributed weights. Used in [[QLoRA]] fine-tuning. Not typically used for inference (GPTQ/AWQ are better for serving).

Properties: 16 quantization levels optimized for the normal distribution of weights; better than uniform INT4 for weight-only quantization; used in QLoRA to enable fine-tuning of 70B models on a single 48GB GPU.

## What to quantize

### Weights (standard)

Most methods focus on weights. Weight quantization is straightforward because weights are static (known at quantization time). The granularity choice trades quality against metadata:

- **Per-tensor**: one scale for the whole tensor. Simplest, lowest metadata overhead.
- **Per-channel**: one scale per output channel. Better quality, more metadata.
- **Per-group**: one scale per group of N elements. Balance between quality and metadata. GPTQ/AWQ typically use group size 128.

### Activations (harder)

Activations depend on input, so they can't be pre-quantized. They must be quantized on-the-fly during inference. This is harder because activation distributions vary with input, and outliers in activations cause quantization issues (SmoothQuant addresses this). Activation quantization is less common than weight quantization; usually only for INT8.

### KV cache

INT8 or FP8 KV cache halves memory. Critical for long-context inference where the KV cache dominates memory. The KV cache stores keys and values for all previous tokens during autoregressive generation; for long contexts (128K+) it can be larger than the model weights. Quantizing it to FP8/INT8 halves its memory, enabling longer contexts on the same GPU.

- vLLM: `--kv-cache-dtype fp8`.
- TensorRT-LLM: native support.
- Quality impact: minimal (KV cache values are well-behaved).

For 128K context on Llama 3 8B: FP16 KV cache = 16 GB; FP8 KV cache = 8 GB. The difference determines whether you fit on one GPU.

### Optimizer state (training)

FP8 optimizer state is a research area. Adam's m and v are 2× parameter count; quantizing them to FP8 halves their memory. Useful for training very large models. Less mature than inference quantization; supported by some training frameworks (TransformerEngine).

## Worked examples

### Serving an AWQ model with vLLM

```bash
# Serve an AWQ-quantized model with vLLM
vllm serve TheBloke/Llama-2-70B-Chat-AWQ \
    --quantization awq \
    --dtype half
```

Or in Python:

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="TheBloke/Llama-2-70B-Chat-AWQ",
    quantization="awq",
    dtype="float16",
    gpu_memory_utilization=0.9,
    max_model_len=4096,
)

sampling_params = SamplingParams(temperature=0.7, max_tokens=100)
outputs = llm.generate(["Hello!"], sampling_params)
```

For local use, GGUF is the format of choice:

```bash
# Ollama with GGUF
ollama run llama3:8b-q4_K_M

# llama.cpp directly
./main -m llama-3-8b-q4_K_M.gguf -p "Hello!"
```

### Quantizing your own model

```python
# GPTQ quantization with AutoGPTQ
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

model_path = "meta-llama/Llama-3-8B"
quant_path = "Llama-3-8B-GPTQ-4bit"

quant_config = BaseQuantizeConfig(
    bits=4,
    group_size=128,
    desc_act=False,
)

tokenizer = AutoTokenizer.from_pretrained(model_path)
examples = load_calibration_data(tokenizer, n_samples=128, seq_len=512)

model = AutoGPTQForCausalLM.from_pretrained(model_path, quant_config)
model.quantize(examples)
model.save_quantized(quant_path)
```

Note the calibration data in that example: GPTQ/AWQ are only as good as their calibration data. Use representative data from your domain; don't use random text.

## Quality impact

| Method      | Bits | Perplexity change vs FP16 | Notes                          |
|-------------|------|---------------------------|--------------------------------|
| FP8         | 8    | <0.5%                     | Near-lossless.                 |
| INT8 (RTN)  | 8    | ~1%                       | Acceptable.                    |
| INT8 (SQ)   | 8    | <0.5%                     | Better than RTN.               |
| INT4 (RTN)  | 4    | Significant degradation   | Not recommended.               |
| INT4 (GPTQ) | 4    | ~1-2%                     | Excellent for 4-bit.           |
| INT4 (AWQ)  | 4    | ~1-2%                     | Comparable to GPTQ.            |
| INT4 (GGUF Q4_K_M) | 4 | ~2-3%                  | Good for local use.            |
| INT3 (GPTQ) | 3    | ~3-5%                     | Noticeable degradation.        |
| INT2        | 2    | Significant degradation   | Experimental.                  |

### Quality varies by task

- **Generation**: more sensitive (small errors compound).
- **Classification**: less sensitive (just need the right argmax).
- **Retrieval**: depends on the embedding model.
- **Math/code**: more sensitive (small numerical errors break correctness).

Always benchmark on your specific task, not just aggregate benchmarks — aggregate benchmarks may not reflect your use case.

## Production guidance

Quantization is **the** biggest inference optimization. Without it, serving 70B models would require multi-GPU setups everywhere. The open-source ecosystem (vLLM, Ollama, llama.cpp) is built on quantization — most local LLM use is INT4. For production, quantization enables 4-8× more concurrent requests per GPU. FP8 is the new standard for Hopper+ — it combines INT8's speed with FP16's quality — and quantization also enables edge deployment (mobile, browser, embedded) where memory is constrained.

The working recommendations:

- **For production serving**: use AWQ or GPTQ INT4 on vLLM. Best quality/speed/memory balance.
- **For local / consumer GPU**: use GGUF (Q4_K_M) with llama.cpp or Ollama.
- **For H100 clusters**: use FP8 (better quality than INT4, similar memory).
- **For 7B models**: INT8 is often enough; quality loss is minimal.
- **For 70B+ models**: INT4 is usually necessary to fit on available GPUs.

Mixed precision applies within a single model too: some layers (e.g., embeddings, output projection) are more sensitive — keep them in higher precision and quantize the rest. And practice versioning: store the quantization method with the model. A "GPTQ-4bit" model needs GPTQ inference; don't try to load it as AWQ.

### Fitting a 70B model on a single 80GB H100

Use FP8 for weights (70 GB) + FP8 KV cache. Total: ~70 GB weights + ~10 GB KV cache (for 8K context) = 80 GB. Just fits. For more context, use INT4 weights (35 GB) + FP8 KV cache.

### Decision framework

| Use Case | Recommended Method | Why |
|----------|-------------------|-----|
| Production serving (H100) | FP8 | Best quality at INT8 memory |
| Production serving (A100) | AWQ INT4 | Best quality at INT4 memory |
| Production serving (consumer GPU) | GGUF Q4_K_M | Designed for consumer hardware |
| Local development | GGUF Q4_K_M | Easy to use with Ollama |
| Fine-tuning (memory-constrained) | QLoRA NF4 | Designed for training |
| Maximum quality | FP16/BF16 | No quantization |
| Maximum throughput | INT4 (AWQ or GPTQ) | Fastest matmuls |
| Long-context | INT4 weights + FP8 KV cache | Both matter |
| Edge / mobile | INT2/INT4 (experimental) | Memory-constrained |

## Common pitfalls

- **Using RTN for INT4** — significant quality loss. Always use GPTQ/AWQ for INT4.
- **Forgetting to apply the same quantization to merged LoRA** — fine-tune in BF16, merge the [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] adapter, then quantize for inference. Don't quantize before merging.
- **Mixing quantization formats** — a model quantized with AWQ needs AWQ inference. Don't try to load with GPTQ.
- **Ignoring activation quantization** — for some workloads, activations (not weights) are the bottleneck. Profile before assuming weights are the issue.
- **Wrong group size** — GPTQ/AWQ use block-wise quantization; smaller groups = better quality but more metadata. 128 is a common default.
- **Bad calibration data** — use representative data; don't use random text.
- **Forgetting KV cache quantization** — for long-context, weight quantization alone isn't enough. Quantize the KV cache too. Often the difference between fitting and OOM.
- **Numerical instability** — INT4 can produce NaNs in rare cases. Have a fallback to FP16.
- **Wrong dtype in serving** — vLLM/TGI need the right `quantization` and `dtype` flags. Mismatched flags cause errors or quality degradation.
- **Not benchmarking** — always benchmark on your specific workload.
- **Ignoring hardware support** — INT4 requires specific GPU features. Don't assume INT4 works on all GPUs.

## Further reading

- Frantar et al. (2022), *GPTQ: Accurate Post-Training Quantization*.
- Lin et al. (2023), *AWQ: Activation-aware Weight Quantization*.
- Xiao et al. (2022), *SmoothQuant: Accurate and Efficient Post-Training Quantization*.
- Micikevicius et al. (2022), *FP8 Formats for Deep Learning*.
- llama.cpp's GGUF documentation.
- Dettmers et al. (2023), *QLoRA: Efficient Finetuning of Quantized LLMs*.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[KV Cache Mechanics]] — what gets cached and why the KV cache dominates long-context memory.
- [[PagedAttention]] — memory management for the KV cache.
- [[Speculative Decoding]] — complementary inference optimization.
- [[Mixed Precision Training]] — the training-side counterpart of precision choice.
- [[QLoRA]] — NF4 quantization for fine-tuning.
- [[Continuous Batching]] — quantization raises how many requests fit per GPU.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — serving engines with GPTQ/AWQ/FP8 support.
