---
title: Build a Fine-Tuning Pipeline with LoRA and DPO
type: tutorial
aliases: [LoRA DPO Pipeline, Build Fine-Tuning Pipeline, SFT DPO Pipeline]
tags: [project, fine-tuning, lora, dpo, pipeline, alignment]
sources: ["19 - Build a Fine-Tuning Pipeline with LoRA and DPO"]
created_index: 3
---

Turning a base LLM into a chat assistant is a two-stage recipe: supervised fine-tuning (SFT) teaches the model what good responses look like, and Direct Preference Optimization (DPO) teaches it to prefer good responses over bad ones. This capstone builds that pipeline end to end on a base model such as Llama-3-8B — data prep, LoRA-based SFT, DPO training, evaluation, adapter merging, and deployment. The theory lives in [[Instruction Tuning and Chat Templates]] and [[DPO Derivation]]; this note is the hands-on build, indexed with the other capstones in [[Projects MOC]].

> [!info] TL;DR
> Build an end-to-end fine-tuning pipeline that takes a base model + your data and produces an aligned model via SFT (Supervised Fine-Tuning) with LoRA, then DPO (Direct Preference Optimization). The pipeline handles data prep, training, evaluation, merging, and deployment — covering the standard recipe used to turn a base LLM into a chat assistant. This capstone integrates the fine-tuning, training, inference, and production-operations material into one production-ready system.

## Project goals

By the end of this project, you will have built:

1. A data preparation script for SFT (instruction-response pairs) and DPO (chosen-rejected pairs).
2. SFT training with LoRA via HuggingFace TRL + PEFT.
3. DPO training on top of the SFT model.
4. Evaluation harness: perplexity, MMLU, MT-Bench, hallucination rate.
5. LoRA merging back into the base model for deployment.
6. Deployment via vLLM with the merged model.

## Architecture

The pipeline is strictly sequential: the base model plus an SFT dataset produce an SFT adapter; the adapter plus a preference dataset produce the aligned adapter; the aligned adapter is merged back into the base, evaluated, and deployed:

```mermaid
graph TD
    Base[Base Model e.g. Llama-3-8B] --> SFTData[SFT Dataset]
    SFTData --> SFT[SFT Trainer LoRA]
    SFT --> SFTModel[SFT Adapter]
    SFTModel --> DPOData[DPO Dataset chosen/rejected]
    DPOData --> DPO[DPO Trainer LoRA]
    DPO --> Aligned[Aligned Adapter]
    Aligned --> Merge[Merge to base]
    Merge --> Merged[Merged model]
    Merged --> Eval[Eval harness]
    Eval --> Deploy[Deploy via vLLM]
```

## Prerequisites

```bash
pip install transformers peft trl datasets accelerate bitsandbytes
pip install vllm  # for deployment
pip install lm-eval  # for MMLU
```

## Data preparation

The SFT dataset is instruction-response pairs; the DPO dataset is preference pairs of the form (prompt, chosen, rejected). Both are converted to the model's chat format with `apply_chat_template` — always the base model's official template rather than hand-rolled formatting, because a mismatched chat template is one of the most common ways these pipelines silently break.

```python
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer

def prepare_sft_data(instruction_path: str, output_path: str):
    """Convert instruction-response pairs to chat-format SFT data."""
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
    raw = load_dataset("json", data_files=instruction_path, split="train")

    def to_chat(ex):
        # Apply chat template
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": ex["instruction"]},
            {"role": "assistant", "content": ex["response"]},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        return {"text": text}

    processed = raw.map(to_chat, remove_columns=raw.column_names)
    processed.save_to_disk(output_path)

def prepare_dpo_data(preference_path: str, output_path: str):
    """Convert preference pairs (prompt, chosen, rejected) to DPO format."""
    raw = load_dataset("json", data_files=preference_path, split="train")
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

    def to_dpo(ex):
        prompt_messages = [{"role": "user", "content": ex["prompt"]}]
        prompt = tokenizer.apply_chat_template(prompt_messages, tokenize=False)
        chosen_messages = [{"role": "assistant", "content": ex["chosen"]}]
        rejected_messages = [{"role": "assistant", "content": ex["rejected"]}]
        return {
            "prompt": prompt,
            "chosen": tokenizer.apply_chat_template(chosen_messages, tokenize=False, add_generation_prompt=False),
            "rejected": tokenizer.apply_chat_template(rejected_messages, tokenize=False, add_generation_prompt=False),
        }

    processed = raw.map(to_dpo, remove_columns=raw.column_names)
    processed.save_to_disk(output_path)
```

## SFT training with LoRA

The SFT stage loads the base model in 4-bit (QLoRA) so training fits on modest hardware, then attaches LoRA adapters and trains them with TRL's `SFTTrainer`. The LoRA config targets all seven projection modules — `q_proj`, `k_proj`, `v_proj`, `o_proj` plus the three MLP projections — with rank 16 and alpha 32, which is the standard general-chat configuration; [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] covers the mechanics and [[QLoRA]] the 4-bit training scheme. Training runs 3 epochs at LR 2e-4 on a cosine schedule with BF16, an effective batch of 16 via gradient accumulation, and packing enabled so short examples share sequences:

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer
import torch

def train_sft(
    base_model_id: str = "meta-llama/Meta-Llama-3-8B",
    sft_data_path: str = "./data/sft",
    output_dir: str = "./checkpoints/sft",
    epochs: int = 3,
    lr: float = 2e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
):
    # Load base model in 4-bit (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="flash_attention_2",  # If available
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA configuration
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,  # effective batch = 16
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        weight_decay=0.0,
        max_grad_norm=0.3,
        bf16=True,
        save_strategy="epoch",
        save_total_limit=3,
        logging_steps=10,
        report_to="wandb",
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=load_from_disk(sft_data_path),
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=2048,
        packing=True,  # Pack short examples together for efficiency
    )

    trainer.train()
    trainer.save_model(output_dir)
    return output_dir
```

The `attn_implementation="flash_attention_2"` line picks up [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] kernels when available for faster attention.

## DPO training

DPO runs on top of the SFT checkpoint: the SFT-trained adapter is loaded onto the (still 4-bit) base model with `PeftModel.from_pretrained`, and `DPOTrainer` optimizes the preference objective — the math is in [[DPO Derivation]]. Two hyperparameters matter most. The learning rate is 5e-6, roughly 10x lower than SFT, because DPO is far more sensitive to it. Beta (0.1 by default) is the KL penalty strength — it doubles as the DPO temperature: higher values keep the model closer to the SFT reference (more conservative), lower values let it move further (more aggressive):

```python
from trl import DPOTrainer, DPOConfig

def train_dpo(
    sft_model_path: str = "./checkpoints/sft",
    dpo_data_path: str = "./data/dpo",
    output_dir: str = "./checkpoints/dpo",
    epochs: int = 1,
    lr: float = 5e-6,
    beta: float = 0.1,  # DPO temperature
):
    # Load SFT model + LoRA adapter
    base_model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Meta-Llama-3-8B",
        quantization_config=bnb_config,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(base_model, sft_model_path)

    # DPO config
    dpo_config = DPOConfig(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,  # effective batch = 16
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        bf16=True,
        beta=beta,  # KL penalty strength
        max_prompt_length=1024,
        max_length=2048,
        save_strategy="epoch",
        report_to="wandb",
    )

    trainer = DPOTrainer(
        model=model,
        args=dpo_config,
        train_dataset=load_from_disk(dpo_data_path),
        processing_class=tokenizer,
    )

    trainer.train()
    trainer.save_model(output_dir)
    return output_dir
```

## Evaluation harness

Four metrics, each with a distinct role: perplexity on wikitext as a sanity check that the model still models text, MMLU for retained capability, MT-Bench (a GPT-4-judged multi-turn benchmark) for chat quality, and hallucination rate on TruthfulQA. MMLU goes through lm-eval with 5-shot prompting; MT-Bench and the hallucination check use a judge model — the pattern covered in [[LLM-as-Judge Evaluation]]. The perplexity implementation is shared with the [[Build a Quantization Toolkit]] capstone:

```python
class EvalHarness:
    def __init__(self, model_path: str, tokenizer_path: str):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, device_map="auto", torch_dtype=torch.bfloat16,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    def perplexity(self, dataset: str = "wikitext-2-raw-v1/test") -> float:
        # ... (see Quantization Toolkit project for impl)
        pass

    def mmlu(self, n_samples: int = 200) -> float:
        # Use lm-eval-harness
        from lm_eval import simple_evaluate
        results = simple_evaluate(
            model="hf",
            model_args=f"pretrained={self.model.name_or_path}",
            tasks=["mmlu"],
            num_fewshot=5,
            limit=n_samples,
        )
        return results["results"]["mmlu"]["acc"]

    def mt_bench(self, judge_model: str = "gpt-4o") -> dict:
        """Multi-turn benchmark using GPT-4 as judge."""
        from mt_bench_eval import run_mt_bench
        return run_mt_bench(
            model=self.model,
            tokenizer=self.tokenizer,
            judge_model=judge_model,
        )

    def hallucination_rate(self, dataset: str = "truthfulqa") -> float:
        """% of responses flagged as hallucinated by GPT-4 judge."""
        # Run TruthfulQA, compute % wrong answers
        pass

    def run_all(self) -> dict:
        return {
            "perplexity": self.perplexity(),
            "mmlu": self.mmlu(),
            "mt_bench": self.mt_bench(),
            "hallucination_rate": self.hallucination_rate(),
        }
```

## LoRA merging

For deployment the adapter is folded back into the base weights: load the base in BF16 on CPU, attach the adapter, call `merge_and_unload()`, and save the merged model together with the tokenizer. The output is a plain HuggingFace model with no PEFT dependency:

```python
def merge_lora(base_model_id: str, lora_path: str, output_path: str):
    """Merge LoRA adapter back into base model for deployment."""
    base = AutoModelForCausalLM.from_pretrained(
        base_model_id, torch_dtype=torch.bfloat16, device_map="cpu",
    )
    model = PeftModel.from_pretrained(base, lora_path)
    merged = model.merge_and_unload()
    merged.save_pretrained(output_path)
    # Also save tokenizer
    AutoTokenizer.from_pretrained(base_model_id).save_pretrained(output_path)
    print(f"Merged model saved to {output_path}")
```

## Deployment with vLLM

The merged model is served with [[14 - Inference and Production/Inference/vLLM|vLLM]] behind an OpenAI-compatible API, which is what the `vllm serve` entry point gives you:

```python
# deploy.py
from vllm import LLM, SamplingParams

llm = LLM(
    model="./merged_model",
    dtype="bfloat16",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
    max_model_len=8192,
)

# Serve via OpenAI-compatible API
# vllm serve ./merged_model --port 8000
```

## Production hardening checklist

The lessons that separate a working training script from a production pipeline:

1. **Data quality**: deduplicate SFT data (MinHash + LSH); filter low-quality responses (length, repetition, toxicity).
2. **Chat template**: use the base model's official chat template; mismatched templates break everything.
3. **QLoRA for memory**: 4-bit base + LoRA adapters fit a 70B model on a single 80GB GPU.
4. **Loss masking**: mask the prompt tokens in SFT loss — only train on response tokens (otherwise the model wastes capacity learning to predict prompts).
5. **LR sensitivity**: SFT LR=2e-4, DPO LR=5e-6 (10x lower — DPO is more sensitive).
6. **Beta tuning**: DPO beta=0.1 default; higher = more conservative, lower = more aggressive.
7. **Eval before/after each stage**: track metrics through SFT and DPO; DPO should improve MT-Bench without hurting MMLU.
8. **Reward hacking check**: DPO can overfit to preferences — check that the model isn't just longer/shorter than the chosen responses.
9. **Save intermediate checkpoints**: every epoch; keep the best by eval metric, not the last.
10. **Merge before deployment**: serving LoRA adapters is possible but slower; merge for production.
11. **Quantize after merge**: INT8 or FP8 the merged model for faster inference.
12. **A/B test**: deploy the fine-tuned model alongside the base; route 10% traffic; compare quality and engagement.

## Modern developments (2024–2026)

Fine-tuning practice moved quickly between 2024 and 2026; these are the developments that changed the standard recipe.

### DPO variants (IPO, KTO, SimPO)

IPO (Identity Preference Optimization) fixes DPO's overfitting on noisy preferences. KTO (Kahneman-Tversky Optimization) uses single-sided preferences (good/bad) instead of pairs. SimPO (Simple Preference Optimization) is length-normalized DPO; better for production. All are available in TRL 0.9+, and SimPO is the 2025 default for new projects. [[DPO]] covers the original objective these build on.

### GRPO (group relative policy optimization)

DeepSeek-R1 (2025) uses GRPO — a PPO variant that uses group-relative advantages instead of a learned value function. Simpler than PPO, more stable than DPO, and works well for verifiable rewards (math, code). Increasingly popular for reasoning model training; see [[DeepSeek-R1]], [[RLHF with PPO]], and the [[Build a Reasoning Model Fine-Tune]] capstone.

### Multimodal fine-tuning

Extending SFT+DPO to vision-language models: fine-tune the language model while keeping the vision encoder frozen. LLaVA-Factory, Axolotl, and LLaMA-Factory all support multimodal fine-tuning. Related builds: [[LLaVA]], [[Build a Vision-Language Model]], and [[Build a Multimodal Agent]].

### Synthetic data generation

Use a stronger model (GPT-4, Claude) to generate SFT data for specific tasks. Distillation from a teacher model is now standard for fine-tuning smaller models. Quality control (LLM-as-judge filtering) is essential — the [[Build a Model Distillation Pipeline]] capstone covers the teacher-driven workflow.

### LoRA variants (DoRA, ReLoRA, PiSSA)

DoRA decomposes weights into magnitude + direction; better quality than LoRA at same rank. ReLoRA restarts LoRA training periodically to escape local minima. PiSSA initializes LoRA with principal singular values; faster convergence. All are drop-in replacements for LoRA in PEFT 0.10+.

## Common failure modes

The diagnostic table maps observed symptoms to their usual causes and fixes:

| Symptom                                | Likely Cause                                  | Fix                                                          |
|----------------------------------------|-----------------------------------------------|--------------------------------------------------------------|
| SFT loss plateaus                      | LR too high; or data quality poor             | Lower LR; inspect data; add more diverse examples             |
| Model produces wrong format            | Chat template mismatched                       | Use base model's official chat template exactly               |
| DPO not improving MT-Bench             | LR too low; or beta too high                  | Increase LR to 5e-6; decrease beta to 0.05                    |
| DPO reward hacking (longer responses)  | No length normalization                        | Use SimPO (length-normalized DPO); track response length      |
| MMLU drops after DPO                   | DPO overfitting; capability lost               | Lower DPO LR; fewer epochs; or use IPO (more conservative)    |
| QLoRA OOM                              | 4-bit base + LoRA + activations too large     | Reduce batch; use gradient accumulation; smaller LoRA rank    |
| Merged model differs from adapter      | Merge bug; or wrong base model                 | Verify base model SHA; use `merge_and_unload()` correctly     |
| vLLM refuses merged model              | Quantization mismatch; or wrong format        | Save in safetensors format; verify dtype matches              |
| Catastrophic forgetting                | SFT too aggressive on narrow domain            | Mix in general data (10–20%); use lower LR; LoRA over full FT |
| Eval shows improvement but users hate it| Eval set doesn't reflect production           | Sample real production queries; refresh eval set              |

## Interview questions

**Walk through the full fine-tuning pipeline from base model to deployed chat assistant.** (1) **Base model**: Llama-3-8B (or similar). (2) **SFT data**: 10k–100k instruction-response pairs. (3) **SFT training**: 3 epochs LoRA (r=16) on the response tokens only; LR 2e-4, cosine schedule, BF16. (4) **DPO data**: 5k–50k preference pairs (prompt, chosen, rejected). (5) **DPO training**: 1 epoch on top of SFT model; LR 5e-6, beta 0.1. (6) **Eval**: perplexity (sanity), MMLU (capability), MT-Bench (chat quality), hallucination rate. (7) **Merge**: LoRA adapters merged into base. (8) **Quantize**: INT8 or FP8 for inference. (9) **Deploy**: vLLM serving the merged+quantized model. (10) **A/B test**: 10% traffic initially; monitor quality and engagement.

**Why use LoRA instead of full fine-tuning?** (1) **Memory**: LoRA trains only 0.1–1% of parameters; fits a 70B model on one GPU vs 8+ for full FT. (2) **Speed**: 2–3x faster training (less gradient computation). (3) **Storage**: adapters are 10–100MB vs 14GB for a 7B model. (4) **Modularity**: multiple adapters can be swapped at inference (one base model + many adapters). (5) **Quality**: LoRA matches full FT quality at rank 16+ for most tasks. (6) **Catastrophic forgetting**: LoRA preserves the base model's knowledge better than full FT. Trade-off: for very large domain shifts (continued pretraining on a new language), full FT is still better.

**What's the difference between SFT and DPO, and why do both?** SFT teaches the model what good responses look like (imitation learning on chosen responses). DPO teaches the model to prefer good responses over bad ones (preference learning on pairs). SFT alone produces a model that mimics the training distribution but doesn't know what's "better" vs "worse". DPO refines the model's preferences, making it more aligned with human judgment. Pipeline: SFT first (gives the model basic chat capability), then DPO (refines quality). Skipping SFT and going straight to DPO usually fails — the model doesn't have basic chat ability.

**How do you choose the LoRA rank (r)?** Trade-off: higher r = more capacity = better quality but more parameters/memory. (1) **r=8**: enough for narrow tasks (single-domain fine-tuning like medical QA). (2) **r=16**: default for general chat fine-tuning. (3) **r=32–64**: large domain shifts (continued pretraining on a new language). (4) **r=128+**: rarely needed; usually indicates you should do full FT instead. Empirically, quality saturates around r=64 for most tasks. Memory: r=16 on Llama-3-8B = ~50M trainable params (0.6% of total).

**How do you debug DPO training that's not improving?** (1) **Check data quality**: are the preferences actually informative? Use LLM-as-judge to verify. (2) **Check LR**: too high (5e-5+) causes divergence; too low (1e-7) doesn't move. Default 5e-6. (3) **Check beta**: too high (1.0+) makes DPO too conservative; too low (0.01) causes reward hacking. Default 0.1. (4) **Check SFT quality**: if SFT is bad, DPO can't fix it. (5) **Check loss**: DPO loss should decrease; if not, gradient is wrong. (6) **Check reward margin**: if chosen and rejected rewards are too close, the model isn't learning to distinguish. (7) **Length bias**: DPO can hack by making responses longer/shorter; track response length.

**How do you deploy a fine-tuned model for production?** (1) **Merge LoRA** into the base model (faster inference than adapter serving). (2) **Quantize**: INT8 for A100, FP8 for H100+, INT4 for edge. (3) **Benchmark**: latency, throughput, memory, quality on a representative eval set. (4) **vLLM serving**: `vllm serve merged_model --port 8000`; OpenAI-compatible API. (5) **A/B test**: route 10% of traffic to the new model; compare quality (LLM-as-judge on real prompts) and engagement (thumbs up/down, session length). (6) **Rollback plan**: keep the previous model on standby; auto-rollback if quality degrades >5%. (7) **Monitoring**: track latency, error rate, cost, quality (sample 1% of responses for LLM-as-judge). (8) **Iterate**: collect new preferences from production; retrain monthly.

## See also

- [[Projects MOC]] — the projects index.
- [[Instruction Tuning and Chat Templates]] — SFT and chat template details.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — LoRA mechanics.
- [[QLoRA]] — 4-bit base + LoRA adapters.
- [[DPO Derivation]] — the DPO objective.
- [[RLHF with PPO]] — the RLHF alternative to DPO.
- [[DPO]] — the original DPO paper.
- [[InstructGPT]] — the SFT + preference optimization lineage.
- [[DeepSeek-R1]] — GRPO training at scale.
- [[Quantization]] — post-merge INT8/FP8 quantization.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — serving the merged model.
- [[Build a Reasoning Model Fine-Tune]] — reasoning-specific fine-tuning.
- [[Build an RLHF Pipeline with PPO]] — the PPO-based counterpart pipeline.
- [[Build a Model Distillation Pipeline]] — synthetic SFT data from a teacher.
- [[Build a Quantization Toolkit]] — the perplexity implementation and post-merge quantization workflow.
- [[Build a Speculative Decoding Server]] — speeding up the deployed model.
