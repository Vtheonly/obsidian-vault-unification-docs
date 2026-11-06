#!/usr/bin/env python3
"""Targeted corpus verification for batch-11 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list, so a Python comment inside a code fence can no
longer pass as a heading citation.
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
    # --- covers: closed-source models family ---
    ("master-ai", "00 - Vault Management/Research Queue.md", r"^#+ Closed-Source Model Architectures", "closed-source architectures heading", True),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"ADR-006 . Source-labelling convention for closed-source", "adr-006 heading", True),
    ("master-ai", "10 - Model Architecture Research/2026 Frontier Model Synthesis.md", r"^#+ 10 . 2026 Frontier Model Synthesis", "frontier synthesis note title", True),
    ("master-ai", "10 - Model Architecture Research/2026 Frontier Model Synthesis.md", r"Closed-source models are increasingly hard to differentiate", "closed-source hard to differentiate", False),
    ("master-ai", "10 - Model Architecture Research/Closed Source/09 - Gemini Architecture.md", r"most architecturally transparent of the closed-source frontier models", "gemini closed-source def", False),
    # --- covers: contextual embeddings elmo family ---
    ("master-ai", "05 - NLP Fundamentals/Embeddings/06 - Contextual Embeddings ELMo to BERT.md", r"^#+ 06 - Contextual Embeddings: ELMo", "contextual embeddings note title", True),
    ("master-ai", "05 - NLP Fundamentals/Embeddings/05 - Word2Vec GloVe FastText.md", r"^#+ Static vs Contextual Embeddings", "static vs contextual heading", True),
    ("master-ai", "05 - NLP Fundamentals/Embeddings/06 - Contextual Embeddings ELMo to BERT.md", r"^#+ Modern Contextual Embedding Models", "modern contextual heading", True),
    # --- covers: ddpm family (glossary acronym + dedicated chapter) ---
    ("master-ai", "28 - Glossary/Acronyms/Acronyms Index.md", r"\*\*DDPM\*\* . Denoising Diffusion Probabilistic Models", "ddpm glossary expansion", False),
    ("ai-course", "10 - Generative Models/00. Chapter Overview.md", r"^#+ 10\.4 - Diffusion Models", "diffusion chapter heading", True),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/02. The Reverse Process - Learning to Denoise.md", r"key insight from DDPM \(Ho et al\. 2020\)", "ddpm key insight", False),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/01. The Forward Process - Adding Noise.md", r"Linear schedule.*original DDPM", "original ddpm linear schedule", False),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/03. Score-Based and Latent Diffusion.md", r"The original DDPM \(Ho et al\. 2020\) demonstrated", "original ddpm demonstrated", False),
    # --- covers: rejection sampling family ---
    ("master-ai", "26 - Papers/Alignment/31 - Constitutional AI 2022.md", r"^#+ Stage 1: Constitutional Rejection Sampling", "cai rejection sampling heading", True),
    ("master-ai", "26 - Papers/Alignment/31 - Constitutional AI 2022.md", r"Fine-tune\*\*: the original model is fine-tuned on the revised", "cai stage-1 procedure", False),
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"acceptance/rejection criterion is importance sampling", "spec decoding acceptance criterion", False),
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"resample from the adjusted distribution", "spec decoding resample", False),
    ("master-ai", "26 - Papers/2024-2026/12 - DeepSeek-R1 2025.md", r"Stage 3: Rejection sampling \+ SFT", "deepseek-r1 stage 3", False),
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"rejection sampling preserves the target distribution", "medusa rejection sampling", False),
    # --- covers: frozen parameters family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"^#+ Strategy 1: Feature Extraction \(Freeze Everything\)", "freeze everything heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"^#+ 6\.3 Verifying What Is Frozen and What Is Trainable", "verifying frozen heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"^#+ Mistake 10: Freezing Wrong Layers", "freezing wrong layers heading", True),
    ("master-ai", "23 - Multimodal AI/Fusion Architectures/06 - Cross-Modal Attention.md", r"^#+ Freezing vs\. Fine-Tuning Encoders", "freezing vs fine-tuning heading", True),
    # --- covers: fully-connected family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/04. The Fully Connected Layer and Flattening.md", r"^# 4\.4 The Fully Connected Layer", "fc layer note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"^#+ Why Fully Connected Layers\?", "why fc layers heading", True),
    # --- covers: spatial features family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/02. Hierarchical Feature Extraction.md", r"^# 4\.2 Hierarchical Feature Extraction", "hierarchical feature extraction title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"learn the spatial feature detectors", "vgg16 spatial feature detectors", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"actual spatial feature extraction happens", "resnet spatial feature extraction", False),
    # --- covers: top-k experts family ---
    ("master-ai", "07 - Transformers/Variants/15 - Mixture of Experts Transformer.md", r"^#+ The Router", "moe router heading", True),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"^#+ Mixture of Experts \(MoE\)", "perceptrons moe heading", True),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"Only the top-k experts \(typically k=2\) are evaluated per token", "top-k experts definition", False),
    ("master-ai", "27 - Projects/Implementations/04 - Build a Mini MoE.md", r"router that selects top-K experts per token", "mini moe top-k", False),
    # --- covers: watermarks family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"problem called .dataset bias. or .shortcut learning.", "dataset bias shortcut learning def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"model learned to detect the hospital watermark", "covid watermark case study", False),
    ("master-ai", "25 - Frameworks and Tools/Serving/12 - TGI.md", r"^#+ Watermarking", "tgi watermarking heading", True),
    ("master-ai", "25 - Frameworks and Tools/Serving/12 - TGI.md", r"Kirchenbauer et al\. \(2023\) watermarking scheme", "kirchenbauer watermark scheme", False),
    # --- covers: break symmetry family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"^#+ 14\.2 All-Zero Initialization: The Symmetry Problem", "symmetry problem heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"Symmetry breaking is a necessary condition", "symmetry breaking necessary", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural Network Architecture and Notation.md", r"random weights have already broken the symmetry", "broken symmetry in-situ", False),
    # --- covers: disables dropout / eval mode family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"^#+ Why model\.eval\(\) is Mandatory", "why model.eval heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Training vs\. Evaluation Mode", "bn train vs eval heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"^#+ 2\. model\.eval\(\) . Why It Matters", "model.eval why it matters heading", True),
    # --- covers: error curve family ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"error curve is sloping downwards to the right", "error curve in-situ gd", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"lowest point on the error curve", "error curve lowest point", False),
    # --- covers: hyperbolic tangent family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"^#+ E\. Hyperbolic Tangent \(tanh\)", "ann tanh heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/06. Activation Functions in Deep Learning.md", r"^#+ 2\. Tanh \(Hyperbolic Tangent\)", "activation tanh heading", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/02. Mathematical Notation and Symbols.md", r"The Hyperbolic Tangent \(Tanh\) maps inputs to a range between -1 and 1", "tanh def sentence", False),
    ("master-ai", "04 - Neural Networks/Foundations/02 - Activation Functions.md", r"^#+ Tanh", "master-ai tanh heading", True),
    # --- covers: io-aware family ---
    ("master-ai", "06 - Attention Mechanisms/Efficient Attention/11 - FlashAttention.md", r"is an IO-aware exact attention algorithm", "flashattention io-aware def", False),
    ("master-ai", "26 - Papers/Efficient Attention/08 - FlashAttention 2022.md", r"^#+ Other IO-Aware Kernels", "other io-aware kernels heading", True),
    # --- covers: json schemas family ---
    ("master-ai", "13 - Inference/Decoding/07 - Constrained Decoding and CFG.md", r"^#+ JSON Schema Constrained", "json schema constrained heading", True),
    ("master-ai", "13 - Inference/Decoding/07 - Constrained Decoding and CFG.md", r"^# 07 . Constrained Decoding and CFG", "constrained decoding note title", True),
    ("master-ai", "08 - LLMs/Sampling/03 - Sampling Strategies.md", r"^#+ Constrained decoding", "sampling constrained decoding heading", True),
    # --- covers: learning curve family ---
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"^#+ Diagnosing Bias vs Variance with Learning Curves", "learning curves heading", True),
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"diagnostic than train/test error is the \*\*learning curve\*\*", "learning curve definition", False),
    # --- covers: periodic noise family ---
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.3 Frequency Domain Filtering.md", r"^#+ The problem: periodic noise", "periodic noise problem heading", True),
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.3 Frequency Domain Filtering.md", r"^#+ The solution: notch filter", "notch filter solution heading", True),
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.3 Frequency Domain Filtering.md", r"^#+ Notch filters . the killer use case", "notch killer use case heading", True),
    # --- covers: rare terms family ---
    ("master-ai", "05 - NLP Fundamentals/Pre-Transformer NLP/09 - TF-IDF.md", r"^#+ Inverse Document Frequency \(IDF\)", "idf heading", True),
    ("master-ai", "05 - NLP Fundamentals/Pre-Transformer NLP/09 - TF-IDF.md", r"Rare words.*quokka", "quokka rare terms", False),
    ("master-ai", "05 - NLP Fundamentals/Pre-Transformer NLP/10 - BM25.md", r"^# 10 - BM25", "bm25 note title", True),
    # --- covers: resnet50 family (spelling variant) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"^#+ The Bottleneck Block \(ResNet-50, ResNet-101, ResNet-152\)", "bottleneck resnet-50 heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"^#+ Complete PyTorch Code: Fine-Tuning with ResNet-50", "resnet-50 fine-tuning heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"^#+ Bottleneck Block \(ResNet-50/101/152\)", "ann bottleneck resnet-50 heading", True),
    # --- covers: stride family ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/07. Strides - Skipping Pixels and Downsampling.md", r"^# 2\.3 Strides: Skipping Pixels", "strides note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"^#+ Stride", "convolution stride heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"^#+ 1\.3 Stride and Padding", "stride and padding heading", True),
    # --- covers: vgg16-bn family (underscore variant) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"^#+ 5\. VGG16 vs\. VGG16_BN", "vgg16 vs vgg16_bn heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"vgg16_bn = VGG16 with Batch Normalization", "vgg16_bn def comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"VGG16-BN uses batch norm; original VGG16 does not", "vgg16-bn contrast", False),
    # --- covers: vidore family ---
    ("master-ai", "27 - Projects/Capstones/13 - Build a RAG Evaluation Harness.md", r"ViDoRe \(2024\) is the standard", "vidore standard def", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"\*\*ViDoRe benchmark\*\* \(2024\): became the standard for document retrieval evaluation", "vidore benchmark def", False),
    # --- covers: gradient product family ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"gradient product involves the same matrix raised to a high power", "gradient product rnn", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"terms in the gradient product consistently have magnitude greater than 1", "gradient product exploding", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/06. Transfer Learning and ResNet - Summary.md", r"gradient product includes ten derivative terms", "gradient product summary", False),
    # --- covers: lr schedules family ---
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^# 14 - Learning Rate Schedules", "lr schedules note title", True),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^#+ The Standard Schedule: Warmup \+ Cosine Decay", "warmup cosine heading", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^#+ Warmup: Gradual Learning Rate Ramp-Up", "warmup ramp heading", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^#+ CosineAnnealingLR: Smooth Cosine Decay", "cosine annealing heading", True),
    # --- covers: objective function family ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/01. Mathematical Notation (ML Course).md", r"Cost Function \(or Loss Function / Objective Function\)", "objective function def", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/02. Linear Regression from Scratch.md", r"^#+ 3\. The Error Function \(Cost Function\)", "error cost function heading", True),
    ("ai-course", "03 - Machine Learning/03.4 - Support Vector Machines (SVM)/03. The Mathematics of Separation.md", r"canonical objective function of the Support Vector Machine", "svm canonical objective", False),
    # --- covers: single-vector family ---
    ("master-ai", "09 - Foundation Models/Embedding Models/02 - Embedding Models for Retrieval.md", r"^#+ BGE-M3: Multi-Vector \+ Multi-Lingual", "bge-m3 multi-vector heading", True),
    ("master-ai", "18 - Memory Systems/Vector Memory/04 - Vector Memory Backends.md", r"^#+ Multi-Vector and Late-Interaction Indexes", "multi-vector late-interaction heading", True),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"^#+ Multi-Vector Retrieval", "colpali multi-vector heading", True),
    ("master-ai", "09 - Foundation Models/Embedding Models/02 - Embedding Models for Retrieval.md", r"vs single-vector which collapses all token", "single-vector contrast", False),
    # --- rejects: key noise evidence (homonyms, vault labels) ---
    ("ai-course", "README.md", r"Academic DL Ch1", "academic dl ch1 label", False),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"under-built chapters", "under-built vault term", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"e8f5e9", "mermaid hex color", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"Classify a \*\*New Animal\*\*", "knn new animal exercise", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/01 - Vectors.md", r"\*\*Linear independence\*\* . no vector in a set", "linear independence def (independence homonym sense)", False),
    ("master-ai", "02 - Mathematics/Probability/08 - Bayes Theorem Deep Dive.md", r"naive. independence assumption is wrong", "naive bayes independence (homonym sense)", False),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/03. The Transformer Encoder Block.md", r"\*\*Batch independence\.\*\*", "batch independence (homonym sense)", False),
    ("master-ai", "11 - Training/Data/03 - Data Pipelines and Deduplication.md", r"Common Crawl raw HTML", "common crawl (crawl homonym sense)", False),
    ("master-ai", "04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md", r"^#+ Teacher Forcing", "teacher forcing heading (decoding step family)", True),
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/03. Autoregressive vs Parallel Encoding.md", r"^#+ Autoregressive decoding", "autoregressive decoding heading", True),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"\| Epoch \| Train Loss \| Val Loss \|", "train loss table (train loss reject)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/08. Data Preparation and MLP Implementation.md", r"Randomly deactivates a percentage of neurons", "dropout deactivates (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"filter slides across the entire input", "filter slides prose (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"Update weights using computed gradie", "computed gradients code comment (reject evidence)", False),
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"Hit rate: 30-60% for repetitive content", "30-60 numeric range (reject evidence)", False),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"6-10 new wikilinks per note", "6-10 numeric range (reject evidence)", False),
]


def main() -> int:
    ok = 0
    fail = 0
    for vault, rel, pattern, note, require_heading in CHECKS:
        path = VAULTS[vault] / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            print(f"FAIL [missing file] {vault}/{rel} :: {note}")
            fail += 1
            continue
        lines = text.split("\n")
        pat = re.compile(pattern)
        found = None
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                found = (i, line.strip()[:120])
                break
        if found is None:
            print(f"FAIL [no match] {vault}/{rel} :: {note} :: /{pattern}/")
            fail += 1
            continue
        line_no, snippet = found
        if require_heading:
            struct = extract_structure_text(text)
            heading_lines = {h["line"] for h in struct.get("headings", [])}
            if line_no not in heading_lines:
                print(
                    f"FAIL [not a real heading] {vault}/{rel}:{line_no} :: {note}"
                )
                fail += 1
                continue
        print(f"OK   {vault}/{rel}:{line_no} :: {note}")
        ok += 1
    print(f"\n{ok} OK, {fail} FAIL, {len(CHECKS)} total checks")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
