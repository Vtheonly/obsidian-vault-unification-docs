---
title: TensorRT-LLM
type: concept
aliases: [TensorRT-LLM, TRT-LLM, NVIDIA TensorRT-LLM]
tags: [framework, tensorrt-llm, nvidia, serving, inference, optimization]
sources: ["13 - TensorRT-LLM"]
created_index: 25
---

TensorRT-LLM is NVIDIA's library for building optimized LLM inference engines on NVIDIA GPUs. It works by compiling a model into a TensorRT engine — a binary artifact containing fused kernels, FP8/INT8/INT4 kernels, and platform-specific optimizations for the exact GPU you compiled on. Of the major serving engines it delivers the highest throughput and lowest latency on NVIDIA hardware, but you pay for that with a complex build pipeline, model-specific compilation, and tight NVIDIA coupling. It is the engine of choice when every millisecond and every dollar of GPU spend matters.

> [!info] TL;DR
> TensorRT-LLM is NVIDIA's library for building optimized LLM inference engines on NVIDIA GPUs. It compiles a model into a TensorRT engine — a binary artifact containing fused kernels, FP8/INT8/INT4 kernels, and platform-specific optimizations for the exact GPU you compiled on. TensorRT-LLM delivers the **highest throughput and lowest latency** of any major serving engine on NVIDIA hardware, at the cost of a complex build pipeline, model-specific compilation, and tight NVIDIA coupling. It's the choice when every millisecond and every dollar of GPU spend matters.

## Overview

TensorRT-LLM is developed by NVIDIA. The runtime is C++, while the API and build pipeline are Python. The library is open-source under Apache 2.0, with proprietary optimizations living in the CUDA kernels. It is actively developed and releases approximately quarterly, adding new GPU support (Hopper, Blackwell) and new model architectures.

## Why TensorRT-LLM exists

General-purpose serving engines such as [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] and [[TGI]] prioritize portability and ease of use. They use generic kernels that work across GPU architectures and model families, and this generality leaves performance on the table. NVIDIA builds the hardware and knows exactly which kernel sequences are optimal for each GPU generation, so they can write:

- **Fused kernels** that combine multiple operations into a single GPU kernel (e.g., fused QKV projection, fused softmax+dropout+matmul).
- **Platform-specific kernels** that use Hopper's WGMMA (warpgroup matrix multiply-accumulate) instructions or Blackwell's tensor memory accelerator.
- **Custom FP8/INT8/INT4 kernels** that match the hardware's quantization support exactly.
- **In-flight batching** schedulers that overlap compute and memory transfer at the GPU level.

TensorRT-LLM is the vehicle for delivering these optimizations to LLM serving. The trade-off is that you must compile a model into a TensorRT engine before serving it, and the engine is specific to the GPU type and TensorRT-LLM version you compiled with.

## Core concepts

### The build phase

The first phase is building a TensorRT engine from a model. You provide the model weights (HuggingFace format, ONNX, or Nemo), the model architecture (defined in Python via TensorRT-LLM's `tensorrt_llm` package), and a build configuration covering precision (FP32/FP16/BF16/FP8/INT8/INT4), plugin settings, max batch size, max sequence length, and similar options:

```python
from tensorrt_llm import Builder, ModelConfig

config = ModelConfig(
    architecture="LlamaForCausalLM",
    num_layers=32,
    num_heads=32,
    hidden_size=4096,
    vocab_size=32000,
    precision="fp16",
    max_batch_size=256,
    max_seq_len=4096,
)
builder = Builder()
engine = builder.build(config, weights="path/to/weights")
engine.save("llama-7b-engine")
```

The build takes minutes to hours, depending on model size and optimization level. The output is a binary `engine` file plus a `config.json` describing the engine.

### The runtime phase

At serving time, you load the engine and run inference:

```python
from tensorrt_llm import Runtime

runtime = Runtime("llama-7b-engine")
session = runtime.create_session()
output = session.generate(
    input_ids=input_ids,
    max_new_tokens=128,
    temperature=0.7,
)
```

The runtime is what you deploy. It is fast — there is no Python overhead in the hot path for token generation, because the engine is a C++ binary.

### In-flight batching

TensorRT-LLM's scheduler is called **in-flight batching** (also known as [[Continuous Batching|continuous batching]]). New requests are inserted into the active batch at iteration boundaries, and the scheduler tracks each request's progress (prefill vs. decode) and interleaves them optimally. Compared to vLLM's continuous batching, TensorRT-LLM's in-flight batching is more aggressive about overlapping compute and memory transfer, which produces higher throughput — especially on Hopper, where async warpgroups enable the overlap.

### PagedAttention equivalent

TensorRT-LLM implements its own KV cache management, conceptually similar to [[PagedAttention]] but with NVIDIA-specific optimizations. The KV cache is organized into blocks; blocks are allocated and freed dynamically; attention kernels handle the block lookup efficiently.

### Quantization

TensorRT-LLM supports a wide range of [[Quantization|quantization formats]]:

- **FP8** (Hopper H100+): per-tensor or per-channel scaling.
- **INT8 weight-only**: weights INT8, activations FP16.
- **INT8 weight-activation** (smoothquant-style): both weights and activations INT8.
- **INT4 weight-only**: weights INT4 (GPTQ-style), activations FP16.
- **FP4/INT4 with FP8 activations** (Blackwell B100+): next-generation low-precision.

NVIDIA provides a quantization toolkit (`tensorrt_llm.quantization`) that converts HuggingFace weights to these formats. The toolkit supports calibration (for INT8 weight-activation) and per-channel scaling.

### Plugin architecture

Some operations don't have native TensorRT implementations (e.g., custom attention variants like MLA). TensorRT-LLM exposes a **plugin** API: you write a CUDA kernel, register it as a plugin, and reference it from your model definition. The plugin is then included in the compiled engine. This is how TensorRT-LLM supports novel architectures (Mamba, DeepSeek-V2's MLA, GQA variants) — by writing custom plugins for the novel ops.

### Tensor parallel and pipeline parallel

TensorRT-LLM supports both tensor parallelism (TP) and pipeline parallelism (PP) for multi-GPU serving. TP shards each layer across GPUs; PP splits layers across GPUs sequentially. For large models (70B+), you typically combine TP and PP (e.g., TP=4, PP=2 for 8 GPUs). The `mpirun`-based launcher handles multi-GPU coordination, and communication uses NCCL under the hood.

## Common deployment patterns

### Build once, serve many

Build the engine once per (model, GPU type, TensorRT-LLM version) combination. Cache the engine in artifact storage (S3, NFS). At deploy time, pull the engine and start the server — don't rebuild on every deploy.

### Multi-node serving for big models

For 70B+ models, deploy across multiple nodes. Each node runs a TensorRT-LLM worker; NCCL handles cross-node communication. This requires InfiniBand or NVLink for acceptable latency.

### Triton Inference Server integration

TensorRT-LLM integrates with NVIDIA Triton Inference Server. Triton handles the serving infrastructure (HTTP/gRPC, model repository, metrics); TensorRT-LLM handles the LLM backend. This is the standard production stack for NVIDIA-centric deployments.

### A/B testing via multiple engines

Deploy multiple engines (e.g., FP8 vs. FP16, or 7B vs. 70B) behind a router. Route requests based on cost/quality trade-offs. The router (LiteLLM, an internal gateway) handles the routing logic.

## Comparison to alternatives

| Engine         | Optimization Level          | NVIDIA Coupling    | Build Complexity    | Best For                            |
|----------------|----------------------------|---------------------|---------------------|-------------------------------------|
| TensorRT-LLM   | Maximum (custom kernels)   | Tight (NVIDIA-only) | High (build phase)  | NVIDIA-only max-performance         |
| vLLM           | High (PagedAttention)      | Loose (any GPU)    | Low (load and go)   | Production general-purpose          |
| TGI            | Medium                     | Loose (any GPU)    | Low (Docker)        | HuggingFace-model ease of use       |
| SGLang         | High (RadixAttention)      | Loose (any GPU)    | Low                 | Structured generation, prefix cache |

TensorRT-LLM's distinct strength is **maximum performance on NVIDIA hardware**. The trade-off is build complexity and tight NVIDIA coupling. If you're not on NVIDIA or you can't tolerate the build phase, use vLLM or [[SGLang]].

## Strengths

**Maximum throughput.** On NVIDIA hardware, TensorRT-LLM consistently delivers the highest throughput of any open-source serving engine. Typical gains over vLLM are 20–50% on H100 with FP8, and more on Blackwell with FP4.

**Maximum latency optimization.** For latency-sensitive applications (real-time chat, voice agents), TensorRT-LLM's kernel fusion and async execution reduce per-token latency. This matters when the user is waiting.

**Most mature FP8 support.** TensorRT-LLM has the most mature FP8 support of any open-source engine. FP8 on H100 typically gives 2× throughput over FP16 with minimal quality loss, making it the production default for cost-sensitive workloads.

**Custom plugin extensibility.** Novel architectures (Mamba, MLA, hybrid attention) can be supported via plugins. This is essential for serving cutting-edge models that other engines don't yet support.

**Triton integration.** Triton provides the serving infrastructure (model repository, metrics, multi-model serving) while TensorRT-LLM provides the LLM backend. Together they form a complete production stack.

## Weaknesses

**Build complexity.** The build phase is non-trivial. You must specify the architecture, configure precision, calibrate for INT8, and wait for compilation. For a new model, this can take hours of engineering work plus hours of compile time.

**Engine specificity.** Engines are specific to (model, GPU type, TensorRT-LLM version). You can't take an engine compiled for H100 and run it on A100, and you can't take an engine built with TRT-LLM 0.10 and run it on TRT-LLM 0.11. This complicates deployments.

**NVIDIA-only.** TensorRT-LLM only runs on NVIDIA GPUs. If you want to deploy on AMD or Intel GPUs, you need a different engine (vLLM, TGI). This locks you into NVIDIA hardware.

**Closed optimization details.** While TensorRT-LLM is open-source, many of its best optimizations (custom CUDA kernels, kernel fusion patterns) are opaque. You can't easily understand or modify them, which makes debugging performance issues harder.

**Slower architecture support.** When a new model architecture is released, vLLM and TGI typically support it within days (via HuggingFace integration). TensorRT-LLM support requires NVIDIA to write and ship a plugin, which can take weeks to months.

## Production patterns

### Cache engines aggressively

Build engines once per (model, GPU type, TRT-LLM version) and cache them. Don't rebuild on every deploy. Version the engine files and tag them with the TRT-LLM version so you know which runtime to use.

### Use FP8 by default on H100

For H100 deployments, FP8 is the production default. Quality loss is minimal (typically <1% on benchmarks) and throughput doubles. The exception is when you need exact reproducibility — FP8 has slight numerical variation.

### Use Triton for production

For production, deploy TensorRT-LLM via Triton Inference Server. Triton handles HTTP/gRPC, model repository, metrics, and multi-model serving. Don't roll your own serving layer.

### Pin versions

TRT-LLM versions are not backward-compatible. Pin the version in your Docker image, your engine builds, and your deployment scripts. Test upgrades in staging before production.

### Keep a vLLM fallback

For models or architectures TRT-LLM doesn't yet support, have a vLLM deployment as a fallback. The router can route supported models to TRT-LLM and unsupported models to vLLM.

### Monitor for numerical spikes

TRT-LLM's aggressive optimizations can produce rare numerical instabilities (NaN, inf) that don't appear in vLLM. Monitor for these and have a fallback to FP16 if FP8 produces NaNs.

## When to use TensorRT-LLM

TensorRT-LLM is a good fit when NVIDIA hardware and raw performance dominate the decision:

- **NVIDIA-only production deployments** where performance matters.
- **Latency-sensitive applications**: real-time chat, voice agents, interactive tools.
- **High-throughput cost optimization**: FP8 on H100 halves dollar-per-token.
- **Triton-based stacks**: TRT-LLM is the natural LLM backend.
- **Big-model serving**: 70B+ models where every optimization compounds.

It is a poor fit when portability, speed of setup, or brand-new architectures matter more:

- **AMD or Intel GPU deployments**: TRT-LLM is NVIDIA-only.
- **Cutting-edge architectures** (released in the last month): use vLLM until TRT-LLM adds support.
- **Small teams without ops capacity**: the build phase is too complex.
- **Multi-vendor fleets**: stick with vLLM for portability.
- **Rapid prototyping**: TGI or vLLM are faster to set up.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] — the general-purpose alternative.
- [[TGI]] — the HuggingFace-focused alternative.
- [[SGLang]] — the structured-generation alternative.
- [[Ollama and llama.cpp]] — local inference.
- [[Quantization]] — the quantization formats TensorRT-LLM supports.
- [[Continuous Batching]] — the technique TensorRT-LLM calls in-flight batching.
- [[PagedAttention]] — the related KV cache memory-management approach.
- [[KV Cache Mechanics]] — what the engine's block-based cache manages.
- [[Framework Selection Guide]] — choosing among serving engines.
