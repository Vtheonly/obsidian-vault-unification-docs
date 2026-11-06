---
title: LoRA
type: concept
aliases: [LoRA, Low-Rank Adaptation, PEFT, Adapter Tuning]
tags: [fine-tuning, lora, peft, low-rank, adapter]
sources: [LoRA (Low-Rank Adaptation)]
created_index: 4
---

LoRA (Low-Rank Adaptation) freezes the pretrained weights of a large model and learns small low-rank delta matrices alongside them. This cuts trainable parameters by 100×–1000×, makes fine-tuning practical on consumer GPUs, and produces tiny adapter files that can be swapped per task and merged with zero inference overhead — which is why LoRA is the dominant parameter-efficient fine-tuning (PEFT) method. This note covers the idea and its math, parameter and memory accounting, initialization and scaling, where to apply adapters, rank choice, a full implementation, merging, the variant family, production patterns, and common pitfalls; see [[Training and Adaptation MOC]] for the surrounding area.

> [!info] TL;DR
> LoRA freezes the pretrained weights and learns **low-rank delta matrices** alongside them. This reduces trainable parameters by 100×–1000×, enables fine-tuning on consumer GPUs, and produces small "adapter" files that can be swapped per task. The dominant parameter-efficient fine-tuning (PEFT) method. This note covers the idea, math, parameter accounting, initialization, scaling, where to apply, rank choice, full implementation, merging, variants, production patterns, and common pitfalls.

## The idea

A full fine-tune updates every parameter: $\mathbf{W}' = \mathbf{W} + \Delta \mathbf{W}$. Hu et al. (2021) observed that the **update $\Delta \mathbf{W}$ has low intrinsic rank** during fine-tuning — you don't need a full-rank update to adapt the model. This empirical observation is the key insight: fine-tuning doesn't move weights very far in the parameter space, and the movement is concentrated in a low-dimensional subspace.

LoRA factorizes $\Delta \mathbf{W}$ as a product of two small matrices:

$$
\Delta \mathbf{W} = \mathbf{B} \mathbf{A}
$$

where $\mathbf{A} \in \mathbb{R}^{r \times d}$, $\mathbf{B} \in \mathbb{R}^{d \times r}$, and $r \ll d$. Only $\mathbf{A}$ and $\mathbf{B}$ are trained; $\mathbf{W}$ is frozen. The machinery behind the factorization is nothing more than matrix multiplication — two small matrix products instead of one large one.

The forward pass becomes:

$$
\mathbf{y} = (\mathbf{W} + \mathbf{B} \mathbf{A}) \mathbf{x} = \mathbf{W} \mathbf{x} + \mathbf{B} \mathbf{A} \mathbf{x}
$$

The two terms can be computed in parallel: the base model does $\mathbf{W} \mathbf{x}$, the adapter does $\mathbf{B} \mathbf{A} \mathbf{x}$, and the results are summed.

### Why low-rank works

The empirical observation is that fine-tuning updates have low intrinsic rank — but why? Several theories offer an answer. First, pretrained models already know most of what they need, and fine-tuning just "steers" them slightly; the steering direction is low-dimensional. Second, tasks are simpler than pretraining: pretraining learns language while fine-tuning learns a specific task, so the task-specific adjustment is small. Third, an information bottleneck: the gradient signal during fine-tuning is concentrated in a few directions, and most of the parameter space doesn't move much.

Whatever the cause, the empirical result is robust: rank 16-64 captures most of the benefit of full fine-tuning, across tasks and model sizes.

## Parameter count

For a layer of size $d \times d$, a full fine-tune trains $d^2$ parameters while LoRA at rank $r$ trains $2 d r$ parameters (for $\mathbf{A}$ and $\mathbf{B}$). The ratio is $\frac{2dr}{d^2} = \frac{2r}{d}$; for $r = 8$ and $d = 4096$, this is $16/4096 \approx 0.4\%$.

### Concrete numbers (Llama 3 8B)

Llama 3 8B has 32 layers, hidden size 4096, and per layer 7 linear layers (Q, K, V, O, gate, up, down) — but with GQA, K and V are smaller — for a total of ~8.03B parameters. With LoRA rank 16 on all linear layers, each layer carries ~7 × 2 × 4096 × 16 ≈ 917K parameters and all 32 layers together ~29M, for a ratio of 29M / 8B ≈ 0.36%. A 7B model with LoRA rank 16 on all attention projections typically lands at ~20–50M trainable parameters versus 7B for full fine-tuning — a 100–300× reduction.

### Memory savings

The memory savings are even larger than the parameter savings suggest. A full fine-tune needs the parameters themselves (4 bytes × 7B = 28 GB) plus Adam optimizer state (8 bytes × 7B = 56 GB) plus gradients (4 bytes × 7B = 28 GB), for **112 GB** in total. LoRA at rank 16 needs the base weights (28 GB, frozen, no optimizer state) plus adapters (4 bytes × 29M = 116 MB) plus Adam state for the adapters (8 bytes × 29M = 232 MB) plus gradients for the adapters (4 bytes × 29M = 116 MB), which comes to **~28.5 GB**.

So LoRA fits a 7B model on a single 32 GB GPU (A100 40GB, A100 80GB, H100 80GB), where full fine-tuning needs 8× A100 80GB.

## Initialization

$\mathbf{A}$ is initialized with a random Gaussian (Kaiming uniform), and $\mathbf{B}$ is initialized with zeros. So $\mathbf{B} \mathbf{A} = 0$ at the start of training — the model behaves exactly like the pretrained model, and LoRA then "grows" the delta from zero. This is essential for stable training: the model starts from the pretrained state and gradually adapts. Without this initialization (for example, both random), the model would start in a random state and might not recover the pretrained behavior.

## Scaling factor

LoRA scales the delta by $\alpha / r$:

$$
\mathbf{y} = \mathbf{W} \mathbf{x} + \frac{\alpha}{r} \mathbf{B} \mathbf{A} \mathbf{x}
$$

$\alpha$ is a hyperparameter (typically $2r$ or matched to $r$). The scaling lets you change $r$ without re-tuning the learning rate — $\alpha / r$ keeps the effective update magnitude roughly constant.

### Why α/r?

The product $\mathbf{B} \mathbf{A}$ has magnitude that scales with $r$ (more parameters → larger potential updates). Dividing by $r$ normalizes this, so the effective update magnitude is independent of $r$ — which lets you sweep $r$ without re-tuning the learning rate. Common choices: $\alpha = r$ gives a scaling of 1.0 and is the simplest option; $\alpha = 2r$ gives a scaling of 2.0 with slightly stronger updates; and a fixed $\alpha = 16$ lets you change $r$ without changing $\alpha$, which is common in practice.

## Where to apply LoRA

In the original paper, LoRA was applied only to attention projections ($\mathbf{W}_Q, \mathbf{W}_V$). Empirically, applying LoRA to **all linear layers** (Q, K, V, O, FFN up, FFN down) gives better quality at the same parameter count; applying LoRA only to attention is cheaper but lower quality; and applying LoRA only to FFN misses the attention adjustments. Modern practice is to apply LoRA to all linear layers (sometimes called "LoRA all-linear"), which the HuggingFace PEFT library supports via `target_modules="all-linear"`.

### Why all linear layers?

Attention (Q, K, V, O) controls information routing — LoRA there adapts which tokens attend to which. The FFN (gate, up, down) controls feature transformation — LoRA there adapts what features are extracted. For most tasks both need adjustment, and skipping either limits the adapter's capacity.

### What about embeddings?

LoRA can also be applied to embedding layers (token embeddings, output projection). This is less common but useful for vocabulary adaptation, for example adding new tokens for a domain. For most use cases, freeze embeddings and apply LoRA only to attention and FFN.

## Rank choice

The rank trades capacity against parameter count and overfitting risk:

| Rank $r$ | Trainable params (7B, all-linear) | Use case                              |
|----------|-----------------------------------|---------------------------------------|
| 4–8      | ~10–20M                           | Small adaptations (style, tone)       |
| 16–32    | ~30–60M                           | Standard fine-tuning                  |
| 64–128   | ~100–250M                         | Large domain shifts                   |
| 256+     | ~500M+                            | Approaching full FT quality           |

Higher rank means more capacity but also more parameters and more overfitting risk; for most tasks, $r = 16$ or $r = 32$ is a good default.

### How to choose

Start with $r = 16$; if quality is insufficient, try $r = 32$, then $r = 64$. For style or tone adaptation (small changes), $r = 8$ is often enough. For domain shifts (e.g., general → medical), use $r = 64$ or higher. For new capabilities (e.g., learning to use new tools), $r = 128$+ may be needed. If $r = 256$ is needed, consider full fine-tuning — the PEFT benefit is diminishing.

### Empirical findings

Studies (and the original LoRA paper) show that $r = 8$ captures ~90% of full FT quality on many tasks, $r = 32$ captures ~95%, and $r = 128$ captures ~98-99%, with diminishing returns beyond $r = 128$. This varies by task: hard tasks (large domain shifts) need higher rank.

## Implementation in PyTorch

### From scratch

The core of LoRA is small enough to implement directly on top of a frozen linear layer:

```python
import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    def __init__(self, base_linear: nn.Linear, r=8, alpha=16, dropout=0.0):
        super().__init__()
        self.base = base_linear  # frozen
        for p in self.base.parameters():
            p.requires_grad = False

        d_in = base_linear.in_features
        d_out = base_linear.out_features
        self.alpha = alpha
        self.scaling = alpha / r
        self.r = r

        # A: (r, d_in), B: (d_out, r)
        self.lora_A = nn.Parameter(torch.zeros(r, d_in))
        self.lora_B = nn.Parameter(torch.zeros(d_out, r))
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        # B stays zero (so BA = 0 at init)

        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x):
        # base(x) + scaling * B(A(dropout(x)))
        base_out = self.base(x)
        lora_out = self.dropout(x) @ self.lora_A.T @ self.lora_B.T
        return base_out + self.scaling * lora_out

    def merge(self):
        """Merge LoRA into base weights for inference."""
        with torch.no_grad():
            delta = self.scaling * (self.lora_B @ self.lora_A)
            self.base.weight.add_(delta)
            self.lora_A = None
            self.lora_B = None
```

### Using HuggingFace PEFT

In practice, use HuggingFace's `peft` library:

```python
from peft import LoraConfig, get_peft_model, TaskType

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(base_model, config)

# Print trainable parameters
model.print_trainable_parameters()
# Output: trainable params: 29,491,712 || all params: 8,030,269,440 || trainable%: 0.367%
```

### Training loop

The training loop is the same as full fine-tuning, but only LoRA parameters are trainable:

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=1e-4,  # higher than full FT (1e-5)
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
    bf16=True,  # mixed precision
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)
trainer.train()

# Save adapter (small file, ~50 MB for rank 16)
model.save_pretrained("./lora-output")
```

### Inference with LoRA

```python
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")

# Load adapter
model = PeftModel.from_pretrained(base_model, "./lora-output")

# Option 1: keep adapter separate (swap-able)
output = model.generate(...)

# Option 2: merge adapter into base (faster, no swap)
model = model.merge_and_unload()
output = model.generate(...)
```

## Merging back

For inference, you can either **keep LoRA separate**, running $\mathbf{W} \mathbf{x} + \mathbf{B} \mathbf{A} \mathbf{x}$ with a slight overhead from the extra matmul but with adapters that remain swap-able at runtime, or **merge** it back into $\mathbf{W}$ as $\mathbf{W}' = \mathbf{W} + \frac{\alpha}{r} \mathbf{B} \mathbf{A}$, which has the same forward pass as a full fine-tuned model with **zero inference overhead**.

Merging gives the same quality as separate LoRA with no inference cost. This is one of LoRA's biggest advantages over other PEFT methods (adapters, prefix tuning), which always have inference overhead.

```python
# Merge for deployment
model = model.merge_and_unload()
model.save_pretrained("./merged-model")
```

### When to merge vs. keep separate

Merge for single-task deployment, maximum inference speed, and when there is no need to swap adapters. Keep adapters separate for multi-tenant serving with many adapters, A/B testing, and dynamic adapter selection. [[14 - Inference and Production/Inference/vLLM|vLLM]], SGLang, and other serving engines support both modes, and multi-LoRA serving — keeping many adapters in memory and swapping per request — is increasingly common for multi-tenant deployments.

## Why this matters for AI

LoRA democratized LLM fine-tuning: you can fine-tune a 7B model on a single 24 GB GPU (vs 8× H100 for full fine-tuning). LoRA adapters are tiny (10–500 MB), so you can store many per task and swap them at inference. LoRA is the basis for most production fine-tuning today — custom LLM services (chatbots, coding assistants, RAG) typically use LoRA adapters on top of an open base model. The low-rank observation is **deeply true**: it suggests that fine-tuning is mostly small, low-dimensional adjustments rather than full re-learning. Multi-LoRA serving enables cost-effective personalization as well — one base model plus many small adapters, each serving a different user or task.

## Production implications

**For most fine-tuning tasks, start with LoRA.** Move to full FT only if LoRA quality is insufficient (rare).

**Use merged weights for inference.** Same quality, no overhead — unless you need multi-LoRA serving.

**Multi-tenant serving** loads multiple LoRA adapters and swaps them per request; vLLM, SGLang, and others support this, which enables per-user or per-task customization at low cost.

**Storage** means keeping the base model plus many adapter files: a 7B base + 100 LoRAs is ~14 GB + 100 × 50 MB = 19 GB total, vs 100 full fine-tuned models = 1.4 TB.

**Versioning** should treat adapters separately from the base model. An adapter is compatible only with the base it was fine-tuned on, so store the base model hash with each adapter.

**Learning rate** for LoRA is typically higher than for full FT (1e-4 to 1e-3 vs 1e-5 to 1e-4): the small parameter count means each parameter needs to move more.

**Batch size** benefits from LoRA's small memory footprint, which allows larger batch sizes and can speed up training significantly.

**Multi-GPU** training is unnecessary for most LoRA runs — it trains on a single GPU — but for large datasets multi-GPU (DDP) speeds things up. FSDP is overkill for LoRA since the trainable params are small.

## Common pitfalls

**Too low rank** underfits; the model can't learn the task. Try $r = 16$ minimum.

**Too high rank** overfits and loses the parameter-efficiency benefit. If $r = 256$ is needed, consider full FT.

**Forgetting to apply to FFN** limits capacity — FFN has most of the parameters. Always include FFN modules.

**Wrong learning rate** — LoRA typically needs a higher LR than full FT (1e-4 to 1e-3 vs 1e-5 to 1e-4). Too low → slow convergence; too high → instability.

**Forgetting to merge for inference** wastes compute by keeping LoRA separate. Merge unless you need multi-LoRA.

**Mixing adapters across base models** breaks silently — adapters are tied to a specific base model, so don't mix them. The adapter's `base_model_name_or_path` field documents this.

**Forgetting to save the tokenizer** — LoRA adapters don't include the tokenizer. Save it alongside the adapter.

**Wrong target modules** — different models name their linear layers differently. Check the model's architecture before specifying `target_modules`.

**Forgetting dropout** — LoRA dropout (0.05-0.1) helps regularization. Don't set it to 0 unless you're sure.

**Not using bf16** — train in bf16 to halve memory; see [[Mixed Precision Training]]. The base model can stay in fp32; only LoRA params need gradients.

**Forgetting to set `requires_grad=False` on the base** means you'll train the full model, defeating the purpose. PEFT handles this automatically.

**Not validating before merging** — always evaluate the unmerged model first. If quality is bad, merging won't fix it.

## Variants

### QLoRA

LoRA on top of a 4-bit quantized base. The base model is loaded in 4-bit NF4 quantization; LoRA adapters are trained in bf16 on top. This enables fine-tuning a 70B model on a single 48 GB GPU. See [[QLoRA]] for details.

### DoRA (Weight-Decomposed Low-Rank Adaptation)

Decomposes weights into magnitude and direction, applies LoRA to direction only. Slightly better quality than vanilla LoRA at the same parameter count.

$$
\mathbf{W}' = \frac{\mathbf{W} + \mathbf{B}\mathbf{A}}{\|\mathbf{W} + \mathbf{B}\mathbf{A}\|} \cdot \text{magnitude}
$$

### ReLoRA

Periodically resets $\mathbf{A}, \mathbf{B}$ and merges into $\mathbf{W}$. This allows LoRA to escape its low-rank constraint over training — each "reset" starts a new low-rank adaptation from the current merged weights, accumulating higher-rank updates over time.

### PiSSA

Initializes $\mathbf{A}, \mathbf{B}$ from the SVD of $\mathbf{W}$ — the matrix decomposition that inspires PiSSA — rather than randomly. The adapter starts as the principal components of the original weight, leading to faster convergence and slightly better final quality.

### LoRA+

Uses different learning rates for $\mathbf{A}$ and $\mathbf{B}$ ($\mathbf{B}$ gets a higher LR). Theoretically motivated by the observation that $\mathbf{A}$ and $\mathbf{B}$ play asymmetric roles.

### MoLoRA / LoRAMoE

Multiple LoRA adapters as experts with routing. Each token is routed to the most relevant LoRA expert, enabling multi-task adaptation in a single adapter set.

### GaLore

Gradient Low-Rank Projection: applies low-rank to the gradient rather than the weights. Different mechanism, similar memory savings.

## Comparison to other PEFT methods

| Method          | Trainable Params | Inference Overhead | Quality | Maturity |
|-----------------|------------------|---------------------|---------|----------|
| LoRA            | 0.1-1%           | Zero (after merge)  | High    | Mature   |
| QLoRA           | 0.1-1%           | Zero (after merge)  | High    | Mature   |
| Adapters        | 1-5%             | Small               | Medium  | Mature   |
| Prefix Tuning   | <0.1%            | Small               | Medium  | Mature   |
| Prompt Tuning   | <0.1%            | Zero                | Low     | Mature   |
| DoRA            | 0.1-1%           | Zero (after merge)  | High    | Newer    |
| Full FT         | 100%             | Zero                | Highest | Mature   |

LoRA dominates because it combines parameter efficiency, zero inference overhead (after merge), and high quality. Most production fine-tuning uses LoRA or QLoRA.

## Worked example: fine-tuning a chat model

A complete chat-model fine-tune ties the pieces together — load the base in bf16, apply LoRA to all linear layers, train with an SFT trainer, save the small adapter, then merge for deployment:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
from trl import SFTTrainer

# Load base model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")

# Apply LoRA
config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, config)

# Load dataset
dataset = load_dataset("your-chat-dataset", split="train")

# Train
training_args = TrainingArguments(
    output_dir="./lora-chat",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,  # effective batch size 16
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
    bf16=True,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()

# Save adapter (~50 MB)
model.save_pretrained("./lora-chat")
tokenizer.save_pretrained("./lora-chat")

# For deployment: merge
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./lora-chat-merged")
```

## Interview-style questions

**Why does LoRA work? Why can a low-rank update approximate full fine-tuning?** Empirically, fine-tuning updates have low intrinsic rank. The pretrained model already knows most of what it needs; fine-tuning makes small, low-dimensional adjustments. Rank 16-64 captures most of the benefit.

**How does LoRA's parameter count compare to full fine-tuning?** For a 7B model with rank 16 on all linear layers, LoRA has ~30M trainable parameters vs 7B for full FT — a 200× reduction. Memory savings are even larger (no optimizer state for frozen weights).

**Why initialize B to zero?** So that $\mathbf{B}\mathbf{A} = 0$ at the start, meaning the model behaves exactly like the pretrained model. LoRA then "grows" the delta from zero. Without this, the model would start in a random state and might not recover pretrained behavior.

**When would you merge LoRA vs. keep it separate?** Merge for single-task deployment (zero inference overhead). Keep separate for multi-tenant serving (swap adapters per request), A/B testing, or dynamic adapter selection.

**How does QLoRA differ from LoRA?** QLoRA loads the base model in 4-bit NF4 quantization, then trains LoRA adapters in bf16 on top. This enables fine-tuning a 70B model on a single 48 GB GPU. LoRA assumes the base model is in full precision.

**Why apply LoRA to all linear layers, not just attention?** FFN layers have most of the model's parameters. Skipping FFN limits the adapter's capacity. Applying LoRA to all linear layers (Q, K, V, O, gate, up, down) gives better quality at the same parameter count.

## Further reading

The primary papers and practical references:

- Hu et al. (2021), *LoRA: Low-Rank Adaptation of Large Language Models*.
- Dettmers et al. (2023), *QLoRA: Efficient Finetuning of Quantized LLMs*.
- Liu et al. (2024), *DoRA: Weight-Decomposed Low-Rank Adaptation*.
- HuggingFace PEFT docs: https://huggingface.co/docs/peft
- Sebastian Raschka's LoRA analysis: https://magazine.sebastianraschka.com/p/lora-and-dora-from-scratch

## See also

Related notes across the fine-tuning family:

- [[Training and Adaptation MOC]] — orientation for training and adaptation
- [[QLoRA]] — quantized base + LoRA
- [[DPO Derivation]] — fine-tuning with preferences (can be combined with LoRA)
- [[RLHF with PPO]] — RL fine-tuning (can use LoRA)
- [[Instruction Tuning and Chat Templates]] — instruction tuning (typically with LoRA)
- [[Mixed Precision Training]] — the bf16 training practice LoRA relies on
- [[Quantization]] — weight quantization, the complement that yields QLoRA
- [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]] — the broader transfer-learning tradition LoRA extends
- [[Matrix Multiplication]]
- [[Matrix Decomposition]]
- [[17 - Papers/Scaling and Training/LoRA.md|LoRA]]
