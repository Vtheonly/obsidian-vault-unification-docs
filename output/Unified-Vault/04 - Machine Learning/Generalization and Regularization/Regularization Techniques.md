---
title: Regularization Techniques
type: concept
aliases:
  - Regularization
  - Weight Decay
  - Weight Penalties
  - Dropout
  - Label Smoothing
tags:
  - machine-learning
  - regularization
  - weight-decay
  - dropout
  - l1-regularization
  - l2-regularization
  - elastic-net
  - early-stopping
  - label-smoothing
  - data-augmentation
  - overfitting
sources:
  - "06 - Regularization Techniques"
created_index: 5
---

Regularization is the family of techniques that prevent overfitting by constraining the model: penalty terms (L1, L2, elastic net), dropout, early stopping, data augmentation, label smoothing, and even side effects like the batch-statistical noise of batch normalization. Each member addresses a different failure mode, and the modern deep-learning recipe combines several at once. Without regularization, deep networks overfit catastrophically; with it, they generalize across domains. This note walks through the toolbox in teaching order — penalties first, then the training-time techniques, then the architectural and fine-tuning variants — and closes with how to choose among them.

## Why regularize

Models can fit training data perfectly but generalize poorly — the overfitting condition dissected in [[Bias Variance Tradeoff]], whose diagnostic is the gap between training and validation/test performance ([[Model Evaluation Metrics]]). Regularization deliberately trades a small increase in training loss for a larger reduction in test loss, which means a regularized model can be the better model despite lower training accuracy. The trade is made in three ways:

- Limiting model capacity.
- Adding noise during training.
- Encouraging simpler solutions.

Every technique below is a variation on one of these three mechanisms, and the craft of regularization is matching the technique to the failure mode at hand.

## L1, L2, and elastic net regularization

The weight-penalty family modifies the training objective itself — the base loss $L$ treated in [[Loss Functions]] — by adding a penalty on the weights:

$$
L_{\text{reg}} = L + \lambda \cdot R(\mathbf{w})
$$

The strength hyperparameter $\lambda$ sets how hard the constraint pushes; the choice of penalty $R(\mathbf{w})$ sets what kind of solution is preferred.

### L2 (ridge, weight decay)

$$
R(\mathbf{w}) = \|\mathbf{w}\|_2^2 = \sum_i w_i^2
$$

Shrinks weights toward zero (but rarely to exactly zero). Smaller weights make the network's output change more gently with its input, yielding smoother functions and decision boundaries that generalize better. Equivalent to MAP estimation with a Gaussian prior. The standard for neural networks — and consequently the penalty used far more than L1 in deep learning.

In optimizers like AdamW, L2 is implemented as **decoupled weight decay** (multiply weights by $1 - \eta \lambda$ each step) rather than as a gradient penalty. The distinction matters for adaptive optimizers, and the practical recommendation is to prefer AdamW over Adam plus a `weight_decay` term — the full treatment lives in [[Optimizers and Learning Rate Schedulers]].

### L1 (lasso)

$$
R(\mathbf{w}) = \|\mathbf{w}\|_1 = \sum_i |w_i|
$$

Produces **sparse** weights (many exactly zero). Useful for feature selection — the zeros drop features outright. Equivalent to MAP with a Laplace prior. The contrast with L2 is the headline: L1 drives exact zeros, L2 shrinks but rarely zeroes, which is why L1 lives mostly in feature-selection and classical linear-model settings while L2 dominates deep learning.

### Elastic net

Combination of L1 and L2:

$$
R(\mathbf{w}) = \alpha \|\mathbf{w}\|_1 + (1-\alpha) \|\mathbf{w}\|_2^2
$$

Useful when features are correlated (L1 alone picks one randomly; Elastic Net keeps groups). The mixing parameter $\alpha$ slides between pure lasso and pure ridge.

## Dropout

Dropout (Srivastava et al., 2014) attacks co-adaptation directly. During training, randomly set a fraction $p$ of activations to zero. At test time, use all activations (scaled to compensate).

```python
# Pseudocode
def dropout_forward(x, p, training):
    if training:
        mask = (torch.rand_like(x) > p).float() / (1 - p)
        return x * mask
    return x
```

The `/ (1 - p)` in the mask is **inverted dropout**: surviving activations are scaled up during training so that expected outputs are preserved and no test-time adjustment is needed.

### Why dropout works

- **Ensemble effect**: each forward pass uses a different sub-network. Like bagging, but at the activation level — the ensemble idea underlying [[Random Forests and Bagging]].
- **Noise injection**: prevents co-adaptation (no neuron can rely on any other specific neuron being present).
- **Approximates model averaging** over exponentially many sub-networks.

### Typical dropout rates

- Input layer: 0.1–0.2.
- Hidden layers: 0.3–0.5.
- Attention weights: 0.0–0.1.
- Transformer FFN: 0.0–0.1.

The pattern: strongest (~0.5) on large fully connected hidden layers, weaker elsewhere. Modern LLMs use **very little dropout** because they rely on data scale and other regularizers. But for small-data fine-tuning, dropout is still valuable.

## Early stopping

Halt training when validation loss stops improving (or starts worsening):

```python
best_val = float('inf')
patience, waited = 3, 0
for epoch in range(max_epochs):
    train_one_epoch()
    val_loss = evaluate(val_loader)
    if val_loss < best_val:
        best_val = val_loss
        waited = 0
        save_checkpoint()
    else:
        waited += 1
        if waited >= patience:
            break  # early stop
```

The `save_checkpoint()` call is the part people forget: keep the weights from the best-validation epoch, not the last one. **The cheapest, most reliable regularizer.** Always use it unless you have a strong reason not to. It leans on the same validation signal as the plateau-detecting learning-rate schedulers covered in [[Optimizers and Learning Rate Schedulers]] and the evaluation discipline of [[Model Evaluation Metrics]].

## Label smoothing

Instead of one-hot targets `[0, 0, 1, 0]`, use smoothed targets `[0.033, 0.033, 0.9, 0.033]` (smoothing factor $\epsilon = 0.1$).

- Prevents the model from becoming overconfident.
- Acts as calibration regularization.
- Standard in modern image classification (since Szegedy et al. 2016) and used in some LLM training.

The smoothed targets feed the cross-entropy objective ([[Loss Functions]]), so the change is a one-line modification of the loss computation with an outsized effect on calibration.

## Related techniques

### Data augmentation

Artificially expand the training data via label-preserving transformations:

- **Images**: flip, crop, rotate, color jitter, mixup, cutmix.
- **Text**: synonym replacement, back-translation, random deletion.
- **Audio**: time stretch, pitch shift, noise injection.

Effective when data is limited. Especially powerful for vision — ImageNet training relies heavily on augmentation. It is the practical remedy whenever "get more data" is the right bias-variance answer but collecting data is expensive.

### Batch normalization (side effect: regularization)

BatchNorm normalizes activations using batch statistics. As a side effect, the noise from batch statistics acts as a regularizer — a dropout-style noise effect on generalization, though weaker than dropout. This is part of why BatchNorm improves generalization beyond just faster training.

**Note**: in NLP/Transformers, BatchNorm is rarely used — LayerNorm/RMSNorm is preferred because sequence lengths vary, which makes batch statistics unreliable.

### Weight tying

Weight tying shares weights across layers (e.g., input and output embeddings in language models). It reduces parameters and acts as a regularizer (forces the embedding space and output space to be the same).

### Regularization in transformers

- **Dropout** on attention weights and FFN activations.
- **Weight decay** (AdamW).
- **Label smoothing** in classification heads.
- **Attention dropout**: critical for preventing the model from over-relying on a few tokens.

### Regularization in LLM fine-tuning

- **LoRA's low-rank constraint** is itself a regularizer (limits the rank of weight updates).
- **KL penalty in RLHF** prevents the policy from drifting too far from the reference.
- **LoRA dropout**: apply dropout to LoRA's A/B matrices.

Fine-tuning is where regularization matters most: you have less data than pretraining and want to preserve the pretrained model's behavior, so constraints like low rank and KL penalties do double duty as quality safeguards.

## Choosing a regularization strategy

### A worked example

A small network with dropout on both hidden layers and weight decay applied through the optimizer:

```python
import torch.nn as nn

class RegularizedModel(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.fc1 = nn.Linear(d, d*2)
        self.drop1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(d*2, d)
        self.drop2 = nn.Dropout(0.1)
    
    def forward(self, x):
        x = self.drop1(torch.relu(self.fc1(x)))
        x = self.drop2(self.fc2(x))
        return x

# Weight decay via optimizer
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
```

The pattern is typical: stronger dropout (0.3) right after the wide first layer where parameters concentrate, lighter dropout (0.1) after the narrower second layer, and weight decay of 0.01 applied through AdamW rather than as a penalty in the loss.

### Production defaults

- **Always use early stopping.** It's free regularization.
- **Weight decay of 0.01–0.1** is a reasonable default for most training. Tune on validation. Typical values run stronger for AdamW-based training than for classic SGD CNN recipes.
- **Dropout in fine-tuning** can help, especially with small data. 0.1 is a good starting point.
- **For LoRA fine-tuning**: keep dropout low (0.05–0.1); the low-rank constraint is already regularizing.
- **Don't apply weight decay to biases or norm parameters** — they don't have a regularization interpretation. Use parameter groups in your optimizer.

The modern recipe for large models combines weight decay + dropout (lightly) + label smoothing + the implicit regularization of SGD ([[Gradient Descent]]) + sheer scale of data. Each ingredient is individually modest; the combination is part of what makes modern LLM training work.

### Common pitfalls

- **Dropout at test time** — never apply dropout during inference. Always check `model.eval()`.
- **Wrong dropout scaling** — PyTorch's `nn.Dropout` uses "inverted dropout" (scales during training), so no test-time adjustment is needed. Old frameworks scaled at test time.
- **Too much regularization** — underfits. Watch training loss; if it can't go down, regularize less.
- **Forgetting to apply regularization to all relevant layers** — typically you skip the output layer, and concentrate dropout where parameters and overfitting risk are highest.
- **Mixing L1 and L2 without intent** — be deliberate about which you're using and why.

### Technique summary

| Technique | Mechanism | Typical setting |
|---|---|---|
| L2 / weight decay | Squared penalty shrinks weights toward zero; Gaussian-prior MAP | Standard for neural networks; 0.01–0.1, tune on validation |
| L1 / lasso | Absolute penalty drives exact zeros; Laplace-prior MAP | Feature selection; sparsity |
| Elastic net | L1 + L2 blend keeps correlated feature groups | Correlated features |
| Dropout | Randomly zero activations; implicit sub-network ensemble | Hidden layers 0.3–0.5; fine-tuning ~0.1 |
| Early stopping | Halt at best validation epoch, keep that checkpoint | Always |
| Data augmentation | Label-preserving transformations grow the data | Limited data, especially vision |
| Label smoothing | Soft targets prevent overconfidence | $\epsilon = 0.1$; classification heads |

## Further reading

- Srivastava et al. (2014), *Dropout: A Simple Way to Prevent Neural Networks from Overfitting*.
- Szegedy et al. (2016), *Rethinking the Inception Architecture for Computer Vision* (label smoothing).
- Zhang et al. (2017), *mixup: Beyond Empirical Risk Minimization*.
- Kukačka et al. (2017), *Regularization for Deep Learning: A Taxonomy* (great survey).

## See also
- [[Adam Optimizer Derivation]]
- [[Normalization Layers]]
- [[13 - Training and Adaptation/Fine-Tuning/LoRA.md|LoRA]]


[[Bias Variance Tradeoff]] explains why these techniques work — variance reduction is the mechanism behind every one of them. [[Optimizers and Learning Rate Schedulers]] covers AdamW and the decoupled weight-decay implementation; [[Model Evaluation Metrics]] covers the validation signals that drive early stopping; [[Loss Functions]] is the base objective the penalties modify; [[Gradient Descent]] is the optimizer whose noise provides implicit regularization; and [[Random Forests and Bagging]] develops the ensemble view dropout approximates at the activation level. Ridge and lasso in their classical linear-model setting connect to [[Regression Fundamentals]]. The map of all machine-learning topics is at [[Machine Learning MOC]].
