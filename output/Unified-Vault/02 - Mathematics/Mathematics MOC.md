---
title: Mathematics MOC
type: overview
aliases: [Mathematics Map of Content, Math MOC, Mathematics Area Map]
tags: [moc, mathematics, navigation]
sources:
  - "MOC"
created_index: 10
---

This map of content organizes the Mathematics area: linear algebra, probability, calculus, optimization, information theory, and statistics. It is the entry point for the area and lists every note in a recommended reading order. These are the mathematical foundations for AI engineering — skip them at your own risk, because every subsequent area depends on this one.

## Reading order

| # | Note | Sub-domain | Purpose |
|---|---|---|---|
| 01 | [[Vectors]] | Linear Algebra | The fundamental object. |
| 02 | [[Dot Product]] | Linear Algebra | The most important operation. |
| 03 | [[Cosine Similarity]] | Linear Algebra | Direction-only similarity. |
| 04 | [[Matrix Multiplication]] | Linear Algebra | The workhorse of deep learning. |
| 05 | [[Matrix Decomposition]] | Linear Algebra | SVD, eigendecomposition, PCA. |
| 06 | [[Tensors and Broadcasting]] | Linear Algebra | Multi-dim arrays; clean vectorized code. |
| 07 | [[Probability Essentials]] | Probability | Distributions, MLE, MAP. |
| 08 | [[Bayes Theorem]] | Probability | Updating beliefs; generative vs discriminative. |
| 09 | [[Gaussian Distribution]] | Probability | Why Gaussians are everywhere; CLT; max entropy. |
| 10 | [[Gradient and Chain Rule]] | Calculus | Foundation of backprop. |
| 11 | [[02 - Mathematics/Calculus/Jacobians and Hessians\|Jacobians and Hessians]] | Calculus | Multivariate derivatives; curvature. |
| 12 | [[Optimization Essentials]] | Optimization | SGD → Adam overview. |
| 13 | [[Adam Optimizer Derivation]] | Optimization | Full derivation of Adam/AdamW. |
| 14 | [[Learning Rate Schedules]] | Optimization | Warmup, cosine decay, linear scaling. |
| 15 | [[Entropy Cross-Entropy and KL Divergence]] | Information Theory | The loss function; KL as regularizer. |
| 16 | [[Estimators and Bias]] | Statistics | MLE, MAP, bias-variance, consistency. |
| 17 | [[Hypothesis Testing]] | Statistics | p-values, confidence intervals, multiple testing. |

## Sub-domains

- **Linear algebra** — notes 01–06: vectors, the operations on them, matrices, decompositions, and the tensor/broadcasting machinery that makes vectorized code possible.
- **Probability** — notes 07–09: distributions, estimation, Bayes' rule, and the Gaussian family.
- **Calculus** — notes 10–11: the gradient and the chain rule that backpropagation is built on, and their multivariate extensions.
- **Optimization** — notes 12–14: the optimizer toolbox from SGD through Adam and AdamW, and the learning-rate schedules that make training stable.
- **Information theory** — note 15: entropy, cross-entropy and KL divergence — the loss-function layer of machine learning.
- **Statistics** — notes 16–17: estimators, bias, and the hypothesis-testing machinery for evaluating experiments.

## Why this area matters

Modern AI engineering rests on a small set of mathematical ideas:

1. **Linear algebra** — every model is a stack of matrix multiplications and the operations around them.
2. **Probability and information theory** — language modeling is probability estimation; cross-entropy is the loss; KL divergence is the regularizer.
3. **Calculus** — backpropagation is the chain rule applied to a computation graph.
4. **Optimization** — training is gradient descent (and its variants).
5. **Statistics** — evaluating experiments (is model A really better than model B?) requires hypothesis testing.

If you can re-derive [[Scaled Dot-Product Attention|scaled dot-product attention]] on a whiteboard, you have enough math. If you can't, this area is for you.

## Where to go next

- **After linear algebra** (notes 01–06): the neural-network area is immediately accessible — neural networks are linear algebra plus calculus plus optimization.
- **After probability and information theory** (notes 07–09, 15): the machine-learning area's evaluation and generalization notes, and the sequence-modeling area's language-modeling notes, become readable.
- **After optimization** (notes 12–14): the training area (pretraining, fine-tuning) builds directly on Adam, AdamW and the learning-rate schedules.

## See also

- [[Foundations MOC]] — the orientation area this map is reached from.
- [[Machine Learning MOC]] — applies these foundations to classical learning.
- [[Neural Network Foundations MOC]] — neural networks = linear algebra + calculus + optimization.
- [[Attention and Transformers MOC]] — attention = dot products + softmax.
