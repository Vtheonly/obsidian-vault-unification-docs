---
title: Research Queue
type: reference
aliases: [Research Queue, Open Research Questions]
tags: [vault-management, research-queue, project-context, evidence-labels]
sources:
  - "Research Queue"
created_index: 15
---

This note preserves the collection's research queue as it stood at the close of iteration 13 (dated 2026-08-08): the open research questions and unresolved factual claims that had to be resolved — or explicitly labeled as inference — before the corresponding note could be marked `Complete`. Every item carries an evidence-status label, from **Officially Confirmed** through **Strongly Inferred** and **Research-Backed** down to **Insufficient public evidence**, because the project's architecture decision ADR-006 requires every claim about a closed-source model to be labeled. The queue is the reason the model-architecture and research-frontier notes read the way they do: it records what was known, what was inferred, and what was deliberately left unverified, item by item. Checked items are resolved; unchecked items were still open at the record date.

## How the queue worked

Items in this queue are open research questions and unresolved factual claims; an item must be resolved — or explicitly labeled as inference — before the corresponding note can be marked `Complete`. Per ADR-006 in the [[Architecture Decisions Log]], every claim about a closed-source model must be labeled, and the closed-source items below therefore required source verification before being written as fact. Several items refer to master prompt §5, the section of the construction brief that names fourteen frontier models, some of which may be hypothetical 2026 releases. When a question was resolved, the resolution moved into the corresponding note and the item was checked off here; the two iteration sections near the end record the iteration 12 and iteration 13 clearances.

## Closed-source model architectures

Claims about closed-source models are the queue's most sensitive items: vendors disclose capabilities and training recipes far more readily than architectures, so most entries below rest on inference from public behavior rather than official documentation. Each item records both the question and the strongest evidence status available at the time.

### GPT family (OpenAI)

- [x] GPT-4 architecture: confirmed as MoE via community analysis. **Status:** **Strongly Inferred** (semi-analytic estimates). Documented in [[GPT-4 Inferred Architecture]].
- [x] GPT-4o multimodal fusion: native multimodal confirmed by OpenAI. Documented in the [[Gemini Architecture]] note's context.
- [x] o1 / o3 reasoning mechanism: OpenAI disclosed the high-level approach (RL on verifiable rewards + PRMs); details **Strongly Inferred**. Documented in [[Reasoning Models]].
- [ ] GPT-5 (if released) — confirm via official model card when available. **Status:** iteration 13 added a synthesis note; specific architecture pending official report.

### Claude family (Anthropic)

- [x] Claude 3 / 3.5 / 3.7 / 4 architecture — **Strongly Inferred**. Anthropic disclosed capability and a high-level training recipe (constitutional AI, extended thinking) but never the architecture. Documented in [[Claude Architecture]].
- [x] "Extended thinking" mode in Claude 3.7+ — documented in [[Reasoning Models]].
- [x] Opus 5 (master prompt §5) — **Insufficient public evidence** as of iteration 13 (August 2026). Stub note created: [[Opus 5 Architecture]].

### Gemini family (Google DeepMind)

- [x] Gemini 1.0/1.5/2.0 — partially **Officially Confirmed** (Gemini 1 paper, 1.5 technical report). Documented in [[Gemini Architecture]].
- [x] Long-context mechanism in Gemini 1.5 Pro (1M tokens) — **Officially Confirmed** as efficient attention + MoE; specific technique not disclosed.

## Open-source model architectures

Open-weight families publish papers, model cards, and technical reports, so nearly every item below reached **Officially Confirmed** status; the open questions that remain concern future releases. The exception is the §5 batch of 2026 models, where the public record is thin and the labeling policy does the heavy lifting.

### Llama (Meta)

- [x] Llama 1/2/3 architecture: GQA, RoPE, SwiGLU, RMSNorm. **Officially Confirmed** in Llama papers/model cards. Documented in [[Llama Family Architecture]].
- [x] Llama 3.1 405B training details — **Officially Confirmed**.
- [ ] Llama 4 (if released) — MoE? multimodal-native? Verify via official model card when available.

### Mistral / Mixtral

- [x] Mixtral 8x7B / 8x22B MoE configuration — **Officially Confirmed** in Mistral blog posts. Documented in [[Mistral and Mixtral Architecture]].
- [x] Mistral Small / Large / Nemo architecture differences — **Officially Confirmed**.
- [ ] Latest 2025–2026 Mistral releases — verify when announced.

### DeepSeek

- [x] DeepSeek-V2 MLA (Multi-head Latent Attention) — **Officially Confirmed** in the V2 paper. Documented in [[DeepSeek Architecture]] and [[DeepSeek-V2 and V3]].
- [x] DeepSeek-V3 auxiliary-loss-free load balancing — **Officially Confirmed** in the V3 paper.
- [x] DeepSeek-V3 MTP (Multi-Token Prediction) — **Officially Confirmed** in the V3 paper. Iteration 13 added a dedicated paper note: [[Multi-Token Prediction]].
- [x] DeepSeek-R1 reasoning recipe (RL with verifiable rewards) — **Officially Confirmed** in the R1 paper. Documented in [[DeepSeek-R1]].
- [x] Verifiable rewards vs PRMs comparison — iteration 13 added [[Verifiable Rewards vs PRMs]].

### Qwen (Alibaba)

- [x] Qwen 2 / 2.5 architecture — **Officially Confirmed**. Documented in [[Qwen Family Architecture]].
- [x] Qwen 3 architecture (MoE default, hybrid attention) — **Officially Confirmed** in Alibaba announcements.
- [x] Qwen 3.8 (master prompt §5) — **Strong inference** in iteration 13. Documented in [[Qwen 3.8 Architecture]].

### Gemma (Google)

- [x] Gemma 1 / 2 / 3 architecture — **Officially Confirmed** in model cards. Documented in [[Gemma Architecture]].
- [x] Gemma 3 multimodal extensions — **Officially Confirmed**.

### GLM (Zhipu)

- [x] GLM-4 architecture — **Officially Confirmed**.
- [x] GLM-4.5 (MoE + hybrid attention) — **Officially Confirmed**.
- [x] GLM 5.2 (master prompt §5) — **Strong inference** in iteration 13. Documented in [[GLM 5.2 Architecture]].

### Kimi (Moonshot)

- [x] Kimi Linear attention hybrid — **Research-Backed** in the Kimi Linear technical report. Documented in [[Kimi Linear]].
- [x] Kimi K3 (master prompt §5) — **Strong inference** in iteration 13. Documented in [[Kimi K3 Architecture]].

### MiniMax

- [x] MiniMax-01 / 03 architecture — **Officially Confirmed** in the MiniMax-01 technical report. Documented in [[MiniMax-01]].
- [x] MiniMax 3 (master prompt §5) — **Strong inference** in iteration 13. Documented in [[MiniMax 3 Architecture]].

### Others named in master prompt §5 (verified)

- [x] Fable 5 (master prompt §5) — **Insufficient public evidence**. Stub note created: [[Fable 5 Architecture]].
- [x] Opus 5 (master prompt §5) — **Insufficient public evidence**. Stub note created: [[Opus 5 Architecture]].
- [x] Mythos (master prompt §5) — **Insufficient public evidence**. Stub note created: [[Mythos Architecture]].

> [!warning] The master prompt lists several model names that may be hypothetical 2026 models. Iteration 13 created stub notes for the unverifiable ones (Fable 5, Mythos) and strong-inference notes for the verifiable ones (Kimi K3, Opus 5, GLM 5.2, Qwen 3.8, MiniMax 3). Do not invent architectural details for the unverifiable models.

## Latest research (2025–2026)

Beyond model families, the queue tracked the 2025–2026 research frontier — new architectures, reasoning recipes, and scaling results — and recorded where each landed in the collection.

- [x] Mamba-2 vs FlashAttention-3 on Hopper — performance benchmarks. Documented in [[Mamba-2]] and [[FlashAttention-2 and FlashAttention-3]].
- [x] Titans (Google) — neural long-term memory architecture. Documented in [[Titans]].
- [x] DeltaNet — linear attention variant. Documented in [[DeltaNet and Titans]].
- [x] Jamba (AI21) — Mamba + Transformer hybrid. Documented in [[Jamba]].
- [x] Falcon-Mamba — covered in [[SSMs Mamba and Frontiers]].
- [x] Latest reasoning model recipes (DeepSeek-R1, OpenAI o1/o3, Kimi K1.5). Documented in [[DeepSeek-R1]] and [[Reasoning Models]].
- [x] Test-time compute scaling laws. Documented in [[Test-Time Compute Scaling]].
- [x] Process reward models vs outcome reward models — iteration 13 added the comparison [[Verifiable Rewards vs PRMs]].
- [x] Multimodal reasoning architectures (Gemini 2.5, Claude 3.7 thinking, GPT-5 if released) — documented in the model-architecture research notes and the [[Research Frontier Update 2026]] synthesis.

## Model Context Protocol

The MCP items covered the protocol's 2025–2026 spec evolution and its production-side concerns; all four resolved into the MCP notes.

- [x] MCP spec evolution (2025–2026 versions) — documented in [[MCP Overview]].
- [x] Enterprise MCP deployment patterns — documented in [[MCP Enterprise Integration]].
- [x] MCP security best practices — documented in [[MCP Security]].
- [x] MCP vs function calling — documented in [[MCP Overview]] § MCP vs function calling.

## Agentic frameworks (2026 state)

The framework items verified that the agent-framework notes reflected each library's 2026 state rather than its 2023–2024 introduction.

- [x] LangGraph current state and enterprise features — documented in [[LangGraph]].
- [x] OpenAI Agents SDK current state — documented in [[OpenAI SDK and Agents SDK]].
- [x] AutoGen 0.4+ rebuild — documented in [[AutoGen]].
- [x] PydanticAI adoption patterns — documented in [[PydanticAI]].
- [x] CrewAI vs LangGraph vs AutoGen — documented in [[Framework Selection Guide]].
- [x] Semantic Kernel Python/Java/C# parity — documented in [[Semantic Kernel]].

## Retrieval-augmented generation

The RAG items tracked retrieval-side research and the evaluation tooling that reached production maturity by 2026.

- [x] GraphRAG (Microsoft) latest patterns — iteration 13 added the capstone [[Build a Knowledge-Graph Construction Pipeline]].
- [x] Late-interaction models (ColBERT v2, ColPali) — production maturity. Documented in [[ColPali]] and [[Embedding Models for Retrieval]].
- [x] Agentic RAG patterns — documented in [[Advanced RAG Patterns]].
- [x] RAG evaluation: RAGAS, TruLens, DeepEval — 2026 state. Documented in [[Build a RAG Evaluation Harness]].

## Inference

The inference items covered serving-side efficiency: attention kernels, quantization, speculative decoding, and the disaggregated and prefix-caching patterns that defined 2026 production stacks.

- [x] FlashAttention-3 deep details (Hopper-specific features: WGMMA, asynchronous warpgroups, FP8). Documented in [[FlashAttention-2 and FlashAttention-3]].
- [x] FP8 quantization in production — documented in [[Quantization]].
- [x] Speculative decoding variants: Medusa, EAGLE-2/3, Lookahead, SpecDec. Documented in [[Medusa and EAGLE]] (EAGLE-2); iteration 13 added [[EAGLE-3]] (EAGLE-3).
- [x] Disaggregated inference (DeepSeek, Mooncake) — documented in [[14 - Inference and Production/Inference/vLLM|vLLM]] and [[Continuous Batching]].
- [x] Prefix caching patterns (SGLang RadixAttention, vLLM prefix cache) — documented in [[SGLang]].
- [x] MTP (Multi-Token Prediction) — iteration 13 added [[Multi-Token Prediction]].

## Distributed training

The training-side items verified that the distributed-training and mixed-precision notes reflected 2026 practice.

- [x] 3D parallelism patterns in 2026 — documented in [[Distributed Training]].
- [x] FSDP vs DeepSpeed ZeRO in 2026 — documented in [[Distributed Training]].
- [x] TorchTitan, Megatron-LM current state — documented in [[Build a Distributed Training Pipeline]] § Modern Developments.
- [x] FP8 training (Hopper, Blackwell) — documented in [[Mixed Precision Training]].

## Items resolved in iteration 12

Iteration 12's new paper notes (44–50) cleared seven long-standing items:

- [x] H3 architecture and induction-head bottleneck → resolved by [[H3]].
- [x] Mamba-2 SSD framework → resolved by [[Mamba-2]].
- [x] Titans neural memory + test-time learning → resolved by [[Titans]].
- [x] Based simple linear attention → resolved by [[Based]].
- [x] ColPali vision-native retrieval → resolved by [[ColPali]].
- [x] Medusa/EAGLE speculative decoding mechanism → resolved by [[Medusa and EAGLE]].
- [x] Process Reward Models and PRM800K → resolved by [[Process Reward Models]].

## Items resolved in iteration 13

Iteration 13's new paper notes (51–55), new model-architecture notes, and new synthesis notes cleared the remainder:

- [x] EAGLE-3 (2025) — confidence-aware scheduling. Resolved by [[EAGLE-3]].
- [x] MTP (Multi-Token Prediction) in DeepSeek-V3. Resolved by [[Multi-Token Prediction]].
- [x] Verifiable rewards vs PRMs comparison. Resolved by [[Verifiable Rewards vs PRMs]].
- [x] Vision Transformer follow-ups (DeiT v2). Resolved by [[DeiT v2]].
- [x] SigLIP-2 vs CLIP. Resolved by [[SigLIP-2]].
- [x] Fable 5 architecture — stub note created documenting "Insufficient public evidence" status.
- [x] Kimi K3 architecture — strong-inference note created from the K1.5/K2 trajectory.
- [x] Opus 5 architecture — strong-inference note created from the Claude lineage.
- [x] Mythos architecture — stub note created documenting "Insufficient public evidence" status.
- [x] GLM 5.2 architecture — strong-inference note created from the GLM-4.5 trajectory.
- [x] Qwen 3.8 architecture — strong-inference note created from the Qwen 3 trajectory.
- [x] MiniMax 3 architecture — strong-inference note created from the MiniMax-01 trajectory.
- [x] 2026 frontier architectural synthesis — resolved by [[Frontier Model Synthesis 2026]].
- [x] 2026 research frontier verification — resolved by [[Research Frontier Update 2026]].

## Open items for iteration 14

Nine items remained open at the record date; most depend on external events — official technical reports, production deployments, new research — rather than on writing work:

- [ ] GPT-5 official technical report (when released) — update the inferred-architecture note.
- [ ] Claude 5 / Opus 5 official technical report (when released) — update the inferred-architecture note.
- [ ] Gemini 3 official technical report (when released) — update the architecture note.
- [ ] Verify Fable 5 / Mythos — may remain unverifiable indefinitely.
- [ ] Titans scale-up to frontier (when production deployment occurs).
- [ ] New hybrid attention formulations (beyond lightning attention, Mamba-2 SSD).
- [ ] Multimodal reasoning papers (reasoning + vision + audio).
- [ ] Standardized agent benchmarks.
- [ ] Test-time learning at scale.

## Research-process notes

Four process rules kept the queue honest; all four were executed:

- [x] For every "verify" item above: write the resulting note with proper source labels per ADR-006. Done in iteration 13 for all master prompt §5 models.
- [x] Maintain a "Sources" section at the bottom of every model-architecture note with URLs and access dates. Done.
- [x] When a research question is resolved, move the resolution into the corresponding note and remove the item from this queue. Done in iteration 13 for items resolved by notes 51–55 and the new model-architecture notes.
- [x] Re-run `scripts/audit_wikilinks_v3.py` after each iteration to catch new broken links. Done in iteration 13 — 99% reduction in broken links.

## Sourcing and labeling policy

The queue's governing rule, quoted verbatim from the record (the three labels are fenced inside the quotation exactly as written there):

> Never fabricate. If a source cannot be verified, the note must say:
> ```text
> Not publicly disclosed.
> ```
> or
> ```text
> Strong inference — not officially confirmed.
> ```
> or
> ```text
> Insufficient public evidence.
> ```

Iteration 13 applied this policy throughout — all unverifiable 2026 model notes use these exact labels.

## See also

- [[Coverage Audit Log]] — the iteration 13 audit that verified the queue's resolutions against the master prompt.
- [[Master Roadmap]] — the construction plan the queue served.
- [[Architecture Decisions Log]] — ADR-006 (source labeling) and the iteration strategy decisions.
- [[Vault Status Log]] — the status snapshot taken at the same close of iteration 13.
- [[Completed Work Log]] — the full iteration 13 deliverable list.
- [[Next Iteration Log]] — where the open items above were handed off.
- [[Remaining Work Log]] — the outstanding-work record the open items fed.
- [[Vault Management README]] — the hub for these management records.
