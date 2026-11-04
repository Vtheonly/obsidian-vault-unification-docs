---
title: Dropout and Regularization
type: example
aliases:
  - "Q17 - Dropout and Regularization"
  - "Dropout and Regularization Quiz"
  - "Dropout Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - dropout
  - regularization
  - overfitting
  - inverted-dropout
  - early-stopping
  - co-adaptation
  - ensemble
sources:
  - "Q17 - Dropout and Regularization"
created_index: 29
---

This quiz bank practices the diagnosis of overfitting and the regularization toolkit that counters it, with dropout as the centerpiece. Its twenty-seven questions — ten true-or-false, nine multiple choice, and eight matching — cover the training-versus-validation gap, the Bernoulli mask and the inverted-dropout scaling that preserves expected values, co-adaptation and the ensemble argument, and companion techniques such as early stopping, L1 and L2 penalties, data augmentation, and batch normalization. The full treatment lives in [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]], with the surrounding toolkit in [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]] and [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]; decide on an answer before unfolding it.

## True or false

Ten statements open the quiz: two on recognizing overfitting, four on dropout's mechanics and history, and four on the wider regularization toolkit of purpose, co-adaptation, early stopping, and ensembles. The false statements reverse well-worn definitions — the dropout rate as a keep-probability, regularization as complexity-increasing — so check each claim against the formal statement of the idea.

### Recognizing overfitting

Two statements on the definition of overfitting and the train-versus-validation gap that reveals it.

> [!question] Overfitting occurs when a model performs well on training data but poorly on validation data.
>> [!success]- Answer
>> True

> [!question] A training accuracy of 99% and validation accuracy of 75% indicates a healthy model that generalizes well.
>> [!success]- Answer
>> False

### Dropout mechanics and history

Four statements on dropout's origins, the expected-value preservation of inverted dropout, the meaning of the rate p, and what happens at test time.

> [!question] Dropout was introduced by Geoffrey Hinton and his team in 2014.
>> [!success]- Answer
>> True

> [!question] Inverted dropout ensures that the expected value of each neuron's output remains the same during training.
>> [!success]- Answer
>> True

> [!question] The dropout rate p determines the probability that a neuron will be kept rather than dropped.
>> [!success]- Answer
>> False

> [!question] At test time, dropout is applied with the same random mask as during training.
>> [!success]- Answer
>> False

### Regularization, co-adaptation, and ensembles

Four statements on what regularization is for, how dropout fights co-adaptation, when early stopping kicks in, and what the ensemble view really claims.

> [!question] The primary purpose of regularization is to increase model complexity.
>> [!success]- Answer
>> False

> [!question] Dropout prevents co-adaptation by forcing neurons to learn features that are individually useful.
>> [!success]- Answer
>> True

> [!question] Early stopping is a regularization technique that involves stopping training when validation loss starts increasing.
>> [!success]- Answer
>> True

> [!question] Ensemble averaging is a benefit of dropout because it trains multiple models simultaneously.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions probe the diagnostic signals of overfitting and the arithmetic of dropout in detail. The wrong options swap the direction of a scaling factor or quietly redefine a term — p as the keep-probability, ensemble averaging as literally training many models — so pin down the definitions before committing.

### Diagnosing overfitting

Four questions on the primary indicator, the factor that is not a cause, the capacity extreme, and the point where validation loss turns.

> [!question] What is the primary indicator that a model is overfitting?
> a) High training accuracy but low validation accuracy
> b) Low training accuracy but high validation accuracy
> c) Both training and validation accuracy are low
> d) Both training and validation accuracy are high but decreasing
>> [!success]- Answer
>> a) High training accuracy but low validation accuracy

> [!question] Which of the following is NOT a primary cause of overfitting?
> a) Too many parameters relative to training data
> b) Too little training data
> c) Too many epochs
> d) Too few layers in the network
>> [!success]- Answer
>> d) Too few layers in the network

> [!question] What is the "death by capacity" problem?
> a) When a model has too few parameters to learn the data
> b) When a model has too many parameters and can memorize the training data
> c) When a model's capacity is perfectly matched to the data complexity
> d) When a model's capacity decreases during training
>> [!success]- Answer
>> b) When a model has too many parameters and can memorize the training data

> [!question] What is the "divergence point" in the context of overfitting?
> a) The point where training and validation accuracy are equal
> b) The point where training accuracy reaches 100%
> c) The point where validation loss starts increasing while training loss continues decreasing
> d) The point where the model's capacity becomes too high
>> [!success]- Answer
>> c) The point where validation loss starts increasing while training loss continues decreasing

### Dropout arithmetic and behavior

Four questions on the scaling of surviving neurons, the full mathematical operation on an activation, how co-adaptation is prevented, and what happens at test time.

> [!question] What happens to the outputs of neurons that are not dropped during training with dropout?
> a) They remain unchanged
> b) They are scaled up by a factor of 1/(1-p)
> c) They are scaled down by a factor of (1-p)
> d) They are replaced with zeros
>> [!success]- Answer
>> b) They are scaled up by a factor of 1/(1-p)

> [!question] What is the mathematical operation performed by dropout on a neuron's activation h_i with probability p?
> a) Set h_i to zero
> b) Set h_i to h_i/(1-p)
> c) Set h_i to r_i * h_i where r_i is Bernoulli(1-p)
> d) Set h_i to r_i * h_i/(1-p) where r_i is Bernoulli(1-p)
>> [!success]- Answer
>> d) Set h_i to r_i * h_i/(1-p) where r_i is Bernoulli(1-p)

> [!question] How does dropout help prevent co-adaptation of neurons?
> a) By forcing all neurons to learn the same features
> b) By randomly dropping neurons and preventing dependencies
> c) By scaling down all neuron outputs
> d) By increasing the number of neurons in each layer
>> [!success]- Answer
>> b) By randomly dropping neurons and preventing dependencies

> [!question] What is the effect of dropout at test time?
> a) The same dropout mask is applied as during training
> b) No dropout is applied, and all neurons are used
> c) A different, fixed dropout mask is applied
> d) Dropout is applied with a higher rate than during training
>> [!success]- Answer
>> b) No dropout is applied, and all neurons are used

### The ensemble effect

One question on what dropout's ensemble claim actually says.

> [!question] Which of the following statements about dropout's ensemble effect is true?
> a) It trains 2^n independent models where n is the number of neurons
> b) It approximates an ensemble average of sub-networks during training
> c) It requires training multiple models separately and then averaging their outputs
> d) It only works for convolutional neural networks, not fully connected networks
>> [!success]- Answer
>> b) It approximates an ensemble average of sub-networks during training

## Matching

Eight matching questions pair the vocabulary with its definitions, techniques with their mechanisms, causes with their descriptions, and formulas with the quantities they express. The groups are shuffled independently, and in one question two statements share a single implication, so decide from the definitions rather than the letter positions.

### Definitions and mechanisms

Two questions matching items with their descriptions and techniques with their primary mechanisms.

> [!question] Match the item with its description.
>> [!example] Group A
>> a) Dropout
>> b) Overfitting
>> c) Inverted dropout
>> d) Co-adaptation
>
>> [!example] Group B
>> n) Scaling neuron outputs to preserve expected value
>> o) Neurons developing interdependencies where specific neurons only produce useful outputs when others are active
>> p) Randomly setting a fraction of neurons to zero during training
>> q) Model memorizing training data without generalizing to unseen data
>
>> [!success]- Answer
>> a) -> p)
>> b) -> q)
>> c) -> n)
>> d) -> o)

> [!question] Match the regularization technique with its primary mechanism.
>> [!example] Group A
>> a) Dropout
>> b) Early stopping
>> c) L2 regularization
>> d) Data augmentation
>
>> [!example] Group B
>> n) Penalizing large weights to encourage simpler models
>> o) Stopping training when validation performance degrades
>> p) Randomly dropping neurons to create sub-networks
>> q) Creating modified versions of training data
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)
>> d) -> q)

### Causes and formulations

Two questions on what causes overfitting and the formulas dropout is built on.

> [!question] Match the cause of overfitting with its description.
>> [!example] Group A
>> a) Too many parameters
>> b) Too little data
>> c) Too many epochs
>> d) High learning rate
>
>> [!example] Group B
>> n) Model memorizes noise rather than learning general patterns
>> o) Model has too many degrees of freedom relative to data
>> p) Insufficient examples to learn true data distribution
>> q) Training for too long causes fitting of training noise
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> q)
>> d) -> n)

> [!question] Match the mathematical concept with its correct formulation in dropout.
>> [!example] Group A
>> a) Dropout mask
>> b) Dropout output
>> c) Expected value preservation
>> d) Dropout rate
>
>> [!example] Group B
>> n) r_i ~ Bernoulli(1-p)
>> o) E[tilde{h}_i] = h_i
>> p) p determines probability of dropping a neuron
>> q) tilde{h}_i = r_i * h_i / (1-p)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> q)
>> c) -> o)
>> d) -> p)

### Benefits and implications

Two questions on what dropout buys and what the training-validation gaps imply.

> [!question] Match the dropout benefit with its explanation.
>> [!example] Group A
>> a) Prevents co-adaptation
>> b) Ensemble effect
>> c) Adds noise for robustness
>> d) Reduces model capacity
>
>> [!example] Group B
>> n) Forces neurons to learn individually useful features
>> o) Approximates averaging of multiple models
>> p) Makes network more resistant to input variations
>> q) Decreases number of parameters in the network
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

> [!question] Match the statement about overfitting with its correct implication.
>> [!example] Group A
>> a) Training accuracy >> Validation accuracy
>> b) Model performs well on training but poorly on test
>> c) Small gap between training and validation performance
>> d) Large gap between training and validation performance
>
>> [!example] Group B
>> n) Indicates good generalization
>> o) Suggests severe overfitting
>> p) Diagnostic signal of overfitting
>> q) May indicate underfitting
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)
>> d) -> o)

### Use cases and scenarios

Two questions on when each technique fits best and how dropout behaves across training and inference.

> [!question] Match the regularization technique with its typical use case.
>> [!example] Group A
>> a) Dropout
>> b) Early stopping
>> c) L1 regularization
>> d) Batch normalization
>
>> [!example] Group B
>> n) Effective for large networks with many parameters
>> o) Useful when training time is limited
>> p) Particularly effective for sparse feature selection
>> q) Helps stabilize training but not primarily a regularization technique
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

> [!question] Match the dropout scenario with its correct description.
>> [!example] Group A
>> a) Training with dropout
>> b) Test/inference with dropout
>> c) Training without dropout
>> d) Dropout rate p = 0.5
>
>> [!example] Group B
>> n) All neurons used with no scaling
>> o) Random subset of neurons used with scaling
>> p) All neurons used with full weights
>> q) Maximum regularization effect
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

## See also

- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Batch Normalization|Batch Normalization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Data Augmentation|Data Augmentation]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Weight Initialization|Weight Initialization]]
- [[Glossary MOC]]
