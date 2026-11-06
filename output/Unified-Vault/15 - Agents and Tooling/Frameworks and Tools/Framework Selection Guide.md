---
title: Framework Selection Guide
type: reference
aliases: [Framework Selection Guide]
tags: [frameworks, langgraph, autogen, pydanticai, crewai, vllm]
sources: ["01 - Framework Selection Guide"]
created_index: 14
---

Choosing a framework is one of the first structural decisions in an AI project, and the right answer follows from what you are building: a chatbot, a RAG system, a single agent, a multi-agent system, a serving stack, or a local development setup. This guide walks that decision tree, summarizes the major agent and LLM frameworks, compares the serving engines, and closes with production implications and common pitfalls. The short version: LangGraph for production agents, PydanticAI for type-safe Python, vLLM for serving, Ollama for local dev, pgvector for the vector database if you already have Postgres, and Qdrant otherwise.

> [!info] TL;DR
> Choosing the right framework for your AI project: LangGraph for production agents, PydanticAI for type-safe Python, vLLM for serving, Ollama for local dev, pgvector for vector DB if you already have Postgres, Qdrant otherwise. This note guides the choices.

## Decision tree

### What are you building?

Start from the artifact you are building; each branch below names the recommended tools and the trade-off.

**A chatbot / single-turn Q&A**
- Use direct OpenAI / Anthropic SDK or `litellm`.
- Don't need a framework.

**A RAG system**
- Use LlamaIndex (purpose-built for RAG) or LangChain.
- For simple cases, write the pipeline directly.

**An agent (single agent with tools)**
- PydanticAI (type-safe, clean API).
- LangGraph (more features, more complex).
- OpenAI Agents SDK (if OpenAI-only).

**A multi-agent system**
- LangGraph (production-grade, durable).
- AutoGen (group chat pattern).
- CrewAI (role-based, simpler).

**Serving an LLM in production**
- vLLM (default).
- TensorRT-LLM (NVIDIA-only, max perf).
- SGLang (newer, often faster for agentic workloads).

**Running LLMs locally**
- Ollama (easiest UX).
- llama.cpp (most flexible, lowest level).
- LM Studio (GUI).

**Vector database**
- pgvector (if you have Postgres; simplest ops).
- Qdrant (standalone, fast, Rust-based).
- Weaviate (feature-rich).
- Milvus (very large scale).
- Pinecone (managed, no ops).

**Embedding models**
- BGE (open-source default).
- OpenAI text-embedding-3 (managed, easy).
- Cohere / Voyage (managed, high quality).

## Framework summaries

The one-paragraph profiles below expand each branch of the decision tree.

### LangChain / LangGraph

**LangChain** is a general LLM application framework with many integrations, though it can be over-abstracted. **LangGraph** is its graph-based agent framework — production-grade, with durable execution, and **the recommended choice for serious agent work**. LangSmith rounds out the ecosystem with observability and eval (commercial).

### LlamaIndex

[[LlamaIndex]] is a RAG-focused framework — better than LangChain for pure RAG. It has strong data connectors (loaders for many file types), but is less general-purpose than LangChain.

### OpenAI SDK / Agents SDK

The [[OpenAI SDK and Agents SDK]] pair is OpenAI's first-party Python SDK plus the Agents SDK (2024+), the official agent framework with tight OpenAI integration. Useful if you're committed to OpenAI models.

### PydanticAI

[[PydanticAI]] is a type-safe agent framework with strong Python type hints, built by the Pydantic team. It has a clean API with less abstraction than LangChain, and is good for production agents that need type safety.

### AutoGen (Microsoft)

[[AutoGen]] is a multi-agent conversation framework built around the group chat pattern (multiple agents talk to each other). AutoGen 0.4+ (2025) is a major rewrite with a cleaner architecture.

### CrewAI

[[CrewAI]] is a role-based multi-agent framework: define agents with roles ("Researcher", "Writer") and assign tasks. It is simpler than LangGraph but less flexible, and good for straightforward workflows.

### Semantic Kernel (Microsoft)

[[Semantic Kernel]] is multi-language (Python, C#, Java) and strong in enterprise Microsoft-stack environments, though less popular in pure Python ecosystems.

### Haystack (deepset)

[[Haystack]] is an older framework, still maintained, good for search and RAG, though less popular than LangChain/LlamaIndex.

### DSPy (Stanford)

[[DSPy]] is "programming with prompts" — declarative prompt optimization that compiles declarative programs into optimized prompts. Research-grade but production-curious.

## Serving frameworks

The serving engines below execute models in production or on local machines; the choice hinges on hardware, workload, and operational constraints.

### vLLM

[[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] is the default for production LLM serving. It provides PagedAttention, continuous batching, prefix caching, spec decoding, and LoRA serving, behind an OpenAI-compatible API.

### TensorRT-LLM (NVIDIA)

[[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]] delivers the highest performance on NVIDIA hardware, compiling models to optimized kernels. Use it only for NVIDIA-only deployments with strict performance requirements.

### TGI (HuggingFace)

[[TGI]] is HuggingFace's serving engine, with good HF Hub integration, though it is less performant than vLLM.

### SGLang

[[SGLang]] is newer and strong for agentic / structured workloads, with RadixAttention for prefix caching. It often outperforms vLLM on specific workloads.

### Ollama

Ollama is a local LLM runtime with the best UX for single-user development. It uses the GGUF format and runs on CPU + GPU. It is not for production serving.

### llama.cpp

llama.cpp is a C++ LLM inference library, lower-level than Ollama, and best for embedded / edge / custom integrations. It also uses the GGUF format. Both local options are covered in [[Ollama and llama.cpp]].

## Worked example (PydanticAI agent)

A minimal PydanticAI agent shows what a typed, framework-assisted agent looks like in practice:

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class ResearchResult(BaseModel):
    summary: str
    sources: list[str]

research_agent = Agent(
    model='openai:gpt-4o',
    result_type=ResearchResult,
    system_prompt='You are a research assistant. Provide concise summaries with sources.',
)

@research_agent.tool
async def search(ctx, query: str) -> str:
    """Search the web."""
    return await web_search(query)

result = research_agent.run_sync('Research the history of attention in deep learning.')
print(result.data.summary)
print(result.data.sources)
```

## Why this matters for AI

Framework choice affects **development speed, production reliability, and team productivity**. The "best" framework depends on your use case, team skills, and existing stack. For most teams starting new agent work in 2026, **LangGraph for agents, vLLM for serving, pgvector for vectors** is a sensible default stack.

## Production implications

**Don't over-framework.** Many use cases are simpler without a framework — direct API calls work fine.

**For production agents**, LangGraph is the safest bet: durable, observable, well-supported.

**For serving**, vLLM is the default. Move to TensorRT-LLM only if you've benchmarked and need more.

**For local dev**, Ollama — so much easier than installing CUDA, PyTorch, etc.

**Avoid vendor lock-in**: prefer open-source frameworks where possible, and use LiteLLM for LLM API abstraction.

## Common pitfalls

**Adopting a framework too early** — start with direct API calls; add a framework when you outgrow them.

**Using LangChain for everything** — it's general-purpose but over-abstracted for simple cases.

**Mixing frameworks** — pick one and commit. Mixing LangChain + LlamaIndex + custom code is a mess.

**Ignoring observability** — whatever framework you pick, add tracing (LangSmith, Langfuse, Arize).

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[LangGraph]] — the recommended production agent framework.
- [[PydanticAI]] — type-safe agents in Python.
- [[LangChain]] — the general-purpose LLM framework.
- [[LlamaIndex]] — the RAG-focused framework.
- [[OpenAI SDK and Agents SDK]] — the OpenAI-first stack.
- [[AutoGen]] — multi-agent group chat.
- [[CrewAI]] — role-based multi-agent workflows.
- [[Semantic Kernel]] — multi-language, Microsoft-stack.
- [[Haystack]] — production NLP/RAG.
- [[DSPy]] — declarative prompt optimization.
- [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] — the default serving engine.
- [[15 - Agents and Tooling/Frameworks and Tools/TensorRT-LLM|TensorRT-LLM]] — the NVIDIA-optimized serving engine.
- [[TGI]] — the HuggingFace serving engine.
- [[SGLang]] — the agentic-workload serving engine.
- [[Ollama and llama.cpp]] — local LLM runtimes.
- [[RAG Pipeline Overview]] — what a RAG system entails before choosing its framework.
- [[Continuous Batching]]
- [[14 - Inference and Production/Inference/vLLM.md|vLLM]]
