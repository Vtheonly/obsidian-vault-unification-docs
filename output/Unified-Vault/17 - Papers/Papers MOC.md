---
title: Papers MOC
type: overview
aliases: [Papers Map of Content, Landmark Papers MOC, Papers Reading List, AI Papers MOC]
tags: [moc, papers, reading-list, landmark-papers]
sources:
  - "26 — Papers MOC"
created_index: 42
---

This area collects the 55 landmark papers that shaped modern AI engineering, covering 2014–2025. Each paper has its own note with a summary, key contributions, architecture, impact, and links to related concepts, so a single stop is usually enough to understand what a paper changed and why it mattered. The notes are organized into nine thematic groups — landmark LLMs, the attention and Transformer lineage that built them, scaling and training, efficiency, multimodal, reasoning, agents and RAG, alignment and RLHF, and the state space models and linear attention line. Start with the chronological tour in the reading order section, jump into whichever group matches the problem at hand, or follow the topic paths in the group paragraphs to trace a single thread across groups.

## Reading order

Read chronologically to watch the field unfold — attention is invented to break the fixed seq2seq bottleneck, becomes the whole model in the Transformer, scales into the LLM era, and is then made efficient, multimodal, capable of reasoning, agentic, aligned, and cheap to serve. The eras below give that tour; each group section that follows opens with the topical reading path for its own theme, and says where to go next when a path crosses groups.

### 2014–2017: attention origins and the Transformer

Bahdanau 2014 → Luong 2015 → Vaswani 2017 (*Attention Is All You Need*). Attention is born as the fix for the fixed seq2seq bottleneck, is simplified into multiplicative dot-product scoring, and is then promoted to the only mechanism in the model.

### 2018–2019: the encoder and decoder era

GPT-1 2018 → BERT 2018 → GPT-2 2019 → T5 2019 → Transformer-XL 2019. The pretrain-then-finetune paradigm arrives on the generative side (GPT-1, GPT-2) and the bidirectional-encoder side (BERT), T5's text-to-text framing unifies every task under one objective, and Transformer-XL opens the long-context line with segment recurrence and relative position.

### 2020: scaling and efficiency

GPT-3 2020 → Reformer, Longformer, Linformer, BigBird, ViT 2020. Scale delivers in-context learning while the efficient-attention wave arrives — LSH attention, sliding windows, low-rank projection, local + global + random sparsity — and the Transformer crosses into vision with the patch-based ViT.

### 2021: components refined

LoRA 2021 → Performer 2021 → Swin Transformer 2021. Adaptation gets cheap (low-rank), attention gets linearized (random Fourier features), and vision Transformers get hierarchy (shifted windows).

### 2022: alignment and efficiency breakthroughs

FlashAttention 2022 → InstructGPT 2022 → Constitutional AI 2022 → Flamingo 2022 → Perceiver 2022. IO-aware exact attention enables long context, the RLHF recipe and its AI-feedback successor RLAIF arrive, and the first few-shot visual-language models appear.

### 2023: the open-weights explosion and reasoning techniques

LLaMA 2023 → Mistral 7B 2023 → DPO 2023 → PagedAttention 2023 → Mamba 2023 → Reflexion 2023 → Self-Refine 2023 → Tree of Thoughts 2023 → GPT-4 2023 → FlashAttention-2 2023. Open weights catalyze the ecosystem, direct preference optimization replaces PPO, KV-cache paging multiplies serving throughput, selective SSMs challenge attention, and the self-critique and search techniques of agentic reasoning arrive.

### 2024–2025: MoE, reasoning, and hybrids

GQA 2024 → DeepSeek-V2/V3 2024 → FlashAttention-3 2024 → Jamba 2024 (hybrid SSM-Transformer) → DeepSeek-R1 2025 → Kimi Linear 2025 → MiniMax-01 2025 (linear-attention hybrid, 1M context). Grouped-query attention becomes the default for modern LLMs, auxiliary-loss-free MoE makes frontier-grade training radically cheaper, the first production SSM-Transformer hybrids ship, and verifiable-reward RL produces open-weights reasoning.

### Foundational scaling theory

Scaling Laws (Kaplan 2020 + Chinchilla 2022) — power-law scaling and Chinchilla's 20 tokens/param recipe. Read this alongside the LLM line to see each model as a point on the curve.

### Reasoning techniques: sampling and search

Self-Consistency 2022 (sample + vote) → Tree of Thoughts 2023 (search) → Graph of Thoughts 2023 (DAG search). The arc runs from sampling many chains of thought and majority-voting, to searching over reasoning trees, to merging and refining over arbitrary graphs.

## Landmark LLMs

The flagship models that defined each era of the LLM age — the papers to reach for when you need the primary source for what a frontier or open-weights model actually did. The line starts with GPT-1 in the attention and Transformers group below and runs through GPT-2 and GPT-3 to GPT-4; it then splits into the open-weights branch that LLaMA catalyzed, the small-model branch (Mistral 7B, where 7B beats 13B), and the Mixture-of-Experts efficiency branch (DeepSeek-V2 and V3 — see [[Mixture of Experts]] for the concept) before culminating in DeepSeek-R1 over in the reasoning group. Read in publication order to watch capability, openness, and cost-efficiency trade places as the field's dominant concern.

- [[GPT-2]] (2019) — zero-shot task transfer; the scaling hypothesis.
- [[GPT-3]] (2020) — scale → in-context learning; foundation of the LLM era.
- [[GPT-4 Technical Report]] (2023) — multimodal; professional-grade capability.
- [[LLaMA]] (2023) — the open-weights LLM that catalyzed the ecosystem.
- [[Mistral 7B]] (2023) — SWA + GQA; 7B beats 13B.
- [[DeepSeek-V2 and V3]] (2024) — MLA + auxiliary-loss-free MoE; $5.5M training.

## Attention and Transformers

Where the whole field begins. Attention was invented to break the fixed seq2seq bottleneck (Bahdanau), simplified into multiplicative dot-product scoring (Luong), and then promoted to the only mechanism in the model (Vaswani) — the Transformer that is the foundation of all modern LLMs, treated conceptually in [[The Transformer]]. From there the group follows the 2018–2019 encoder-and-decoder era — GPT-1's pretrain-then-finetune for generative models, BERT's bidirectional encoder, T5's text-to-text framing — and then the vision branch: the patch-based Vision Transformer, the shifted-window hierarchical Swin Transformer, and DeiT v2's modernized training recipe, which now serves as a VLM vision encoder.

- [[17 - Papers/Attention and Transformers/Bahdanau Attention|Bahdanau Attention]] (2014) — birth of attention; the fix for the fixed seq2seq bottleneck.
- [[17 - Papers/Attention and Transformers/Luong Attention|Luong Attention]] (2015) — multiplicative (dot-product) attention.
- [[Attention Is All You Need]] (2017) — the Transformer; foundation of all modern LLMs.
- [[GPT-1]] (2018) — pretrain-then-finetune for generative models.
- [[17 - Papers/Attention and Transformers/BERT|BERT]] (2018) — the pretrain-finetune paradigm; bidirectional encoder.
- [[T5]] (2019) — text-to-text framing; span corruption; C4.
- [[Vision Transformer]] (2020) — Transformers for vision; patch-based.
- [[Swin Transformer]] (2021) — shifted windows; hierarchical vision Transformer.
- [[DeiT v2]] (2024) — modernized ViT training recipe; VLM vision encoder.

## Scaling and training

Two papers that turned model-building from craft into arithmetic: the Kaplan and Chinchilla scaling laws, and the low-rank adaptation method that made fine-tuning large models cheap. The training-theory reading path runs Scaling Laws → GPT-3 → LLaMA → DeepSeek-V2 and V3, each later model demonstrating the recipes the power laws prescribe, with LoRA underneath as the default parameter-efficient fine-tuning method.

- [[Scaling Laws (Kaplan and Chinchilla)]] (2020/22) — power-law scaling; Chinchilla's 20 tokens/param recipe.
- [[17 - Papers/Scaling and Training/LoRA|LoRA]] (2021) — low-rank adaptation; the default PEFT method.

## Efficiency

Everything that makes Transformers affordable to run: the long-context attention line, the KV-cache serving line, and the decoding line. The efficient-attention path runs Transformer-XL → Reformer → Longformer → Linformer → BigBird → Performer → FlashAttention → GQA, with FlashAttention-2 and FlashAttention-3 refining the IO-aware line. PagedAttention contributes paging for the KV cache — the technique behind the [[14 - Inference and Production/Inference/vLLM|vLLM]] serving engine's 2–4× throughput. The decoding line is single-model speculative decoding (concept overview in [[Speculative Decoding]]): Medusa and EAGLE, then EAGLE-3's confidence-aware variant, plus DeepSeek-V3's training-time multi-token prediction.

- [[Transformer-XL]] (2019) — segment recurrence + relative position.
- [[Reformer]] (2020) — LSH attention + reversible layers.
- [[Longformer]] (2020) — sliding window + global attention.
- [[Linformer]] (2020) — low-rank attention projection.
- [[BigBird]] (2020) — local + global + random; theoretical guarantees.
- [[Performer]] (2021) — random Fourier features; linearized attention.
- [[17 - Papers/Efficiency/FlashAttention|FlashAttention]] (2022) — IO-aware exact attention; enabled long context.
- [[FlashAttention-2 and FlashAttention-3]] (2023–24) — 2× with FA2; Hopper-optimized FA3.
- [[GQA]] (2024) — grouped-query attention; the default for modern LLMs.
- [[PagedAttention and vLLM]] (2023) — paging for the KV cache; 2–4× throughput.
- [[Medusa and EAGLE]] (2024) — single-model speculative decoding; 2–4× speedup.
- [[EAGLE-3]] (2025) — confidence-aware spec decoding; 4–6× speedup.
- [[Multi-Token Prediction]] (2024) — training-time multi-token prediction (DeepSeek-V3).

## Multimodal

Perception and vision-language. The canonical path enters through the CLIP concept ([[CLIP]]) and the Vision Transformer (in the attention and Transformers group), then runs Perceiver → Flamingo → BLIP-2 — general perception, few-shot visual-language modeling, and the Q-Former bridge — and continues toward the LLaVA concept ([[LLaVA]]). The two newer entries cover the retrieval and encoder sides of modern VLMs: ColPali's vision-native document retrieval that eliminates OCR, and SigLIP-2, the multilingual vision encoder that is the default for 2026-era VLMs.

- [[Perceiver]] (2022) — asymmetric attention; general perception.
- [[Flamingo]] (2022) — few-shot visual-language model; Perceiver resampler.
- [[BLIP-2]] (2023) — the Q-Former bridge between frozen vision and a frozen LLM.
- [[ColPali]] (2024) — vision-native document retrieval; eliminates OCR.
- [[SigLIP-2]] (2025) — the default 2026 VLM vision encoder; multilingual.

## Reasoning

Making models reason rather than pattern-match. The sampling-and-search arc runs Self-Consistency → Tree of Thoughts → Graph of Thoughts: sample N chain-of-thought paths and majority-vote, then search over reasoning trees, then generalize to DAGs with merge and refine operations. DeepSeek-R1 completes the group as the RL-trained open-weights reasoning model, built on verifiable rewards rather than process reward models — the trade the alignment group's final note charts. The chain-of-thought foundation itself is treated in [[Chain of Thought]] in the agents area.

- [[Self-Consistency]] (2022) — sample N CoT paths, majority vote; +10–20% reasoning.
- [[Tree of Thoughts]] (2023) — search over reasoning trees; planning.
- [[Graph of Thoughts]] (2023) — generalizes ToT to DAGs; merge + refine operations.
- [[DeepSeek-R1]] (2025) — verifiable-reward RL; open-weights reasoning.

## Agents and RAG

The paper origins of the agent stack: retrieval-augmented generation for grounding, and the self-critique loops for iterative improvement. The full agents-and-reasoning path runs RAG → chain of thought → self-consistency → Reflexion → Self-Refine → Tree of Thoughts → Graph of Thoughts → DeepSeek-R1, crossing into the reasoning group above; within this group, Reflexion contributes verbal reinforcement learning via the self-critique loop and Self-Refine iterative self-critique and refinement.

- [[RAG]] (2020) — the original retrieval-augmented generation paper.
- [[Reflexion]] (2023) — verbal reinforcement learning; the self-critique loop.
- [[Self-Refine]] (2023) — iterative self-critique and refinement.

## Alignment and RLHF

Teaching models to follow human intent. InstructGPT established the RLHF recipe (SFT → RM → PPO); Constitutional AI replaced human feedback with AI feedback (RLAIF); DPO replaced PPO with direct preference optimization; and the reward-modeling line — Process Reward Models' step-level rewards, then the Verifiable Rewards vs PRMs comparison — charts the shift that produced reasoning models and the R1-Zero paradigm. The alignment reading path is InstructGPT → Constitutional AI → DPO → DeepSeek-R1.

- [[InstructGPT]] (2022) — the RLHF recipe; SFT → RM → PPO.
- [[Constitutional AI]] (2022) — RLAIF; AI feedback instead of human feedback.
- [[DPO]] (2023) — direct preference optimization; replaced PPO.
- [[Process Reward Models]] (2023) — step-level reward models; foundation for reasoning models.
- [[Verifiable Rewards vs PRMs]] (2025) — RLVR vs PRM comparison; the R1-Zero paradigm shift.

## State space models and linear attention

The linear-time alternative to attention, and the hybrid architectures that combine both. H3 identified the induction-head bottleneck that pure SSMs face; Mamba answered with selective SSMs; Mamba-2's SSD framework unified SSMs with linear attention; and the production line followed — Jamba as the first production hybrid SSM-Transformer, Based as the simple, reproducible Taylor-expansion linear attention, Titans with neural memory and test-time learning for million-token context, and Kimi Linear and MiniMax-01 as the million-token open hybrids. The hybrid-architectures reading path runs Mamba → Jamba → Kimi Linear → MiniMax-01.

- [[H3]] (2022) — hybrid SSM + attention; identified the induction-head bottleneck.
- [[Mamba]] (2023) — selective SSMs; linear-time sequence modeling.
- [[Mamba-2]] (2024) — the SSD framework unifying SSMs and linear attention; 8192 state size.
- [[Jamba]] (2024) — first production hybrid SSM-Transformer; 1:7 ratio.
- [[Based]] (2024) — simple Taylor-expansion linear attention; reproducible hybrid.
- [[Titans]] (2024) — neural memory + test-time learning; million-token context.
- [[Kimi Linear]] (2025) — hybrid linear/attention for million-token context.
- [[MiniMax-01]] (2025) — linear-attention hybrid; first open 1M context.

## Future expansion

The collection grows at the frontier. Planned additions: 2026 frontier-model architectures (GPT-5, Claude 5, Gemini 3 — when their technical reports emerge); long-context breakthroughs (Ring Attention variants, new positional schemes); multimodal reasoning papers; and agent benchmarks and evaluation frameworks.

## See also

- [[Attention and Transformers MOC]] — concept-level treatments of the attention mechanism, the Transformer, and its architecture variants.
- [[Large Language Models MOC]] — the LLM concepts behind the landmark models.
- [[Training and Adaptation MOC]] — fine-tuning and adaptation concepts, including the LoRA method this area's paper introduced.
- [[Inference and Production MOC]] — the serving, KV-cache, and speculative-decoding engineering built on the efficiency papers.
- [[Foundation Models and Multimodal MOC]] — the CLIP and LLaVA concepts that bracket the multimodal line.
- [[Agents and Tooling MOC]] — the agent patterns and RAG pipelines these papers seeded.
- [[Interpretability and Research MOC]] — interpretability, model architecture research, and the research frontiers that continue the state-space and hybrid story.
