#!/usr/bin/env python3
"""Targeted corpus verification for batch-7 cover/gap/borderline citations.

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
    # --- covers ---
    ("master-ai", "06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md", r"^# 14 - GQA", "gqa-mqa-mla title"),
    ("master-ai", "06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md", r"^## MQA", "mqa heading"),
    ("master-ai", "06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md", r"^## GQA", "gqa heading"),
    ("master-ai", "06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md", r"^## MLA", "mla heading"),
    ("master-ai", "06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md", r"^## Worked Example", "gqa worked example"),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"^# DPO Derivation", "dpo title"),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"^## The Derivation", "dpo derivation heading"),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"^### Step 5", "dpo step 5"),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"^## Variants", "dpo variants"),
    ("master-ai", "11 - Training/Optimization/04 - Mixed Precision Training.md", r"BF16 \(Brain Float 16", "bf16 heading"),
    ("master-ai", "11 - Training/Optimization/04 - Mixed Precision Training.md", r"FP16 \(IEEE 754", "fp16 heading"),
    ("master-ai", "11 - Training/Optimization/04 - Mixed Precision Training.md", r"^# 04", "mixed precision title"),
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"DeepSeek-R1 \(Jan 2025\)", "r1 reasoning models"),
    ("master-ai", "10 - Model Architecture Research/Open Source/01 - DeepSeek Architecture.md", r"DeepSeek-R1: Reasoning on V3", "r1 deepseek arch"),
    ("master-ai", "24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md", r"DeepSeek-R1 \(January 2025\)", "r1 ttc scaling"),
    ("master-ai", "17 - RAG/Ingestion and Retrieval/01 - RAG Pipeline Overview.md", r"^# RAG Pipeline Overview", "rag pipeline overview title"),
    ("master-ai", "17 - RAG/Ingestion and Retrieval/01 - RAG Pipeline Overview.md", r"\*\*Ingest\*\*", "rag ingest step"),
    ("master-ai", "27 - Projects/Capstones/14 - Build a Multimodal RAG Pipeline.md", r"Step 4: Ingestion Pipeline", "multimodal ingestion step"),
    ("master-ai", "27 - Projects/Capstones/21 - Build a Knowledge-Graph Construction Pipeline.md", r"Step 1: Document Ingestion", "kg ingestion step"),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule and Convergence.md", r"^# 6\. Gradient Descent", "gd update rule title"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"^### The Update Rule", "ann update rule"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"Final Weight Update", "ann final weight update"),
    ("master-ai", "02 - Mathematics/Linear Algebra/04 - Matrix Multiplication.md", r"LoRA approximates a weight update", "lora weight update"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"Low-Level Features \(Early Layers\)", "low-level features heading"),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"Hierarchical features", "hierarchical features heading"),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/03. Data Structures - Lists, Tuples, and Sets.md", r"^[#]+ .*[Tt]uple", "tuples note title"),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/03. Data Structures - Lists, Tuples, and Sets.md", r"\*\*Definition:\*\* Ordered, \*\*immutable\*\* collection", "tuple definition"),
    ("master-ai", "02 - Mathematics/Linear Algebra/01 - Vectors.md", r"ordered tuple", "vector as ordered tuple"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"^## Pipeline Overview", "training pipeline overview"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/07. Scaling, Pipeline and Interpretability - Summary.md", r"Pipeline Overview", "scaling pipeline overview"),
    ("master-ai", "18 - Memory Systems/Vector Memory/04 - Vector Memory Backends.md", r"^# 04", "vector memory backends title"),
    ("master-ai", "16 - Multi-Agent Systems/Enterprise/04 - Enterprise Multi-Agent Architectures.md", r"^### Audit Log", "enterprise audit log"),
    ("master-ai", "19 - MCP/Security/03 - MCP Security.md", r"Audit [Ll]og", "mcp security audit log"),
    ("master-ai", "19 - MCP/Integration/04 - MCP Enterprise Integration.md", r"^### Audit Log", "mcp enterprise audit log"),
    # --- confirmed gap: async def ---
    ("master-ai", "27 - Projects/Capstones/08 - Build an MCP Server.md", r"async def main", "mcp server async main"),
    ("master-ai", "27 - Projects/Capstones/08 - Build an MCP Server.md", r"MCP handlers are async", "mcp async handlers warning"),
    ("master-ai", "27 - Projects/Capstones/08 - Build an MCP Server.md", r"block the event loop", "event loop blocking warning"),
    ("master-ai", "27 - Projects/Capstones/08 - Build an MCP Server.md", r"asyncio\.to_thread", "asyncio to_thread"),
    ("master-ai", "19 - MCP/Components/02 - MCP Components.md", r"don't block event loop", "mcp components async io"),
    ("master-ai", "16 - Multi-Agent Systems/Enterprise/04 - Enterprise Multi-Agent Architectures.md", r"async patterns", "enterprise async patterns"),
    ("master-ai", "25 - Frameworks and Tools/Agent Frameworks/01 - Framework Selection Guide.md", r"async def search", "framework guide async tool"),
    ("master-ai", "18 - Memory Systems/Vector Memory/04 - Vector Memory Backends.md", r"async def search_memories", "vector memory async def"),
    # --- reject in-situ coverage citations ---
    ("master-ai", "02 - Mathematics/Linear Algebra/02 - Dot Product.md", r"is the angle between", "dot product theta angle"),
    ("master-ai", "02 - Mathematics/Linear Algebra/03 - Cosine Similarity.md", r"measures the \*\*angle\*\*", "cosine similarity angle"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"Validation Phase", "validation phase"),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"Train vs Val Loss", "train vs val loss"),
    ("master-ai", "04 - Neural Networks/Training/06 - Backpropagation.md", r"upstream gradient", "backprop upstream gradient"),
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. The Encoder-Decoder Pattern - Conditional Generation.md", r"one token at a time", "encoder-decoder one token"),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"^# Tokenization Overview", "tokenization overview title"),
    ("ai-course", "07 - Sequence Models and RNNs/07.2 - LSTM and GRU/02. GRU - Simplifying the LSTM.md", r"Merges the forget and input gates", "gru merges gates"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"doubling pattern is not arbitrary", "channel doubling rationale"),
    ("ai-course", "03 - Machine Learning/03.8 - Dimensionality Reduction/01. Principal Component Analysis (PCA).md", r"Center the data", "pca center step"),
    ("master-ai", "19 - MCP/Architecture/01 - MCP Overview.md", r"Read-only data sources", "mcp read-only resources"),
    ("ai-course", "07 - Sequence Models and RNNs/07.2 - LSTM and GRU/01. LSTM - Gates as Learned Traffic Controllers.md", r"Weights per step", "lstm weights per step"),
    ("master-ai", "21 - LLMOps and MLOps/Pipelines/01 - LLMOps vs MLOps.md", r"Per-request cost tracking", "per-request cost tracking"),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"chapter 10 model arch notes", "10 model arch prose"),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"Understanding the Difficulty of Training", "difficulty paper title"),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"grad_output is a tuple", "tuple in code comment"),
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
                print(f"OK  {label:34s} {vault}/{rel}:{i} :: {ln}")
            ok += 1
        else:
            print(f"NOHIT {label:34s} {vault}/{rel} :: pattern={pat!r}")
            nohit += 1
    print(f"\n{ok} OK, {nohit} NOHIT/MISSING of {len(CHECKS)} checks")
    return 0 if nohit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
