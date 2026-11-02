---
title: Vector Storage with pgvector
type: concept
aliases: ["pgvector", "pgvector Deep Dive", "PostgreSQL for AI", "Vector Storage with pgvector"]
tags: [infrastructure, postgres, pgvector, vector-storage, hybrid-search, rag]
sources: ["02 — Vector Storage with pgvector"]
created_index: 5
---

pgvector is a PostgreSQL extension that adds a native `vector` column type and approximate-nearest-neighbor (ANN) indexing, so embeddings can live inside the same database as everything else an application stores. For AI workloads such as retrieval-augmented generation, agent memory, and semantic search, this removes an entire class of infrastructure — no separate vector database, no cross-store synchronization, and hybrid queries written in plain SQL. This note, part of the [[Inference and Production MOC]] area, covers why colocation matters, setup and query patterns, indexing choices, performance characteristics, and the operational practices that keep a pgvector-backed service healthy in production.

> [!info] TL;DR
> pgvector is a Postgres extension that adds a `vector` type and ANN indexing (HNSW, IVFFlat). For most AI applications — agent memory, RAG, semantic search — pgvector is the right default: it stores vectors alongside relational data, supports ACID transactions, and uses SQL for hybrid search. It scales comfortably to ~100M vectors per index, beyond which dedicated vector DBs become preferable.

## Why pgvector

The traditional split between relational data and vector data created friction: user profiles, document metadata, and audit logs live in Postgres, while embeddings for semantic search lived in a separate vector DB (Pinecone, Qdrant). Joining the two required application-level coordination, fragile sync, and dual-write consistency issues.

pgvector eliminates this split. Vectors live in the same Postgres tables as the rest of your data, which means you can join vectors with relational data in a single query, run ACID transactions across both, and keep using Postgres's mature ecosystem of ORMs, backups, replication, and monitoring.

For most production AI workloads, pgvector is the right default. It is not the fastest at extreme scale, but it is the simplest to operate and the most flexible — where that trade-off finally flips is covered in "when to choose a dedicated vector DB" below.

## Setup

Enabling the extension and declaring a typed vector column is all it takes to turn an ordinary table into a searchable embedding store. A representative schema for document search:

```sql
-- Install the extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table with a vector column
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,  -- OpenAI text-embedding-3-small dimension
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Create an HNSW index for fast ANN search
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Create a B-tree index for tenant filtering
CREATE INDEX ON documents (tenant_id, created_at);
```

The `embedding VECTOR(1536)` column fixes the vector dimensionality — 1536 matches the OpenAI `text-embedding-3-small` model named in the comment — and the vector type enforces that dimensionality at insert. The `vector_cosine_ops` operator class on the HNSW index specifies cosine similarity; the other options are `vector_l2_ops` (Euclidean distance) and `vector_ip_ops` (inner product). The companion B-tree index on `(tenant_id, created_at)` exists for metadata filtering, which the hybrid queries below rely on.

## Queries

### Semantic search

The core query finds the nearest neighbors of a query embedding and converts cosine distance into a similarity score:

```sql
-- Find the 10 most similar documents to a query embedding
SELECT id, title, content, 1 - (embedding <=> $1) AS similarity
FROM documents
ORDER BY embedding <=> $1
LIMIT 10;
```

The `<=>` operator is cosine distance; `<->` is L2 distance, and `<#>` is negative inner product. Subtracting the cosine distance from 1 turns it into the similarity score the query reports.

### Hybrid search (vector + metadata filter)

Filtering by tenant or date before ranking shows the advantage of keeping vectors and their metadata in one place:

```sql
-- Find similar documents, filtered by tenant and date
SELECT id, title, content, 1 - (embedding <=> $1) AS similarity
FROM documents
WHERE tenant_id = $2
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY embedding <=> $1
LIMIT 10;
```

Postgres's query planner combines the HNSW index (vector search) with the B-tree index (metadata filter) efficiently. This is one of pgvector's biggest advantages — hybrid search is just SQL.

### Hybrid search (vector + full-text)

Vector and keyword signals can also be fused inside a single statement:

```sql
-- Combine vector similarity with keyword search
WITH vector_results AS (
    SELECT id, 1 - (embedding <=> $1) AS vector_score
    FROM documents
    ORDER BY embedding <=> $1
    LIMIT 100
),
keyword_results AS (
    SELECT id, ts_rank_cd(search_vector, query) AS keyword_score
    FROM documents, plainto_tsquery('english', $2) query
    WHERE search_vector @@ query
    LIMIT 100
)
SELECT d.id, d.title, d.content,
       (vr.vector_score * 0.7 + COALESCE(kr.keyword_score, 0) * 0.3) AS combined_score
FROM documents d
LEFT JOIN vector_results vr ON d.id = vr.id
LEFT JOIN keyword_results kr ON d.id = kr.id
WHERE vr.id IS NOT NULL OR kr.id IS NOT NULL
ORDER BY combined_score DESC
LIMIT 10;
```

This is the "reciprocal rank fusion" or weighted-score approach to hybrid search. Each candidate's vector score is blended with its keyword score — weighted 0.7 and 0.3 here, with `COALESCE` absorbing documents found by only one of the two channels — combining semantic (vector) and lexical (full-text) signals for better recall than either alone.

## Indexing choices

pgvector ships two ANN index types, and the choice between them is a trade-off between build cost, memory, and recall.

### HNSW (recommended default)

HNSW builds a graph where each node is a vector and edges connect similar vectors; a search traverses the graph greedily from a random entry point. Two parameters govern construction: `m` (default 16) sets graph connectivity — higher means better recall and more memory — and `ef_construction` (default 64) sets build-time search depth — higher means better recall and a slower build. A third knob, `ef_search` (default 40), is set per query rather than at build time; raising it buys better recall at the price of slower queries.

HNSW is the right choice for most workloads. It gives >95% recall at sub-millisecond latency for moderate-scale datasets.

### IVFFlat

IVFFlat partitions vectors into clusters, and a search scans only the closest clusters. Its `lists` parameter sets the number of clusters — the rule of thumb is `sqrt(rows)` — and `probes` sets how many clusters each query scans, where higher values mean better recall and slower queries. IVFFlat is faster to build than HNSW but gives lower recall at the same latency. Use IVFFlat only if HNSW build time or memory is prohibitive.

### When to use no index

For very small tables (<10K rows), a sequential scan with vector distance computation is faster than index traversal. Skip the index until you have enough data to justify it.

## Performance considerations

The numbers in this section are rules of thumb for typical deployments; treat them as planning anchors rather than guarantees.

### Index build time

HNSW builds are expensive. For 1M vectors of 1536 dimensions, expect a build time of 5–30 minutes depending on hardware and parameters, and 2–4 GB of memory during the build. For large datasets, build the index on a replica or during a maintenance window.

### Memory usage

HNSW indexes are in-memory. A 1536-dimension vector is 6 KB (float4), so 1M vectors occupy 6 GB raw; the HNSW graph overhead adds ~30% on top, for a total of ~8 GB. Postgres's shared buffers must be large enough to hold the index for good performance — if the index spills to disk, latency explodes.

### Query latency

Typical latency on commodity hardware (8 vCPU, 32 GB RAM) scales with the number of indexed vectors:

| Vectors | Typical latency |
|---|---|
| 10K | <1 ms |
| 100K | 1–5 ms |
| 1M | 5–20 ms |
| 10M | 20–100 ms (consider dedicated vector DB) |

The last row is where a dedicated vector database stops being a theoretical concern.

### Throughput

A single Postgres instance handles ~100–1000 queries per second on vector search, depending on index size and hardware. For higher throughput, use read replicas or a dedicated vector DB.

## Operational patterns

### Embedding pipeline

Store embeddings alongside the data they describe, but compute them asynchronously:

```text
# On insert, just store the text
INSERT INTO documents (title, content) VALUES (?, ?) RETURNING id;

# Async job computes and updates the embedding
async def embed_document(doc_id):
    doc = await get_document(doc_id)
    embedding = await openai.embeddings.create(input=doc.content, model="text-embedding-3-small")
    await db.execute("UPDATE documents SET embedding = $1 WHERE id = $2", embedding, doc_id)
```

This decouples insert latency from embedding cost: the insert returns immediately with just the text stored, and a background job computes the vector and writes it back. Use Celery, SQS, or a similar queue to drive that job — the same asynchronous-messaging tooling discussed in [[Messaging with Kafka and Celery]].

### Embedding versioning

When you change embedding models, old embeddings are invalid (they live in a different vector space). Track the embedding version so old and new vectors can be told apart:

```sql
ALTER TABLE documents ADD COLUMN embedding_model TEXT;
ALTER TABLE documents ADD COLUMN embedding_version INT;

-- During migration, re-embed documents with the new model
UPDATE documents SET embedding = $1, embedding_version = 2 WHERE id = $2;
```

Filter by version in queries to avoid mixing old and new embeddings.

### Tenant isolation

For multi-tenant SaaS, use Postgres row-level security:

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT);
```

Each request sets `app.tenant_id` at the start of the transaction, and Postgres automatically filters all queries. This is stronger isolation than application-level filtering, which is bug-prone.

### Backup and recovery

pgvector data is just Postgres data. Standard Postgres backup tools (`pg_dump`, `pg_basebackup`, WAL archiving, point-in-time recovery) work without modification. This is a significant advantage over dedicated vector DBs, which require their own backup tooling.

### Monitoring

Four signals catch most pgvector problems early, and they slot naturally into a broader [[Observability Stack]]:

- **Index size** — track growth; unexpected growth may indicate a write bug.
- **Query latency** — p50, p95, and p99; slow queries indicate index degradation or insufficient memory.
- **Cache hit ratio** — from `pg_stat_user_indexes`; a low ratio suggests the index doesn't fit in memory.
- **Recall** — sample queries with known-good results and alert on recall drops.

Index size and cache hit ratio expose memory pressure before it turns into a latency incident, while the recall check guards against silent degradation of the ANN index itself.

## Common pitfalls

Most pgvector failures trace back to a mismatch between how vectors were stored and how they are queried.

### Wrong distance metric

Using cosine distance when you stored L2-normalized vectors (or vice versa). Pick one and be consistent — for most text embeddings, cosine distance is the right choice.

### No tenant filter

Searching all tenants' vectors when you only need one. Always filter by `tenant_id` in the WHERE clause — Postgres will use the B-tree index to prune before the HNSW search.

### Stale embeddings

Changed embedding models without re-embedding. Old vectors don't match new queries. Track embedding version; re-embed during migration.

### Index not in memory

An HNSW index spilled to disk due to small `shared_buffers`. Latency explodes when it does. Size `shared_buffers` to fit the index, or use a dedicated vector DB.

### No hybrid search

Pure vector search misses exact matches — entity names, IDs, code identifiers. Always combine with full-text or keyword search.

### Wrong dimensionality

Storing 768-dimensional vectors in a `VECTOR(1536)` column (or vice versa). The vector type enforces dimensionality at insert — make sure it matches your embedding model.

## When to choose a dedicated vector DB

pgvector is the right default, but switch to a dedicated vector DB (Qdrant, Milvus, Pinecone) when:

- You have >100M vectors and HNSW memory becomes prohibitive.
- You need sub-millisecond latency at very high QPS (>10K).
- You need specialized indexes (DiskANN, PQ) that pgvector doesn't support.
- You need to scale vector search independently of your relational database.

For most applications, this threshold is far away. Start with pgvector; migrate only when you hit a real limit.

## See also

- [[Inference and Production MOC]] — the area orientation for inference and production topics.
- [[Production AI Stack]] — where vector storage fits in an end-to-end production architecture.
- [[Embedding Models for Retrieval]] — the models that produce the embeddings stored and searched here.
- [[Observability Stack]] — latency percentiles, cache ratios, and alerting for production services.
- [[Messaging with Kafka and Celery]] — queue-backed asynchronous work such as background embedding jobs.
