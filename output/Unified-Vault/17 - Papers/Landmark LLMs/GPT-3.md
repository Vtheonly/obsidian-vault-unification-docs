---
title: GPT-3
type: concept
aliases: [GPT-3 2020, Brown 2020, Language Models are Few-Shot Learners]
tags: [paper, gpt, decoder, scaling, in-context]
sources:
  - "04 - GPT-3 2020"
created_index: 33
---

GPT-3 scaled the decoder-only Transformer to 175 billion parameters and demonstrated **few-shot in-context learning** — the ability to perform new tasks from a handful of examples placed in the prompt, with no weight updates. The paper reshaped the field's understanding of what scale alone could unlock and made "prompt engineering" a first-class engineering discipline. See [[Papers MOC]] for the surrounding area.

## Citation

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., et al. (2020). *Language Models are Few-Shot Learners*. NeurIPS 2020. arXiv:2005.14165.

## The problem being solved

After [[17 - Papers/Attention and Transformers/BERT|BERT]] (2018) and [[GPT-2]] (2019), transfer learning in NLP followed a clear pattern: pretrain → fine-tune on a downstream task. Fine-tuning works well but has costs: you need labeled data for every task, you need to store a separate fine-tuned copy of the model per task, and deployment becomes a model-management problem.

The GPT-2 paper had already hinted that sufficiently large language models could perform tasks *without* fine-tuning, just by conditioning on a prompt. But GPT-2 (1.5B params) was not reliable enough for production use. The GPT-3 authors hypothesized that scaling parameters, data, and compute by ~100× would push in-context learning past the threshold of practical usefulness.

The bet was that scale — not architectural innovation — was the main missing ingredient. GPT-3 has essentially the same architecture as GPT-2; the difference is 175B vs 1.5B parameters.

## The architecture

GPT-3 is a [[Decoder-Only Architecture|decoder-only Transformer]] with:

| Property            | Value           |
|---------------------|-----------------|
| Parameters          | 175B            |
| Layers              | 96              |
| Hidden dimension    | 12288           |
| Attention heads     | 96              |
| Context window      | 2048 tokens     |
| Vocabulary          | ~50K BPE        |
| Positional encoding | Learned         |

The architecture is deliberately conservative: pre-norm, learned positional (not [[RoPE]]), dense (no [[Mixture of Experts|MoE]]). The contribution is the scale, not the design.

### Model family

The paper also released a *family* of smaller models so researchers could study scaling behavior:

| Model     | Params  | Layers | d_model |
|-----------|---------|--------|---------|
| GPT-3 Small | 125M  | 12     | 768     |
| GPT-3 Medium | 350M | 24     | 1024    |
| GPT-3 Large | 760M   | 24     | 1536    |
| GPT-3 XL   | 1.3B    | 24     | 2048    |
| GPT-3 2.7B | 2.7B    | 32     | 2560    |
| GPT-3 6.7B | 6.7B    | 32     | 4096    |
| GPT-3 13B  | 13B     | 40     | 5140    |
| GPT-3 175B | 175B    | 96     | 12288   |

### Training data

- ~300B tokens of filtered Common Crawl (weight 60%).
- WebText2 (19%), Books1 (7%), Books2 (8%), Wikipedia (3%).

Total training compute: ~3.14 × 10²³ FLOPs. At 2020 prices this was a single run costing single-digit millions of dollars — a level of investment that defined the emerging "frontier model" economics.

## The three learning modes

The paper introduced a vocabulary that became standard:

- **Zero-shot**: condition on a task instruction only. E.g., "Translate English to French: cheese =>".
- **One-shot**: include one example. E.g., a single English→French pair, then a new prompt to translate.
- **Few-shot**: include K examples (typically 10–100) in the prompt, then the new query.

In all three modes the model weights are *frozen*. The "learning" is just the model conditioning on the prompt — no gradient updates. This was a paradigm shift: previously "learning" meant gradient updates; now it meant providing context (see [[In-Context Learning]]).

## Key results

GPT-3 was evaluated across >50 tasks: translation, QA, arithmetic, news article generation, novel tasks (word unscrambling, novel analogies), and on-the-fly reasoning.

### Translation

On X→English, GPT-3 few-shot matched unsupervised SOTA and approached supervised SOTA on some pairs. On English→X it was weaker, presumably because non-English text was a minority of the training corpus.

### Question answering

On TriviaQA, few-shot GPT-3 reached 64.3% — within 4 points of the open-domain fine-tuned SOTA at the time (64.8% for an open-book model). Without any fine-tuning or external retrieval.

### Arithmetic

On 2-digit addition, GPT-3 175B reached 100% accuracy; on 4-digit addition, ~26%; on 5-digit, ~10%. The smooth degradation suggests the model learned a real (if imperfect) algorithm rather than memorizing.

### News article generation

Human raters identified GPT-3-written news articles as human-written ~50% of the time at the 175B scale, vs ~12% for the 125M baseline. This was the first widely-publicized demonstration that LLMs could pass as human at the paragraph level.

### New tasks

The paper tested "task insertion" — teaching the model a completely synthetic mapping (e.g., "Use a word in a sentence"). At 175B, GPT-3 could often follow instructions demonstrated only in the prompt. The few-shot capability was real and robust to task novelty.

## Why it worked

### Smooth scaling

The most important scientific finding was that capability emerges *smoothly* with scale. Tasks that the 1.3B model could not do at all, the 13B model did poorly, and the 175B model did passably. There was no obvious threshold — but at any given scale, you could predict roughly where the model would land on the capability curve.

### In-context learning as an emergent property

GPT-2 did not exhibit reliable in-context learning. GPT-3 did. The difference was scale alone. This was strong evidence that ICL is not a specialized architectural feature but a property that emerges when a model has enough capacity and has been trained on enough diverse tasks (with tasks implicit in the pretraining data as document patterns).

### Meta-learning interpretation

The authors framed in-context learning as **meta-learning over SGD**: the model has seen millions of "tasks" in pretraining (each sequence is a different implicit task), so it learns a learning algorithm that operates over the activations (the prompt) rather than the weights. This is now the standard interpretation.

## Limitations

The paper itself acknowledged serious limitations, many of which became central concerns of subsequent research:

- **Hallucination**. GPT-3 confidently invents facts, citations, and entities (see [[Hallucination]]).
- **Weak long-context reasoning**. Beyond ~2048 tokens the model "forgets" early prompt content.
- **Common-sense failures**. The model produces plausible-sounding but logically wrong answers in physical/world-knowledge reasoning.
- **Bias amplification**. Gender, racial, and religious biases from the training corpus show up in completions.
- **Few-shot is not robust**. Performance varies a lot with prompt phrasing — the model is sensitive to formatting and example ordering.
- **No tool use**. GPT-3 (as released in the paper) cannot call calculators, search the web, or execute code. All reasoning has to happen inside the forward pass.
- **Energy and cost**. A single 175B inference is expensive. Production deployment at scale required quantization, distillation, and routing — topics that became core inference engineering concerns.

## Impact and legacy

GPT-3 reshaped the field in several concrete ways:

1. **Prompt engineering as a discipline**. Once the model was fixed, the lever engineers had was the prompt. [[RAG]], the [[ReAct Pattern]], [[Chain of Thought|CoT]], and the entire agent ecosystem grew from this shift.

2. **The API economy**. OpenAI launched the GPT-3 API in 2020, the first widely-used "model as a service." This established the commercial pattern that all frontier labs followed.

3. **Scale as a research bet**. The smooth scaling curves made "just scale it" a legitimate research strategy. Chinchilla (2022), PaLM (2022), Gopher (2021), and Llama (2023) all extended this bet empirically (see [[Scaling Laws (Kaplan and Chinchilla)]]).

4. **Foundation for instruction tuning**. GPT-3's raw completions were often unhelpful (e.g., continuing a question with another question). [[InstructGPT]] (2022) showed that lightweight RLHF made GPT-3 dramatically more useful. ChatGPT launched on top of this instruction-tuned variant.

5. **Benchmarks had to evolve**. GPT-3 saturated many existing benchmarks, which motivated MMLU, BIG-Bench, GPQA, and the modern eval ecosystem (see [[LLM Benchmarks]]).

## What came after

- **InstructGPT / ChatGPT** (2022): RLHF on top of GPT-3 → conversational, helpful assistant.
- **GPT-4** (2023): multimodal, MoE (rumored), much stronger reasoning; architecture officially undisclosed.
- **Codex** (2021): GPT-3 fine-tuned on code → GitHub Copilot.
- **Llama** (2023): open weights at GPT-3-class quality, much smaller, enabled the open LLM ecosystem.

## Further reading

- Original paper: arXiv:2005.14165
- Kaplan et al. (2020), *Scaling Laws for Neural Language Models* — the theoretical basis for GPT-3's scale.
- Hoffmann et al. (2022), *Training Compute-Optimal LLMs* (Chinchilla) — refined the scaling law.
- OpenAI API documentation.

## See also

- [[GPT-2]] — the 1.5B predecessor whose zero-shot hints GPT-3 made practical
- [[InstructGPT]] — the RLHF layer that made GPT-3 useful
- [[GPT-4 Technical Report]] — the multimodal successor
- [[LLaMA]] — the open-weights response at GPT-3-class quality
- [[Scaling Laws (Kaplan and Chinchilla)]] — the scaling-law lineage (Kaplan and Chinchilla)
- [[GPT Family]] — the family overview
- [[Papers MOC]]
