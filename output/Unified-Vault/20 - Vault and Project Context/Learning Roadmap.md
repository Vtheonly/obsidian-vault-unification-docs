---
title: Learning Roadmap
type: reference
aliases: [Curriculum Roadmap, Study Roadmap, Learning Path]
tags: [roadmap, curriculum, learning-path, navigation]
sources: ["Learning Roadmap"]
created_index: 7
---

This note preserves the collection's curriculum-style study path — a learner's route from foundations to research frontiers, designed for someone with roughly 12–18 months of part-time study to invest. It is organized as fourteen phases (0–13), each with a goal, a reading list, a build exercise, and a checkpoint, and it remains the collection's canonical answer to "in what order should I learn this field?". The phase reading lists name the collection's domain maps and concept notes; the links resolve to the topical area maps and notes where each subject now lives.

## How to use this roadmap

Each phase has four parts:

- **Goal** — what you should be able to do at the end.
- **Read** — the MOCs and key notes to read, in order.
- **Build** — a small project to consolidate the material.
- **Checkpoint** — questions you should be able to answer.

Skip a phase only if you can already pass its checkpoint.

## Phase 0 — Mathematical Foundations (4–6 weeks)

The goal is to re-derive scaled dot-product attention from scratch on a whiteboard. This phase drills the linear algebra, probability, calculus, optimization, and information theory that every later phase assumes.

**Read:**

- [[Mathematics MOC]]
- Linear algebra: vectors, dot products, matrix multiplication, SVD — [[Vectors]], [[Dot Product]], [[Matrix Multiplication]], [[Matrix Decomposition]]
- Probability: distributions, Bayes, entropy, cross-entropy, KL — [[Probability Essentials]], [[Bayes Theorem]], [[Entropy Cross-Entropy and KL Divergence]]
- Calculus: gradients, chain rule, Jacobians — [[Gradients and Gradient Descent]], [[Gradient and Chain Rule]], [[02 - Mathematics/Calculus/Jacobians and Hessians|Jacobians and Hessians]]
- Optimization: gradient descent → AdamW, LR schedules — [[Gradient Descent]], [[Adam Optimizer Derivation]], [[Learning Rate Schedules]]
- Information theory: entropy, mutual information

**Build:**

- Implement softmax from scratch (with numerical stability).
- Implement matrix multiplication from scratch and verify against `numpy`.

**Checkpoint:**

- Why does softmax saturate for large logits?
- Why is cross-entropy the natural loss for classification?
- Why does Adam combine momentum and RMSProp?

## Phase 1 — ML & Neural Network Foundations (4–6 weeks)

The goal is to train an MLP from scratch (no framework) on MNIST. This phase pairs the classical machine-learning material with the neural-network fundamentals that carry the rest of the curriculum.

**Read:**

- [[Machine Learning MOC]]
- [[Neural Network Foundations MOC|Neural Networks MOC]]
- Bias-variance, regularization — [[Bias Variance Tradeoff]], [[Regularization Techniques]]
- Backpropagation derivation (with computation graph) — [[Backpropagation]]
- MLPs, activation functions (ReLU, GELU) — [[Perceptrons and Multi-Layer Perceptrons]], [[Activation Functions]]
- Optimizers, initialization (Xavier, He) — [[Optimizers and Learning Rate Schedulers]], [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]

**Build:**

- Implement backprop by hand on a 2-layer MLP.
- Then implement the same MLP in PyTorch.

**Checkpoint:**

- Derive the gradient of softmax + cross-entropy.
- Why does He initialization help ReLU networks?

## Phase 2 — Sequence Modeling & Pre-Transformer NLP (3–4 weeks)

The goal is to understand why attention was invented. This phase walks the pre-Transformer world — tokenization, embeddings, n-gram and recurrent language models, and the seq2seq bottleneck that motivated attention.

**Read:**

- [[NLP and Language Models MOC|NLP Fundamentals MOC]]
- Tokenization: BPE, WordPiece, SentencePiece — [[BPE]], [[WordPiece]], [[SentencePiece]]
- Word embeddings: Word2Vec, GloVe, FastText — [[Word2Vec GloVe and FastText]]
- N-gram LMs, perplexity — [[N-Gram Language Models]], [[Perplexity]]
- RNN / LSTM / GRU — [[Recurrent Neural Networks]], [[LSTM]], [[GRU]]
- Seq2Seq and the information bottleneck — [[Seq2Seq and the Information Bottleneck]]
- Bahdanau attention — [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]

**Build:**

- Train a small BPE tokenizer on a corpus.
- Train a small character-level RNN-LM.

**Checkpoint:**

- Why does the Seq2Seq encoder-decoder bottleneck motivate attention?
- What problem does BPE solve over word-level tokenization?

## Phase 3 — Attention & The Transformer (4–6 weeks)

The goal is to implement a Transformer block from scratch in PyTorch. This is the centerpiece phase: the attention mechanism and the architecture built on it.

**Read:**

- [[Attention and Transformers MOC|Attention Mechanisms MOC]]
- [[Attention and Transformers MOC|Transformers MOC]]
- Self-attention — [[Self-Attention]]
- Multi-head attention — [[Multi-Head Attention]]
- Positional encoding — [[Positional Encoding]], [[RoPE]]
- The Transformer block — [[Transformer Block]]
- Pre-norm vs post-norm — [[Pre-Norm vs Post-Norm]]
- LayerNorm / RMSNorm — [[Normalization Layers]]

**Build:**

- Implement scaled dot-product attention.
- Implement multi-head attention.
- Implement a full Transformer encoder block.
- Train it on a toy task (e.g., copy, sort).

**Checkpoint:**

- Why scale by √d_k?
- Why use multiple heads?
- Why RoPE over sinusoidal encoding?

## Phase 4 — LLMs (4–6 weeks)

The goal is to understand the modern LLM stack end-to-end — architecture, caching, sampling, evaluation, capabilities, and failure modes.

**Read:**

- [[Large Language Models MOC|LLMs MOC]]
- Decoder-only architecture — [[Decoder-Only Architecture]]
- KV cache — [[KV Cache Mechanics]]
- Sampling — [[Sampling Strategies]]
- In-context learning — [[In-Context Learning]]
- Tool use / function calling — [[Function Calling]]
- Evaluation: MMLU, GPQA, HumanEval — [[LLM Benchmarks]]
- Hallucination causes — [[Hallucination]]

**Build:**

- Generate text from a small LLM (e.g., GPT-2) with top-k, top-p, temperature.
- Implement a basic KV cache.

**Checkpoint:**

- Why is the KV cache critical for autoregressive inference?
- What's the difference between top-k and top-p?
- What makes a model "instruction-tuned"?

## Phase 5 — Training & Fine-Tuning (4–6 weeks)

The goal is to LoRA-fine-tune a small LLM on a custom dataset. This phase covers the full training side: pretraining objectives and scaling laws through alignment.

**Read:**

- [[Training and Adaptation MOC|Training MOC]]
- [[Training and Adaptation MOC|Fine-Tuning MOC]]
- Pretraining objectives — [[Pretraining Objectives and Scaling Laws]]
- Scaling laws (Chinchilla) — [[Scaling Laws (Kaplan and Chinchilla)]]
- Distributed training (DP/TP/PP/ZeRO/FSDP) — [[Distributed Training]]
- SFT, instruction tuning — [[Instruction Tuning and Chat Templates]]
- LoRA — [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- QLoRA — [[QLoRA]]
- RLHF with PPO — [[RLHF with PPO]]
- DPO — [[DPO Derivation]]

**Build:**

- LoRA-fine-tune a small LLM (e.g., Llama-3.2-1B) on a custom instruction dataset.
- Optionally: DPO fine-tune.

**Checkpoint:**

- Why is LoRA parameter-efficient?
- Why does DPO not need a reward model?
- Why does PPO need a reference model?

## Phase 6 — Inference Engineering (3–4 weeks)

The goal is to serve a small LLM with vLLM and understand the internals — the caching, batching, quantization, and decoding tricks that make serving fast.

**Read:**

- [[Inference and Production MOC|Inference MOC]]
- KV cache deep dive — [[KV Cache Mechanics]]
- PagedAttention — [[PagedAttention]]
- Continuous batching — [[Continuous Batching]]
- Quantization (INT8, INT4, FP8, GPTQ, AWQ, GGUF) — [[Quantization]]
- Speculative decoding — [[Speculative Decoding]]
- vLLM, TGI, TensorRT-LLM — [[14 - Inference and Production/Inference/vLLM|vLLM]], [[TGI]], [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]]

**Build:**

- Serve a 7B LLM with vLLM.
- Benchmark latency/throughput at different batch sizes.
- Quantize a model with AWQ and measure quality + speed.

**Checkpoint:**

- Why is PagedAttention faster than naive KV caching?
- When does speculative decoding help?
- INT4 vs INT8 — quality/speed/memory tradeoffs.

## Phase 7 — Agents & Tool Calling (4–6 weeks)

The goal is to build a small agent that uses tools to complete a multi-step task. This phase covers the reasoning patterns and tool interfaces that make an LLM act.

**Read:**

- [[Agents and Tooling MOC|AI Agents MOC]]
- Agent vs workflow vs LLM app — [[Agent vs Workflow vs LLM Application]]
- ReAct — [[ReAct Pattern]]
- Chain-of-Thought — [[Chain of Thought]]
- Function calling — [[Function Calling]]
- Reflection — [[Reflection]]
- Planner-executor pattern — [[Planner-Executor Pattern]]
- Tree-of-Thoughts (planned) — [[Tree of Thoughts]]

**Build:**

- Build a ReAct agent that can search the web, run Python, and answer multi-step questions.

**Checkpoint:**

- What's the difference between an LLM app, workflow, and agent?
- When does reflection help vs hurt?
- How do you prevent infinite loops in agents?

## Phase 8 — RAG & Memory (4–6 weeks)

The goal is to build a production-quality RAG pipeline. This phase pairs retrieval-augmented generation with the memory systems that give agents persistent state.

**Read:**

- [[Agents and Tooling MOC|RAG MOC]]
- [[Agents and Tooling MOC|Memory Systems MOC]]
- RAG pipeline overview — [[RAG Pipeline Overview]]
- Chunking strategies — [[Chunking, Hybrid Search, and Reranking]]
- Embedding models — [[Embedding Models for Retrieval]]
- Hybrid search (BM25 + vector) — [[BM25]]
- Reranking
- GraphRAG, Agentic RAG, Self-RAG — [[Advanced RAG Patterns]]
- Memory types — [[Memory Types]]
- Vector DBs — [[Vector Memory Backends]]

**Build:**

- Build a RAG pipeline over a corpus of PDFs.
- Add BM25 + vector hybrid search.
- Add a cross-encoder reranker.
- Evaluate with RAGAS.

**Checkpoint:**

- Why does hybrid search outperform pure vector search?
- When does GraphRAG beat vanilla RAG?
- How do you evaluate citation faithfulness?

## Phase 9 — MCP & Multi-Agent Systems (3–4 weeks)

The goal is to build a multi-agent system over MCP. This phase covers the Model Context Protocol and the coordination patterns of multi-agent architectures.

**Read:**

- [[Agents and Tooling MOC|MCP MOC]]
- [[Agents and Tooling MOC|Multi-Agent Systems MOC]]
- MCP architecture — [[MCP Overview]]
- MCP resources/prompts/tools — [[MCP Components]]
- Multi-agent architectures (hierarchical, swarm, blackboard) — [[Multi-Agent Architectures]]
- Coordination, communication, consensus — [[Coordination and Consensus]], [[Communication Patterns]]

**Build:**

- Expose a small tool over MCP.
- Build a 2-agent system (planner + executor) that uses MCP tools.

**Checkpoint:**

- What problem does MCP solve that function calling doesn't?
- When does a multi-agent system outperform a single agent?

## Phase 10 — Infrastructure, LLMOps & Production (4–6 weeks)

The goal is to deploy an LLM application to production with monitoring. This phase covers the infrastructure, operations, and production-hardening layers of the stack.

**Read:**

- [[Inference and Production MOC|AI Infrastructure MOC]]
- [[Inference and Production MOC|LLMOps MOC]]
- [[Inference and Production MOC|Production AI MOC]]
- FastAPI, Docker, Kubernetes
- PostgreSQL + pgvector, Redis, Kafka — [[Vector Storage with pgvector]], [[Messaging with Kafka and Celery]]
- Monitoring, drift detection — [[Production Monitoring]]
- Prompt injection defense — [[LLM Security and Prompt Injection]]
- Cost optimization — [[Cost Optimization]]

**Build:**

- Deploy a RAG application with FastAPI + Docker + Postgres + pgvector.
- Add Prometheus + Grafana monitoring — [[Observability Stack]].
- Add guardrails (prompt injection detection) — [[Guardrails]].

**Checkpoint:**

- How do you detect prompt injection?
- How do you measure and reduce cost per query?
- What's your rollback strategy?

## Phase 11 — Model Architecture Research (ongoing)

The goal is to read the major model technical reports and understand each architecture's choices. This phase is ongoing: the model landscape keeps moving.

**Read:**

- [[Interpretability and Research MOC|Model Architecture Research MOC]]
- Llama, Mistral, DeepSeek, Qwen, Gemma — [[Llama Family Architecture]], [[Mistral and Mixtral Architecture]], [[DeepSeek Architecture]], [[Qwen Family Architecture]], [[Gemma Architecture]]
- GPT, Claude, Gemini (publicly disclosed portions) — [[GPT-4 Inferred Architecture]], [[Claude Architecture]], [[Gemini Architecture]]
- MLA (DeepSeek), GQA (Llama), MoE configurations — [[GQA MQA and MLA]], [[Mixture of Experts]]

**Build:**

- Compare architectures in a table.
- Pick one architectural innovation (e.g., MLA) and write a deep note on it.

**Checkpoint:**

- What's the difference between MHA, MQA, GQA, MLA?
- Why does DeepSeek use auxiliary-loss-free load balancing?
- What's the tradeoff between dense and MoE?

## Phase 12 — Research Frontiers (ongoing)

The goal is to track the bleeding edge. This phase is ongoing by design.

**Read:**

- [[Interpretability and Research MOC|Research Frontiers MOC]]
- Mamba / Mamba-2 — [[Mamba]], [[Mamba-2]]
- Hybrid architectures (Jamba, Falcon-Mamba) — [[Jamba]]
- Test-time compute, reasoning models — [[Test-Time Compute Scaling]], [[Reasoning Models]]
- Long-context (1M+ tokens) — [[Long-Context Architectures]]
- 2026 emerging architectures — [[Research Frontier Update 2026]]

**Build:**

- Pick one frontier topic and write a deep note.
- Reproduce a small experiment from a recent paper.

**Checkpoint:**

- When does Mamba outperform Transformer attention?
- What's the mechanism behind test-time compute scaling?

## Phase 13 — Papers & Projects (ongoing)

The final phase pairs the paper archive with the project workshop and stays open indefinitely: read landmark papers and build implementations.

**Read:**

- [[Papers MOC]]
- [[Projects MOC]]

**Build (capstones):**

- Implement attention from scratch — [[Build Attention and Transformer From Scratch]] (planned)
- Implement a Transformer from scratch — [[Build Attention and Transformer From Scratch]] (planned)
- Build a mini RAG pipeline — [[Build a Mini RAG Pipeline]] (planned)
- Build a mini agent — [[Build a Mini Agent]] (planned)
- Build a mini MoE — [[Build a Mini MoE]] (planned)

## See also

- [[Reading Orders]] — alternative paths (researcher, engineer, interviewer).
- [[Master Roadmap]] — the full scope of the collection.
- [[Master AI MOC]] — the master map of content.
- [[Master AI README]] — the collection's introduction and domain table.
- [[Master AI Index]] — the collection's master index record.
