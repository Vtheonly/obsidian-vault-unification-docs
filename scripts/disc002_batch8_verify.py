#!/usr/bin/env python3
"""Targeted corpus verification for batch-8 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware where it matters: several probe 'heading' hits were Python
comments inside code blocks (e.g. '# From CSV (Most common)'); this script
matches content lines, and every citation used in a decision rationale must
appear here with a real line number.
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
    # (vault, path, pattern, label)
    # --- covers: MCP / chapters / dedicated notes ---
    ("master-ai", "19 - MCP/Architecture/01 - MCP Overview.md", r"^# 01 - MCP", "mcp overview title"),
    ("master-ai", "13 - Inference/MOC.md", r"^# 13", "13 inference MOC title"),
    ("master-ai", "10 - Model Architecture Research/MOC.md", r"^# 10", "10 model architecture MOC title"),
    ("master-ai", "03 - Machine Learning/Reinforcement Learning/10 - PPO Deep Treatment.md", r"^# 10 - PPO Deep Treatment", "ppo deep treatment title"),
    ("master-ai", "15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application.md", r"^# Agent vs Workflow vs LLM Application", "agent vs workflow note title"),
    # --- covers: reasoning family ---
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"^## What Makes a Reasoning Model", "what makes a reasoning model"),
    ("master-ai", "24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md", r"^## The Reasoning Model Wave", "reasoning model wave"),
    # --- covers: test-data family ---
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"^## 3\. Test Set", "test set heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"^### Run on Test Set", "run on test set heading"),
    ("ai-course", "02 - Python and Data Tooling/02.4 - Data Cleaning and Preprocessing/04. Feature Scaling and Normalization.md", r"fit the scaler on the full dataset", "test-data leakage warning"),
    # --- covers: BERT / embedder family ---
    ("master-ai", "07 - Transformers/Encoder Models/07 - BERT.md", r"^## BERT Family", "bert family heading"),
    ("master-ai", "05 - NLP Fundamentals/Embeddings/06 - Contextual Embeddings ELMo to BERT.md", r"contextual embeddings was the conceptual leap", "elmo to bert leap"),
    ("master-ai", "09 - Foundation Models/Embedding Models/02 - Embedding Models for Retrieval.md", r"^## What Makes a", "retrieval embedding model heading"),
    ("master-ai", "09 - Foundation Models/Embedding Models/06 - Embedding Model Training.md", r"^# 06", "embedding model training title"),
    # --- covers: computation graph family ---
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"^## Backpropagation = Chain Rule Applied to a Computation Graph", "computation graph calculus heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural Network Architecture and Notation.md", r"^### The Computational Graph", "computational graph heading"),
    ("master-ai", "04 - Neural Networks/Training/06 - Backpropagation.md", r"keeps the computation graph for re-use", "retain graph memory leak"),
    # --- covers: float32 family ---
    ("master-ai", "11 - Training/Optimization/04 - Mixed Precision Training.md", r"^## Master Weights in FP32", "master weights fp32 heading"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"Scales pixel values from \[0, 255\]", "totensor float32 conversion"),
    # --- covers: partial derivative family ---
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"^## Partial Derivatives", "partial derivatives heading"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/04. Partial vs. Ordinary Derivatives.md", r"treat \*\*all other variables", "partial vs ordinary critical rule"),
    # --- covers: typing family ---
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/01. Variables, Operators, and Type Casting.md", r"^## 1\.1 Variables and Dynamic Typing", "dynamic typing heading"),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/01. Variables, Operators, and Type Casting.md", r"Python is \*\*dynamically typed\*\*", "dynamic typing definition"),
    ("master-ai", "25 - Frameworks and Tools/Agent Frameworks/11 - PydanticAI.md", r"leverage Python type hints", "pydanticai type hints"),
    ("master-ai", "25 - Frameworks and Tools/Agent Frameworks/15 - Semantic Kernel.md", r"type hints become the JSON schema", "semantic kernel type hints"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/04. The Perceptron and the Chain Rule.md", r"dynamic typing and interpretation overhead", "perceptron dynamic typing"),
    # --- covers: augmentation / conv / transfer-learning ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"^# 18\. Data Augmentation", "data augmentation note title"),
    ("master-ai", "03 - Machine Learning/Generalization/06 - Regularization Techniques.md", r"^## Data Augmentation", "regularization augmentation heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"^# 3\. The Convolution Operation Deep Dive", "convolution operation title"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/02. Core Operators and Geometry - Summary.md", r"^#### Example A: Standard Conv Layer", "standard conv layer heading"),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"Hierarchical features", "master-ai cnns hierarchical features"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"^## Strategy 1: Feature Extraction", "freeze strategy 1 heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"All layers unfrozen", "full fine-tuning unfrozen"),
    # --- covers: silu family ---
    ("master-ai", "04 - Neural Networks/Foundations/02 - Activation Functions.md", r"^### SwiGLU", "swiglu activation functions heading"),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"SwiGLU \(Swish-Gated", "perceptrons swiglu formula"),
    ("master-ai", "07 - Transformers/Components/05 - Feed-Forward Network Deep.md", r"^### SwiGLU \(Llama", "ffn swiglu heading"),
    # --- covers: papers family ---
    ("master-ai", "26 - Papers/Alignment/07 - InstructGPT 2022.md", r"^# 07", "instructgpt paper title"),
    ("master-ai", "07 - Transformers/Decoder Models/09 - GPT Family Evolution.md", r"^### GPT-3\.5 / InstructGPT", "gpt family instructgpt"),
    # --- covers: channel depth ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"match the exact channel depth", "channel depth rule"),
    # --- covers: draft head family ---
    ("master-ai", "26 - Papers/Efficient Attention/51 - EAGLE-3 2025.md", r"trains the draft head on top of a frozen target model", "eagle3 draft head"),
    ("master-ai", "26 - Papers/Efficient Attention/52 - MTP Multi-Token Prediction.md", r"natural draft head", "mtp draft head"),
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"acceptance/rejection resampling", "spec decoding rejection resampling"),
    # --- covers: output validation family ---
    ("master-ai", "22 - Production AI/Security/01 - LLM Security and Prompt Injection.md", r"^### 2\. Output validation", "llm security output validation"),
    ("master-ai", "19 - MCP/Security/03 - MCP Security.md", r"validate tool call arguments against schemas", "mcp output validation"),
    ("master-ai", "25 - Frameworks and Tools/Agent Frameworks/10 - CrewAI.md", r"^### Output Validation", "crewai output validation"),
    # --- covers: predicted class ---
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/01. Model Evaluation and Metrics.md", r"compares the \*\*Predicted Class\*\*", "predicted class definition"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"Predicted Class\*\* against", "foundations predicted class"),
    # --- covers: bilinear family ---
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.7 Geometric Transformations and Interpolation.md", r"^### Bilinear interpolation", "bilinear heading"),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.7 Geometric Transformations and Interpolation.md", r"^### Bicubic interpolation", "bicubic heading"),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.7 Geometric Transformations and Interpolation.md", r"^### Nearest-neighbor interpolation", "nearest neighbor heading"),
    ("master-ai", "07 - Transformers/Variants/13 - Vision Transformer ViT.md", r"This bicubic interpolation works well", "vit bicubic"),
    # --- reject in-situ coverage citations ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"^# 15\. The Vanishing and Exploding", "vanishing exploding title"),
    ("ai-course", "03 - Machine Learning/03.7 - Tree-Based Models/03. Gradient Boosting and XGBoost.md", r"keeps all samples with large gradients", "goss large gradients"),
    ("master-ai", "06 - Attention Mechanisms/MOC.md", r"^# 06", "attention mechanisms MOC title"),
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/03. From RNNs to Attention - The Historical Bridge.md", r"sequence attends to itself", "self-attends prose"),
    ("ai-course", "02 - Python and Data Tooling/02.4 - Data Cleaning and Preprocessing/04. Feature Scaling and Normalization.md", r"^# ", "feature scaling note title"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^# 16\. Batch Normalization", "batch normalization note title"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule and Convergence.md", r"Why do we subtract", "subtract update rule"),
    ("master-ai", "08 - LLMs/Limitations/05 - Hallucination.md", r"confident wrong answers", "hallucination confident wrong answers"),
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/02. Teacher Forcing and Exposure Bias.md", r"^# ", "teacher forcing exposure bias title"),
    ("ai-course", "02 - Python and Data Tooling/02.3 - Essential Python Libraries/03. DataFrames - Deep Dive and Operations.md", r"read_csv", "dataframes read_csv"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/04. Machine Learning vs Deep Learning.md", r"manually extract", "ml vs dl extract features"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"manual feature engineering", "cnn manual feature engineering"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"2 extra buffers", "optimizer memory table"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"torch\.no_grad", "no_grad treatment"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"right to explanation", "gdpr right to explanation"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/06. Applications of Deep Learning.md", r"Fraud Detection", "fraud detection applications"),
]


def main() -> int:
    ok = 0
    nohit = 0
    for vault, rel, pat, label in CHECKS:
        root = VAULTS[vault]
        p = root / rel
        if not p.exists():
            print(f"MISSING FILE: {vault}/{rel}")
            nohit += 1
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        hits = []
        rx = re.compile(pat, re.MULTILINE)
        for i, ln in enumerate(lines, 1):
            if rx.search(ln):
                hits.append((i, ln.strip()[:110]))
        if hits:
            for i, ln in hits[:3]:
                print(f"OK  {label:38s} {vault}/{rel}:{i} :: {ln}")
            ok += 1
        else:
            print(f"NOHIT {label:38s} {vault}/{rel} :: pattern={pat!r}")
            nohit += 1
    print(f"\n{ok} OK, {nohit} NOHIT/MISSING of {len(CHECKS)} checks")
    return 0 if nohit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
