---
title: Embedding Models for Retrieval
type: concept
aliases: ["Embedding Models for Retrieval", "Embedding Models", "retrieval embedding models", "BGE", "BAAI General Embedding", "E5", "GTE", "SigLIP-2"]
tags: [embedding-models, retrieval, contrastive, bge, e5, gte, mteb, rag]
sources: ["02 - Embedding Models (BGE, E5, GTE, SigLIP-2)"]
created_index: 4
---

> [!info] TL;DR
> Modern embedding models (BGE, E5, GTE, OpenAI text-embedding-3, SigLIP-2) are BERT-family encoders — or decoder-based models for the larger variants — fine-tuned with a contrastive loss to produce sentence and document embeddings for retrieval. They are the backbone of every RAG system. The 2024–2026 landscape adds BGE-M3 (multilingual + multi-granularity), SigLIP-2 (image-text), and the late-interaction (ColBERT/ColPali) alternative to single-vector embeddings.

Retrieval embedding models turn queries and documents into vectors in a space where semantic similarity becomes geometric proximity, and they are the backbone of every retrieval-augmented generation (RAG) system. The modern landscape spans open-source BERT-family workhorses (BGE, E5, GTE), decoder-based quality leaders (E5-Mistral, GTE-Qwen2), commercial APIs (OpenAI, Cohere, Voyage), a multimodal image-text entry (SigLIP-2), and the late-interaction paradigm (ColBERT, ColPali). This note covers what makes an embedding model a retrieval model, the major model families and their MTEB evaluation, worked examples, choosing and operating them in production, the 2024–2026 developments, and a diagnostic table for the failure modes you will actually hit. See [[Foundation Models and Multimodal MOC]] for the surrounding family and [[Embedding Model Training]] for how these models are trained.

## What makes a retrieval embedding model

A standard [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] model produces contextual token embeddings, but no single "sentence embedding." To get a sentence embedding, you can pool token embeddings (mean, max, or `[CLS]`), or fine-tune with a contrastive objective that pushes similar sentences together and dissimilar ones apart in embedding space.

Modern retrieval embedding models use the second approach — contrastive fine-tuning on millions of (query, relevant_doc, irrelevant_doc) triplets. The contrastive loss (InfoNCE for CLIP-style, sigmoid for SigLIP-style) trains the model to score the correct (query, doc) pair higher than incorrect pairs. This produces embeddings where semantic similarity = cosine similarity.

The key property: embeddings live in a vector space where **semantic similarity = geometric proximity**. This allows vector search: given a query, find the documents whose embeddings are closest. Without contrastive training, BERT embeddings don't have this property — semantically similar sentences can be far apart in embedding space.

## The major embedding models

### BGE (BAAI General Embedding, 2022–2024)

BGE is open-source and BERT-family. Its variants scale from BGE-small (33M) through BGE-base (110M) to BGE-large (335M), plus BGE-M3 (multilingual + multi-granularity). It delivers strong performance on retrieval benchmarks (MTEB) and is used by most open-source RAG systems. BGE-M3 (2024) is the flagship: it supports 100+ languages, dense + sparse + multi-vector retrieval, and up to 8K context.

### E5 (Microsoft, 2022–2024)

E5 is BERT-family, with contrastive training on web text + labeled data. Variants: E5-base, E5-large, multilingual-E5, and E5-Mistral (decoder-based, 7B parameters). It is strong on multilingual retrieval. E5-Mistral uses a Mistral-7B backbone — much larger than BERT-family but better quality on long documents.

### GTE (Alibaba, 2023–2024)

GTE is BERT-family, trained on large-scale weakly-supervised data. Variants: GTE-base, GTE-large, multilingual GTE, and GTE-Qwen2 (decoder-based). It is competitive with BGE and E5. GTE-Qwen2 uses a Qwen-2 backbone — the decoder-based approach gives state-of-the-art retrieval quality at high cost.

### OpenAI text-embedding-3 (2024)

Closed-source and accessible via API. It ships as text-embedding-3-small (1536 dim) and text-embedding-3-large (3072 dim), is strong on MTEB, and supports shortening — reducing the dimension with minimal quality loss. Shortening works by projecting the 3072-dim embedding to 256/512/1024 dim via Matryoshka representation learning; the trade-off is that lower dim = faster search but lower quality.

### Cohere Embed v3

Commercial and strong on multilingual. It supports int8/binary quantization for fast search, and Embed v3 introduced an input_type parameter ("search_document", "search_query", "classification", "clustering") — the model produces different embeddings for different use cases.

### Voyage AI

Commercial and optimized for retrieval; often SOTA on MTEB. The line includes voyage-3 (1024 dim), voyage-3-large (3072 dim), and voyage-multilingual-2.

### SigLIP-2 (Google, 2025)

SigLIP-2 is the multimodal entry: it produces embeddings for both images and text in a shared space, and is used for image-text retrieval (find images matching a text query, or vice versa). It replaces CLIP for 2026 multimodal RAG systems — see [[CLIP]] for the model it displaces and [[Vision Foundation Models]] for the vision-encoder view of the same model.

### Late-interaction models (ColBERT, ColPali)

ColBERT and ColPali are a different paradigm: instead of one embedding per document, they produce one embedding per token (ColBERT) or per image patch (ColPali). Retrieval then scores max-sim over token/patch embeddings (late interaction). This is higher quality than single-vector embeddings, but more expensive — multiple vectors per doc.

## Evaluation: MTEB

**MTEB (Massive Text Embedding Benchmark)** is the standard eval. It covers retrieval (BEIR, MS MARCO), classification, clustering, STS (semantic textual similarity), reranking, and summarization.

Check the MTEB leaderboard (https://huggingface.co/spaces/mteb/leaderboard) for current SOTA. As of 2026, the leaderboard is dominated by:

- **Top open-source**: BGE-M3, GTE-Qwen2, E5-Mistral.
- **Top commercial**: Voyage-3, OpenAI text-embedding-3-large, Cohere Embed v3.

Different models win different subtasks. For pure retrieval, GTE-Qwen2 and Voyage-3 are SOTA. For multilingual, BGE-M3. For image-text, SigLIP-2. Always check the specific subtask relevant to your use case, not the aggregate score.

## Worked example: BGE

The FlagEmbedding library wraps BGE with the retrieval query prefix built in:

```python
from FlagEmbedding import FlagModel

model = FlagModel('BAAI/bge-large-en-v1.5', 
                  query_instruction_for_retrieval="Represent this sentence for searching relevant passages: ")

docs = ["The cat sat on the mat.", "Paris is the capital of France.", "Dogs love to play fetch."]
query = "Where is Paris?"

doc_embeddings = model.encode(docs)
query_embedding = model.encode_queries([query])

scores = query_embedding @ doc_embeddings.T
# Should rank "Paris is the capital of France" highest.
```

The dot product against the transposed document matrix is the entire retrieval loop at this scale. Note that the query goes through `encode_queries` rather than `encode`: BGE expects different prefixes for queries vs documents, and the library applies the query instruction for you.

## Worked example: BGE-M3 (multilingual + multi-granularity)

BGE-M3 can be driven through the same library, and its distinguishing feature is that one `encode` call returns dense, sparse, and multi-vector (ColBERT-style) outputs simultaneously:

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

docs = [
    "Paris is the capital of France.",  # English
    "巴黎是法国的首都。",  # Chinese
    "Tokyo is the capital of Japan.",  # English
]
query = "What is the capital of France?"  # English query

# BGE-M3 produces dense, sparse, and multi-vector embeddings simultaneously
output = model.encode(docs, return_dense=True, return_sparse=True, return_colbert_vecs=True)
query_output = model.encode_queries([query], return_dense=True, return_sparse=True, return_colbert_vecs=True)

# Compute scores three ways
dense_scores = model.compute_dense_score(query_output, output)
sparse_scores = model.compute_sparse_score(query_output, output)
colbert_scores = model.compute_colbert_score(query_output, output)

print("Dense scores:", dense_scores)  # for fast retrieval
print("Sparse scores:", sparse_scores)  # like BM25, good for keyword matches
print("ColBERT scores:", colbert_scores)  # late-interaction, highest quality

# Production: often combine all three (hybrid fusion)
```

An English query retrieves a Chinese document because the dense space is shared across 100+ languages; the sparse scores behave like BM25 and reward keyword matches, while the ColBERT scores give the highest quality at the highest compute.

## Choosing an embedding model

The decision is driven by hosting constraints, language coverage, and latency budget:

| Consideration             | Recommendation                              |
|---------------------------|---------------------------------------------|
| Open source / self-hosted | BGE, E5, GTE                                |
| Best quality (text)        | Check MTEB leaderboard; Voyage-3, GTE-Qwen2 |
| Multilingual              | BGE-M3, multilingual-E5, Cohere Embed       |
| Low cost / fast           | BGE-small, E5-small                         |
| Long context              | BGE-M3 (up to 8k tokens), Jina embeddings   |
| API / managed             | OpenAI, Cohere, Voyage                      |
| Image-text                | SigLIP-2 (replaces CLIP for 2026)           |
| Document retrieval        | ColPali (vision-native, no OCR)             |
| Highest retrieval quality | ColBERT v2, ColPali (late interaction)      |

Treat the table as a starting point and verify against the MTEB subtask that matches your workload before committing.

## Production implications

Ten rules of thumb cover most deployments. Start with BGE-large-en-v1.5 for English retrieval — strong, open-source, well-supported. For multilingual, use BGE-M3 or multilingual-E5. For multimodal (image + text), use SigLIP-2 — the 2026 default; CLIP is legacy. For documents (PDFs, screenshots), consider ColPali — it eliminates OCR entirely. Embedding dimension matters: larger = more expressive but slower search, and 768–1024 is the sweet spot for single-vector; multi-vector (ColBERT) is higher quality but slower. Quantize embeddings to int8 for 4x memory reduction with minimal quality loss — most vector DBs support this. Cache embeddings: re-embedding the same document is wasteful, so hash and cache. Re-embed when you change models — embeddings are model-specific and can't be mixed. Query prefix matters: many models (BGE, E5) require different prefixes for queries vs documents, so match the model's convention. Finally, Matryoshka embeddings (OpenAI text-embedding-3, Voyage-3) support dimension shortening — use this to trade off quality vs latency.

## Common pitfalls

> [!warning]
> The classic mistakes: **using a non-retrieval embedding model** (base BERT embeddings are much worse than fine-tuned BGE/E5); **forgetting the query prefix** (many models — BGE, E5 — require different prefixes for queries vs documents; match the model's convention); **wrong max sequence length** (BGE is 512; longer documents need chunking; BGE-M3 supports 8K but is slower); **mixing embedding models** (different models produce different spaces; similarities across them are meaningless); **not normalizing** (some models output normalized vectors, others don't; match the search metric — cosine vs L2); **using CLIP for 2026 multimodal RAG** (SigLIP-2 is the modern default; CLIP is legacy); **OCR + text embedding for documents** (ColPali, which is vision-native, is often better and skips OCR); and **treating embedding dimension as the only quality metric** (a 1024-dim BGE-M3 may beat a 3072-dim OpenAI embedding on specific tasks — always check MTEB for your use case).

## Modern developments (2024–2026)

### Decoder-based embedding models

2024 saw the emergence of decoder-based embedding models (E5-Mistral, GTE-Qwen2). These use a Mistral-7B or Qwen-2-7B backbone with the last hidden state as the embedding. They are much larger than BERT-family (7B vs 110M), but deliver better quality on long documents and complex queries. The trade-off: 10× slower and 10× more memory.

### BGE-M3: multi-vector + multi-lingual

BGE-M3 (2024) produces dense, sparse (BM25-like), and multi-vector (ColBERT-style) embeddings simultaneously. This enables hybrid retrieval (combine dense + sparse) without separate models, and it supports 100+ languages and up to 8K context.

### Matryoshka representation learning

OpenAI text-embedding-3 and Voyage-3 use Matryoshka embeddings — they train at multiple dimensions simultaneously (3072, 1024, 256). At inference, you can truncate to any dimension with minimal quality loss. The trade-off: lower dim = faster search but lower quality. This allows a runtime trade-off without retraining.

### SigLIP-2: multilingual image-text

SigLIP-2 (Google, 2025) is the default 2026 vision encoder for VLMs. It produces embeddings for both images and text in a shared space, and is used for image-text retrieval, multimodal RAG, and as the vision encoder in PaliGemma 2, InternVL 2.5, and LLaVA-NeXT.

### ColPali: vision-native document retrieval

ColPali (2024) eliminates OCR entirely — it embeds document pages as images and retrieves via late interaction over patches. It is faster than OCR + text retrieval and handles visual content (charts, tables, diagrams) better.

### Instruction-tuned embeddings

Models like E5-Mistral accept instructions ("find a passage that answers this question" vs "find a passage with similar topic"). The instruction shapes the embedding space, improving task-specific retrieval. The future of embedding models is instruction-aware.

## Failure modes and diagnostics

When retrieval misbehaves, the symptom usually points at one of a small set of causes:

| Symptom                                  | Likely Cause                                        | Fix                                                              |
|------------------------------------------|------------------------------------------------------|------------------------------------------------------------------|
| Low retrieval recall                     | Wrong model; or no query prefix                      | Use BGE-M3; ensure query prefix matches model convention         |
| Multilingual queries return wrong docs   | Model not multilingual                               | Switch to BGE-M3 or multilingual-E5                              |
| Long documents truncated                | Max sequence length too short                         | Use BGE-M3 (8K); or chunk long documents                          |
| Search latency too high                  | Embedding dim too large; or no quantization           | Matryoshka-shorten to 1024 dim; or quantize to int8               |
| Image-text retrieval fails              | Using text-only model for images                      | Switch to SigLIP-2 for image-text                                |
| Document retrieval quality low          | OCR errors corrupting text                            | Use ColPali (vision-native, no OCR)                              |
| Embeddings take too much memory          | Storing full precision (FP32) embeddings              | Quantize to int8; or use Matryoshka-shortened embeddings         |
| Different model embeddings mixed         | Migration bug                                         | Re-embed all documents with the new model; never mix            |
| Cosine similarity doesn't match expectation | Embeddings not normalized                          | Normalize before cosine; or use L2 distance                      |

Two rows deserve emphasis because they are silent failures: mixing embeddings from different models produces meaningless similarities and is almost always a migration bug, and unnormalized embeddings make cosine similarity lie unless you normalize first or switch to L2 distance.

## Relationship to other concepts

These models descend from the static-embedding tradition (Word2Vec, GloVe, FastText — see [[Word2Vec GloVe and FastText]]) and the contextual-embedding line that runs from ELMo to BERT (see [[Contextual Embeddings ELMo to BERT]]). In a RAG pipeline they are the retrieval half — chunking, hybrid search, and reranking consume their outputs — and their vectors are stored and searched in a vector database such as [[Vector Storage with pgvector]]. The training side (contrastive objectives, in-batch negatives, hard negatives) is covered in [[Embedding Model Training]], and the image-text branch connects to [[CLIP]], [[Vision Foundation Models]], and [[Multimodal Foundation Models]].

## Interview questions

**Why are contrastive-trained embeddings better for retrieval than base BERT embeddings?** Base BERT is trained on masked language modeling — it learns contextual token representations but no single sentence embedding. Mean-pooling BERT's token embeddings gives a sentence embedding, but the embedding space isn't optimized for semantic similarity (similar sentences can be far apart). Contrastive training (InfoNCE for CLIP, sigmoid for SigLIP) explicitly shapes the embedding space: similar (query, doc) pairs are pulled together, dissimilar pairs pushed apart. The result: cosine similarity = semantic similarity. Without contrastive training, the embedding space is "random" with respect to semantic similarity.

**When would you use ColBERT/ColPali (late interaction) over BGE (single vector)?** When retrieval quality matters more than latency/memory. Late-interaction models produce one vector per token (ColBERT) or per patch (ColPali); retrieval scores the query against each token/patch and takes the max (max-sim). This is higher quality because it preserves token-level matching (vs single-vector, which collapses all tokens into one vector). The trade-off: storage is N× larger (one vector per token vs one per doc) and search is slower (N dot products per doc vs one). Use single-vector (BGE) for high-volume retrieval; late-interaction (ColBERT/ColPali) when quality is critical and volume is moderate.

**How does BGE-M3's multi-vector output work?** BGE-M3 produces three outputs simultaneously: (1) **dense embeddings** (a single 1024-dim vector per doc — standard retrieval), (2) **sparse embeddings** (BM25-like token weights — keyword matching), (3) **ColBERT-style multi-vector** (one vector per token — late interaction). At retrieval, compute all three scores and combine via weighted fusion. This gives the best of dense (semantic), sparse (keyword), and late-interaction (high quality) retrieval without needing three separate models. In production, BGE-M3 is the default for 2026 multilingual RAG.

## Further reading

- MTEB leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- BGE paper: Xiao et al. (2023), *C-Pack: Packaged Resources To Advance General Chinese Embedding*.
- E5 paper: Wang et al. (2022), *Text Embeddings by Weakly-Supervised Contrastive Pre-training*.
- BGE-M3 paper: Chen et al. (2024), *M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings*.
- SigLIP-2 paper: Tschannen et al. (2025).
- ColPali paper: Faysse et al. (2024).

## See also

- [[Foundation Models and Multimodal MOC]] — the area orientation for this family.
- [[Embedding Model Training]] — how these models are trained.
- [[Vision Foundation Models]] — the vision-side encoders.
- [[CLIP]] — the image-text contrastive model that SigLIP-2 replaces.
- [[Multimodal Foundation Models]] — the multimodal family.
- [[Multimodal AI Overview]] — where image-text retrieval fits.
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the backbone architecture.
- [[Contextual Embeddings ELMo to BERT]] — the encoder lineage.
- [[Word2Vec GloVe and FastText]] — the static-embedding ancestors.
- [[Vector Storage with pgvector]] — the storage layer for these embeddings.
