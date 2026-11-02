---
title: Choosing the Right Architecture
type: concept
aliases:
  - Choosing the Right Architecture for the Task
  - task-to-architecture mapping
  - architecture selection
tags:
  - transformers
  - architecture
  - encoder-decoder
  - model-selection
  - design-space
  - task-mapping
sources:
  - "04. Choosing the Right Architecture for the Task"
created_index: 21
---

Given a task, which Transformer configuration should you use — encoder-only, decoder-only, or encoder-decoder? The answer reduces to three questions: does the task require generation, are input and output distinct sequences, and how much data do you have. This note ties the design space together into actionable guidance — a decision tree, task-by-task recommendations, and per-configuration guidance — then closes with the modern reality: decoder-only dominance for general-purpose AI, with encoder-only and encoder-decoder remaining the right choice for task-specific, parameter-efficient models.

## The decision framework

Given a task, which Transformer configuration should you use? The answer depends on three questions:

1. **Does the task require generation?** If yes, you need a decoder (autoregressive). If no, an encoder suffices.
2. **Are input and output distinct sequences?** If yes, encoder-decoder is natural. If no (input is a prefix of output), decoder-only.
3. **How much data do you have?** If limited, prefer the most parameter-efficient architecture (encoder-only for understanding, encoder-decoder for seq2seq). If abundant, decoder-only scales best.

## The decision tree

```
Does the task require generation?
│
├── NO (understanding only: classification, retrieval, QA-span, NER)
│   └── Use ENCODER-ONLY (BERT, RoBERTa, DeiT, ViT)
│       — bidirectional context, MLM-trained, parameter-efficient
│
└── YES (generation required)
    │
    ├── Are input and output distinct sequences (translation, summarization, ASR)?
    │   │
    │   ├── YES, and parameter efficiency matters
    │   │   └── Use ENCODER-DECODER (T5, BART, Whisper)
    │   │       — encoder processes input bidirectionally, decoder generates
    │   │
    │   └── NO, or parameter efficiency is not critical
    │       └── Use DECODER-ONLY (GPT, LLaMA)
    │           — simpler, scales better, any text as training data
    │
    └── Is the task open-ended (chat, code, creative writing)?
        └── Use DECODER-ONLY — this is what modern LLMs are built for
```

## Task-by-task recommendations

### Understanding tasks (no generation)

| Task | Recommendation | Why |
| :--- | :--- | :--- |
| Text classification | Encoder-only (BERT) | Bidirectional context; small model suffices |
| Named entity recognition | Encoder-only (BERT) | Per-token labels; bidirectional context |
| Question answering (extractive) | Encoder-only (BERT) | Find span in context; bidirectional |
| Sentence embeddings / retrieval | Encoder-only (BERT, with contrastive loss) | Encode query and docs independently |
| Image classification | ViT (encoder-only) | Whole image available; CLS token readout |

Understanding tasks are the encoder's home ground: the whole input is available at once, bidirectional context earns its keep, and a small parameter-efficient model usually suffices.

### Sequence-to-sequence tasks (distinct input/output)

| Task | Recommendation | Why |
| :--- | :--- | :--- |
| Translation | Encoder-decoder (T5, Marian) or large decoder-only | Distinct input/output; encoder-decoder more efficient |
| Summarization | Encoder-decoder (BART, T5) or decoder-only | Distinct input/output; encoder-decoder handles long input well |
| Speech recognition | Encoder-decoder (Whisper) | Audio input, text output — fundamentally distinct |
| Code from spec | Decoder-only (Codex, StarCoder) | Spec is a prefix of the code; decoder-only natural |

When input and output are genuinely distinct sequences, the encoder-decoder split is the natural fit — unless the "input" is really a prefix of the output, as when generating code from a spec, where decoder-only is the native shape of the task.

### Open-ended generation

| Task | Recommendation | Why |
| :--- | :--- | :--- |
| Chat / dialogue | Decoder-only (GPT, LLaMA, Claude) | The dominant architecture for conversational AI |
| Text completion | Decoder-only | The native task of decoder-only models |
| Creative writing | Decoder-only | Open-ended; no fixed input/output structure |
| Code completion | Decoder-only (Codex) | Continue the code; decoder-only natural |

Open-ended generation has no fixed input/output structure to exploit, which is precisely the regime the decoder-only architecture was built for.

### Vision tasks

| Task | Recommendation | Why |
| :--- | :--- | :--- |
| Image classification | ViT (encoder-only) | Whole image; CLS token |
| Object detection | Swin Transformer + detection head | Hierarchical features needed |
| Semantic segmentation | Swin / ViT + decoder (U-Net style) | Dense prediction; encoder-decoder |
| Image generation | Diffusion model with U-Net | Iterative denoising; encoder-decoder pattern |

Vision follows the same logic: classification is understanding (encoder-only), dense prediction needs an encoder-decoder structure, and generation leans on the iterative denoising of diffusion models with a U-Net — itself an encoder-decoder pattern.

## When to use each configuration

### Encoder-only (BERT, ViT)

Use encoder-only when the task is understanding, not generation; when the whole input is available at once; when parameter efficiency matters (limited compute or data); and when you need rich bidirectional representations. Do not use it when you need to generate output, or when the task is open-ended (chat, completion).

### Decoder-only (GPT, LLaMA)

Use decoder-only when the task is generation (especially open-ended); when you have abundant training data (or are fine-tuning a pretrained model); when you want one architecture for many tasks (a universal model); and when simplicity and scalability matter. Do not use it when the task is purely understanding and you need maximum parameter efficiency (encoder-only is better), or when the task has a distinct input/output structure and you need efficiency (encoder-decoder is better).

### Encoder-decoder (T5, BART, Whisper)

Use encoder-decoder when the task is sequence-to-sequence with distinct input and output; when parameter efficiency matters (the encoder-decoder structure is more efficient than decoder-only for seq2seq); and when the input is long and needs bidirectional processing before generation. Do not use it when the task is open-ended generation (decoder-only is simpler), when the task is understanding only (encoder-only suffices), or when you want a universal model for many tasks (decoder-only is more flexible).

## The modern reality: decoder-only dominance

For general-purpose AI (the GPT/Claude/Gemini class), **decoder-only has won**. The reasons:

1. **Training data simplicity.** Next-token prediction uses any text. No masking, no input/output pairing, no task formatting. The entire internet is training data.
2. **Scaling.** One architecture, one objective. Scale up model, data, compute — capabilities emerge.
3. **Universality.** A decoder-only model can do translation (frame as continuation), summarization (frame as continuation), QA (frame as continuation), classification (frame as continuation + restrict output). One model, all tasks.
4. **Inference simplicity.** One inference pattern: feed prompt, generate continuation. No task-specific heads, no architectural switches.

Encoder-only and encoder-decoder remain relevant for **task-specific models** where the task structure is known and parameter efficiency matters: BERT-style models for classification, retrieval, NER (especially on-device or in pipelines), and T5/Whisper for translation, summarization, ASR (where the seq2seq structure is natural and efficiency matters). But for general-purpose AI, the field has converged on decoder-only. The GPT-4 / Claude / Gemini / LLaMA class are all decoder-only Transformers, trained on next-token prediction, fine-tuned with RLHF, and deployed as universal assistants.

## Key takeaways

1. The choice of Transformer configuration depends on: does the task need generation? Are input/output distinct? How much data do you have?
2. Encoder-only for understanding (classification, retrieval, NER, ViT).
3. Encoder-decoder for sequence-to-sequence with distinct input/output (translation, summarization, ASR).
4. Decoder-only for generation, especially open-ended (chat, completion, code).
5. For general-purpose AI, decoder-only has won — the GPT/Claude/Gemini class are all decoder-only.
6. Encoder-only and encoder-decoder remain relevant for task-specific, parameter-efficient models.

This concludes the picture: you now understand the Transformer architecture, its application to vision (ViT), and the encoder/decoder design space. The other great architectural family of modern deep learning — autoencoders, VAEs, GANs, and diffusion models — extends these same encoder-decoder ideas into generative modeling.

## See also

- [[Attention and Transformers MOC]]
- [[BERT vs GPT vs T5]] — the three configurations compared
- [[Autoregressive vs Parallel Encoding]] — the processing trade-off behind the choice
- [[Information Bottleneck and Latent Space]] — what flows between encoder and decoder
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the encoder-only exemplar
- [[GPT Family]] — the decoder-only exemplar
- [[T5 and BART]] — the encoder-decoder exemplar
- [[ViT Architecture]] — encoder-only attention for images
- [[Inductive Bias]] — how architecture encodes task assumptions
