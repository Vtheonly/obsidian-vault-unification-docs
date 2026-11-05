---
title: Logit Lens and Tuned Lens
type: concept
aliases: ["Logit Lens", "Tuned Lens", "Intermediate Layer Probing"]
tags: [interpretability, logit-lens, tuned-lens, probing]
sources:
  - "02 - Logit Lens and Tuned Lens"
created_index: 3
---

The logit lens applies a Transformer's final unembedding layer — the vocabulary projection — to intermediate layer activations, producing a probability distribution over the vocabulary at each layer. This reveals what the model is "thinking" at each depth: you can see the prediction forming and updating across layers. The tuned lens extends this with a learned affine transformation per layer to correct for the gap between intermediate and final representations. Together, they provide a simple, model-agnostic window into Transformer computation; see [[Interpretability and Research MOC]] for the surrounding area.

## The problem being solved

[[Mechanistic Interpretability|Mechanistic interpretability]] aims to understand what Transformers compute at each layer. But intermediate activations are high-dimensional vectors with no obvious interpretation — you can't look at a 4096-dimensional vector and tell what it "means".

The final layer's output, by contrast, is interpretable: it's a probability distribution over the vocabulary, and we can read off the top predicted tokens. But by the time we reach the final layer, all the computation is done — we see the result, not the process.

The logit lens (nostalgebraist, 2020) bridges this gap with a simple idea: apply the final unembedding layer ($W_U$) to intermediate activations. This projects each layer's hidden state into the vocabulary space, giving us a probability distribution at every depth.

## The logit lens

### The method

For a Transformer with $L$ layers, hidden dimension $d$, and vocabulary $V$, normal decoding works as follows. The final layer produces a hidden state $h_L$ of shape `(d,)`. The unembedding matrix $W_U$ of shape `(V, d)` projects $h_L$ to logits, $\text{logits} = W_U \cdot h_L$, of shape `(V,)`. A softmax over the logits gives the output probability distribution.

The logit lens applies this same projection to intermediate hidden states:

```text
For each layer l in 1..L:
    h_l = hidden state at layer l  (after the residual stream)
    logits_l = W_U · h_l
    probs_l = softmax(logits_l)
```

Now you have a probability distribution over the vocabulary at each layer. From these per-layer distributions you can read off the top predicted token at each layer, see how the prediction updates across layers, identify layers where the prediction is confident vs. uncertain, and detect "prediction flips" — layers where the model changes its mind.

### What it reveals

Applying the lens across layers revealed several patterns about how Transformers process information.

**Early layers are random-looking.** Layers 1–5 typically produce near-uniform distributions or predict common tokens ("the", "a", "and"). The model is still building up representations.

**Middle layers start predicting the correct token.** Around layer 6–10 (in a 12-layer model), the correct token often appears in the top-K predictions, but not always at rank 1.

**Late layers refine and commit.** The final 2–3 layers sharpen the distribution, moving the correct token to rank 1 and suppressing alternatives.

**Prediction flips are informative.** When the model predicts token A at layer 8 but token B at layer 12, the flip often corresponds to a specific computation (e.g., resolving a coreference, completing an idiom).

### Example output

For the prompt "The capital of France is", a 12-layer model might show:

| Layer | Top-1 Prediction | Probability |
|-------|------------------|-------------|
| 1     | "the"            | 0.05        |
| 3     | "a"              | 0.04        |
| 5     | "Paris"          | 0.15        |
| 7     | "Paris"          | 0.45        |
| 9     | "Paris"          | 0.78        |
| 11    | "Paris"          | 0.92        |
| 12    | "Paris"          | 0.95        |

This shows the prediction forming at layer 5 and sharpening through layer 12.

## The tuned lens

### The problem with the logit lens

The logit lens assumes that intermediate hidden states are in the same "space" as the final hidden state — that you can apply $W_U$ directly. But this isn't quite right. Each layer's hidden state is transformed by subsequent layers before reaching the output, so applying $W_U$ directly to an intermediate state is like applying a translation dictionary to a language it wasn't designed for.

The result: the logit lens works (you can see predictions forming), but the intermediate distributions are noisy and less calibrated than the final distribution.

### The fix: learned affine transformations

The tuned lens (Belrose et al., 2023) adds a learned affine transformation $T_l$ per layer:

```text
logits_l = W_U · (T_l(h_l))
         = W_U · (A_l · h_l + b_l)
```

where $A_l$ (shape `(d, d)`) and $b_l$ (shape `(d,)`) are learned per layer. The transformation "tunes" the intermediate hidden state to be more compatible with the unembedding matrix.

### Training the tuned lens

Training is a small, fast loop that leaves the base model untouched. For each layer $l$, collect hidden states $h_l$ on a corpus of text. For each $h_l$, the "target" is the next token $y$ — the same target the full model is predicting. Train $A_l, b_l$ to minimize cross-entropy between $\text{softmax}(W_U \cdot T_l(h_l))$ and $y$. You're only learning $A_l, b_l$, not modifying the base model.

### What the tuned lens reveals

The tuned lens produces more calibrated intermediate distributions than the logit lens, and three findings stand out.

**Intermediate layers are more capable than the logit lens suggests.** With proper tuning, layer 6 of a 12-layer model often achieves nearly the same next-token prediction accuracy as the full model. The logit lens underestimates intermediate capability because the untrained $W_U$ projection is suboptimal.

**The "capability curve" is smoother.** With the logit lens, capability sometimes appears to jump discontinuously between layers. The tuned lens reveals that capability increases more smoothly — the jumps were artifacts of the projection mismatch.

**Early layers have more information than expected.** Even layer 1–2, with the tuned lens, can sometimes predict the next token above chance — suggesting that the model extracts relevant features very early.

## Comparison

The two lenses trade a small amount of training effort for substantially better per-layer fidelity:

| Aspect                  | Logit Lens             | Tuned Lens                          |
|-------------------------|------------------------|-------------------------------------|
| Method                  | Apply `W_U` directly   | Apply `W_U · T_l` with learned `T_l`|
| Calibration             | Poor at middle layers  | Good across all layers              |
| Training required       | None                   | Small affine model per layer        |
| Computational cost      | Minimal                | Minimal (just a matrix multiply)    |
| Reveals                 | Approximate predictions| Calibrated predictions              |
| Use case                | Quick exploration      | Rigorous analysis                   |

The logit lens suits quick exploration of a model; the tuned lens is the tool of choice when per-layer claims need to be calibrated and defensible.

## Applications

### Understanding model behavior

For a given prompt, plot the top-K predictions at each layer. This reveals when the model "knows" the answer (which layer first predicts it), when the model is uncertain (layers with flat distributions), and when the model changes its mind (prediction flips).

### Detecting capabilities and limitations

Test the model on tasks where you know the answer. The lens reveals whether the model "knows" the answer at intermediate layers even if the final output is wrong — useful for diagnosing where the model fails.

### Comparing models

Compare the per-layer prediction curves of different models (e.g., GPT-2 vs Llama). This reveals architectural differences in how information is processed.

### Steering model behavior

Some research uses the lens to identify layers where specific information is represented, then modifies those activations to steer the model's output (activation patching, representation engineering) — the mechanics of which are covered in [[Activation Patching and Causal Tracing]].

### Training dynamics

Apply the lens to checkpoints during training. This reveals how the model's internal computation evolves over training — when does it start predicting the correct token at each layer?

## Limitations

### Vocabulary-biased

Both lenses project to the vocabulary space, which means they can only reveal predictions about tokens. They cannot reveal other information the model computes (syntactic structure, entity tracking, world model) unless that information is reflected in token predictions.

### Layer-specific, not token-specific

The lens shows what the model predicts at each layer for a specific position, but it doesn't directly reveal what each *attention head* or *neuron* is doing. For that, you need finer-grained techniques — see [[Sparse Autoencoders]] and [[Activation Patching and Causal Tracing]].

### Tuned lens requires training data

The tuned lens requires a corpus to train the affine transformations. The choice of corpus affects what the lens reveals — a lens trained on news text might not calibrate well for code.

### Doesn't explain causation

The lens shows *what* the model predicts at each layer, not *why*. If the model flips its prediction at layer 8, the lens shows the flip but not which attention heads or neurons caused it.

## Tooling

Several libraries make the lenses easy to apply. **TransformerLens** (Neel Nanda) includes a logit lens implementation. The **tuned-lens** package (Belrose et al.) is the official implementation of the tuned lens. **Ecco** (explainability for Transformer models) provides an interactive logit lens visualization. A custom implementation is also easy: just apply $W_U$ to intermediate hidden states and softmax.

## See also

- [[Interpretability and Research MOC]]
- [[Mechanistic Interpretability]]
- [[Probing]]
- [[Sparse Autoencoders]]
- [[Activation Patching and Causal Tracing]]
