---
title: Instruction Tuning and Chat Templates
type: concept
aliases: ["Instruction Tuning", "SFT", "Supervised Fine-Tuning", "Chat Templates"]
tags: [fine-tuning, instruction-tuning, sft, chat-templates]
sources: ["03 - Instruction Tuning and Chat Templates"]
created_index: 3
---

> [!info] TL;DR
> SFT (supervised fine-tuning) on instruction-response pairs turns a base LLM (which only predicts next tokens) into a chat model (which follows instructions). Chat templates format conversations consistently. The bridge between pretraining and aligned chat models.

Supervised fine-tuning (SFT) on instruction-response pairs is the step that turns a pretrained base LLM — which only predicts next tokens — into a chat model that follows instructions. The loop itself is small: collect pairs, format them with the model's chat template, and train with the standard causal-language-modeling loss computed on the response tokens only. Every part of that loop carries failure modes that fail silently rather than loudly, which is why chat templates, dataset quality, epochs, and learning rates each get their own treatment here. In the [[Training and Adaptation MOC]] pipeline, instruction tuning is the bridge between pretraining and aligned chat models, and the foundation that DPO and RLHF build on.

## What instruction tuning does

The behavioral difference is easiest to see with the same fact phrased two ways. A pretrained base LLM continues text: given the prompt "The capital of France is", it produces the completion " Paris, which is known for..." — a plausible sentence continuation, not an answer. An instruction-tuned model responds to instructions: given "What is the capital of France?", it returns "The capital of France is Paris."

The transformation between the two is supervised fine-tuning on (instruction, response) pairs. The model learns to treat the input as an instruction to follow, not text to continue — a reframing of what the input means, not a new architecture.

## The SFT training loop

The loop has three steps:

1. Collect (instruction, response) pairs — usually 10k–1M examples.
2. Format each as a single sequence using a chat template.
3. Train with standard CLM loss, but **only compute loss on the response tokens** (mask the instruction).

Step three is where implementations earn their keep: the model should learn to generate responses, not to predict the instruction, so every prompt token has to be excluded from the loss. A worked implementation renders the full conversation through the chat template, then renders the prompt-only version with `add_generation_prompt=True`; the length of the prompt-only tokenization marks exactly where the assistant response starts:

```python
def format_and_mask(example, tokenizer):
    text = tokenizer.apply_chat_template(
        [{"role": "user", "content": example["instruction"]},
         {"role": "assistant", "content": example["response"]}],
        tokenize=False,
    )
    full_ids = tokenizer(text, return_tensors="pt").input_ids[0]
    
    # Find where the assistant response starts; mask everything before
    prompt_text = tokenizer.apply_chat_template(
        [{"role": "user", "content": example["instruction"]}],
        tokenize=False, add_generation_prompt=True,
    )
    prompt_ids = tokenizer(prompt_text, return_tensors="pt").input_ids[0]
    
    labels = full_ids.clone()
    labels[:len(prompt_ids)] = -100  # ignore in loss
    return {"input_ids": full_ids, "labels": labels}
```

The labels start as a clone of the full input ids, and `labels[:len(prompt_ids)] = -100` overwrites every prompt position with -100 (PyTorch's ignore_index), so only response tokens contribute to the loss. Passing `tokenize=False` keeps `apply_chat_template` in string mode — it returns the formatted text, and the caller tokenizes the full sequence once.

## Chat templates

Each model has its own chat template — a way to format conversations into a single string the model was trained on. Chat templates are tokenization-level constructs: the control tokens they insert are vocabulary entries, and the user/assistant boundary they draw is exactly what the masking logic above keys off. The same two-turn conversation — "Hello!" from the user, "Hi there!" from the assistant — looks different under each family's template.

### ChatML (used by many models, including Qwen, some Mistral)

```text
<|im_start|>user
Hello!<|im_end|>
<|im_start|>assistant
Hi there!<|im_end|>
```

### Llama 3

```text
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Hello!<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Hi there!<|eot_id|>
```

### Mistral

```text
[INST] Hello! [/INST] Hi there!</s>
```

> [!warning]
> Each model expects its own template. Using the wrong template causes silent quality degradation — the model produces reasonable-sounding but suboptimal responses.

The degradation is silent because wrongly formatted input is still well-formed text: the model was simply never trained on that arrangement of control tokens, so it answers at lower quality without raising an error anywhere in the stack. The defense is to never assemble these strings by hand — `tokenizer.apply_chat_template(messages)` applies the correct template automatically.

## Instruction datasets

### Open-source datasets

The open ecosystem spans two orders of magnitude in scale and both origins — human-written and model-generated:

| Dataset | Composition |
|---|---|
| OpenAssistant | ~150k human-written conversations |
| Alpaca / Vicuna | GPT-3.5-generated instructions (52k) |
| Dolly | Databricks human-written (15k) |
| OpenHermes | large synthetic (1M) |
| UltraChat | large synthetic (1.5M) |
| FLAN | Google's instruction tuning collection |

The pattern in the table is that the human-written collections are small (Dolly at 15k, OpenAssistant at ~150k) while the synthetic ones run to a million examples and beyond — the quantity side of a trade-off that the quality guidance and the interview answers below both return to.

### Commercial and private datasets

On the commercial side, InstructGPT / GPT-4 data comes from human labelers plus RLHF, and Anthropic's HH-RLHF dataset pairs helpfulness with harmlessness. Beyond those, most frontier models use large proprietary SFT datasets that are never released; the open collections above are what everyone else trains on.

## Quality considerations

Whatever the origin, the bar the data must clear is the same. Diversity matters — vary instructions, response lengths, and topics, because the model reproduces whatever distribution it is shown. No contradictions: don't include conflicting instructions ("be brief" + "explain in detail"), since the model has no way to resolve them other than averaging. No harmful content, if you want a safe model — filter or label carefully. Format consistency: responses should follow a consistent style, because inconsistent styles leak directly into generation. And synthetic data can work — many top open models are trained mostly on synthetic (GPT-4-generated) data, so curation, not origin, is the deciding factor.

## Why instruction tuning matters

Instruction tuning is the step that turns a pretrained model into a useful chatbot; without it, LLMs are just text completers. The shift from "few examples in prompt" (ICL) to "fine-tuned on instructions" was the second big LLM shift, after pretraining — the in-prompt version of that earlier capability is covered in [[In-Context Learning]]. For most production use cases, you start with an instruction-tuned model (e.g., Llama-3-8B-Instruct, not Llama-3-8B). For custom fine-tuning, instruction tuning is the foundation — DPO/RLHF build on top.

## Production implications

The operating rules that follow from all of the above:

- **Use Instruct versions of models** for chat / agentic use cases. Base models are for research or continued pretraining.
- **Always apply the correct chat template.** HuggingFace tokenizers do this automatically via `apply_chat_template`.
- **For custom SFT**, use a framework like TRL (HuggingFace), Axolotl, or Unsloth. They handle the formatting and loss masking correctly.
- **Don't over-train.** SFT typically needs only 1–3 epochs on 10k–100k examples. More = overfitting.
- **Use LoRA** for SFT — full fine-tuning is rarely needed and expensive.

The last rule is the cost lever: SFT is usually combined with [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] rather than full fine-tuning, and [[QLoRA]] is the memory-efficient variant of that combination. The frameworks in the third bullet exist precisely because the first two rules are easy to get subtly wrong by hand.

## Common pitfalls

The recurring mistakes, each with the symptom it produces:

- **Using a base model for chat** — produces completions, not responses. Use Instruct versions.
- **Wrong chat template** — silent quality loss. Always use `apply_chat_template`.
- **Forgetting to mask instruction tokens in loss** — the model learns to "predict" the instruction, which is wasteful and can hurt quality.
- **Bad SFT data** — contradictions, low quality, and harmful content all leak into the model.
- **Too many epochs** — overfits; the model produces templated, repetitive responses.
- **Wrong LR for SFT** — typically 1e-5 to 5e-5 for full FT, 1e-4 to 5e-4 for LoRA. Higher than pretraining LR.

The learning rate row is the one that flips by method — full fine-tuning sits in the lower band, LoRA in the higher — and the reasoning behind each band is spelled out in the interview answers below. The first two rows are the classic "my fine-tuned model underperforms" reports, and both fail without any visible error.

## Interview questions

The distinctions interviewers probe about instruction tuning compress into six questions.

1. **Q: What is the difference between a base model and an instruction-tuned model?**
   A: A base model continues text: "The capital of France is" → " Paris, which is known for...". An instruction-tuned model responds to instructions: "What is the capital of France?" → "The capital of France is Paris." The transformation is SFT on (instruction, response) pairs. Always use Instruct versions for chat/agentic use cases.

2. **Q: Why do you mask the instruction tokens in the loss?**
   A: You only want the model to learn to *generate* responses, not to *predict* instructions. If you compute loss on instruction tokens, the model wastes capacity learning to generate the user's input. Mask instruction tokens with -100 (PyTorch's ignore_index) so only response tokens contribute to the loss.

3. **Q: What is a chat template and why does using the wrong one cause silent quality loss?**
   A: Each model has its own format for conversations (ChatML, Llama-3 format, Mistral [INST] format). The model was trained on its specific template. Using the wrong template means the model sees input in a format it wasn't trained on — it still produces reasonable-sounding output but at lower quality. Always use `tokenizer.apply_chat_template(messages)`.

4. **Q: How many examples do you need for SFT?**
   A: Typically 10K-100K high-quality examples for 1-3 epochs. More isn't better — over-training causes the model to produce templated, repetitive responses. Quality matters more than quantity: 10K diverse, well-formatted examples beat 100K mediocre ones.

5. **Q: What LR should you use for SFT?**
   A: Full fine-tuning: 1e-5 to 5e-5 (lower than pretraining because the model is already good). LoRA: 1e-4 to 5e-4 (higher because LoRA params start from zero). DPO: 5e-7 to 5e-6 (much lower — preference loss is sharp). Always sweep on a short run.

6. **Q: Can you do SFT with synthetic data (GPT-4-generated)?**
   A: Yes — many top open models (OpenHermes, Tulu) are trained mostly on synthetic data. Key considerations: (1) diversity — vary instructions, response lengths, topics; (2) no contradictions; (3) format consistency; (4) filter for quality (some synthetic data is bad). Synthetic data is scalable and cheap; quality control is the bottleneck.

## Further reading

Three papers anchor the lineage — the original instruction-following result, the self-generation recipe behind synthetic instruction data, and the open replication that popularized it:

- Ouyang et al. (2022), *Training language models to follow instructions with human feedback* (InstructGPT).
- Wang et al. (2022), *Self-Instruct: Aligning Language Models with Self-Generated Instructions*.
- Taori et al. (2023), *Stanford Alpaca*.

## See also

The neighboring notes, with the relationship in each case:

- [[Training and Adaptation MOC]] — the area orientation: where SFT sits between pretraining and preference alignment.
- [[Pretraining Objectives and Scaling Laws]] — the stage whose CLM loss SFT reuses on a much smaller corpus.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — usually combined with SFT.
- [[QLoRA]] — memory-efficient SFT.
- [[DPO Derivation]] — builds on top of SFT.
- [[RLHF with PPO]] — alternative alignment.
- [[In-Context Learning]] — SFT turns ICL into consistent behavior.
- [[Large Language Models MOC]] — the LLM capabilities that instruction tuning unlocks.
