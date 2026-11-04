---
title: Common Mistakes and How to Fix Them
type: example
aliases:
  - "Q25 - Common Mistakes and How to Fix Them"
  - "Common Mistakes and How to Fix Them Quiz"
  - "CNN Common Mistakes Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - pytorch
  - debugging
  - optimizer-zero-grad
  - model-eval
  - batchnorm
  - dropout
  - gradient-accumulation
sources:
  - "Q25 - Common Mistakes and How to Fix Them"
created_index: 25
---

This quiz bank practices the two PyTorch mistakes that most often quietly corrupt a training run: forgetting `optimizer.zero_grad()`, so gradients accumulate across iterations, and forgetting `model.eval()`, so Dropout and BatchNorm keep their training-mode behavior during validation. Its twenty-nine questions — ten true-or-false, nine multiple choice, and ten matching — cover the erratic loss and sudden spikes left by stale gradients, the running-statistics contract of BatchNorm at evaluation, small-batch sensitivity, deliberate gradient accumulation every N batches, and the mode behavior of Dropout, BatchNorm, InstanceNorm, LayerNorm, and GroupNorm. The catalogue of failures and fixes lives in [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]], with the end-to-end routine in [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]] and the layer mechanics in [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]] and [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: four on gradient hygiene — accumulation, clearing cadence, and placement — five on the train-eval switching contract, and one on BatchNorm's running statistics. The false statements flip the direction of the bugs, claiming a steady loss decline from accumulated gradients or an inflated validation accuracy from a missing `model.eval()`, so trace what each omission actually does.

### Gradient hygiene

Four statements on accumulation across iterations, on the symptom that does and does not follow, on clearing every N batches under gradient accumulation, and on where the call may sit within an iteration.

> [!question] Forgetting to call `optimizer.zero_grad()` before each backward pass in PyTorch will cause gradients to accumulate across iterations.
>> [!success]- Answer
>> True

> [!question] The primary symptom of forgetting `optimizer.zero_grad()` is that training loss decreases steadily and consistently.
>> [!success]- Answer
>> False

> [!question] When using gradient accumulation, you should call `optimizer.zero_grad()` every N batches rather than every batch.
>> [!success]- Answer
>> True

> [!question] The placement of `optimizer.zero_grad()` doesn't matter as long as it's called once per training iteration.
>> [!success]- Answer
>> True

### Switching between train and eval

Five statements on calling `model.train()` for evaluation, Dropout's default at evaluation, the direction of the validation-accuracy error, automatic mode switching, and whether `torch.no_grad()` makes `model.eval()` redundant.

> [!question] When evaluating a model in PyTorch, it's important to call `model.train()` to ensure consistent results.
>> [!success]- Answer
>> False

> [!question] Dropout layers remain active during evaluation in PyTorch by default.
>> [!success]- Answer
>> False

> [!question] Forgetting `model.eval()` during evaluation typically causes validation accuracy to be higher than expected.
>> [!success]- Answer
>> False

> [!question] PyTorch automatically handles mode switching between training and evaluation for layers like Dropout and BatchNorm.
>> [!success]- Answer
>> False

> [!question] When using `torch.no_grad()`, you still need to call `model.eval()` to ensure proper behavior of certain layers.
>> [!success]- Answer
>> True

### BatchNorm at evaluation

One statement on which statistics BatchNorm uses once evaluation mode is set.

> [!question] BatchNorm layers in evaluation mode use the running mean and variance accumulated during training.
>> [!success]- Answer
>> True

## Multiple choice

Nine questions pair each mistake with its mechanics: what accumulates when `zero_grad()` is skipped, which symptoms do not belong to it, where the call belongs in the loop, and what BatchNorm and Dropout do when evaluation mode is forgotten. The small-batch scenario and the Linear-layer distractor reward knowing which layers are actually mode-sensitive.

### The zero_grad mistake

Three questions on what happens when the call is forgotten, on the symptom that is not caused by it, and on its typical placement in the training loop.

> [!question] What happens if you forget to call `optimizer.zero_grad()` before each backward pass?
> a) The gradients will be reset to zero, causing no updates
> b) Gradients from previous iterations accumulate, leading to incorrect updates
> c) The optimizer will automatically handle gradient accumulation
> d) PyTorch will raise an error
>> [!success]- Answer
>> b) Gradients from previous iterations accumulate, leading to incorrect updates

> [!question] Which of the following is NOT a symptom of forgetting `optimizer.zero_grad()`?
> a) Training loss decreases erratically
> b) Model becomes unstable after initial learning
> c) Loss suddenly spikes to very large values
> d) Training accuracy improves steadily
>> [!success]- Answer
>> d) Training accuracy improves steadily

> [!question] Where should `optimizer.zero_grad()` typically be placed in a training loop?
> a) After `optimizer.step()`
> b) Before `loss.backward()`
> c) After `loss.backward()`
> d) It doesn't matter as long as it's called once per iteration
>> [!success]- Answer
>> b) Before `loss.backward()`

### Evaluation mode

Four questions on the purpose of `model.eval()`, on what BatchNorm does without it, on the scenario that makes the omission most severe, and on the effect of Dropout staying active.

> [!question] What is the purpose of calling `model.eval()` before evaluation?
> a) To enable dropout for regularization
> b) To use batch statistics instead of running statistics
> c) To disable dropout and use running statistics for BatchNorm
> d) To increase model capacity
>> [!success]- Answer
>> c) To disable dropout and use running statistics for BatchNorm

> [!question] What happens to BatchNorm layers during evaluation if you forget to call `model.eval()`?
> a) They use the running mean and variance
> b) They use the current batch's mean and variance
> c) They are disabled
> d) They raise an error
>> [!success]- Answer
>> b) They use the current batch's mean and variance

> [!question] Which of these scenarios would make the impact of forgetting `model.eval()` most severe?
> a) Evaluating with large batch sizes
> b) Evaluating with small batch sizes
> c) Evaluating a model without BatchNorm
> d) Evaluating with `torch.no_grad()`
>> [!success]- Answer
>> b) Evaluating with small batch sizes

> [!question] What is the effect of Dropout layers remaining active during evaluation?
> a) Predictions become deterministic and stronger
> b) Predictions become stochastic and potentially weaker
> c) The model trains faster
> d) No effect on predictions
>> [!success]- Answer
>> b) Predictions become stochastic and potentially weaker

### Accumulation and mode-sensitive layers

Two questions on when gradient accumulation is intentional and on the layer that does not change behavior between modes.

> [!question] When would you intentionally use gradient accumulation in PyTorch?
> a) When you want to accumulate gradients across multiple mini-batches
> b) When you want to reset gradients more frequently
> c) When you want to disable gradient computation
> d) When you want to increase learning rate
>> [!success]- Answer
>> a) When you want to accumulate gradients across multiple mini-batches

> [!question] Which of the following is NOT a layer that behaves differently between training and evaluation modes in PyTorch?
> a) Dropout
> b) BatchNorm
> c) Linear
> d) InstanceNorm
>> [!success]- Answer
>> c) Linear

## Matching

Ten matching questions organize the material by mistake, by layer, and by function: the same three mistakes recur across fixes, symptoms, explanations, and impacts, while Dropout, BatchNorm, InstanceNorm, LayerNorm, and GroupNorm rotate through training-mode and evaluation-mode behaviors. The scenario group carries a piece of gradient-accumulation arithmetic — batch size 128 toward an effective 512 — that fixes the clearing cadence at every 4 batches, and the first fix group deliberately contains two identical entries, both resolved by `model.eval()`.

### Mistakes, fixes, and symptoms

Four questions matching the three mistakes with their correct fixes, their primary symptoms, their explanations, and their impact on model performance.

> [!question] Match the mistake with its correct fix.
>> [!example] Mistake
>> a) Forgetting optimizer.zero_grad()
>> b) Forgetting model.eval() during evaluation
>> c) Using training mode during validation
>
>> [!example] Fix
>> n) Call optimizer.zero_grad() before backward pass
>> o) Call model.eval() before evaluation
>> p) Call model.eval() before evaluation
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the mistake with its primary symptom.
>> [!example] Mistake
>> a) Forgetting optimizer.zero_grad()
>> b) Forgetting model.eval() during evaluation
>> c) Using training mode during validation
>
>> [!example] Symptom
>> n) Erratic training loss or sudden spikes
>> o) Lower than expected validation accuracy
>> p) Inconsistent validation metrics across runs
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the mistake with its explanation.
>> [!example] Mistake
>> a) Forgetting optimizer.zero_grad()
>> b) Forgetting model.eval() during evaluation
>> c) Using training mode during validation
>
>> [!example] Explanation
>> n) Gradients accumulate instead of being replaced
>> o) Dropout remains active, BatchNorm uses batch stats
>> p) Predictions become stochastic and unreliable
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the mistake with its impact on model performance.
>> [!example] Mistake
>> a) Forgetting optimizer.zero_grad()
>> b) Forgetting model.eval() during evaluation
>> c) Using training mode during validation
>
>> [!example] Impact
>> n) Training becomes unstable or oscillates
>> o) Validation accuracy degraded by 1-5%
>> p) Inconsistent results across validation runs
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Layer behavior by mode

Three questions on how Dropout, BatchNorm, and InstanceNorm behave in training mode, how Dropout, BatchNorm, and LayerNorm behave in evaluation mode, and the typical training-mode behavior of Dropout, BatchNorm, and GroupNorm.

> [!question] Match the layer with its behavior in training mode.
>> [!example] Layer
>> a) Dropout
>> b) BatchNorm
>> c) InstanceNorm
>
>> [!example] Behavior in Training Mode
>> n) Uses current batch's mean and variance
>> o) Randomly zeros neurons
>> p) Normalizes each channel separately
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the layer with its behavior in evaluation mode.
>> [!example] Layer
>> a) Dropout
>> b) BatchNorm
>> c) LayerNorm
>
>> [!example] Behavior in Evaluation Mode
>> n) Uses running mean and variance
>> o) All neurons active, outputs scaled
>> p) Normalizes across all features
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the layer with its typical training mode behavior.
>> [!example] Layer
>> a) Dropout
>> b) BatchNorm
>> c) GroupNorm
>
>> [!example] Training Mode Behavior
>> n) Normalizes within each group
>> o) Randomly drops neurons
>> p) Normalizes using current batch statistics
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Functions and their defaults

Two questions on the purpose of `optimizer.zero_grad()`, `model.eval()`, and `torch.no_grad()`, and on what `optimizer.step()`, `loss.backward()`, and `model.train()` do by default.

> [!question] Match the PyTorch function with its purpose.
>> [!example] Function
>> a) optimizer.zero_grad()
>> b) model.eval()
>> c) torch.no_grad()
>
>> [!example] Purpose
>> n) Disables gradient computation
>> o) Switches model to evaluation mode
>> p) Clears gradients from previous iteration
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the PyTorch component with its default behavior.
>> [!example] Component
>> a) optimizer.step()
>> b) loss.backward()
>> c) model.train()
>
>> [!example] Default Behavior
>> n) Switches layers to training mode
>> o) Accumulates gradients with existing ones
>> p) Updates model parameters using gradients
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### When to clear the gradients

One question matching the standard loop, a gradient-accumulation setup, and model evaluation with the action each calls for.

> [!question] Match the scenario with its recommended action.
>> [!example] Scenario
>> a) Standard training loop
>> b) Gradient accumulation with batch size 128, desired effective batch size 512
>> c) Model evaluation
>
>> [!example] Action
>> n) Call optimizer.zero_grad() every batch
>> o) Call optimizer.zero_grad() every 4 batches
>> p) Call model.eval() and use torch.no_grad()
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

## See also

- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/PyTorch Implementation Basics|PyTorch Implementation Basics]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Batch Normalization|Batch Normalization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Dropout and Regularization|Dropout and Regularization]]
- [[Glossary MOC]]
