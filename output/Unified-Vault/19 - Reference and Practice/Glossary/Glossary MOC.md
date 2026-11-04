---
title: Glossary MOC
type: overview
aliases: ["Glossary MOC", "Glossary", "28 — Glossary MOC"]
tags: [moc, glossary, reference]
sources: ["28 — Glossary MOC"]
created_index: 3
---

This note is the hub of the glossary, the vault's reference layer for AI engineering vocabulary. The glossary exists for the three lookups that interrupt reading — an unfamiliar term, an unexplained acronym, an ambiguous symbol — and every entry links to the dedicated concept note where one exists, so the glossary doubles as a name-to-note index for the vault. Start here to pick the right glossary note, or use the quick reference below to jump straight to the concept notes behind the most common terms.

## How to use the glossary

The glossary has three notes, one for each kind of lookup, and all three are cross-linked to the concept notes they index. Terms are the default entry point; acronyms and notation cover the cases where the obstacle is an abbreviation or a symbol rather than a word.

### Terms

[[A-Z Terms]] is the comprehensive alphabetical list of AI engineering terms, with concise definitions and links to concept notes. Look the term up, read the one-line definition, and follow the link when the definition is not enough.

### Acronyms

[[Acronyms Index]] is the quick reference for AI acronyms — BPE, GQA, RLHF, and the rest — with expansions and links to the notes that cover them. Reach for it when the acronym itself is the obstacle; expanding it is usually enough to reconnect with the full term entry.

### Notation

[[Notation Conventions]] defines the mathematical and symbolic notation used across the vault: vectors, matrices, attention, probability, calculus, and reinforcement learning. It resolves the ambiguities that arise when the same symbol can mean different things in different notes, and it is the place to check how a formula should be read before decoding it.

## Quick reference: most common terms

The terms below come up most often, grouped by theme. Each links to its dedicated concept note; the definitions behind the names live in [[A-Z Terms]] and [[Acronyms Index]], and the symbols they are written with are fixed by [[Notation Conventions]].

### Attention and transformers

The core vocabulary of the Transformer family: the attention computation itself, the block that packages it, and the variants that make it cheaper to run.

- [[Self-Attention]] · [[Multi-Head Attention]] · [[Transformer Block]] · [[RoPE]] · [[KV Cache Mechanics]] · [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] · [[GQA MQA and MLA]] · [[Sliding Window Attention]] · [[Sparse Attention]]

### Training and fine-tuning

How models are built and adapted: pretraining and its scaling behavior, distributed execution, instruction tuning, and the parameter-efficient and preference-based adaptation methods.

- [[Pretraining Objectives and Scaling Laws]] · [[Distributed Training]] · [[Instruction Tuning and Chat Templates]] · [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] · [[QLoRA]] · [[RLHF with PPO]] · [[DPO Derivation]] · [[Proximal Policy Optimization]]

### Inference and serving

How trained models generate: the cache that makes autoregressive decoding feasible, the memory and precision tricks that make it affordable, and the decoding strategies that shape what comes out.

- [[KV Cache Mechanics]] · [[PagedAttention]] · [[14 - Inference and Production/Inference/vLLM|vLLM]] · [[Quantization]] · [[Speculative Decoding]] · [[Sampling Strategies]]

### Agents and RAG

The vocabulary of systems that act and systems that retrieve: reasoning patterns, tool calls, and the stages of the retrieval pipeline.

- [[ReAct Pattern]] · [[Chain of Thought]] · [[Function Calling]] · [[RAG Pipeline Overview]] · [[Chunking, Hybrid Search, and Reranking]] · [[Advanced RAG Patterns]]

### Production

What it takes to run AI systems for real users: the stack, vector storage, traffic management, safety, observability, and cost.

- [[Production AI Stack]] · [[Vector Storage with pgvector]] · [[Gateway and Router Patterns]] · [[Guardrails]] · [[Production Monitoring]] · [[Cost Optimization]]

### Mathematics

The objects and tools underneath everything: vectors and their products, the information-theoretic quantities, and the optimization machinery.

- [[Vectors]] · [[Dot Product]] · [[Entropy Cross-Entropy and KL Divergence]] · [[Gradient and Chain Rule]] · [[Optimization Essentials]] · [[Adam Optimizer Derivation]]

## See also

- [[A-Z Terms]] — alphabetical glossary of AI engineering terms.
- [[Acronyms Index]] — expansions for the acronyms used across the vault.
- [[Notation Conventions]] — mathematical and symbolic conventions.
- [[Interview Prep MOC]] — the interview-prep question banks, this area's other reference collection.
