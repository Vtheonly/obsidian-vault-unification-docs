---
title: BERT
type: concept
aliases: [Bidirectional Encoder Representations from Transformers]
tags: [transformer, encoder, bert, mlm, fine-tuning, nlp]
sources: ["07 - BERT"]
created_index: 23
---

BERT (Devlin et al. 2018) is a bidirectional, encoder-only Transformer pretrained with masked language modeling — the model that kicked off the modern NLP era. It produces contextual embeddings rather than text: no decoder, no generation. It is still widely used for classification, NER, and embeddings, and it is the backbone of modern embedding models such as BGE and E5; see [[Contextual Embeddings ELMo to BERT]] for where it sits in the lineage.

> [!info] TL;DR
> BERT (Devlin et al. 2018) is a bidirectional encoder-only Transformer pretrained with Masked Language Modeling. Kicked off the modern NLP era. Still widely used for classification, NER, embeddings, and as the backbone of modern embedding models (BGE, E5).

## Architecture

BERT is a Transformer **encoder** (see [[The Transformer]] and [[Transformer Block]]) with bidirectional attention — no causal mask — so every token attends to every other token (see [[Self-Attention]]). Base has 12 layers, hidden dim 768, 12 heads, 110M parameters; Large has 24 layers, hidden dim 1024, 16 heads, 340M parameters. No decoder, no generation: BERT produces contextual embeddings, not text.

## Pretraining objectives

### Masked language model

Randomly mask 15% of tokens; predict them from the rest. Of the 15% selected, 80% are replaced with `[MASK]`, 10% with a random token, and 10% left unchanged.

The mix forces the model to learn contextual representations, not just memorize the `[MASK]` token — the 10% random + 10% unchanged prevent the model from learning that masked positions are always `[MASK]`.

### Next sentence prediction

Given sentence pairs, predict whether they're adjacent in the original text. Uses a `[CLS]` token at the start. **RoBERTa (Liu et al. 2019)** showed NSP doesn't help and removed it; modern BERT-family models skip NSP.

## Input format

```
[CLS] sentence A [SEP] sentence B [SEP]
```

`[CLS]` is the classification token; its final-layer representation is used for sequence classification (see [[CLS Token]]). `[SEP]` separates segments. Segment embeddings are separate learned embeddings for sentence A vs B (see [[Embedding Layer]]).

## Fine-tuning BERT

The pretrain-then-fine-tune paradigm: **pretrain** BERT once on a large corpus (Wikipedia + BookCorpus), then **fine-tune** for downstream tasks with a small task-specific head — classification: `[CLS]` + linear head; NER: per-token linear head; Q&A: predict start and end positions; sentence pair: `[CLS]` + binary head. Fine-tuning is fast (an hour on a single GPU) and gives SOTA on many tasks with very little labeled data.

## The BERT family

Each variant refines the original recipe along a different axis:

| Model      | Change vs BERT                                  |
|------------|-------------------------------------------------|
| RoBERTa    | More data, bigger batches, no NSP, dynamic MLM  |
| ALBERT     | Factorized embeddings, parameter sharing        |
| DeBERTa    | Disentangled attention, enhanced mask decoder   |
| ELECTRA    | Replaced token detection (more efficient)       |
| DistilBERT | Distilled (6 layers, 60% params, 95% quality)   |
| Sentence-BERT | Pooled sentence embeddings for semantic search |

## BERT as embedding backbone

Many modern embedding models are BERT-like models fine-tuned for retrieval with contrastive loss: **BGE** (BAAI), **E5** (Microsoft), **GTE** (Alibaba), and **sentence-transformers** (SBERT), the original. These produce sentence/document embeddings for RAG, search, and clustering — still BERT-family under the hood.

## Worked example

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

inputs = tokenizer("This movie was great!", return_tensors="pt", truncation=True, max_length=512)
outputs = model(**inputs)
logits = outputs.logits  # (1, 2)
predicted_class = logits.argmax(-1)
```

For fine-tuning: standard supervised training, lr=2e-5, 3–5 epochs, batch size 16–32.

## Why this matters

BERT was the model that **made Transformers dominant** in NLP — the pretrain-then-fine-tune paradigm originated here. BERT-family models are still **the right choice** for classification, NER, extraction, and embedding: cheaper and often more accurate than LLMs for these tasks. For RAG, BERT-family embedding models (BGE, E5) are the standard — every RAG system uses one. Understanding BERT also helps you read older NLP papers (2018–2021) and use embedding models correctly. For the counterparts, see [[GPT Family]], [[T5 and BART]], and [[BERT vs GPT vs T5]].

## Production implications

For **classification / NER / extraction** with limited data, fine-tune a BERT-family model — faster, cheaper, often more accurate than an LLM. For **embeddings in RAG**, use a modern BERT-family embedder (BGE-large, E5-large, GTE-large); don't use raw BERT embeddings — fine-tuned for retrieval is much better. **Max sequence length** is 512 (or 1024 for some variants); for longer documents, use sliding window or Longformer. **Quantization**: BERT quantizes well to INT8; most serving frameworks support it out of the box. **DistilBERT** for low-latency / edge deployments: 60% smaller, 60% faster, 95% of quality.

## Common pitfalls

Five mistakes cover most BERT-related bugs:

- **Wrong tokenizer for the model** — `bert-base-uncased` requires lowercased input; `bert-base-cased` requires original case.
- **Forgetting `[CLS]` and `[SEP]`** — most HuggingFace tokenizers add these, but raw `encode` may not.
- **Using BERT for generation** — it can't generate; it's bidirectional.
- **Passing > 512 tokens** — silent truncation or error. Always truncate explicitly.
- **Comparing BERT embeddings across models** — different BERT variants have different embedding spaces. Don't mix.

## Further reading

Three papers anchor the BERT story:

- Devlin et al. (2019), *BERT: Pre-training of Deep Bidirectional Transformers*.
- Liu et al. (2019), *RoBERTa: A Robustly Optimized BERT Pretraining Approach*.
- Reimers & Gurevych (2019), *Sentence-BERT*.

## See also

- [[Attention and Transformers MOC]]
- [[BERT vs GPT vs T5]]
- [[GPT Family]]
- [[T5 and BART]]
- [[The Transformer]]
- [[Transformer Block]]
- [[CLS Token]]
- [[Contextual Embeddings ELMo to BERT]]
