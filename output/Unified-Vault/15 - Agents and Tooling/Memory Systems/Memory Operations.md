---
title: Memory Operations
type: concept
aliases: ["Memory Consolidation", "Memory Decay", "memory ops"]
tags: [memory, operations, consolidation, decay, retrieval, forgetting, gdpr]
sources: ["03 - Memory Operations"]
created_index: 28
---

Agent memory is not a passive store — it is an active system with operations: **write** (store new memories), **read** (retrieve relevant memories), **consolidate** (merge and summarize), **decay** (deprecate stale or low-value memories), and **forget** (delete). Without these operations, memory grows unboundedly, retrieval quality degrades, and the agent acts on stale information. The operations are inspired by human memory (consolidation during sleep, decay over time) but implemented as explicit system functions. This note covers the five core operations, their lifecycle, implementation patterns, a quantitative model of decay and consolidation, and the production practices and failure modes around them.

## The five core operations

The five operations form a loop around the memory store: writes feed it, reads pull from it, and consolidation, decay, and forgetting keep it healthy over time.

```mermaid
graph LR
  Input[New information] --> Write[Write]
  Write --> Store[(Memory Store)]
  Query[Query] --> Read[Read]
  Store --> Read
  Read --> Use[Use in context]
  Store -->|periodic| Consolidate[Consolidate]
  Consolidate --> Store
  Store -->|time-based| Decay[Decay]
  Decay --> Store
  Store -->|low value| Forget[Forget]
  Forget --> Deleted[(Discarded)]
```

### Write

The write operation stores new information in memory, and it comes in several variants. A **direct write** is when the agent (or application) explicitly stores a fact: "The user's name is Alice." An **extracted write** is when a background process extracts facts from the conversation and stores them: "Based on the conversation, extract 3 facts about the user." An **inferred write** is when the agent infers a fact that was not directly stated: "The user mentioned a 6-year-old daughter; the user is likely a parent."

Each write should include metadata:

- **Source**: who/what wrote it (agent ID, user, system).
- **Timestamp**: when it was written.
- **Confidence**: how certain the fact is (1.0 for explicit statements, lower for inferences).
- **TTL**: time-to-live, if the fact is expected to expire (e.g., "user is currently in a meeting" — expires in 1 hour).
- **Tags**: categorical metadata for filtering (topic, entity, type).

Without metadata, you cannot decay, consolidate, or validate memories later.

### Read

Read retrieves relevant memories for the current context. The main read operations are **semantic search** (embed the query, retrieve the top-K most similar memories, using a vector DB), **keyword search** (BM25 or full-text search for exact matches — useful for entity names and IDs), **hybrid search** (semantic + keyword combined; the typical production default), **time-filtered** reads (only memories from the last N hours/days, useful for "what happened recently" queries), **metadata-filtered** reads (only memories with specific tags, useful for topic-specific retrieval), and **graph traversal** (if memories are linked, e.g., in a knowledge graph, traverse from a starting memory to related ones).

Read operations should return not just the memory content but also the metadata, so the agent can reason about source, confidence, and recency.

### Consolidate

Consolidation merges and summarizes memories to reduce redundancy and improve retrieval quality. Its main patterns are **deduplication** (if two memories are semantically similar, merge them: "User likes pizza" + "User ordered pizza twice this week" → "User likes pizza (frequently orders)"), **summarization** (replace N old memories with a single summary — common for conversation history, e.g., summarize the last 50 turns into a paragraph), **hierarchical summarization** (summaries of summaries: day → week → month → year, where each level is more compact but loses detail), **entity consolidation** (merge all facts about an entity into a single "entity card": "Alice: name=Alice, age=32, lives=NYC, job=engineer."), and **conflict resolution** (if two memories conflict — "user lives in NYC" vs. "user lives in London" — resolve by recency, confidence, or explicit user correction).

Consolidation is typically run as a background job (every N turns, or nightly) rather than synchronously during a conversation. It is expensive (LLM calls for summarization) but essential for long-running agents.

### Decay

Decay reduces the priority or confidence of memories over time. **Time-based decay** lowers confidence with age — a fact from 6 months ago has lower confidence than one from yesterday. **Access-based decay** deprioritizes memories that haven't been retrieved in a long time, similar to LRU cache eviction. **Reinforcement** works in the opposite direction: when a memory is retrieved and used, its confidence is boosted (it's clearly still relevant). A common functional form is **exponential decay**: `confidence *= 0.99^days_since_write` — smooth and gradual.

Decay does not delete memories — it just affects retrieval ranking. A decayed memory is still retrievable if explicitly searched for, but it ranks lower in semantic search.

### Forget

Forgetting deletes memories that are no longer useful. Its patterns are **TTL expiration** (memories with a TTL are deleted when it expires — "user is in a meeting" is deleted after 1 hour), **low-confidence deletion** (memories below a confidence threshold, e.g. 0.2, are deleted during consolidation), **explicit deletion** (the agent or user explicitly forgets a fact: "Forget that I told you my password."), **privacy-driven deletion** (delete PII after a retention period, per GDPR or similar regulations), and **capacity-driven deletion** (when memory is full, evict the lowest-priority memories, LRU-style).

Forgetting is irreversible unless you have an audit log. Be conservative — decay first, forget only when clearly safe.

## Operation lifecycle

A single memory typically flows through all five operations over its lifetime:

```mermaid
graph TD
  Turn1[Turn 1: user says something] -->|extract| Write1[Write fact F1]
  Turn2[Turn 5: related topic] -->|retrieve| Read1[Read F1 + others]
  Read1 --> Use1[Use in response]
  Use1 --> Reinforce[Reinforce F1 confidence]
  Turn3[Turn 20: similar fact F2 written] --> Write2[Write F2]
  Background[Background job every 50 turns] --> Consol[Consolidate F1 + F2 → F3]
  Consol --> Decay1[Decay original F1, F2]
  TimePasses[Time passes] --> Decay2[Decay F3 confidence]
  LowConf[Confidence < 0.2] --> Forget1[Forget F3]
```

In words: a fact extracted at turn 1 is written with metadata; at turn 5 a related topic triggers a read, and using the memory in a response reinforces its confidence; at turn 20 a similar fact is written; a background job running every 50 turns consolidates the two into a merged memory and decays the originals; as time passes the merged memory's confidence decays; and once confidence drops below 0.2 the memory is forgotten.

## Implementation patterns

### Memory as a database

Most production memory systems use a database as the store:

- **Vector DB** (Pinecone, Qdrant, Weaviate, pgvector): for semantic search.
- **Relational DB** (Postgres): for structured facts, metadata, relationships.
- **Document DB** (MongoDB): for flexible memory schemas.
- **Graph DB** (Neo4j): for entity-relationship memories (knowledge graphs).

A hybrid approach works well: pgvector gives you both vector search and relational queries in one database. For most production systems, this is the right starting point.

### A typical memory schema

A memory record carries the content, its embedding, and the operational metadata:

```python
class Memory(BaseModel):
    id: str
    user_id: str
    tenant_id: str
    content: str  # the actual memory text
    embedding: list[float]  # for vector search
    metadata: dict  # source, tags, entities
    confidence: float  # 0.0 to 1.0
    created_at: datetime
    last_accessed_at: datetime
    access_count: int
    ttl: Optional[datetime]  # when to expire
    superseded_by: Optional[str]  # if a newer memory replaces this one
```

### Operation APIs

The five operations become a small store interface:

```python
class MemoryStore:
    def write(self, content: str, metadata: dict = None, confidence: float = 1.0, ttl: timedelta = None) -> str: ...
    def read(self, query: str, limit: int = 5, filter: dict = None) -> list[Memory]: ...
    def consolidate(self, user_id: str) -> int: ...  # returns number of memories merged
    def decay(self, user_id: str) -> int: ...  # returns number of memories decayed
    def forget(self, memory_id: str) -> bool: ...
    def reinforce(self, memory_id: str) -> None: ...  # boost confidence on access
```

These APIs are wrapped in agent tools (function calls) so the agent can manage memory autonomously, similar to MemGPT (see [[MemGPT and Letta]]). [[Function Calling]] is the mechanism that exposes them to the model.

## A mathematical model of decay and consolidation

A useful way to reason about memory operations quantitatively is to assign each memory $m_i$ a **priority score** $p_i \in [0, 1]$ that determines its retrieval ranking and eligibility for forgetting. The priority is updated by three rules:

1. **Time decay** (continuous): $p_i(t) = p_i(t_0) \cdot e^{-\lambda \Delta t}$ where $\Delta t = t - t_{\text{last\_access}}$ and $\lambda$ is the decay constant (e.g., $\lambda = 0.01$/day for slow decay, $\lambda = 0.1$/day for fast decay).
2. **Access reinforcement** (discrete): each time $m_i$ is retrieved, $p_i \leftarrow \min(1, p_i + \alpha)$ where $\alpha \approx 0.1$.
3. **Confidence update** (continuous): if a new memory $m_j$ contradicts $m_i$, set $p_i \leftarrow p_i \cdot (1 - c_j)$ where $c_j$ is the confidence of the new memory.

A memory is **forgetting-eligible** when $p_i < \theta_{\text{forget}}$ (typically 0.05). It is **consolidation-eligible** when there exists another memory $m_j$ with cosine similarity $> \theta_{\text{similar}}$ (typically 0.85). These thresholds must be tuned per use case — too-aggressive forgetting discards useful memories; too-conservative consolidation leaves duplicates that confuse retrieval.

For a graph-structured memory store (knowledge graph), the same model extends by adding **edge weights** that represent relationship strength. Consolidation becomes **community detection** (group related nodes); decay becomes **edge weight reduction** over time; forgetting becomes **node pruning** for low-degree, low-weight nodes.

## Modern developments (2024–2026)

### Tiered memory with hot, warm, and cold storage

Production memory systems now use three-tier storage. The **hot tier** (in-process memory, Redis) holds working memory plus the last 1–2k turns, with sub-millisecond access. The **warm tier** (vector DB with SSD-backed index, e.g., Qdrant) holds frequently accessed facts and summaries, with 10–50ms access. The **cold tier** (Postgres table, S3 archive) holds full history and rarely accessed facts, with 100–500ms access.

A **promotion/demotion policy** moves memories between tiers based on access frequency. Mem0 v2, Letta 0.7, and LangGraph's Checkpoint v2 all implement this pattern with slight variations (see [[LangGraph]]).

### GraphRAG-inspired memory consolidation

Microsoft's GraphRAG (2024) introduced a memory consolidation pattern: rather than storing raw text chunks, extract entities + relationships and store them as a knowledge graph. When new information arrives, update the graph (add nodes/edges, merge duplicates). Retrieval combines vector search over node summaries with graph traversal for multi-hop queries. This pattern produces more structured, queryable memory than flat vector stores, especially for entity-heavy domains (legal, medical, financial). [[Advanced RAG Patterns]] covers the retrieval side of this idea.

### Sleep-time consolidation

Building on the MemGPT sleep-time-compute pattern (see [[MemGPT and Letta]]), modern systems run consolidation jobs during idle windows:

1. **Cluster memories** by semantic similarity; merge clusters below a similarity threshold into a single summary memory.
2. **Detect conflicts** — memories with similar subjects but contradictory content; resolve by recency + confidence.
3. **Extract entity cards** — for each entity mentioned in ≥3 memories, generate a structured "entity card" summarizing all known facts.
4. **Re-rank by importance** — use an LLM-as-judge to score each memory 0–10; demote memories scoring <4 to cold storage.

### Memory versioning and time travel

Some applications (legal, audit) require knowing "what did the agent know at time T?" Versioning memory means each write produces a new version with `valid_from`/`valid_to` timestamps; superseded memories are not deleted but marked as historical. Querying with `AS_OF=T` returns the memory state at time T. This is implemented as a temporal table in Postgres or a versioned KV store.

### Right-to-be-forgotten compliance

GDPR Article 17 and similar regulations require that users can request deletion of their personal data — including from agent memory. A compliant memory system must:

1. Track all memories by `user_id` (every memory owned by exactly one user).
2. Support cascading delete: `forget(user_id)` deletes all memories for that user, including references in consolidated summaries (which requires re-running consolidation after deletion).
3. Maintain an audit log of the deletion (who requested it, when, scope) without retaining the deleted content.
4. Handle "soft delete" (mark as deleted) for grace periods, then hard delete after confirmation.

## Worked example: implementing decay and consolidation

A minimal implementation of the priority model and a pairwise consolidation job:

```python
import math
from datetime import datetime, timedelta
from typing import Optional

class MemoryRecord:
    def __init__(self, id: str, content: str, confidence: float = 1.0):
        self.id = id
        self.content = content
        self.confidence = confidence
        self.created_at = datetime.utcnow()
        self.last_accessed_at = self.created_at
        self.access_count = 0
        self.superseded_by: Optional[str] = None

    def priority(self, now: datetime, lambda_decay: float = 0.01, alpha_boost: float = 0.1) -> float:
        """Compute current priority score in [0, 1]."""
        if self.superseded_by:
            return 0.0  # superseded memories are effectively gone
        days_since_access = (now - self.last_accessed_at).total_seconds() / 86400
        time_decay = math.exp(-lambda_decay * days_since_access)
        boost = min(1.0, alpha_boost * self.access_count)
        return self.confidence * (0.7 * time_decay + 0.3 * boost)  # weighted blend

    def touch(self):
        """Called when this memory is retrieved."""
        self.last_accessed_at = datetime.utcnow()
        self.access_count += 1

# Example consolidation: merge two memories if cosine similarity > 0.85
def consolidate_pair(m1: MemoryRecord, m2: MemoryRecord, llm) -> MemoryRecord:
    """Use an LLM to merge two semantically similar memories."""
    prompt = f"""Merge these two memories into a single concise statement:
    Memory A: {m1.content}
    Memory B: {m2.content}
    Merged:"""
    merged_content = llm.complete(prompt).strip()
    merged = MemoryRecord(
        id=f"merged-{m1.id}-{m2.id}",
        content=merged_content,
        confidence=max(m1.confidence, m2.confidence),
    )
    m1.superseded_by = merged.id
    m2.superseded_by = merged.id
    return merged

# Nightly background job
def run_consolidation(store, user_id: str, similarity_threshold: float = 0.85):
    memories = store.list_all(user_id)
    for i, m1 in enumerate(memories):
        for m2 in memories[i+1:]:
            if m1.superseded_by or m2.superseded_by:
                continue
            sim = cosine_similarity(embed(m1.content), embed(m2.content))
            if sim > similarity_threshold:
                merged = consolidate_pair(m1, m2, llm)
                store.write(merged)
```

## Common pitfalls

### No consolidation

Memories accumulate without deduplication. After 1000 turns, the store has 5000 memories, many redundant. Search quality degrades and latency increases.

### No decay

A fact from 2 years ago has the same confidence as one from yesterday. The agent acts on stale information. Always implement decay.

### Forgetting without audit

A user asks "what did you know about me last month?" and you cannot answer because you forgot everything. Maintain an audit log of forgotten memories for compliance and debugging.

### No confidence tracking

All memories are treated as equally reliable. The agent acts on a low-confidence inference the same way as a high-confidence explicit statement. Always track and use confidence.

### Synchronous consolidation

Consolidation runs during the conversation, adding seconds of latency. Run it as a background job.

### No per-tenant isolation

Agent A reads Agent B's user's memories. Use row-level security or explicit tenant filtering on every query.

### Embedding drift

If you change embedding models, old memories have stale embeddings and are not retrievable. Either re-embed everything (expensive) or maintain a versioning scheme.

## Common failure modes

The symptoms operators observe usually point to a specific missing operation or mis-set parameter. The diagnostic table maps each symptom to its likely cause and fix.

| Symptom                                | Likely Cause                                  | Fix                                                          |
|----------------------------------------|-----------------------------------------------|--------------------------------------------------------------|
| Search returns irrelevant memories     | Embedding model poorly suited to content type | Use domain-tuned embedder; consider fine-tuning              |
| Agent acts on stale facts              | No decay implemented                          | Implement exponential decay; tune λ per memory type          |
| Memory grows unbounded                 | No consolidation or forgetting job            | Schedule nightly consolidation; cap memory count per user    |
| Consolidation loses important details  | LLM summarizer too aggressive                 | Increase summary length; preserve named entities             |
| Same fact stored 5x                    | No dedup on write                             | Pre-write similarity check; reject if sim > 0.95             |
| Latency grows with memory size         | Linear scan in read path                      | Use ANN index (HNSW, IVF); pin hot memories in Redis         |
| Memory leak across users               | Missing tenant filter on read                 | Enforce `WHERE tenant_id = ?` on every query                 |
| Cannot answer "what did you know at T" | No versioning                                 | Add temporal table; track `valid_from`/`valid_to`            |
| GDPR delete leaves orphan facts        | Consolidated summaries still contain PII      | Re-run consolidation after deletion; scrub PII from summaries|

## Interview questions

**Walk through the lifecycle of a single memory from write to forget.** (1) **Write** — the agent or an extractor stores the fact with metadata (source, timestamp, confidence, TTL). (2) **Read** — at retrieval time, the memory is ranked by priority (decay × confidence × recency). (3) **Reinforce** — if retrieved, `last_accessed_at` updates and confidence is boosted. (4) **Consolidate** — if a similar memory is later written, an LLM merges them; the originals are marked superseded. (5) **Decay** — priority decreases exponentially with time since last access. (6) **Forget** — once priority drops below threshold (or TTL expires, or the user requests deletion), the memory is hard-deleted (with an audit log entry).

**Why is consolidation expensive, and how do you make it tractable?** Consolidation requires pairwise similarity checks (O(n²)) and LLM calls for each merge. To make it tractable: (1) run it as a **background job** during low-traffic windows; (2) **cluster first** with cheap ANN search, then only consolidate within clusters; (3) **batch LLM calls** — merge multiple memory pairs in a single prompt; (4) **incremental consolidation** — only process memories written since the last run, not the whole store. A 1M-memory store can be consolidated nightly with ~$5 of LLM cost using these techniques.

**How do you handle conflicting memories (e.g., "user lives in NYC" vs. "user lives in London")?** Three-step conflict resolution: (1) **Detect** — during consolidation, if two memories have high subject similarity but contradictory content (use an LLM judge), flag them as a conflict. (2) **Resolve** — apply priority rules: explicit user statement > inferred; recent > old; high-confidence > low-confidence. (3) **Mark** — the losing memory is marked `superseded_by` the winning one (not deleted, for audit purposes). For ambiguous cases (same recency, same confidence), surface it to the user: "I have conflicting info — do you live in NYC or London?"

**What's the difference between decay and forgetting?** **Decay** is a soft signal — it reduces a memory's priority/retrieval rank but doesn't remove it; the memory is still searchable if explicitly queried. **Forgetting** is hard deletion — the memory is removed from the store (possibly with an audit log). Decay is reversible (retrieval boosts priority back up); forgetting is irreversible. Best practice: decay aggressively, forget conservatively. Use forgetting only for TTL expiration, low-confidence cleanup, or explicit user/GDPR requests.

**How would you implement GDPR-compliant "right to be forgotten" in an agent memory system?** (1) Every memory has a `user_id` — no anonymous writes. (2) `forget(user_id)` cascade-deletes all memories where `user_id` matches, including in consolidated summaries (re-run consolidation to scrub PII). (3) The audit log records the deletion event (who, when, scope) but NOT the deleted content. (4) Soft-delete for a 30-day grace period (recoverable), then hard-delete. (5) Vector embeddings derived from deleted content are also deleted (not just the text). (6) Backups must support point-in-time deletion requests — typically a 30-day backup retention limit, with GDPR delete requests queued for after-backup-expiry.

**How does tiered storage (hot/warm/cold) interact with decay?** Decay drives tier transitions. The hot tier holds high-priority memories (recently accessed, high confidence). As priority decays, memories are **demoted** to the warm tier (slower access, larger capacity), then to the cold tier (slowest, largest, cheapest). Re-access **promotes** them back to the hot tier. This is the same pattern as CPU caches (L1/L2/L3) — the OS analogy continues to hold. Tuning: hot tier ~1k memories/user (Redis, ~1MB/user), warm tier ~50k (Qdrant, ~50MB/user), cold tier unbounded (S3, ~$0.023/GB/month).

## Why this matters

Memory operations are the difference between an agent that learns and one that forgets. Without consolidation, agents accumulate noise. Without decay, agents act on stale information. Without forgetting, agents become slow and unmanageable.

For production agents, the memory operations layer is as important as the LLM itself. A great LLM with poor memory operations produces a worse user experience than a mediocre LLM with well-designed memory.

## Relationship to other concepts

[[Memory Types]] provides the cognitive-science taxonomy that motivates operations like consolidation (sleep) and decay (the forgetting curve). [[MemGPT and Letta]] exposes these operations as agent-callable tools, and [[Vector Memory Backends]] is the storage layer where write/read/decay/forget physically happen. The read operation uses the same search techniques as [[Chunking, Hybrid Search, and Reranking]], and [[Advanced RAG Patterns]] covers the GraphRAG-style consolidation ideas. [[Autonomous Agent Lifecycles]] describes the phases during which these operations fire. On the production side, [[PII and Data Leakage]] covers PII handling in memory write/forget, and [[Production Monitoring]] covers memory-ops metrics (write rate, retrieval latency, consolidation cost). There is also a quantitative view: [[Entropy Cross-Entropy and KL Divergence]] frames consolidation as compression, and [[Estimators and Bias]] frames confidence scoring as a statistical estimator.

## See also

- [[Agents and Tooling MOC]] — the area orientation for agents and tooling.
- [[Memory Types]] — the taxonomy that motivates the operations.
- [[MemGPT and Letta]] — exposes memory operations as agent-callable tools.
- [[Vector Memory Backends]] — the storage layer where operations physically happen.
- [[Chunking, Hybrid Search, and Reranking]] — search techniques used by the read operation.
- [[Advanced RAG Patterns]] — GraphRAG-inspired consolidation.
- [[RAG Pipeline Overview]] — retrieval as the read operation.
- [[Autonomous Agent Lifecycles]] — when operations fire during agent lifecycles.
- [[LangGraph]] — checkpoint-based persistent state with tiered-storage variants.
- [[Function Calling]] — the mechanism that wraps memory APIs as agent tools.
- [[PII and Data Leakage]] — PII handling in memory write/forget.
- [[Production Monitoring]] — memory-ops metrics.
- [[Entropy Cross-Entropy and KL Divergence]] — consolidation as compression.
- [[Estimators and Bias]] — confidence scoring as an estimator.
