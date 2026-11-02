---
title: GPU Infrastructure and Sizing
type: concept
aliases: [GPU Infrastructure, GPU Sizing, GPU Deployment]
tags: [infrastructure, gpu, compute, sizing, deployment, cost-optimization]
sources: [04 — GPU Infrastructure and Sizing]
created_index: 1
---

GPUs are the dominant line item in AI infrastructure budgets, so decisions about GPU type, GPU count, and deployment model ripple through everything else: cost-per-token, achievable latency, and the largest model you can serve or train. This note covers the accelerator landscape, the memory arithmetic for sizing inference and training, the parallelism options when a model does not fit on one device, deployment models from managed APIs to owned hardware, and the operational concerns of running GPU fleets in production. Read it alongside the serving engines that build on this hardware — [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — and [[Inference and Production MOC]] for the surrounding area.

> [!info] TL;DR
> The GPU is the dominant cost in AI infrastructure. Choosing the right GPU type, count, and deployment model (owned vs. rented vs. managed) determines your cost-per-token, latency, and capability ceiling. For inference: A10/H100 for production, L4 for development. For training: H100 for frontier, A100 for fine-tuning. For most teams, cloud GPUs with reserved capacity beat owned hardware until scale justifies ownership.

## The GPU landscape

Between 2024 and 2026 the practical menu of accelerators is a short list of NVIDIA datacenter parts, one serious AMD contender, and a handful of specialized silicon. For LLM workloads, memory capacity and memory bandwidth matter as much as raw FLOPs, because decoding is usually memory-bound: the faster you can stream weights and KV cache out of HBM, the more tokens per second you get.

### NVIDIA datacenter GPUs

| GPU         | Hopper Gen | Ampere Gen | Memory       | Bandwidth | Best For                          |
|-------------|------------|------------|--------------|-----------|-----------------------------------|
| H100        | Yes        | -          | 80 GB HBM3   | 3.35 TB/s | Frontier training, large inference |
| H200        | Yes        | -          | 141 GB HBM3e | 4.8 TB/s  | Long-context inference, LLM training |
| B100/B200   | Blackwell  | -          | 192 GB HBM3e | 8 TB/s    | Next-gen training (2025+)          |
| A100 80GB   | -          | Yes        | 80 GB HBM2e  | 2.0 TB/s  | Fine-tuning, large-model inference |
| A100 40GB   | -          | Yes        | 40 GB HBM2e  | 1.5 TB/s  | Smaller models, development        |
| L40S        | Ada        | -          | 48 GB GDDR6  | 0.86 TB/s | Inference, video, graphics         |
| A10         | Ampere     | -          | 24 GB GDDR6  | 0.6 TB/s  | Small/medium inference             |
| L4          | Ada        | -          | 24 GB GDDR6  | 0.3 TB/s  | Development, small inference       |
| T4          | Turing     | -          | 16 GB GDDR6  | 0.32 TB/s | Legacy, low-cost inference         |

The H100 is the frontier-training and large-inference workhorse; the H200's 141 GB of HBM3e targets long-context inference and LLM training; and the Blackwell B100/B200 parts (192 GB HBM3e, 8 TB/s) are the next generation for training from 2025 onward. The A100 pair remains the fine-tuning and large-model-inference default, with the 40 GB variant suiting smaller models and development. Below that, the L40S serves inference, video, and graphics workloads; the A10 handles small and medium inference; the L4 is a development and small-inference part; and the aging T4 still earns its keep for legacy, low-cost inference.

### AMD GPUs

AMD's MI300X offers 192 GB HBM3 and is competitive with the H100 for inference. Its software ecosystem (ROCm) is less mature than CUDA but improving. The MI250 is the previous generation and is still used in some HPC environments.

### TPUs and specialized accelerators

Google's TPU v5e, v5p, and v6 are custom ASICs for matrix multiplication — competitive for training and inference, but they tie you to Google Cloud. The Groq LPU is specialized for fast inference, delivering very high tokens/sec for some models, though with limited model support. Cerebras and SambaNova build specialized AI hardware for niche use cases.

For most teams, NVIDIA GPUs remain the default — the software ecosystem (CUDA, PyTorch, vLLM, TensorRT-LLM) is mature and well-supported, which is worth more than raw hardware comparisons suggest.

## Sizing for inference

### Memory requirements

An inference GPU must hold four things at once:

1. **Model weights**: `params × bytes_per_param`. For a 7B model in fp16: 14 GB. In INT8: 7 GB. In INT4: 3.5 GB.
2. **KV cache**: `2 × num_layers × hidden_dim × seq_len × batch_size × bytes_per_param`. Grows with sequence length and batch size.
3. **Activations**: relatively small for inference.
4. **Overhead**: ~10% for CUDA context, framework overhead.

Two worked examples anchor the arithmetic. For a 7B model with 4k context, batch size 8, fp16: weights are 14 GB and KV cache is ~4 GB, for a total of ~18 GB — that fits on an A10 (24 GB). For a 70B model with 32k context, batch size 8, fp16: weights are 140 GB and KV cache is ~80 GB, for a total of ~220 GB — that needs 4× A100 80GB or 3× H100 80GB with tensor parallelism. The KV cache term is why long context is expensive even when the model itself fits; see [[PagedAttention]] and [[KV Cache Mechanics]] for how serving engines manage it.

### Throughput versus latency

Throughput-optimal serving uses a large batch size and maximizes GPU utilization: it is the cheapest per token but has higher latency, because the batch must fill before processing. Latency-optimal serving uses batch size 1 and processes immediately: lowest latency but expensive per token, since the GPU is underutilized. For interactive chat, optimize for latency (batch 1-8); for offline batch processing, optimize for throughput (batch 32-256).

### Model parallelism

When a model doesn't fit on one GPU, there are four ways to spread it:

- **Tensor parallelism (TP)**: split each layer's matrices across GPUs. Requires fast GPU-to-GPU interconnect (NVLink). Lowest latency, highest GPU coupling.
- **Pipeline parallelism (PP)**: split layers across GPUs, pipeline execution. Lower bandwidth requirement, higher latency.
- **Expert parallelism (EP)**: for MoE models, distribute experts across GPUs.
- **Data parallelism (DP)**: replicate the model across GPU groups, process different requests in parallel.

For inference, TP is most common. vLLM and TensorRT-LLM support TP seamlessly, so a multi-GPU replica is a configuration flag rather than a engineering project.

## Sizing for training

### Memory requirements

Training memory includes:

1. **Model weights**: same as inference.
2. **Gradients**: same size as weights.
3. **Optimizer state**: Adam needs 2× weights in fp32 (momentum + variance). Total: 4× weights in fp32 = 8× weights in bytes (for fp16 training).
4. **Activations**: large, depends on batch size and sequence length. Gradient checkpointing reduces this at compute cost.

The optimizer term dominates. For a 7B model with Adam, fp16 training, batch size 4, 4k context: weights are 14 GB, gradients 14 GB, optimizer state 56 GB, and activations ~16 GB — a total of ~100 GB, needing 2× A100 80GB. That 8× multiplier on weight bytes is why naive fine-tuning of large models is out of reach for most teams.

### Why LoRA and QLoRA matter for training budgets

This is why **LoRA/QLoRA** is so valuable — it freezes the base weights (no gradients, no optimizer state for them) and trains only small adapter matrices. A 65B model can be QLoRA-fine-tuned on a single 48GB GPU. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] and [[QLoRA]] for the method details.

### Distributed training patterns

When one GPU is not enough, the standard patterns are:

- **Data Parallel (DP)**: each GPU has a full copy, processes different batches. Gradients are all-reduced across GPUs.
- **ZeRO (DeepSpeed)**: shards optimizer state, gradients, and parameters across GPUs. Reduces memory per GPU.
- **FSDP (PyTorch)**: similar to ZeRO, native PyTorch.
- **3D Parallelism (TP + PP + DP)**: for very large models (100B+), combine all three. Complex to set up.

For fine-tuning, FSDP or ZeRO-3 is the standard. For pretraining frontier models, 3D parallelism with Megatron-LM or TorchTitan. [[Distributed Training]] covers these patterns in depth, and [[Mixed Precision Training]] explains the fp16/bf16 arithmetic that the 8× multiplier assumes.

## Deployment models

### Cloud on-demand

Pay per hour (or per second). Most expensive per hour but most flexible. Best for development, bursty workloads, and short-lived experiments. Providers: AWS (P4/P5 instances), GCP (A2/A3 instances), Azure (ND series), Lambda Labs, CoreWeave.

### Reserved and spot capacity

**Reserved** capacity commits you to 1–3 years in exchange for a 30–60% discount — best for steady-state production. **Spot** capacity lets you bid on spare capacity for a 60–90% discount, but instances can be reclaimed with a 2-minute warning — best for fault-tolerant batch workloads such as training with checkpointing.

### Owned hardware

Buying GPUs outright is capital expenditure, not operational. Amortized over 3–4 years it is the cheapest per hour at high utilization, and it suits steady-state production with predictable load and teams that already have datacenter capacity. Total cost of ownership includes power, cooling, networking, datacenter space, and operations staff — the sticker price of the GPU is only part of the bill.

### Managed inference services

Here the provider runs the model and you call an API. Examples: OpenAI, Anthropic, Together, Anyscale, Replicate, Modal, Baseten. There is no GPU management and you pay per token or per hour, which fits teams without ML infrastructure expertise, low-volume workloads, and prototypes. The limitation is less control over model, prompt, and deployment.

### Choosing a deployment model

The decision framework collapses workload profile into deployment choice:

| Workload profile                       | Best deployment                |
|----------------------------------------|--------------------------------|
| Prototype, low volume                  | Managed API (OpenAI, Together) |
| Production, low-medium volume          | Cloud on-demand or reserved    |
| Production, high volume                | Cloud reserved or owned        |
| Training, occasional                   | Cloud spot with checkpointing  |
| Training, continuous                   | Owned or cloud reserved        |
| Latency-sensitive, low volume          | Cloud on-demand, single GPU    |
| Latency-sensitive, high volume         | Owned, multiple GPUs           |

The pattern: volume and latency sensitivity push you toward commitment (reserved or owned), while burstiness and experimentation push you toward flexibility (on-demand or spot).

## Cost optimization levers

Hardware choice sets the floor; several serving techniques push cost down from there.

### Quantization

INT8 (or FP8) gives a 2× memory reduction with minimal quality loss and is supported by vLLM and TensorRT-LLM. INT4 (GPTQ, AWQ) gives a 4× memory reduction with small quality loss — best for cost-sensitive inference. QLoRA combines a 4-bit base with a 16-bit adapter and enables fine-tuning large models on small GPUs. [[Quantization]] covers the techniques.

### Speculative decoding

A small "draft" model proposes tokens; the large model verifies. When the draft is correct, you skip the large model's forward pass. Expect 2–3× throughput on accept-heavy workloads. See [[Speculative Decoding]].

### Caching

**Prefix caching** caches the KV state of common prefixes (system prompts, few-shot examples) and avoids recomputation. **Semantic caching** caches responses for similar queries — higher hit rate but risks returning wrong answers.

### Batching

**Continuous batching** (as in vLLM) processes requests of different lengths together with dynamic batching, for 5–10× throughput vs. naive batching. See [[Continuous Batching]].

### Right-sizing

Match GPU size to model size — don't run a 7B model on an H100; use an A10 or L4. Match GPU count to throughput requirements — don't use 4 GPUs if 2 suffice. Monitor utilization: if GPU utilization is <50%, you're over-provisioned.

## Operational concerns

### GPU drivers and CUDA

Pin driver versions — driver upgrades can break CUDA compatibility. Use Docker images with bundled CUDA to avoid host driver issues (NVIDIA Container Toolkit).

### Monitoring

**GPU utilization** should target >70% for production; low utilization means wasted spend. Track **memory utilization** as actual usage vs. allocation. Watch **temperature**: high temperatures throttle performance and reduce GPU lifespan. **Power draw** feeds capacity planning. Tools: `nvidia-smi`, DCGM exporter (Prometheus), and cloud provider metrics — the dashboarding side is covered in [[Observability Stack]].

### Failure handling

GPUs fail; plan for it. For inference: load balancer + health checks + multiple replicas. For training: checkpoint frequently and resume from the last checkpoint on failure. For spot instances: checkpoint every N steps and use spot replacement controllers (k8s spot handler).

### Networking

For multi-GPU inference, the interconnect hierarchy is NVLink (within a node) >> InfiniBand (across nodes) >> Ethernet. For training, InfiniBand or NVLink is required for 3D parallelism; Ethernet-only training is impractical at scale.

## Common pitfalls

**Overprovisioning for headroom.** "We might need more capacity, so let's get 8 GPUs." Unused GPUs are pure waste — start small and scale based on actual load.

**No quantization.** Running fp16 when INT8 would suffice is 2× cost for negligible quality difference. Always quantize for inference unless you have a specific reason not to.

**No continuous batching.** Processing one request at a time is 5–10× more expensive than necessary. Use vLLM or a similar server.

**Synchronous inference in web handlers.** Calling the LLM synchronously in a FastAPI handler blocks the worker. Use async patterns or offload to a dedicated inference service.

**No checkpointing for training.** Training for days without checkpointing means a failure at hour 47 loses everything. Checkpoint every N minutes.

**Wrong GPU type for workload.** Using an H100 for a 1B model, or a T4 for a 70B model. Match the GPU to the workload.

**Ignoring spot for batch.** Batch workloads (training, evaluation, bulk inference) are perfect for spot instances; paying on-demand for them is a 4–10× cost premium.

## See also

- [[Inference and Production MOC]] — orientation for the whole area
- [[Production AI Stack]] — where this hardware sits in the end-to-end serving stack
- [[Observability Stack]] — GPU metrics, dashboards, and alerting
- [[Vector Storage with pgvector]] — the storage tier sharing the budget
- [[Messaging with Kafka and Celery]] — queue-driven work distribution onto these GPUs
- [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — the serving engines with seamless tensor parallelism
- [[Continuous Batching]], [[PagedAttention]], [[KV Cache Mechanics]] — turning the same GPUs into 5–10× throughput
- [[Quantization]] and [[Speculative Decoding]] — the main cost levers on this hardware
- [[Cost Optimization]] — the economics across the whole stack
- [[Distributed Training]], [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], [[QLoRA]], [[Mixed Precision Training]] — the training-memory side of the sizing math
