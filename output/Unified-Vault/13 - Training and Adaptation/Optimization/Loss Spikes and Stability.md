---
title: Loss Spikes and Stability
type: concept
aliases: [Loss Spikes, Training Stability, Loss Divergence, NaN Loss]
tags: [training, stability, loss-spikes, gradient-clipping, debugging]
sources: ["05 — Loss Spikes and Stability"]
created_index: 7
---

Loss spikes — sudden, large increases in training loss during otherwise stable training — are a notorious problem in large-scale LLM training. A single spike can cascade into divergence (loss → NaN) and waste millions of dollars of compute, so production runs treat stability as an engineered property rather than luck. This note covers why spikes happen, how to detect them, how to prevent them, how to recover when they strike anyway, and how production systems automate the whole loop; it is the stability counterpart to [[Mixed Precision Training]], whose lower-precision formats are one of the leading spike sources.

> [!info] TL;DR
> Loss spikes can be caused by bad data batches, numerical instability in mixed precision, optimizer state corruption, learning rate issues, or genuine model instability at scale. Without intervention, a single spike can cascade into divergence (loss → NaN), wasting millions of dollars of compute. The standard toolkit for handling spikes: **gradient clipping** (prevent extreme updates), **loss scaling** (for FP16), **selective skip-on-spike** (skip the bad batch), **learning rate warmup** (avoid early instability), and **checkpoint rollback** (rewind to a pre-spike checkpoint). Production training runs instrument these aggressively.

## Why loss spikes happen

A loss spike is a sudden increase in training loss — typically 10× or more — that occurs during otherwise stable training. The fundamental causes fall into five categories, and attributing a spike to the right one determines the response: data problems call for skipping batches and pipeline fixes, numerical problems call for precision changes, and optimization problems call for schedule changes.

### Bad data batches

A single batch with anomalous data can produce a large loss. The common culprits:

- **Highly repetitive text**: the model fits the repetition pattern, then a non-repetitive batch produces high loss.
- **Out-of-distribution text**: a batch of code when the model expected natural language.
- **Corrupted text**: encoding errors, binary blobs misclassified as text.
- **Long-tail rare tokens**: batches with unusual tokens cause large gradients.

Even one bad batch in a million can cause a spike. The challenge is identifying it among millions of batches, which is why disciplined data pipelines ([[Data Pipelines and Deduplication]]) are the first line of defense.

### Numerical instability

Mixed precision training (FP16, BF16, FP8) introduces numerical noise. Most of the time this noise is harmless, but occasionally it accumulates:

- **Gradient underflow**: small gradients become zero in FP16, then accumulate in the optimizer state, eventually causing a large update when they resurface.
- **Activation overflow**: large activations become inf, propagating through the network.
- **Softmax saturation**: extreme logits cause softmax to produce one-hot outputs, which then produce extreme gradients.

The mechanics of these failures trace back to the limited range and precision of the formats themselves, covered in [[Mixed Precision Training]].

### Optimizer state issues

Adam's running statistics (m and v) can become corrupted:

- **v (variance) estimate becomes too small**: the next gradient appears larger than expected, producing a huge update.
- **v estimate becomes too large**: updates become tiny, training stalls (this isn't a spike but is a related failure).
- **Beta values mismatch**: if beta1/beta2 are too high, the optimizer reacts slowly to distribution shifts, then overreacts.

The too-small v case is the direct spike mechanism — a normal gradient normalized by a collapsed variance estimate becomes a huge update — while the too-large case fails quietly as a stall instead.

### Learning rate issues

Three schedule pathologies show up repeatedly:

- **Warmup too fast**: the learning rate ramps up too quickly in the first few hundred steps, before the optimizer state has stabilized.
- **Decay too slow**: late in training, a high learning rate produces instability because the model is near a local minimum.
- **Schedule restarts**: cosine restarts or step decays can cause temporary spikes as the optimizer re-stabilizes.

Warmup-related spikes hit early, decay-related spikes hit late, and restart-related spikes are transient.

### Genuine model instability at scale

Large models (70B+) can exhibit spontaneous spikes without an obvious cause. The Chinchilla and GPT-3 papers both report unexplained spikes during training. These may be related to:

- **Sharp minima**: the model finds a region of the loss landscape with high curvature, where small updates produce large loss changes.
- **Attention pattern collapse**: attention heads suddenly concentrate on a single token, producing high loss.
- **MoE routing instability**: in mixture-of-experts models (see [[Mixture of Experts]]), the router can suddenly route all tokens to one expert, producing a spike.

## Detecting spikes

### Loss monitoring

The most direct signal: monitor the training loss closely. A spike is typically defined as:

- **Spike threshold**: loss > 2× the moving average (or 3× the previous step).
- **NaN/Inf detection**: loss is `nan` or `inf`.

Production training runs log loss every step and alert on these conditions. A simple moving average over the last 100 steps is the baseline; exponential weighted moving averages respond faster.

### Gradient norm monitoring

Even when loss looks stable, gradient norms can signal trouble:

- **Gradient norm spike**: a 10× increase in the L2 norm of gradients signals an extreme update is coming.
- **Gradient norm collapse**: a 10× decrease suggests the optimizer is becoming unstable in a different way (vanishing gradients).

Log the gradient norm before clipping; the pre-clip norm is the signal. Collapse connects to the broader vanishing-gradient pathology covered in [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

### Weight norm monitoring

Track the L2 norm of each layer's weights. If a layer's weights suddenly grow or shrink, that's a sign of instability in that layer. Some training runs use weight clipping (rare) or per-layer learning rate scaling (also rare) based on these norms.

### Activation statistics

Track mean, std, and max of activations at each layer. Spikes in activation max (especially to inf) signal numerical issues. This is more useful for debugging than for online detection — the overhead of computing these statistics is non-trivial.

## Preventing spikes

### Gradient clipping

The single most effective preventive measure. Clip the global gradient norm to a threshold (typically 1.0):

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

This ensures no single update can move the weights by more than `lr * 1.0` in L2 norm. It doesn't prevent the cause of the spike, but it prevents the spike from causing a catastrophic update. Gradient clipping is so standard that essentially all production LLM training runs use it. The threshold (1.0) is a hyperparameter; lower values (0.5) are more conservative, higher values (5.0) are more permissive.

### Learning rate warmup

Linear warmup over the first N steps (typically 2000-10000) gradually increases the learning rate from 0 to the target. This gives the optimizer state time to stabilize before updates become large:

```python
from torch.optim.lr_scheduler import LambdaLR
import math

def get_warmup_cosine_schedule(optimizer, warmup_steps, total_steps):
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))
    return LambdaLR(optimizer, lr_lambda)
```

Without warmup, training a model from random init can spike immediately — the gradients are large, Adam's bias correction hasn't stabilized, and the optimizer hasn't yet built up its variance estimate, so a high learning rate amplifies the early chaos into divergence. Warmup is essential for Transformers.

### Loss scaling (FP16 only)

In FP16 training, loss scaling (see [[Mixed Precision Training]]) prevents gradient underflow. If you see spikes specifically in FP16 training, check the loss scaler — it may be skipping too many steps or scaling incorrectly.

### Weight decay

Weight decay (L2 regularization) keeps weights bounded, preventing the runaway weight growth that can cause spikes:

```python
optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=0.1)
```

A weight decay of 0.1 is standard for LLM training. Too high (1.0+) slows learning; too low (0.0) risks instability.

### Stable initialization

Initialization that produces reasonable activation magnitudes from the start reduces early-training instability:

- **He initialization** for ReLU-based networks.
- **Xavier initialization** for tanh/sigmoid.
- **Truncated normal** with small std (0.02) for Transformers (the BERT/GPT standard).

Bad initialization can cause spikes in the first few hundred steps before the optimizer stabilizes. The general mechanics of initialization live in [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]].

## Handling spikes when they happen

### Skip the bad batch

If a single batch produces a spike, skip it without updating:

```python
loss = model(batch)
if loss > spike_threshold:
    print(f"Spike detected: loss={loss.item()}")
    continue  # skip this batch
loss.backward()
optimizer.step()
```

This is effective for data-caused spikes. The bad batch is logged for later inspection.

### Checkpoint rollback

If the spike caused a bad update (the loss doesn't recover after a few steps), roll back to the last good checkpoint:

```python
if loss.isnan() or loss > 10 * moving_average:
    # Restore from checkpoint
    model.load_state_dict(torch.load(last_good_checkpoint))
    optimizer.load_state_dict(torch.load(last_good_optimizer))
    # Skip the bad batch, continue training
    continue
```

This is the production standard for large training runs. Without checkpoint rollback, a single NaN can waste weeks of compute.

### Reduce the learning rate

If spikes recur, reduce the learning rate by 2-10×. This is a sign that the model is near a sharp minimum where the current learning rate is too aggressive.

### Switch to BF16 (if using FP16)

If you're using FP16 and seeing frequent spikes, switch to BF16. The wider range eliminates most FP16-specific numerical issues.

### Inspect the data

When a spike occurs, save the offending batch. Inspect it manually:

- Are there unusual tokens?
- Is the text unusually long or short?
- Is it from a different distribution than the rest?
- Is it duplicated many times across the dataset?

Patterns in the bad batches often reveal data pipeline bugs.

## Debugging chronic spikes

If spikes happen frequently (more than once per billion tokens), something is systematically wrong. The debugging approach changes one variable at a time so that disappearing spikes localize the cause:

1. **Switch to FP32**: temporarily disable mixed precision. If spikes disappear, the cause is numerical.
2. **Reduce learning rate by 10×**: if spikes disappear, the learning rate is too high.
3. **Disable optimizer state**: use plain SGD instead of Adam. If spikes disappear, the optimizer state is the problem.
4. **Reduce batch size**: if spikes disappear, large-batch instability is the cause.
5. **Inspect data**: manually examine a sample of batches. Look for anomalies.
6. **Check model init**: verify that initial activations have reasonable magnitudes (mean ≈ 0, std ≈ 1).
7. **Profile gradient flow**: check that gradients at each layer have reasonable magnitudes. Vanishing or exploding gradients at specific layers indicate architectural issues.

## Production practices

### Frequent checkpointing

Save a checkpoint every 1000-5000 steps. Keep the last 3-5 checkpoints so you can roll back further if needed. Storage is cheap; retraining is not.

### Spike logging

When a spike occurs, log the step number, the loss value before and after, the gradient norm before clipping, the batch's source and content hash (for later inspection), and the optimizer state's beta1, beta2, and v statistics. This data is invaluable for diagnosing chronic issues.

### Automated recovery

Production training systems automatically detect spikes, roll back, and skip the offending batch:

```python
def train_step(model, batch, optimizer, moving_avg_loss, spike_threshold=5.0):
    loss = model(batch)

    # Check for spike
    if loss.isnan() or (moving_avg_loss > 0 and loss > spike_threshold * moving_avg_loss):
        log_spike(loss, batch)
        rollback_checkpoint(model, optimizer)
        return None  # signal: skip this step

    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    return loss.item()
```

This is the standard pattern for production training runs at scale: detect spike → rollback → skip batch → continue.

### Periodic FP32 validation

Every N steps (e.g., 10K), run a few batches in FP32 to validate that mixed precision isn't degrading quality. If FP32 loss diverges from BF16 loss, something is wrong with the mixed precision setup.

## See also

- [[Training and Adaptation MOC]] — orientation for the training and adaptation area.
- [[Mixed Precision Training]] — the source of many numerical spikes.
- [[Data Pipelines and Deduplication]] — bad data is a common spike cause.
- [[Distributed Training]] — distributed training adds spike complexity.
- [[Pretraining Objectives and Scaling Laws]] — the objectives being optimized at scale.
- [[Optimizers and Learning Rate Schedulers]] — optimizer and schedule choices that affect stability.
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the underlying gradient pathologies.
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]] — initialization's role in early stability.
