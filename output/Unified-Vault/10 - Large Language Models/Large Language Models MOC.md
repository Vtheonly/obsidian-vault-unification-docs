---
title: Large Language Models MOC
type: overview
aliases: [LLMs MOC, LLM MOC, Large Language Models Map of Content, Large Language Models Overview]
tags: [llm, moc, overview]
sources: ["08 — LLMs MOC"]
created_index: 5
---

This note is the orientation map for the large language models area: it indexes the six content notes, orders them into a teaching sequence, and connects them to the neighbouring areas they depend on. The sequence follows a deliberate arc — the architecture LLMs are built on, the machinery that makes generating with them feasible, the capability that makes them general-purpose, the failure mode that blocks production adoption, and the benchmarks that measure all of it. Read the table in order for a first pass through the area, or jump straight to the sub-family you need.

> [!info] Large Language Models — what they are, how they work, how to use them, and where they fail.

## Reading order

The area holds seven notes: this map plus the six content notes it indexes, sequenced so that each note supplies the prerequisites for the next. The map itself is the entry point; the six siblings are the substance.

| # | Note | Sub-family | Purpose |
|---|------|------------|---------|
| 00 | Large Language Models MOC (this note) | Orientation | The area map: reading order, sub-families, and neighbouring areas. |
| 01 | [[Decoder-Only Architecture]] | Architecture | Modern LLM recipe. |
| 02 | [[KV Cache Mechanics]] | Context & KV Cache | What makes autoregressive generation feasible. |
| 03 | [[Sampling Strategies]] | Sampling | How to turn logits into tokens. |
| 04 | [[In-Context Learning]] | Capabilities | Few-shot learning; what makes LLMs general. |
| 05 | [[Hallucination]] | Limitations | The biggest production blocker. |
| 06 | [[LLM Benchmarks]] | Evaluation | MMLU, GPQA, HumanEval, MATH, Chatbot Arena. |

The order is not arbitrary. The architecture note defines the object; the KV cache and sampling notes define how it generates; in-context learning defines why it is useful; hallucination defines where it breaks; and the benchmarks define how any of it is measured.

## Sub-families

The area divides into six sub-families, one per content note, and the names below are the ones used in the reading-order table.

**Architecture** (note 01) — [[Decoder-Only Architecture]] is the modern LLM recipe: causal self-attention plus next-token prediction, the shared skeleton of GPT, Llama, Mistral, Qwen, and DeepSeek, together with the component stack, parameter and FLOPs accounting, and the reasons decoder-only displaced encoder-decoder.

**Context & KV Cache** (note 02) — [[KV Cache Mechanics]] explains what makes autoregressive generation feasible: the cached keys and values that stop every step from recomputing the whole context, the memory-sizing formulas, GQA/MQA/MLA, prefill versus decode, and the serving optimizations built on the cache.

**Sampling** (note 03) — [[Sampling Strategies]] covers how to turn logits into tokens: greedy decoding, beam search, temperature, top-k, top-p (nucleus), min-p, repetition penalties, and the recipes production APIs actually default to.

**Capabilities** (note 04) — [[In-Context Learning]] is the few-shot property that makes LLMs general: new tasks learned from prompt examples alone, with no weight updates, implemented by induction heads and traded off against fine-tuning and retrieval.

**Limitations** (note 05) — [[Hallucination]] is the biggest production blocker: confident fabrication with structural root causes, the taxonomy of its forms and severity levels, and the layered mitigations — RAG, prompting, fine-tuning, verification, calibration, tool use — that reduce but never eliminate it.

**Evaluation** (note 06) — [[LLM Benchmarks]] is the measurement layer: MMLU, GPQA, HumanEval, MATH, BBH, Chatbot Arena and the wider specialized landscape, plus the pitfalls — contamination, saturation, judge bias — that decide how much a score should be trusted.

## Why this area matters

Large language models are the point at which deep learning became a general-purpose technology: one pretrained model, applied to almost any language task through a prompt. That generality has a specific anatomy, and each note in this area carries one load-bearing piece of it — generation is feasible because of the KV cache, controllable through sampling, useful because of in-context learning, and only as trustworthy as hallucination mitigation and honest benchmark reading make it. Anyone selecting a model, writing prompts, tuning a decoding recipe, or shipping a feature on top of an LLM is working inside the territory this area maps.

The area also sits at the junction of its neighbours. The Transformer machinery underneath every note here is the subject of [[Attention and Transformers MOC]], and the language-modeling lineage that produced the LLM is mapped in [[NLP and Language Models MOC]]. What happens before deployment — pretraining objectives, scaling laws, fine-tuning, alignment — belongs to [[Training and Adaptation MOC]]; what happens after — serving engines, batching, quantization, monitoring — belongs to [[Inference and Production MOC]].

## See also

The six notes of this area, in reading order:

- [[Decoder-Only Architecture]] — the modern LLM recipe.
- [[KV Cache Mechanics]] — what makes autoregressive generation feasible.
- [[Sampling Strategies]] — how to turn logits into tokens.
- [[In-Context Learning]] — few-shot learning; what makes LLMs general.
- [[Hallucination]] — the biggest production blocker.
- [[LLM Benchmarks]] — MMLU, GPQA, HumanEval, MATH, Chatbot Arena.

The neighbouring area maps:

- [[Attention and Transformers MOC]] — the architecture.
- [[NLP and Language Models MOC]] — the modeling lineage that produced the LLM.
- [[Training and Adaptation MOC]] — pretraining, fine-tuning, and alignment.
- [[Inference and Production MOC]] — running LLMs in production.

Two further directions extend the same material beyond this area's notes: per-model deep dives into the architectural specifics of individual model families, and using LLMs as agents, where the capabilities and limitations mapped above become the operating constraints of tool-using systems.
