---
title: Conceptual Interview Questions
type: reference
aliases: [Interview Questions, Conceptual Q&A, Conceptual Interview Questions 2, Advanced Interview Q&A, Iteration 13 Interview Questions]
tags: [interview, conceptual, attention, transformers, llms, reasoning-models, vlms, mcp, grpo, hybrid, scaling, spec-decoding, quantization, dpo-variants]
sources:
  - "01 - Conceptual Interview Questions"
  - "06 - Conceptual Interview Questions 2"
created_index: 6
---

This note is the consolidated conceptual AI-engineering interview question bank: common questions with concise answers and pointers to the concept notes that treat each topic in depth. Coverage runs from attention and Transformers, LLM training, inference, fine-tuning, RAG, and agents through reasoning models, vision-language models, MCP, memory systems, multi-agent patterns, interpretability, scaling laws, quantization, DPO variants, GraphRAG, long-context behavior, and the 2026 frontier architectures. Questions are grouped topically and range from fundamentals to senior-level depth, so the same bank serves screening rounds and senior AI engineering interviews alike. It sits in [[Interview Prep MOC]] alongside [[Coding Interview Questions]] and [[System Design Interview Questions]].

## Attention and Transformers

Warm-up questions on the Transformer building blocks: the attention computation, its memory-saving variants, and how position and depth are handled.

**Why scale the dot product by $\sqrt{d_k}$ in attention?**
Without scaling, the dot product's variance grows with $d_k$. For large $d_k$, softmax saturates (one entry → 1, others → 0), causing vanishing gradients. Scaling brings variance back to 1, keeping softmax in its non-saturated regime. See the "Why scale by √d_k" discussion in [[Self-Attention]].

**What's the difference between MHA, MQA, GQA, MLA?**
- **MHA**: one K/V per head (most params, best quality).
- **MQA**: one K/V shared across all heads (least params, slight quality loss).
- **GQA**: groups of heads share K/V (sweet spot — Llama, Mistral, Gemma).
- **MLA**: compress K/V into a low-rank latent (DeepSeek; smallest KV cache).

See [[GQA MQA and MLA]] for the full comparison.

**Why use multi-head attention instead of a single big head?**
Multiple heads let the model attend to different relations simultaneously (one head for previous-token, another for induction, another for syntax). Heads specialize. See [[Multi-Head Attention]].

**Pre-norm vs post-norm?**
Pre-norm (norm before sublayer) keeps the residual path clean, enabling stable training of deep Transformers. Post-norm (norm after residual) was the original but is unstable past ~12 layers. All modern LLMs use pre-norm. See [[Pre-Norm vs Post-Norm]].

**Why do Transformers need positional encoding?**
Self-attention is permutation-invariant — without positional info, the model can't distinguish token order. RoPE (modern default) rotates Q and K by position, making attention depend on relative offset. See [[Positional Encoding]] and [[RoPE]].

**What does FlashAttention do?**
FlashAttention is an IO-aware exact attention algorithm. It tiles the computation to keep intermediates in fast GPU SRAM instead of slow HBM. 2–4x faster, 10x less memory, no quality loss. See [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]].

## LLM training and alignment

The training pipeline from base model to aligned chat model, plus the modern preference-optimization landscape.

**What's the difference between pretraining, SFT, and RLHF/DPO?**
- **Pretraining**: train on massive text corpus with next-token prediction. Produces a base model.
- **SFT (supervised fine-tuning)**: fine-tune on instruction-response pairs. Produces a chat-capable model.
- **RLHF/DPO**: align with human preferences via reward model + PPO (RLHF) or direct preference optimization (DPO). Produces an aligned chat model.

See [[Pretraining Objectives and Scaling Laws]], [[Instruction Tuning and Chat Templates]], [[RLHF with PPO]], and [[DPO]].

**What does LoRA do and why does it work?**
LoRA freezes the pretrained weights and learns low-rank delta matrices alongside them. It works because fine-tuning updates have low intrinsic rank — you don't need full-rank updates to adapt the model. Reduces trainable params 100–1000x. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]].

**What are IPO, KTO, SimPO, and how do they differ from DPO?**
- **DPO** (2023): direct preference optimization on (prompt, chosen, rejected) pairs. Standard recipe.
- **IPO** (2024): Identity Preference Optimization. Fixes DPO's overfitting on noisy preferences by regularizing the preference gap. More conservative than DPO.
- **KTO** (2024): Kahneman-Tversky Optimization. Uses single-sided preferences (good/bad) instead of pairs. Doesn't need paired data — works on thumbs-up/thumbs-down signals.
- **SimPO** (2024): length-normalized DPO. Removes DPO's length bias (DPO can prefer longer responses). Better for production chat alignment.

By 2026, SimPO is the default for new projects; DPO remains for backward compatibility; KTO for thumbs-up/down datasets; IPO for noisy preferences. See [[DPO]], [[DPO Derivation]], and [[Build a Fine-Tuning Pipeline with LoRA and DPO]].

**Why does DPO have a length bias?**
DPO's loss compares log P(chosen) - log P(rejected). If the chosen response is longer, log P(chosen) is naturally lower (more tokens to predict). The model can game this by making responses shorter, increasing log P(chosen) artificially. SimPO normalizes by length: log P(chosen) / len(chosen) - log P(rejected) / len(rejected). Removes the length bias. See [[DPO Derivation]].

**When would you use KTO instead of DPO?**
KTO (Kahneman-Tversky Optimization) uses single-sided preferences: each response is labeled "good" or "bad" (thumbs up/down), not paired. Use KTO when: (1) you only have unary feedback (thumbs up/down from users, no paired comparisons); (2) collecting paired data is expensive (KTO works on any unary feedback); (3) the dataset is imbalanced (more thumbs up than down, or vice versa). DPO requires paired data (chosen vs rejected); KTO doesn't. Trade-off: paired data has more signal per example (relative comparison), so DPO converges faster when you have pairs. See [[DPO Derivation]].

## Scaling laws and compute budgets

How much compute, how much data, and what it costs.

**What does the Chinchilla scaling law say?**
Compute-optimal training uses ~20 tokens per parameter. Pre-Chinchilla models (GPT-3, original Llama) were undertrained — too few tokens for their size. Post-Chinchilla models (Llama 2, Mistral) follow the recipe. Modern small models (Llama 3 8B, trained on 15T tokens) are overtrained — far more tokens than Chinchilla-optimal — because inference cost dominates total cost. Overtraining makes the model better at inference time, which justifies the extra pretraining compute. See [[Scaling Laws (Kaplan and Chinchilla)]] and [[Pretraining Objectives and Scaling Laws]].

**Why does Llama 3 8B use 15T tokens (way more than Chinchilla's 20:1)?**
Llama 3 8B has 8B parameters, so Chinchilla-optimal would be 160B tokens. Llama 3 8B was trained on 15T tokens — ~94× Chinchilla. Why? Because Llama 3 8B is a serving model (will be used billions of times); the extra pretraining compute is amortized over many inference calls. Chinchilla assumed pretraining and inference compute are equally weighted; in practice, inference dominates. So overtraining is optimal when inference is the bottleneck. See [[Scaling Laws (Kaplan and Chinchilla)]] and [[Llama Family Architecture]].

**How do you compute the FLOPs for training a transformer?**
Approximate FLOPs ≈ 6 × N × D, where N is parameter count and D is token count. The factor 6 comes from: 2 (forward pass: matmul) × 2 (backward pass: matmul + gradient) × 1 (master weight). For Llama 3 70B (70B params, 15T tokens): 6 × 70e9 × 15e12 = 6.3e24 FLOPs ≈ 6 × 10²⁴ FLOPs. At 50% MFU on H100 (700 TFLOPs BF16), this takes ~110k H100-hours = ~4600 H100-days. At $2/H100-hour, ~$220K. Frontier models (10²⁵+ FLOPs) cost tens of millions in compute alone.

## Inference efficiency

Serving cost is dominated by memory movement and redundant compute, so the highest-leverage levers are the KV cache, batching, speculative decoding, and quantization.

### KV cache and batching

**What is the KV cache and why does it matter?**
The KV cache stores keys and values for all previous tokens so autoregressive generation only computes the new token's Q/K/V, not all tokens'. Without it, generating 1000 tokens from a 4096-token prompt would cost ~4M token-equivalent computations instead of ~4K. See [[KV Cache Mechanics]].

**How does PagedAttention work?**
Manages the KV cache as fixed-size pages (like OS virtual memory) instead of contiguous allocations. Eliminates fragmentation (60–80% memory waste in naive approach), enables continuous batching, gives 2–4x throughput. See [[PagedAttention and vLLM]].

**Why is decode memory-bound at batch size 1?**
At batch size 1, each token generation requires reading the full model weights from HBM (e.g., 14 GB for a 7B model in fp16). The actual compute is tiny (one matmul per layer). So you're limited by HBM bandwidth (~3 TB/s), not compute. This is why batching helps — it amortizes weight reads across multiple requests.

### Speculative decoding

**What is speculative decoding?**
Use a small "draft" model to propose multiple tokens, then have the large "target" model verify them in one forward pass. Accepted tokens come free; rejected tokens are resampled. 2–3x speedup, no quality loss. See [[Speculative Decoding]].

**Why is spec decoding bit-identical to vanilla decoding?**
Spec decoding uses rejection sampling to preserve the target model's distribution. For each speculated token: (1) compute P_target(token) and P_draft(token); (2) accept with probability min(1, P_target / P_draft); (3) if rejected, resample from the corrected distribution (P_target - P_draft, normalized). This procedure is provably equivalent to sampling from P_target directly. No quality loss. The output distribution is identical to vanilla decoding given the same random seed. See [[Medusa and EAGLE]].

**How does EAGLE-3 achieve 4–6× speedup?**
Three innovations. (1) **Confidence-aware scheduling**: predict which speculated branches will be accepted (via a small MLP), prune low-confidence branches before the verification forward pass. (2) **Training-time MTP**: the target model is trained with multi-token prediction, making its hidden states "speculation-friendly". (3) **Longer speculation**: K=8–16 (vs EAGLE-2's K=4–8). Combined: 90–97% acceptance rate (vs EAGLE-2's 85–95%), giving 4–6× speedup. See [[EAGLE-3]].

**When does spec decoding hurt performance?**
Five cases. (1) **Very short generations** (<50 tokens): draft overhead > speedup. (2) **Low acceptance rate** (<50%): rejected drafts waste compute. (3) **Large batch sizes** (>32): tree verification has diminishing returns at high batch. (4) **Code generation**: draft models struggle with code's discrete structure. (5) **Highly creative tasks** (poetry, brainstorming): draft models predict "safe" continuations that get rejected. For these, fall back to vanilla. Adaptive routers detect these cases and switch modes. See [[Medusa and EAGLE]].

**How does MTP (Multi-Token Prediction) relate to spec decoding?**
MTP is a *training-time* technique: the model is trained to predict multiple future tokens, producing a built-in draft head. Spec decoding (EAGLE-3) is an *inference-time* technique that leverages MTP-trained models. Without MTP, EAGLE-3 falls back to EAGLE-2-style behavior. MTP makes the target model's hidden states "speculation-friendly" — explicitly trained to support multi-token lookahead. DeepSeek-V3 uses MTP; EAGLE-3 achieves 4–6× on DeepSeek-V3. See [[Multi-Token Prediction]] and [[EAGLE-3]].

### Quantization

**When would you use INT4 vs INT8 vs FP8?**
- **INT8**: ~1% quality loss, 2x memory reduction. Easy. Default for general serving.
- **INT4 (GPTQ/AWQ)**: ~1–2% quality loss, 4x memory reduction. Standard for serving 70B+ models on consumer GPUs.
- **FP8 (Hopper+)**: <0.5% quality loss, 2x reduction. Best quality, requires H100+ hardware.

Production guidance: use FP8 on H100+ (best quality, easy); INT8 on A100 (good quality, broad hardware support); INT4 when memory is constrained (consumer GPUs, edge). See [[Quantization]] and [[Build a Quantization Toolkit]].

**How does GPTQ differ from AWQ?**
- **GPTQ** (Frantar et al., 2022): post-training quantization using second-order information (Hessian of weights). Quantizes weights column-by-column, updating remaining weights to compensate. Accurate but slow (minutes per model).
- **AWQ** (Lin et al., 2023): activation-aware quantization. Identifies "important" weights (high-magnitude activations) and keeps them in higher precision; quantizes the rest to INT4. Faster than GPTQ, comparable quality.

Both produce INT4 models; AWQ is generally preferred for production (faster, similar quality). See [[Quantization]].

**Why is FP8 better than INT8?**
Three reasons. (1) **Dynamic range**: FP8 has exponent + mantissa, so it can represent both very small and very large values; INT8 is fixed-point, limited range. (2) **No calibration**: FP8 quantization doesn't require a calibration dataset (just convert); INT8 requires running sample inputs to determine scaling factors. (3) **Hardware native**: H100+ has native FP8 tensor cores, so FP8 matmul is as fast as INT8. Trade-off: FP8 requires Hopper+ hardware; INT8 works on older GPUs. See [[Quantization]].

**How do you quantize a 70B model to fit on a single 80GB GPU?**
Use **QLoRA + INT4**. Steps: (1) Load base model in INT4 (4-bit weights, ~35GB for 70B). (2) Add LoRA adapters (rank 16, ~50M params, ~200MB). (3) Train LoRA on top of frozen INT4 base. (4) Merge LoRA back into base for deployment. (5) Serve merged INT4 model on single 80GB GPU. Quality: ~2–3% loss vs BF16; cost: 1× GPU instead of 2×. See [[QLoRA]] and [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]].

## Reasoning models and test-time compute

**What's the difference between a reasoning model and a regular LLM?**
Reasoning models (o1, R1, Claude thinking) are trained to produce long internal chain-of-thought before answering. They spend more compute at inference ("test-time compute scaling") to solve harder problems. Same architecture; different training and inference pattern. See [[Reasoning Models]].

**What is test-time compute scaling?**
Allowing the model to "think" longer at inference (longer CoT) to solve harder problems. Snell et al. (2024) showed accuracy scales as $\log(\text{tokens})$. A new dimension of capability — pre-2024, capability came from parameters, data, and training compute; test-time compute is the fourth. See [[Test-Time Compute Scaling]] and [[Reasoning Models]].

**Why does test-time compute scale logarithmically with accuracy?**
Snell et al. (2024) showed accuracy scales as $\log(\text{tokens})$. The intuition: reasoning is a search problem; doubling search budget adds a constant number of "additional branches" the model can explore. Each branch has diminishing probability of being correct. So 2× tokens gives a constant accuracy gain (not 2× accuracy). This is why reasoning models are 10–100× more expensive than standard LLMs — the log scaling means accuracy gains require exponentially more compute. See [[Test-Time Compute Scaling]].

**What's the difference between o1 and R1?**
Both are trained with RL on verifiable rewards; the recipes differ in details. o1 (OpenAI, Sep 2024) is closed-source, with hidden CoT, trained with RL on verifiable rewards + PRMs. R1 (DeepSeek, Jan 2025) is open-source, with visible CoT, trained with RL on verifiable rewards (GRPO); R1-Zero showed pure RL (no SFT first) can produce emergent CoT. The full difference list: (1) **R1 is open-weights**; o1 is API-only. (2) **R1's CoT is visible**; o1's is hidden. (3) **R1-Zero** showed that pure RL (no SFT first) produces emergent CoT; o1 likely used SFT before RL. (4) **R1 uses GRPO** (no value model); o1 likely uses PPO with a value model. (5) **R1 builds on DeepSeek-V3** (MLA + aux-loss-free MoE); o1's architecture is undisclosed. See [[DeepSeek-R1]] and [[Process Reward Models]].

**What is GRPO, and how does it differ from PPO?**
Group Relative Policy Optimization (DeepSeek, the R1 optimizer): samples N completions per prompt, uses group mean as baseline. Doesn't need a separate value model (PPO does — PPO uses a learned value model to estimate expected reward). GRPO is simpler (no value model to train), cheaper, more stable for binary-reward settings (math correctness, code passing), and works well when the reward signal is sharp. PPO with a value model remains valuable for non-verifiable rewards (chat alignment). See [[DeepSeek-R1]] and [[RLHF with PPO]].

**Why did DeepSeek-R1-Zero skip SFT?**
R1-Zero: pure RL on verifiable rewards (no SFT first). The hypothesis: SFT on reasoning traces biases the model toward specific reasoning patterns; pure RL lets the model discover its own reasoning strategies. The result: R1-Zero's CoT is longer, more exploratory, and less polished than R1's (which used SFT). R1-Zero demonstrated that SFT is not strictly necessary for emergent CoT — RL alone suffices. But R1 (with SFT) is more readable and safer, so production uses R1 not R1-Zero. See [[DeepSeek-R1]].

**What is the "aha moment" in R1-Zero's training?**
During R1-Zero's RL training, the model spontaneously developed a behavior of reflecting on its own reasoning ("Wait, let me reconsider this..."). This wasn't trained explicitly — it emerged from the reward signal (correct answers correlate with self-correction). The "aha moment" was DeepSeek's term for this emergent behavior. It demonstrates that RL on verifiable rewards can produce sophisticated reasoning behaviors without explicit supervision. See [[DeepSeek-R1]].

**When does RLVR beat PRM?**
RLVR (Reinforcement Learning with Verifiable Rewards) beats PRM (Process Reward Model) when: (1) **the answer is verifiable** — math, code, formal logic; (2) **annotation budget is limited** — RLVR is free (rule-based verifier), PRM requires labels; (3) **reward hacking matters** — RLVR is immune (rule-based), PRM is susceptible. PRM wins when: (1) **answer is not verifiable** — creative writing, subjective tasks; (2) **credit assignment matters** — PRM gives per-step signal; (3) **reasoning is long** — PRM's dense signal helps convergence. Most 2026 reasoning models use RLVR alone or RLVR + PRM hybrid. See [[Verifiable Rewards vs PRMs]] and [[Process Reward Models]].

**When should you use a reasoning model vs. a standard LLM?**
- **Reasoning model** (o1, R1): hard problems (math, code, multi-step reasoning), batch tasks (latency OK), high-stakes (quality justifies cost).
- **Standard LLM** (GPT-4o, Llama 3): simple Q&A, real-time chat, high-volume, cost-sensitive.
- **Hybrid**: route easy queries to standard LLM, hard to reasoning model. 5-10× cost reduction.

See [[Reasoning Models]].

**Why are reasoning models 10–100× more expensive than standard LLMs?**
Because they generate 10–50K thinking tokens per query. At $60/1M output tokens (o1), 30K CoT = $1.80 per query just for thinking. Standard LLMs generate 500–1000 output tokens. The cost ratio is (30K / 1K) × (output_token_price_ratio) ≈ 30–100×. Mitigations: spec decoding (4–6× cost reduction), distillation (10× cost reduction), adaptive thinking (5–10× cost reduction for mixed workloads). See [[Reasoning Models]].

**How do you serve a reasoning model cost-effectively?**
Three techniques. (1) **Speculative decoding** (EAGLE-3): the model's CoT is highly predictable (it's repetitive, structured). EAGLE-3 spec decoding gives 4–6× speedup on R1-style models. (2) **Adaptive thinking**: route easy queries to a non-reasoning model; only use the reasoning model for hard queries. Saves 5–10× cost. (3) **Distillation**: distill the reasoning model into a smaller student (DeepSeek's R1-Distill series). The student inherits ~85% of the reasoning capability at 10× lower cost. See [[EAGLE-3]] and [[Build a Model Distillation Pipeline]].

## Vision-language models

**How does LLaVA work?**
Frozen CLIP-ViT encoder → image tokens → MLP projector → LLM. The LLM is fine-tuned (LoRA or full SFT) to consume image tokens alongside text. Simple, modular, cheap to train — only projector + LLM adapter are trained. Limitation: vision encoder can't see text context. See [[LLaVA]] and [[CLIP]].

**What's the difference between stitched, cross-attention, and native multimodal?**
- **Stitched** (LLaVA): frozen vision encoder + projector + LLM. Simple, modular, limited fusion.
- **Cross-attention** (BLIP-2): Q-Former compresses image into few tokens, LLM gets via cross-attention. Better fusion, more complex.
- **Native** (GPT-4o): image patches and text tokens in one Transformer. Maximum integration, requires massive multimodal training data.

See [[Multimodal AI Overview]] and [[BLIP-2]].

**Why are native multimodal models (Gemini) better than stitched (LLaVA)?**
Native multimodal models train on text + images + audio from the start; the Transformer learns cross-modal representations during pretraining. Stitched models (LLaVA) bolt a vision encoder onto a pretrained LLM via a projector; the LLM doesn't natively understand images. Native models have: (1) better cross-modal reasoning, (2) lower latency (no separate vision encoder forward pass), (3) better grounding (image features are deeply integrated). Trade-off: native models require massive multimodal training data and compute; stitched models are cheaper to train. See [[Multimodal AI Overview]].

**How does SigLIP-2 differ from CLIP?**
Three differences. (1) **Loss**: CLIP uses softmax contrastive (pick matching text out of N candidates); SigLIP-2 uses sigmoid (each pair independently classified). Sigmoid is simpler, works at smaller batch sizes. (2) **Self-supervised pretraining**: SigLIP-2 does DINOv2-style self-supervised vision pretraining *before* contrastive training. CLIP trains from scratch. (3) **Multilingual**: SigLIP-2 supports 100+ languages natively; CLIP is primarily English. SigLIP-2 beats CLIP by 6+ points on ImageNet zero-shot. See [[SigLIP-2]] and [[CLIP]].

**Why are VLMs more expensive than text LLMs?**
Images consume 500-4000 tokens depending on resolution and model. A 1024×1024 image in GPT-4o = ~750 tokens = ~$0.002 per image. For document-heavy apps (10+ images per query), costs add up. Mitigations: tile large images, cache image embeddings, use smaller vision encoders. See [[Multimodal AI Overview]].

**When does a VLM cost more than 10× a text LLM?**
When images consume 1000+ tokens each AND there are 10+ images per query. A 1024×1024 image in GPT-4o = ~750 tokens. For a document-heavy app (10+ pages), that's 7.5K tokens just for images. At $5/1M input tokens, that's $0.04 per query just for images. Mitigations: (1) tile large images, (2) cache image embeddings, (3) use smaller vision encoders, (4) OCR + text LLM for purely textual content in images. See [[Multimodal AI Overview]].

**When would you use a VLM vs OCR + text LLM?**
VLM when (1) visual content adds value beyond extractable text (charts, diagrams, handwriting), (2) task needs visual reasoning, (3) UX benefits from image input. OCR + text LLM when (1) input is mostly text in images, (2) cost/latency critical, (3) task is purely linguistic. VLMs are 5-10× more expensive; only use when visual content adds value.

**How does ColPali differ from traditional document RAG?**
Traditional document RAG: OCR the document → chunk → embed → retrieve. ColPali: skip OCR entirely; embed the document page as an image (using SigLIP/CLIP-style encoder) → retrieve via late interaction (max-sim over patches). ColPali is faster (no OCR), handles visual content better (charts, tables, diagrams), and matches text-only retrieval quality. The trade-off: ColPali requires VLM-grade vision encoders, which are larger than text-only embedders. See [[ColPali]] and [[SigLIP-2]].

## Retrieval-augmented generation

**Why use hybrid search (BM25 + vector)?**
Pure vector search misses exact-match queries (product codes, names, error messages). Pure BM25 misses semantic matches. Combining both (typically with reciprocal rank fusion) gives the best of both. See [[Chunking, Hybrid Search, and Reranking]].

**When does GraphRAG beat vector RAG?**
Three cases. (1) **Multi-hop reasoning**: questions requiring connecting info across documents ("Who founded the company that acquired X?"). (2) **Entity-centric queries**: questions about a specific entity ("What do we know about OpenAI?"). (3) **Global questions**: questions about the whole corpus ("What are the main themes?"). For single-hop factual questions, vector RAG is sufficient and faster. See [[Advanced RAG Patterns]] and [[Build a Knowledge-Graph Construction Pipeline]].

**How do you handle entity deduplication in GraphRAG?**
Three approaches. (1) **String normalization**: lowercase, strip punctuation, remove legal suffixes (Inc, Corp, Ltd). Catches obvious cases. (2) **Embedding similarity**: embed entity names, cluster by cosine similarity (>0.9), merge clusters. Catches semantic duplicates. (3) **LLM-based matching**: for each new entity, ask LLM "is this the same as any existing entity?" Catches subtle cases (acronyms, aliases). Production: combine all three — normalization first (cheap), then embedding (medium cost), then LLM (expensive, only for ambiguous cases). See [[Build a Knowledge-Graph Construction Pipeline]].

**How does Microsoft GraphRAG differ from a basic GraphRAG pipeline?**
Two key additions. (1) **Hierarchical summarization**: detects communities (clusters of related entities), summarizes each community into a higher-level description. Enables global questions ("what are the main themes?") that pure entity-lookup can't answer. (2) **Query routing**: detects whether a query is "local" (specific entity, multi-hop) or "global" (corpus-wide theme) and routes to different retrieval strategies. Local uses entity lookup + subgraph extraction; global uses community summaries. See [[Build a Knowledge-Graph Construction Pipeline]].

**How would you design a multi-tenant RAG system?**
- Postgres + pgvector for storage; row-level security for tenant isolation.
- Per-tenant namespaces for embeddings and metadata.
- Cache per-tenant (don't share LLM responses across tenants).
- Rate limit per tenant.
- Audit log per tenant.
- PII redaction at ingest.
- Hybrid search (BM25 + vector) + reranker.

See [[RAG]], [[RAG Pipeline Overview]], [[PII and Data Leakage]], and [[Production AI Stack]].

## Long-context behavior

**What is "lost in the middle"?**
Models retrieve information well at the start and end of context but fail in the middle. The heatmap (position × accuracy) shows a U-shape: high accuracy at 0% and 100%, low in 50%. Caused by attention's positional bias (some positions get more attention weight than others, regardless of content). Mitigations: (1) reorder context to put important info at edges, (2) use YaRN/NTK scaling for better position encoding, (3) use hybrid attention (Jamba, MiniMax-01) which is more uniform. See [[Long-Context Architectures]] and [[Build a Long-Context Evaluation Harness]].

**What is YaRN, and how does it extend context length?**
YaRN (Yet another RoPE extensioN) interpolates RoPE frequencies non-uniformly — higher frequencies interpolated more aggressively, lower frequencies less. This is based on the observation that high-frequency components encode local position (less affected by length extension) while low-frequency components encode global position (more affected). Extends RoPE models to 4–32× training length without retraining. Used by Llama 3.1 to extend from 8K to 128K. See [[YaRN and NTK-Aware Scaling]] and [[RoPE]].

**How do hybrid attention models (Kimi K2, MiniMax-01) achieve 1M context?**
Hybrid attention models use mostly linear-attention layers (O(n) complexity) with periodic full-attention layers (O(n²) but sparse). The KV cache grows linearly with most layers (linear attention has fixed-size state) and quadratically only with the few full-attention layers. Net: KV cache grows ~O(n) instead of O(n²). A pure-attention model at 1M tokens would need ~500GB of KV cache; a hybrid can fit in ~50GB. See [[Kimi Linear]] and [[MiniMax-01]].

## Agents and tool use

**What's the difference between an LLM app, a workflow, and an agent?**
- **LLM app**: single call, no tools, no state.
- **Workflow**: multi-step with predefined control flow.
- **Agent**: LLM decides next step in a loop with tools.
- **Autonomous agent**: long-running, self-directed.

See [[Agent vs Workflow vs LLM Application]].

**What does ReAct stand for?**
**Rea**soning + **A**c**t**ing. The pattern: Thought → Action → Observation → Thought → ... → Finish. Combines chain-of-thought reasoning with tool use. See [[ReAct Pattern]] and [[Chain of Thought]].

### Model Context Protocol

**What is MCP, and why does it exist?**
MCP (Anthropic, 2024) is an open protocol for connecting LLMs to external tools, resources, and prompts. It exists because every LLM provider had their own tool-calling format, fragmenting the ecosystem. MCP standardizes the protocol so an MCP server works with any MCP-compatible client (Claude, Cursor, custom apps). See [[MCP Overview]] and [[Function Calling]].

**What are the three resource types in MCP?**
1. **Tools**: functions the LLM can call (e.g., `search_database`, `send_email`). Schema-based; LLM decides when to call.
2. **Resources**: data the LLM can read (e.g., file contents, database rows). Client decides what to expose.
3. **Prompts**: pre-written prompt templates the user can invoke (e.g., `summarize this file`). User-initiated, not LLM-initiated.

In short: tools are LLM-driven; resources are client-driven; prompts are user-driven. See [[MCP Components]].

**How does MCP differ from function calling?**
Function calling is the LLM API feature (LLM emits a structured tool-call request). MCP is a *protocol* that wraps function calling with: server discovery, schema management, authentication, and a standard client-server architecture. MCP uses function calling internally but adds the protocol layer. Use MCP for cross-client tool sharing (a single MCP server works with Claude, Cursor, custom apps); use function calling for app-specific tools. See [[MCP Overview]] and [[Function Calling]].

**What transports does MCP support?**
1. **stdio**: client spawns server as subprocess; communication via stdin/stdout. Simple, local.
2. **HTTP+SSE**: client connects to server over HTTP; server-sent events for streaming. Remote, scalable.
3. **WebSocket**: bidirectional, useful for interactive sessions.

Most local MCP servers use stdio; remote/enterprise servers use HTTP+SSE. See [[MCP Overview]].

**How do you secure an MCP server?**
Six layers. (1) **Authentication**: OAuth 2.0 or API keys; never trust the client. (2) **Authorization**: per-tool permissions; not every client should call every tool. (3) **Input validation**: validate all tool inputs against a strict schema; reject malformed inputs. (4) **Rate limiting**: per-client rate limits to prevent DoS. (5) **Audit logging**: log every tool call for forensics. (6) **Sandboxing**: run dangerous tools (file system, shell) in a sandbox; never on the host. See [[MCP Security]].

**How would you design an MCP marketplace?**
A registry for publishing/discovering MCP servers. Components: (1) **Server registry**: list of published MCP servers with metadata (name, version, description, owner). (2) **Discovery**: search by capability ("find servers that expose `send_email`"). (3) **Security scanning**: scan published servers for known vulnerabilities (prompt injection, command injection, excessive permissions). (4) **Versioning**: support multiple versions per server; allow rollback. (5) **Reviews/ratings**: community-driven quality signal. See [[Build an MCP Marketplace]] and [[MCP Security]].

## Memory systems

**What are the four types of memory in AI systems?**
1. **Working memory**: current context (the prompt, recent turns).
2. **Episodic memory**: past experiences (specific conversations, events).
3. **Semantic memory**: facts and knowledge (user preferences, world knowledge).
4. **Procedural memory**: how-to knowledge (skills, workflows, tool patterns).

See [[Memory Types]].

**How does MemGPT work?**
MemGPT (Packer et al. 2023) borrows from OS virtual memory: a fixed-size "main context" (LLM's context window) plus a "secondary storage" of older messages. The LLM itself decides when to page in/out (via special function calls). This gives the appearance of unbounded memory within a fixed context window. See [[MemGPT and Letta]].

**When do you need vector memory vs. knowledge graph memory?**
- **Vector memory**: unstructured text snippets (past conversations, documents). Best for "find similar past interactions."
- **Knowledge graph memory**: structured entities and relations (user → friends → preferences). Best for "what do I know about this entity and its connections."
- **Hybrid**: most production systems use both — vectors for fuzzy recall, KG for structured queries.

See [[Vector Memory Backends]].

## Multi-agent systems

**When should you use multi-agent vs single-agent?**
Multi-agent when: (1) task decomposes into specialist roles, (2) one LLM's context can't hold all info, (3) different sub-tasks need different models, (4) you need verification (one produces, another critiques), (5) long-running with parallelism. Single-agent otherwise — start single, move to multi only when you hit a ceiling. See [[Multi-Agent Architectures]].

**What are the common multi-agent patterns?**
1. **Hierarchical** (planner-executor): clear division of labor, rigid.
2. **Manager-worker**: dynamic delegation, parallel execution.
3. **Peer swarm**: agents discuss as equals, robust but unbounded.
4. **Blackboard**: shared state, decoupled agents.
5. **Marketplace/bidding**: agents bid on tasks, self-organizing.

See [[Multi-Agent Architectures]].

**How do you prevent multi-agent systems from looping forever?**
Four safeguards: (1) iteration cap per agent and per workflow, (2) timeout per agent and per task, (3) convergence detection (state stops changing → terminate), (4) cycle detection in graph-based systems (LangGraph has built-in recursion limits). Combine all four.

**Why is LangGraph the production standard for multi-agent in 2026?**
Four reasons: (1) durable execution (survives crashes via checkpointing), (2) observable (LangSmith integration), (3) graph-based (explicit state and edges make control flow debuggable), (4) mature (battle-tested at scale). Alternatives ([[AutoGen]], [[CrewAI]]) lag on durability and observability. See [[LangGraph]].

## Model architecture frontiers

Where capacity, attention, and memory architecture are heading: sparse experts, state space hybrids, and the converged 2026 recipe.

### Mixture of Experts and sparse capacity

**What is MoE and how does routing work?**
Mixture-of-Experts replaces each FFN with multiple parallel FFN "experts" plus a router. Each token activates only top-k experts (typically 2). The router is a small linear layer that outputs a probability distribution over experts; the top-k are selected. Decouples parameter count from compute — you get more capacity at the same compute cost. See [[Mixture of Experts]].

**What is the difference between dense and MoE models?**
- **Dense** (Llama 3 70B): all parameters active per token. Linear scaling of compute with parameters.
- **MoE** (Mixtral 8x7B, DeepSeek-V3): only top-k experts active per token. Decouples parameters from compute — more capacity at same compute cost.

Trade-off: MoE has higher memory requirements (all experts in memory) but lower compute per token. Better when memory is cheap and compute is expensive (most serving scenarios). See [[Mistral and Mixtral Architecture]] and [[Mixture of Experts]].

**What is the auxiliary-loss-free routing in DeepSeek-V3?**
Standard MoE uses an auxiliary loss to balance load across experts (prevents all tokens routing to one expert). DeepSeek-V3's innovation: bias terms added to the router's logits, dynamically adjusted based on actual load. Eliminates the auxiliary loss (which can hurt quality) while maintaining balance. See [[DeepSeek Architecture]] and [[DeepSeek-V2 and V3]].

**Why does DeepSeek-V3 use MLA instead of GQA?**
MLA (Multi-head Latent Attention) compresses K and V into a low-rank latent vector, achieving KV cache sizes even smaller than MQA while maintaining MHA-like quality. This is what makes DeepSeek-V3 (671B total, 37B active) economical to serve — the KV cache is small enough to fit on a single node. See [[GQA MQA and MLA]], [[DeepSeek Architecture]], and [[DeepSeek-V2 and V3]].

### State space models and hybrid attention

**What is Mamba, and how does it differ from attention?**
Mamba is a selective state space model (SSM). Differences: (1) $O(n)$ training vs $O(n^2)$ for attention, (2) $O(1)$ inference memory (fixed state) vs $O(n)$ (growing KV cache), (3) approximate recall (state compresses history) vs exact recall (attention can copy any token), (4) weaker ICL (no induction heads). See [[SSMs Mamba and Frontiers]] and [[Mamba]].

**Why do hybrid SSM-Transformer models (Jamba, Zamba, Kimi K2) outperform pure SSMs?**
Pure SSMs (Mamba, Mamba-2) compress history into a fixed-size state, losing exact token-level information. They fail at in-context retrieval (looking up a specific earlier token). At large scale, attention's exact recall and ICL matter more; pure Mamba compresses history into a fixed state, losing exact details. Hybrids (Jamba, Zamba, Kimi K2) add a few attention layers (1:7 ratio is common) for recall + ICL, while using many Mamba/SSM layers for efficiency. Best of both: O(n) complexity from SSMs + exact recall from attention. H3 (2022) was the first to demonstrate this pattern. See [[SSMs Mamba and Frontiers]], [[Jamba]], and [[H3]].

**What is "lightning attention" in MiniMax-01?**
Lightning attention is MiniMax's specific linear-attention formulation. It's a kernel-friendly variant of linear attention that achieves near-optimal throughput on modern GPUs. The key innovation: a specific tensor contraction pattern that maps well to GPU memory hierarchy (similar to FlashAttention for softmax attention). Other labs use different formulations (Kimi's Mamba-style selective scan, GLM's sparse attention). The 2026 hybrid-attention landscape has multiple competing formulations; it's unclear which will win. See [[MiniMax-01]] and [[Linear Attention]].

**What are Titans, and how do they differ from attention and SSMs?**
Titans (Google, 2024) introduce a **neural long-term memory module** that persists across sequences, updated via gradient descent on a "surprise" metric. Unlike attention (no persistent state) or SSMs (fixed state), Titans learn what to memorize and what to forget. The memory module is updated online during inference (test-time learning). A potential third way beyond attention and SSMs — but production deployment is still early. See [[Titans]] and [[DeltaNet and Titans]].

**Why is the 7:1 SSM:attention ratio common in hybrids?**
Empirically, 7:1 (Jamba) and similar ratios (MiniMax-01, Kimi K2) balance efficiency and quality. Lower ratios (more attention) → better quality but quadratic cost. Higher ratios (more SSM) → better efficiency but worse retrieval. 7:1 was found to be a sweet spot — enough attention layers to enable induction heads and in-context learning, enough SSM layers to keep compute O(n). Different ratios work for different use cases: code generation benefits from more attention; long-context summarization benefits from more SSM. See [[RWKV and RetNet]].

### The 2026 frontier

**What's the converged 2026 frontier recipe?**
By 2026, every frontier model uses: **MoE capacity** (8–256 experts, 2–8 active) + **hybrid attention** (linear + full, ~7:1 ratio) + **RoPE with YaRN scaling** + **RMSNorm pre-norm** + **SwiGLU activation** + **long context** (256K–1M tokens) + **RL on verifiable rewards** for reasoning + **native multimodal** fusion + **EAGLE-3 spec decoding** for inference. The convergence is striking — the 2024 "Llama-style" recipe has been extended with sparse capacity and hybrid attention. See [[Frontier Model Synthesis 2026]].

**Why has the field converged on MoE + hybrid attention?**
Two reasons. (1) **Compute efficiency**: MoE decouples capacity from compute (more parameters at same FLOPs); hybrid attention reduces context complexity from O(n²) to O(n). Both directly reduce cost. (2) **Quality**: empirically, MoE matches dense quality at lower compute; hybrid attention matches pure-attention quality at lower compute. Both have been validated at frontier scale (DeepSeek-V3, Kimi K2, MiniMax-01). The combination gives 5–10× cost reduction vs dense pure-attention models at the same quality. See [[Frontier Model Synthesis 2026]].

**What's the next architectural revolution after MoE + hybrid attention?**
Unclear. Candidates: (1) **Titans-style test-time learning** (neural memory updated at inference). (2) **Truly sub-quadratic attention** (better than current linear attention formulations). (3) **Multimodal-native architectures** (single Transformer for text+image+audio+video, not separate encoders). (4) **Neuro-symbolic hybrids** (neural + symbolic reasoning). None of these has reached frontier-scale production deployment as of 2026. The field may be entering a period of consolidation rather than revolution. See [[Frontier Model Synthesis 2026]].

## Interpretability

**What is mechanistic interpretability?**
Reverse-engineering neural networks into understandable circuits. Key findings: (1) the residual stream is a memory bus, (2) attention heads specialize (previous-token, induction, syntactic), (3) features can be decomposed via sparse autoencoders. Pioneered by Anthropic. See [[Mechanistic Interpretability]].

**What is an induction head?**
A two-head circuit that implements in-context learning: (1) a previous-token head writes "the previous token was X" into the residual stream, (2) the induction head finds previous occurrences of X's predecessor and copies its successor. Together: "if you saw A→B before, predict B when you see A." Emerges suddenly during training. See [[Mechanistic Interpretability]].

**What is polysemanticity, and how do SAEs address it?**
Polysemanticity: a single neuron fires for multiple unrelated concepts (cat, DNA, French Revolution). Happens because there are more concepts than neurons — the model uses superposition. SAEs decompose activations into many sparse monosemantic features, each firing for one concept. See [[Sparse Autoencoders]] and [[Mechanistic Interpretability]].

**What is a steering vector?**
A direction in activation space corresponding to a property (sentiment, honesty, toxicity), found by training a linear probe. You can steer the model by adding/subtracting this direction from the residual stream during inference — adding amplifies the property, subtracting suppresses it. "Representation engineering." See [[Probing]].

## Production AI

**How do you evaluate an LLM application?**
- **Offline**: golden set of 50–200 examples; LLM-as-judge + human review.
- **Online**: A/B testing, shadow deployment, user feedback (thumbs up/down).
- **Monitoring**: latency, cost, error rate, hallucination rate (sampled LLM-as-judge).
- **Benchmarks**: MMLU, GPQA for capability; task-specific for your domain.

See [[LLM Benchmarks]] and [[Build a RAG Evaluation Harness]].

**What is prompt injection and how do you defend?**
Adversarial inputs that hijack the model's behavior. Defenses: input filtering, output validation, system prompt isolation, guardrail models (Llama Guard), sandboxing, human-in-the-loop for sensitive actions. No complete defense — use defense-in-depth. See [[LLM Security and Prompt Injection]] and [[Guardrails]].

**What is prompt injection, and why is it hard to defend?**
Adversarial inputs that hijack the model's behavior. Hard to defend because LLMs can't distinguish "instructions" from "data" — both are text in the same context. No complete defense in 2026; use defense-in-depth (input filtering, output validation, guardrail models, sandboxing). See [[LLM Security and Prompt Injection]].

**What's the difference between direct and indirect prompt injection?**
- **Direct**: attacker is the user, explicitly trying to override instructions ("ignore previous instructions").
- **Indirect**: attacker embeds instructions in data the model reads (web pages, PDFs, retrieved documents). User is the victim; attacker is a third party. Indirect is more dangerous because the user didn't write the malicious content.

See [[LLM Security and Prompt Injection]].

**How do you secure an LLM agent that takes real-world actions?**
Six layers: (1) sandbox (Docker, no network), (2) least privilege (minimal auth), (3) allowlist (only approved APIs/tools), (4) human-in-the-loop for destructive actions (email, delete, pay), (5) audit logging, (6) rate limits per session. See [[LLM Security and Prompt Injection]] and [[Human-in-the-Loop Patterns]].

**What is the OWASP Top 10 for LLMs?**
The standard LLM security taxonomy: (1) prompt injection, (2) insecure output handling, (3) training data poisoning, (4) model DoS, (5) supply chain, (6) sensitive info disclosure, (7) insecure plugins, (8) excessive agency, (9) overreliance/hallucination, (10) model theft. See [[LLM Security and Prompt Injection]].

**How would you reduce LLM serving costs by 80%?**
Stack: (1) model routing — 50% reduction (route easy to small model), (2) quantization — 50% reduction (INT8/FP8), (3) prompt caching — 30-60% for templated prompts, (4) continuous batching — 2-5× throughput, (5) response caching — 10-30% for repeated queries. Combined: 80-90% cost reduction with ~1-3% quality loss. See [[Production AI Stack]], [[Gateway and Router Patterns]], and [[Quantization]].

## How to use this note

Work each question actively rather than reading passively. For each question: (1) try to answer without looking; (2) check the answer above; (3) read the linked concept note for depth; (4) practice out loud — interview answers should be 30–60 seconds, not 5 minutes; and (5) for conceptual depth, also read any "Interview Questions" section at the end of the linked concept notes for extra practice material.

## See also

- [[Interview Prep MOC]]
- [[Coding Interview Questions]]
- [[System Design Interview Questions]]
- [[Conceptual Questions on Neural Network Fundamentals]]
- [[Glossary MOC]]
- [[Agents and Tooling MOC]]
- [[Interpretability and Research MOC]]
- [[Papers MOC]]
- [[Projects MOC]]
