#!/usr/bin/env python3
"""Targeted corpus verification for batch-10 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list (batch-10 improvement), so a Python comment inside
a code fence can no longer pass as a heading citation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402

VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

# (vault, path, pattern, note, require_heading)
# require_heading=True additionally asserts the matched line is a REAL
# heading per the authoritative fence-aware mdextract extraction.
CHECKS = [
    # --- covers: dpo 2023 family ---
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"^# DPO Derivation", "dpo derivation note title", True),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"^# 09", "dpo 2023 paper note title", True),
    ("master-ai", "02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md", r"^#+ DPO's implicit KL", "dpo implicit kl heading", True),
    # --- covers: final classification / classification head family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/04. The Fully Connected Layer and Flattening.md", r"Fully Connected Layer \(Classification Head\)", "fc layer classification head title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"^#+ Replacing the Classification Head", "replacing classification head heading", True),
    ("master-ai", "26 - Papers/Transformers/21 - Vision Transformer ViT 2020.md", r"^#+ Classification Head", "vit classification head heading", True),
    ("master-ai", "03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md", r"A classification head is softmax regression", "classification head is softmax regression", False),
    # --- covers: fpr family ---
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"^#+ Type I Error \(False Positive Rate\)", "type i error fpr heading", True),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"\*\*False Positive Rate \(FPR\)\*\*\. It measures the fraction of actual negatives", "fpr definition sentence", False),
    # --- covers: hybrid models family ---
    ("master-ai", "26 - Papers/2024-2026/30 - Kimi Linear 2025.md", r"hybrid architecture that combines linear attention", "kimi linear hybrid definition", False),
    ("master-ai", "26 - Papers/2024-2026/41 - Jamba 2024.md", r"hybrid architecture", "jamba hybrid mention", False),
    ("master-ai", "10 - Model Architecture Research/Closed Source/11 - Kimi K3 Architecture.md", r"Linear-time hybrid architecture", "kimi k3 hybrid", False),
    ("master-ai", "24 - Research Frontiers/State Space Models/01 - SSMs Mamba and Frontiers.md", r"^# 01 - Research Frontiers: SSMs, Mamba", "ssms mamba frontiers title", True),
    ("master-ai", "06 - Attention Mechanisms/Self-Attention/04 - Self-Attention.md", r"trend is toward \*\*hybrid architectures\*\*", "self-attention hybrid trend", False),
    # --- covers: imagenet normalization family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"ImageNet Normalization Is Non-Negotiable", "imagenet normalization callout", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"mean = \[0\.485, 0\.456, 0\.406\]", "imagenet mean values", False),
    # --- covers: long-running agents family ---
    ("master-ai", "15 - AI Agents/Autonomy/08 - Autonomous Agent Lifecycles.md", r"^#+ Long-Running Agent Patterns", "long-running agent patterns heading", True),
    ("master-ai", "15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application.md", r"Autonomous Agent \(Long-Running, Self-Directed\)", "autonomous agent long-running heading", True),
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"long-running agents that operate without", "ai-vs-ml autonomous def", False),
    # --- covers: pure vector search family ---
    ("master-ai", "17 - RAG/Ingestion and Retrieval/02 - Chunking Hybrid Search Reranking.md", r"^# 02 - Chunking, Hybrid Search, and Reranking", "hybrid search note title", True),
    ("master-ai", "17 - RAG/Ingestion and Retrieval/02 - Chunking Hybrid Search Reranking.md", r"^#+ Hybrid Search \(BM25 \+ Vector\)", "hybrid search bm25 vector heading", True),
    ("master-ai", "05 - NLP Fundamentals/Pre-Transformer NLP/10 - BM25.md", r"^#+ BM25 vs Vector Search", "bm25 vs vector search heading", True),
    ("master-ai", "05 - NLP Fundamentals/Pre-Transformer NLP/10 - BM25.md", r"Pure vector search misses exact-match queries", "pure vector search limitation", False),
    # --- covers: running mean family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Training vs\. Evaluation Mode", "bn train vs eval heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"saved running mean", "saved running mean", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"exponential moving average", "bn ema explanation", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"running statistics are NOT controlled by", "transfer learning running stats", False),
    # --- covers: unembedding family ---
    ("master-ai", "07 - Transformers/Components/06 - Embedding Layer.md", r"^#+ Tied vs Untied Embeddings", "tied vs untied heading", True),
    ("master-ai", "07 - Transformers/Components/06 - Embedding Layer.md", r"The output layer \(un-embedding\) is also a", "un-embedding definition sentence", False),
    ("master-ai", "04 - Neural Networks/Training/07 - Initialization Schemes.md", r"^#+ Output projection", "output projection heading", True),
    ("master-ai", "04 - Neural Networks/Training/07 - Initialization Schemes.md", r"Final unembedding: often initialized to zeros", "final unembedding init rule", False),
    ("master-ai", "14 - Interpretability/Mechanistic/02 - Logit Lens and Tuned Lens.md", r"compatible with the unembedding matrix", "logit lens unembedding use", False),
    ("master-ai", "26 - Papers/Alignment/07 - InstructGPT 2022.md", r"unembedding head replaced by a scalar output", "instructgpt unembedding head", False),
    # --- covers: unlabeled family ---
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/02. Types of Learning.md", r"trained on an \*\*unlabeled dataset\*\*", "unlabeled dataset definition", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"trained on an \*\*unlabeled dataset\*\*", "summary unlabeled definition", False),
    # --- covers: 20 tokens per family ---
    ("master-ai", "26 - Papers/2024-2026/42 - Scaling Laws (Kaplan and Chinchilla).md", r"optimal ratio is ~20 tokens per parameter", "chinchilla 20 tokens ratio", False),
    ("master-ai", "11 - Training/Pretraining/01 - Pretraining Objectives and Scaling Laws.md", r"compute-optimal training uses ~20 tokens per parameter", "pretraining 20 tokens", False),
    ("master-ai", "26 - Papers/2024-2026/42 - Scaling Laws (Kaplan and Chinchilla).md", r"^#+ The Compute-Optimal Allocation", "compute optimal allocation heading", True),
    # --- covers: adaptiveavgpool2d family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"Global Average Pooling", "gap note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"Global Average Pooling using nn\.AdaptiveAvgPool2d", "gap adaptiveavgpool2d usage", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/03. Activation and Pooling Layers.md", r"gap = nn\.AdaptiveAvgPool2d\(1\)", "activation pooling gap code", False),
    # --- covers: base models / chat models family ---
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md", r"^#+ For base models", "for base models heading", True),
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md", r"^#+ For instruction-tuned / chat models", "for chat models heading", True),
    ("master-ai", "01 - AI Foundations/03 - A Brief History of AI.md", r"Pretrained base models aren't useful chatbots", "base models not chatbots", False),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"makes a base model into a chat model", "base into chat model", False),
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"An instruction-tuned model responds to instructions", "instruction tuned contrast", False),
    # --- covers: channel dimensions / color channels family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/03. The Bridge - From Basic Convolution to Learned Weights.md", r"^#+ The Dimension of Depth \(Channels\)", "dimension of depth heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"^#+ Understanding Feature Maps as Channels", "feature maps as channels heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"^#+ Generating Multiple Output Channels", "multiple output channels heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"3rd dimension: \*\*Color Channels\*\*", "color channels definition", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"red, green, and blue color channels", "rgb color channels", False),
    # --- covers: cpu' family (device placement) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"^#+ Mistake 4: Data on Wrong Device", "data wrong device heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"PyTorch requires all tensors involved in an operation to be on the same device", "device explanation", False),
    ("master-ai", "25 - Frameworks and Tools/Serving/08 - Ollama and llama.cpp.md", r"^#+ CPU vs\. GPU", "cpu vs gpu heading", True),
    # --- covers: final convolutional family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/07. Scaling, Pipeline and Interpretability - Summary.md", r"^#+ Step 2: Target the Last Convolutional Layer", "gradcam last conv layer heading (summary)", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"final convolutional layer of a CNN produces feature maps that retain spatial information", "gradcam final conv layer in-situ", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"final convolutional layer produces .?C.? feature maps", "nin final conv layer", False),
    # --- covers: non-verifiable family ---
    ("master-ai", "26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md", r"^#+ Approach B: Verifiable Rewards \(RLVR\)", "rlvr approach heading", True),
    ("master-ai", "26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md", r"Extending to non-verifiable domains is an open problem", "non-verifiable open problem", False),
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"^#+ 1\. Verifiable Rewards \(the key innovation\)", "verifiable rewards heading", True),
    # --- covers: spatial feature family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"learn the spatial feature detectors", "vgg16 spatial feature detectors", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"actual spatial feature extraction happens", "resnet spatial feature extraction", False),
    # --- covers: 56-layer / higher training error family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"^# 11\. The Degradation Problem", "degradation note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"56-layer network is strictly worse at fitting the training data", "56-layer strictly worse", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"56-layer network had \*\*higher training error\*\*", "56-layer higher training error", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"^#+ 5\. ResNet \(2015\): Solving the Degradation Problem", "resnet solving degradation heading", True),
    # --- covers: best validation family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"^#+ 2\.3 Epochs and Early Stopping", "epochs early stopping heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"checkpoint with the best validation loss", "best validation loss checkpoint", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"^#+ Early Stopping", "dropout note early stopping heading", True),
    ("master-ai", "03 - Machine Learning/Generalization/06 - Regularization Techniques.md", r"^#+ Early Stopping", "regularization early stopping heading", True),
    # --- covers: mini moe family ---
    ("master-ai", "27 - Projects/Implementations/04 - Build a Mini MoE.md", r"^# 04 — Build a Mini MoE", "mini moe project title", True),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"^#+ Mixture of Experts \(MoE\)", "moe heading perceptrons", True),
    # --- covers: one bias family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"still has only one bias value", "one bias value", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"add one bias → apply ReLU", "add one bias atomic op", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"One bias per filter", "one bias per filter", False),
    # --- covers: snell family ---
    ("master-ai", "24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md", r"^# 06 — Test-Time Compute Scaling", "test-time compute note title", True),
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"^#+ Test-Time Compute Scaling Law", "ttc scaling law heading", True),
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"Snell et al\. \(2024\) showed that test-time compute scales", "snell showed ttc scales", False),
    ("master-ai", "24 - Research Frontiers/08 - 2026 Research Frontier Update.md", r"Snell et al\. \(2024\) log-scaling law is now empirically validated", "snell log-scaling validated", False),
    # --- covers: alignment method family ---
    ("master-ai", "10 - Model Architecture Research/Closed Source/08 - Claude Architecture.md", r"^#+ Constitutional AI as the Alignment Method", "claude constitutional heading", True),
    ("master-ai", "26 - Papers/Alignment/31 - Constitutional AI 2022.md", r"CAI is the alignment method used by Anthropic", "cai alignment method", False),
    ("master-ai", "03 - Machine Learning/Reinforcement Learning/10 - PPO Deep Treatment.md", r"PPO is the algorithm behind RLHF.*the alignment method that produced ChatGPT", "ppo alignment method", False),
    # --- rejects: citation verification ---
    ("master-ai", "00 - Vault Management/Research Queue.md", r"Per ADR-006, every claim about a closed-source model must be labeled", "adr-006 vault-management label", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"replaced PaliGemma with Qwen2-VL", "paligemma interchangeable vlm", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"the specific VLM is interchangeable", "colpali vlm interchangeable", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"^#+ 3\.2 Block 1: Two Conv3-64 \+ MaxPool", "vgg conv3-64 label heading", True),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"Peak LR: 3e-4", "3e-4 in-situ value", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/07. Probability and Statistics for ML.md", r"no triangle inequality", "triangle inequality in-situ (KL)", False),
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"For 0-1 loss, the formula is non-monotonic", "0-1 loss in-situ", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"gradient would have been zeroed out", "zeroed in-situ", False),
    ("master-ai", "00 - Vault Management/Master Roadmap.md", r"- \[~\] Long-running agents", "roadmap long-running agents item", False),
]


def main() -> int:
    ok = 0
    fail = 0
    for vault, rel, pat, note, require_heading in CHECKS:
        path = VAULTS[vault] / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            print(f"FAIL (missing file) {vault}/{rel} :: {note}")
            fail += 1
            continue
        rx = re.compile(pat, re.MULTILINE)
        m = rx.search(text)
        if not m:
            print(f"FAIL (no match)    {vault}/{rel} :: {note} :: /{pat}/")
            fail += 1
            continue
        line_no = text[: m.start()].count("\n") + 1
        matched_line = text[m.start() : text.find("\n", m.start())].strip()
        if require_heading:
            struct = extract_structure_text(text)
            if not any(h["line"] == line_no for h in struct["headings"]):
                print(
                    f"FAIL (not real heading) {vault}/{rel}:{line_no} :: {note} "
                    f":: {matched_line[:70]}"
                )
                fail += 1
                continue
        print(f"OK   {vault}/{rel}:{line_no} :: {note} :: {matched_line[:80]}")
        ok += 1
    print(f"\n{ok} OK, {fail} FAIL of {len(CHECKS)} checks")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
