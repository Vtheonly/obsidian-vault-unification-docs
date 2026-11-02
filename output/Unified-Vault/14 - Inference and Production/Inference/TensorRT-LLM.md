---
title: TensorRT-LLM
type: concept
aliases: [TensorRT-LLM, TRT-LLM, NVIDIA Inference, Inference Engine]
tags: [inference, tensorrt-llm, nvidia, serving, deployment]
sources: ["08 — TensorRT-LLM (Inference Chapter Perspective)"]
created_index: 12
---

TensorRT-LLM is NVIDIA's highest-performance LLM serving engine for NVIDIA hardware. Its defining characteristic is compilation: the model is built once into a TensorRT engine — a binary with fused kernels, FP8/INT8 support, and platform-specific optimizations — so you trade build-time complexity for runtime performance. This note covers the inference characteristics (latency, throughput, memory, cost per token), the feature set (in-flight batching, FP8, speculative decoding, quantization, constrained decoding, streaming), deployment patterns from Triton to multi-node, and the trade-offs that decide when to choose it over [[14 - Inference and Production/Inference/vLLM|vLLM]], TGI, or SGLang.

> [!info] TL;DR
> TensorRT-LLM is the **highest-performance LLM serving engine on NVIDIA hardware**. It compiles a model into a TensorRT engine — a binary with fused kernels, FP8/INT8 support, and platform-specific optimizations. > The compilation step is the key difference from vLLM/TGI: you trade build-time complexity for runtime performance. For the framework-perspective treatment, see the frameworks-and-tools coverage of TensorRT-LLM.

## Why TensorRT-LLM for inference

Inference has different priorities than training:

- **Latency** matters more than throughput (users wait for tokens).
- **Cost-per-token** matters more than absolute speed (production economics).
- **Stability** matters more than flexibility (production uptime).
- **Numerical reproducibility** may matter (regulated industries).

TensorRT-LLM is optimized for these priorities. It compiles the model once into a binary that runs optimally on the target GPU, with no Python overhead in the hot path. For latency-sensitive applications (real-time chat, voice agents, interactive tools), TensorRT-LLM delivers the lowest per-token latency of any open-source engine.

## Performance characteristics

### Latency

For a 7B model on H100 (FP8):

| Engine         | Prefill (1000 tokens) | Per-token decode | Total (100 + 100 tokens) |
|----------------|----------------------|------------------|--------------------------|
| TensorRT-LLM   | ~15ms                | ~5ms             | ~25ms                    |
| vLLM           | ~25ms                | ~8ms             | ~40ms                    |
| TGI            | ~30ms                | ~10ms            | ~50ms                    |

(The numbers are approximate; actual performance depends on workload.)

The latency advantage comes from:

- **Fused kernels**: multiple operations (QKV, softmax, FFN) compiled into single CUDA kernels, reducing kernel launch overhead.
- **WGMMA on Hopper**: Hopper's warpgroup matrix multiply-accumulate instructions, used by TensorRT-LLM's FP8 kernels.
- **Async execution**: compute and memory transfer overlap, hiding latency.

### Throughput

For a 7B model on H100 (FP8, batched):

| Engine         | Tokens/sec | Requests/sec (avg 200 tokens) |
|----------------|------------|-------------------------------|
| TensorRT-LLM   | ~25,000    | ~125                          |
| vLLM           | ~18,000    | ~90                           |
| TGI            | ~14,000    | ~70                           |

Throughput advantage is smaller than latency advantage because vLLM's PagedAttention is also highly optimized. The gap widens at scale (70B+) where TensorRT-LLM's optimizations compound.

### Memory

TensorRT-LLM uses memory more efficiently than vLLM for some workloads:

- **Weights**: same (both support INT4/INT8/FP8 quantization).
- **KV cache**: TensorRT-LLM uses block-based KV cache similar to PagedAttention, with NVIDIA-specific optimizations.
- **Activations**: TensorRT-LLM's kernel fusion reduces activation memory.

For 70B models on H100 80GB, TensorRT-LLM typically fits larger batches than vLLM at the same latency.

### Cost per token

Cost per token = (GPU-hour cost) / (tokens per hour). For H100 at ~$3/hour:

- TensorRT-LLM: $3 / (25,000 × 3600) = ~$0.00000003 per token = ~$0.03 per million tokens.
- vLLM: ~$0.04 per million tokens.
- TGI: ~$0.05 per million tokens.

The 20-40% cost reduction compounds at scale. For a service processing billions of tokens per day, TensorRT-LLM saves thousands of dollars per day.

## Inference features

### In-flight batching

TensorRT-LLM's continuous batching (called "in-flight batching" in NVIDIA's terminology) inserts and evicts requests at iteration boundaries, like vLLM's continuous batching. The implementation uses NVIDIA-specific kernel scheduling for tighter compute-memory overlap. Conceptually the algorithm is identical to vLLM's; the difference is in the kernel implementation (see [[Continuous Batching]] for the algorithm).

### FP8 inference

FP8 on H100 halves memory and doubles throughput vs. FP16. TensorRT-LLM has the most mature FP8 implementation:

- **Per-tensor scaling**: each weight and activation tensor is scaled to fit FP8's range (E4M3: ~0.002 to ~448). The scale is computed from the tensor's absmax.
- **E4M3 format**: used for both weights and activations (sufficient range for inference).
- **Quality preservation**: <1% degradation on most benchmarks.

For production deployment on H100, FP8 is the default for cost-sensitive workloads. The quality loss is minimal; the cost savings are significant.

### Speculative decoding

TensorRT-LLM supports speculative decoding with both draft-model and Medusa-style approaches. The engine handles the draft model's KV cache and the verification step efficiently.

### Quantization

TensorRT-LLM supports:

- **INT4 weight-only** (GPTQ-style): 4x memory reduction, slight quality loss.
- **INT8 weight-only**: 2x memory reduction, minimal quality loss.
- **INT8 weight-activation** (SmoothQuant): 2x memory + 2x throughput, more quality loss.
- **FP8**: 2x memory + 2x throughput, minimal quality loss (Hopper+).
- **FP4** (Blackwell+): 4x memory + 4x throughput (cutting edge).

The choice depends on hardware, quality requirements, and the specific model. FP8 is the production sweet spot on H100 (see [[Quantization]] for the format details).

### Constrained decoding

TensorRT-LLM supports JSON schema and regex constrained decoding via integration with `xgrammar` and `outlines`. The constraint engine is called from the C++ runtime, avoiding Python overhead.

### Streaming

TensorRT-LLM streams tokens via the OpenAI-compatible API (SSE) or via Triton's streaming protocol. Streaming latency (time to first token) is competitive with vLLM.

## Deployment patterns

### Triton Inference Server

The standard production deployment is via Triton Inference Server:

- **Triton** handles HTTP/gRPC, model repository, metrics, multi-model serving.
- **TensorRT-LLM backend** handles LLM-specific execution.
- **Triton's model repository** stores the compiled TensorRT engine.

```mermaid
graph TD
  Client[Client] -->|HTTP/gRPC| Triton[Triton Inference Server]
  Triton --> TensorRT-LLM[TensorRT-LLM Backend]
  TensorRT-LLM --> Engine[Compiled Engine .engine]
  Engine --> GPU1[GPU 0]
  Engine --> GPU2[GPU 1]
```

Triton provides:

- Multi-model serving (different engines on different GPUs).
- Model versioning (deploy new engine versions with traffic splitting).
- Metrics (Prometheus endpoint with per-model latency, throughput).
- Load balancing across multiple Triton instances.

### Standalone deployment

For simpler setups, TensorRT-LLM can be deployed standalone via its Python API:

```python
from tensorrt_llm import Runtime
runtime = Runtime("path/to/engine")
session = runtime.create_session()
output = session.generate(input_ids=input_ids)
```

This is appropriate for development or for embedding TensorRT-LLM in a custom serving stack.

### Multi-node deployment

For 70B+ models that don't fit on a single GPU:

- **Tensor parallelism**: shard each layer across GPUs.
- **Pipeline parallelism**: split layers across GPUs sequentially.
- **NCCL communication**: GPU-to-GPU communication via NCCL.

Multi-node requires InfiniBand or NVLink for acceptable latency. The deployment uses `mpirun` to launch workers on each node.

### Hybrid deployment (TensorRT-LLM + vLLM)

For fleets serving many models:

- **TensorRT-LLM** for the high-traffic models (where compilation cost is amortized).
- **vLLM** for the long-tail models (where compilation isn't worth it).

A router (LiteLLM or custom) routes requests based on model name. This combines TRT-LLM's performance with vLLM's flexibility.

## Trade-offs

### Build complexity

The biggest inference trade-off: TensorRT-LLM requires a build phase. You must:

1. Specify the model architecture (in Python or via a config file).
2. Choose precision and optimization settings.
3. Wait minutes-to-hours for compilation.
4. Test the engine produces correct output.
5. Deploy the engine to production.

vLLM has no build phase — you load the model and serve. This is a major operational advantage for vLLM in environments with rapid model turnover (testing many models, frequent updates).

### Engine specificity

Engines are specific to (model, GPU type, TensorRT-LLM version). For a fleet with multiple GPU types (A100, H100, B100), you need separate engines for each. Storage and version management become operational concerns.

### NVIDIA-only

TensorRT-LLM only runs on NVIDIA GPUs. If your fleet includes AMD or Intel GPUs, you need a different engine for those.

### Architecture support lag

When a new model architecture is released (e.g., Mamba, MLA), TensorRT-LLM support requires NVIDIA to write a plugin. This can take weeks-to-months. vLLM and TGI typically support new architectures within days via HuggingFace integration.

## When to choose TensorRT-LLM

Choose TensorRT-LLM when:

- **NVIDIA-only fleet** with strict latency targets.
- **High-traffic models** where compilation cost is amortized over many requests.
- **70B+ models** where every optimization compounds.
- **FP8 on H100** is a cost requirement.
- **Triton is already your serving infrastructure**.

Choose vLLM when:

- **Multi-vendor fleet** (AMD, Intel GPUs).
- **Frequent model changes** (build phase is too slow).
- **Cutting-edge architectures** not yet supported by TensorRT-LLM.
- **Simpler deployment** is more important than peak performance.

Choose TGI when:

- **HuggingFace-model compatibility** is critical.
- **Chat templates** are important.
- **Ease of deployment** matters more than peak performance.

Choose SGLang when:

- **Agentic workloads** with prefix sharing.
- **Structured output** is the primary use case.

## Production best practices

Build engines once per (model, GPU type, TRT-LLM version) and cache them in artifact storage (S3, NFS); don't rebuild on every deploy, and version the engine files explicitly. Pin versions: TRT-LLM versions are not backward-compatible, so pin the Docker image, engine version, and runtime version, and test upgrades in staging. Use FP8 by default on H100 — the 1% quality loss is worth the 2× cost reduction for most workloads. Have a vLLM fallback for models or architectures TRT-LLM doesn't yet support; the router can route supported models to TRT-LLM and unsupported models to vLLM. Monitor for numerical issues: TRT-LLM's aggressive optimizations can produce rare numerical instabilities (NaN, inf); monitor for these and have a fallback to FP16 if FP8 produces NaNs. For production, deploy via Triton Inference Server — don't roll your own serving layer on top of the Python API.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — the flexible alternative with no build phase.
- [[Continuous Batching]] — the algorithm behind in-flight batching.
- [[Quantization]] — INT4/INT8/FP8/FP4 formats in detail.
- [[Speculative Decoding]] — draft-model and Medusa-style acceleration.
- [[Constrained Decoding]] — JSON schema and regex support via xgrammar and outlines.
- [[Production AI Stack]] — where the serving engine sits in a production deployment.
