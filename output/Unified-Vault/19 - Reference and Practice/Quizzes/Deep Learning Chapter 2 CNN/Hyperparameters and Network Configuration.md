---
title: Hyperparameters and Network Configuration
type: example
aliases:
  - "Q7 - Hyperparameters and Network Configuration"
  - "Hyperparameters and Network Configuration Quiz"
  - "Network Configuration Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - hyperparameters
  - cnn
  - filter-count
  - receptive-field
  - underfitting
  - overfitting
  - computational-cost
sources:
  - "Q7 - Hyperparameters and Network Configuration"
created_index: 32
---

This quiz bank practices the architectural hyperparameters that shape a CNN before training ever begins: how many filters each convolutional layer carries, how filter size and network depth trade off, and how the standard progression grows channels while spatial resolution shrinks. Its thirty questions — ten true-or-false, ten multiple choice, and ten matching — cover the representational-capacity role of filter count, the underfitting and overfitting symptoms of too few or too many filters, receptive-field arithmetic for stacked 3×3 convolutions, and the parameter counts that separate convolutional, fully connected, and pooling layers. The full treatment lives in [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]], with the operator mathematics in [[06 - Computer Vision/Core Operators and Geometry/The Convolution Operation|The Convolution Operation]] and [[06 - Computer Vision/Core Operators and Geometry/Receptive Fields and 1x1 Convolutions|Receptive Fields and 1x1 Convolutions]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: four on what filter count does to capacity, underfitting, and generalization, two on the parameter-versus-hyperparameter distinction, and four on the progression convention and its arithmetic. The false statements lean on absolutes — more filters always improving performance or generalization — and on receptive-field arithmetic that equates a single 5×5 convolution with two consecutive 3×3 convolutions.

### Filter count and representational capacity

Four statements on filters as capacity, on the claim that more is always better in performance and in generalization, and on underfitting from too few.

> [!question] The number of filters in a convolutional layer determines the representational capacity of that layer.
>> [!success]- Answer
>> True

> [!question] Increasing the number of filters in a convolutional layer always improves model performance.
>> [!success]- Answer
>> False

> [!question] Too few filters in a convolutional layer can lead to underfitting.
>> [!success]- Answer
>> True

> [!question] More filters always lead to better generalization on validation data.
>> [!success]- Answer
>> False

### Hyperparameters versus parameters

Two statements on whether hyperparameters are learned during training and whether the two terms are synonymous.

> [!question] Hyperparameters are learned during the training process.
>> [!success]- Answer
>> False

> [!question] Parameters and hyperparameters are synonymous terms in deep learning.
>> [!success]- Answer
>> False

### Progression, receptive fields, and compute

Four statements on the increase-filters-as-resolution-falls convention, the receptive field of a 5×5 against two stacked 3×3 convolutions, and the computational consequences of doubling.

> [!question] The standard progression in CNN architectures is to increase the number of filters as spatial resolution decreases.
>> [!success]- Answer
>> True

> [!question] A single 5×5 convolution has the same receptive field as two consecutive 3×3 convolutions.
>> [!success]- Answer
>> False

> [!question] Doubling the number of filters in a layer roughly doubles the computation required for that layer.
>> [!success]- Answer
>> True

> [!question] The doubling pattern of filters across layers maintains approximately equal computational cost per layer.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions work from capacity planning to diagnosis: starting progressions for ImageNet-scale and CIFAR-10 data, what happens as spatial resolution falls, what a training loss that plateaus above zero signals, and what doubling a layer's filters does to its FLOPs. The filter ladders in the options differ by a factor of two at each rung, so read the direction of each progression carefully.

### Sizing the filter progression

Four questions on the primary effect of too many filters, the starting ladder for ImageNet-scale data, the recommendation for smaller datasets like CIFAR-10, and the fix for an underfitting model with too few filters.

> [!question] What is the primary effect of having too many filters in a convolutional layer?
> a) Reduced computational cost
> b) Underfitting
> c) Overfitting and computational waste
> d) No change in model performance
>> [!success]- Answer
>> c) Overfitting and computational waste

> [!question] What is a good starting point for a simple CNN on ImageNet-scale data?
> a) 16→32→64→128 filters
> b) 64→128→256→512 filters
> c) 128→256→512→1024 filters
> d) 32→64→128→256 filters
>> [!success]- Answer
>> b) 64→128→256→512 filters

> [!question] What happens when spatial resolution decreases in a CNN?
> a) The number of filters should decrease
> b) The number of filters should increase
> c) The number of filters should remain constant
> d) The number of filters becomes irrelevant
>> [!success]- Answer
>> b) The number of filters should increase

> [!question] What is a recommended approach for a CNN on smaller datasets like CIFAR-10?
> a) Start with 128→256→512→1024 filters
> b) Start with 64→128→256→512 filters
> c) Start with 32→64→128 filters
> d) Start with 16→32→64→128 filters
>> [!success]- Answer
>> c) Start with 32→64→128 filters

### Receptive fields and stacking

Two questions on the definition of a receptive field and on what stacking multiple 3×3 convolutions does to it.

> [!question] What is the receptive field of a neuron in a convolutional layer?
> a) The size of the input image
> b) The region in the input that can influence that neuron's activation
> c) The number of filters in the next layer
> d) The size of the output feature map
>> [!success]- Answer
>> b) The region in the input that can influence that neuron's activation

> [!question] What is the effect of stacking multiple 3×3 convolutions?
> a) The receptive field remains 3×3
> b) The receptive field becomes smaller
> c) The receptive field grows larger than a single 3×3 convolution
> d) The receptive field becomes exactly the same as a single 9×9 convolution
>> [!success]- Answer
>> c) The receptive field grows larger than a single 3×3 convolution

### Symptoms, fixes, and costs

Four questions on the observable symptom of underfitting, the computational effect of doubling filters, the benefit of the spatial-down-channels-up progression, and the remedy when too few filters are the cause.

> [!question] What is a symptom of underfitting in a CNN with too few filters?
> a) Large gap between training and validation accuracy
> b) High training loss that plateaus above zero
> c) Perfect training accuracy but poor validation accuracy
> d) Extremely fast convergence
>> [!success]- Answer
>> b) High training loss that plateaus above zero

> [!question] What is the approximate effect of doubling the number of filters in a layer?
> a) Halves the computation
> b) No change in computation
> c) Doubles the FLOPs for that layer
> d) Quadruples the computation
>> [!success]- Answer
>> c) Doubles the FLOPs for that layer

> [!question] What is the benefit of the progression where spatial resolution decreases while channels increase?
> a) Reduces total memory usage
> b) Preserves the total number of activations across layers
> c) Increases model complexity
> d) Reduces training time
>> [!success]- Answer
>> b) Preserves the total number of activations across layers

> [!question] What should be done if a model with too few filters is underfitting?
> a) Reduce the number of filters
> b) Add more regularization
> c) Increase the number of filters
> d) Decrease the learning rate
>> [!success]- Answer
>> c) Increase the number of filters

## Matching

Ten matching questions pair the architectural levers with their effects, the failure modes with their symptoms and remedies, and the layer types with their parameter counts. Two groups return to the same trio — too few filters, too many filters, balanced progression — first from the angle of impact and then of observable symptom, and the parameter-count group rewards checking the k×k×C_in arithmetic before pairing.

### Architectural levers

Three questions matching hyperparameters with their descriptions, CNN properties with their effects, and design principles with their applications.

> [!question] Match the architectural hyperparameter with its description.
>> [!example] Hyperparameter
>> a) Number of Filters
>> b) Filter Size
>> c) Network Depth
>
>> [!example] Description
>> n) Determines the size of the local region each filter considers
>> o) Number of layers in the network
>> p) Controls the representational capacity of each layer
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the CNN property with its effect.
>> [!example] Property
>> a) More filters
>> b) Larger filter size
>> c) Deeper network
>
>> [!example] Effect
>> n) Higher computational cost
>> o) Larger receptive field
>> p) Higher representational capacity
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the design principle with its application.
>> [!example] Principle
>> a) Increasing filters with depth
>> b) Using small filter sizes (3×3)
>> c) Adding regularization
>
>> [!example] Application
>> n) Controls overfitting
>> o) Preserves computational balance
>> p) Builds larger receptive fields efficiently
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Filter progressions by dataset

One question pairing the three filter ladders with the dataset scales they suit.

> [!question] Match the filter progression with the appropriate dataset.
>> [!example] Filter Progression
>> a) 64→128→256→512
>> b) 32→64→128
>> c) 16→32→64→128
>
>> [!example] Dataset
>> n) ImageNet-scale data
>> o) Very small datasets
>> p) CIFAR-10
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

### Failure modes and remedies

Three questions on problems and their solutions, layer characteristics and their impacts, and training issues with their observable symptoms.

> [!question] Match the problem with its potential solution.
>> [!example] Problem
>> a) Underfitting
>> b) Overfitting
>> c) Computational imbalance
>
>> [!example] Solution
>> n) Add regularization (dropout, weight decay)
>> o) Increase number of filters
>> p) Adjust filter progression to maintain computational balance
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the layer characteristic with its impact.
>> [!example] Characteristic
>> a) Too few filters
>> b) Too many filters
>> c) Balanced filter progression
>
>> [!example] Impact
>> n) High training loss, underfitting
>> o) Large gap between training and validation accuracy
>> p) Maintains computational balance across layers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the training issue with its observable symptom.
>> [!example] Issue
>> a) Underfitting due to too few filters
>> b) Overfitting due to too many filters
>> c) Computational bottleneck
>
>> [!example] Symptom
>> n) Large gap between training and validation accuracy
>> o) High training loss that plateaus above zero
>> p) Uneven computation across layers
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Parameter counts by layer type

One question on the parameter count carried by a convolutional layer, a fully connected layer, and a pooling layer.

> [!question] Match the architectural element with its parameter count.
>> [!example] Element
>> a) Convolutional layer with k×k filters and C_in input channels
>> b) Fully connected layer with N inputs and M outputs
>> c) Pooling layer
>
>> [!example] Parameter Count
>> n) k×k×C_in×M parameters
>> o) k×k×C_in + 1 parameters per filter
>> p) Zero parameters
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Concepts in definition

One question defining the receptive field against the hyperparameter and parameter terms.

> [!question] Match the concept with its definition.
>> [!example] Concept
>> a) Receptive Field
>> b) Hyperparameter
>> c) Parameter
>
>> [!example] Definition
>> n) Values set before training that control model architecture or training
>> o) Values learned during training (weights and biases)
>> p) The region in input space that affects a particular neuron's activation
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Layer roles across depth

One question on what the early, middle, and final layers of a CNN typically do.

> [!question] Match the CNN component with its typical function.
>> [!example] Component
>> a) Early convolutional layers
>> b) Middle convolutional layers
>> c) Final fully connected layers
>
>> [!example] Function
>> n) High-level feature extraction and classification
>> o) Pattern detection (edges, textures)
>> p) Abstract feature representation
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

## See also

- [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
- [[The Convolution Operation]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[The Convolution Operation Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/PyTorch Implementation Basics|PyTorch Implementation Basics]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Weight Initialization|Weight Initialization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[Glossary MOC]]
