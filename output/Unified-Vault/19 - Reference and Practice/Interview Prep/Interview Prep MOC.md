---
title: Interview Prep MOC
type: overview
aliases: ["Interview Prep MOC", "Interview Preparation MOC", "29 — Interview Prep MOC"]
tags: [moc, interview, interview-prep, reference]
sources: ["29 — Interview Prep MOC"]
created_index: 7
---

This note orients interview preparation for AI engineering roles. AI engineering interviews have converged on three question types — conceptual, system design, and coding — and this collection indexes the three question banks that cover them, from screening-level fundamentals through senior-level material on reasoning models, vision-language models, MCP, quantization, and the 2026 frontier architectures. Start here to pick a bank and a reading order; each bank is self-contained and links to the concept notes behind its questions.

## Reading order

Work through the banks in their numbered order — conceptual, then system design, then coding — because the concepts must be understood before they can be designed around or implemented. Each bank itself runs from core to advanced, so a full preparation pass covers the conceptual fundamentals, the three most common system design questions and the four core coding implementations, then the advanced design prompts, the senior-level conceptual questions, and finally the advanced from-scratch implementations.

| # | Note | Sub-domain | Purpose |
|---|------|------------|---------|
| 01 | [[Conceptual Interview Questions]] | Conceptual | Attention, training, fine-tuning, and RAG conceptual Q&A, extending through reasoning models, VLMs, MCP, GRPO, hybrid architectures, scaling, speculative decoding, quantization, DPO variants, GraphRAG, long-context, and the 2026 frontier architectures. |
| 02 | [[System Design Interview Questions]] | System design | Multi-tenant RAG, LLM serving, and agent platform design, plus reasoning model serving, VLM deployment, MCP-based agent platforms, and multi-agent production systems. |
| 03 | [[Coding Interview Questions]] | Coding | Attention, MHA, sampling, and RoPE from scratch, plus the GRPO loss, patch embedding, MCP server, MoE routing, PagedAttention, and INT4 quantization, and the newer YaRN, GQA, RoPE scaling, KV cache compression, EAGLE-2 speculative decoding, and GPTQ quantization implementations. |

## The three banks

The collection splits into three sub-domains — conceptual, system design, and coding — with one bank per sub-domain. Every question links to the concept note that backs it, so working the banks doubles as a guided tour of the vault's concept coverage.

### Conceptual questions

[[Conceptual Interview Questions]] is the conceptual bank: common questions with concise answers and pointers to the concept notes that treat each topic in depth. Coverage runs from attention and Transformers, LLM training, inference, fine-tuning, RAG, and agents through the senior-level material — reasoning models, vision-language models, MCP, memory systems, multi-agent patterns, interpretability, scaling laws, quantization, DPO variants, GraphRAG, long-context behavior, and the 2026 frontier architectures — and the senior-level material alone adds 25+ Q&A. Questions are grouped topically and range from fundamentals to senior-level depth, so the same bank serves screening rounds and senior AI engineering interviews alike.

### System design questions

[[System Design Interview Questions]] is the system design bank. The three most common LLM system design prompts — design a multi-tenant RAG platform, design an LLM serving system, and design an agent platform — are joined at the senior level by four advanced prompts covering reasoning-model serving, Vision-Language Model deployment, MCP-based agent architectures, and multi-agent production systems. Each question draws on the same core components (model serving, vector storage, prompt management, observability) with a different emphasis, and each is worked through with requirements clarification, architecture, key decisions, cost arithmetic, failure handling, and a scale-up plan.

### Coding questions

[[Coding Interview Questions]] is the coding bank: sixteen from-scratch PyTorch implementations, each doable in 20–50 lines. The four most common — scaled dot-product attention, multi-head attention, top-k/top-p sampling, and the KV cache — are joined by the advanced engineering topics that distinguish a senior AI engineer from a junior one (the GRPO loss, VLM patch embedding, MCP tool servers, MoE routing, PagedAttention, and INT4 quantization — depth, not breadth) and by the newer exercises (YaRN, GQA, NTK-aware RoPE scaling, KV cache compression, EAGLE-2 speculative decoding, and GPTQ quantization). Every entry keeps the problem statement, the math it implements, a reference solution with tests, the key implementation details, the common pitfalls, and the follow-up questions an interviewer is likely to ask.

## Why this matters for AI

Each bank exists because of what its question type filters for:

- AI engineering interviews have converged on three question types: conceptual (do you understand the concepts?), system design (can you architect a production system?), and coding (can you implement core components?).
- The system design questions test integration knowledge: how do serving, retrieval, caching, monitoring, and cost optimization fit together?
- The coding questions test depth: can you implement attention, sampling, RoPE, and the KV cache from scratch? If you can, you understand them; if you can't, you don't.
- Coverage extends to the newer topics as well: reasoning models, VLMs, MCP, GRPO, hybrid architectures, scaling laws, speculative decoding, quantization, DPO variants, GraphRAG, long-context, and the 2026 frontier architectures.

## Production implications

Three habits carry across both the design and the coding rounds:

- For system design: always address cost and quality explicitly. Most candidates focus only on latency and miss these.
- For coding: know the shapes. Most bugs in attention implementations are shape errors.
- For both: have a scale-up plan. Show how the design evolves from 1K to 1M users.

## Common interview topics

The mapping below connects each interview topic to the concept notes that back it. The first group is the long-standing core of AI engineering interviews; the second is the newer material, with each entry annotated by the bank question that exercises it.

### Core topics

| Topic | Key concept notes |
|-------|-------------------|
| Attention | [[Self-Attention]], [[Multi-Head Attention]] |
| Transformers | [[Transformer Block]], [[08 - Attention and Transformers/Transformer Architecture/BERT\|BERT]] |
| LLMs | [[Decoder-Only Architecture]], [[LLM Benchmarks]] |
| Fine-tuning | [[13 - Training and Adaptation/Fine-Tuning/LoRA\|LoRA]], [[RLHF with PPO]] |
| Inference | [[KV Cache Mechanics]], [[14 - Inference and Production/Inference/vLLM\|vLLM]], [[Continuous Batching]] |
| Agents | [[ReAct Pattern]], [[Function Calling]] |
| RAG | [[RAG Pipeline Overview]], [[Chunking, Hybrid Search, and Reranking]] |
| Production | [[LLM Security and Prompt Injection]] |

### Newer topics

- **Reasoning models** — [[Reasoning Models]]; exercised by the GRPO loss question in the coding bank and reasoning-model serving in the system design bank.
- **Vision-language models** — [[LLaVA]]; exercised by the VLM patch-embedding question in the coding bank and VLM deployment in the system design bank.
- **MCP** — [[MCP Overview]]; exercised by the MCP server implementation in the coding bank and the MCP platform question in the system design bank.
- **Multi-agent systems** — [[Multi-Agent Architectures]]; exercised by the multi-agent production systems question in the system design bank.
- **Mixture of experts** — [[Mixture of Experts]]; exercised by the MoE routing question in the coding bank.
- **KV cache paging** — [[PagedAttention]]; exercised by the PagedAttention question in the coding bank.
- **Quantization** — [[Quantization]]; exercised by the INT4 quantization question in the coding bank.
- **YaRN and RoPE scaling** — [[YaRN and NTK-Aware Scaling]]; exercised by the YaRN and NTK-aware RoPE-scaling questions in the coding bank.
- **GQA** — [[GQA MQA and MLA]]; exercised by the grouped-query attention question in the coding bank.
- **Speculative decoding** — [[Speculative Decoding]]; exercised by the EAGLE-2 speculative decoding question in the coding bank.
- **GraphRAG** — asked in the conceptual bank's senior-level material.
- **Long-context evaluation** — asked in the conceptual bank's senior-level material.
- **2026 frontier architectures** — [[Frontier Model Synthesis 2026]]; asked in the conceptual bank's senior-level material.
- **DPO variants** — [[DPO Derivation]]; asked in the conceptual bank's senior-level material.
- **Hybrid architectures** — [[SSMs Mamba and Frontiers]]; asked in the conceptual bank's senior-level material.

## See also

- [[Glossary MOC]] — this area's other reference collection: term, acronym, and notation lookups for every concept named in the banks.
- [[Build Attention and Transformer From Scratch]] — hands-on build of the Transformer components the coding bank tests.
- [[Build a Mini RAG Pipeline]] — hands-on build of the retrieval pipeline behind the RAG design prompts.
- [[Build a Mini Agent]] — hands-on build of the agent loop behind the agent-platform design prompt.
