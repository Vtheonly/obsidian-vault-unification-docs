---
title: Conceptual Questions on Neural Network Fundamentals
type: example
aliases:
  - "Conceptual Questions"
  - "Qs1"
  - "Qs4"
  - "Neural Network Fundamentals Conceptual Questions"
tags:
  - deep-learning
  - quiz
  - practice
  - question-series
  - logistic-regression
  - mean-squared-error
  - log-loss
  - binary-cross-entropy
  - sigmoid
  - bias-term
  - gradient-descent
  - convexity
sources:
  - "Conceptual Questions"
  - "Qs4"
created_index: 48
---

This note collects the course's short question series on neural-network fundamentals: two conceptual questions with their full answers, one on why Mean Squared Error cannot serve as the loss for Logistic Regression and one on what the bias term contributes to a network. The questions and answers are kept complete so the series works as a quick self-check. The theory behind both answers is developed in [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]], [[Loss Functions]], and [[Activation Functions]], with wider conceptual Q&A in [[Conceptual Interview Questions]].

## Why mean squared error fails for logistic regression

The first question targets the classic loss-function mistake in binary classification — reaching for the regression loss — and its answer walks the full causal chain from the sigmoid squashing to the stuck optimizer.

**Q: Why can't we use Mean Squared Error (MSE) for Logistic Regression?**
A: Logistic Regression passes the linear combination $z$ through a Sigmoid activation function. If you insert a Sigmoid function inside the MSE equation, the resulting mathematical landscape becomes non-convex. It will have multiple local minima, meaning Gradient Descent is highly likely to get stuck and fail to find the optimal solution. We use Log Loss (Binary Cross-Entropy) because it guarantees a convex landscape.

The same convexity distinction is quizzed at length in [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Logistic Regression|Logistic Regression]] and [[Loss Functions and Cost Optimization]], with the information-theoretic background in [[Entropy Cross-Entropy and KL Divergence]].

## The purpose of the bias term

The second question separates the two learnable quantities inside a neuron: the weights, which scale an input's contribution, and the bias, which moves the activation.

**Q: What is the purpose of the bias term ($b$)?**
A: While weights ($w$) determine the slope or importance of an input, the bias ($b$) shifts the activation function left or right. Without a bias, the activation function must always cross the origin $(0,0)$, which severely limits the patterns the network can learn.

Activation functions are practiced in [[Activation Functions in Deep Learning]], and the network-level material that puts weights and biases to work is practiced in [[Multi-Layer Perceptron and Backpropagation]] and [[Gradient Descent Optimization]].

## A stray authoring note

One line of authoring shorthand rode along with the series, unattached to any question or answer: "use this in the 2d to 3d". Nothing else in the series indicates what it refers to; the fragment stands alone.

## See also

- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Loss Functions]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[Gradient Descent]]
- [[Activation Functions]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Logistic Regression|Logistic Regression]]
- [[Loss Functions and Cost Optimization]]
- [[Activation Functions in Deep Learning]]
- [[Multi-Layer Perceptron and Backpropagation]]
- [[Gradient Descent Optimization]]
- [[Conceptual Interview Questions]]
- [[Glossary MOC]]
