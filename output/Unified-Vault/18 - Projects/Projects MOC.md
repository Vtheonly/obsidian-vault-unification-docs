---
title: Projects MOC
type: overview
aliases: [Projects Map of Content, 27 Projects MOC, Implementation Projects MOC]
tags: [moc, projects, implementation]
sources: ["27 — Projects MOC"]
created_index: 25
---

This area is the vault's workshop: 24 hands-on projects in which the concepts studied elsewhere get built from scratch, because building from scratch is the best way to verify you understand a concept — reading papers and using frameworks leaves gaps. The projects are organized into three tiers that double as a difficulty progression: two mini-projects that build complete working systems at the smallest useful scope, four from-scratch implementations of core model internals, and eighteen end-to-end capstones that assemble production-style systems. The suggested path runs from the mini-projects through the implementations to the capstones, and each section below states its theme, background, and recommended order.

## How this area is organized

Three folders, three tiers. **Mini-Projects** holds the two smallest builds, each a complete system small enough to hold in your head. **Implementations** holds the four from-scratch model builds — attention and the Transformer, a Mixture-of-Experts layer, a nanoGPT-style trainer, and a Mamba-style state space model. **Capstones** holds the remaining eighteen projects, each an end-to-end system that combines several sub-domains at once.

The collection started with three founding projects — the Transformer built from scratch, the mini RAG pipeline, and the mini agent — and grew in waves to its current total of 24: first the mini MoE, the tiny LLM trainer, and the multi-agent system; then the reasoning model fine-tune, the MCP server, the mini SSM, and the vision-language model; then four more capstones in the distributed training pipeline, the code agent, the RAG evaluation harness, and the multimodal RAG pipeline; then five more in the multimodal agent, the speculative decoding server, the quantization toolkit, the MCP marketplace, and the fine-tuning pipeline with LoRA and DPO; and finally the five newest — the RLHF pipeline with PPO, the knowledge-graph construction pipeline (GraphRAG), the long-context evaluation harness, the agent observability platform, and the model distillation pipeline.

## Mini-projects

The entry tier, and the recommended starting point for the area. Both projects build a complete, working system with no framework and no abstractions, and both exist to make an entire category of software transparent — once you have built one, the frameworks that wrap the same ideas stop being magic. Either project works as a first build; the recommended order takes the RAG pipeline first, and the agent second.

[[Build a Mini RAG Pipeline]] implements the full retrieval-augmented generation pipeline — ingestion, chunking, embedding, retrieval, and generation — so that every component of the RAG family, starting from [[RAG Pipeline Overview]], becomes transparent. [[Build a Mini Agent]] implements the ReAct loop — reasoning interleaved with acting — with web search and calculator tools, the same loop described in [[ReAct Pattern]] that every agent framework wraps.

## Implementations

The from-scratch tier: four builds that reconstruct core model internals with no framework. These are the projects where claims of understanding get tested, and they assume the theory they implement — the attention and Transformer material especially. The recommended order is attention first, then the MoE layer, then the trainer, then the state space model.

[[Build Attention and Transformer From Scratch]], the founding project of the whole area, walks from attention through multi-head attention (MHA) to a full Transformer block and a mini-GPT — the hands-on counterpart of [[Self-Attention]] and [[Multi-Head Attention]]. [[Build a Mini MoE]] builds a Mixture-of-Experts layer with routing and auxiliary loss, the mechanism that clarifies how [[Mixture of Experts]] works in Mixtral and DeepSeek-V3 — and, by inference, in GPT-4. [[Build a Tiny LLM Trainer]] is a nanoGPT-style training loop with a learning-rate schedule: the full training recipe, from data to model to optimizer, in one small codebase. [[Build a Mini SSM]] builds a Mamba-style selective state space model, putting the ideas of [[Mamba]] into running code.

## Capstones

The top tier: eighteen end-to-end, production-style systems, each combining several sub-domains at once — an agent capstone draws on the agents families, a training capstone on training and adaptation, an efficiency capstone on inference. They group into the five themes below; a complete linear walk of the capstones runs from the multi-agent system through to the model distillation pipeline, and the thematic grouping is for orientation, so enter through whichever theme matches the system you need to build.

### Agents and tooling

Five capstones on the agent stack. [[Build a Multi-Agent System]] builds hierarchical orchestration — a planner plus specialized executors with a synthesis step — the pattern used in production and the hands-on counterpart of [[Multi-Agent Architectures]]. [[Build an MCP Server]] exposes resources, prompts, and tools via the MCP protocol, the three primitives behind [[MCP Overview]]. [[Build a Code Agent]] is a SWE-bench-style agent that navigates a repository, edits code, and runs tests. [[Build an MCP Marketplace]] builds a registry for publishing and discovering MCP servers, with security scanning against the supply-chain concerns of [[MCP Security]]. [[Build an Agent Observability Platform]] assembles a tracing SDK, a collector, anomaly detection, and a UI — the foundation of production debugging, and the hands-on counterpart of the [[Observability Stack]].

### Training, alignment, and distillation

Five capstones on the training side. [[Build a Reasoning Model Fine-Tune]] applies GRPO with verifiable rewards in an R1-style recipe. [[Build a Distributed Training Pipeline]] runs FSDP across multiple GPUs with mixed precision and checkpointing, the practice behind [[Distributed Training]]. [[Build a Fine-Tuning Pipeline with LoRA and DPO]] is the end-to-end SFT + DPO pipeline — [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], QLoRA ([[QLoRA]]), merging, and deployment. [[Build an RLHF Pipeline with PPO]] builds the canonical deep-alignment recipe, SFT → RM → PPO, InstructGPT-style; its theory lives in [[RLHF with PPO]]. [[Build a Model Distillation Pipeline]] implements response, logit, and feature distillation from teacher to student — the canonical recipe for compressing a frontier model.

### Multimodal systems

Three capstones on the multimodal stack, grounded in [[Multimodal AI Overview]]. [[Build a Vision-Language Model]] is LLaVA-style: a vision encoder, a projection layer, and an LLM. [[Build a Multimodal RAG Pipeline]] retrieves with CLIP embeddings and generates with a VLM — cross-modal retrieval. [[Build a Multimodal Agent]] combines VLM perception with a planner and vision tools.

### Retrieval, knowledge graphs, and evaluation

Three capstones on retrieval and its measurement. [[Build a RAG Evaluation Harness]] measures retrieval, generation, and end-to-end metrics, RAGAS-style. [[Build a Knowledge-Graph Construction Pipeline]] does entity and relation extraction into Neo4j with hybrid retrieval — the GraphRAG approach, showing how knowledge graphs complement vector RAG (see [[Advanced RAG Patterns]]). [[Build a Long-Context Evaluation Harness]] runs needle-in-haystack, multi-needle, and multi-hop probes with a heatmap, the tool for validating claims about million-token models alongside [[Long-Context Architectures]].

### Inference and efficiency

Two capstones on serving efficiency. [[Build a Speculative Decoding Server]] implements EAGLE-2 speculative decoding on [[14 - Inference and Production/Inference/vLLM|vLLM]] for a 2–4x speedup, the technique behind [[Speculative Decoding]]. [[Build a Quantization Toolkit]] covers INT4, INT8, and FP8 via GPTQ, AWQ, and bitsandbytes, with quality and latency benchmarks — the practice of [[Quantization]].

## Why this area matters

Implementing from scratch is the only way to verify genuine understanding; reading papers and using frameworks leaves gaps, and a build is where those gaps surface. Beyond the general principle, each project buys a specific piece of transparency. The mini RAG project covers the full RAG pipeline, so every component of the retrieval family becomes transparent. The mini agent covers the ReAct loop, so every agent framework does. The mini MoE project shows how Mixture-of-Experts actually works, clarifying Mixtral, DeepSeek-V3, and GPT-4 (inferred). The tiny LLM trainer shows the full training recipe, from data to model to optimizer. The multi-agent capstone shows hierarchical agent orchestration, the pattern used in production. The RLHF pipeline shows the canonical deep-alignment recipe, InstructGPT-style. The GraphRAG pipeline shows how knowledge graphs complement vector RAG. The long-context evaluation harness validates claims about million-token models. The agent observability platform is the foundation of production debugging. And the model distillation pipeline is the canonical way to compress a frontier model into a smaller one.

## Production implications

The builds in this area are deliberately minimal, and that is the point: start with these minimal implementations, then swap components for production-grade alternatives — vLLM, [[Vector Storage with pgvector|pgvector]], LangSmith — once you understand what each piece does. Always include evaluation; a RAG or agent system without an eval set cannot be improved safely, which is why two of the capstones are evaluation harnesses. The mini agent's error handling and tracing patterns are the foundation of production agent systems. The MoE project's naive implementation is for learning; production MoE requires expert parallelism and kernel fusion. And distillation, RLHF, and long-context evaluation are the highest-ROI projects for production teams — they directly reduce cost and improve quality.

## Future expansion

Five projects are planned to extend the collection next:

- A continuous pretraining pipeline — continued pretraining on a new domain.
- A multimodal reasoning model — vision plus reasoning training.
- An MCP-based agent platform — multi-server, multi-tenant.
- An automated red-team pipeline — systematic prompt injection testing.
- A model routing system — cost-aware routing across multiple models.

## See also

- [[Attention and Transformers MOC]] — the theory that the from-scratch Transformer and attention build reconstructs.
- [[Training and Adaptation MOC]] — the fine-tuning, RLHF, and distributed-training theory behind the training capstones.
- [[Inference and Production MOC]] — the serving, quantization, speculative decoding, and observability theory behind the efficiency capstones.
- [[Agents and Tooling MOC]] — the agent, RAG, and MCP families behind the agent capstones.
- [[Foundation Models and Multimodal MOC]] — the multimodal theory behind the vision-language and multimodal RAG capstones.
- [[Machine Learning MOC]] — the reinforcement-learning foundations, PPO included, under the alignment capstones.
- [[Large Language Models MOC]] — the LLM foundations under the tiny trainer and the fine-tuning pipelines.
- [[Interpretability and Research MOC]] — the research frontier, state space models and long context, that the mini SSM and long-context harness touch.
- [[Projects MOC]]
