---
title: LlamaIndex
type: concept
aliases: [LlamaIndex, GPT Index]
tags: [framework, llamaindex, rag, data-framework]
sources: ["05 - LlamaIndex"]
created_index: 18
---

LlamaIndex is a data framework for LLM applications, focused on connecting custom data sources to LLMs. Its strengths are document ingestion (diverse loaders), indexing (multiple index types for different retrieval patterns), and structured querying (query engines that combine retrieval with LLM reasoning). It is the standard choice for RAG-centric applications where data connection is the primary challenge; this note covers its core abstractions, advanced features, strengths and weaknesses, fit guidance, and production patterns.

> [!info] TL;DR
> LlamaIndex is a data framework for LLM applications, focused on connecting custom data sources to LLMs. Its strengths are document ingestion (diverse loaders), indexing (multiple index types for different retrieval patterns), and structured querying (query engines that combine retrieval with LLM reasoning). LlamaIndex is the standard choice for RAG-centric applications where data connection is the primary challenge.

## Overview

LlamaIndex is developed by LlamaIndex Inc. (Jerry Liu, 2022). It is available in Python and TypeScript, under the MIT license. It is actively developed and focused on enterprise RAG.

## Core focus: data connection

While LangChain tries to be a general LLM framework, LlamaIndex focuses specifically on the **data problem**: how do you connect LLMs to your data? That covers three things: loading data from diverse sources (file systems, databases, APIs, SaaS tools), structuring data for efficient retrieval (indexes), and querying data in ways that leverage LLM reasoning. This focus makes LlamaIndex the strongest framework for RAG applications, especially enterprise RAG with complex data sources.

## Core abstractions

### Documents and nodes

A **Document** is a container for a piece of text plus metadata (source, author, date, etc.). A **Node** is a chunk of a document — the unit of retrieval. Nodes have parent-document relationships.

```python
from llama_index.core import Document, SimpleNodeParser

doc = Document(text="Long document text...", metadata={"source": "report.pdf"})
parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)
nodes = parser.get_nodes_from_documents([doc])
```

### Indexes

Indexes are data structures that enable efficient retrieval. LlamaIndex supports several:

- **VectorStoreIndex**: embeddings for semantic search. The default for most RAG.
- **SummaryIndex** (formerly ListIndex): stores nodes in a sequence; good for summarization.
- **TreeIndex**: hierarchical tree of summaries; good for long documents.
- **KeywordTableIndex**: keyword extraction + lookup; good for entity-centric search.
- **KnowledgeGraphIndex**: entities + relationships; good for multi-hop reasoning.

```python
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex(nodes)
```

### Query engines

Query engines combine retrieval with LLM reasoning:

```python
query_engine = index.as_query_engine(similarity_top_k=5)
response = query_engine.query("What is the revenue trend?")
print(response.response)
```

The query engine works in four steps: it embeds the query, retrieves top-K nodes from the index, constructs a prompt with the query plus retrieved context, and calls the LLM to generate an answer.

### Chat engines

Chat engines maintain conversation history:

```python
chat_engine = index.as_chat_engine()
response = chat_engine.chat("Tell me about the company")
followup = chat_engine.chat("What about their competitors?")
```

### Retrievers

Retrievers are customizable retrieval logic:

```python
from llama_index.core.retrievers import VectorIndexRetriever

retriever = VectorIndexRetriever(index, similarity_top_k=10)
nodes = retriever.retrieve("query")
```

You can compose retrievers (union, intersection, routing) for complex retrieval strategies.

### Response synthesizers

Response synthesizers control how the LLM synthesizes a response from retrieved nodes. The **Compact** mode stuffs all nodes into one prompt, **Tree summarize** recursively summarizes chunks, and **Refine** generates an initial answer and then refines it with each subsequent chunk.

### Data loaders

LlamaIndex has 200+ data loaders (LlamaHub) for diverse sources, spanning file types (PDF, DOCX, HTML, Markdown, code files), databases (Postgres, MongoDB, Snowflake, BigQuery), SaaS tools (Notion, Slack, GitHub, Google Drive, Jira), and the web (URL crawling, sitemap parsing, RSS feeds).

```python
from llama_index.readers.file import PDFReader
from llama_index.readers.github import GithubRepositoryReader

# Load from PDF
pdf_docs = PDFReader().load_data("report.pdf")

# Load from GitHub
github_docs = GithubRepositoryReader(owner="owner", repo="repo").load_data()
```

## Advanced features

### LlamaParse

LlamaParse is LlamaIndex's commercial document parsing service. It handles complex PDFs (tables, figures, multi-column layouts) better than open-source alternatives, and produces Markdown that's LLM-friendly.

### LlamaCloud

LlamaCloud is a managed indexing and retrieval service. It handles document ingestion, indexing, and retrieval without infrastructure management, and is targeted at enterprise RAG.

### Workflows

Workflows are LlamaIndex's workflow system (similar to LangGraph) for multi-step RAG pipelines. They cover conditional retrieval (try vector search, fall back to keyword), multi-hop retrieval (retrieve, reason, retrieve again), and agentic RAG (the LLM decides when to retrieve and what to query).

### Agents

LlamaIndex has its own agent abstractions, though they're less mature than LangGraph's. The `ReActAgent` implements the standard ReAct loop, the `FunctionAgent` is function-calling-based, and the `WorkflowAgent` is built on the workflow system.

### Structured output

LlamaIndex supports structured output extraction:

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

query_engine = index.as_query_engine(output_cls=Person)
result = query_engine.query("Extract the person from the document")
print(result.name)  # "Alice"
```

## Strengths

### Data connection breadth

LlamaIndex's 200+ loaders cover virtually any data source. If you need to ingest data from an unusual source, LlamaIndex likely has a loader. This is its biggest advantage over LangChain.

### Index variety

Multiple index types let you choose the right structure for your data: vector for semantic search, tree for long-document summarization, graph for multi-hop reasoning, and keyword for exact-match retrieval. Most other frameworks only support vector indexes.

### RAG-centric design

Every abstraction is designed with RAG in mind. The query engine, retriever, synthesizer separation maps cleanly to the RAG pipeline, making it easy to customize each stage.

### LlamaParse for complex documents

For enterprise RAG with complex PDFs (tables, figures, multi-column), LlamaParse is significantly better than open-source alternatives. It's a commercial add-on but worth it for production RAG.

### Cleaner abstractions than LangChain

LlamaIndex's abstractions (Document, Node, Index, QueryEngine) are more cohesive and less leaky than LangChain's. The framework feels more focused.

## Weaknesses

### Narrower scope than LangChain

LlamaIndex is RAG-focused. If you need general agent capabilities, complex tool orchestration, or non-RAG patterns, LangChain/LangGraph is more capable.

### Smaller community than LangChain

LlamaIndex has a smaller community and fewer third-party integrations. For niche use cases, you may need to build your own integrations.

### Commercial components

LlamaParse and LlamaCloud are commercial. For open-source-only projects, you may need alternatives (Unstructured.io, self-hosted parsing).

### Less mature agent support

LlamaIndex's agent abstractions are less mature than LangGraph's. For complex agents, LangGraph is the better choice.

## When to use LlamaIndex

### Good fit

LlamaIndex is a good fit for **RAG applications** — the primary use case, and LlamaIndex is the strongest RAG framework; **complex data ingestion**, with diverse data sources and complex document formats; **enterprise RAG**, with LlamaParse and LlamaCloud for production deployments; and **multi-index applications**, when you need different index types for different query patterns.

### Poor fit

It is a poor fit for **agent-heavy applications** (use [[LangGraph]]), **simple chatbots** (direct API calls are simpler), and **non-RAG LLM applications**, where LlamaIndex's RAG focus is overkill.

## Comparison to alternatives

| Framework   | Focus                    | Strengths                          | Weaknesses                       |
|-------------|--------------------------|------------------------------------|----------------------------------|
| LlamaIndex  | RAG + data connection    | Loaders, index variety, LlamaParse | Narrower scope, smaller community|
| LangChain   | General LLM framework    | Breadth, integrations, community   | Heavy abstractions, breaking chgs|
| DSPy        | Prompt optimization      | Systematic optimization            | Learning curve, compilation cost |
| Haystack    | Production NLP/RAG       | Clean design, production-focused   | Smaller community                |

LlamaIndex and Haystack are the closest competitors (both RAG-focused). LlamaIndex has broader data loader support; Haystack has a cleaner production architecture.

## Production patterns

### Use LlamaParse for complex PDFs

For enterprise RAG with complex documents (tables, multi-column, figures), LlamaParse is worth the cost. Open-source alternatives (PyPDF, pdfplumber) struggle with these formats.

### Combine index types

For complex applications, use multiple indexes: a vector index for semantic search, a keyword index for entity lookup, and a tree index for document summarization. Route queries to the appropriate index based on query type.

### Customize retrievers

The default vector retriever is a starting point. For production, customize with hybrid retrieval (vector + keyword), reranking (cross-encoder after retrieval), parent-document retrieval (retrieve chunks, return parent documents), and multi-hop retrieval (iterative retrieval for complex questions).

### Use the workflow system for complex pipelines

For multi-step RAG (query rewriting, multi-hop, agentic), use LlamaIndex's workflow system rather than nesting query engines. It's more maintainable.

### Monitor retrieval quality

Track retrieval metrics (recall, precision) separately from generation metrics. A great LLM with poor retrieval produces hallucinated answers.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[RAG Pipeline Overview]] — the retrieval pipeline these abstractions map onto.
- [[Chunking, Hybrid Search, and Reranking]] — the retrieval-stage techniques to customize.
- [[Advanced RAG Patterns]] — multi-hop, agentic, and conditional retrieval beyond the basics.
- [[LangChain]] — the general-purpose alternative.
- [[LangGraph]] — the stronger choice for complex agents.
- [[Haystack]] — the closest RAG-focused competitor.
- [[DSPy]] — declarative prompt optimization.
- [[Framework Selection Guide]] — overall decision guidance across frameworks.
