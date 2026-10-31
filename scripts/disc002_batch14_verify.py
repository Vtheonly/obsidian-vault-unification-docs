#!/usr/bin/env python3
"""Targeted corpus verification for batch-14 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list, so a Python comment inside a code fence can no
longer pass as a heading citation.

Session-13/14 lessons applied: heading LEVELS checked exactly (## vs ###),
note titles that differ from filenames, **bold** markers inside patterns,
term-separated definitions, the glossary indexes checked before any
acronym-absence claim, and regex-vs-LaTeX escaping (in a regex, \\t means
TAB and \\c is a bad escape — literal '\\times'/'\\vdots' need '\\\\times'/
'\\\\vdots' inside patterns; \\* is needed for literal asterisks).
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
    # --- covers: bounding boxes family (#1) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"\| \*\*Object detection\*\* \| Bounding boxes \+ labels \|", "object detection task table", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"^#+ Object Detection", "object detection heading", True),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/05. Computer Vision Metrics - IoU, mAP, Dice.md", r"IoU measures the overlap between a predicted bounding box and a ground-truth bounding box", "iou bounding box def", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/05. Computer Vision Metrics - IoU, mAP, Dice.md", r"^#+ Object detection metrics", "object detection metrics heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md", r"class labels \(or bounding boxes, or segmentation masks\) as output", "bounding boxes in output list", False),
    # --- covers: conditional generation family (#2) ---
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. The Encoder-Decoder Pattern - Conditional Generation.md", r"^#+ 01\. The Encoder-Decoder Pattern", "conditional generation note title", True),
    ("ai-course", "07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. The Encoder-Decoder Pattern - Conditional Generation.md", r"the conceptual bridge from .RNNs that classify sequences. to .RNNs that generate sequences.", "conditional generation bridge", False),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/03. Score-Based and Latent Diffusion.md", r"^#+ Conditional generation: text-to-image", "diffusion conditional generation heading", True),
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/01. The Encoder-Decoder Design Space - BERT vs GPT vs T5.md", r"\(the RNN version of this design space\)", "design space rnn version link", False),
    # --- rejects: different results family (#3) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"stochastic \(different runs produce different results\) and suboptimal", "dropout stochastic prose", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"Each evaluation gives different results because neurons are randomly dropped", "eval dropout warning", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"Mistake 6: Not Setting Random Seed", "random seed mistake heading", False),
    # --- covers: loss curve family (#4) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"plotting the loss\. The optimal learning rate is typically near the steepest point of the loss curve", "lr range test loss curve", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"how noisy the validation loss curve is", "validation loss curve noise", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/01. Gradient Descent Optimization (DL Course).md", r"monitor the loss curve for plateau behavior", "loss curve plateau monitoring", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/01. Gradient Descent Optimization (DL Course).md", r"the loss curve will look like a seismograph reading", "sgd seismograph", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"Sudden spikes in the loss curve", "loss curve spikes", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"The loss curve looks like a seismograph reading during an earthquake", "exploding seismograph", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"The loss curve will show violent oscillations", "init oscillations", False),
    ("ai-course", "07 - Sequence Models and RNNs/07.1 - Motivation and Recurrence/04. The Vanishing and Exploding Gradient Problem in RNNs.md", r"the loss curve suddenly spikes to `NaN`", "rnn loss curve nan", False),
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"Diagnosing Bias vs Variance with Learning Curves", "learning curves diagnostic", False),
    ("master-ai", "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md", r"the \*\*learning curve\*\*: plot train and validation error as a function of training set si", "learning curve def", False),
    # --- rejects: visual information family (#5) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/07. Inception Architecture Deep Dive.md", r"^#+ The Legacy: Multi-Scale Processing and Dimensionality Reduction", "multi-scale heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/04. VGG and Classic Architectures - Summary.md", r"visual information exists at multiple scales", "multi-scale visual info", False),
    ("ai-course", "06 - Image Processing/03. Spatial Filtering and Neighborhood Processing/3.9 Image Pyramids and Multi-Scale Representation.md", r"Pyramids are the data structure for any algorithm that needs to handle objects at multiple scales", "pyramids multi-scale", False),
    # --- rejects: answer questions family (#6) ---
    ("master-ai", "09 - Foundation Models/Multimodal/05 - Multimodal Foundation Models.md", r"\*\*VQA\*\* \(Visual Question Answering\): answer questions about images", "vqa gloss", False),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"answer questions, and perform various la", "llm capability prose", False),
    # --- covers: causality family (#7) ---
    ("master-ai", "14 - Interpretability/Mechanistic/04 - Activation Patching and Causal Tracing.md", r"gold standard for establishing \*\*causality\*\* in interpretability", "activation patching causality", False),
    ("master-ai", "14 - Interpretability/Probing/05 - Probing.md", r"^#+ Correlation, Not Causation", "probing correlation heading", True),
    ("master-ai", "14 - Interpretability/Mechanistic/02 - Logit Lens and Tuned Lens.md", r"Doesn't Explain Causation", "logit lens causation", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/03. Linear Regression (DL Perspective).md", r"Requires linear correlation and causality between X and Y", "regression causality assumption", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/03. Linear Regression (DL Perspective).md", r"relationship \(correlation/causality\) between an Exogenous", "regression correlation causality", False),
    ("master-ai", "08 - LLMs/Architecture/01 - Decoder-Only Architecture.md", r"^#+ The Causal Mask", "causal mask heading", True),
    # --- covers: encoder-decoder models family (#8) ---
    ("master-ai", "00 - Vault Management/Master Roadmap.md", r"^#+ Encoder-Decoder Models", "roadmap enc-dec heading", True),
    ("master-ai", "07 - Transformers/Encoder-Decoder Models/12 - T5 and BART.md", r"^#+ Why Encoder-Decoder\?", "why enc-dec heading", True),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"used an \*\*encoder-decoder RNN\*\*", "enc-dec rnn def", False),
    ("master-ai", "07 - Transformers/Architecture/01 - Transformer Block.md", r"^#+ Encoder-decoder block \(T5, BART\)", "enc-dec block variant heading", True),
    # --- rejects: image content family (#9) ---
    ("master-ai", "23 - Multimodal AI/Vision-Language/03 - LLaVA.md", r"LLaVA hallucinates image content", "llava hallucination", False),
    ("master-ai", "08 - LLMs/Limitations/05 - Hallucination.md", r"^#+ Why LLMs Hallucinate", "hallucination heading", True),
    # --- rejects: large errors family (#10) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Squaring penalizes large errors exponentially more than s", "squaring penalizes", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/02. Linear Regression from Scratch.md", r"\*\*Penalizes Large Errors:\*\* Squaring disproportionately punishes outliers", "penalizes large errors", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/02. Loss Functions and Cost Optimization.md", r"This quadratic penalty means the model will prioritize fixing the largest errors firs", "quadratic penalty", False),
    # --- rejects: local structure family (#11) ---
    ("ai-course", "03 - Machine Learning/03.8 - Dimensionality Reduction/01. Principal Component Analysis (PCA).md", r"PCA preserves global variance, not local neighborhoods", "pca global not local", False),
    ("ai-course", "03 - Machine Learning/03.8 - Dimensionality Reduction/02. t-SNE and UMAP.md", r"they preserve local neighborhoods", "tsne local neighborhoods", False),
    # --- rejects: pure transformers family (#12) ---
    ("master-ai", "26 - Papers/2024-2026/41 - Jamba 2024.md", r"^#+ Comparison with Pure SSMs and Pure Transformers", "pure comparison heading", True),
    ("master-ai", "26 - Papers/2024-2026/41 - Jamba 2024.md", r"pure Transformers are typically faster", "pure transformers faster", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/05. Evolution of CNN Architectures.md", r"use hybrid architectures with convolutional front-ends and Transformer back-ends", "hybrid architectures", False),
    # --- rejects: semantically meaningful family (#13) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture and Philosophy.md", r"highly abstract and semantically meaningful", "semantic features prose", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/02. Hierarchical Feature Extraction.md", r"^#+ Layer 3\+ — High-Level Features", "high-level features heading", True),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"^#+ 4\. Hierarchical features", "hierarchical features heading", True),
    # --- covers: sora family (#14) ---
    ("master-ai", "23 - Multimodal AI/Vision-Language/01 - Multimodal AI Overview.md", r"^#+ Sora \(OpenAI, 2024\)", "sora heading", True),
    ("master-ai", "23 - Multimodal AI/Vision-Language/01 - Multimodal AI Overview.md", r"Text-to-video generation\. Minutes-long, high quality\.", "sora gloss", False),
    ("master-ai", "23 - Multimodal AI/Diffusion/05 - DiT and FLUX.md", r"\*\*Sora\*\* \(OpenAI's video generation model\) uses a DiT-based architecture", "sora dit gloss", False),
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"Sora \(video generation, 2024\)", "sora timeline entry", False),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/03. Score-Based and Latent Diffusion.md", r"\*\*Video generation:\*\* Sora, Runway Gen-3, Kling", "video generation list", False),
    ("ai-course", "10 - Generative Models/10.4 - Diffusion Models/03. Score-Based and Latent Diffusion.md", r"used in Sora and SD3", "dit sora sd3", False),
    # --- rejects: every spatial / every spatial position family (#15, #28) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"applied at every spatial position of the input", "weight sharing def", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"^#+ Weight Sharing: Translation Equivariance and Parameter Savings", "weight sharing heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/01. Local Connectivity and Parameter Sharing.md", r"^#+ 4\.1 Local Connectivity and Parameter Sharing", "parameter sharing note title", True),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"Weight sharing means the same kernel is applied at every spatial position", "cnn weight sharing q", False),
    # --- rejects: goodfellow et / et al family (#16, #17) ---
    ("ai-course", "10 - Generative Models/10.3 - GANs/01. The Adversarial Game - Generator vs Discriminator.md", r"\(Goodfellow et al\. 2014\) frames generation as a", "goodfellow gan attribution", False),
    ("master-ai", "02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md", r"Goodfellow et al\., \*Deep Learning\* — Chapter 6\.5", "goodfellow textbook ref", False),
    ("master-ai", "02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md", r"Goodfellow et al\., \*Deep Learning\* — Chapter 3", "goodfellow ch3 ref", False),
    # --- covers: low-rank approximation family (#18) ---
    ("master-ai", "02 - Mathematics/Linear Algebra/05 - Matrix Decomposition.md", r"^#+ Low-Rank Approximation: The Magic of SVD", "low-rank heading", True),
    ("master-ai", "02 - Mathematics/Linear Algebra/04 - Matrix Multiplication.md", r"\*\*Low-rank approximation\*\* \(SVD, LoRA\): truncate the sum to the top-\$r\$ terms", "low-rank matmul def", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"\*\*Low-rank approximation\*\*: truncating SVD to the top \$k\$ singular values gives the best rank-\$k\$ approximat", "low-rank svd def", False),
    ("master-ai", "12 - Fine-Tuning/PEFT/01 - LoRA.md", r"^#+ LoRA \(Low-Rank Adaptation\)", "lora note title", True),
    # --- covers: manhattan distance family (#19) ---
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"d\(x, y\) = \\sum_\{i=1\}\^\{n\} \|x_i - y_i\|", "manhattan formula", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"^#+ 2\. Manhattan Distance \(\$L\^1\$ Norm\)", "manhattan heading", True),
    ("ai-course", "06 - Image Processing/01. Fundamentals of Digital Images/1.6 Pixel Relationships and Distance Metrics.md", r"^#+ B\. City-Block Distance \(\$D_4\$ or Manhattan\)", "city-block heading", True),
    ("master-ai", "02 - Mathematics/Linear Algebra/01 - Vectors.md", r"L1 is the Manhattan \(taxicab\) distance — the sum of absolute coordinate differences", "l1 manhattan gloss", False),
    # --- rejects: modern long-context family (#20, #48) ---
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md", r"Modern long-context models \(128K-2M tokens\) claim to use long context effectively", "modern long-context ppl", False),
    ("master-ai", "26 - Papers/Efficient Attention/18 - Longformer 2020.md", r"Modern long-context models use additional techn", "modern long-context longformer", False),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/02. Positional Encoding - Injecting Order Into a Set.md", r"converged on relative-position encodings \(RoPE, ALiBi\) for modern long-context models", "rope alibi convergence", False),
    # --- rejects: modern models family (#21) ---
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/04. The Transformer Decoder Block - Masking and Cross-Attention.md", r"many modern models \(GPT, LLaMA\) are \*\*decoder-only\*\*", "modern models decoder-only", False),
    ("master-ai", "07 - Transformers/Architecture/01 - Transformer Block.md", r"most modern models have a final LayerNorm/RMSNorm after the last block", "final norm modern models", False),
    # --- covers: non-contiguous family (#22) ---
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"tensors become non-contiguous\. Operations like `view` require contiguous tensors", "non-contiguous def", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"^#+ Contiguity rules of thumb", "contiguity rules heading", True),
    ("master-ai", "02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md", r"^#+ Memory Layout", "memory layout heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md", r"Channels are non-contiguous in spatial memory", "nchw non-contiguous", False),
    # --- covers: parameter update family (#23) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/06. Transfer Learning and ResNet - Summary.md", r"^#+ 1\.4\.5 Parameter Update \(Gradient Descent\)", "param update heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/03. Hyperparameters and Basic PyTorch - Summary.md", r"^#+ The Adam Parameter Update", "adam param update heading", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"is an optimization algorithm that uses the gradient to minimize a function\. The update rule:", "update rule def", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"The core update rule is:", "core update rule", False),
    # --- rejects: small weights family (#24) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"small weights, each layer essentially multiplies its input by a very small number", "small weights collapse", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"Small weights cause vanishing", "small weights vanishing", False),
    # --- rejects: state across family (#25) ---
    ("master-ai", "04 - Neural Networks/Architectures/04 - RNN LSTM GRU.md", r"maintaining a hidden state across timesteps", "rnn hidden state", False),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/05. The Full Transformer - Assembling the Pieces.md", r"no persistent state across sequences", "transformer statelessness", False),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"shard state across GPUs", "optimizer state sharding", False),
    # --- rejects: across runs family (#26) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"This ensures reproducible results across runs on the same hardware", "reproducible across runs", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"deterministic and comparable across runs", "deterministic across runs", False),
    # --- rejects: correct answers family (#27) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"\*\*`targets`\*\*: The known, correct answers \(labels\)", "targets correct answers", False),
    ("ai-course", "01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/01. Introduction to Machine Learning.md", r"the .Ground Truth. or the correct answers in a training set come from human experts", "ground truth tip", False),
    # --- rejects: exponential moving family (#29) ---
    ("master-ai", "02 - Mathematics/Optimization/13 - Adam Derivation.md", r"is the exponential moving average of squared gradients", "adam ema def", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"The velocity is an exponential moving average of past gradients", "momentum ema def", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"via exponential moving avera", "batchnorm ema", False),
    # --- covers: input space family (#30) ---
    ("ai-course", "03 - Machine Learning/03.4 - Support Vector Machines (SVM)/06. The Kernel Trick.md", r"Project the data from the current space \(Input Space\) into a higher-dimensional space \(Feature Space\)", "input space def", False),
    ("ai-course", "03 - Machine Learning/03.4 - Support Vector Machines (SVM)/06. The Kernel Trick.md", r"A\[2D Input Space\]", "input space mermaid", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/02 - Dot Product.md", r"The .kernel trick. lets us compute in feature space without explicitly mapping to it", "kernel trick dot product", False),
    ("master-ai", "02 - Mathematics/Linear Algebra/02 - Dot Product.md", r"defines a \*\*hyperplane\*\* in input space", "hyperplane input space", False),
    # --- covers: lr scheduler family (#31) ---
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^#+ 14 - Learning Rate Schedules", "lr schedules note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"^#+ Step 3\.3: Learning Rate Scheduler", "lr scheduler step heading", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"^#+ ReduceLROnPlateau: The Most Practical Scheduler", "reducelronplateau heading", True),
    # --- covers: neural network architecture family (#32) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural Network Architecture and Notation.md", r"^#+ 3\. Neural Network Architecture and Notation", "nn architecture note title", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/01. Fundamentals of Neural Networks.md", r"^#+ 2\. Neural Network Architecture", "nn architecture heading", True),
    # --- rejects: produces garbage family (#33) ---
    ("ai-course", "10 - Generative Models/00. Chapter Overview.md", r"sampling a random latent vector usually produces garbage", "ae garbage prose", False),
    ("ai-course", "10 - Generative Models/10.1 - Autoencoders/01. The Autoencoder - Compression as Learning.md", r"autoencoders cannot generate new examples, because their latent space is not a nice di", "ae limitation", False),
    # --- rejects: radford et / et al family (#34, #35) ---
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/04. ViT Architecture and Design Decisions.md", r"\*\*CLIP\*\* \(Radford et al\. 2021\): co-train an image encoder", "clip radford attribution", False),
    ("ai-course", "10 - Generative Models/10.3 - GANs/01. The Adversarial Game - Generator vs Discriminator.md", r"A standard DCGAN \(Deep Convolutional GAN, Radford et al\. 2015\)", "dcgan radford attribution", False),
    ("master-ai", "26 - Papers/LLMs/15 - GPT-2 2019.md", r"^#+ 15 — GPT-2 \(Radford et al\., 2019\)", "gpt2 paper title", True),
    ("master-ai", "23 - Multimodal AI/Vision-Language/02 - CLIP.md", r"^#+ 02 — CLIP", "clip note title", True),
    # --- rejects: times 4096 family (#36) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md", r"7 \\times 7 \\times 512 \\times 4096 = 102", "times 4096 artifact", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/02. The Mathematics of Receptive Fields and 1x1 Convolutions.md", r"27 \\times 4096 \+ 192 = 110", "times 4096 receptive field", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md", r"25088 \\times 4096 \+ 4096 =", "vgg16 fc6 table", False),
    # --- covers: transformer blocks family (#37) ---
    ("master-ai", "07 - Transformers/Architecture/01 - Transformer Block.md", r"^#+ Transformer Block", "transformer block heading", True),
    ("master-ai", "08 - LLMs/Architecture/01 - Decoder-Only Architecture.md", r"a stack of Transformer blocks with \*\*causal\*\* self-attention", "stack of blocks def", False),
    ("master-ai", "07 - Transformers/Components/05 - Feed-Forward Network Deep.md", r"the .computation. half of every Transformer block", "ffn half of block", False),
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/04. ViT Architecture and Design Decisions.md", r"Dropout is applied \*inside\* the Transformer blocks", "vit dropout placement", False),
    # --- rejects: 16 patches family (#38) ---
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/01. From Words to Patches - How ViT Tokenizes an Image.md", r"For ViT-Base with 224×224 images and 16×16 patches: \$N\+1 = 197\$ tokens", "vit-base patches", False),
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/04. ViT Architecture and Design Decisions.md", r"^#+ 6\. Why 16×16 patches\?", "why 16 patches heading", True),
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/01. From Words to Patches - How ViT Tokenizes an Image.md", r"The choice of patch size \$P\$ is the key hyperparameter of a ViT", "patch size tradeoff", False),
    ("master-ai", "26 - Papers/Transformers/21 - Vision Transformer ViT 2020.md", r"^#+ Patches Make Attention Tractable", "patches tractable heading", True),
    # --- rejects: across multiple gpus family (#39) ---
    ("master-ai", "11 - Training/Distributed Training/02 - Distributed Training.md", r"shard the model across multiple GPUs", "shard across gpus", False),
    ("master-ai", "08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md", r"distribute the KV cache across multiple GPUs", "kv cache across gpus", False),
    # --- rejects: add positional family (#40) ---
    ("master-ai", "07 - Transformers/Components/06 - Embedding Layer.md", r"Add positional encoding \(if not using RoPE\)", "add positional comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"project these patches into 1D embeddings, add positional encodings", "vit pipeline summary", False),
    # --- rejects: attended family (#41) ---
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/03. From RNNs to Attention - The Historical Bridge.md", r"The Bahdanau attention was \*\*cross-attention\*\*: the decoder attended to the encoder", "decoder attended encoder", False),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/01. Self-Attention - When the Sequence Attends to Itself.md", r"a decoder attended to an encoder", "self-attention note prose", False),
    # --- rejects: frees family (#42) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"PyTorch frees \(deletes\) the computational graph after the backward pass", "frees computational graph", False),
    ("master-ai", "13 - Inference/KV Cache/02 - PagedAttention.md", r"recompute its KV when memory frees", "pagedattention memory frees", False),
    # --- covers: gradient explosion family (#43) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"^#+ 15\. The Vanishing and Exploding Gradient Problems", "vanishing exploding note title", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"^#+ 14\.3\.2 Gradient Explosion", "gradient explosion heading", True),
    ("master-ai", "04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md", r"^#+ 08 - Vanishing and Exploding Gradients", "master-ai vanishing exploding title", True),
    ("master-ai", "04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md", r"^#+ Exploding gradient", "exploding gradient heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md", r"^#+ The Exploding Gradient Problem", "exploding gradient problem heading", True),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"^#+ Gradient Clipping", "gradient clipping heading", True),
    # --- rejects: gradient points family (#44) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"the gradient points toward steepest \*ascent\* \(maximum error\)", "gradient points ascent", False),
    ("ai-course", "03 - Machine Learning/03.1 - Regression/02. Linear Regression from Scratch.md", r"the gradient points uphill \(direction of steepest ascent\)", "gradient points uphill", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"The gradient points in the direction of steepest ascent, so subtracting it", "gradient points deep dive", False),
    # --- rejects: learn different family (#45) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"to break symmetry \(so neurons learn different features\)", "symmetry breaking features", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural Network Architecture and Notation.md", r"the gradients would also be identical", "identical gradients", False),
    # --- covers: ml engineer family (#46) ---
    ("master-ai", "01 - AI Foundations/05 - AI Engineer Roles.md", r"^#+ ML Engineer", "ml engineer heading", True),
    ("ai-course", "01 - Foundations and Overview/01.3 - Data Science Foundations/05. Careers and Roles in the Data Ecosystem.md", r"^#+ 4\. Machine Learning Engineer", "ml engineer careers heading", True),
    ("ai-course", "01 - Foundations and Overview/01.3 - Data Science Foundations/05. Careers and Roles in the Data Ecosystem.md", r"\*\*ML Engineer\*\* \| Production & Scalability", "ml engineer role table", False),
    ("ai-course", "01 - Foundations and Overview/01.3 - Data Science Foundations/07. Exercise 1 - Identifying Applications and Roles.md", r"An \*\*ML Engineer\*\* is focused on the \*\*deployment and optimization\*\* of models", "ml engineer exercise reasoning", False),
    # --- rejects: model families family (#47) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"Different PyTorch model families use different names for their classification head", "model families heads", False),
    ("master-ai", "09 - Foundation Models/Code Models/04 - Code Models.md", r"^#+ The Major Code Model Families", "code model families heading", True),
    # --- rejects: network architectures family (#49) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"family of deep convolutional neural network architectures introduced to make very deep networks trainable", "resnet family prose", False),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"^#+ The Evolution of CNN Architectures", "cnn evolution heading", True),
    # --- covers: scalar loss family (#50) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"returns a single scalar value that represents the total error across the training data", "scalar loss def", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"neural networks always have a scalar loss and millions of parameters", "scalar loss reverse-mode", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"define a scalar loss function \$\\mathcal\{L\}", "scalar loss function def", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/07. Multi-Layer Perceptron and Backpropagation.md", r"This single number quantifies how wrong the entire network is", "single number loss", False),
    # --- rejects: scales better family (#51) ---
    ("ai-course", "08 - Attention and Transformers/08.3 - Vision Transformers/01. From Words to Patches - How ViT Tokenizes an Image.md", r"it scales better with data", "vit scales with data", False),
    ("ai-course", "08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/04. Choosing the Right Architecture for the Task.md", r"simpler, scales better, any text as training data", "decoder-only scales", False),
    ("master-ai", "26 - Papers/Transformers/14 - GPT-1 2018.md", r"Decoder-only scales better", "gpt1 decoder scales", False),
    # --- rejects: sequence attends family (#52) ---
    ("ai-course", "07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/03. From RNNs to Attention - The Historical Bridge.md", r"what if a sequence attends to itself\?", "sequence attends question", False),
    ("ai-course", "08 - Attention and Transformers/08.2 - The Transformer Architecture/01. Self-Attention - When the Sequence Attends to Itself.md", r"^#+ 01\. Self-Attention — When the Sequence Attends to Itself", "self-attention note title", True),
    ("master-ai", "06 - Attention Mechanisms/Origins/01 - Origins of Attention.md", r"Self-attention \(Transformer 2017\): a sequence attends to itself", "origins self-attention def", False),
    # --- rejects: single hidden family (#53) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/01. Fundamentals of Neural Networks.md", r"get a value out of a single hidden node", "single hidden node", False),
    ("master-ai", "06 - Attention Mechanisms/Origins/02 - Bahdanau Attention.md", r"a small feedforward network with a single hidden layer", "bahdanau single hidden", False),
    ("master-ai", "04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md", r"^#+ Why Hidden Layers\?", "why hidden layers heading", True),
    # --- rejects: use linear family (#54) ---
    ("master-ai", "14 - Interpretability/Probing/05 - Probing.md", r"The convention in modern interpretability is to use linear probes", "linear probes convention", False),
    ("ai-course", "06 - Image Processing/04. Frequency Domain and Restoration/4.4 Image Degradation and Noise Models.md", r"use linear filters \(Gaussian low-pass\)", "linear filters usage", False),
    # --- rejects: use relu family (#55) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md", r"Use ReLU to fix", "use relu memory aid", False),
    ("master-ai", "04 - Neural Networks/Foundations/02 - Activation Functions.md", r"^#+ The ReLU Family", "relu family heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"ReLU is the foundational innovation that makes deep learning possible", "relu foundational", False),
    # --- rejects: vdots family (#56) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md", r"\\vdots \\\\ x_n", "vdots vector artifact", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/08. Multivariate Calculus - Jacobians and Hessians.md", r"\\vdots & \\ddots & \\vdots", "vdots jacobian artifact", False),
    # --- rejects: every row family (#57) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"// Step 2: Loop through every row", "every row loop comment", False),
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"distance between the New Animal and every row in the Training Table", "knn every row", False),
    # --- rejects: model saved family (#58) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"New best model saved! Val Acc", "model saved print", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"Save to a file\. Overwrites the previous best", "checkpoint save comment", False),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"\*\*Checkpoint selection\*\*: save checkpoints periodically and validate", "checkpoint selection", False),
    # --- rejects: 1000-class family (#59) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"Replace the 1000-class FC with a 10", "1000-class fc replace", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md", r"Replace 1000-class output with our", "1000-class output replace", False),
    # --- rejects: 51cf66 family (#60) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"style D fill:#51cf66", "51cf66 artifact init", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"fill:#51cf66", "51cf66 artifact vanishing", False),
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
