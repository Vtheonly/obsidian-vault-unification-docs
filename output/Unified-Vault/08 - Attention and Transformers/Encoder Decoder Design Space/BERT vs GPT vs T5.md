---
title: BERT vs GPT vs T5
type: concept
aliases:
  - The Encoder-Decoder Design Space
  - BERT GPT T5
  - encoder-only vs decoder-only
  - Transformer design space
tags:
  - transformers
  - architecture
  - bert
  - gpt
  - t5
  - encoder-decoder
  - design-space
sources:
  - "01. The Encoder-Decoder Design Space - BERT vs GPT vs T5"
created_index: 20
---

The full Transformer (Vaswani et al. 2017) has both an encoder and a decoder, but you can use the pieces separately, producing three configurations: encoder-only (BERT), decoder-only (GPT), and encoder-decoder (T5). The three make opposite architectural choices — bidirectional versus causal attention, masked language modeling versus next-token prediction versus denoising — and each is good at a different family of tasks. This note explains why BERT, GPT, and T5 make those choices, what each is good and bad at, and why the field converged on decoder-only for general-purpose LLMs.

## The three Transformer configurations

### Encoder-only (BERT, RoBERTa, DeiT, ViT)

An encoder-only model is a stack of encoder blocks with **bidirectional self-attention** — every token attends to every other token, with no masking. It is trained with **masked language modeling (MLM)**: randomly mask 15% of tokens and predict them from the unmasked context, so the model sees the entire sequence (with holes) and fills them in.

This configuration is good at **understanding** tasks where the whole input is available at once: classification (sentiment, topic), entity recognition (per-token labels), question answering (extract an answer span from context), retrieval (encode query and documents, compare them), and image classification (ViT).

It is bad at **generation**. Because attention is bidirectional, every token sees every other token — you cannot generate one token at a time without "cheating" by looking at the future. Encoder-only models are not naturally autoregressive. Generating with one requires workarounds rather than the native next-token loop of a decoder.

Examples: BERT (Devlin et al. 2018), RoBERTa, ALBERT, DeiT, ViT, CLIP image encoder.

### Decoder-only (GPT, LLaMA, PaLM, Mistral)

A decoder-only model is a stack of decoder blocks **without cross-attention** — just masked self-attention + FFN. Causal masking means each token attends only to itself and previous tokens. The training objective is **next-token prediction**: given tokens $1, \ldots, t$, predict token $t+1$. The model sees only the past and predicts the future.

This configuration is good at **generation** tasks: text completion, chat / dialogue, code generation, translation (by framing it as "English: ... French: ..." and generating the French), and summarization (by framing it as "Article: ... Summary: ..." and generating the summary) — essentially any task that can be framed as "continue this text".

It is bad at tasks requiring **bidirectional understanding**. A decoder-only model processes text left-to-right, so it cannot use information from later tokens to inform earlier ones. For tasks like extractive QA ("find the answer span in this passage") this is a mild disadvantage — but in practice, decoder-only models are large enough that they overcome this limitation.

Why it dominates modern LLMs: decoder-only models can be trained on **any text** without needing input/output pairs. The entire internet is training data — just predict the next token. This is why GPT-3, LLaMA, and essentially all modern LLMs are decoder-only: the training data is effectively unlimited, and the architecture scales gracefully.

Examples: GPT-2, GPT-3, GPT-4, LLaMA, PaLM, Mistral, Qwen, Claude, Gemini.

### Encoder-decoder (T5, BART, original Transformer, Whisper)

An encoder-decoder model is the full encoder + decoder with **cross-attention**. The encoder processes the input bidirectionally; the decoder generates the output autoregressively, attending to the encoder via cross-attention.

The training objective is **denoising / span-filling**. T5 trains by corrupting the input (dropping spans, replacing them with sentinel tokens) and training the decoder to reconstruct the original. BART trains by corrupting the input (token deletion, text infilling, sentence shuffling) and reconstructing it.

This configuration is good at **sequence-to-sequence** tasks where input and output are distinct: translation (English → French), summarization (long article → short summary), speech recognition (audio → text, e.g., Whisper), and code generation from specs (spec → code).

It is bad at tasks where input and output are **not naturally distinct**. For example, for open-ended chat, an encoder-decoder model needs to be fed "user message: X, assistant response:" and generate the response — but the encoder is processing a different sequence than the decoder is generating, which is wasteful compared to a decoder-only model that processes "user message: X, assistant response: Y" as one sequence.

Examples: original Transformer (Vaswani 2017), T5 (Raffel et al. 2019), BART, Whisper, M2M100.

## Why three configurations exist — the task-architecture fit

The three configurations exist because different tasks have different input-output structures, and the architecture should match:

| Task type | Input | Output | Best configuration |
| :--- | :--- | :--- | :--- |
| Classification | One sequence | One label | Encoder-only |
| Span extraction (QA) | One sequence | One span | Encoder-only |
| Generation (open-ended) | One sequence (prompt) | One sequence (continuation) | Decoder-only |
| Translation | Source sequence | Target sequence | Encoder-Decoder |
| Summarization | Long sequence | Short sequence | Encoder-Decoder |
| Speech recognition | Audio sequence | Text sequence | Encoder-Decoder |

The pattern: **if input and output are the same sequence (continuation), use decoder-only. If they are distinct sequences, use encoder-decoder. If there is no generation (just understanding), use encoder-only.**

This is the cleanest way to think about the design space, but there is a major caveat: **decoder-only models can do everything**, just sometimes less efficiently. GPT-3 (decoder-only) does translation by framing it as text continuation; T5 (encoder-decoder) does it natively. Both work; the decoder-only approach is simpler (one architecture for all tasks) but the encoder-decoder approach is more parameter-efficient for sequence-to-sequence tasks. The field has converged on **decoder-only for general-purpose LLMs** (because of training-data simplicity and scaling) and **encoder-decoder or encoder-only for task-specific models** (where the task structure is known in advance).

## Masked language modeling vs next-token prediction

The training objective is the deepest difference between encoder-only and decoder-only models.

### BERT's masked language modeling (MLM)

Mask 15% of tokens randomly; predict the masked tokens from the *bidirectional* context; the model sees the whole sequence (with holes) and fills them in. MLM is **bidirectional**: predicting a masked token in the middle of a sentence can use information from both sides. This is why BERT is good at understanding tasks — it has learned to use the full context.

MLM is **not naturally generative**: you cannot generate a sequence by masking tokens, because the model expects to see the surrounding context. Generating with BERT requires iterative refinement (mask-and-rewrite), which is awkward.

### GPT's next-token prediction (NTP)

Given tokens $1, \ldots, t$, predict token $t+1$; the model sees only the past (causal masking); training runs on every position simultaneously (teacher forcing). NTP is **unidirectional**: predicting token $t+1$ can only use tokens $1, \ldots, t$. This is less natural for understanding (BERT's bidirectional context is richer) but is **exactly the inference-time task** for generation — at inference, you generate token $t+1$ from the previous tokens, which is what NTP trains.

NTP is **naturally generative**: at inference, you feed the prompt, predict the next token, append it, predict the next, and so on. No architectural mismatch between training and inference.

The tradeoff: MLM gives better per-token understanding (bidirectional) but no natural generation. NTP gives natural generation but weaker per-token understanding (unidirectional). The modern resolution: **scale NTP enough and the understanding catches up.** GPT-3 and beyond are decoder-only (NTP-trained) yet perform well on understanding tasks, simply because they have seen enough text to learn bidirectional patterns implicitly.

## The "one architecture to rule them all" trend

The field has trended toward **decoder-only models** for general-purpose AI, for three reasons:

1. **Training data simplicity.** NTP uses any text — no masking, no input/output pairing, no task-specific formatting. The entire internet is training data.
2. **Scaling simplicity.** One architecture, one objective, one training loop. Scale up the model, the data, and the compute, and capabilities emerge.
3. **Task universality.** A decoder-only model can do translation, summarization, QA, classification, code generation, etc. — all by framing the task as text continuation. No need for different architectures per task.

Encoder-only models (BERT) remain dominant for **task-specific understanding** (classification, retrieval) where you do not need generation and want maximum sample efficiency. Encoder-decoder models (T5, Whisper) remain dominant for **sequence-to-sequence tasks** where the input/output distinction is natural and parameter efficiency matters. But for general-purpose AI — the GPT/Claude/Gemini class — decoder-only has won. The simplicity of "predict the next token, scale it up, see what emerges" has proven more powerful than the more structured alternatives.

## Key takeaways

1. Three Transformer configurations: encoder-only (BERT), decoder-only (GPT), encoder-decoder (T5).
2. Encoder-only is bidirectional, trained with masked LM, best for understanding.
3. Decoder-only is causal, trained with next-token prediction, best for generation — and dominates modern LLMs.
4. Encoder-decoder has cross-attention, trained with denoising, best for distinct input/output tasks (translation, summarization).
5. The training objective is the deepest difference: MLM (bidirectional, understanding) vs NTP (causal, generation).
6. The field has converged on decoder-only for general-purpose AI, because NTP uses any text as training data and scales gracefully.
7. Encoder-only and encoder-decoder remain relevant for task-specific models where the task structure is known.

## See also

- [[Attention and Transformers MOC]]
- [[The Transformer]] — the original encoder-decoder architecture
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the canonical encoder-only model
- [[GPT Family]] — the decoder-only lineage
- [[T5 and BART]] — the encoder-decoder lineage
- [[Transformer Decoder Block]] — causal masking and cross-attention in the decoder
- [[ViT Architecture]] — encoder-only attention applied to images
- [[Autoregressive vs Parallel Encoding]] — the processing trade-off behind these choices
- [[Information Bottleneck and Latent Space]] — what flows between encoder and decoder
- [[Choosing the Right Architecture]] — task-by-task selection guidance
- [[The Encoder-Decoder Pattern]] — the RNN version of this design space
