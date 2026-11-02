---
title: CNN Course Overview
type: overview
aliases:
  - CNN Course
  - Convolutional Neural Networks Course
  - "Course: Convolutional Neural Networks (The Complete Vault)"
  - CNN Course Map
tags:
  - cnn
  - convolutional-neural-networks
  - computer-vision
  - course-overview
  - reading-order
  - orientation
sources:
  - "00. Course Overview"
created_index: 11
---

This note is the map of the convolutional neural networks course — the navigation entry point for the CNN side of the computer vision area. The course is one continuous progression: it starts from how a convolution learns, works through the geometry of feature maps, assembles complete architectures, and ends with training, evaluation, and interpretability in PyTorch. Every CNN-side note of the area is listed below, grouped the way the course teaches them.

## Reading order

Follow the groups in order — each builds on the concepts of the previous one. The foundations group establishes the fundamental mechanics of how filters learn. The core operators then explain how spatial dimensions change, through the output-dimension formula, padding, and strides, and how pooling downsamples feature maps. The architecture group ties the operators together into complete networks: local connectivity, hierarchical features, and the classification head, followed by the full lineage of classic designs. The advanced components — $1\times1$ convolutions, global average pooling, and the modern strides-versus-max-pooling debate — are treated inside the operators notes. The training group then goes under the hood into training mechanics, and the pipeline group turns training into a repeatable, checkable workflow. For a practical learning path through all of it, follow [[CNN Mastery Roadmap]].

> [!info] Nothing was lost
> The course reached its current form through four iterative versions (Part 1–4) plus nineteen individual chapter files. All duplicates were removed, all LLM generation-loop corruptions were discarded, and all unique content was preserved and expanded — no information was lost along the way.

## Foundations and philosophy

This group answers "what is a CNN and why does it work at all": the neural-network background, the two-part architecture, and the step from hand-designed filters to filters that learn. Everything after it assumes this vocabulary.

- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — neural networks from first principles, why grid-structured images break the MLP, and the biological and historical line to the CNN.
- [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]] — the two-part design: convolutional front-end feature extractor, classifier back-end, and the modularity that makes transfer learning possible.
- [[From Basic Convolution to Learned Weights]] — the bridge from classical, hand-designed filters to filters learned by gradient descent.
- [[Demystifying Tensors - Volumes, Depth, and Data Formats]] — images and feature maps as multi-dimensional volumes; NCHW vs NHWC and how shapes flow through layers.
- [[Processing 3D Volumes, Depth Summation, and Biases]] — multi-channel convolution, the depth summation rule, and the bias term.
- [[Foundations and Philosophy Summary]] — the consolidated study guide for this group.

## Core operators and geometry

This group covers the operators that do the actual computation and the geometry they control: the convolution operation itself, the output-dimension formula, padding, strides, receptive fields and $1\times1$ convolutions, plus the two operator families that shape every modern architecture — activations and pooling.

- [[The Convolution Operation]] — filters, kernels, and feature maps; the complete mathematics of convolution, multi-channel convolution, and true convolution vs cross-correlation.
- [[Receptive Fields and 1x1 Convolutions]] — the iterative receptive-field formula with worked examples, the mathematics of stacking small filters, and what $1\times1$ convolutions actually do.
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]] — why non-linearity is essential, the ReLU family and the classical activations, and the mechanics of max and average pooling.
- [[Advanced Pooling and Global Average Pooling]] — average vs max pooling compared from first principles, global average pooling, and why GAP replaced the giant fully connected classifiers.
- [[The Output Spatial Dimension Formula]] — the output-dimension formula, with its edge cases.
- [[Padding - Mathematics, Edge Effects, and Valid vs Same]] — padding mathematics, edge effects, and valid vs same.
- [[Strides - Skipping Pixels and Downsampling]] — strided convolution, downsampling, and the strides-vs-pooling debate.
- [[Core Operators and Geometry Summary]] — the consolidated study guide for this group.

## Architecture and connectivity

This group ties the operators into complete architectures — why conv layers connect locally and share parameters, how features become hierarchical, how a network ends in a classification head — and then walks the historical lineage of designs and their deep dives.

- [[Local Connectivity and Parameter Sharing]] — the two principles, sparse local connections and shared weights, that make convolutional layers tractable, with the parameter-count proof.
- [[Hierarchical Feature Extraction]] — the level-by-level abstraction from edges to parts to objects, and why one massive layer cannot do it.
- [[The Fully Connected Layer and Flattening]] — the classification head, the flattening mechanics, and the softmax output.
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — the lineage from LeNet-5 through AlexNet, VGG, Inception, ResNet and their successors.
- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]] — the philosophy of uniformity, the mathematical case for $3\times3$ filters, and the layer-by-layer walkthrough.
- [[06 - Computer Vision/Architecture and Connectivity/Inception Architecture Deep Dive|Inception Architecture Deep Dive]] — the multi-scale parallel-filter module and the $1\times1$ bottleneck that made it affordable.
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]] — why deeper networks trained worse, and the residual-learning fix.
- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]] — basic vs bottleneck blocks, projection shortcuts, and the ResNet variant family.
- [[VGG and Classic Architectures Summary]] — the consolidated study guide for the classic architectures, with the complete PyTorch implementations.

## Training and transfer learning

This group goes under the hood into training mechanics — how gradients flow through convolutional layers, both to update the weights and to route errors back to earlier layers, and how those weights are initialized — and then turns to the practical side: building and training real models in PyTorch, where transfer learning from pre-trained backbones is the default rather than the exception.

- [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]] — why transfer learning works, and the three strategies: feature extraction, selective fine-tuning, and training from scratch.
- [[06 - Computer Vision/Training and Transfer Learning/PyTorch Implementation Basics|PyTorch Implementation Basics]] — the first end-to-end PyTorch walkthrough: data loading, `nn.Module`, and the training loop.
- [[06 - Computer Vision/Training and Transfer Learning/PyTorch Advanced - VGG16 and Pre-trained Models|PyTorch Advanced - VGG16 and Pre-trained Models]] — loading pre-trained models, freezing and replacing layers, and saving and loading state.
- [[Hyperparameters and Basic PyTorch Summary]] — the consolidated study guide: architecture hyperparameters, loss functions, optimizers, and tuning.
- [[Normalization, Regularization, and Augmentation Summary]] — the consolidated study guide: dropout, batch normalization, weight decay, and augmentation pipelines.
- [[Transfer Learning and ResNet Summary]] — the under-the-hood companion: the chain rule, hand-calculated backpropagation, gradient flow through convolutional layers, vanishing and exploding gradients, and Xavier and He weight initialization.

## Pipeline, evaluation, and interpretability

The closing group of the core course assembles everything into a complete, checkable workflow: a five-phase training pipeline, the catalog of implementation mistakes that break training silently, and the tools that show what a trained network actually learned — plus fully solved exercises.

- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]] — the five phases from data preparation to final evaluation.
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]] — the classic mistakes that most often break CNN training, each with its fix.
- [[CNN Interpretability]] — Grad-CAM and the other tools that open the black box.
- [[Scaling, Pipeline, and Interpretability Summary]] — the consolidated study guide for this stretch of the course: advanced pooling and GAP, evaluation metrics, the pipeline, the mistakes, and interpretability.
- [[CNN Solved Exercises]] — five fully solved exercises, from output dimensions and parameter counting to a complete CIFAR-10 training run.

## Advanced operators and modern tasks

Two further groups extend the course beyond the core. The advanced operators re-engineer convolution itself for efficiency and upsampling, and the modern-task notes turn to the problems beyond classification.

- [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]] — the four operator families modern architectures are built from.
- [[Detection and Segmentation]] — the levels of visual understanding, object detection, semantic segmentation, and the architecture landscape.
- [[Deep Learning for Imaging]] — the deep-learning systems, such as DnCNN and U-Net, that grew out of classical restoration work.

## See also

- [[CNN Mastery Roadmap]] — the condensed, phased learning path through this material.
- [[Image Processing Global Index]] — the classical image-processing half of the computer vision area.
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — where the course begins.
- [[The Convolution Operation]] — the operator everything else builds on.
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — the architecture lineage in one place.
