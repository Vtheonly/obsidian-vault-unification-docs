---
title: Chapter Overview
type: overview
aliases:
  - "Sequence Models and RNNs: Chapter Overview"
  - Sequence Models and RNNs
  - Sequence Models area overview
tags:
  - sequence-models
  - recurrent-neural-networks
  - lstm
  - gru
  - encoder-decoder
  - attention
sources:
  - "00 - Sequence Models and RNNs: Chapter Overview"
created_index: 1
---

This note is the orientation for the Sequence Models area: a map of why the area exists, what its notes cover, and the order to read them in. The whole area develops one idea — a hidden state updated at every time step, so that the same weights are reused across time and the past persists into the present — from its motivation, through its failure modes, to the encoder–decoder systems that hit a wall only attention could break. Skim it top to bottom before diving into any note, and return whenever you lose the thread.

> [!info] Where this area sits
> **Prerequisites:** the feedforward baseline — MLPs, backpropagation, and activation functions ([[Perceptrons and Multi-Layer Perceptrons]], [[Backpropagation]], [[Activation Functions]]) — plus gradient descent and loss functions ([[Gradient Descent]], [[Loss Functions]]), and the chain rule and partial derivatives that backpropagation rests on.
> **Next:** [[Attention and Transformers MOC]] — this area is the conceptual bridge that makes the Transformer architecture feel inevitable rather than arbitrary.

## Why this area exists

Everything you have built so far — MLPs, CNNs — treats every input as an independent, fixed-shape object. A CNN looks at one image and emits one label; an MLP looks at one feature vector and emits one prediction. There is no notion of order, no notion of history, no notion that the meaning of an input depends on what came before it.

But a huge fraction of real-world data is sequential:

- A sentence is a sequence of words whose meaning depends on order ("the dog bit the man" vs "the man bit the dog").
- A time series is a sequence of measurements whose future values depend on past values.
- A spoken word is a sequence of audio frames.
- A stock price is a sequence of ticks.
- A protein is a sequence of amino acids whose 3D shape depends on the order.

A plain MLP cannot handle this gracefully. If you feed it a fixed-size window of the past, you must choose the window size in advance, and the model has no way to remember important events from further back — and enlarging the window only trades the problem for parameter explosion, as [[Why Sequence Models]] shows in detail. If you feed it a variable-length sequence by flattening it, you destroy the order information and you cannot handle sequences of different lengths.

Recurrent Neural Networks (RNNs) were invented to fix this. The defining idea is breathtakingly simple: the network has a hidden state that is updated at every time step, so the same weights are reused across time and the past persists into the present. This single idea — weight sharing across time — is the conceptual bridge between CNNs (which share weights across space) and Transformers (which share weights across positions). The reference treatment of the whole recurrent family lives in [[Recurrent Neural Networks]]; this area builds the idea carefully, explains why vanilla RNNs fail in practice, how LSTMs and GRUs patch the failure, and how the Encoder–Decoder pattern turned RNNs into translation machines — and then hit a wall that only attention could break.

## The four subareas

The area's notes fall into four subareas, and the order below is the intended reading order — each note assumes the previous one.

### Motivation and Recurrence

Where the recurrent idea comes from and how it is trained: why feedforward networks break on sequences, the recurrent neuron and unrolling through time, backpropagation through time on the unrolled graph, and the gradient pathology that depth-through-time creates.

1. [[Why Sequence Models]]
2. [[The Recurrent Neuron]]
3. [[Backpropagation Through Time]]
4. [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]

### LSTM and GRU

The architectural patch: gates as learned traffic controllers that give the gradient an additive highway, the GRU's cheaper simplification, and the practical trade-offs between the two cells.

1. [[LSTM]]
2. [[GRU]]
3. [[LSTM vs GRU]]

### Sequence to Sequence

Conditional generation: two RNNs chained through a single context vector, the teacher-forcing trick that trains them (and the exposure bias it buys), and the decoding strategies that turn output probabilities into sentences.

1. [[The Encoder-Decoder Pattern]]
2. [[Teacher Forcing and Exposure Bias]]
3. [[Beam Search and Decoding Strategies]]

### Pitfalls and Limits

Why the design runs out of room: why one fixed-size vector is not enough, why even gated RNNs struggle with long-range dependencies, and the historical bridge from those limits to attention.

1. [[The Bottleneck Problem]]
2. [[Long-Range Dependencies]]
3. [[From RNNs to Attention]]

## How to read this area

The area is sequential by construction — each note assumes the previous one. But the intuition is more important than the math. If you understand why a vanilla RNN forgets, why an LSTM remembers, and why a single fixed-size context vector becomes a bottleneck, you understand 90% of what you need to appreciate the Transformer; the remaining 10% is just notation.

The last note — [[From RNNs to Attention]] — is the door into [[Attention and Transformers MOC]]. Do not skip it.

## What this area deliberately does not cover

Three families of material are left out on purpose, none of them central to the conceptual line from recurrence to attention:

- **Practical RNN training in PyTorch.** That belongs in a project notebook, not in conceptual notes — the goal here is understanding, not syntax.
- **Bidirectional RNNs and stacked RNNs.** No dedicated note; they are simple extensions once the core recurrence is clear.
- **WaveNet, temporal convolutions, and state-space models (Mamba).** Advanced topics beyond the recurrent-to-attention lineage — the closing note ([[From RNNs to Attention]]) points at the state-space line among its research directions so you know the family exists.

## See also

- [[Recurrent Neural Networks]] — reference treatment of the whole recurrent family
- [[Seq2Seq and the Information Bottleneck]] — the sequence-to-sequence pattern at reference depth
- [[Neural Network Foundations MOC]] — the feedforward foundations this area extends
- [[Convolutional Neural Networks]] — the other place weights are shared across a dimension
- [[Attention and Transformers MOC]] — the destination this area is building toward
- [[Perceptrons and Multi-Layer Perceptrons]], [[Backpropagation]], [[Activation Functions]], [[Gradient Descent]], [[Loss Functions]] — prerequisite material
