---
title: Reading Orders
type: reference
aliases: [Reading Order, Alternative Reading Orders]
tags: [reference, navigation, roadmap, reading-order, vault-context]
sources: ["Reading Order"]
created_index: 13
---

This note archives the collection's goal-tailored reading orders: five alternative routes through the material, each tuned to a different kind of reader, from the frontier-tracking researcher to the complete newcomer. Drafted in iteration 1 of the collection's curation (2026-08-07), they are preserved here as project context — a record of how the collection was meant to be navigated once a reader's goal was known. The canonical curriculum order remains the [[Learning Roadmap]]; every path below is an alternative to it, not a replacement.

## The orders and the canonical path

Each path is a numbered route through the collection's sections, quoted exactly as drafted, and each closes with its original time estimate. The section numbers are the collection's archival numbering, kept the way the orders were written; the paths deliberately overlap — attention, transformers and LLMs appear in nearly all of them — but they differ in what they skip, what they emphasize, and where they start. A reader who wants the single canonical sequence should simply follow the [[Learning Roadmap]]; [[Master AI MOC]] remains the master map of content, and the collection's top-level plan is [[Master Roadmap]].

## Path A — Researcher (frontier-focused)

For someone who already knows the basics and wants to track the bleeding edge.

```text
1.  06 Attention Mechanisms (full, including efficient + long-context)
2.  07 Transformers (full)
3.  10 Model Architecture Research (per-model deep dives)
4.  24 Research Frontiers
5.  26 Papers (in chronological order)
6.  00 Vault Management/Research Queue (open questions)
```

Estimated time: ongoing (this is a lifestyle, not a phase).

The route skips the foundations entirely and heads straight for the frontier: the attention and transformers material in full, efficient and long-context variants included, then per-model architecture deep dives, the research frontiers, the papers in chronological order via [[Papers MOC]], and finally the open questions tracked in the [[Research Queue]]. The estimate is the message: for a researcher, reading is not a phase to finish but a practice to maintain.

## Path B — Engineer (production-focused)

For someone building LLM applications in production.

```text
1.  08 LLMs (capabilities + limitations)
2.  13 Inference (KV cache, sampling, serving, quantization)
3.  15 AI Agents (architecture, tool calling, patterns)
4.  17 RAG (full pipeline)
5.  18 Memory Systems
6.  19 MCP
7.  25 Frameworks and Tools
8.  20 AI Infrastructure
9.  21 LLMOps and MLOps
10. 22 Production AI
```

Estimated time: 4–6 months part-time.

The sequence starts with what LLMs can and cannot do, moves to the serving side of inference — [[KV Cache Mechanics]], [[Sampling Strategies]], [[Quantization]] — then through agent architecture and tool calling, the full retrieval-augmented generation pipeline ([[RAG Pipeline Overview]]), memory systems, and MCP ([[MCP Overview]]), before closing with the industrial tail: frameworks and tools, infrastructure, LLMOps ([[LLMOps vs MLOps]]), and production practice.

## Path C — Interview Candidate

For someone preparing for AI/ML/LLM engineering interviews.

```text
1.  29 Interview Prep (start here — identify gaps)
2.  28 Glossary (drill terms)
3.  06 Attention Mechanisms (most-asked topic)
4.  07 Transformers
5.  08 LLMs (capabilities + limitations)
6.  13 Inference (KV cache, sampling, quantization)
7.  12 Fine-Tuning (LoRA, RLHF, DPO)
8.  17 RAG (pipeline + evaluation)
9.  15 AI Agents (ReAct, tool calling, function calling)
10. 19 MCP (current state)
11. 22 Production AI (system design)
12. 27 Projects (have something to talk about)
```

Estimated time: 4–8 weeks of focused prep.

The path opens at the interview-prep hub ([[Interview Prep MOC]]) to identify gaps, then drills glossary terms ([[Glossary MOC]]) before marching through the most-asked topics in order: attention — the most-asked topic of them all — transformers, LLM capabilities and limitations, inference mechanics, fine-tuning ([[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], RLHF, [[DPO Derivation]]), the RAG pipeline and its evaluation, agent patterns ([[ReAct Pattern]], tool calling, [[Function Calling]]), the current state of MCP, and production system design. It ends at projects, so the candidate has something to talk about.

## Path D — Newcomer (from zero)

For someone with no ML background.

```text
1.  01 AI Foundations (orientation)
2.  02 Mathematics (linear algebra, probability, calculus, optimization)
3.  03 Machine Learning (supervised, evaluation)
4.  04 Neural Networks (MLPs, backprop)
5.  05 NLP Fundamentals (tokenization, embeddings)
6.  06 Attention Mechanisms (Bahdanau → self-attention → multi-head)
7.  07 Transformers (the block)
8.  08 LLMs (decoder-only, KV cache, sampling)
9.  → continue with Learning Roadmap
```

Estimated time: 6–9 months part-time.

This is the on-ramp: orientation in AI foundations, the mathematics (linear algebra, probability, calculus, optimization), machine learning (supervised learning, evaluation), neural networks (MLPs, [[Backpropagation]]), NLP fundamentals (tokenization — [[Tokenization Overview]] — and embeddings), the attention story from [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]] through [[Self-Attention]] to [[Multi-Head Attention]], the transformer block itself ([[Transformer Block]]), and finally LLMs. Step nine hands the reader off to the [[Learning Roadmap]] to continue.

## Path E — Paper-First Learner

For someone who learns best by reading original papers.

```text
1.  26 Papers (in chronological order)
2.  For each paper, read the corresponding concept note(s) in the vault
3.  Implement the paper's key idea as a small project in 27 Projects
4.  Repeat
```

This path requires solid math and ML foundations. If you struggle with a paper, drop down to the relevant concept note in 02–08.

The path is a loop rather than a line: read the papers in chronological order ([[Papers MOC]]), read the corresponding concept notes for each paper, implement the paper's key idea as a small project ([[Projects MOC]]), and repeat. The caveat matters — "02–08" is the archival span from the mathematics section through the LLMs section, so a struggling reader drops down to the foundations rather than pushing through.

## Choosing a path

The five estimates make the trade-off between the paths explicit:

| Path | Built for | Estimated time |
| --- | --- | --- |
| A — Researcher | Already knows the basics; tracks the bleeding edge | Ongoing (a lifestyle, not a phase) |
| B — Engineer | Building LLM applications in production | 4–6 months part-time |
| C — Interview candidate | AI/ML/LLM engineering interviews | 4–8 weeks of focused prep |
| D — Newcomer | No ML background | 6–9 months part-time |
| E — Paper-first learner | Learns best from original papers | Not estimated; the loop ends with "Repeat" |

Paths B and D are the closest to a full curriculum and carry the longest fixed timelines; C is a focused sprint; A and E assume foundations and, by design, never really end.

## See also

- [[Learning Roadmap]] — the canonical curriculum order
- [[Master Roadmap]] — the collection's top-level plan
- [[Master AI MOC]] — the master map of content
- [[Master AI Index]] — the archived alphabetical index of concept notes
- [[Master AI README]]
