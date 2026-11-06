---
title: NLP and Language Models MOC
type: overview
aliases: [NLP Fundamentals MOC, NLP and Language Models Map of Content, NLP MOC]
tags: [nlp, moc, language-modeling, tokenization, embeddings, information-retrieval]
sources:
  - "05 — NLP Fundamentals MOC"
created_index: 5
---

This map of content is the entry point to the NLP and Language Models area — the pre-Transformer NLP background you need to understand what Transformers replaced and why. Ten notes span four sub-families: tokenization, embeddings, language modeling, and pre-Transformer information retrieval. Together they cover the whole input side of a language model plus the classical retrieval stack that preceded neural ranking.

> [!info] TL;DR
> The pre-Transformer NLP background you need to understand what Transformers replaced and why. Read the notes in numbered order.

## Reading order

| # | Note | Sub-family | Purpose |
|---|---|---|---|
| 01 | [[Tokenization Overview]] | Tokenization | The bridge between text and model IDs. |
| 02 | [[BPE]] | Tokenization | The dominant subword algorithm. |
| 03 | [[WordPiece]] | Tokenization | BERT's tokenizer. |
| 04 | [[SentencePiece]] | Tokenization | Multilingual / language-agnostic library. |
| 05 | [[Word2Vec GloVe and FastText]] | Embeddings | Static word embeddings. |
| 06 | [[Contextual Embeddings ELMo to BERT]] | Embeddings | The shift to contextual embeddings. |
| 07 | [[N-Gram Language Models]] | Language Modeling | Pre-neural LMs; baseline. |
| 08 | [[Perplexity]] | Language Modeling | The intrinsic LM metric. |
| 09 | [[TF-IDF]] | Pre-Transformer | Classical IR scoring. |
| 10 | [[BM25]] | Pre-Transformer | **SOTA for keyword search; hybrid RAG component.** |

## Sub-families

The numbered order is also a dependency order: tokenization comes first because everything downstream consumes tokens; embeddings follow because models represent tokens as vectors; language modeling asks how well a model predicts them; and the two IR notes close the loop on searching raw text. Sequence modeling itself — RNNs, LSTMs, GRUs, and the Seq2Seq pattern whose limitations motivated attention — is deliberately out of scope here and lives in the sequence models area ([[07 - Sequence Models/Chapter Overview|Chapter Overview]]).

- **Tokenization** — notes 01–04: [[Tokenization Overview]], [[BPE]], [[WordPiece]], [[SentencePiece]].
- **Embeddings** — notes 05–06: [[Word2Vec GloVe and FastText]] and [[Contextual Embeddings ELMo to BERT]], the shift that ends at [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]].
- **Language modeling** — notes 07–08: [[N-Gram Language Models]] and [[Perplexity]].
- **Pre-Transformer NLP** — notes 09–10: [[TF-IDF]] and [[BM25]].

## Why this area matters

Transformers operate on **tokens** and produce **embeddings**. To understand the input pipeline of any LLM, you need to understand tokenization. To understand why attention was invented, you need to understand the limitations of RNN-based Seq2Seq. To understand modern hybrid RAG, you need BM25. The attention story these notes set up continues in [[Attention and Transformers MOC]].

## See also

- [[Tokenization Overview]] — start here; the first note in the reading order.
- [[Neural Network Foundations MOC]] — the underlying NN machinery.
- [[07 - Sequence Models/Chapter Overview|Chapter Overview]] — the RNN, LSTM and GRU background, including the Seq2Seq limits that motivated attention.
- [[Attention and Transformers MOC]] — what replaced RNNs.
- [[The Transformer]] — the architecture that consumes the tokens and embeddings this area introduces.
- [[GPT Family]] — the modern language models.
- [[Large Language Models MOC]]
- [[Agents and Tooling MOC]]
