---
title: Teacher Forcing and Exposure Bias
type: concept
aliases:
  - Teacher forcing
  - Exposure bias
  - Free-running training
  - Scheduled sampling
  - Professor forcing
tags:
  - sequence-models
  - training
  - teacher-forcing
  - exposure-bias
  - seq2seq
  - rnn
sources:
  - "02. Teacher Forcing and Exposure Bias"
created_index: 13
---

In an encoder-decoder network, the decoder generates each token from a hidden state that depends on the previous token, so training requires a choice: feed the model's own predictions back, or feed the ground truth. Free-running training matches inference conditions but lets errors compound hopelessly; teacher forcing, the standard method, converges reliably but leaves the model unable to recover from its own mistakes at inference time. That train/test mismatch is exposure bias, and its symptoms — error accumulation, repetition loops, early divergence — show up in any generated sequence long enough to reveal them.

## The training-time question

In an Encoder-Decoder RNN (see [[The Encoder-Decoder Pattern]]), the decoder generates token $y_t$ from its hidden state $h_t^{dec}$, which depends on the previous token $y_{t-1}$. During training, what should we feed as $y_{t-1}$? There are two choices, and they have very different consequences.

## Free-running: feeding the model's own predictions

At each step, feed the model's predicted token from the previous step as input to the current step:

$$y_{t-1}^{pred} = \arg\max p_{t-1}$$
$$h_t^{dec} = \mathrm{RNN}_{dec}(h_{t-1}^{dec}, y_{t-1}^{pred})$$

This is what the model does at inference time, so training this way would seem to match inference conditions.

The problem is that errors compound. If the model mispredicts $y_1$, that wrong token becomes the input to step 2, which is now off-distribution, which makes $y_2$ more likely to be wrong, and so on. By step 10 the decoder has wandered into a region of token-space it never saw during training and produces garbage. Gradient-based learning cannot recover from this because the gradient signal is corrupted by the cascading errors — the model never learns what the *correct* trajectory looks like.

This is essentially why free-running training does not work for sequence generation.

## Teacher forcing: feeding the ground truth

At each step, feed the *true* previous token as input, regardless of what the model predicted:

$$h_t^{dec} = \mathrm{RNN}_{dec}(h_{t-1}^{dec}, y_{t-1}^{true})$$

This is called **teacher forcing** (Williams and Zipser, 1989). The model always sees the correct previous token, so it is always on-distribution. The gradient at step $t$ is clean — it reflects "given the correct prefix, can you predict the next token?" — and training converges reliably.

Teacher forcing is the standard training method for Encoder-Decoder RNNs. Every translation, summarization, and image-captioning model trained before ~2017 used it, and most modern Transformer decoders still use it.

## The catch: exposure bias

Teacher forcing creates a **train/test mismatch**. During training, the decoder always sees correct previous tokens. During inference, the decoder sees its *own* predicted previous tokens, which are sometimes wrong.

The model never learns how to recover from its own mistakes, because it never makes any during training. At inference time, the first mistake cascades: the wrong token feeds in, the next hidden state is off-distribution, the next prediction is more likely wrong, and the trajectory diverges. This is called **exposure bias** — the model is "exposed" only to correct trajectories during training and is biased toward expecting them.

A useful analogy: imagine learning to drive on a track where the car is always perfectly centered in the lane (an instructor nudges it back for you). You learn to drive well from the centered position. The first time you drift slightly off-center on a real road, you have no idea how to correct, because you never practiced recovery. Teacher forcing is the instructor; exposure bias is the resulting lack of recovery skill.

## Symptoms of exposure bias

At inference time, an exposure-biased model exhibits three characteristic failures:

1. **Error accumulation:** the longer the output, the worse it gets. Short translations look fine; long translations drift into ungrammatical or irrelevant text.
2. **Repetition loops:** the model emits "the the the the the..." because once it makes a small error that puts it in a state where "the" is the most likely token, feeding "the" back in keeps it in that state.
3. **Early divergence:** the first few tokens are usually correct (they depend only on the encoder), but quality collapses once the decoder starts feeding back its own predictions.

## Mitigations

Several mitigations exist, none of them a complete cure.

### Scheduled sampling

Scheduled sampling (Bengio et al. 2015) gradually replaces teacher-forced tokens with model-predicted tokens over the course of training. Early in training, use 100% teacher forcing (clean gradients, reliable learning). Late in training, use mostly model predictions (the model learns to recover from its own errors).

$$\text{prob(use model prediction at step } t) = \epsilon(\text{epoch})$$

where $\epsilon$ ramps from 0 to some target (e.g., 0.5) over training. This reduces exposure bias but introduces noise into the gradient, which can destabilize training.

### Professor forcing

Professor forcing (Goyal et al. 2016) adversarially trains the decoder so that its hidden-state dynamics under teacher-forced and free-running inputs are indistinguishable. It is conceptually elegant but complex to implement.

### Just use beam search

A simpler mitigation is to use **beam search** at inference rather than greedy decoding — see [[Beam Search and Decoding Strategies]]. Beam search explores multiple candidate sequences and is less likely to commit to an early mistake. It does not fix exposure bias, but it softens its impact.

### The modern answer: use a Transformer

In modern NLP, the Encoder-Decoder RNN is rarely used; Transformers (see [[The Transformer]]) have taken over. Transformers still use teacher forcing for training and still exhibit exposure bias, but they are more robust to it because (a) attention gives them direct access to the input at every step, reducing their dependence on the decoder's own state, and (b) they are trained on vastly more data, which broadens the distribution of states the decoder has seen. Exposure bias remains an open problem in sequence generation, but it is no longer the dominant failure mode.

## What to walk away with

The essentials, in order:

1. Teacher forcing — feeding ground-truth previous tokens during training — is the standard way to train sequence decoders because it gives clean gradients.
2. Teacher forcing creates exposure bias: the model never learns to recover from its own mistakes, so errors compound at inference time.
3. Symptoms include error accumulation, repetition loops, and early divergence.
4. Mitigations (scheduled sampling, professor forcing, beam search) help but do not cure the problem.
5. Exposure bias remains an open problem in sequence generation; modern Transformers reduce its impact but do not eliminate it.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[The Encoder-Decoder Pattern]] — the architecture being trained.
- [[Beam Search and Decoding Strategies]] — the inference-time behavior affected by exposure bias.
- [[The Bottleneck Problem]] — the companion architectural limitation of the encoder-decoder RNN.
- [[From RNNs to Attention]] — the path away from the plain Encoder-Decoder RNN.
- [[The Transformer]] — the architecture that reduced, but did not eliminate, exposure bias.
