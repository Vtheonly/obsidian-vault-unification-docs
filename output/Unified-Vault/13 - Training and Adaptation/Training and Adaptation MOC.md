---
title: Training and Adaptation MOC
type: overview
aliases: [Training and Adaptation Map of Content, Training MOC, Fine-Tuning MOC, "11 — Training MOC", "12 — Fine-Tuning MOC"]
tags: [training, fine-tuning, moc, overview, pretraining, alignment]
sources: ["11 — Training MOC", "12 — Fine-Tuning MOC"]
created_index: 11
---

This map of content is the entry point to the training and adaptation area: the complete path from pretraining a foundation model to adapting a pretrained LLM to your task. It indexes the area's eleven notes, sorts them into five sub-families — pretraining, training data, optimization, distributed training, and fine-tuning — and gives a single reading order that runs from pretraining objectives and scaling laws through the alignment methods that finish the job. Most AI engineers will fine-tune rather than pretrain, but understanding pretraining is essential for understanding the models you fine-tune, so the two halves belong on one map.

> [!info] TL;DR
> How foundation models are pretrained, and how to adapt a pretrained LLM to your task. Most AI engineers will fine-tune, not pretrain — but understanding pretraining is essential for understanding the models you fine-tune. Read the pretraining half first (objectives and scaling laws, distributed training, data pipelines, mixed precision, loss spikes), then the fine-tuning half (LoRA, QLoRA, instruction tuning, DPO, RLHF).

## The big picture

Training a foundation model involves five interlocking concerns:

1. **Data** — what you train on; quality determines model quality ([[Data Pipelines and Deduplication]]).
2. **Objective** — what the model learns to predict: CLM, MLM, span corruption ([[Pretraining Objectives and Scaling Laws]]).
3. **Optimization** — how you update weights ([[Mixed Precision Training]] and [[Loss Spikes and Stability]]; the optimizer and learning-rate schedule math itself is background, covered in [[Optimizers and Learning Rate Schedulers]]).
4. **Distribution** — how you parallelize across GPUs ([[Distributed Training]]).
5. **Alignment** — how you make the model useful and safe (the fine-tuning half: [[Instruction Tuning and Chat Templates]], [[RLHF with PPO]], [[DPO Derivation]]).

Each concern is a deep topic. Production training teams have specialists for each. The sub-families of this area mirror the concerns one to one, so every concern has its own shelf of notes.

## Reading order

The area holds eleven notes: this map plus the ten content notes it indexes. The sequence runs in two halves. The pretraining half covers how a randomly initialized transformer becomes a knowledgeable model — what it learns to predict and at what scale, how the run is spread across GPUs, what it trains on, and the numerical formats and stability practices that keep a months-long run alive. The fine-tuning half covers what happens after pretraining, which builds on pretraining rather than replacing it: the parameter-efficient tooling first ([[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], then [[QLoRA]] on top of it), then the alignment pipeline in execution order — instruction tuning as SFT, then preference optimization with DPO or RLHF.

| # | Note | Sub-family | Purpose |
|---|------|------------|---------|
| 01 | [[Training and Adaptation MOC]] | Orientation | This map: reading order, sub-families, and why the area matters. |
| 02 | [[Pretraining Objectives and Scaling Laws]] | Pretraining | CLM/MLM/span corruption; Chinchilla. |
| 03 | [[Distributed Training]] | Distributed training | DP, TP, PP, ZeRO, FSDP; 3D parallelism. |
| 04 | [[Data Pipelines and Deduplication]] | Training data | Collection, extraction, filtering, dedup. |
| 05 | [[Mixed Precision Training]] | Optimization | FP16, BF16, FP8; master weights. |
| 06 | [[Loss Spikes and Stability]] | Optimization | Spike causes, prevention, recovery. |
| 07 | [[13 - Training and Adaptation/Fine-Tuning/LoRA\|LoRA]] | Fine-tuning (PEFT) | The dominant PEFT method. |
| 08 | [[QLoRA]] | Fine-tuning (PEFT) | 4-bit quantized LoRA; fine-tune on consumer GPUs. |
| 09 | [[Instruction Tuning and Chat Templates]] | Fine-tuning (instruction tuning) | SFT; chat templates. |
| 10 | [[DPO Derivation]] | Fine-tuning (DPO) | The simpler alternative to PPO. |
| 11 | [[RLHF with PPO]] | Fine-tuning (RLHF) | PPO-based alignment; what DPO replaces. |

The order is not arbitrary. The pretraining half follows the life cycle of a run — decide the objective and the scale, parallelize the cluster, prepare the corpus, then keep the numerics healthy until the final checkpoint — and the fine-tuning half opens with the efficiency tooling before walking the alignment pipeline in the order it is applied to a base model.

## Sub-families

The five sub-families carry the five concerns of the big picture; each description says what its notes contribute to the area.

### Pretraining

Pretraining is the self-supervised stage that turns a randomly initialized transformer into a knowledgeable model, and the objective chosen for it determines what the model can do afterwards — causal language modeling for generators, masked language modeling for encoders, span corruption for text-to-text models, with prefix-LM and fill-in-the-middle as the notable variants. The scaling-law half is what makes pretraining plannable rather than a gamble: Kaplan's power laws, Chinchilla's ~20 tokens per parameter, and the modern practice of deliberate overtraining to save inference cost. The note also walks a real run end to end — data mix, tokenizer, architecture recipe, hyperparameters, schedule, checkpointing, and cost.

- [[Pretraining Objectives and Scaling Laws]] — CLM/MLM/span corruption; Chinchilla; the modern training recipe.

### Training data

Pretraining corpora are engineered rather than found: the raw web arrives as noisy HTML littered with boilerplate, near-duplicate pages, and mixed-quality content, and it has to be cleaned systematically before a model can train on it. The note covers the four-stage pipeline — collection, extraction, filtering, and deduplication — with the tooling and the measured evidence behind each stage. Deduplication (MinHash + LSH) is the single highest-ROI processing step, and the standing lesson is that quality matters more than quantity: a smaller, well-curated corpus beats a larger noisy one.

- [[Data Pipelines and Deduplication]] — collection, extraction, filtering, dedup; quality determines model quality.

### Optimization

How weights are actually updated at scale, in two paired notes. Mixed precision runs the computation in FP16, BF16, or FP8 while master weights stay in FP32 — cutting memory by 2-4× and multiplying throughput through Tensor Cores, with BF16 the production default and FP8 the frontier for the largest runs. Loss spikes are the paired failure mode: the five families of causes (bad data batches, numerical instability, optimizer-state issues, learning-rate issues, and genuine model instability at scale) and the prevention-and-recovery toolkit — gradient clipping, loss scaling, selective skip-on-spike, warmup, and checkpoint rollback.

- [[Mixed Precision Training]] — FP16, BF16, FP8; master weights.
- [[Loss Spikes and Stability]] — spike causes, prevention, recovery.

### Distributed training

A 70B model with its AdamW optimizer state and activations needs roughly 800 GB — far past any single GPU — so large-model training is inseparable from parallelism. The note builds the four strategies — data parallelism replicates the model, tensor parallelism splits weight matrices, pipeline parallelism splits layers, and ZeRO/FSDP shards optimizer state, gradients, and parameters — and shows how they compose into 3D parallelism: tensor parallel within a node, pipeline parallel across nodes, data parallel across the cluster. That composition is what enabled 100B+ model training.

- [[Distributed Training]] — DP, TP, PP, ZeRO, FSDP; 3D parallelism.

### Fine-tuning

Five notes, carrying the alignment concern — SFT, RLHF, RLAIF — together with the efficiency tooling that makes adaptation affordable. The parameter-efficient family (PEFT) comes first: LoRA freezes the pretrained weights and learns low-rank delta matrices alongside them, cutting trainable parameters by 100×–1000× and producing small adapter files that swap per task and merge with zero inference overhead; QLoRA quantizes the frozen base to 4-bit so a 65B model fine-tunes on a single 48 GB GPU. Instruction tuning is the bridge between pretraining and aligned chat models: supervised fine-tuning on instruction-response pairs, formatted by each model's chat template, with loss computed on the response tokens only. Preference optimization closes the pipeline: RLHF with PPO is the original ChatGPT-era recipe — reward model, PPO optimization, and a KL penalty that keeps the policy near the SFT model — and DPO is the simpler alternative to PPO, a closed-form loss derived directly from the KL-constrained RLHF objective. Knowledge distillation, the classic fourth adaptation method, is the one without a dedicated note here.

- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — the dominant PEFT method.
- [[QLoRA]] — 4-bit quantized LoRA; fine-tune on consumer GPUs.
- [[Instruction Tuning and Chat Templates]] — SFT; chat templates.
- [[DPO Derivation]] — the simpler alternative to PPO.
- [[RLHF with PPO]] — PPO-based alignment; what DPO replaces.

## The standard fine-tuning pipeline

The fine-tuning half is not five independent techniques but one standard pipeline:

```mermaid
graph LR
  Base[Base Model] --> SFT[SFT 03]
  SFT --> PrefOpt[Preference Optimization: DPO 04 or RLHF 05]
  PrefOpt --> Merge[Merge LoRA]
  Merge --> Quantize[Quantize for Inference]
  Quantize --> Serve[Serve with vLLM]
```

Read it left to right: start from a base model, supervised fine-tune it ([[Instruction Tuning and Chat Templates]]), preference-optimize it with [[DPO Derivation]] or [[RLHF with PPO]], merge the LoRA adapters back into the weights ([[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]), quantize the result for inference ([[Quantization]]), and serve it ([[14 - Inference and Production/Inference/vLLM|vLLM]]). The numbers inside the node labels count positions within the fine-tuning half of the reading order — SFT is the third note of that sequence, DPO the fourth, RLHF the fifth. Every fine-tuning note in the area is one stage or one tool of this diagram.

## Why this area matters

Even if you never pretrain a model from scratch, the pretraining half earns its keep in four ways:

- **Fine-tuning** uses the same optimization, distribution, and stability techniques at smaller scale.
- **Choosing a model** requires understanding how it was trained — data, objective, scale.
- **Debugging fine-tuning** failures often requires understanding pretraining stability.
- **Estimating training cost** for a custom model requires understanding distributed training and mixed precision.

The fine-tuning half is the part most engineers touch directly: instruction tuning and preference optimization are how a base model becomes a product, and the LoRA family's efficiency is what makes that affordable on realistic hardware.

## Cross-domain connections

Training sits downstream of architecture and upstream of inference, and the map connects in every direction. The optimizer used in most pretraining is Adam, and the schedule used in pretraining is its learning-rate schedule; both mechanics are treated in [[Optimizers and Learning Rate Schedulers]]. The models being trained are the Transformer architectures mapped in [[Attention and Transformers MOC]]. The models this recipe produces, with the capabilities and failure modes that matter when you adapt one, are indexed in [[Large Language Models MOC]]. What comes after training is [[Inference and Production MOC]]: running the fine-tuned model, from quantization and serving to monitoring and cost.

## Future directions

A few recognized topics in training and adaptation have no dedicated notes here yet, and are worth knowing by name even so. On the alignment side, RLAIF and Constitutional AI extend preference optimization beyond human feedback. On the pretraining side, curriculum learning and data mixing, synthetic data generation, tokenizer training, and evaluation during pretraining each deserve their own treatment. On the adaptation side, knowledge distillation — compressing a large teacher into a small student — rounds out the classic toolkit that this area's fine-tuning family does not yet carry.

## See also

The area's notes, in reading order:

- [[Pretraining Objectives and Scaling Laws]] — CLM/MLM/span corruption; Chinchilla.
- [[Distributed Training]] — DP, TP, PP, ZeRO, FSDP; 3D parallelism.
- [[Data Pipelines and Deduplication]] — collection, extraction, filtering, dedup.
- [[Mixed Precision Training]] — FP16, BF16, FP8; master weights.
- [[Loss Spikes and Stability]] — spike causes, prevention, recovery.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — the dominant PEFT method.
- [[QLoRA]] — 4-bit quantized LoRA; fine-tune on consumer GPUs.
- [[Instruction Tuning and Chat Templates]] — SFT; chat templates.
- [[DPO Derivation]] — the simpler alternative to PPO.
- [[RLHF with PPO]] — PPO-based alignment; what DPO replaces.

The neighbouring area maps:

- [[Large Language Models MOC]] — the models this area trains and adapts.
- [[Inference and Production MOC]] — what comes after training: running the fine-tuned model.
- [[Attention and Transformers MOC]] — the architectures being trained.
- [[Optimizers and Learning Rate Schedulers]] — the Adam optimizer and the learning-rate schedules behind most pretraining runs.

The pretraining half produces the base model, the fine-tuning half turns it into a product, and [[Inference and Production MOC]] is where it goes to work.
