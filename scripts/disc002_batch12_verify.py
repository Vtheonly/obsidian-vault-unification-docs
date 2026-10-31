#!/usr/bin/env python3
"""Targeted corpus verification for batch-12 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list, so a Python comment inside a code fence can no
longer pass as a heading citation.

Incorporates the VERIFIED subagent errata (independently re-checked by the
orchestrator): the LogSoftmax ':109' locator belongs to '08. Loss Functions
and Optimizers Deep Dive.md' (not '02. Loss Functions and Cost
Optimization.md'); the thought-vector definition is at '06 - Attention
Mechanisms/Origins/01 - Origins of Attention.md:19' (not the Bahdanau 2014
note); the running-stats/SGD/late-interaction headings are h3 in several
files. The CIFAR-10 definition at Q11:182 (term-separated quiz matching
block) is verified here as the decisive cover evidence.
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
    # --- covers: class label family (#1, #19) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"the actual, correct \*\*Answer\*\* \(the target label\)", "target label def 1", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural Network Architecture and Notation.md", r"the actual, correct \*\*Answer\*\* \(the target label\)", "target label def 2", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/01. Backpropagating to the Output Layer.md", r"the actual, correct \*\*Answer\*\* \(the target label\)", "target label def 3", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"produces class labels", "produces class labels", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"class label for every pixel", "segmentation class label def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/03. Hyperparameters and Basic PyTorch - Summary.md", r"ground-truth class label index", "nll class label index", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"^#+ 7\.2 Target Format: Integer Class Indices", "integer class indices heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"INTEGER CLASS LABELS", "ce integer labels caveat", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"integer class labels \(NOT one-hot\)", "exercise integer labels caveat", False),
    # --- covers: convolutional block family (#2) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"convolutional block follows the pattern \*\*Conv → BatchNorm → ReLU → MaxPool\*\*", "conv block pattern def", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Where to Place Batch Normalization: Conv → BatchNorm → ReLU", "conv bn relu heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"A standard convolutional block: Conv → BatchNorm → ReLU", "convblock docstring", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"Conv Block 5", "conv block abstraction table", False),
    # --- covers: cot chains family (#4) ---
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"learn to produce CoT chains as part of training", "cot chains training", False),
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"produce long CoT chains internally", "cot chains internal", False),
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"N CoT chains at temperature > 0", "n cot chains majority", False),
    ("master-ai", "26 - Papers/Agents and RAG/38 - Self-Consistency 2022.md", r"sample N different reasoning paths", "self-consistency def", False),
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"^# Chain-of-Thought", "cot note title", True),
    # --- covers: fully-connected layer family (#7) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/04. The Fully Connected Layer and Flattening.md", r"^# 4\.4 The Fully Connected Layer", "fc layer note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"The most common type of layer is the fully connected layer", "fc def sentence", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"fully connected layer that process the same input", "fc parameter comparison", False),
    # --- covers: logsoftmax family (#8; CORRECTED :109 file per verified erratum) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/02. Loss Functions and Cost Optimization.md", r"combines LogSoftmax and NLLLoss in a single, numerically stable operation", "logsoftmax composition", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"Use LogSoftmax \+ NLLLoss separately", "logsoftmax alternative (corrected file)", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"Negative Log-Likelihood \(NLLLoss\)\*\*: Given the predicted probabilities", "nllloss definition", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"CrossEntropyLoss combines Lo", "resnet ce loss comment", False),
    ("master-ai", "27 - Projects/Capstones/07 - Build a Reasoning Model Fine-Tune.md", r"take the log-softmax of the logits", "log-softmax capstone", False),
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/03. Beam Search and Decoding Strategies.md", r"^#+ Why log-probabilities, not probabilities", "log-probabilities heading", True),
    # --- covers: models 2023 / reward models 2023 family (#9, #11) ---
    ("master-ai", "26 - Papers/Alignment/50 - Process Reward Models 2023.md", r"^# 50", "prm paper note title", True),
    ("master-ai", "26 - Papers/Alignment/50 - Process Reward Models 2023.md", r"Outcome Reward Model \(ORM\)\*\*: the reward is a single scalar", "orm definition", False),
    ("master-ai", "26 - Papers/Alignment/50 - Process Reward Models 2023.md", r"^#+ Open Dataset \(PRM800K\)", "prm800k heading", True),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"50 - Process Reward Models 2023 \(Lightman et al\.", "paper-note index entry", False),
    ("master-ai", "26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md", r"Let's Verify Step by Step", "verify step by step ref", False),
    # --- covers: single fixed-length vector family (#12, #41; CORRECTED thought-vector locator) ---
    ("master-ai", "04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md", r"^# 05 - Seq2Seq and the Information Bottleneck", "bottleneck note title", True),
    ("master-ai", "04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md", r"single fixed-length vector \$\\mathbf\{c\}\$", "bottleneck fixed-length c", False),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"compressed the entire source sentence into a single fixed-length vector, creating an information bottleneck", "origins bottleneck def", False),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"final hidden state.*is the .thought vector.", "thought vector def (corrected locator)", False),
    ("master-ai", "26 - Papers/Attention Origins/01 - Bahdanau Attention 2014.md", r"Instead of compressing the entire source sentence into a single fixed-length vector", "bahdanau fixed-length", False),
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/01. The Bottleneck Problem - Why One Vector Is Not Enough.md", r"single fixed-size context vector cannot carry enough information", "bottleneck problem note", False),
    # --- covers: sparse signal family (#13) ---
    ("master-ai", "26 - Papers/Alignment/50 - Process Reward Models 2023.md", r"\*\*Sparse signal\*\*: a 10-step math solution gets one reward", "sparse signal definition", False),
    ("master-ai", "26 - Papers/Alignment/50 - Process Reward Models 2023.md", r"sparse signal, hard to debug", "sparse vs dense contrast", False),
    ("master-ai", "26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md", r"\*\*Dense signal\*\*: every step gets a reward", "dense signal definition", False),
    # --- covers: avg pool family (#17) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/03. Activation and Pooling Layers.md", r"^#+ Average Pooling: How It Differs from Max Pooling", "average pooling heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"average pooling produces denser but weaker gradients", "avg pooling gradient def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"Avg Pool 2×2, stride 2", "lenet avg pool row", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"^# 6\. Advanced Pooling Mechanisms", "advanced pooling note title", True),
    # --- covers: class scores family (#20) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"relies on the \*\*linear\*\* relationship between the spatial feature map values and the class scores", "gap class score linearity", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"would affect the class score", "gradcam class score def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"per-pixel class scores", "segmentation class scores", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"^#+ 7\.1 Input Format: Raw Logits", "raw logits heading", True),
    ("master-ai", "02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md", r"model produces logits", "logits entropy def", False),
    # --- covers: final relu family (#23) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"Where is the ReLU After the Addition", "final relu callout", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md", r"\*\*Final ReLU\*\*: Applies ReLU to the sum", "final relu anatomy step", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"Final ReLU after addition", "final relu code comment", False),
    # --- covers: imagenet weights family (#25) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"^#+ 1\.2 Loading with Pre-trained Weights", "pretrained weights heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"widely distributed as pre-trained weights", "vgg pretrained availability", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"When you start from pre-trained weights", "transfer init note", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"models\.ResNet50_Weights\.IMAGENET1K_V1 loads the standard ImageNet weights", "resnet weights api", False),
    # --- covers: input spatial size family (#26) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"imposes no constraint on the input spatial size", "gap no size constraint", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"regardless of the input spatial size", "adaptive pool comment", False),
    # --- covers: output error family (#28) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/02. Backpropagating to the Hidden Layer.md", r"error of a hidden node is defined as", "hidden error definition", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/02. Backpropagating to the Hidden Layer.md", r"push the output error backward across the weights", "push output error", False),
    # --- covers: uses running stats family (#32; heading levels per verified erratum) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Training vs\. Evaluation Mode \(CRITICAL\)", "bn eval mode heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^#+ Why Evaluation Mode Cannot Compute Batch Statistics", "bn eval cannot batch stats heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"^#+ Evaluation Mode", "dropout eval mode heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"batch norm uses running stat", "bn running stats comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"BatchNorm still uses running statistics during training", "bn running stats mistake", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"eval uses running stats", "dropout-vs-bn noise table", False),
    # --- covers: grad-cam heatmap family (#36) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"^#+ 2\. Grad-CAM: Gradient-weighted Class Activation Mapping", "gradcam heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"We compute the Grad-CAM heatmap", "gradcam heatmap formula", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"^#+ \(Optional\) Grad-CAM Visualizations", "gradcam pipeline heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"From CAM to Grad-CAM", "cam to gradcam tip", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/07. Scaling, Pipeline and Interpretability - Summary.md", r"^#+ 5\.2 Grad-CAM", "gradcam summary heading", True),
    # --- covers: pre-trained resnet-50 family (#39) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"^#+ The Bottleneck Block \(ResNet-50, ResNet-101, ResNet-152\)", "bottleneck resnet-50 heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"^#+ Complete PyTorch Code: Fine-Tuning with ResNet-50", "resnet-50 fine-tuning heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"Step 1: Load the pre-trained ResNet-50 model", "resnet-50 load", False),
    # --- covers: sgd optimizer family (#40; heading levels per verified erratum) ---
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"^#+ Stochastic Gradient Descent \(SGD\)", "sgd heading master-ai", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/01. Gradient Descent Optimization (DL Course).md", r"^#+ 2\. Stochastic Gradient Descent \(SGD\)", "sgd heading gd course", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^#+ SGD \(Stochastic Gradient Descent\)", "sgd heading deep dive", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"^#+ SGD \(Stochastic Gradient Descent\)", "sgd heading hyperparameters", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"\| Property \| SGD \+ Momentum \| Adam \|", "sgd vs adam table", False),
    # --- covers: cifar10 (#45; CORRECTED to cover via the term-separated quiz definition) ---
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q11 - The Degradation Problem and Residual Connections.md", r"c\) CIFAR-10 dataset", "cifar term in match block", False),
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q11 - The Degradation Problem and Residual Connections.md", r"n\) A popular benchmark dataset for deep learning with 60,000 32x32 color images in 10 classes", "CIFAR-10 DEFINITION (term-separated)", False),
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q11 - The Degradation Problem and Residual Connections.md", r"c\) -> n\)", "cifar answer pairing", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"load the 50,000 training images", "cifar split comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"CIFAR-10 images have 3 color channels", "cifar channels comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md", r"num_classes = 10  # CIFAR-10 has 10 classes", "cifar classes comment", False),
    ("ai-course", "09 - Quizzes and Question Banks/02. Deep Learning - Chapter 2 (CNN)/Q22 - PyTorch Implementation Basics.md", r"pre-built dataset classes for common benchmarks like MNIST and CIFAR-10", "torchvision datasets quiz", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/07. Lab - Guide Complet Régression Linéaire et Deep Learning (MNIST).md", r"Hello World. du Deep Learning", "mnist definition (contrast)", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/05. Evolution and History of Deep Learning.md", r"ILSVRC \(ImageNet Large Scale Visual Recognition Challenge\) required classifying", "imagenet definition (contrast)", False),
    # --- covers: inside function family (#50) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Derivative of the OUTSIDE function \(leaving the inside alone\)", "chain rule rule statement", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Identify Inside Function", "inside function mermaid", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/05. Forward Propagation and Activation Functions.md", r"Let the inside function be", "sigmoid inside function step", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/03. Understanding the Math Notation - Chain Rule and wrt.md", r"^#+ 5\. Understanding the Math Notation", "chain rule notation note title", True),
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"^# Gradient and Chain Rule", "master-ai chain rule note", True),
    # --- covers: late-interaction retrieval family (#51; heading levels per verified erratum) ---
    ("master-ai", "09 - Foundation Models/Embedding Models/02 - Embedding Models for Retrieval.md", r"^#+ Late-Interaction Models \(ColBERT, ColPali\)", "late-interaction heading retrieval", True),
    ("master-ai", "18 - Memory Systems/Vector Memory/04 - Vector Memory Backends.md", r"^#+ Multi-Vector and Late-Interaction Indexes", "late-interaction heading memory", True),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"^#+ Late Interaction \(ColBERT-style\)", "late interaction heading colpali", True),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"\*\*MaxSim\*\*: for each query token", "maxsim definition", False),
    ("master-ai", "27 - Projects/Mini-Projects/02 - Build a Mini RAG Pipeline.md", r"^#+ Late-Interaction Retrieval \(ColBERT, ColPali\)", "late-interaction heading rag", True),
    # --- covers: multi-class problems family (#59) ---
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"^#+ Multi-Class Extensions: Macro, Micro, and Weighted Averaging", "multi-class extensions heading", True),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"For multi-class problems with \$C\$ classes", "multi-class extension def", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/01. Model Evaluation and Metrics.md", r"^#+ 8\.4\. Multi-Class Classification Example", "multi-class example heading", True),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"^#+ 3\. Multi-Class Extension", "multi-class extension summary heading", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/02. Loss Functions and Cost Optimization.md", r"^#+ Categorical Cross-Entropy — Detailed Breakdown", "categorical ce heading", True),
    # --- rejects: key noise evidence ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"# Core PyTorch library", "core pytorch code comment (reject)", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"memorizes the entire training dataset", "knn lazy learner (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"An \*\*epoch\*\* is one complete pass through the entire training dataset", "epoch definition (covered subject)", False),
    ("master-ai", "12 - Fine-Tuning/PEFT/01 - LoRA.md", r"\[\[12 - Fine-Tuning/MOC\|Fine-Tuning MOC\]\]", "fine-tuning moc wikilink (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"Move data to the same device as the model", "move data comment (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"Val Acc: \{val_acc", "val acc print (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"Train acc >> Val acc", "train vs val acc mermaid (covered subject)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/07. Inception Architecture Deep Dive.md", r"projects to the 1000 ImageNet classes", "1000 imagenet classes prose (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"nn\.Linear\(2048, 1000\) for 1000 ImageNet classes", "resnet 1000 classes (reject evidence)", False),
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"For a 1B-parameter model, reverse mode computes all 1B gradients", "1b reverse mode (reject evidence)", False),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"for a 1B-parameter model, the Hessian is", "1b hessian (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"best_val_acc = 0\.0", "best val acc code (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"best validation accuracy seen so far", "best val acc comment (reject evidence)", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"# Core PyTorch library", "core pytorch library comment (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"'epoch': epoch,", "epoch checkpoint key (reject evidence)", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning (Summary).md", r"subgraph Epoch\[", "epoch mermaid (covered subject)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"computing all gradients via reverse-mode automati", "gradients via reverse mode (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"failed for networks deeper than 3-4 layers", "networks deeper prose (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"Era 1: Deeper", "era 1 deeper (covered subject)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"Randomly crop 224×224", "randomly crop comment (reject evidence)", False),
    ("master-ai", "15 - AI Agents/Tool Calling/04 - Function Calling.md", r"Validate tool arguments server-side", "server-side validation (reject evidence)", False),
    ("master-ai", "19 - MCP/Architecture/01 - MCP Overview.md", r"Server-side composition", "server-side composition (reject evidence)", False),
    ("master-ai", "19 - MCP/Security/03 - MCP Security.md", r"MCP sits at the intersection of two trust boundaries", "mcp trust boundaries (covered subject)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"train_dir = data_dir / 'train'", "train dir path (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"val_dir = data_dir / 'val'", "val dir path (reject evidence)", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"multi-vector embeddings are 5–10x larger than single-vector", "10x larger prose (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"the filter slides across the entire input", "filter slides def (covered subject)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"Update model parameters using the computed gradients", "model parameters comment (reject evidence)", False),
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"Trying multiple approaches", "cot multiple approaches (reject evidence)", False),
    ("master-ai", "24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md", r"trying multiple approaches", "ttc multiple approaches (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"Train Acc: \{train_acc", "train acc print (reject evidence)", False),
    ("master-ai", "25 - Frameworks and Tools/Serving/14 - SGLang.md", r"Answer directly:", "sglang answer directly (reject evidence)", False),
    ("master-ai", "09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md", r"learns to produce the answer directly", "distillation answer directly (reject evidence)", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"ColPali's key innovation", "colpali possessive (reject evidence)", False),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"^# 48", "colpali note title (covered base)", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"Epoch summary", "epoch summary comment (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"the final layer is called 'fc' \(fully connected\)", "fc attribute def (covered subject)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"model\.fc\.in_features", "fc attribute api (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"Compute gradients via backpropagation", "gradients via backprop comment (reject evidence)", False),
    ("master-ai", "15 - AI Agents/Reasoning/02 - Chain-of-Thought.md", r"Let's think step by step", "cot trigger phrase (covered subject)", False),
    ("master-ai", "15 - AI Agents/Reasoning/06 - Tree of Thoughts and Self Consistency.md", r"Let's think step by step", "cot trigger in tot code", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"Max pooling is a non-linear operation that selects the maximum value", "max pooling definition (covered subject)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/07. Inception Architecture Deep Dive.md", r"Max pooling selects the maximum activation", "max pooling selects prose (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"class MNISTNet\(nn\.Module\)", "mnistnet class (reject evidence)", False),
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"The target model verifies the tree", "target verifies (reject evidence)", False),
    ("master-ai", "20 - AI Infrastructure/Compute/04 - GPU Infrastructure and Sizing.md", r"model proposes tokens; the large model verifies", "large model verifies (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"Move images to GPU", "move images fix (reject evidence)", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"Move labels to GPU", "move labels fix (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/05. Forward Propagation and Activation Functions.md", r"our network's guess", "network's guess prose (reject evidence)", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/01. Backpropagating to the Output Layer.md", r"our network's guess", "network's guess prose 2 (reject evidence)", False),
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
