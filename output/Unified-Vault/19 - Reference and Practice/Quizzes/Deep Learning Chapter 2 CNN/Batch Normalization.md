---
title: Batch Normalization
type: example
aliases:
  - "Q16 - Batch Normalization"
  - "Batch Normalization Quiz"
  - "BN Quiz"
  - "Internal Covariate Shift Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - batch-normalization
  - internal-covariate-shift
  - dying-relu
  - vanishing-gradients
  - training-stability
  - optimization
sources:
  - "Q16 - Batch Normalization"
created_index: 24
---

This quiz bank practices batch normalization and the problem it was introduced to solve: internal covariate shift, the changing distribution of activations between layers during training. Its twenty-nine questions — ten true-or-false, nine multiple choice, and ten matching — cover the 2015 introduction by Sergey Ioffe and Christian Szegedy, the non-stationary landscape each layer sees when distributions drift, the saturated-sigmoid and dying-ReLU pathologies that distribution shifts cause, the careful initialization and tiny learning rates that pre-BN training demanded, and the later Santurkar et al. challenge to the original explanation of BN's benefits. The concepts are developed in [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]], alongside [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]] and [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: two on the technique's origins and reach, two on what internal covariate shift is and does to the landscape, two on the competing explanations of why BN helps, two on pre-BN practice and what BN does not fix, and two on the activation pathologies that distribution shifts cause. The false statements overclaim — BN eliminating the need for careful initialization, large learning rates being safe before BN, a stationary landscape under shift — so weigh each against the historical record.

### Origins and reach

Two statements on who introduced the technique and where it now sits in modern architectures.

> [!question] Batch Normalization was introduced by Sergey Ioffe and Christian Szegedy in 2015.
>> [!success]- Answer
>> True

> [!question] Batch Normalization is embedded in virtually every successful CNN architecture from ResNet to EfficientNet.
>> [!success]- Answer
>> True

### Internal covariate shift

Two statements on the definition of the shift and the kind of landscape it leaves each layer optimizing over.

> [!question] Internal Covariate Shift refers to the shifting distribution of activations between layers during training.
>> [!success]- Answer
>> True

> [!question] Internal Covariate Shift makes the optimization landscape effectively stationary from the perspective of each individual layer.
>> [!success]- Answer
>> False

### Competing explanations

Two statements on what the original BN paper claimed as the primary benefit, and what the later "How Does Batch Normalization Help Optimization?" paper suggested.

> [!question] According to the original BN paper, the primary benefit of Batch Normalization is reducing Internal Covariate Shift.
>> [!success]- Answer
>> True

> [!question] The "How Does Batch Normalization Help Optimization?" paper suggested that BN's benefits may not primarily come from reducing ICS.
>> [!success]- Answer
>> True

### Pre-BN practice and the limits of BN

Two statements on the learning rates practitioners could get away with before BN, and on whether BN removes the need for careful initialization.

> [!question] Before Batch Normalization, practitioners could use large learning rates without causing divergence.
>> [!success]- Answer
>> False

> [!question] Batch Normalization completely eliminates the need for careful weight initialization.
>> [!success]- Answer
>> False

### Activation pathologies

Two statements on the dying ReLU problem and on what saturated sigmoid inputs do to gradients.

> [!question] The dying ReLU problem occurs when activations are pushed into the negative regime where ReLU outputs zero.
>> [!success]- Answer
>> True

> [!question] When using sigmoid activation functions, input drift into the saturated regime causes gradients to become vanishingly small.
>> [!success]- Answer
>> True

## Multiple choice

Nine questions work through the problem BN addresses, how a weight update in one layer disturbs the next, the notation of the formal description, and the activation failures that shifting distributions produce. Several distractors name real phenomena attached to the wrong cause, so trace each symptom back to its actual mechanism.

### The problem BN addresses

Two questions on the problem itself and on what makes the landscape effectively non-stationary for each layer.

> [!question] What problem does Batch Normalization primarily address?
> a) Vanishing gradients
> b) Internal Covariate Shift
> c) Overfitting
> d) Computational complexity
>> [!success]- Answer
>> b) Internal Covariate Shift

> [!question] What makes the optimization landscape effectively non-stationary from the perspective of each individual layer?
> a) Fixed input distributions
> b) Constant learning rates
> c) Internal Covariate Shift
> d) Batch Normalization
>> [!success]- Answer
>> c) Internal Covariate Shift

### How the shift propagates

Three questions on what happens to layer k+1 when layer k's weights change, what the shift does to training speed, and what the distribution of activations depends on.

> [!question] What happens to layer k+1 when the weights of layer k are updated?
> a) Its input distribution remains the same
> b) Its input distribution changes
> c) It becomes permanently deactivated
> d) It requires no further adaptation
>> [!success]- Answer
>> b) Its input distribution changes

> [!question] What is a consequence of Internal Covariate Shift on training speed?
> a) Training becomes significantly faster
> b) Learning rates can be increased without issues
> c) Training is dramatically slowed down
> d) No effect on training speed
>> [!success]- Answer
>> c) Training is dramatically slowed down

> [!question] What does the distribution of activations x depend on?
> a) Only the parameters of the current layer
> b) Only the input data
> c) All parameters of the preceding layers
> d) The learning rate
>> [!success]- Answer
>> c) All parameters of the preceding layers

### Activation failures

Two questions on the gradient problem that distribution shifts cause under sigmoid, and on what happens when ReLU inputs go negative.

> [!question] What problem can occur with sigmoid activation functions due to distribution shifts?
> a) Exploding gradients
> b) Vanishing gradients
> c) Dead neurons
> d) Overfitting
>> [!success]- Answer
>> b) Vanishing gradients

> [!question] What happens when ReLU activations are pushed into the negative regime?
> a) They output values greater than 1
> b) They output zero, causing the "dying ReLU" problem
> c) They become linear
> d) They explode
>> [!success]- Answer
>> b) They output zero, causing the "dying ReLU" problem

### Notation and pre-BN practice

Two questions on the symbol for the mini-batch size in the formal description, and on what training deep networks required before BN.

> [!question] What is the mini-batch size denoted as in the formal description of Internal Covariate Shift?
> a) k
> b) n
> c) m
> d) θ
>> [!success]- Answer
>> c) m

> [!question] What was required before Batch Normalization when training deep networks?
> a) Larger learning rates
> b) Careful initialization, tiny learning rates, and long convergence times
> c) No special initialization techniques
> d) Fewer layers in the network
>> [!success]- Answer
>> b) Careful initialization, tiny learning rates, and long convergence times

## Matching

Ten matching questions pair the core terms with their descriptions and notation, concepts with their effects, training difficulties with their causes, architectural elements with their relationships, challenges with their solutions, activation functions with their failure modes, researchers with their contributions, and eras with their impacts. Two of the mappings swap the first two targets, so anchor each pair on its definition rather than its position in the list.

### Terms and notation

Two questions matching the technique's vocabulary to its descriptions, and the symbols of the formal description to their roles.

> [!question] Match the following terms with their descriptions.
>> [!example] Group A
>> a) Batch Normalization
>> b) Internal Covariate Shift
>> c) Dying ReLU
>
>> [!example] Group B
>> n) Technique to normalize layer inputs
>> o) Shifting distribution of activations between layers
>> p) ReLU outputs zero when inputs are negative
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following network components with their roles in Internal Covariate Shift.
>> [!example] Group A
>> a) θj
>> b) x
>> c) Θ
>
>> [!example] Group B
>> n) Parameters of layer j
>> o) Activations of a layer
>> p) All parameters of preceding layers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Effects and their causes

Two questions on what saturated activations and small learning rates lead to, and on what stands behind slow convergence, instability, and the need for small learning rates.

> [!question] Match the following concepts with their effects.
>> [!example] Group A
>> a) Saturated sigmoid
>> b) Small learning rates
>> c) Poor initialization
>
>> [!example] Group B
>> n) Vanishing gradients
>> o) Slow convergence
>> p) Training never recovers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following training difficulties with their causes.
>> [!example] Group A
>> a) Slow convergence
>> b) Optimization instability
>> c) Need for small learning rates
>
>> [!example] Group B
>> n) Non-stationary optimization landscape
>> o) Perpetual re-adaptation to new distributions
>> p) Prevents destructive updates
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Architecture and layers

Two questions on how layers feed one another, and on how much distribution shift the earlier, later, and middle layers experience.

> [!question] Match the following architectural elements with their relationships.
>> [!example] Group A
>> a) Layer k
>> b) Layer k+1
>> c) Output
>
>> [!example] Group B
>> n) Receives inputs from layer k
>> o) Outputs serve as inputs to layer k+1
>> p) Final result of the network
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the following network layers with their experiences during training.
>> [!example] Group A
>> a) Earlier layers
>> b) Later layers
>> c) Middle layers
>
>> [!example] Group B
>> n) Experience more distribution shifts
>> o) Experience fewer distribution shifts
>> p) Experience moderate distribution shifts
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Challenges and their solutions

Two questions on the remedies for the shift and the activation failures, and on the issues each activation function develops under distribution shifts.

> [!question] Match the following optimization challenges with their solutions.
>> [!example] Group A
>> a) Internal Covariate Shift
>> b) Vanishing gradients
>> c) Dying ReLU
>
>> [!example] Group B
>> n) Batch Normalization
>> o) Avoiding saturated regime
>> p) Careful initialization
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following activation functions with their issues related to distribution shifts.
>> [!example] Group A
>> a) Sigmoid
>> b) ReLU
>> c) Tanh
>
>> [!example] Group B
>> n) Saturates for large positive/negative values
>> o) Outputs zero for negative inputs
>> p) Saturates for extreme values
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Researchers and eras

Two questions on the people behind the technique and its critique, and on what each historical period demanded or enabled.

> [!question] Match the following researchers with their contributions.
>> [!example] Group A
>> a) Ioffe and Szegedy
>> b) Santurkar et al.
>> c) Xavier and He
>
>> [!example] Group B
>> n) Introduced Batch Normalization
>> o) Questioned the primary benefit of BN
>> p) Developed initialization techniques
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following historical developments with their impacts on deep learning.
>> [!example] Group A
>> a) Pre-Batch Normalization era
>> b) Post-Batch Normalization era
>> c) Santurkar et al. findings
>
>> [!example] Group B
>> n) Required careful initialization and small learning rates
>> o) Enabled faster training and more layers
>> p) Challenged original explanation of BN benefits
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

## See also

- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[Activation Functions]]
- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Weight Initialization|Weight Initialization]]
- [[The Vanishing and Exploding Gradient Problems]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[Exercises Solved and Explained]]
- [[Glossary MOC]]
