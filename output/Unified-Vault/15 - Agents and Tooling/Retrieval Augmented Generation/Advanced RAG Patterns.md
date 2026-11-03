---
title: Advanced RAG Patterns
type: concept
aliases: [Agentic RAG, GraphRAG, Self-RAG, Corrective RAG, CRAG]
tags: [rag, agentic-rag, graphrag, self-rag, advanced, corrective-rag]
sources: ["03 - Advanced RAG Patterns"]
created_index: 39
---

Beyond basic retrieve-once-generate RAG lies a family of advanced patterns that trade cost and complexity for answer quality. Agentic RAG uses an LLM agent to decide when and what to retrieve, GraphRAG uses a knowledge graph for multi-hop retrieval, and Self-RAG / Corrective RAG let the model self-assess and re-retrieve. This note covers each pattern, when it helps and when it doesn't, a LangGraph worked example, production implications, and common pitfalls.

> [!info] TL;DR
> Beyond basic RAG: **Agentic RAG** uses an LLM agent to decide when and what to retrieve. **GraphRAG** uses a knowledge graph for multi-hop retrieval. **Self-RAG / Corrective RAG** lets the model self-assess and re-retrieve. Higher quality, higher cost, more complexity.

## Agentic RAG

Standard RAG retrieves once and generates. Agentic RAG puts an agent in charge: it decides when to retrieve, what query to use, and whether to retrieve again.

### The pattern

```text
User question
   ↓
[Agent reasons: do I need to search?]
   ↓ yes
[Agent formulates search query]
   ↓
[Retrieve]
   ↓
[Agent observes results: enough info?]
   ↓ no
[Agent reformulates query, searches again]
   ↓ yes
[Agent generates answer with citations]
```

The loop: the agent reasons about whether search is needed, formulates a query, retrieves, observes the results, and then either reformulates and searches again or generates a cited answer.

### When agentic RAG helps

Agentic RAG pays off for complex questions requiring multi-hop retrieval, for questions where the initial query needs reformulation, and for questions that need synthesis across multiple sources.

### When it doesn't

For simple lookups, just do basic RAG. It is also a poor fit for latency-sensitive applications, since each retrieve-observe cycle adds seconds.

### Implementation

Use the [[ReAct Pattern]] with retrieval as a tool. [[LangGraph]] and [[LlamaIndex]] both have agentic RAG templates.

## GraphRAG (Microsoft, 2024)

GraphRAG builds a **knowledge graph** from documents, then uses graph traversal for retrieval.

### The pipeline

1. **Extract entities and relationships** from each document (LLM-based).
2. **Build a graph**: nodes = entities, edges = relationships.
3. **Cluster entities** into communities (e.g., the Leiden algorithm).
4. **Generate community summaries** (LLM-based).
5. **Query**:
   - For specific entity queries: traverse the graph from the entity.
   - For broad queries: read community summaries.

### When GraphRAG helps

GraphRAG helps with multi-hop questions about entities and relationships ("Who are the key players in X and how do they connect?") and with questions where the answer requires synthesizing across many documents.

### When it doesn't

It doesn't help with simple factual lookups (basic RAG is fine), with document collections without clear entity structure, or with cost-sensitive applications — GraphRAG construction is expensive.

## Self-RAG (Asai et al. 2023)

Self-RAG trains the model to **self-assess** whether retrieval is needed and whether retrieved context is relevant.

### Reflection tokens

The model emits special "reflection" tokens: `Retrieve` (should I retrieve? yes/no), `ISREL` (is the retrieved doc relevant? yes/no), `ISSUP` (is the answer supported by the docs? yes/no), and `ISUSE` (is the answer useful? rating).

### Training

Self-RAG fine-tunes the model on trajectories that include these reflection tokens, with rewards for correct retrieval and grounded answers.

### Inference

At inference time the model self-decides when to retrieve and self-evaluates its answers. If unsupported, it can re-retrieve and try again.

## Corrective RAG (CRAG, Yan et al. 2024)

CRAG is a simpler alternative to Self-RAG. First retrieve documents. Then run a **confidence assessment**: a small model scores whether the retrieved docs are relevant. If confidence is high, use the docs (with retrieval refinement); if confidence is low, **fall back to web search**. Finally, generate the answer with the (corrected) context. CRAG doesn't require fine-tuning — it's a prompting + workflow pattern.

## Worked example: agentic RAG with LangGraph

A minimal agentic RAG loop in LangGraph — retrieve, assess whether the retrieved docs are sufficient, and either loop back to retrieve or proceed to generate:

```python
from langgraph.graph import StateGraph, END

class State(TypedDict):
    question: str
    retrieved: List[str]
    answer: str
    needs_more: bool

def decide_retrieve(state):
    # LLM decides if retrieval is needed
    decision = llm.generate(f"Does this question need retrieval? {state['question']}")
    if "yes" in decision.lower():
        return "retrieve"
    return "generate"

def retrieve(state):
    query = llm.generate(f"Formulate a search query for: {state['question']}")
    docs = vector_db.search(query, k=5)
    return {"retrieved": docs}

def assess(state):
    # LLM assesses if retrieved docs are sufficient
    assessment = llm.generate(f"Are these docs sufficient? {state['retrieved']}")
    return {"needs_more": "no" in assessment.lower()}

def generate(state):
    answer = llm.generate(f"Context: {state['retrieved']}\nQ: {state['question']}")
    return {"answer": answer}

graph = StateGraph(State)
graph.add_node("retrieve", retrieve)
graph.add_node("assess", assess)
graph.add_node("generate", generate)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "assess")
graph.add_conditional_edges("assess", lambda s: "retrieve" if s["needs_more"] else "generate")
graph.add_edge("generate", END)
app = graph.compile()
```

## Why this matters for AI

These patterns represent the **frontier of RAG** in 2026 — most production RAG is still basic, but advanced patterns are increasingly adopted for high-value use cases. Agentic RAG is the bridge between RAG and full agents; many "agents" are essentially agentic RAG with tools. GraphRAG is Microsoft's bet on knowledge-graph-augmented retrieval, useful for enterprise knowledge management. Self-RAG and CRAG address the "stuck with bad retrieval" failure mode of basic RAG.

## Production implications

Start with basic RAG + reranking, and add agentic patterns only when you've exhausted simpler approaches. Agentic RAG is expensive (multiple LLM calls per query) — use it for high-value queries, not high-volume. GraphRAG requires significant upfront investment (graph construction) but pays off for entity-heavy domains. Self-RAG / CRAG improve reliability at moderate cost, and CRAG is the easier starting point (no fine-tuning). On latency: advanced patterns add 5–30s per query, which is not suitable for real-time chat.

## Common pitfalls

- **Jumping to advanced patterns too early** — basic RAG with good chunking + hybrid search + reranking is hard to beat.
- **No evaluation** — without measuring retrieval quality, you can't tell if agentic patterns help.
- **Cost overruns** — agentic patterns can 10x token costs. Budget per query.
- **Infinite loops** — agentic RAG can loop forever on bad queries. Always set max iterations.

## Further reading

- Asai et al. (2023), *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*.
- Yan et al. (2024), *Corrective Retrieval Augmented Generation*.
- Edge et al. (2024), *From Local to Global: A GraphRAG Approach to Query-Focused Summarization* (Microsoft GraphRAG).

## See also

- [[RAG Pipeline Overview]]
- [[Chunking, Hybrid Search, and Reranking]]
- [[ReAct Pattern]] — the agent loop agentic RAG builds on
- [[Reflection]] — self-assessment in agents
- [[LangGraph]] — graph-based agent orchestration
- [[LlamaIndex]] — agentic RAG templates
- [[Build a Knowledge-Graph Construction Pipeline]] — building the graphs GraphRAG retrieves over
- [[Agents and Tooling MOC]]
