---
title: vLLM
type: concept
aliases: [vLLM, LLM Serving Engine, Serving]
tags: [inference, serving, vllm, continuous-batching, llm]
sources: ["04 - vLLM and Continuous Batching"]
created_index: 13
---

vLLM is the dominant open-source LLM serving engine and the de facto standard for production deployment of open models. Its throughput advantage rests on two coupled ideas — continuous batching at the iteration level and PagedAttention for KV-cache memory management — which together deliver 10–20x throughput over naive serving. This note covers why HuggingFace `generate` falls short, the engine's feature set and APIs, the alternative engines (TensorRT-LLM, TGI, SGLang, llama.cpp/Ollama) and how to choose among them, and the performance considerations and tuning knobs that govern production deployments.

> [!info] TL;DR
> vLLM is the dominant open-source LLM serving engine. Continuous batching + PagedAttention give 10–20x throughput vs naive serving. TensorRT-LLM and TGI are alternatives. The standard for production LLM deployment in 2026.

## Why not just use HuggingFace `generate`

Naive `model.generate()` has three problems:

1. **Batching is static**: a batch of 8 requests must all finish before any new request joins. Long requests delay the whole batch.
2. **No KV cache management**: each request allocates contiguous memory for the max possible length — wastes 60–80% to fragmentation.
3. **No prefix caching**: identical system prompts across requests are processed independently.

Production LLM serving needs to handle 100s–1000s of concurrent requests efficiently. That requires purpose-built infrastructure — and measured against it, serving with `model.generate()` directly is 10–20x slower than a real engine.

## Continuous batching (iteration-level batching)

Instead of batching requests for their **entire generation**, vLLM batches them **per iteration** (per token):

```text
Step 1: requests A, B, C generate token 1, 2, 1 (respectively)
Step 2: A finishes; D joins. B, C, D generate token 3, 2, 1
Step 3: C finishes; E joins. B, D, E generate token 4, 1, 1
...
```

At every step, the batch composition can change — finished requests leave, new requests join. This keeps the GPU saturated and minimizes tail latency. The contrast with static batching is stark: static batching forms a batch, processes it to completion, and returns all results, so the batch's wall-clock time is determined by the longest request; under continuous batching, at every iteration (token) the scheduler can insert new requests and evict finished ones. Combined with PagedAttention for KV cache management, continuous batching gives 10–20x throughput vs static batching — the same 10-20x vLLM delivers over naive `model.generate()` via continuous batching + PagedAttention. The scheduler's full algorithm is covered in [[Continuous Batching]].

## The vLLM engine

vLLM (Kwon et al. 2023) is the dominant open-source LLM serving engine. Key features:

- **PagedAttention**: KV cache as pages (see [[PagedAttention]]).
- **Continuous batching**: iteration-level.
- **Prefix caching**: shared prefixes (system prompts) cached across requests.
- **Tensor parallelism**: split model across GPUs.
- **Quantization support**: GPTQ, AWQ, FP8, INT8 KV cache.
- **LoRA serving**: serve multiple LoRA adapters on a single base model.
- **Speculative decoding**: with draft models.
- **OpenAI-compatible API**: drop-in replacement for OpenAI clients.

PagedAttention and continuous batching are the throughput core; the remaining features build on that foundation — prefix caching exploits the block structure, tensor parallelism and quantization fit larger models onto the same GPUs, and LoRA serving and speculative decoding extend what a single deployment can do.

### Prefix caching

If multiple requests share a common prefix (e.g., the same system prompt), their KV caches can share the prefix blocks. The prefix is computed once and reused. vLLM supports this via `--enable-prefix-caching`. It helps significantly for chatbot/RAG workloads where system prompts are shared; hit rate: 30-80% depending on workload.

## Running vLLM

### Serving from the command line

```bash
# Serve a model
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192
```

### The Python API

Or in Python:

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")
prompts = ["Hello!", "What is the capital of France?", "Write a poem."]
sampling = SamplingParams(temperature=0.7, max_tokens=100)
outputs = llm.generate(prompts, sampling)
for out in outputs:
    print(out.outputs[0].text)
```

### The OpenAI-compatible API server

```bash
vllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000
```

Then use any OpenAI-compatible client:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Alternatives

### TensorRT-LLM (NVIDIA)

[[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] has the highest performance on NVIDIA hardware. It is closed source (with open wrappers), compiles models to optimized NVIDIA kernels, and is best for pure-NVIDIA production deployments where every % matters.

### TGI (Text Generation Inference, HuggingFace)

HuggingFace's serving engine. Good ecosystem integration (HuggingFace Hub). Less performant than vLLM but easier to use. Used in HuggingFace's inference endpoints.

### SGLang

A newer open-source engine. RadixAttention for prefix caching (more flexible than vLLM's). Often outperforms vLLM on agentic / structured workloads. Active development.

### llama.cpp / Ollama

For local / consumer-GPU inference. GGUF format. CPU + GPU. Not for high-throughput production serving.

### MLPerf-style custom engines

For absolute maximum performance: custom CUDA kernels. Only worth it for hyperscale deployments.

## Choosing a serving engine

| Use case                          | Recommendation         |
|-----------------------------------|------------------------|
| General production                | vLLM                   |
| NVIDIA-only, max performance      | TensorRT-LLM           |
| HuggingFace ecosystem             | TGI                    |
| Agentic / structured output       | SGLang                 |
| Local / single user               | Ollama, llama.cpp      |
| Multi-LoRA serving                | vLLM (best support)    |
| Speculative decoding              | vLLM, SGLang           |

The decision rule behind the table: vLLM for general production (the default); TGI for the HuggingFace ecosystem; TensorRT-LLM for NVIDIA-only, max performance (compilation cost); SGLang for agentic/structured workloads (RadixAttention prefix caching); Ollama/llama.cpp for local/single user. For most teams: start with vLLM, and switch to TensorRT-LLM only if you need max performance on NVIDIA.

## Performance considerations

### Throughput vs latency

**Throughput** is tokens/sec across all requests, maximized by large batches. **Latency** is time-to-first-token and time-per-output-token for individual requests, maximized by small batches. There's a tradeoff: large batches improve throughput but increase per-request latency. Pick based on your use case (interactive chat = latency-sensitive; batch processing = throughput-sensitive).

### Prefill vs decode

**Prefill** (process the prompt) computes attention over all prompt tokens: it is compute-bound, parallelizable across tokens, and achieves high GPU utilization. **Decode** (generate new tokens) generates one token at a time, attending to prompt + generated tokens: it is memory-bound, sequential, and shows low GPU utilization at batch size 1. This is why batching matters more for decode — it amortizes the weight reads. Chunked prefill interleaves prefill chunks with decodes to smooth latency.

### Tuning knobs

vLLM exposes the knobs that govern all of the above:

- `--gpu-memory-utilization`: how much GPU memory vLLM can use. Higher = bigger batches.
- `--max-model-len`: max context length. Affects memory and KV cache size.
- `--tensor-parallel-size`: number of GPUs for tensor parallelism.
- `--enable-prefix-caching`: turn on prefix caching (default in recent vLLM).
- `--swap-space`: CPU memory for swapping KV cache (helps with overload).

## Why this matters

Production LLM deployment **requires** a proper serving engine. Using `model.generate()` directly is 10–20x slower. vLLM is the de facto open standard — knowing it is essential for any AI engineer deploying models. The continuous batching + PagedAttention pattern is now industry-standard; even commercial providers use variants of it.

## Production implications

Default to vLLM for serving open-source LLMs. Enable prefix caching for chatbot / RAG workloads. Quantize models (AWQ INT4) before serving — 4x memory reduction. Monitor GPU utilization — if <50%, increase batch size; if 100%, add GPUs. Use tensor parallelism for models >40GB (70B in fp16 needs TP=2 on H100). Use multi-LoRA serving for multi-tenant setups: load the base model once, swap adapters per request.

## Common pitfalls

The recurring failure modes:

- **Wrong `gpu-memory-utilization`** — too high → OOM; too low → wasted capacity.
- **Forgetting to set `max-model-len`** — defaults can cause OOM with long prompts.
- **Not enabling prefix caching** — major throughput loss for chatbot workloads.
- **Serving the base model instead of Instruct** — base models don't follow instructions.
- **Using `model.generate()` in production** — 10–20x slower than vLLM.

## Further reading

For primary sources, see Kwon et al. (2023), *Efficient Memory Management for Large Language Model Serving with PagedAttention* (vLLM); the vLLM documentation at https://docs.vllm.ai; SGLang at https://github.com/sgl-project/sglang; and TensorRT-LLM at https://github.com/NVIDIA/TensorRT-LLM.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[PagedAttention]] — vLLM's memory management.
- [[Continuous Batching]] — the scheduling algorithm.
- [[Speculative Decoding]] — vLLM supports it.
- [[Quantization]] — vLLM supports INT4/INT8/FP8.
- [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — the NVIDIA-only, compile-for-performance alternative.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — the adapters served multi-tenant on a single base model.
- [[Production AI Stack]] — where the serving engine fits in production.
- [[KV Cache Mechanics]] — the memory PagedAttention manages.
