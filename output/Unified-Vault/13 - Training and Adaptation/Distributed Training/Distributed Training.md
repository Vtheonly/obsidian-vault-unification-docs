---
title: Distributed Training
type: concept
aliases: [Distributed Training, ZeRO, FSDP, Zero Redundancy Optimizer, Fully Sharded Data Parallel, "02 - Distributed Training (DP, TP, PP, ZeRO, FSDP)"]
tags: [training, distributed, zero, fsdp, tensor-parallel, pipeline-parallel, data-parallel, llm-training]
sources: ["02 - Distributed Training"]
created_index: 1
---

Training a 70B+ model needs far more memory than any single GPU has, so large-model training is inseparable from spreading the model, its optimizer state, and the computation itself across many devices. This note explains the four parallelism strategies that make that possible — data parallelism, tensor parallelism, pipeline parallelism, and ZeRO/FSDP sharding — and how they combine into the 3D parallelism behind modern LLM training. It also works through the memory arithmetic that forces the issue, a worked FSDP example, production guidance, and the pitfalls that bite most often — read it alongside [[Training and Adaptation MOC]] for the surrounding area.

> [!info] TL;DR
> Training a 70B+ model requires distributed training across many GPUs. The four main parallelism strategies — data parallel, tensor parallel, pipeline parallel, and ZeRO/FSDP — can be combined. Modern LLM training uses 3D parallelism (DP + TP + PP) plus ZeRO-style sharding.

## Why distributed training?

A 70B model in fp16: 140 GB of weights. Optimizer state (AdamW): 4x = 560 GB. Activations: 100+ GB. Total: ~800 GB per replica — way past an 80GB H100.

That arithmetic is the whole motivation: a single replica of the model, its optimizer, and its activations cannot live on one card, let alone train there. So you need to **shard the model across multiple GPUs**, and you need to **parallelize the computation** across them. The four strategies below are the standard answers, and they compose.

## The four parallelism strategies

### Data parallelism (DP)

Each GPU has a **full copy** of the model. Each processes a different batch. Gradients are averaged across GPUs (all-reduce) before the optimizer step:

```text
GPU 0: model + batch 0 → grads → all-reduce → update
GPU 1: model + batch 1 → grads → all-reduce → update
GPU 2: model + batch 2 → grads → all-reduce → update
GPU 3: model + batch 3 → grads → all-reduce → update
```

DP is simple, and it works for any model that fits on one GPU. The limit is memory: each GPU needs full model + optimizer + activations, so it doesn't help if the model is too big for one GPU. Data parallelism multiplies throughput without shrinking the per-GPU footprint.

### Tensor parallelism (TP)

Tensor parallelism splits individual weight matrices across GPUs. For $\mathbf{y} = \mathbf{W}\mathbf{x}$ with $\mathbf{W} \in \mathbb{R}^{n \times m}$, there are two ways to make the split:

- **Column parallel**: each GPU holds $\mathbf{W}_i \in \mathbb{R}^{n \times m/k}$, computes $\mathbf{y}_i = \mathbf{W}_i \mathbf{x}$. Concatenate the $\mathbf{y}_i$s.
- **Row parallel**: each GPU holds $\mathbf{W}_i \in \mathbb{R}^{n/k \times m}$, computes a partial sum. All-reduce to combine.

For a Transformer block, the two pair up: attention Q/K/V/O projection split column-parallel, then FFN split row-parallel (or vice versa), with one all-reduce per block. The trade is memory against communication. Memory: weights sharded across $k$ GPUs. Communication: all-reduce per layer (high bandwidth required) — which is why TP is typically combined with NVLink-connected GPUs (within a node).

### Pipeline parallelism (PP)

Pipeline parallelism splits the layers across GPUs. GPU 0 has layers 1–10, GPU 1 has 11–20, etc. Activations flow forward through the pipeline; gradients flow backward:

```text
GPU 0: layers 1-10 → activations → GPU 1
GPU 1: layers 11-20 → activations → GPU 2
GPU 2: layers 21-30 → activations → GPU 3
GPU 3: layers 31-40 → loss → backward
```

Memory: layers sharded across GPUs. The catch is the **bubble problem**: while GPU 1 processes batch 1, GPU 0 is idle (or processing batch 2) — the "pipeline bubble" is wasted compute. **Micro-batching** is the standard remedy: split each batch into smaller micro-batches and pipeline them. Reduces the bubble.

### ZeRO (Zero Redundancy Optimizer)

DP replicates the full model + optimizer + gradients on every GPU. ZeRO shards these:

- **ZeRO-1**: shard optimizer state (the biggest chunk — Adam's m and v are 8x params in fp32).
- **ZeRO-2**: shard optimizer state + gradients.
- **ZeRO-3**: shard optimizer state + gradients + parameters (full sharding).

ZeRO-3 is essentially what FSDP (Fully Sharded Data Parallel) does in PyTorch. With ZeRO-3 / FSDP, each GPU only holds $1/k$ of the model. Before each layer's forward, the shards are gathered (all-gather); after backward, they're reduced (reduce-scatter).

### FSDP (PyTorch's ZeRO-3)

FSDP is PyTorch's native implementation of ZeRO-3. Standard for modern LLM training in PyTorch — the worked example below shows what wrapping a model with it looks like in practice.

## Combining: 3D parallelism

For very large models (70B+), combine all three, matching each strategy to the communication fabric it can tolerate:

- **TP within a node** (8 GPUs connected by NVLink, fast all-reduce).
- **PP across nodes** (slower communication, but pipeline can hide it).
- **DP / ZeRO across the cluster** (scale to many nodes).

Example for a 70B model on 64 H100 GPUs (8 nodes × 8 GPUs):

- TP=8 (within each node).
- PP=4 (across 4 pipeline stages = 4 nodes per stage... actually 8 nodes total so 2 stages of 4 nodes each, but let's say PP=4 = 4 stages of 2 nodes each).
- DP=2 (data parallel replicas).

Plus ZeRO-1 for optimizer state sharding. The TP × PP × DP product accounts for all 64 GPUs, and ZeRO-1 trims the optimizer-state footprint on top.

## Worked example (FSDP)

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision

model = AutoModelForCausalLM.from_pretrained(...)
model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # ZeRO-3
    mixed_precision=MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
    ),
    auto_wrap_policy=...,
)
```

`ShardingStrategy.FULL_SHARD` selects the ZeRO-3 full-sharding mode, and the `MixedPrecision` policy keeps parameters and reductions in bf16 — the same fp16/bf16 trade-offs covered in [[Mixed Precision Training]]. In practice, use a framework like Megatron-LM, DeepSpeed, or TorchTitan that handles the 3D parallelism setup. Building a distributed training pipeline hands-on is the natural project for making FSDP's mechanics concrete.

## Why this matters for AI

If you train large models, **distributed training is mandatory**. Understanding the tradeoffs is essential. The flip side is knowing when you can skip it: for fine-tuning with [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], you usually don't need distributed training — LoRA params are small enough for a single GPU. For inference, **tensor parallelism** is the most common ([[14 - Inference and Production/Inference/vLLM|vLLM]] supports it natively). Zooming out: the shift from DP-only to 3D parallelism is what enabled 100B+ model training.

## Production implications

The decision tree is short:

- **Fine-tuning (LoRA)**: usually single-GPU. No distributed setup needed.
- **Full fine-tuning of 7B+**: use FSDP across multiple GPUs.
- **Continued pretraining**: use a framework (DeepSpeed, Megatron, TorchTitan). Don't roll your own.

Underneath all three branches sits the same physical constraint: **communication is the bottleneck** for distributed training. NVLink within a node (300+ GB/s) >> InfiniBand between nodes (50-100 GB/s) >> Ethernet (10-25 GB/s). Plan cluster topology accordingly — the 3D placement rule above (TP in-node, PP across nodes) is a direct consequence of this hierarchy, and the infrastructure side of these decisions is what [[GPU Infrastructure and Sizing]] covers.

## Common pitfalls

> [!warning] The five pitfalls that bite most often
> - **Wrong TP size** — too high (e.g., TP=8 across nodes) kills performance due to slow inter-node all-reduce. TP should be within a node.
> - **Pipeline bubble too large** — too few micro-batches. Increase micro-batch count.
> - **Forgetting activation checkpointing** — long-context training OOMs without it.
> - **Mixed precision issues** — fp16 needs loss scaling; bf16 doesn't. Don't mix.
> - **Wrong learning rate for distributed** — when you scale batch size, scale LR too (linear scaling rule, see [[Optimizers and Learning Rate Schedulers]]).

Each of these traces back to a mechanism described above. The TP pitfall is the communication hierarchy in disguise: an all-reduce that is fast over NVLink becomes a performance killer across nodes, which is why TP should stay within a node. The bubble pitfall is pipeline arithmetic — more micro-batches in flight means less idle time per stage, at the price of more memory for activations. The mixed-precision pitfall is the fp16/bf16 loss-scaling asymmetry; the full story lives in [[Mixed Precision Training]]. And the learning-rate pitfall is the linear scaling rule in shorthand — when you scale batch size, scale LR too; the full rule, including when it stops working, is in the interview answers below.

## Further reading

Three papers anchor this territory, together with the PyTorch FSDP documentation:

- Rajbhandari et al. (2020), *ZeRO: Memory Optimizations Toward Training Trillion Parameter Models*.
- Shoeybi et al. (2019), *Megatron-LM*.
- Narayanan et al. (2021), *Efficient Large-Scale Language Model Training on GPU Clusters* (3D parallelism).
- PyTorch FSDP docs: https://pytorch.org/docs/stable/fsdp.html

## Interview questions

These are the distinctions interviewers actually probe, and they double as a self-test for this note.

**Q: What's the difference between DP, TP, PP, and ZeRO/FSDP?**
A: DP replicates the full model on each GPU, processing different batches. TP splits individual weight matrices across GPUs (column-parallel or row-parallel). PP splits layers across GPUs (pipeline stages). ZeRO/FSDP shards optimizer state, gradients, and parameters across GPUs (like DP but without replication). Modern training combines all four (3D parallelism): TP within a node, PP across nodes, DP/ZeRO across the cluster.

**Q: When would you use FSDP vs DeepSpeed ZeRO-3?**
A: FSDP is PyTorch-native and simpler. DeepSpeed offers more features (CPU offload, NVMe offload, custom configs). For most new projects, FSDP is sufficient. Choose DeepSpeed when you need CPU/NVMe offload or specific ZeRO configurations.

**Q: What is the pipeline bubble and how do you reduce it?**
A: The pipeline bubble is idle time when earlier pipeline stages wait for later stages to finish. Reduce it with micro-batching: split each batch into smaller micro-batches and pipeline them, so GPU 0 can start on micro-batch 2 while GPU 1 processes micro-batch 1. More micro-batches = smaller bubble but more memory for activations.

**Q: How does tensor parallelism work for a Transformer block?**
A: QKV projection is column-parallel (each GPU computes a subset of heads). The attention output is row-parallel (each GPU computes a partial sum). One all-reduce per block combines the partial sums. This requires NVLink-connected GPUs (within a node) for low-latency communication.

**Q: How much memory does ZeRO-3/FSDP save?**
A: ZeRO-3 shards parameters + gradients + optimizer state across $k$ GPUs. Each GPU holds $1/k$ of the total. For a 70B model with AdamW: ~280 GB total → ~35 GB per GPU on 8 GPUs. Without ZeRO-3, you'd need 280 GB on each GPU.

**Q: What's the linear scaling rule for distributed training?**
A: When you multiply batch size by $k$, multiply LR by $k$ (with proportional warmup). Works for moderate changes (2-8x). For very large batches (>8x), use sqrt scaling or LARS/LAMB. The rule assumes gradient noise variance scales as $1/B$.

## See also

Related notes across training, fine-tuning, and serving:

- [[Training and Adaptation MOC]] — orientation for the training and adaptation area
- [[Pretraining Objectives and Scaling Laws]] — what's being trained, and compute-optimal training at scale
- [[Mixed Precision Training]] — distributed + mixed precision together, including the loss-scaling story
- [[Loss Spikes and Stability]] — training stability when batch sizes and learning rates change
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — fine-tuning that usually fits on a single GPU
- [[QLoRA]] — the quantized variant of LoRA, with an even smaller footprint
- [[GPU Infrastructure and Sizing]] — the NVLink/InfiniBand/Ethernet hierarchy and cluster topology planning
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — tensor parallelism at inference; distributed inference uses similar techniques
- Building a distributed training pipeline (a capstone project) — hands-on FSDP implementation with checkpointing
- [[Inference and Production MOC]]
