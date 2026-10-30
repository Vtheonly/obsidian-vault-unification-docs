#!/usr/bin/env python3
"""Targeted corpus verification for batch-6 cover/borderline citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).
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
    ("ai-course", "02 - Python and Data Tooling/02.3 - Essential Python Libraries/01. NumPy - Numerical Computation and Arrays.md", r"randn\(3, 2\)", "randn std-normal comment"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"random values \(randn\)", "checklist randn heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"Using randn", "exercises randn heading"),
    ("master-ai", "27 - Projects/Capstones/13 - Build a RAG Evaluation Harness.md", r"[Ee]val set", "RAG eval harness"),
    ("master-ai", "17 - RAG/Ingestion and Retrieval/01 - RAG Pipeline Overview.md", r"Building an Evaluation Set", "RAG eval set section"),
    ("master-ai", "21 - LLMOps and MLOps/Pipelines/01 - LLMOps vs MLOps.md", r"eval set management", "LLMOps eval set"),
    ("master-ai", "09 - Foundation Models/Embedding Models/06 - Embedding Model Training.md", r"eval set for your domain", "embedding eval set"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"#{2,3} \d\. (Validation|Test) Set", "val/test split sections"),
    ("ai-course", "02 - Python and Data Tooling/02.4 - Data Cleaning and Preprocessing/05. Categorical Encoding and Text Normalization.md", r"Using sklearn", "sklearn heading"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"Scikit-Learn Implementation", "scikit summary heading"),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"scikit-learn for metric computation", "sklearn eval workflow"),
    ("ai-course", "03 - Machine Learning/03.5 - K-Means Clustering/01. K-Means Clustering.md", r"n_init=10", "kmeans n_init"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/07. Probability and Statistics for ML.md", r"described by a probability distribution", "random variable def"),
    ("master-ai", "08 - LLMs/Sampling/03 - Sampling Strategies.md", r"The Probability Distribution View", "sampling distribution heading"),
    ("master-ai", "02 - Mathematics/Probability/07 - Probability Essentials.md", r"language model is a probability distribution", "LM as distribution"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"into a probability distribution over", "softmax distribution"),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"Diagonal extraction", "diagonal extraction section"),
    ("master-ai", "02 - Mathematics/Linear Algebra/05 - Matrix Decomposition.md", r"diagonal matrix of eigenvalues", "Lambda diagonal"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"sum of diagonal", "trace diagonal"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"\\Sigma \\in \\mathbb\{R\}", "SVD Sigma diagonal"),
    ("ai-course", "07 - Sequence Models and RNNs/07.1 - Motivation and Recurrence/03. Backpropagation Through Time (BPTT).md", r"\\mathrm\{diag\}\(1 - h_t\^2\)", "BPTT diag"),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"diagonal preconditioner", "Adam diagonal preconditioner"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"spatially adjacent", "dropout2d adjacent"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"Where Are the Weights Cached", "weights cached callout"),
    ("master-ai", "08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md", r"KV Cache Mechanics", "KV cache note"),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"majority vote", "KNN majority vote"),
    ("master-ai", "26 - Papers/Agents and RAG/38 - Self-Consistency 2022.md", r"Majority vote", "self-consistency majority"),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"eigenvector of a square matrix", "square matrix eigendef"),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.1 The Mechanics of Spatial Filtering.md", r"small, square matrix", "kernel square"),
    ("ai-course", "08 - Attention and Transformers/08.1 - The Attention Mechanism/03. Scaled Dot-Product Attention - Why the Square Root.md", r"Why the Square Root", "sqrt dedicated note"),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/03. Data Structures - Lists, Tuples, and Sets.md", r"collection of \*\*unique\*\* elements|unique elements", "set unique def"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/05. Evolution and History of Deep Learning.md", r"1\.4 million images", "imagenet 1.4M"),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/03. Regression Metrics - MAE, MSE, RMSE, R2, MAPE.md", r"off by 10x", "MSE 10x rationale"),
    ("ai-course", "02 - Python and Data Tooling/02.3 - Essential Python Libraries/01. NumPy - Numerical Computation and Arrays.md", r"10x to 100x faster", "numpy 10x"),
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/02. The Information Bottleneck and Latent Space.md", r"compressed representation", "latent compressed"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"network's", "network possessive"),
]


def main() -> int:
    for vault, rel, pat, label in CHECKS:
        root = VAULTS[vault]
        p = root / rel
        if not p.exists():
            print(f"MISSING FILE: {vault}/{rel}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        hits = []
        rx = re.compile(pat)
        for i, ln in enumerate(lines, 1):
            if rx.search(ln):
                hits.append((i, ln.strip()[:110]))
        if hits:
            for i, ln in hits[:3]:
                print(f"OK  {label:34s} {vault}/{rel}:{i} :: {ln}")
        else:
            print(f"NOHIT {label:34s} {vault}/{rel} :: pattern={pat!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
