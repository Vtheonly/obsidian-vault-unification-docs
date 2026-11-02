---
title: Data Pipelines and Deduplication
type: concept
aliases: [Data Pipelines, Deduplication, Data Filtering, Pretraining Data]
tags: [llm, training, data-pipeline, deduplication, filtering, pretraining]
sources: ["03 - Data Pipelines and Deduplication"]
created_index: 10
---

Pretraining corpora are engineered rather than found: the raw web arrives as noisy HTML littered with boilerplate, near-duplicate pages, and mixed-quality content, and it has to be cleaned systematically before a model can train on it. This note covers the four-stage data pipeline — collection, extraction, filtering, and deduplication — together with the tooling, empirical evidence, and operating practices behind each stage. Skipping any stage silently degrades the trained model, and none more so than deduplication.

> [!info] TL;DR
> Pretraining data quality is the single biggest determinant of LLM quality. A 7B model trained on 2T tokens of well-curated, deduplicated, filtered data outperforms a 70B model trained on 5T tokens of raw web scrape. The data pipeline has four stages: **collection** (gather raw text), **extraction** (strip HTML, boilerplate, navigation), **filtering** (remove low-quality, toxic, or non-text content), and **deduplication** (remove near-duplicate documents). Each stage has well-established best practices and tooling. Skipping any stage — especially deduplication — silently degrades model quality.

## Why data pipelines matter

The Chinchilla scaling laws (Hoffmann et al., 2022) showed that for compute-optimal training, you need ~20 tokens per parameter (see [[Pretraining Objectives and Scaling Laws]]); a 70B model needs 1.4T tokens. But this assumes the tokens are high-quality. If the data contains duplicates, low-quality text, or irrelevant content, the effective compute-per-quality-token drops dramatically. Empirical studies have shown:

- **Deduplication** alone can improve benchmark performance by 5-15% (Lee et al., 2022).
- **Quality filtering** (keeping only high-quality text) can improve performance by 10-20%.
- **Toxic content filtering** reduces harmful generations without hurting general capability.
- **Code and math upweighting** improves reasoning even on non-code/math tasks.

A common saying in LLM training captures the stakes: "garbage in, garbage out, but at scale." The same scaling laws that make data quality matter for small models make it critical for large models — every issue is multiplied by the data scale.

## Collection

Collection, the first of the four pipeline stages, gathers the raw corpus. Pretraining data comes from a handful of source families. Web crawls supply the bulk: Common Crawl (the dominant source, ~5TB raw text per crawl) and CC-Stories (filtered story-like content). Curated corpora — Wikipedia, GitHub (code), arXiv (scientific papers), StackExchange (Q&A), PubMed (medical) — are high-quality but narrow. Books come from Books3 (controversial — copyright issues) and Project Gutenberg (public domain). Common Crawl includes news, and some teams license additional news corpora. Proprietary data — licensed data from publishers, internal data, synthetic data — rounds out the mix.

The mix matters. Llama 3's pretraining mix is roughly 50% web, 20% code, 17% books, 5% scientific, 8% other, and the exact mix is a hyperparameter tuned via ablations. The extremes both hurt: too much web and the corpus is broad but noisy; too much curated and it is high-quality but narrow.

### Formats

Raw data comes in many formats: HTML, PDF, JSON, XML, plain text. The pipeline must normalize to a common format (typically JSONL with `text`, `source`, `timestamp`, `url` fields).

### Volume vs. quality trade-off

More data is better only if it's high-quality. A 1T-token corpus of well-filtered data beats a 5T-token corpus of mixed quality, and the "quality per token" metric matters more than raw token count. Quality matters more than quantity.

## Extraction

Extraction, the second stage, converts fetched pages into clean text. Web pages contain text mixed with navigation, ads, boilerplate, and formatting; extraction removes the noise and keeps the content.

### HTML stripping

The standard HTML-stripping tools span a range of speed and quality:

- **trafilatura**: a Python library for web content extraction. Good balance of speed and quality.
- **resiliparse**: a fast C-based HTML parser and content extractor.
- **boilerpipe**: an older Java-based tool; less maintained.
- **Newspaper3k**: news-focused extractor.

The extraction step must preserve structure (paragraphs, headings, lists) while removing noise. Aggressive extraction (treating everything as one text blob) loses structure; conservative extraction (keeping all HTML) keeps noise.

### PDF extraction

PDFs are a major source of scientific and technical content but are notoriously hard to parse. The main tools:

- **GROBID**: a machine-learning-based PDF parser, good for scientific papers.
- **PyMuPDF (fitz)**: fast PDF text extraction.
- **pdfplumber**: more accurate but slower.
- **Nougat** (Meta, 2023): a neural PDF parser that handles formulas and tables. Better than rule-based tools for scientific PDFs.

PDF extraction quality varies wildly. For pretraining, expect to lose ~10-20% of PDF content to extraction failures.

### Boilerplate removal

Even after HTML stripping, pages contain boilerplate: cookie notices, navigation menus, related-content links. Boilerplate detection uses three families of signals:

- **Density-based**: text density (characters per line) identifies content vs. boilerplate.
- **Structural**: HTML structure (main content vs. sidebar) identifies content.
- **ML-based**: trained classifiers identify content blocks.

### Language identification

Use **fastText's language identification model** to tag each document with its language. Documents below a confidence threshold (e.g., 0.7) are discarded. This is essential for multilingual models — you don't want English training to be polluted by misclassified non-English text.

## Filtering

Filtering, the third stage, removes content that would actively harm training: low-quality text, toxic content, personal data, and benchmark contamination.

### Quality filters

Quality filtering removes low-quality text. The main approaches:

- **Perplexity filtering**: use a small LM (e.g., a 1B model trained on Wikipedia) to score documents. High perplexity = low quality. Keep documents with perplexity below a threshold.
- **Heuristic filters**: word count, average word length, ratio of stopwords, ratio of digits, presence of obscenities. These are crude but fast.
- **Classifier-based**: train a binary classifier on (high-quality, low-quality) document pairs. Apply to filter the corpus.

The CCNet pipeline (Wenzek et al., 2020) is the standard reference for quality filtering. It uses a 5-gram KenLM model trained on Wikipedia to score documents. Perplexity filtering works because Wikipedia is high-quality text: documents that are "surprising" to a Wikipedia-trained model are likely low-quality (spam, gibberish, boilerplate).

### Toxic content filtering

Toxic content (hate speech, violence, adult content) should be filtered for safety. Tools:

- **Toxic-BERT**: a classifier fine-tuned on the Jigsaw toxicity dataset.
- **List-based**: regex matching against word lists (crude but fast).
- **Block-list URLs**: filter content from known-bad domains.

> [!warning]
> Aggressive toxic filtering can remove legitimate content (medical text about violence, historical accounts of war). Tune thresholds carefully.

### Personally identifiable information (PII)

PII (SSNs, phone numbers, email addresses, credit card numbers) should be redacted:

- **Regex-based**: patterns for common PII formats.
- **NER-based**: named entity recognition for names, addresses, organizations.
- **Differential privacy**: add noise to rare n-grams (advanced; rarely used in pretraining).

### Contamination filtering

Benchmark contamination (training data containing test set questions) inflates benchmark scores on [[LLM Benchmarks]]. Filter:

- Exact-match: remove documents containing exact benchmark questions.
- N-gram match: remove documents with high n-gram overlap with benchmarks.
- Fuzzy match: remove documents with high fuzzy similarity.

This is essential for credible benchmark numbers. Models trained on contaminated data look better than they are.

## Deduplication

Deduplication, the final stage, removes near-duplicate documents and is the single highest-ROI data processing step.

### Why deduplication matters

Web data is highly duplicative:

- **Exact duplicates**: the same document appears at multiple URLs (mirrors, copies).
- **Near-duplicates**: the same document with minor edits (typos fixed, formatting changed).
- **Template-based**: boilerplate pages generated from templates (e.g., e-commerce product pages).
- **Cross-source**: Wikipedia content is copied into many other sources.

Without deduplication, the model sees the same content multiple times and overfits to it. This wastes training compute and produces biased models. Lee et al. (2022) showed that deduplication improves benchmark performance by 5-15% across model sizes, and the effect is largest for models trained on more data — duplicates compound with scale. Deduplication is also cheap (MinHash+LSH), which is why it has the highest quality-per-compute ratio of any data processing step.

### Exact deduplication

Exact deduplication removes documents with identical content. Implementation:

1. Compute a hash (e.g., SHA-256) of each document's normalized text.
2. Keep only the first document with each hash.

This is fast and catches exact duplicates. Tools: Apache Spark's `dropDuplicates`, custom hash-based deduplication.

### Fuzzy (near-duplicate) deduplication

Fuzzy deduplication removes documents that are similar but not identical. Approaches:

- **MinHash + LSH** (Locality-Sensitive Hashing): the standard approach. Compute MinHash signatures for each document; use LSH to find candidate pairs; verify with Jaccard similarity.
- **SimHash**: an alternative LSH technique. Compute a 64-bit fingerprint; documents with small Hamming distance are near-duplicates.
- **Embedding-based**: encode documents as embeddings; cluster; remove within-cluster duplicates. More expensive but catches semantic duplicates.

Under the hood, MinHash computes a signature (e.g., 128 hashes) for each document by hashing its n-grams and keeping the minimum, and LSH buckets documents with similar signatures so that candidate pairs can be verified with Jaccard similarity. This is what lets the approach scale to trillion-token corpora efficiently — O(n) per document, not O(n²) pairwise. MinHash + LSH is the production standard, and the standard reference implementation is in the DCLM (DataCombiner) and CommonCatalog pipelines.

### Document-level vs. paragraph-level deduplication

Deduplication can operate at two granularities:

- **Document-level**: remove duplicate documents. Catches mirror pages, copied articles.
- **Paragraph-level**: remove duplicate paragraphs within and across documents. Catches boilerplate paragraphs (e.g., "About the author" sections copied across many sites).

Production pipelines do both: document-level first (cheaper), then paragraph-level on the deduplicated set.

### Deduplication at training time

Even after offline deduplication, online (in-batch) deduplication helps: ensure that no two documents in the same batch are too similar. This prevents the model from memorizing specific phrasings. Implementation: maintain a rolling window of recent documents; reject new documents with high similarity to any in the window.

## The production pipeline

A modern pretraining data pipeline chains all of these stages end to end:

```mermaid
graph TD
  Crawl[Common Crawl raw HTML] --> Extract[trafilatura extraction]
  Extract --> LangID[Language identification]
  LangID --> Filter[Quality + toxicity + PII + contamination filters]
  Filter --> DedupExact[Exact deduplication: SHA-256]
  DedupExact --> DedupFuzzy[Fuzzy deduplication: MinHash + LSH]
  DedupFuzzy --> Mix[Mix with curated sources]
  Mix --> Tokenize[Tokenize with BPE]
  Tokenize --> Shard[Shard into training files]
  Shard --> Train[Pretraining]
```

Note that tokenization is applied after data processing — the corpus is fully extracted, filtered, and deduplicated before it is tokenized (see [[Tokenization Overview]]) and sharded into training files. Each stage is parallelized across hundreds of CPU machines. The full pipeline for a 5T-token corpus takes days to weeks on a cluster of 100+ machines.

## Tools and frameworks

The ecosystem covers everything from full Common Crawl processing to distributed deduplication:

| Tool | Role |
| --- | --- |
| **CCNet** | Facebook Research's pipeline for Common Crawl processing. Reference implementation for quality filtering. |
| **DCLM (DataCombiner)** | A modular pipeline from the DataComp-LM project. Modern, well-tested. |
| **CommonCatalog** | A catalog of processed Common Crawl snapshots. |
| **Datatrool** | HuggingFace's data processing library. Good for smaller-scale pipelines. |
| **Spark** | Distributed processing for the deduplication step. |
| **Ray** | Alternative distributed framework; some pipelines use Ray instead of Spark. |

CCNet is the KenLM-based quality-filtering reference described above, while DCLM (DataCombiner) and CommonCatalog carry the standard MinHash + LSH deduplication implementations.

## Practical recommendations

A short checklist distills the operating lessons of production pipelines:

- **Don't skip deduplication.** It's the single highest-ROI data processing step.
- **Use perplexity filtering** for quality. A 1B model trained on Wikipedia is sufficient.
- **Filter benchmarks aggressively.** Contamination is the most common cause of inflated benchmark numbers.
- **Version your data.** Track which documents came from which sources, processed by which pipeline version. Reproducibility requires this.
- **Build a held-out evaluation set** from your data. Sample 1000 documents after each stage; manually inspect. This catches pipeline regressions early.
- **Mix sources deliberately.** Web data is broad but noisy; curated data is high-quality but narrow. The mix is a key hyperparameter.

Every item traces back to the evidence above: deduplication and quality filtering carry the measured benchmark gains, deliberate mixing avoids the broad-but-noisy and high-quality-but-narrow failure modes, and aggressive contamination control is what makes those benchmark numbers credible in the first place.

## Interview questions

The mechanics above condense into six questions that come up repeatedly:

- **Q: Why is deduplication the single highest-ROI data processing step?**
  A: Web data is highly duplicative (mirrors, copies, templates). Without dedup, the model sees the same content multiple times and overfits to it. Lee et al. (2022) showed dedup improves benchmark performance by 5-15%. It's cheap (MinHash+LSH) and has the highest quality-per-compute ratio of any data processing step.

- **Q: How does MinHash + LSH work for fuzzy deduplication?**
  A: MinHash computes a signature (e.g., 128 hashes) for each document by hashing its n-grams and keeping the minimum. LSH (Locality-Sensitive Hashing) buckets documents with similar signatures. Candidate pairs are verified with Jaccard similarity. This scales to trillion-token corpora efficiently — O(n) per document, not O(n²) pairwise.

- **Q: What is perplexity filtering and why does it work?**
  A: Use a small LM (e.g., 1B trained on Wikipedia) to score each document. High perplexity = low quality (the document is surprising/unusual). Keep documents below a threshold. This works because Wikipedia is high-quality text; documents that are "surprising" to a Wikipedia-trained model are likely low-quality (spam, gibberish, boilerplate).

- **Q: How do you handle benchmark contamination in training data?**
  A: Three approaches: (1) exact-match — remove documents containing exact benchmark questions; (2) n-gram match — remove documents with high n-gram overlap with benchmarks; (3) fuzzy match — remove documents with high fuzzy similarity. This is essential for credible benchmark numbers.

- **Q: What is the ideal data mix for LLM pretraining?**
  A: Llama 3's mix is roughly 50% web, 20% code, 17% books, 5% scientific, 8% other. Code and math upweighting improves reasoning even on non-code/math tasks. The mix is a hyperparameter tuned via ablations. Too much web → broad but noisy; too much curated → high-quality but narrow.

- **Q: How does data quality interact with scaling laws?**
  A: Chinchilla's 20 tokens/parameter ratio assumes high-quality data. If data contains duplicates or low-quality text, the effective compute-per-quality-token drops. A 7B model on 2T well-curated tokens outperforms a 70B model on 5T raw web scrape. Quality matters more than quantity.

## See also

- [[Training and Adaptation MOC]] — orientation for the training and adaptation area
- [[Pretraining Objectives and Scaling Laws]] — what to do with the data; data quality affects compute-optimal training
- [[Distributed Training]] — how to train on the processed corpus
- [[Mixed Precision Training]] — numerical considerations once training begins
- [[Loss Spikes and Stability]] — what happens when data is bad; bad data causes spikes
- [[Embedding Model Training]] — data pipelines for embedding models
- [[LLM Benchmarks]] — the evaluations that contamination filtering protects
- [[PII and Data Leakage]] — PII filtering in data pipelines, from the production-security side
- [[Tokenization Overview]] — tokenization is applied after data processing
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — parameter-efficient adaptation of the pretrained base this pipeline produces
