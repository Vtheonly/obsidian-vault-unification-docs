---
title: VGG16 Architecture Deep Dive
type: example
aliases:
  - "Q9 - VGG16 Architecture Deep Dive"
  - "VGG16 Architecture Deep Dive Quiz"
  - "VGG16 Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - vgg16
  - cnn-architectures
  - receptive-field
  - convolution
  - ilsvrc-2014
  - parameter-counting
sources:
  - "Q9 - VGG16 Architecture Deep Dive"
created_index: 46
---

This quiz bank practices VGG-16, the architecture that showed depth built from small, uniform kernels could outperform large mixed filters. Its twenty-nine questions — ten true-or-false, ten multiple choice, and nine matching — cover the Oxford team behind it, the four configurations from VGG-11 to VGG-19, the receptive-field mathematics that lets three 3×3 convolutions match one 7×7, the parameter arithmetic in C-notation, and the fully connected bottleneck. The deep dive lives in [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]], with the wider story in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: four on VGG-16 as a landmark — its authors, its filters, its ILSVRC 2014 showing, its input — five on receptive fields and stacked small convolutions, and one on the fully connected bottleneck. The false statements are the classic traps: filter mixtures VGG never used and receptive-field arithmetic that is off by one.

### The VGG-16 landmark

Four statements on who designed the network, which filters it standardizes on, what it demonstrated about depth, and the input it accepts.

> [!question] VGG-16 was designed by Karen Simonyan and Andrew Zisserman from the University of Oxford.
>> [!success]- Answer
>> True

> [!question] VGG-16 uses a mixture of filter sizes including 11×11, 5×5, and 3×3 convolutional layers.
>> [!success]- Answer
>> False

> [!question] VGG-16 demonstrated that deeper networks consistently outperformed shallower ones in the ILSVRC 2014 competition.
>> [!success]- Answer
>> True

> [!question] VGG-16 accepts RGB images of size 256×256×3 as input.
>> [!success]- Answer
>> False

### Receptive fields and stacked 3×3 convolutions

Five statements on the definition of a receptive field, its size for a single layer, the parameter comparison between stacked and single kernels, and the jump's effect on growth.

> [!question] Two consecutive 3×3 convolutions have the same receptive field as one 5×5 convolution but use more parameters.
>> [!success]- Answer
>> False

> [!question] The receptive field of a neuron at layer l is defined as the set of neurons in the input layer whose activations can influence that neuron.
>> [!success]- Answer
>> True

> [!question] For a single convolutional layer with kernel size k and stride 1, the receptive field is exactly k-1.
>> [!success]- Answer
>> False

> [!question] Three consecutive 3×3 convolutions use more parameters than one 7×7 convolution while achieving the same receptive field.
>> [!success]- Answer
>> False

> [!question] The jump (effective stride) at layer l-1 affects the growth of receptive field size at layer l.
>> [!success]- Answer
>> True

### The fully connected bottleneck

One statement on the cost of VGG-16's classifier head.

> [!question] In VGG-16, the fully connected layers became a bottleneck due to their high computational cost and parameter count.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions work through the design philosophy and its arithmetic: why 3×3 everywhere, how many stacked convolutions match a 7×7, the parameter counts that follow, and the shapes that flow through the blocks. The numeric options sit close together — 25,600 against 25,665 — so compute rather than recognize.

### Design philosophy

Two questions on VGG-16's philosophical contribution and the stacking count that matches a 7×7 receptive field.

> [!question] What is the primary philosophical contribution of VGG-16?
> a) Using large filters to increase computational efficiency
> b) Standardizing on 3×3 convolutions throughout the network
> c) Implementing heterogeneous filter sizes for better performance
> d) Reducing network depth to minimize parameters
>> [!success]- Answer
>> b) Standardizing on 3×3 convolutions throughout the network

> [!question] According to the receptive field proof, how many consecutive 3×3 convolutions are needed to achieve the same receptive field as one 7×7 convolution?
> a) 2
> b) 3
> c) 4
> d) 5
>> [!success]- Answer
>> b) 3

### Parameters, variants, and shapes

Four questions on the parameter count of a 5×5 layer, the change from VGG-13, the advantage of two 3×3 over one 5×5, and the output shape of the first convolution.

> [!question] What is the parameter count for a single 5×5 convolution with 64 input and 64 output channels?
> a) 25,600
> b) 25,665
> c) 36,928
> d) 49,152
>> [!success]- Answer
>> b) 25,665

> [!question] What was the key architectural change that made VGG-16 different from VGG-13?
> a) Additional convolution in Block 5
> b) Replacement of max pooling with average pooling
> c) Addition of batch normalization layers
> d) Reduction in the number of fully connected layers
>> [!success]- Answer
>> a) Additional convolution in Block 5

> [!question] What is the main advantage of using two 3×3 convolutions instead of one 5×5 convolution?
> a) Larger receptive field
> b) Fewer parameters while maintaining the same receptive field
> c) Reduced computational complexity
> d) Higher accuracy on all benchmarks
>> [!success]- Answer
>> b) Fewer parameters while maintaining the same receptive field

> [!question] What is the output shape after the first convolutional layer (Conv1-1) in VGG-16 with input shape (N, 3, 224, 224)?
> a) (N, 64, 224, 224)
> b) (N, 32, 112, 112)
> c) (N, 64, 112, 112)
> d) (N, 32, 224, 224)
>> [!success]- Answer
>> a) (N, 64, 224, 224)

### Pooling, the bottleneck, and receptive fields

Four questions on what stride-2 pooling does to the receptive field, the fully connected issue, the stride-1 recurrence, and the receptive field after three 3×3 convolutions.

> [!question] How does the receptive field size change when a stride-2 max pooling layer is added?
> a) It increases by a factor of 2
> b) It decreases by a factor of 2
> c) It remains the same
> d) It increases by the kernel size
>> [!success]- Answer
>> a) It increases by a factor of 2

> [!question] What was the primary issue with the fully connected layers in VGG-16?
> a) They used too few parameters
> b) They created a computational bottleneck
> c) They lacked non-linear activations
> d) They were not compatible with backpropagation
>> [!success]- Answer
>> b) They created a computational bottleneck

> [!question] For a stack of stride-1 convolutions, the receptive field recurrence relation simplifies to:
> a) r_l = r_{l-1} + k
> b) r_l = r_{l-1} + (k - 1)
> c) r_l = r_{l-1} * k
> d) r_l = r_{l-1} + 1
>> [!success]- Answer
>> b) r_l = r_{l-1} + (k - 1)

> [!question] What is the receptive field size after three consecutive 3×3 convolutions with stride 1?
> a) 5×5
> b) 7×7
> c) 9×9
> d) 11×11
>> [!success]- Answer
>> b) 7×7

## Matching

Nine matching questions assemble the full architecture: the four configurations, the five blocks, the parameter formulas per configuration, and the receptive-field identities. The groups are shuffled independently, and the C-notation formulas reward a quick check of the arithmetic before pairing.

### Configurations and blocks

Three questions matching configurations with their key characteristics, blocks with their operation sequences, and variants with their layer counts.

> [!question] Match the VGG configuration with its key characteristic.
>> [!example] Group A
>> a) VGG-11
>> b) VGG-13
>> c) VGG-16
>> d) VGG-19
>
>> [!example] Group B
>> n) 8 conv layers, baseline configuration
>> o) 10 conv layers with extra conv in Blocks 3, 4
>> p) 13 conv layers with extra conv in Blocks 3, 4, 5
>> q) 16 conv layers, deepest configuration evaluated
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

> [!question] Match the VGG block with its operation sequence.
>> [!example] Group A
>> a) Block 1
>> b) Block 2
>> c) Block 3
>> d) Block 5
>
>> [!example] Group B
>> n) Conv3-64, Conv3-64, MaxPool2d
>> o) Conv3-128, Conv3-128, MaxPool2d
>> p) Conv3-256, Conv3-256, Conv3-256, MaxPool2d
>> q) Conv3-512, Conv3-512, Conv3-512, Conv3-512, MaxPool2d
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

> [!question] Match the VGG variant with its layer configuration.
>> [!example] Group A
>> a) VGG-11
>> b) VGG-13
>> c) VGG-16
>> d) VGG-19
>
>> [!example] Group B
>> n) 8 conv + 3 FC layers
>> o) 10 conv + 3 FC layers
>> p) 13 conv + 3 FC layers
>> q) 16 conv + 3 FC layers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

### Concepts, principles, and layer roles

Three questions on architectural concepts, design principles and their implications, and the role of each layer type.

> [!question] Match the architectural concept with its description.
>> [!example] Group A
>> a) Receptive field
>> b) Jump (effective stride)
>> c) Local Response Normalization
>> d) Parameter count
>
>> [!example] Group B
>> n) The set of input pixels that can influence a neuron's activation
>> o) The number of input pixels corresponding to a shift of 1 pixel at a given layer
>> p) The total number of learnable weights in a layer
>> q) A technique that normalizes across channels to enhance generalization
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> q)
>> d) -> p)

> [!question] Match the VGG design principle with its implication.
>> [!example] Group A
>> a) Uniform filter size
>> b) Increased depth
>> c) Small filters
>> d) More non-linearities
>
>> [!example] Group B
>> n) Reduces hyperparameter search space
>> o) Consistently improved performance in systematic evaluation
>> p) Better parameter efficiency for same receptive field
>> q) Enhanced representational power of the network
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

> [!question] Match the layer type with its role in VGG-16.
>> [!example] Group A
>> a) Convolutional layer
>> b) Max pooling layer
>> c) ReLU activation
>> d) Fully connected layer
>
>> [!example] Group B
>> n) Reduces spatial dimensions by half
>> o) Applies learnable filters to extract features
>> p) Introduces non-linearity
>> q) Classifies features into final categories
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

### Parameter counts and receptive fields

Two questions pairing convolution configurations with parameter formulas and receptive-field properties with their mathematics.

> [!question] Match the convolution configuration with its parameter count for C input and C output channels.
>> [!example] Group A
>> a) One 5×5 conv
>> b) Two 3×3 convs
>> c) One 7×7 conv
>> d) Three 3×3 convs
>
>> [!example] Group B
>> n) 18C² + 2C parameters
>> o) 25C² + C parameters
>> p) 49C² + C parameters
>> q) 27C² + 3C parameters
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

> [!question] Match the receptive field property with its mathematical relationship.
>> [!example] Group A
>> a) Single layer with kernel k
>> b) Stack of n layers with kernel k, stride 1
>> c) Adding stride-2 pooling
>> d) Two consecutive 3×3 convolutions
>
>> [!example] Group B
>> n) Receptive field = k
>> o) Receptive field = 1 + n(k-1)
>> p) Doubles the effective stride
>> q) Receptive field = 5
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

### The computational profile

One question on where parameters, computation, memory, and receptive-field growth concentrate in VGG-16.

> [!question] Match the computational concept with its effect on VGG-16.
>> [!example] Group A
>> a) Parameter count
>> b) Computational cost
>> c) Memory usage
>> d) Receptive field growth
>
>> [!example] Group B
>> n) Dominated by fully connected layers
>> o) Increases quadratically with channels
>> p) Grows linearly with depth for fixed kernel size
>> q) Affected by both depth and spatial dimensions
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> q)
>> d) -> p)

## See also

- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[VGG and Classic Architectures Summary]]
- [[06 - Computer Vision/Training and Transfer Learning/PyTorch Advanced - VGG16 and Pre-trained Models|PyTorch Advanced - VGG16 and Pre-trained Models]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Inception Architecture Deep Dive|Inception Architecture Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/PyTorch Advanced - VGG16 and Pre-trained Models|PyTorch Advanced - VGG16 and Pre-trained Models]]
- [[The Mathematics of Receptive Fields and 1x1 Convolutions]]
- [[Glossary MOC]]
