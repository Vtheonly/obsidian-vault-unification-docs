#!/usr/bin/env python3
"""Targeted corpus verification for batch-13 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list, so a Python comment inside a code fence can no
longer pass as a heading citation.

Session-13 lessons applied: heading LEVELS checked exactly (## vs ###),
note titles that differ from filenames, **bold** markers inside patterns,
term-separated definitions, and the glossary indexes checked before any
acronym-absence claim.
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
    # --- covers: openhermes family (#1) ---
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"\*\*OpenHermes\*\*: large synthetic \(1M\)", "openhermes dataset gloss", False),
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"many top open models \(OpenHermes, Tulu\) are trained mostly on synthetic data", "openhermes synthetic-data use", False),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"Most open-source chat models \(Zephyr, OpenHermes, Tulu, many Llama fine-tunes\) use DP", "openhermes dpo adoption", False),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"Zephyr, OpenHermes, Tulu\) was largely enabled by D", "openhermes dpo 2023 paper", False),
    # --- covers: outside function family (#2; batch-12 inside-function precedent) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Derivative of the OUTSIDE function \(leaving the inside alone\)", "outside function rule", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Identify Outside Function: f\( \)", "outside function mermaid step", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/05. Forward Propagation and Activation Functions.md", r"derivative of the outside function \$\\log\(z\)\$", "outside function log sigmoid", False),
    # --- covers: resnet18 family (#3) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"^#+ The Basic Block \(ResNet-18 and ResNet-34\)", "basic block heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/06. Transfer Learning and ResNet - Summary.md", r"\*\*Basic Block \(ResNet-18/34\):\*\* Consists of two sequential", "basic block def summary", False),
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q12 - ResNet Bottleneck Blocks and Architectural Variants.md", r"a\) ResNet-18 and ResNet-34", "basic block quiz answer", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"^#+ Basic Block \(ResNet-18 / ResNet-34\)", "ann basic block heading", True),
    # --- covers: scalar bias family (#4) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"exactly one\* distinct scalar bias parameter", "scalar bias def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/02. Core Operators and Geometry - Summary.md", r"\$b_k\$ is the scalar bias term corresponding to the \$k\$-th filter", "scalar bias summary def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"adds a scalar bias term \$b\$", "scalar bias affine", False),
    # --- covers: single artificial neuron family (#5, #6) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"^#+ The Artificial Neuron: The Atomic Unit", "artificial neuron heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"fundamental building block of every neural network is the artificial neuron, sometimes called a perceptron", "artificial neuron def", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule and Convergence.md", r"A single artificial neuron \(a perceptron\) doing a simple task is functionally identical to linear regression", "single artificial neuron perceptron", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.4 - Labs/01. TP2.md", r"two core components of a single artificial neuron", "tp2 formal neuron", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.4 - Labs/01. TP2.md", r"Lab 2: Formal Neuron", "tp2 lab title", False),
    # --- covers: still sota family (#7; glossary precedent ddpm) ---
    ("master-ai", "28 - Glossary/Acronyms/Acronyms Index.md", r"\*\*SOTA\*\* — State Of The Art", "sota glossary entry", False),
    ("ai-course", "03 - Machine Learning/03.7 - Tree-Based Models/02. Random Forests and Bagging.md", r"boosting is the .state of the art.", "state of the art in situ", False),
    ("master-ai", "27 - Projects/Capstones/12 - Build a Code Agent.md", r"State of the art \(2025\)", "state of the art capstone", False),
    # --- covers: tree shape family (#8) ---
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"^#+ Tree-based Speculation", "tree-based speculation heading", True),
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"tree-structured\*\* drafts instead of linear sequences", "tree-structured drafts def", False),
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"form a \*\*tree\*\* of possible continuations", "medusa tree def", False),
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"target model verifies the tree in a single forward pass", "medusa tree verification", False),
    ("master-ai", "26 - Papers/Efficient Attention/51 - EAGLE-3 2025.md", r"Tree topology is reactive", "eagle3 tree topology", False),
    ("master-ai", "26 - Papers/Efficient Attention/51 - EAGLE-3 2025.md", r"picks a tree shape after computing the draft probabilities", "eagle3 tree shape", False),
    # --- covers: true negatives family (#9) ---
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"\*\*True Negative \(TN\)\*\*: The patient is HEALTHY", "true negative def", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"cm\.ravel\(\) returns \[TN, FP, FN, TP\]", "ravel order", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"comparing predicted labels against true labels", "confusion matrix intro", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"True Negative \(TN\)", "knn tn cell", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"\*\*TN\*\* \(True Negative\)", "ml summary tn cell", False),
    # --- covers: def keyword family (#10) ---
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/05. Functions and Lambda Expressions.md", r"^#+ 5\.1 Defining Functions", "defining functions heading", True),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/05. Functions and Lambda Expressions.md", r"Functions are reusable blocks of code", "functions def", False),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/05. Functions and Lambda Expressions.md", r"\*\*Parameter:\*\* The variable listed inside the parentheses", "parameter def", False),
    # --- covers: super family (#11) ---
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/06. Object Oriented Programming (OOP) in Data Science.md", r"^#+ 6\.3 Inheritance", "inheritance heading", True),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/06. Object Oriented Programming (OOP) in Data Science.md", r"Inheritance allows a class \(Child\) to derive attributes and methods from another class \(Parent\)", "inheritance def", False),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/06. Object Oriented Programming (OOP) in Data Science.md", r"super\(\)\.__init__\(name, age\) # Initialize parent", "super init gloss", False),
    # --- covers: normalization layers family (#12) ---
    ("master-ai", "07 - Transformers/Components/04 - Normalization Layers.md", r"^#+ Normalization Layers", "normalization layers note title", True),
    ("master-ai", "07 - Transformers/Components/04 - Normalization Layers.md", r"^#+ BatchNorm vs LayerNorm", "bn vs ln heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ 16\. Batch Normalization", "batch norm note title", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Layer Normalization \(LN\)", "layer norm heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"reduces the number of normalization layers", "convnext normalization", False),
    # --- covers: odot family (#13) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"The \*\*Hadamard product\*\* \$A \\odot B\$ is element-wise multiplication", "hadamard def", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"Confusing \$\\odot\$ \(Hadamard\) with", "hadamard caution", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/01 - Vectors.md", r"^#+ Element-wise \(Hadamard\) Product", "hadamard heading", True),
    ("ai-course", "07 - Sequence Models and RNNs/07.2 - LSTM and GRU/01. LSTM - Gates as Learned Traffic Controllers.md", r"\$\\odot\$ is element-wise \(Hadamard\) product", "lstm odot gloss", False),
    # --- covers: low frequencies family (#14) ---
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.1 Introduction to the Frequency Domain.md", r"\*\*Low frequencies:\*\* gratings that oscillate slowly", "low frequencies def", False),
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.1 Introduction to the Frequency Domain.md", r"\*\*Low frequencies\*\* = smooth, large-scale structure", "low frequencies def 2", False),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.9 Image Pyramids and Multi-Scale Representation.md", r"fold back as spurious low frequencies", "aliasing low frequencies", False),
    ("master-ai", "06 - Attention Mechanisms/Positional Information/08 - RoPE.md", r"capture coarse long-range position", "rope low frequency", False),
    # --- covers: feed-forward network family (#15) ---
    ("master-ai", "07 - Transformers/Components/05 - Feed-Forward Network Deep.md", r"^#+ 05 - Feed-Forward Network \(FFN\) Deep Dive", "ffn deep dive title", True),
    ("master-ai", "07 - Transformers/Architecture/01 - Transformer Block.md", r"^#+ 2\. Feed-Forward Network \(FFN\)", "transformer block ffn heading", True),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"^#+ The Feed-Forward Network in Transformers", "ffn in transformers heading", True),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/03. The Transformer Encoder Block.md", r"^#+ Sublayer 2: Position-wise Feedforward Network \(FFN\)", "position-wise ffn heading", True),
    # --- covers: learning rate schedules family (#16, #17) ---
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^#+ 14 - Learning Rate Schedules", "lr schedules note title", True),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^#+ The Standard Schedule: Warmup \+ Cosine Decay", "warmup cosine heading", True),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^#+ Step decay", "step decay heading", True),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"^#+ Learning-Rate Schedules", "learning-rate schedules heading", True),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"The learning rate is the \*\*single most important hyperparameter\*\*", "lr most important", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^#+ CosineAnnealingLR: Smooth Cosine Decay", "cosine annealing heading", True),
    # --- covers: goodfellow family (#18) ---
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/05. Evolution and History of Deep Learning.md", r"Ian Goodfellow creates GANs \(Generative Adversarial Networks\), allowing AI to generate realistic images", "goodfellow gan history", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/05. Evolution and History of Deep Learning.md", r"Ian Goodfellow invents GANs", "goodfellow timeline", False),
    ("ai-course", "09 - Quizzes and Question Banks/01. Deep Learning - Chapter 1 (Introduction to DL)/Q3 - Evolution and History of Deep Learning.md", r"c\) Ian Goodfellow", "goodfellow quiz answer", False),
    # --- covers: high bias family (#19) ---
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"Underfit = high bias; overfit = high variance", "bias variance def", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"^#+ .*Underfitting \(High Bias\)", "knn high bias heading", True),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"^#+ .*Underfitting \(High Bias\)", "ml summary high bias heading", True),
    ("ai-course", "03 - Machine Learning/03.7 - Tree-Based Models/03. Gradient Boosting and XGBoost.md", r"weak learner\*\* \(high bias, low variance", "xgboost weak learner", False),
    # --- covers: single attention family (#20) ---
    ("master-ai", "06 - Attention Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md", r"A single attention head computes \*\*one\*\* weighted average of value vectors", "single head def master-ai", False),
    ("ai-course", "08 - Attention and Transformers/08.1 - The Attention Mechanism/04. Multi-Head Attention - Parallel Relationship Patterns.md", r"A single attention head at dimension \$d\$ produces a weighted average of values", "single head bandwidth", False),
    ("ai-course", "08 - Attention and Transformers/08.1 - The Attention Mechanism/04. Multi-Head Attention - Parallel Relationship Patterns.md", r"A single attention head computes one attention distribution per query", "single head one distribution", False),
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/03. From RNNs to Attention - The Historical Bridge.md", r"A single attention head can learn one pattern of relationships", "single head one pattern", False),
    # --- covers: dynamic range family (#21) ---
    ("ai-course", "06 - Image Processing/01. Fundamentals of Digital Images/1.3 Resolution and Bit Depth.md", r"determines the \*\*Dynamic Range\*\* and the \*\*Color Palette\*\*", "dynamic range bit depth def", False),
    ("ai-course", "06 - Image Processing/02. Intensity Transformations and Histograms/2.1 The Image Histogram.md", r"image uses the full dynamic range", "histogram dynamic range", False),
    ("ai-course", "06 - Image Processing/02. Intensity Transformations and Histograms/2.3 Contrast Stretching.md", r"^#+ 2\.3 Contrast Stretching", "contrast stretching note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"wider dynamic ran", "pooling dynamic range", False),
    # --- covers: latent vector family (#22) ---
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/02. The Information Bottleneck and Latent Space.md", r"generalization of the autoencoder's fixed latent vector", "fixed latent vector", False),
    ("ai-course", "10 - Generative Models/10.2 - Variational Autoencoders/01. From Autoencoder to VAE - Learning a Distribution.md", r"Sampling a random latent vector and decoding it produces garbage", "random latent vector", False),
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/02. The Information Bottleneck and Latent Space.md", r"\*\*latent representation\*\* or \*\*code\*\*", "latent representation def", False),
    ("ai-course", "10 - Generative Models/10.1 - Autoencoders/01. The Autoencoder - Compression as Learning.md", r"^#+ What the latent space looks like", "latent space heading", True),
    # --- covers: projection layer family (#23) ---
    ("master-ai", "23 - Multimodal AI/Vision-Language/03 - LLaVA.md", r"^#+ 2\. Projection Layer", "llava projection heading", True),
    ("master-ai", "23 - Multimodal AI/Vision-Language/03 - LLaVA.md", r"A single linear layer \(or a small MLP in LLaVA-1\.5\) that maps CLIP embeddings", "llava projection def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"A single linear projection layer can then map this vector directly to the output classes", "vgg projection", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"learn an optimal linear projection for matching dimensions", "resnet option b projection", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"learned linear projection", "bottleneck 1x1 projection", False),
    # --- covers: squared gradients family (#24) ---
    ("master-ai", "02 - Mathematics/Optimization/13 - Adam Derivation.md", r"exponential moving average of squared gradients", "adam v_t def", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"accumulates past squared gradients to adapt the learning rate", "rmsprop squared gradients", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"Second moment\*\* \(mean of squared gradients, like RMSProp\)", "second moment gloss", False),
    # --- covers: steepest ascent / gradient direction family (#25, #26) ---
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"direction of steepest ascent", "gradient steepest ascent", False),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"It points in the direction of steepest ascent", "jacobians steepest ascent", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/02. Linear Regression from Scratch.md", r"gradient points uphill \(direction of steepest ascent\)", "uphill steepest ascent", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"Direction\*\* of steepest ascent", "direction of steepest ascent", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/01 - Vectors.md", r"step in the negative gradient direction", "negative gradient direction", False),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.6 Canny and LoG - Advanced Edge Detection.md", r"gradient direction \(perpendicular to the edge\)", "canny gradient direction", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"acts like a \*\*sensitivity vector\*\*", "sensitivity vector", False),
    # --- covers: tensor shape family (#27) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"\*\*tensor shape manipulation\*\*", "tensor shape manipulation", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"^#+ NCHW vs NHWC", "nchw nhwc heading", True),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"Tensor shape bugs are the most common error in deep learning", "tensor shape bugs", False),
    # --- covers: per filter family (#28) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"Bias: Exactly One Per Filter, Not Per Channel or Per Pixel", "one per filter caution", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"one\*\* bias parameter per filter", "one bias per filter def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md", r"One bias per filter\. Total biases = 128", "one bias per filter count", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"Parameters per filter", "parameters per filter", False),
    # --- covers: image features family (#29) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/02. Hierarchical Feature Extraction.md", r"^#+ 4\.2 Hierarchical Feature Extraction", "hfe note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/02. Hierarchical Feature Extraction.md", r"core magic of deep neural architectures is \*\*Hierarchical Feature Extraction\*\*", "hfe def", False),
    ("master-ai", "23 - Multimodal AI/Fusion Architectures/06 - Cross-Modal Attention.md", r"Image features are treated as additional input tokens", "image features tokens", False),
    ("master-ai", "23 - Multimodal AI/Vision-Language/03 - LLaVA.md", r"projected image features", "projected image features", False),
    # --- covers: runtimeerror family (#30) ---
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/08. Error Handling and Exception Management.md", r"^#+ 8\. Error Handling and Exception Management", "error handling note title", True),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/08. Error Handling and Exception Management.md", r"Robust code does not crash when it encounters unexpected input", "error handling def", False),
    ("ai-course", "02 - Python and Data Tooling/02.2 - Python Programming Essentials/08. Error Handling and Exception Management.md", r"\*\*ValueError:\*\* Function receives argument of correct type but inappropriate value", "valueerror def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"RuntimeError: Expected input channels 32 but got 64", "runtimeerror channel mismatch", False),
    ("master-ai", "04 - Neural Networks/Training/06 - Backpropagation.md", r"RuntimeError: Trying to backward through the graph a second time", "runtimeerror backward twice", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"RuntimeError: view size is not compatible", "runtimeerror view", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"RuntimeError: Expected all tensors to be on the same device", "runtimeerror device", False),
    # --- rejects: concept-side coverage citations ---
    # floor function (lfloor/rfloor rejects)
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"^#+ Handling Fractional Edge Cases \(The Floor Function\)", "floor function heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"floor function accounts for the fact that", "floor function def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"Why the Floor Function\?", "floor function why", False),
    # cosine / sine (cos, sin rejects)
    ("master-ai", "02 - Mathematics/Linear Algebra/03 - Cosine Similarity.md", r"^#+ Cosine Similarity", "cosine similarity note title", True),
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.2 The Fourier Transform.md", r"real part\*\* \(the cosine component\) and an \*\*imaginary part\*\* \(the sine component\)", "fourier cosine sine components", False),
    ("master-ai", "06 - Attention Mechanisms/Positional Information/07 - Sinusoidal and Learned Positional.md", r"^#+ 07 - Sinusoidal and Learned Positional", "sinusoidal note title", True),
    ("master-ai", "06 - Attention Mechanisms/Positional Information/06 - Positional Encoding Overview.md", r"Each dimension is a sine/cosine at a different frequency", "sine cosine frequency", False),
    # chain rule (outside-function reject support is a cover; predicted labels reject)
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"# Predicted labels", "predicted labels code comment", False),
    # reward model (reward model needed reject)
    ("master-ai", "12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md", r"^#+ Stage 2: Reward Model Training", "reward model stage heading", True),
    ("master-ai", "02 - Mathematics/Statistics/16 - Estimators and Bias.md", r"by eliminating the reward model, DPO reduces variance", "reward model elimination", False),
    # moe (active per reject)
    ("master-ai", "07 - Transformers/Variants/15 - Mixture of Experts Transformer.md", r"^#+ 15 - Mixture-of-Experts \(MoE\) Transformer", "moe note title", True),
    ("master-ai", "10 - Model Architecture Research/Closed Source/07 - GPT-4 Inferred Architecture.md", r"only a fraction of parameters are active per token", "active per token", False),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"^#+ Mixture of Experts \(MoE\)", "moe heading", True),
    # tokenization (input tokens reject)
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"^#+ Tokenization Overview", "tokenization note title", True),
    # parameter sharing (across positions reject)
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/01. Local Connectivity and Parameter Sharing.md", r"^#+ 4\.1 Local Connectivity and Parameter Sharing", "parameter sharing note title", True),
    ("master-ai", "04 - Neural Networks/Architectures/04 - RNN LSTM GRU.md", r"^#+ 9\. Weight sharing across time", "weight sharing heading", True),
    # learning rate range test (small learning / small learning rate rejects)
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"learning rate range test", "lr range test", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"starting with a very small learning rate and gradually increasing it", "small lr warmup", False),
    # relu positive inputs (positive inputs reject)
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/06. Activation Functions in Deep Learning.md", r"positive inputs produce positive outputs", "tanh zero-centered", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"Gradient = 1 for positive inputs", "relu positive gradient", False),
    # hybrid architectures (use hybrid reject)
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"hybrid architectures with convolutional front-ends and Transformer back-ends", "hybrid architectures", False),
    ("master-ai", "10 - Model Architecture Research/Open Source/07 - GLM 5.2 Architecture.md", r"use hybrid attention", "use hybrid attention", False),
    # early/later layers (later layers reject)
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"gradients that are 100. or 1000. smaller", "early layer gradient scale", False),
    # loss decreases (training curves covered)
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"validation loss decreases more slowly and may plateau", "refinement phase", False),
    # example strings (cat sat, emails)
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/02. Positional Encoding - Injecting Order Into a Set.md", r"The cat sat on the mat", "cat sat example", False),
    ("master-ai", "03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md", r"spam filter that always says", "emails spam example", False),
    # vault meta (my-project, source files)
    ("ai-course", "README.md", r"/home/z/my-project/scripts/02_build_master_vault\.py", "my-project path artifact", False),
    ("ai-course", "README.md", r"Source files:\*\*", "source files label", False),
    # generic verb phrases (initialize, model uses, acts like, use cases)
    ("ai-course", "03 - Machine Learning/03.1 - Regression/02. Linear Regression from Scratch.md", r"Initialize gradients to 0", "initialize comment", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"Initialize Parameter", "initialize mermaid node", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/02. Loss Functions and Cost Optimization.md", r"it acts like MSE", "acts like mse", False),
    ("ai-course", "02 - Python and Data Tooling/02.3 - Essential Python Libraries/06. Interactive Plotting with Plotly.md", r"covers 90% of use cases", "use cases phrase", False),
    # numeric artifacts (times 64, times 224, times 16)
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"7 \\times 7 \\times 3 \\times 64 = 9", "times 64 artifact", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"224 \\times 224 \\times 3 = 150", "times 224 artifact", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"3 \\times 3 \\times 16 \+ 1", "times 16 artifact", False),
    # lfloor/rfloor latex artifacts
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"\\lfloor t / \\text\{step", "lfloor artifact", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"\\left\\lfloor \\frac\{W - k \+ 2p\}\{s\} \\right\\rfloor", "rfloor artifact", False),
    # cos/sin latex artifacts
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"1 \+ \\cos\\left\(\\frac\{t\}\{T_\{\\max\}", "cos artifact", False),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.10 The Hough Transform.md", r"x \\cos\\theta \+ y \\sin\\theta", "sin artifact hough", False),
    # creative writing use-case phrase
    ("master-ai", "08 - LLMs/Sampling/03 - Sampling Strategies.md", r"Creative writing", "creative writing row", False),
    # new data generic phrase
    ("ai-course", "03 - Machine Learning/03.8 - Dimensionality Reduction/02. t-SNE and UMAP.md", r"Can embed new data", "new data phrase", False),
    # large model generic phrase
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"VGG16 is a large model", "large model phrase", False),
    # model uses verb phrase
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"model uses significantly less GPU memory", "model uses phrase", False),
    # reward model needed phrase fragment
    ("master-ai", "02 - Mathematics/Statistics/16 - Estimators and Bias.md", r"no reward model needed", "reward model needed fragment", False),
    # input tokens phrase
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. The Encoder-Decoder Pattern - Conditional Generation.md", r"T\$ input tokens", "input tokens phrase", False),
    # ascent fragment
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"steepest \*ascent\* \(maximum error\)", "ascent fragment", False),
]


def main() -> int:
    ok = 0
    fail = 0
    for vault, path, pattern, note, require_heading in CHECKS:
        root = VAULTS[vault]
        fp = root / path
        if not fp.exists():
            print(f"MISSING FILE [{note}] {vault}/{path}")
            fail += 1
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        lines = text.split("\n")
        pat = re.compile(pattern)
        struct = extract_structure_text(text)
        heading_lines = {h["line"]: h["text"] for h in struct.get("headings", [])}
        found = False
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                if require_heading and i not in heading_lines:
                    continue
                status = "HEADING" if i in heading_lines else "LINE"
                print(f"OK   [{note}] {vault}/{path}:{i} ({status}) :: {line.strip()[:110]}")
                found = True
                ok += 1
                break
        if not found:
            print(f"FAIL [{note}] {vault}/{path} pattern={pattern!r}")
            fail += 1
    print(f"\n{ok} OK, {fail} FAIL, {len(CHECKS)} checks")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
