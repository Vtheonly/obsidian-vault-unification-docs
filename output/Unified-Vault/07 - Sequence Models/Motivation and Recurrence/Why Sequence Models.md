---
title: Why Sequence Models
type: concept
aliases:
  - "Why Sequence Models — The Limits of Feedforward Networks"
  - The Limits of Feedforward Networks
  - Motivation for Sequence Models
tags:
  - sequence-models
  - recurrent-neural-networks
  - feedforward-networks
  - weight-sharing
  - language-modeling
  - order-dependence
sources:
  - "01. Why Sequence Models — The Limits of Feedforward Networks"
created_index: 8
---

Every neural network in the feedforward family — the perceptron, the MLP, the CNN — quietly assumes that its input is a fixed-size, position-independent object. The assumption is so natural that it usually goes unstated, and it is harmless for images and tabular data. It becomes fatal the moment you apply these networks to language, audio, or time series, where order carries meaning and length varies. This note pinpoints exactly where feedforward architectures break down on sequences, why enlarging the input window cannot repair them, and how the cure — sharing weights across time, the way CNNs share weights across space — defines the recurrent neural network.

## The hidden assumption of feedforward networks

Every feedforward network treats its input as a fixed-size, position-independent object: a 28×28 image is a 28×28 image regardless of which class it belongs to, and a 10-feature row in a tabular dataset has the same 10 features for every row. The assumption is so natural that it is rarely written down, but it has a consequence that becomes obvious the moment you apply these networks to language, audio, or time series: the network has no memory, and the network has no notion of order.

Images and sentences sit on opposite sides of this divide. An image is mostly translation-invariant — a cat in the top-left corner is still a cat in the bottom-right corner — and CNNs exploit this by sharing weights across spatial positions. A sentence is order-dependent in an irreducible way: "the dog bit the man" and "the man bit the dog" contain the same words but mean opposite things, and no spatial pooling can recover that difference. A feedforward network can only handle a sentence by flattening it into a fixed-length vector, which destroys two things at once: it forces you to choose a maximum length in advance, and it throws away the fact that the words form a sequence rather than a set.

## Three tasks a feedforward network cannot do well

### Language modeling

Given "the cat sat on the", predict the next word. A feedforward network can do this if you fix the context length — say, always look at the last 5 words — but the compromise fails in three ways. It cannot use context from 20 words ago when the sentence calls for it ("I grew up in France. ... [many sentences later] ... I speak fluent ___"). It needs a separate set of input weights for position 1, position 2, ... position 5, so with no parameter sharing across time the model has to relearn that "the" is "the" no matter where it appears. And it cannot generate sequences of arbitrary length, because the input shape is fixed.

### Translation

Translating "how are you?" to "comment ça va ?" maps 3 words to 3 words. But translating a 30-word sentence to a 25-word sentence is a different problem entirely: the input and output lengths differ, and there is no fixed alignment between input position $i$ and output position $j$. A feedforward network has no mechanism for this.

### Time-series forecasting

Predicting tomorrow's electricity demand from the last 24 hours is fine for an MLP. But predicting next month's sales from a multi-year history, where seasonal patterns repeat every 365 days and trend changes slowly over years, requires the model to remember events from arbitrarily far back. A fixed window throws away most of that history.

## Why a bigger window does not help

The natural reaction is to just make the window larger — look at the last 1000 words, the last 10 years of data, the last 1000 audio frames. This fails for three reasons.

First, parameter explosion. If the input dimension is 1000 and the first hidden layer has 1000 neurons, the first weight matrix has $10^6$ parameters — all of them dedicated to a single, position-specific mapping. With no sharing, the network has to independently learn that "the" at position 17 means the same thing as "the" at position 942.

Second, statistical inefficiency. Because each position has its own weights, the network never sees the regularity that "the" is "the" wherever it appears. It cannot pool evidence across positions, and generalization suffers.

Third, fixed length is a lie. No matter how big you make the window, there will always be a sequence longer than it. And for sequences shorter than the window, you waste input slots on padding tokens, which dilutes the signal.

## Share weights across time, as CNNs share across space

A CNN works because the same convolutional kernel is applied at every spatial position: the network learns one pattern ("vertical edge") and reuses it everywhere, and the number of parameters is independent of the image size. The analogous idea for sequences is to apply the same weights at every time step, and let the network's output at time $t$ depend on its own output at time $t-1$. That way the same "what does this word mean" function is applied to every position; the network's internal state at time $t$ becomes a function of the entire history up to $t$, so memory is built in; the number of parameters becomes independent of the sequence length; and variable-length sequences become first-class citizens. This is the definition of a recurrent neural network.

## Feedforward, convolutional, and recurrent networks compared

| Property | Feedforward MLP | CNN | (Vanilla) RNN |
| :--- | :--- | :--- | :--- |
| Input shape | Fixed vector | Fixed image (or volume) | Variable-length sequence |
| Weight sharing | None | Across spatial positions | Across time steps |
| Memory of past | None | None (within one forward pass) | Yes (hidden state) |
| Handles order | No | Only spatial | Yes (explicitly) |
| Handles variable length | No | No | Yes |
| Gradient flow | One backward pass | One backward pass | Through time (BPTT) |

Notice that the RNN column is the first one that says "yes" to memory, order, and variable length simultaneously. That is the whole reason RNNs exist.

## What to walk away with

A feedforward network treats every input as an unordered, fixed-size object — fine for images and tabular data, fatal for sequences. Enlarging the input window does not solve the problem; it just makes the parameter explosion and the statistical inefficiency worse. The right move is to share weights across time and let the network carry state, which is exactly what an RNN does. CNNs and RNNs are conceptually siblings: CNNs share weights across space, RNNs share weights across time, and both reduce parameters by exploiting a symmetry in the data. The next note, [[The Recurrent Neuron]], formalizes "share weights across time" and shows the diagram that every RNN explanation in the world eventually draws — the **unrolled computational graph**.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[The Recurrent Neuron]] — makes weight sharing across time precise and unrolls the loop
- [[Backpropagation Through Time]] — how the recurrent network is trained
- [[Long-Range Dependencies]] — the memory requirement that defeats fixed windows
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — the spatial weight-sharing sibling
- [[Artificial Neural Networks]] and [[Perceptrons and Multi-Layer Perceptrons]] — the feedforward baseline being contrasted
