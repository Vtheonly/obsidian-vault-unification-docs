---
title: TGI
type: concept
aliases: [TGI, Text Generation Inference, HuggingFace TGI]
tags: [framework, tgi, huggingface, serving, inference]
sources: ["12 - TGI"]
created_index: 24
---

TGI (Text Generation Inference) is HuggingFace's production LLM serving engine: a Rust-based router with Python-based model execution, optimized for HuggingFace-model compatibility (transformers, tokenizers, Hub integration) and ease of deployment. It supports continuous batching, tensor parallelism, quantization, and OpenAI-compatible APIs, making it the default serving choice when you want to deploy a HuggingFace model with minimal configuration. It is less aggressively optimized than [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] or [[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]], but it has the best out-of-the-box experience for HuggingFace-model deployments.

> [!info] TL;DR
> TGI is HuggingFace's production LLM serving engine. It's a Rust-based router with Python-based model execution, optimized for HuggingFace-model compatibility (transformers, tokenizers, Hub integration) and ease of deployment. TGI is the default serving choice when you want to deploy a HuggingFace model with minimal configuration. It supports continuous batching, tensor parallelism, quantization, and OpenAI-compatible APIs. TGI is less aggressively optimized than vLLM or TensorRT-LLM but has the best out-of-the-box experience for HuggingFace-model deployments.

## Overview

TGI is developed by HuggingFace. The router is written in Rust and the model code in Python. It is open-source under Apache 2.0, and HuggingFace also offers a managed Inference Endpoints service built on it. It is actively developed and is the default serving engine for HuggingFace's own Inference Endpoints.

## Why TGI exists

vLLM is the most aggressive open-source serving engine, but it's tightly coupled to its own model implementations. If you want to serve a model from the HuggingFace Hub that vLLM doesn't yet support, you're stuck. TGI was built to fill that gap:

- **Hub integration**: any model on the HuggingFace Hub works out of the box.
- **Tokenizer compatibility**: HuggingFace tokenizers, chat templates, and special tokens all work natively.
- **Chat templates**: TGI respects the model's `chat_template` field, so conversational models work without manual prompt engineering.
- **Simplified deployment**: a single Docker command launches a fully-functional API.

TGI trades raw throughput for compatibility and ease of use. For most teams, that's the right trade-off — they'd rather have a working endpoint today than a 20% faster endpoint next week.

## Core concepts

### The router (Rust)

The router is the front-end that accepts HTTP requests. It's written in Rust for performance and handles:

- Request queuing and batching.
- Token streaming via SSE.
- OpenAI-compatible `/v1/chat/completions` and `/v1/completions` endpoints.
- A native `/generate` endpoint with TGI-specific extensions (best-of-N, watermarking, grammar-based decoding).
- Load balancing across multiple model workers.

The Rust router is one of TGI's distinctive design choices. It keeps request handling fast and memory-safe even under heavy load.

### The model server (Python)

The model server is Python-based, using HuggingFace `transformers` and `accelerate`. It runs the actual model forward pass. The server supports:

- Tensor parallelism via `accelerate`.
- Quantization via `bitsandbytes` (4-bit, 8-bit) and GPTQ/AWQ.
- Flash Attention 2 integration (see [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]).
- Custom model code (via HuggingFace's `trust_remote_code`).

### Continuous batching

TGI implements continuous batching (also called iteration-level batching). New requests are inserted into the active batch as soon as a slot frees up, without waiting for the current batch to complete. This is the same fundamental technique as vLLM's [[Continuous Batching|continuous batching]] — both engines independently arrived at the same approach.

### PagedAttention (partial)

TGI does **not** implement full [[PagedAttention]] (the paging-based KV cache memory management that vLLM pioneered). Instead, TGI uses a more conventional KV cache layout with bucketed sequence lengths. This means TGI's memory efficiency is lower than vLLM's for highly variable sequence lengths, but the implementation is simpler and works with a wider range of model architectures.

### Chat templates

TGI reads the `chat_template` field from the model's tokenizer config. This means chat models work out of the box:

```bash
docker run -p 8080:80 ghcr.io/huggingface/text-generation-inference:latest \
  --model meta-llama/Llama-3.1-8B-Instruct
```

The endpoint will apply Llama-3's chat template automatically when you call `/v1/chat/completions`. No manual prompt formatting.

### Quantization

TGI supports several [[Quantization|quantization formats]]:

- **bitsandbytes** (4-bit, 8-bit): easy to use, moderate speedup.
- **GPTQ**: post-training quantization, INT4 weights.
- **AWQ**: activation-aware quantization, INT4 weights.
- **EETQ** (8-bit): faster than bitsandbytes for some models.
- **FP8** (Hopper+): via `transformers` integration.

Quantization is configured at startup:

```bash
docker run ... --model TheBloke/Llama-2-13B-AWQ --quantize awq
```

### Watermarking

TGI implements the Kirchenbauer et al. (2023) watermarking scheme. When enabled (`--watermark 1`), the model subtly biases the selection of "green" tokens during sampling. The watermark is detectable later without affecting generation quality. This is useful for distinguishing AI-generated text from human text in safety-critical applications.

### Grammar-based decoding

TGI supports grammar-constrained decoding via the Outlines library. You can specify a JSON schema or grammar and TGI will force the model's output to conform:

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Extract the user info"}],
    "response_format": {
      "type": "json_schema",
      "json_schema": {"schema": {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}}
    }
  }'
```

The output is guaranteed to validate against the schema. This is essential for downstream code that parses model output, and it is the same guarantee that [[Constrained Decoding]] provides at the token level.

## Common deployment patterns

### Single-container deployment

The simplest pattern: one Docker container, one model, one port. Ideal for development and small-scale production.

```bash
docker run --gpus all -p 8080:80 \
  -v /data:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --sharded 1 \
  --quantize awq
```

### Multi-GPU sharding

For models that don't fit on one GPU, TGI supports tensor parallelism via `--sharded N`:

```bash
docker run --gpus all -p 8080:80 \
  ... \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --sharded 4
```

This shards the model across 4 GPUs using `accelerate`'s tensor parallelism. Less efficient than Megatron-style TP (no custom kernels) but works for any HuggingFace model.

### Inference endpoints (managed)

HuggingFace offers a managed TGI service (Inference Endpoints). You pick a model and a GPU type; HuggingFace handles deployment, scaling, and updates. Useful for teams that don't want to operate GPU infrastructure.

### Multi-model routing

For production, run TGI behind a router (like LiteLLM or an internal gateway) that routes requests to different TGI instances based on model name. Each TGI instance serves one model; the router provides a unified API.

## Comparison to alternatives

| Engine         | Optimization Focus         | Model Compatibility        | Best For                              |
|----------------|----------------------------|-----------------------------|---------------------------------------|
| TGI            | HF model compatibility     | Excellent (any HF model)    | HF-model deployments, ease of use     |
| vLLM           | Throughput, PagedAttention | Good (HF + custom)          | Max-throughput production             |
| TensorRT-LLM   | NVIDIA-specific kernels    | Requires conversion         | NVIDIA-only, max performance          |
| SGLang         | RadixAttention, structured | Good (HF + custom)          | Structured outputs, prefix caching    |
| Ollama         | Local UX                   | GGUF quantized models       | Local development                     |

TGI's distinct strength is **HuggingFace compatibility**: any model from the Hub, including custom architectures, works with minimal configuration. The trade-off is raw throughput — vLLM and TensorRT-LLM are faster on benchmarks, but they require more setup and may not support every model.

## Strengths

**Hub integration.** Any model on the HuggingFace Hub works. Custom architectures via `trust_remote_code`. Tokenizers, chat templates, special tokens — all native. This is TGI's killer feature.

**Easy deployment.** A single Docker command launches a working API. No model conversion, no kernel compilation, no YAML. For teams new to LLM serving, TGI has the lowest activation energy.

**OpenAI API compatibility.** The `/v1/chat/completions` and `/v1/completions` endpoints are OpenAI-compatible. Most client libraries (LangChain, OpenAI SDK, etc.) work with TGI as a drop-in replacement for OpenAI.

**Rust router performance.** The Rust router handles thousands of concurrent connections with low overhead. The Python model server is the bottleneck, not the router.

**Chat template support.** Chat templates work automatically. No manual prompt engineering, no per-model adapter code. This is a major productivity win for teams serving many models.

## Weaknesses

**Slower than vLLM.** Without PagedAttention, TGI's KV cache management is less efficient. For workloads with highly variable sequence lengths and high concurrency, vLLM's memory efficiency translates to higher throughput. TGI's gap is typically 10–30% on throughput benchmarks.

**Less aggressive optimization.** TGI doesn't have the kernel-level optimizations of TensorRT-LLM (custom GEMM kernels, FP8 on Hopper, etc.). For NVIDIA-only deployments where every microsecond matters, TensorRT-LLM is faster.

**Smaller community than vLLM.** vLLM has a larger open-source community and more rapid feature development. TGI's development is more closely tied to HuggingFace's roadmap.

**Quantization variety but not unified.** TGI supports multiple quantization formats (bitsandbytes, GPTQ, AWQ, EETQ, FP8) but each has different setup, performance characteristics, and model support. Choosing the right one requires experimentation.

## Production patterns

### Use Docker for deployment

TGI is designed to run in Docker. The official image is well-maintained and includes all dependencies. Don't try to install TGI natively — Docker is the supported path.

### Pin the image version

TGI versions change frequently, and breaking changes happen. Pin the image tag (`ghcr.io/huggingface/text-generation-inference:2.3.0` not `:latest`) and test upgrades in staging.

### Use AWQ for INT4 quantization

For INT4 quantization, AWQ generally gives better quality than GPTQ and similar throughput. The Bloke's AWQ-quantized models on the Hub are widely compatible.

### Enable chat templates

Always use chat templates via `/v1/chat/completions`. The raw `/generate` endpoint requires manual prompt formatting and is more error-prone.

### Set memory limits

Configure `--max-batch-prefill-tokens` and `--max-total-tokens` to bound memory usage. Without these, a single long request can OOM the server.

### Monitor queue depth

TGI's router exposes Prometheus metrics. Monitor `tgi_queue_size` — if it grows, you need to scale out (more replicas) or scale up (bigger GPUs).

### Use a router for multi-model

For multi-model deployments, run TGI behind LiteLLM or a custom gateway. Each TGI instance serves one model; the router handles model routing, rate limiting, and auth.

## When to use TGI

TGI is a good fit when HuggingFace compatibility and setup speed dominate:

- **HuggingFace-model deployments**: any model from the Hub, especially custom architectures.
- **Teams new to LLM serving**: easiest setup of any major engine.
- **Conversational models**: chat templates work out of the box.
- **Mixed-model fleets**: consistent API across many models.
- **HuggingFace Inference Endpoints**: managed TGI is the natural extension.

It is a poor fit when raw performance or local development dominates:

- **Max-throughput workloads**: vLLM is faster.
- **NVIDIA-only with strict latency targets**: TensorRT-LLM is faster.
- **Heavy structured generation**: SGLang's RadixAttention is more efficient.
- **Local development**: [[Ollama and llama.cpp]] is easier.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] — the higher-throughput alternative.
- [[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]] — the NVIDIA-optimized alternative.
- [[SGLang]] — the structured-generation alternative.
- [[Ollama and llama.cpp]] — the local inference alternative.
- [[Continuous Batching]] — the batching technique TGI and vLLM share.
- [[PagedAttention]] — the KV cache technique TGI only partially implements.
- [[Quantization]] — the quantization formats TGI supports.
- [[Constrained Decoding]] — the technique behind grammar-based decoding.
- [[Framework Selection Guide]] — choosing among serving engines.
