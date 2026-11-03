---
title: Vector Memory Backends
type: concept
aliases: ["Vector Databases for Agents", "vector database", "vector store", "vector DB"]
tags: [memory, vector-db, pgvector, pinecone, qdrant, hybrid-search, ann, quantization]
sources: ["04 - Vector Memory Backends"]
created_index: 30
---

Vector databases store embeddings for semantic search, and they are the storage foundation of both RAG pipelines and agent memory. The major options in 2024–2026 are pgvector (a Postgres extension — the simplest, most integrated choice), Pinecone (managed SaaS with zero ops), Qdrant (open-source, Rust-based, fast), Weaviate (open-source, with a GraphQL API), and Milvus (open-source, scaling to billions of vectors). The right choice depends on scale, ops capacity, and integration needs. This note covers why vector databases exist, the major options and their trade-offs, the indexing algorithms underneath them, hybrid search, multi-tenancy, production considerations, and the failure modes that show up in real deployments.

## Why vector databases exist

Semantic search requires comparing the meaning of text, not just keywords. This is done by embedding text into high-dimensional vectors (typically 768–3072 dimensions) and computing similarity (cosine similarity, dot product) between vectors. Vectors close in embedding space correspond to text with similar meaning.

The problem: storing and searching millions of vectors is not what relational databases are built for. Brute-force search — computing similarity to every vector — is O(N), which is too slow at scale. Vector databases use **approximate nearest neighbor (ANN)** algorithms to search in O(log N) or better. They index vectors using structures like HNSW (Hierarchical Navigable Small World), IVF (Inverted File), or PQ (Product Quantization) to trade a small amount of recall for a massive speedup.

## The major options

Five databases cover the bulk of production deployments, each with a distinct sweet spot in the space of scale, operational capacity, and integration needs.

### pgvector

pgvector is a Postgres extension that adds a `vector` type and vector indexing, so you store embeddings alongside relational data in the same database.

Its strengths are that it is integrated with Postgres (no separate database to operate), it provides ACID transactions across relational and vector data, it has a mature ecosystem (any ORM that supports Postgres supports pgvector), it enables hybrid search that combines vector similarity with SQL filters (e.g., "find similar documents in tenant X created after date Y"), and its performance is good enough for most use cases (millions of vectors).

Its weaknesses are that it is not as fast as dedicated vector DBs at very large scale (100M+ vectors), index rebuilds can be slow, and its ANN algorithm choices are limited (HNSW, IVFFlat).

When to use it: most production agent memory systems, RAG with fewer than 10M vectors, and any system already using Postgres.

### Pinecone

Pinecone is a managed SaaS vector database. You create an index, upload vectors, and query by API — there is no infrastructure to operate.

Its strengths are zero ops (Pinecone handles scaling, replication, and backups), speed (low latency, high throughput), a serverless option (pay per query), built-in metadata filtering, and a mature, well-documented API.

Its weaknesses are that it is closed source (vendor lock-in), cost scales with usage and can be expensive at high query volumes, data must leave your infrastructure (a compliance concern for some industries), and you have limited control over indexing parameters.

When to use it: teams without DBA capacity, prototypes that need to scale fast, and workloads where the convenience justifies the cost.

### Qdrant

Qdrant is an open-source vector database written in Rust, available self-hosted or as a managed cloud.

Its strengths are speed (Rust, no GC pauses), rich filtering (payload filtering with complex conditions), support for sparse vectors (BM25-like) alongside dense vectors — useful for hybrid search — good documentation and an active community, and both self-hosted and managed options.

Its weaknesses are that it is newer than Pinecone with a smaller ecosystem, and its tooling is less mature than pgvector's Postgres ecosystem.

When to use it: teams that want open-source with strong performance, hybrid search needs, or self-hosting requirements.

### Weaviate

Weaviate is an open-source vector database with GraphQL and REST APIs, self-hosted or managed cloud.

Its strengths are built-in modules for common embedding models (OpenAI, Cohere, HuggingFace) that embed automatically on insert, a GraphQL API for complex queries, hybrid search (keyword + vector) out of the box, multi-tenancy support (each tenant gets isolated collections), and generative capabilities (built-in RAG patterns).

Its weaknesses are that it is more complex to operate than Qdrant, the GraphQL API has a learning curve, and its performance is slightly behind Qdrant in benchmarks.

When to use it: teams that want built-in embedding + RAG patterns and multi-tenant SaaS applications.

### Milvus

Milvus is an open-source vector database designed for very large scale (billions of vectors), self-hosted or as managed cloud (Zilliz).

Its strengths are that it scales to billions of vectors, it supports multiple index types (HNSW, IVF, DiskANN, etc.), it has a distributed architecture (sharding, replication), and it separates storage from compute.

Its weaknesses are that it is complex to operate (multiple components: proxy, query node, data node, etc.), it is overkill for most use cases (if you have fewer than 100M vectors, Milvus is more than you need), and it has a steeper learning curve.

When to use it: very large-scale deployments (100M+ vectors) and specialized vector search workloads.

### At a glance

The first-generation comparison comes down to open-source posture, managed availability, scale ceiling, hybrid search, and multi-tenancy:

| Database  | Open Source | Managed | Scale      | Hybrid Search | Multi-Tenant | Best For                          |
|-----------|-------------|---------|------------|---------------|--------------|-----------------------------------|
| pgvector  | Yes         | Many    | <100M      | Yes (SQL)     | Yes (RLS)    | Most production systems           |
| Pinecone  | No          | Yes     | Any        | Yes           | Yes          | Zero-ops teams                    |
| Qdrant    | Yes         | Yes     | <1B        | Yes (sparse)  | Yes          | Performance-focused, self-host    |
| Weaviate  | Yes         | Yes     | <1B        | Yes           | Yes          | Built-in RAG, multi-tenant SaaS   |
| Milvus    | Yes         | Zilliz  | Billions   | Yes           | Yes          | Very large scale                  |

## Indexing algorithms

The choice of indexing algorithm affects speed, recall, and memory, and each algorithm occupies a different point on that trade-off surface.

### HNSW (hierarchical navigable small world)

HNSW is a graph-based index. It builds a multi-layer graph where each node is a vector and edges connect similar vectors. Search traverses the graph from a random entry point, greedily moving toward the query.

- **Speed**: very fast (sub-millisecond at moderate scale).
- **Recall**: high (>95% at typical parameters).
- **Memory**: high (the graph is in memory).
- **Build time**: slow (the graph is expensive to construct).

HNSW is the default in pgvector, Qdrant, Weaviate, and most modern vector DBs. It is the right choice for most use cases.

### IVF (inverted file)

IVF partitions vectors into clusters. At search time, only the clusters closest to the query are scanned.

- **Speed**: fast.
- **Recall**: moderate (depends on how many clusters you scan).
- **Memory**: lower than HNSW.
- **Build time**: fast.

IVF is older than HNSW and mostly superseded, but it is still useful for very large datasets where HNSW's memory footprint is prohibitive.

### Product quantization

PQ compresses vectors by dividing them into sub-vectors and quantizing each one, reducing memory by 8–64× at the cost of some recall.

- **Speed**: very fast (compressed vectors are fast to scan).
- **Recall**: lower than HNSW/IVF.
- **Memory**: very low.

PQ is used for very large datasets where memory is the constraint, and it is often combined with IVF (IVF-PQ).

### DiskANN

DiskANN is a disk-based index. It stores vectors on disk with a small in-memory graph for navigation, which enables searching datasets larger than RAM.

- **Speed**: slower than in-memory indexes (disk I/O).
- **Recall**: high.
- **Memory**: low (only the graph is in memory).

DiskANN is used for very large datasets that don't fit in RAM. Milvus supports it, and other DBs are adding support.

## Hybrid search

Pure vector search misses exact matches — entity names, IDs, and code identifiers don't survive embedding. Hybrid search combines two complementary signals:

- **Dense vector search**: semantic similarity.
- **Sparse vector / keyword search**: exact matches, BM25-style.

Most modern vector DBs support hybrid search: pgvector combines with Postgres full-text search, Qdrant has native sparse vectors, Weaviate has built-in hybrid search, and Pinecone supports it via sparse-dense hybrid.

For agent memory and RAG, hybrid search is typically better than pure vector search — it catches both semantic and lexical matches. The same techniques are covered in [[Chunking, Hybrid Search, and Reranking]].

## Multi-tenancy

For SaaS applications, each tenant's data must be isolated. The main isolation patterns, from strongest to weakest:

- **Database per tenant**: strongest isolation, highest overhead.
- **Schema per tenant**: good isolation, moderate overhead (Postgres schema).
- **Collection per tenant**: vector DB native (Weaviate and Qdrant support this).
- **Row-level filtering**: weakest isolation, lowest overhead (pgvector with `WHERE tenant_id = ?`).

For most SaaS applications, row-level filtering with proper indexing — and ideally database-level row-level security — is sufficient. Stronger isolation is needed for regulated industries or when tenants genuinely cannot share infrastructure.

## Production considerations

### The embedding pipeline

Storing a vector requires embedding the text first, which brings several decisions. The **embedding model** (OpenAI text-embedding-3-small/large, BGE, E5, GTE) affects dimensionality, quality, and cost. **Embedding cost** runs $0.02–$0.13 per 1M tokens (OpenAI), which adds up for large corpora. **Embedding version** matters because changing models means you must re-embed everything — maintain a versioning scheme. And **async embedding** (embedding in a background job via Celery or SQS) avoids blocking writes.

### Index maintenance

HNSW parameters `m` (graph connectivity) and `ef_construction` (build-time search depth) affect quality and build time — tune them for your dataset. As you add vectors, the index degrades, so periodic rebuilds maintain quality. Deleted vectors leave gaps; vacuum reclaims the space.

### Replication and backup

Most vector DBs support replication for high availability. Snapshot the database regularly — for pgvector this is just Postgres backup, and for others use the DB's snapshot mechanism. For disaster recovery, test restore procedures: a backup you haven't restored is not a backup.

### Monitoring

Watch **query latency** (p50, p95, p99 — slow queries indicate index degradation), **recall** (sample queries with known good results and check that the index returns them), **index size** (track growth; unexpected growth may indicate a write bug), and **throughput** (queries per second, for capacity planning).

## Common pitfalls

### Wrong embedding model

Using an old or poor embedding model caps everything downstream: the model determines the upper bound of search quality. Use a current, well-evaluated model (BGE-large, OpenAI text-embedding-3, etc.).

### No hybrid search

Pure vector search misses exact matches. Always combine it with keyword search for production systems.

### No metadata filtering

Searching all vectors when you only need a subset wastes enormous resources. Always filter by tenant, time, and tags — without filtering, you search 100M vectors when you needed 10K.

### Stale embeddings

Changing embedding models without re-embedding breaks retrieval: old vectors live in the old embedding space while new queries use the new one, so they don't match. Either re-embed everything or maintain parallel indexes during migration.

### No recall monitoring

Recall degrades silently as the index grows, and without monitoring you discover it when users complain. Sample queries with known good results and alert on recall drops.

### Over-indexing

Creating too many indexes — different embedding models, different parameters — costs storage and write throughput for each one. Pick one good index and use it.

## Modern developments (2024–2026)

### Multi-vector and late-interaction indexes

The ColBERT pattern (part of the [[BLIP-2]]-era multi-vector work) is now mainstream: each document is tokenized into N tokens, each token gets its own embedding, and retrieval uses **MaxSim** (sum of max similarities per query token) instead of a single dot product. Vespa, Weaviate, and a new wave of dedicated late-interaction stores (e.g., Colin, LightOn's successors) support this natively. Multi-vector indexes are 5–10x larger than single-vector but achieve 10–20% higher nDCG on retrieval benchmarks.

### Quantized vector indexes

Production vector DBs now universally support three families of quantization:

- **Product Quantization (PQ)**: split a 1024-dim vector into 16 sub-vectors of 64 dims each; quantize each sub-vector to 8 bits via codebook. 16x compression with ~3% recall loss.
- **Scalar Quantization (SQ)**: convert fp32 → int8. 4x compression, ~1% recall loss.
- **Binary quantization**: convert to 1-bit per dim. 32x compression, ~5–10% recall loss. Combined with **re-scoring** (retrieve 10x candidates with binary, re-score top-K with full fp32), it reaches 99% of full-precision recall at 1/30th the storage cost.

Qdrant's `BinaryQuantization` and pgvector's `bit` indexes (0.7+) made this mainstream for billion-scale deployments.

### Disk-based ANN indexes

For trillion-scale corpora that don't fit in RAM, **DiskANN** (Microsoft) and **SPANN** (Microsoft) keep the search graph on SSD and only load graph nodes on demand. Latency is 5–20ms (vs 1–5ms for in-memory HNSW), but at 1/100th the cost. They are used by Bing, Apple, and major RAG platforms. The trade-off is acceptable for archival memory tiers where latency budgets are 50ms+.

### Hybrid search becomes the default

Pure vector search is now considered an anti-pattern for production. The 2025 consensus is **hybrid search**: combine BM25 (lexical) + vector (semantic) with reciprocal rank fusion (RRF). Most vector DBs ship this natively (Weaviate 1.25+, Qdrant 1.8+, pgvector + tsvector). Open-source libraries like `mixedbread-ai/rerank` and `cohere-ai/rerank` add a cross-encoder reranking step that boosts precision another 5–10%.

### Serverless vector databases

Pinecone Serverless (2024) introduced a storage/compute separation for vector indexes — you pay for storage ($0.10/GB/month) and query compute (per-100k-queries) separately. This dropped costs 10–50x for sparse workloads. Weaviate, Qdrant Cloud, and Turbopuffer followed. For RAG systems with bursty traffic, serverless is now the default.

### Vector indexes in Postgres

pgvector 0.7+ added **HNSW** indexes (in addition to IVFFlat), **half-vec** (16-bit floats, 2x compression), and **binary quantization** with re-scoring. For applications already on Postgres, pgvector is now the recommended default — no need for a separate vector DB until you hit ~100M vectors or strict latency SLAs.

### Specialized indexes for embedding model migrations

The "embedding model upgrade" problem — you change embedders and all your old vectors are stale — is now solved by three techniques. **Multi-index serving** keeps the old index for a transition period, queries both, and merges results. **On-demand re-embedding** lazily re-embeds documents as they're accessed. **Adapter networks** train a small neural net to map old embeddings → new embeddings, avoiding full re-embedding; Cohere, OpenAI, and Voyage AI all publish adapter recipes for their embedder upgrades.

## Production vector databases in 2026

By 2026 the landscape extends well beyond the original five: Vespa, Chroma, LanceDB, and Turbopuffer join pgvector, Pinecone, Qdrant, Weaviate, and Milvus, and the differentiators have shifted toward index type, multi-vector support, and serverless pricing.

| System       | Index Type                | Hybrid Search | Multi-Vector | Serverless | Open Source | Best For                                       |
|--------------|---------------------------|---------------|--------------|------------|-------------|------------------------------------------------|
| pgvector     | HNSW, IVFFlat             | Via tsvector  | Limited      | Via cloud PG | Yes       | Apps already on Postgres; <100M vectors        |
| Pinecone     | Proprietary (graph + PQ)  | Yes           | Yes          | Yes        | No          | Managed serverless; enterprise; zero ops       |
| Qdrant       | HNSW + scalar/binary Q    | Yes           | Yes          | Via cloud  | Yes         | Self-hosted with rich filtering; cost-sensitive |
| Weaviate     | HNSW                      | Yes (BM25 + vector) | Yes     | Yes        | Yes         | Schema-first; module ecosystem (multi-modal)   |
| Milvus       | HNSW, IVF, DiskANN, SCANN | Yes           | Yes          | Via Zilliz | Yes         | Billion-scale; on-prem enterprise              |
| Vespa        | HNSW + tensor fields      | Yes           | Yes (late-int) | Via cloud | Yes       | Real-time + complex ranking + huge scale       |
| Chroma       | HNSW                      | Limited       | No           | Via cloud  | Yes         | Prototyping; small datasets                    |
| LanceDB      | IVF + PQ                  | Yes           | Yes          | Embedded   | Yes         | Embedded (no server); multimodal; lakehouse    |
| Turbopuffer  | Disk-based HNSW           | Yes           | Yes          | Yes        | No          | Cost-optimized serverless on S3                |

## Worked example: production vector memory with pgvector

The schema pairs an HNSW-indexed half-precision embedding column with metadata, full-text search, and tenant columns:

```sql
-- Schema with HNSW index + hybrid search
CREATE TABLE memories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    tenant_id   UUID NOT NULL,
    content     TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}',
    embedding   halfvec(1024) NOT NULL,  -- half-precision: 2x smaller than vector
    confidence  REAL NOT NULL DEFAULT 1.0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    access_count INT NOT NULL DEFAULT 0,
    superseded_by UUID REFERENCES memories(id)
);

-- HNSW index for fast ANN search (half-vec + binary quantization)
CREATE INDEX ON memories USING hnsw (embedding halfvec_l2_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN index for metadata filtering
CREATE INDEX ON memories USING gin (metadata);
CREATE INDEX ON memories USING btree (tenant_id, user_id, last_accessed_at DESC);

-- Full-text search index for BM25 (hybrid search)
ALTER TABLE memories ADD COLUMN tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX ON memories USING gin (tsv);
```

The query path runs BM25 and vector search in parallel and fuses them with reciprocal rank fusion:

```python
import asyncpg
import numpy as np

async def search_memories(
    pool, user_id: str, tenant_id: str, query: str,
    query_embedding: np.ndarray, limit: int = 10,
    metadata_filter: dict = None, time_filter_days: int = None,
) -> list[dict]:
    """Hybrid search: BM25 + vector, fused with reciprocal rank fusion."""
    async with pool.acquire() as conn:
        # Step 1: BM25 (lexical) search — top 50
        bm25_sql = """
            SELECT id, content, metadata, ts_rank(tsv, plainto_tsquery($1)) AS bm25_score
            FROM memories
            WHERE tenant_id = $2 AND user_id = $3
              AND tsv @@ plainto_tsquery($1)
              AND superseded_by IS NULL
            ORDER BY bm25_score DESC
            LIMIT 50
        """
        bm25_results = await conn.fetch(bm25_sql, query, tenant_id, user_id)

        # Step 2: Vector (semantic) search — top 50 with binary quantization + re-score
        vec_sql = """
            SELECT id, content, metadata,
                   embedding <=> $1::halfvec AS distance
            FROM memories
            WHERE tenant_id = $2 AND user_id = $3
              AND superseded_by IS NULL
              AND ($4::int IS NULL OR created_at > now() - ($4::int || ' days')::interval)
            ORDER BY embedding <=> $1::halfvec
            LIMIT 50
        """
        vec_results = await conn.fetch(
            vec_sql,
            asyncpg.Record(query_embedding.tolist()),
            tenant_id, user_id, time_filter_days,
        )

        # Step 3: Reciprocal Rank Fusion (RRF)
        rrf_k = 60  # standard constant
        scores = {}
        for rank, r in enumerate(bm25_results, start=1):
            scores[r['id']] = scores.get(r['id'], 0) + 1.0 / (rrf_k + rank)
        for rank, r in enumerate(vec_results, start=1):
            scores[r['id']] = scores.get(r['id'], 0) + 1.0 / (rrf_k + rank)

        # Step 4: Top-K by fused score
        top_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
        results_by_id = {r['id']: r for r in [*bm25_results, *vec_results]}
        return [dict(results_by_id[i]) | {'fused_score': scores[i]} for i in top_ids]
```

Several production patterns are visible in this example. **Half-precision embeddings** (`halfvec`) cut index size 2x with negligible recall loss. **Hybrid search via RRF** combines lexical and semantic signals without retraining. **Tenant isolation via WHERE clauses** is applied to every query, with row-level security as defense in depth. **Pre-filtering** by `superseded_by IS NULL` avoids retrieving historical memories. And **asyncpg** provides connection pooling and concurrent queries in production.

## Common failure modes

Most production incidents trace back to a handful of root causes. The diagnostic table below maps the symptoms operators actually observe to their likely cause and the corresponding fix.

| Symptom                                | Likely Cause                                  | Fix                                                          |
|----------------------------------------|-----------------------------------------------|--------------------------------------------------------------|
| Recall drops after embedder upgrade    | Old vectors in old space; new queries in new  | Multi-index serving + lazy re-embedding; or train adapter   |
| Search latency 10x higher than expected| HNSW ef_search too high; or no quantization   | Tune ef_search (start 64); enable PQ or binary quantization |
| Index build takes hours                | ef_construction too high; single-threaded     | Lower ef_construction (64→32); parallelize build            |
| OOM on bulk insert                     | Building HNSW on huge batch in RAM            | Stream inserts in batches of 10k; build index after         |
| Metadata filter ignored                | Filter applied post-retrieval, not pre-       | Use vector DB's pre-filter API (Qdrant `filter`, Weaviate `where`) |
| Empty results on exact entity match    | Pure vector search misses exact strings       | Use hybrid (BM25 + vector); add entity aliases              |
| Index size > 10x raw data              | No quantization; ef_construction too high     | Apply PQ (16x compression); tune HNSW m (16→8)              |
| Tenant A sees tenant B's memories      | Missing tenant_id in WHERE clause             | Use RLS policies; CI test for cross-tenant leaks            |
| Re-embedding the whole DB on upgrade   | No versioning on embedding model              | Track `embedder_version` column; query with right model     |
| Slow at 1B+ vectors                    | HNSW in-memory; can't fit                     | Migrate to DiskANN / SPANN; or shard by tenant               |

## Interview questions

**When would you choose pgvector over a dedicated vector DB like Pinecone?** Choose pgvector when (1) you're already on Postgres and want one fewer system to operate; (2) you need strong transactional consistency between relational data and vectors (e.g., memories with foreign keys to user records); (3) your corpus is <100M vectors and your SLA is <50ms p99. Choose Pinecone (or Qdrant Cloud, Weaviate Cloud) when (1) you need managed serverless with zero ops; (2) you're at 1B+ vectors; (3) you need advanced features like multi-vector or late-interaction retrieval that pgvector lacks.

**Explain HNSW vs IVF — when do you use each?** HNSW (Hierarchical Navigable Small World) builds a multi-layer graph; queries traverse from a sparse top layer down to a dense bottom layer. It offers O(log n) query time, O(n log n) build time, and high RAM usage (graph + vectors in memory) — best for <100M vectors with tight latency SLAs. IVF (Inverted File) clusters vectors into Voronoi cells via k-means; queries probe the nearest N cells. It has lower RAM and lower build time, but lower recall at the same latency — best for 100M–1B vectors or when memory is constrained. Many DBs (Milvus, pgvector) support both; use HNSW for hot tiers and IVF for warm tiers.

**How does binary quantization with re-scoring work, and what's the trade-off?** Each fp32 component of the vector is replaced with 1 bit (the sign of the component). The 1024-dim fp32 vector (4KB) becomes a 1024-bit binary vector (128B) — 32x smaller. Hamming distance on binary vectors is dramatically faster (XOR + popcount, SIMD-parallel). At query time, retrieve 10x the desired K using fast binary search, then **re-score** those candidates with full fp32 dot products. The result: 99% of full-precision recall at 30x lower storage and 5x lower latency. The trade-off is implementation complexity — you need to store both binary and full-precision vectors (or re-compute on demand).

**How do you handle embedding model migrations in production?** Three approaches, in increasing order of complexity: (1) **big-bang re-embedding** — take downtime, re-embed everything, swap indexes; simple but disruptive, and it only works for small corpora. (2) **Dual-index serving** — keep the old index running, build a new index in parallel, query both with RRF, and slowly migrate traffic to the new index; zero downtime, but 2x query cost during migration. (3) **Adapter network** — train a small MLP that maps old embeddings → new embeddings, applied at query time (transform the new query into the old space) or at index time (transform old vectors into the new space); cheapest, but it requires training data (pairs of old + new embeddings on the same text).

**What's reciprocal rank fusion (RRF) and why is it the standard for hybrid search?** RRF combines ranked result lists from multiple retrievers (e.g., BM25 + vector) using the formula `score(d) = sum over retrievers of 1 / (k + rank_retriever(d))` where `k ≈ 60`. RRF has three properties that make it the default: (1) it doesn't require score calibration across retrievers (BM25 scores and cosine similarities aren't comparable); (2) it's robust to outliers (a single retriever's high score can't dominate); (3) it's parameter-light (only `k` to tune). Most vector DBs ship RRF natively, and it consistently beats single-retriever baselines by 5–15% on nDCG.

**How would you design a multi-tenant vector memory system with strict isolation?** Four layers of isolation: (1) **Logical** — every row has `tenant_id`, all queries filter on it, and CI tests check for cross-tenant leakage. (2) **Schema** — separate schemas per tenant (Postgres) or separate collections (Qdrant) for high-value tenants. (3) **Physical** — separate databases/clusters for the largest tenants, with a shared cluster for small ones. (4) **Crypto** — encrypt memory at rest with per-tenant keys (envelope encryption via AWS KMS); keys are never co-located with data. Combine this with RLS policies (defense in depth), audit logging of every query, and quarterly penetration tests for cross-tenant access.

## Relationship to other concepts

[[Memory Types]] describes what gets stored in vector memory, and [[MemGPT and Letta]] uses vector databases as the archival memory backend. The write/read/decay/forget operations described in [[Memory Operations]] map onto vector DB CRUD plus scheduled jobs. The same hybrid search techniques are covered in [[Chunking, Hybrid Search, and Reranking]]; [[RAG Pipeline Overview]] shows where vector databases sit in a retrieval pipeline, and [[Advanced RAG Patterns]] builds on both. Embedding model selection drives index design ([[Embedding Models for Retrieval]]), and embedding model upgrades trigger re-indexing ([[Embedding Model Training]]). PII in memory must be encrypted and filtered ([[PII and Data Leakage]]), and PQ/SQ/binary quantization share theory with model quantization ([[Quantization]]).

## See also

- [[Agents and Tooling MOC]] — the area orientation for agents and tooling.
- [[Memory Types]] — what gets stored in vector memory.
- [[Memory Operations]] — write/read/decay/forget map to vector DB CRUD.
- [[MemGPT and Letta]] — uses vector DBs as the archival memory backend.
- [[Chunking, Hybrid Search, and Reranking]] — the search techniques used on top of vector stores.
- [[RAG Pipeline Overview]] — vector DBs in RAG.
- [[Advanced RAG Patterns]] — retrieval patterns built on vector stores.
- [[Embedding Models for Retrieval]] — model selection drives index design.
- [[Embedding Model Training]] — model upgrades trigger re-indexing.
- [[Quantization]] — PQ/SQ/binary quantization share theory with model quantization.
- [[PII and Data Leakage]] — PII in memory must be encrypted and filtered.
