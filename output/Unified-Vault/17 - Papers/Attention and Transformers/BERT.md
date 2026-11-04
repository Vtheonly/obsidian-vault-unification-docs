---
title: BERT
type: concept
aliases: [BERT 2018, Devlin 2018, Bidirectional Encoder Representations from Transformers]
tags: [paper, bert, encoder, masked-language-model, pretraining]
sources:
  - "03 - BERT 2018"
created_index: 10
---

BERT (Bidirectional Encoder Representations from Transformers) showed that pretraining a Transformer encoder with two simple unsupervised objectives — Masked Language Modeling (MLM) and Next Sentence Prediction (NSP) — produces representations that transfer to almost any NLP classification or QA task with minimal fine-tuning. BERT established the **pretrain-then-finetune** paradigm that still dominates NLP, and it remains a production workhorse for search ranking, intent classification, moderation, and embedding generation. This note covers the bidirectional pretraining recipe, its results, its successors, and where it still runs today — see [[Papers MOC]] for the surrounding paper collection and [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] for the concept-level treatment.

## Citation

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL 2019. arXiv:1810.04805.

## The problem being solved

In 2017, the standard recipe for NLP transfer learning was: pretrain word embeddings (Word2Vec, GloVe) → use them as input features to a task-specific architecture (CNN, BiLSTM, etc.). This worked but was shallow — the pretrained representations captured only static word meaning, not syntax, semantics, or context.

[[Attention Is All You Need|Attention Is All You Need]] and [[GPT-1]] (Radford 2018) had shown that you could pretrain a Transformer end-to-end and then fine-tune. But GPT-1 used a **decoder-only** architecture with left-to-right (causal) language modeling, which meant the representation of each token could only see its left context. For tasks like NER, sentiment, or QA — which benefit from bidirectional context — this was a real limitation.

BERT's contribution was to ask: what if we pretrain a *bidirectional* encoder that can see both left and right context for every token? The challenge is that standard language modeling is left-to-right; you cannot predict the next token if you have already seen it. BERT solved this with **masked language modeling** — randomly mask some tokens and predict them from the surrounding context on both sides.

## The architecture

BERT is a multi-layer Transformer encoder. The paper released two sizes:

| Model      | Layers | Hidden | Heads | Params |
|------------|--------|--------|-------|--------|
| BERT Base  | 12     | 768    | 12    | 110M   |
| BERT Large | 24     | 1024   | 16    | 340M   |

BERT Base was deliberately sized to match GPT-1's parameter count to enable head-to-head comparison.

### Input representation

The input is a sequence of WordPiece tokens (see [[WordPiece]]). Each token's representation is the sum of:

1. **Token embedding** — learned lookup.
2. **Segment embedding** — learned "sentence A" vs "sentence B" indicator (for NSP).
3. **Position embedding** — learned, absolute position up to 512.

Special tokens: `[CLS]` (always the first token; its final hidden state is used as the aggregate sequence representation for classification — see [[CLS Token]]), `[SEP]` (sentence boundary), `MASK` (placeholder for MLM), `[PAD]`.

### Pretraining objective 1: masked language modeling (MLM)

Randomly mask 15% of WordPiece tokens. Of those:

- 80% replaced with `MASK`.
- 10% replaced with a random token.
- 10% left unchanged.

The model predicts the original token at each masked position. The 80/10/10 split is a mismatch-distribution trick: pure `MASK` never appears at fine-tune time, so the small random-replacement and unchanged fractions force the model to maintain useful representations for every token, not just `MASK`.

Only masked positions contribute to the loss — this makes MLM less sample-efficient than causal LM (which has a loss on every token), but the bidirectional context more than compensates in downstream quality.

### Pretraining objective 2: next sentence prediction (NSP)

For tasks like QA or NLI that involve sentence-pair reasoning, BERT adds an auxiliary binary classification: given two sentences A and B, is B the actual next sentence in the source corpus, or a random sentence?

50% of training pairs are real consecutive sentences; 50% have B sampled randomly. The `[CLS]` token's representation is fed to a binary classifier. Later work (RoBERTa) showed NSP adds little value; it was dropped in most subsequent encoder pretraining.

### Pretraining data

- BooksCorpus (800M words)
- English Wikipedia (2,500M words)

Total ~3.3B words. Pretraining took 4 days on 64 TPU v2 chips for BERT Large — nontrivial but accessible by 2018 standards.

## Fine-tuning

For downstream tasks, BERT is fine-tuned by replacing the output head with a task-specific layer and training end-to-end on the downstream dataset for a few epochs. The paper showed four canonical task setups:

- **Single-sentence classification** (SST-2 sentiment, etc.): `[CLS]` hidden state → linear classifier.
- **Sentence-pair classification** (MNLI, QQP, etc.): same as above, with both sentences concatenated.
- **Question answering** (SQuAD): for each token, predict start and end probabilities of the answer span.
- **Sequence labeling** (NER): per-token classifier.

Fine-tuning is cheap: SQuAD took ~30 minutes on a single TPU.

## Key results

BERT set new state of the art on 11 NLP tasks:

| Task                     | Previous SOTA | BERT   | Δ      |
|--------------------------|---------------|--------|--------|
| GLUE (average)           | 80.6          | 82.1   | +1.5   |
| SQuAD 1.1 (F1)           | 91.6          | 93.2   | +1.6   |
| SQuAD 2.0 (F1)           | 83.0          | 87.1   | +4.1   |
| SWAG (acc)               | 78.4          | 86.5   | +8.1   |

The improvements were not marginal; BERT moved the field decisively. Within months, virtually every NLP benchmark had a BERT-based leader.

## Why it worked

### Bidirectional context

Every token's representation aggregates information from both left and right neighbors. For tasks like NER or QA, where the surrounding context is essential, this is materially better than a left-to-right decoder.

### Pretrain-finetune as a paradigm

The paper made the recipe explicit: pretrain on cheap unlabeled text → fine-tune on small labeled data. This worked so well that within a year it was the *default* approach for any NLP task with limited labels.

### Cheap fine-tuning

Because BERT's representations were already strong, fine-tuning required only a few epochs on a small dataset. This brought transfer learning within reach of any research lab, not just large companies.

### The [CLS] token as a pooling convention

Using a single token's representation as the input to a task head is simple and effective. The convention persists across most encoder and encoder-decoder models today.

## Limitations and what came after

- **NSP was a wash**. RoBERTa (Liu et al., 2019) removed NSP, used more data, larger batches, and dynamic masking — strictly better. The lesson: BERT's *architecture* was right; its *pretraining recipe* was conservative.
- **Static maximum length of 512**. BERT cannot natively process long documents. [[Longformer]], [[BigBird]], and other long-context encoders addressed this with sparse attention.
- **WordPiece + cased/uncased vocabulary** is brittle for non-English text and code. [[SentencePiece]] and BPE-based tokenizers became standard.
- **Encoder-only is awkward for generation**. BERT cannot be used directly as a language model. GPT-style decoder-only models eventually dominated because they handle both understanding and generation with a single architecture.
- **Whole-word masking helps**. Later Chinese and multilingual BERT variants adopted whole-word masking to avoid the model "cheating" by predicting only sub-tokens.

## Successors

- **RoBERTa** (Facebook, 2019): optimized pretraining recipe; same architecture, better results.
- **ALBERT** (Google, 2019): parameter sharing across layers; smaller, faster.
- **DistilBERT** (HuggingFace, 2019): 6-layer distillation of BERT; ~60% smaller, ~60% faster, retains 95%+ quality.
- **DeBERTa** (Microsoft, 2020): disentangled attention; better position/word representation separation.
- **ELECTRA** (Stanford/Google, 2020): replaced-token detection pretraining, far more sample-efficient.
- **Sentence-BERT** (2019): siamese fine-tune for sentence embeddings.

## Impact and legacy

BERT reshaped NLP in three concrete ways:

1. **Established pretrain-finetune as universal**. After BERT, no serious NLP system trained from scratch — every model was either pretrained or distilled from a pretrained model.
2. **Made Transformers the default encoder**. CNNs and BiLSTMs essentially disappeared from new NLP architectures after 2019.
3. **Created the open-weights ecosystem**. BERT was released on day one (on arXiv and Google's repo) and quickly appeared in HuggingFace's model hub. This set the precedent for the open-weights culture that defined the 2018–2025 LLM era.

For inference and production deployments, BERT remains a workhorse in 2024–2026: search ranking, intent classification, moderation, embedding generation. The model that pioneered the recipe is also the model that still runs in production at scale.

## Further reading

- Original paper: arXiv:1810.04805
- RoBERTa: arXiv:1907.11692 (Liu et al., 2019) — the optimized recipe.
- ELECTRA: arXiv:2003.10555 — replaced-token detection.
- DeBERTa: arXiv:2006.03654 — disentangled attention.
- HuggingFace `transformers` library — BERT, RoBERTa, DeBERTa all available.

## See also

- [[Papers MOC]] — the paper index for this area.
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the concept-level treatment of the architecture.
- [[GPT-1]] — the decoder-only counterpart released the same year.
- [[Attention Is All You Need|Attention Is All You Need]] — the Transformer encoder BERT is built from.
- [[Contextual Embeddings ELMo to BERT]] — the ELMo-to-BERT evolution of contextual representations.
- [[T5]] and [[GPT-2]] — the encoder-decoder and decoder-only paths that followed.
- [[WordPiece]], [[BPE]] and [[SentencePiece]] — the tokenization stack.
- [[Embedding Layer]] — how the token/segment/position sums are implemented.
- [[Longformer]] and [[BigBird]] — the long-context encoders that lifted the 512-token limit.
- [[Embedding Models for Retrieval]] — where BERT-class encoders live in production retrieval.
