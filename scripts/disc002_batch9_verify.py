#!/usr/bin/env python3
"""Targeted corpus verification for batch-9 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware where it matters: several probe 'heading' hits were Python
comments inside code blocks; this script matches content lines, and every
citation used in a decision rationale must appear here with a real line
number.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

CHECKS = [
    # --- covers: agent-architecture title family ---
    ("master-ai", "15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application.md", r"^# Agent vs Workflow vs LLM Application", "agent vs workflow note title"),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"\[\[15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application\]\]", "arch decisions wikilink"),
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"Agent vs Workflow vs LLM Application\|", "ai-vs-ml wikilink"),
    ("master-ai", "08 - LLMs/Capabilities/04 - In-Context Learning.md", r"Agent vs Workflow vs LLM Application\|", "icl wikilink"),
    # --- covers: agent autonomy family ---
    ("master-ai", "15 - AI Agents/Autonomy/08 - Autonomous Agent Lifecycles.md", r"^# 08", "autonomous agent lifecycles title"),
    ("master-ai", "15 - AI Agents/Autonomy/08 - Autonomous Agent Lifecycles.md", r"six phases of an autonomous agent lifecycle", "six phases interview question"),
    ("master-ai", "15 - AI Agents/Autonomy/09 - Human-in-the-Loop Patterns.md", r"Autonomous Agent Lifecycles\]\] — HiTL fits into the lifecycle", "hitl lifecycle link"),
    # --- covers: papers family (constitutional ai / instructgpt / bert) ---
    ("master-ai", "26 - Papers/Alignment/31 - Constitutional AI 2022.md", r"^# 31", "constitutional ai 2022 paper title"),
    ("master-ai", "01 - AI Foundations/03 - A Brief History of AI.md", r"\*\*Constitutional AI\*\* \(Anthropic, 2022\) — RLAIF", "brief history constitutional ai"),
    ("master-ai", "10 - Model Architecture Research/Closed Source/08 - Claude Architecture.md", r"\[\[31 - Constitutional AI 2022\]\]", "claude arch constitutional ai link"),
    ("master-ai", "10 - Model Architecture Research/Closed Source/08 - Claude Architecture.md", r"^### Constitutional AI as the Alignment Method", "claude arch constitutional heading"),
    ("master-ai", "26 - Papers/Alignment/07 - InstructGPT 2022.md", r"^# 07", "instructgpt paper title"),
    ("master-ai", "26 - Papers/Transformers/03 - BERT 2018.md", r"^# 03", "bert 2018 paper title"),
    ("master-ai", "05 - NLP Fundamentals/Embeddings/06 - Contextual Embeddings ELMo to BERT.md", r"^# 06 - Contextual Embeddings", "elmo to bert title"),
    ("master-ai", "07 - Transformers/Encoder Models/07 - BERT.md", r"^## BERT Family", "bert family heading"),
    # --- covers: adaptive learning family ---
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"layer-wise adaptive learning rates", "lamb adaptive rates"),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"^## Adam", "optimization essentials adam heading"),
    ("master-ai", "02 - Mathematics/Optimization/13 - Adam Derivation.md", r"^# 13", "adam derivation title"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^### Adam: The Modern Default Optimizer", "adam modern default heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"Adam combines the ideas of momentum and adaptive learning rates", "adam combines momentum adaptive"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"applies adaptive learning rates", "cnn backprop adaptive rates"),
    # --- covers: dropout family ---
    ("master-ai", "03 - Machine Learning/Generalization/06 - Regularization Techniques.md", r"^## Dropout \(Srivastava", "regularization dropout heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"^# 1[0-9]\. Dropout", "dropout note title"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"Dropout Rate \| Fraction of neurons to drop", "dropout rate table row"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/08. Data Preparation and MLP Implementation.md", r"Regularization strength.*dropout rate", "regularization strength dropout rate"),
    # --- covers: exploding gradient family ---
    ("master-ai", "04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md", r"^### Exploding gradient", "exploding gradient heading master-ai"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"^# 15\. The Vanishing and Exploding Gradient Problems", "vanishing exploding note title"),
    ("ai-course", "07 - Sequence Models and RNNs/07.1 - Motivation and Recurrence/04. The Vanishing and Exploding Gradient Problem in RNNs.md", r"^# 04", "rnn vanishing exploding title"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md", r"^#### The Exploding Gradient Problem", "weight init exploding heading"),
    # --- covers: convolutional base family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"also called the Feature Extractor or the convolutional base", "front-end convolutional base definition"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"^## The Two-Part Architecture: Front-End and Back-End", "two-part architecture heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"^## The Front-End: Feature Extractor", "front-end feature extractor heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"\.features \(convolutional base\)", "features convolutional base"),
    # --- covers: input spatial family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"W\$ = input spatial dimension", "conv formula W definition"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"^# 2\.1 The Output Spatial Dimension Formula", "output spatial dimension title"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"W\$ is the input spatial dimension", "exercises W definition"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"preserves the input spatial dimensions", "same padding preserves input spatial"),
    # --- covers: pth / state_dict family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"^## 7\. model\.state_dict\(\): Saving and Loading", "state_dict section heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"A `state_dict` \(state dictionary\) is a Python dictionary", "state_dict definition"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"A model's `state_dict` is a standard Python dictionary", "summary state_dict definition"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"Saving and Loading the State Dictionary \(Recommended\)", "summary state dict recommended"),
    # --- covers: representational capacity family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/08. Data Preparation and MLP Implementation.md", r"determines model capacity", "hyperparameter determines capacity"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"degrees of freedom that it can fit", "degrees of freedom memorization"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/02. The Mathematics of Receptive Fields and 1x1 Convolutions.md", r"does reduce the representational capacity", "bottleneck reduces capacity"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"loss in representational capacity", "mobilenet capacity loss"),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"larger model capacity at fixed inference cost", "moe larger capacity"),
    # --- covers: attention layer family ---
    ("master-ai", "06 - Attention Mechanisms/Self-Attention/04 - Self-Attention.md", r"learnable parameters per attention layer", "3d2 params per attention layer"),
    ("master-ai", "07 - Transformers/Architecture/01 - Transformer Block.md", r"^### Encoder block \(BERT\)", "encoder block bert heading"),
    ("master-ai", "26 - Papers/2024-2026/30 - Kimi Linear 2025.md", r"linear attention layers per 1 full attention layer", "kimi linear ratio"),
    ("master-ai", "26 - Papers/2024-2026/41 - Jamba 2024.md", r"Sprinkling 1 attention laye", "jamba sprinkling attention"),
    # --- covers: main path family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"convolutions in the main path toward zero", "main path weights to zero"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"the main path output \$F\(x\)\$", "main path output F(x)"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"Even if main path has vanishing gradients", "ann main path gradient"),
    # --- covers: open-weights family ---
    ("master-ai", "10 - Model Architecture Research/Open Source/03 - Llama Family Architecture.md", r"^### Open Weights Enabled Adoption", "llama open weights heading"),
    ("master-ai", "10 - Model Architecture Research/Open Source/03 - Llama Family Architecture.md", r"Standardized open-weights LLM design", "llama standardized open-weights"),
    ("master-ai", "10 - Model Architecture Research/Open Source/05 - Qwen Family Architecture.md", r"China's leading open-weights LLM", "qwen open-weights llm"),
    ("master-ai", "10 - Model Architecture Research/Closed Source/07 - GPT-4 Inferred Architecture.md", r"^## How This Compares to Open-Weights", "gpt4 open-weights comparison"),
    # --- covers: pointwise family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"Pointwise convolution \(1×1\)\*\*: Apply", "mobilenet pointwise conv"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/07. Inception Architecture Deep Dive.md", r"filter that looks at one pixel at a time", "inception pointwise branch"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/02. The Mathematics of Receptive Fields and 1x1 Convolutions.md", r"^## 1×1 Convolutions: Why They Seem Useless", "1x1 why useless heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/02. The Mathematics of Receptive Fields and 1x1 Convolutions.md", r"^### Cross-Channel Mixing", "cross-channel mixing heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"^#### 2\. Pointwise Convolution", "summary pointwise heading"),
    # --- covers: relu family ---
    ("master-ai", "04 - Neural Networks/Foundations/02 - Activation Functions.md", r"^## The ReLU Family", "relu family heading"),
    ("master-ai", "04 - Neural Networks/Foundations/02 - Activation Functions.md", r"^### ReLU \(Rectified Linear Unit\)", "relu heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/01. Fundamentals of Neural Networks.md", r"^### 2\. ReLU \(Rectified Linear Unit\)", "fundamentals relu heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md", r"Kaiming \(He\) Normal.*ReLU activations", "kaiming relu table row"),
    # --- covers: tokens per parameter family ---
    ("master-ai", "26 - Papers/2024-2026/42 - Scaling Laws (Kaplan and Chinchilla).md", r"optimal ratio is ~20 tokens per parameter", "chinchilla 20 tokens ratio"),
    ("master-ai", "11 - Training/Pretraining/01 - Pretraining Objectives and Scaling Laws.md", r"^### Chinchilla \(Hoffmann et al\., 2022\) — The Corrective", "chinchilla corrective heading"),
    ("master-ai", "11 - Training/Pretraining/01 - Pretraining Objectives and Scaling Laws.md", r"compute-optimal training uses ~20 tokens per parameter", "pretraining 20 tokens"),
    ("master-ai", "11 - Training/Data/03 - Data Pipelines and Deduplication.md", r"you need ~20 tokens per parameter", "data pipeline 20 tokens"),
    # --- covers: utf-8 family ---
    ("master-ai", "05 - NLP Fundamentals/Tokenization/02 - BPE.md", r"^## Byte-Level BPE", "byte-level bpe heading"),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/04 - SentencePiece.md", r"decompose it into UTF-8 bytes", "sentencepiece byte fallback"),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"multi-byte UTF-8 sequences", "non-english tax utf8"),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"BPE merges span multi-byte UTF-8 boundaries", "streaming utf8 boundaries"),
    # --- covers: fine-tuning chapter family ---
    ("master-ai", "12 - Fine-Tuning/MOC.md", r"^# 12", "fine-tuning MOC title"),
    ("master-ai", "12 - Fine-Tuning/PEFT/01 - LoRA.md", r"^# LoRA \(Low-Rank Adaptation\)", "lora note title"),
    ("master-ai", "01 - AI Foundations/04 - The Modern AI Stack.md", r"\[\[12 - Fine-Tuning/MOC\|12 Fine-Tuning\]\]", "modern stack fine-tuning link"),
    # --- covers: DPO / preference pairs family ---
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"Direct Preference Optimization \(Rafailov et al\., 2023\) simplifies RLHF", "dpo tldr definition"),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"trained on preference pairs.*Bradley-Terry", "preference pairs bradley-terry"),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"binary classification loss on preference pairs", "dpo2023 binary classification"),
    ("master-ai", "01 - AI Foundations/04 - The Modern AI Stack.md", r"instruction pairs, preference pairs, domain da", "modern stack preference pairs"),
    ("master-ai", "12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md", r"supervised learning on preference pairs", "rlhf ppo preference pairs"),
    # --- covers: previous-token family ---
    ("master-ai", "06 - Attention Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md", r"Previous-token heads.*always attend to position", "previous-token heads definition"),
    ("master-ai", "08 - LLMs/Capabilities/04 - In-Context Learning.md", r"Previous-token head.*at position \$t\$", "icl previous-token head"),
    ("master-ai", "14 - Interpretability/Mechanistic/01 - Mechanistic Interpretability.md", r"previous-token head writes", "mech interp previous-token"),
    # --- covers: RAG family ---
    ("master-ai", "17 - RAG/Ingestion and Retrieval/01 - RAG Pipeline Overview.md", r"A RAG \(Retrieval-Augmented Generation\) pipeline retrieves", "rag pipeline definition"),
    ("master-ai", "08 - LLMs/Limitations/05 - Hallucination.md", r"^### Retrieval-Augmented Generation \(RAG\)", "hallucination rag heading"),
    ("master-ai", "26 - Papers/Agents and RAG/35 - RAG 2020.md", r"retrieve relevant context, condition generation on it", "rag2020 retrieve condition"),
    # --- covers: running stats family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"running_mean and running_var saved during training", "bn running mean var"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"EMA momentum for running stats update", "bn ema momentum"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"running statistics are a better estimate of the population", "running stats better estimate"),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/03. The Transformer Encoder Block.md", r"inference \(running stats\)", "layernorm running stats"),
    # --- covers: source sentence family ---
    ("master-ai", "04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md", r"entire source sentence must pass through", "seq2seq source sentence bottleneck"),
    ("master-ai", "04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md", r"reverse the source sentence", "sutskever reversal trick"),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"reads the source sentence word by word", "origins encoder reads source"),
    ("master-ai", "26 - Papers/Attention Origins/01 - Bahdanau Attention 2014.md", r"compressing the entire source sentence", "bahdanau paper source sentence"),
    # --- covers: stride-2 family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"Stride-2 convolutions as an alternative to pooling", "stride-2 alternative to pooling"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/07. Strides - Skipping Pixels and Downsampling.md", r"^# 2\.3 Strides: Skipping Pixels and Downsampling", "strides note title"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/02. The Mathematics of Receptive Fields and 1x1 Convolutions.md", r"because of the stride-2 convolution", "receptive field stride-2"),
    # --- covers: unnormalized / logits family ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"raw logits \(unnormalized scores\)", "softmax unnormalized scores"),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"Logits \| `\(B, N, V\)`", "logits shape table"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"Raw unnormalized scores from the model", "raw unnormalized scores comment"),
    # --- covers: value function family ---
    ("master-ai", "03 - Machine Learning/Reinforcement Learning/09 - Policy Gradients and Actor Critic.md", r"with a value function \(\"critic\"\)", "actor critic value function"),
    ("master-ai", "03 - Machine Learning/Reinforcement Learning/07 - MDPs and Bellman Equations.md", r"value function \(\"critic\"\)", "mdp actor critic"),
    ("master-ai", "03 - Machine Learning/Reinforcement Learning/10 - PPO Deep Treatment.md", r"Value function loss", "ppo value function loss"),
    # --- covers: additive attention family ---
    ("master-ai", "06 - Attention Mechanisms/Origins/02 - Bahdanau Attention.md", r"This is called \*\*additive attention\*\* because", "bahdanau additive attention definition"),
    ("master-ai", "06 - Attention Mechanisms/Origins/03 - Luong Attention.md", r"simplified Bahdanau's additive attention into \*\*multiplicative\*\*", "luong simplified additive"),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"Used \*\*additive attention\*\*", "origins additive attention"),
    # --- covers: output tensor family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"produces a 3D output tensor", "front-end 3d output tensor"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"Output Tensor.*\[Batch", "output tensor shape listing"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/02. Core Operators and Geometry - Summary.md", r"^### Final Output Tensor", "final output tensor heading"),
    # --- covers: chapter 07 family ---
    ("ai-course", "07 - Sequence Models and RNNs/00. Chapter Overview.md", r"^# 00 - Sequence Models and RNNs", "chapter 07 overview title"),
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/01. The Bottleneck Problem - Why One Vector Is Not Enough.md", r"most important note in Chapter 07", "most important note chapter 07"),
    ("ai-course", "07 - Sequence Models and RNNs/07.1 - Motivation and Recurrence/01. Why Sequence Models - The Limits of Feedforward Networks.md", r"^# 01\. Why Sequence Models", "why sequence models title"),
    # --- rejects: sso / academic taxonomy / others citation checks ---
    ("master-ai", "16 - Multi-Agent Systems/Enterprise/04 - Enterprise Multi-Agent Architectures.md", r"Integrates with enterprise SSO \(Okta, Azure AD, etc\.\)", "enterprise sso integration"),
    ("master-ai", "16 - Multi-Agent Systems/Enterprise/04 - Enterprise Multi-Agent Architectures.md", r"accepts SSO tokens and resolves them to identity", "orchestrator sso tokens"),
    ("master-ai", "19 - MCP/Integration/04 - MCP Enterprise Integration.md", r"OAuth 2\.0, SSO integration", "mcp gateway sso"),
    ("master-ai", "19 - MCP/Integration/04 - MCP Enterprise Integration.md", r"Integrates with enterprise SSO", "mcp sso integration"),
    ("ai-course", "README.md", r"Academic DL", "academic dl readme"),
    ("ai-course", "README.md", r"Academic ML", "academic ml readme"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"RandomRotation\(degrees=15\)", "rotation degrees 15"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"cameras may have po", "surveillance cameras"),
    ("ai-course", "02 - Python and Data Tooling/02.3 - Essential Python Libraries/01. NumPy - Numerical Computation and Arrays.md", r"10x to 100x faster", "numpy 100x faster"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/02. Loss Functions and Cost Optimization.md", r"100x larger than expected", "outlier 100x larger"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"weights='DEFAULT'", "default weights string"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"self\.bn1 = nn\.BatchNorm2d", "bn1 code identifier"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"self\.bn2 = nn\.BatchNorm2d", "bn2 code identifier"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/05. Normalization, Regularization and Augmentation - Summary.md", r"\\text\{gen\}", "latex gen subscript"),
    ("master-ai", "20 - AI Infrastructure/Compute/04 - GPU Infrastructure and Sizing.md", r"Hopper Gen \| Ampere Gen", "gpu gen columns"),
    ("ai-course", "02 - Python and Data Tooling/02.1 - Python Environment Setup/04. Virtual Environments and Package Management.md", r"install Python globally", "globally install python"),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"Lesson from this Exercise", "knn lesson callout"),
    ("ai-course", "02 - Python and Data Tooling/02.1 - Python Environment Setup/02. Installation and Distributions.md", r"Add Python to PATH", "command path install"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/01. Mathematical Notation (ML Course).md", r"Sigma \(Summation\)", "sigma summation command"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"eval uses running stats", "bn table running stats"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"import torch\.nn as nn", "import torch nn"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"transforms\.RandomRotation\(degrees=15\)", "checklist rotation degrees"),
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q19 - Transfer Learning and Fine-Tuning.md", r"Final performance with limited data", "limited data quiz"),
    ("ai-course", "10 - Generative Models/10.3 - GANs/03. Wasserstein GANs and Modern Variants.md", r"gradient penalty.*critic", "wgan critic gradient penalty"),
    ("master-ai", "08 - LLMs/Limitations/05 - Hallucination.md", r"Hallucinated tool arguments", "hallucinated tool arguments"),
]


def main() -> int:
    ok = 0
    fail = 0
    for vault, rel, pattern, label in CHECKS:
        path = VAULTS[vault] / rel
        if not path.exists():
            print(f"MISSING FILE [{label}] {vault}/{rel}")
            fail += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        found = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                found.append(i)
        if found:
            ok += 1
            print(f"OK   [{label}] {vault}/{rel}:{found[0]}"
                  + (f" (+{len(found)-1} more)" if len(found) > 1 else ""))
        else:
            fail += 1
            print(f"FAIL [{label}] {vault}/{rel} :: /{pattern}/")
    print(f"\n{ok} ok, {fail} failed of {len(CHECKS)} checks")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
