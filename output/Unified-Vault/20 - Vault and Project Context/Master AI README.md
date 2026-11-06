---
title: Master AI README
type: reference
aliases: [AI Engineering Obsidian Vault README, Vault README, Collection README]
tags: [readme, navigation, project-context]
sources: ["AI Engineering Obsidian Vault"]
created_index: 10
---

This note archives the collection's README — the introduction that greeted every new reader of the AI engineering vault, stated what the collection is and how to use it, and summarized its status, its thirty-domain structure, its recommended reading orders, its construction protocol, and its quality standards. It documents the collection as it stood at its first iteration and is preserved as project context alongside the other navigation records of the collection's construction.

## What this collection is

A production-quality vault for mastering **AI engineering** — from mathematical foundations through 2026 research frontiers — designed to function as a university curriculum, technical book, research notebook, professional engineering handbook, and internal AI-company knowledge base all at once. The recommended ways in:

- Start at [[Master AI MOC|the master map of content]].
- Or follow the [[Learning Roadmap]] if you want a curriculum order.
- Or jump to any domain in the table below.
- Use Obsidian's graph view to see how concepts connect.
- Every note has YAML frontmatter (`tags`, `created`, `iteration`) so you can query the collection with Dataview or Bases.

## Collection status

At the time of this record the collection stood at **iteration 1 (first iteration — Mode A)**: the foundation was established and the architecture complete (175 folders), with foundational notes generated for the most dependency-critical concepts and many chapters still at "Planned" — the full accounting lives in [[Vault Status Log]]. The collection was **iteratively constructed** by design: each iteration leaves it in a clean, recoverable state, and to resume work the reader was directed to [[Next Iteration Log]], with the running records kept in [[Current Iteration Log]], [[Completed Work Log]], and [[Remaining Work Log]].

## Domains

The collection's thirty numbered domains plus an archives slot, each with its purpose and its status at first iteration. The domain links resolve to the topical area maps where each domain's material now lives.

| #   | Domain                            | Purpose                                                                  | Status            |
|-----|-----------------------------------|--------------------------------------------------------------------------|-------------------|
| 00  | [[Vault Management README\|00 Vault Management]] | Persistent project state — roadmap, status, logs, audits.                | Complete       |
| 01  | [[Foundations MOC\|01 AI Foundations]]       | What AI engineering is; roles; the modern AI stack.                      | Planned        |
| 02  | [[Mathematics MOC\|02 Mathematics]]          | Linear algebra, probability, calculus, optimization, information theory. | Partial        |
| 03  | [[Machine Learning MOC\|03 Machine Learning]]     | Supervised / unsupervised / reinforcement learning, evaluation.          | Planned        |
| 04  | [[Neural Network Foundations MOC\|04 Neural Networks]]      | Perceptrons, MLPs, CNNs, RNNs, training, regularization.                 | Partial        |
| 05  | [[NLP and Language Models MOC\|05 NLP Fundamentals]]     | Tokenization, embeddings, language modeling, pre-transformer NLP.        | Partial        |
| 06  | [[Attention and Transformers MOC\|06 Attention Mechanisms]] | Bahdanau → Luong → self-attention → multi-head → positional → efficient. | Partial        |
| 07  | [[Attention and Transformers MOC\|07 Transformers]]         | The Transformer block, encoder/decoder variants, components.             | Partial        |
| 08  | [[Large Language Models MOC\|08 LLMs]]                 | LLM architecture, context/KV, sampling, evaluation, capabilities.        | Partial        |
| 09  | [[Foundation Models and Multimodal MOC\|09 Foundation Models]]    | Vision, multimodal, embedding, code, reasoning foundation models.        | Planned        |
| 10  | [[Interpretability and Research MOC\|10 Model Architecture Research]] | Per-model architecture analysis (Llama, DeepSeek, GPT, Claude, etc.). |  Planned        |
| 11  | [[Training and Adaptation MOC\|11 Training]]             | Pretraining, alignment, data, distributed training.                      | Planned        |
| 12  | [[Training and Adaptation MOC\|12 Fine-Tuning]]          | PEFT, RLHF, DPO, instruction tuning, distillation.                      | Partial        |
| 13  | [[Inference and Production MOC\|13 Inference]]            | KV cache, decoding, quantization, serving, optimization.                 | Partial        |
| 14  | [[Interpretability and Research MOC\|14 Interpretability]]     | Mechanistic interp, attention analysis, SAEs, probing.                   | Planned        |
| 15  | [[Agents and Tooling MOC\|15 AI Agents]]            | Agent architecture, planning, reasoning, tool calling, autonomy.         | Partial        |
| 16  | [[Agents and Tooling MOC\|16 Multi-Agent Systems]]  | Architectures, communication, coordination, enterprise patterns.         | Planned        |
| 17  | [[Agents and Tooling MOC\|17 RAG]]                  | Ingestion, chunking, retrieval, reranking, evaluation, advanced patterns.| Partial        |
| 18  | [[Agents and Tooling MOC\|18 Memory Systems]]       | Memory types, architectures, operations, vector/KG memory.               | Planned        |
| 19  | [[Agents and Tooling MOC\|19 MCP]]                  | Model Context Protocol — architecture, components, security, integration.| Planned        |
| 20  | [[Inference and Production MOC\|20 AI Infrastructure]]    | Serving, storage, messaging, compute, observability.                     | Planned        |
| 21  | [[Inference and Production MOC\|21 LLMOps and MLOps]]     | Pipelines, monitoring, evaluation, deployment, cost optimization.        | Planned        |
| 22  | [[Inference and Production MOC\|22 Production AI]]        | Reference architectures, reliability, security, scaling, patterns.       | Planned        |
| 23  | [[Foundation Models and Multimodal MOC\|23 Multimodal AI]]        | Vision-language, audio, video, diffusion, fusion architectures.          | Planned        |
| 24  | [[Interpretability and Research MOC\|24 Research Frontiers]]   | SSMs, hybrids, reasoning, long-context, efficiency, 2026 emerging.       | Planned        |
| 25  | [[Agents and Tooling MOC\|25 Frameworks and Tools]] | LangChain, LangGraph, vLLM, Ollama, vector DBs, etc.                     | Planned        |
| 26  | [[Papers MOC\|26 Papers]]               | Landmark papers — Bahdanau → 2026.                                       | Planned        |
| 27  | [[Projects MOC\|27 Projects]]             | Implementations, mini-projects, capstones.                               | Planned        |
| 28  | [[Glossary MOC\|28 Glossary]]            | A–Z glossary, acronyms, notation conventions.                            | Planned        |
| 29  | [[Interview Prep MOC\|29 Interview Prep]]       | Conceptual, system design, coding interview banks.                       | Planned        |
| 99  | (Archives)                        | Superseded / deprecated content.                                         | Planned        |

## Recommended reading orders

Three orders were recommended from the door — a full curriculum order and two role-based shortcuts — and the same orders, with their alternatives, are carried in [[Reading Orders]].

### Curriculum order (beginner → advanced)

1. [[Foundations MOC|01 AI Foundations]]
2. [[Mathematics MOC|02 Mathematics]]
3. [[Machine Learning MOC|03 Machine Learning]]
4. [[Neural Network Foundations MOC|04 Neural Networks]]
5. [[NLP and Language Models MOC|05 NLP Fundamentals]]
6. [[Attention and Transformers MOC|06 Attention Mechanisms]]
7. [[Attention and Transformers MOC|07 Transformers]]
8. [[Large Language Models MOC|08 LLMs]]
9. [[Training and Adaptation MOC|11 Training]] → [[Training and Adaptation MOC|12 Fine-Tuning]]
10. [[Inference and Production MOC|13 Inference]]
11. [[Agents and Tooling MOC|15 AI Agents]] → [[Agents and Tooling MOC|16 Multi-Agent Systems]]
12. [[Agents and Tooling MOC|17 RAG]] → [[Agents and Tooling MOC|18 Memory Systems]] → [[Agents and Tooling MOC|19 MCP]]
13. [[Inference and Production MOC|20 AI Infrastructure]] → [[Inference and Production MOC|21 LLMOps and MLOps]] → [[Inference and Production MOC|22 Production AI]]
14. [[Foundation Models and Multimodal MOC|23 Multimodal AI]]
15. [[Interpretability and Research MOC|24 Research Frontiers]]
16. [[Interpretability and Research MOC|10 Model Architecture Research]]
17. [[Papers MOC|26 Papers]]
18. [[Projects MOC|27 Projects]]
19. [[Interview Prep MOC|29 Interview Prep]]

### Researcher path (frontier-focused)

1. [[Attention and Transformers MOC|06 Attention Mechanisms]] (full)
2. [[Attention and Transformers MOC|07 Transformers]]
3. [[Interpretability and Research MOC|24 Research Frontiers]]
4. [[Interpretability and Research MOC|10 Model Architecture Research]]
5. [[Papers MOC|26 Papers]]

### Engineer path (production-focused)

1. [[Large Language Models MOC|08 LLMs]]
2. [[Inference and Production MOC|13 Inference]]
3. [[Agents and Tooling MOC|15 AI Agents]]
4. [[Agents and Tooling MOC|17 RAG]]
5. [[Agents and Tooling MOC|19 MCP]]
6. [[Inference and Production MOC|20 AI Infrastructure]]
7. [[Inference and Production MOC|21 LLMOps and MLOps]]
8. [[Inference and Production MOC|22 Production AI]]
9. [[Agents and Tooling MOC|25 Frameworks and Tools]]

## Construction protocol

The collection follows an iterative construction protocol, defined in its "What to do" construction document:

- **Mode A (first iteration):** architect the system, establish the roadmap, build foundations.
- **Mode B (subsequent):** recover state from the project-state records, continue from where the previous iteration stopped.

See [[Vault Management README]] for the protocol as kept in the project-state area, and [[Master Roadmap]] for the coverage tree each iteration worked against.

## Quality standards

Every concept note in the collection was held to a fixed set of standards:

- One coherent concept per note.
- YAML frontmatter (`tags`, `created`, `iteration`).
- A fixed internal arc — definition → intuition → motivation → internal operation → (math when applicable) → code example → production implications → cross-links.
- Mermaid diagrams where they aid understanding.
- Wikilinks to at least 3 related notes.
- Closed-source model claims labeled per ADR-006, the source-labelling convention for closed-source model architectures.
- No fabrication. No placeholders presented as final content.

The full set of standards is recorded in [[Architecture Decisions Log]].

## Where the collection came from

The collection was built from two governing documents — an "Ultimate Prompt" that specified its scope and standards, and the "What to do" protocol that specified the iterative construction procedure — which together defined the vault's architecture, quality bar, and working method. The record's own source line is preserved verbatim (repository name typo sic): built from `Ultimate Prompt.md` and `What to do.md` in the [ObsidainAgentGithubUplaod](https://github.com/Vtheonly/ObsidainAgentGithubUplaod) repository.

## See also

- [[Master AI MOC]] — the front-door map of content this README pointed to first.
- [[Master Roadmap]] — the complete intended coverage tree behind the domain table.
- [[Learning Roadmap]] — the curriculum path through the domains.
- [[Reading Orders]] — the alternative reading orders in full.
- [[Master AI Index]] — the collection's master index record.
- [[Vault Management README]] and [[Architecture Decisions Log]] — construction protocol, project state, and standards.
