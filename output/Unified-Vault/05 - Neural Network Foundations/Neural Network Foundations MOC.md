---
title: Neural Network Foundations MOC
type: overview
aliases: [Neural Networks MOC, NN Foundations MOC, Neural Networks Map of Content]
tags: [neural-networks, moc, deep-learning, foundations]
sources:
  - "04 — Neural Networks MOC"
created_index: 15
---

This map of content organizes the neural network foundations area: the building blocks of deep learning (perceptrons, MLPs, activations, backpropagation) and the pre-Transformer architectures (CNNs, RNNs, Seq2Seq) that motivate attention. It is the entry point for the area and lists every note in a recommended reading order. This area is the bridge from classical machine learning to deep learning: everything a modern Transformer stack does is built from the components collected here.

## Reading order

| # | Note | Sub-family | Purpose |
|---|---|---|---|
| 01 | [[Perceptrons and Multi-Layer Perceptrons]] | Basics | The universal function approximator: from the single perceptron to the MLP. |
| 02 | [[Artificial Neural Networks]] | Basics | The unified overview: formal neuron, architecture, training loop, curve fitting. |
| 03 | [[Activation Functions]] | Basics | ReLU, tanh, sigmoid, softmax and beyond — nonlinearity is what makes depth meaningful. |
| 04 | [[Forward Propagation]] | Basics | The forward pass: mathematics, worked example, code and matrix formulation. |
| 05 | [[Neural Network Architecture and Notation]] | Basics | Architecture components and the notation conventions used across the area. |
| 06 | [[Data Preparation for Neural Networks]] | Basics | Cleaning, scaling, splits and the practical MLP-implementation guide. |
| 07 | [[Backpropagation]] | Backpropagation | The algorithm that trains every network — full derivation from output layer to hidden layers. |
| 08 | [[Matrix Implementation of Backpropagation]] | Backpropagation | The matrix form and the delta-weight formula that make backprop practical. |
| 09 | [[05 - Neural Network Foundations/Backpropagation/Backpropagation and Gradient Flow in CNNs\|Backpropagation and Gradient Flow in CNNs]] | Backpropagation | How gradients flow through convolutional and pooling layers. |
| 10 | [[Formal Neuron Lab]] | Labs | Hands-on: implement the formal neuron and visualize activation functions. |
| 11 | [[Data Cleaning and Encoding Lab]] | Labs | Hands-on: clean, normalize and encode a raw dataset for training. |
| 12 | [[Convolutional Neural Networks]] | Architectures | Convolutions, locality, translation invariance, ResNet — the vision foundation. |
| 13 | [[Recurrent Neural Networks]] | Architectures | Sequence modeling before Transformers: vanilla RNN, LSTM and GRU gating. |
| 14 | [[Seq2Seq and the Information Bottleneck]] | Architectures | The encoder-decoder fixed-vector bottleneck that attention was invented to fix. |
| 15 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization\|Weight Initialization]] | Training dynamics | Xavier and He schemes; bad initialization means no training at all. |
| 16 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients\|Vanishing and Exploding Gradients]] | Training dynamics | Why deep networks are hard to train and how the fixes work. |
| 17 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization\|Batch Normalization]] | Training dynamics | Internal covariate shift, the four-step math, train/eval modes and the alternatives. |
| 18 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization\|Dropout and Regularization]] | Training dynamics | Dropout mechanics and math plus the weight-penalty family. |
| 19 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation\|Data Augmentation]] | Training dynamics | The transform catalog and the training/validation pipeline discipline. |
| 20 | [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration\|Hyperparameters and Network Configuration]] | Training dynamics | Architectural and training hyperparameters, scaling rules and tuning strategies. |

## Sub-families

- **Basics** — notes 01–06: the neuron, the layer, activations, the forward pass, notation and data preparation. Read these before anything else in the area.
- **Backpropagation** — notes 07–09: the training algorithm from its scalar derivation to its matrix implementation and its convolutional special case.
- **Labs** — notes 10–11: two hands-on labs that turn the basics into working code.
- **Architectures** — notes 12–14: the three pre-Transformer architecture families and their failure modes.
- **Training dynamics and stability** — notes 15–20: initialization, gradient pathologies, normalization, regularization, augmentation and hyperparameter discipline — everything that keeps training stable.

## Why this area matters

Modern Transformers are "just" stacked neural network layers with a clever routing mechanism (attention). To understand Transformers, you need to understand:

- What a neural layer is (perceptron → MLP).
- How training works (backpropagation + an optimizer).
- Why deep networks are hard (vanishing and exploding gradients).
- What came before (RNNs, CNNs, Seq2Seq) — and why attention was invented to fix their problems.

## Where to go next

The adjacent areas pick up exactly where this one ends: the mathematics behind networks (calculus and linear algebra used by backpropagation), the classical machine learning background (gradient descent, regularization, evaluation), and the attention mechanisms and language-model areas that turn these foundations into modern sequence models. [[Machine Learning MOC]] is the closest neighbor and assumes the same vocabulary.

## See also

- [[Perceptrons and Multi-Layer Perceptrons]] — start here if you are new to neural networks.
- [[Backpropagation]] — the heart of the area.
- [[Recurrent Neural Networks]] — the sequence-modeling background for attention.
- [[Machine Learning MOC]] — the classical-ML foundation this area builds on.
- [[Mathematics MOC]]
- [[NLP and Language Models MOC]]
- [[Attention and Transformers MOC]]
