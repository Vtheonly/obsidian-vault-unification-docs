---
title: vLLM
type: concept
aliases: [vLLM, vLLM Framework, Inference Server]
tags: [framework, vllm, serving, inference, pagedattention]
sources: ["07 - vLLM"]
created_index: 26
---

vLLM is the dominant open-source LLM inference engine, built around PagedAttention (block-level KV cache management) and continuous batching. It delivers 2–4× higher throughput than naive serving, with prefix caching, tensor parallelism, and support for quantization. It has been the default choice for self-hosted LLM serving from 2024–2026 — if you're running an open-weights LLM in production, you're probably using vLLM. This note covers why vLLM exists, its core features, usage as a server and as a library, performance, strengths and weaknesses, and production patterns.

> [!info] TL;DR
> vLLM is the dominant open-source LLM inference engine, built around PagedAttention (block-level KV cache management) and continuous batching. It delivers 2–4× higher throughput than naive serving, with prefix caching, tensor parallelism, and support for quantization. vLLM is the default choice for self-hosted LLM serving in 2024–2026 — if you're running an open-weights LLM in production, you're probably using vLLM.

## Overview

vLLM comes from UC Berkeley / the vLLM project (2023, now community-maintained). It is written in Python + CUDA kernels and licensed Apache 2.0. It is actively developed and has become the standard for open-source LLM serving.

## Why vLLM exists

Before vLLM, serving LLMs was inefficient in three ways. Naive serving allocates a contiguous block of GPU memory per request, sized for the maximum sequence length — this wastes 60–80% of memory to internal fragmentation. Requests are batched statically: you wait to fill a batch, then process it together, which adds latency and underutilizes the GPU. And the KV cache cannot be shared across requests, even when they share prefixes (system prompts, few-shot examples).

vLLM — introduced in the [[PagedAttention and vLLM]] paper — solved these with three innovations: **PagedAttention**, block-level KV cache management (like OS paging); **continuous batching**, dynamic, per-iteration batching; and **prefix caching**, sharing the KV cache for common prefixes. The result is a 2–4× throughput improvement on the same hardware, with no quality loss (exact attention computation).

## Core features

### PagedAttention

The KV cache is divided into fixed-size blocks (typically 16 tokens). Each request has a block table mapping its logical token positions to physical blocks. Blocks are allocated on demand and freed when the request completes. The benefits:

- No internal fragmentation (only the last block in a request is partially unused).
- No external fragmentation (blocks are allocated from a pool).
- Blocks can be shared across requests (for common prefixes).

See [[PagedAttention]] and [[PagedAttention and vLLM]] for details.

### Continuous batching

At every decoding step, vLLM can admit new requests (if KV blocks are available), evict completed or preempted requests, and reorder requests to maximize GPU utilization. Unlike static batching, which waits to fill a batch, continuous batching processes whatever is currently active — this dramatically reduces latency for mixed workloads. [[Continuous Batching]] covers the technique in detail.

### Prefix caching

vLLM caches the KV blocks for recently seen prompts. If a new request's prompt starts with a cached prefix, the prefix blocks are reused without recomputation. For chat applications, where each turn repeats the prior conversation, this gives large latency and compute savings — often a 50–80% reduction in prefill compute for subsequent turns.

### Tensor parallelism

For models that don't fit on one GPU, vLLM supports tensor parallelism — splitting each layer's matrices across GPUs. It requires fast GPU-to-GPU interconnect (NVLink preferred).

```bash
# Launch with 4-way tensor parallelism
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4
```

### Quantization

vLLM supports multiple [[Quantization]] formats:

- **INT8**: 2× memory reduction, minimal quality loss.
- **INT4** (GPTQ, AWQ): 4× memory reduction, small quality loss.
- **FP8** (Hopper GPUs): 2× throughput on H100.
- **GGUF**: for CPU inference (limited support).

Quantization lets you run larger models on smaller GPUs. A 70B model in INT4 fits on a single 80GB GPU; in FP16 it needs 2 GPUs.

### LoRA serving

vLLM can serve multiple [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] adapters from a single base model. This is the "one base model + many adapters" deployment pattern: load the base model once, load multiple LoRA adapters (each is small, ~100MB), and route requests to the appropriate adapter based on the request. This is dramatically more efficient than serving each adapter as a separate model.

### OpenAI-compatible API

vLLM's server implements the OpenAI API: `/v1/chat/completions` for chat completions, `/v1/completions` for text completions, and `/v1/embeddings` for embeddings (if the model supports them). This means any code written for OpenAI works with vLLM by changing the `base_url`.

### Streaming

vLLM supports streaming responses via Server-Sent Events (SSE), compatible with the OpenAI streaming format.

## Usage

### As a server

```bash
# Start the server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000

# Use it like OpenAI
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}]
    }'
```

### As a library

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct")
sampling_params = SamplingParams(temperature=0.7, max_tokens=100)

outputs = llm.generate(["Hello, how are you?"], sampling_params)
print(outputs[0].outputs[0].text)
```

### With tensor parallelism

```python
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,
    quantization="awq",  # INT4 quantization
)
```

### With LoRA adapters

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    enable_lora=True,
    max_loras=4,
    max_lora_rank=16,
)

outputs = llm.generate(
    prompts=["Customer question..."],
    sampling_params=SamplingParams(),
    lora_request=LoRARequest(lora_name="customer_support", lora_int_id=1, lora_local_path="/path/to/lora"),
)
```

## Performance

Typical throughput improvements over naive serving (HuggingFace Transformers):

| Model         | HF Transformers | vLLM  | Speedup |
|---------------|-----------------|-------|---------|
| Llama-7B      | 1.0×            | 3.5×  | 3.5×    |
| Llama-13B     | 1.0×            | 3.0×  | 3.0×    |
| Llama-70B     | 1.0×            | 2.5×  | 2.5×    |

With prefix caching on chat workloads, expect an additional 1.5–2× throughput, because subsequent turns reuse the prefix.

## Strengths

### Performance

vLLM is the fastest open-source LLM server for most workloads. PagedAttention + continuous batching + prefix caching together deliver 2–4× over naive serving.

### OpenAI compatibility

The OpenAI-compatible API means existing code works without modification. This is a huge adoption advantage — you can switch from OpenAI to self-hosted vLLM by changing one URL.

### Model support

vLLM supports most popular open-weights models: Llama, Mistral, Qwen, DeepSeek, Gemma, Phi, and many more. New models are added quickly after release.

### Quantization support

Multiple quantization formats (INT8, INT4, FP8) let you trade quality for memory/throughput. This is essential for running large models on limited hardware.

### LoRA support

Multi-LoRA serving enables the "one base + many adapters" pattern, which is dramatically more efficient than serving each adapter separately.

### Active development

vLLM has a large, active community. New features (FP8, speculative decoding, longer context) are added regularly — see [[Speculative Decoding]] for the acceleration technique behind one of them.

## Weaknesses

### GPU-specific

vLLM is optimized for NVIDIA GPUs. AMD support exists but is less mature. CPU inference is limited.

### Memory overhead

vLLM's KV cache management has some overhead. For very small models or very short sequences, the overhead may exceed the benefits.

### Configuration complexity

vLLM has many configuration options (block size, GPU memory utilization, max sequences, swap space). Tuning for optimal performance requires understanding these.

### No training support

vLLM is inference-only. For training or fine-tuning, use other frameworks (HuggingFace Transformers, PyTorch FSDP, DeepSpeed).

### Limited long-context optimization

For very long contexts (>32K), vLLM's performance degrades. Specialized long-context servers (Ring Attention, distributed inference) may be better.

## Comparison to alternatives

| Server           | Strengths                          | Weaknesses                       | Best For                          |
|------------------|------------------------------------|----------------------------------|-----------------------------------|
| vLLM             | Performance, OpenAI-compat, community | GPU-specific, config complexity  | Most production serving           |
| TGI (HuggingFace)| Production features, simple        | Slower than vLLM                 | HuggingFace ecosystem users       |
| TensorRT-LLM     | NVIDIA-optimized, fastest on H100  | Complex setup, NVIDIA-only       | Maximum performance on NVIDIA     |
| Ollama           | Simple, local, CPU+GPU             | Not for high-throughput serving  | Local development, small scale    |
| llama.cpp        | CPU, mobile, embedded              | Low throughput                   | Edge devices, local use           |

vLLM is the default for production serving. [[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]] may be faster on H100 but is harder to use. [[TGI]], [[SGLang]], and [[Ollama and llama.cpp]] are the adjacent options in this area.

## Production patterns

### Right-size GPU memory utilization

vLLM's `gpu_memory_utilization` parameter controls how much GPU memory is used for the KV cache. Set it high enough to maximize throughput but low enough to leave room for other processes:

```bash
--gpu-memory-utilization 0.9  # use 90% of GPU memory
```

### Enable prefix caching

For chat applications, enable prefix caching (`--enable-prefix-caching`). This gives 1.5–2× throughput on multi-turn conversations.

### Use quantization for large models

For models that don't fit on your GPUs in FP16, use quantization: INT8 for a 2× reduction (minimal quality loss), AWQ or GPTQ INT4 for a 4× reduction (small quality loss), and FP8 on H100 for 2× throughput.

### Monitor queue depth

Monitor the request queue depth. If it grows, you need more replicas or a larger GPU. vLLM's metrics endpoint provides this data.

### Use multiple replicas behind a load balancer

For high availability and throughput, run multiple vLLM replicas behind a load balancer (NGINX, HAProxy, Kubernetes Service).

### Pin model versions

When using HuggingFace model IDs, pin to specific revisions to avoid silent updates:

```bash
--model meta-llama/Llama-3.1-8B-Instruct --revision abc123
```

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[PagedAttention and vLLM]] — the paper that introduced PagedAttention and vLLM.
- [[PagedAttention]] — the block-level KV cache technique.
- [[Continuous Batching]] — the dynamic batching technique.
- [[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]] — the NVIDIA-optimized alternative.
- [[TGI]] — the HuggingFace serving alternative.
- [[SGLang]] — the serving engine with automatic prefix caching.
- [[Ollama and llama.cpp]] — local and edge serving.
- [[Quantization]] — the quantization formats vLLM supports.
- [[Speculative Decoding]] — a decoding-acceleration feature added to vLLM.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — the adapter technique behind multi-LoRA serving.
- [[GPU Infrastructure and Sizing]] — hardware planning for serving workloads.
