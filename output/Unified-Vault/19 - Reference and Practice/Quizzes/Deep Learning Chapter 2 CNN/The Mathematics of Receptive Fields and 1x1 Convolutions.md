---
title: The Mathematics of Receptive Fields and 1x1 Convolutions
type: example
aliases:
  - "Q4 - The Mathematics of Receptive Fields and 1x1 Convolutions"
  - "The Mathematics of Receptive Fields and 1x1 Convolutions Quiz"
  - "Receptive Field Mathematics Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - receptive-field
  - effective-stride
  - jump
  - window-analogy
  - network-depth
  - 1x1-convolution
sources:
  - "Q4 - The Mathematics of Receptive Fields and 1x1 Convolutions"
created_index: 43
---

This quiz bank practices the arithmetic of receptive fields: what the region of influence is, how it grows as convolutional layers stack, and how the jump (effective stride) and receptive-field recurrences compute it layer by layer. Its twenty-four questions — ten true-or-false, eight multiple choice, and six matching — cover the definition and the Window Analogy, the growth from 3×3 to 5×5 and beyond, and the two iterative formulas with their base cases. The full development, including the 1×1 convolutions this chapter pairs with the receptive-field mathematics, lives in [[Receptive Fields and 1x1 Convolutions]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: three on what a receptive field is and how to picture it, four on how it grows with depth, and three on the recurrences that compute it. The false statements swap small for large, early for late, shrink what depth actually grows, or freeze the field at the first layer's size.

### Definition and intuition

Three statements on the definition of the receptive field, what a small one captures, and the Window Analogy.

> [!question] The receptive field of a neuron in a CNN is the region of the input image that influences the output of that neuron.
>> [!success]- Answer
>> True

> [!question] A neuron with a small receptive field captures coarse-grained, global patterns.
>> [!success]- Answer
>> False

> [!question] The Window Analogy compares the receptive field to a window through which a neuron looks at the input image.
>> [!success]- Answer
>> True

### Growth with depth

Four statements on the first layer's exact size, the direction of growth as the network deepens, what early layers detect, and the second layer's size.

> [!question] A neuron in the first convolutional layer with 3×3 filters has a receptive field of exactly 3×3.
>> [!success]- Answer
>> True

> [!question] The receptive field size decreases as we go deeper into the network.
>> [!success]- Answer
>> False

> [!question] Early layers in a CNN detect objects and scenes due to their large receptive fields.
>> [!success]- Answer
>> False

> [!question] The receptive field size in the second convolutional layer with 3×3 filters is 3×3, same as the first layer.
>> [!success]- Answer
>> False

### The jump and receptive-field recurrences

Three statements on the jump recurrence, the receptive-field recurrence, and the base case that starts the jump calculation.

> [!question] The jump (effective stride) at layer L is computed as j_L = j_{L-1} × S_L.
>> [!success]- Answer
>> True

> [!question] The receptive field size R_L at layer L is computed as R_L = R_{L-1} + (K_L - 1) × j_{L-1}.
>> [!success]- Answer
>> True

> [!question] The base case for jump calculation is j_0 = 1.
>> [!success]- Answer
>> True

## Multiple choice

Eight questions work through concrete sizes at each depth, what the jump measures, and how the base cases and a new stride-1 layer change the arithmetic. The wrong options are usually a neighboring layer's answer — 3×3 where 5×5 belongs, a jump of 1 where 2 belongs — so anchor each answer to the layer the question names.

### Receptive field size at each depth

Two questions on the first layer's field and the second layer's field measured against the original input.

> [!question] What is the receptive field of a neuron in the first convolutional layer that uses 3×3 filters?
> a) 1×1
> b) 3×3
> c) 5×5
> d) 7×7
>> [!success]- Answer
>> b) 3×3

> [!question] If a neuron in the second convolutional layer (also using 3×3 filters) has a receptive field of 5×5, what is the receptive field size in terms of the original input?
> a) 3×3
> b) 5×5
> c) 7×7
> d) 9×9
>> [!success]- Answer
>> b) 5×5

### Ordering across depth

One question on which neurons see more of the input.

> [!question] Which of the following statements about receptive fields is correct?
> a) Neurons in early layers have larger receptive fields than those in later layers
> b) Neurons in later layers have larger receptive fields than those in early layers
> c) All neurons in a CNN have the same receptive field size
> d) Receptive field size decreases with network depth
>> [!success]- Answer
>> b) Neurons in later layers have larger receptive fields than those in early layers

### The jump and its arithmetic

Three questions on what the jump represents, the jump after a stride-1 first layer, and the jump at a stride-2 third layer.

> [!question] What does the jump (effective stride) at layer L represent?
> a) The size of the kernel at layer L
> b) The distance in the original input image between two adjacent pixels in the feature map at layer L
> c) The number of layers in the network
> d) The padding size at layer L
>> [!success]- Answer
>> b) The distance in the original input image between two adjacent pixels in the feature map at layer L

> [!question] If the first layer has a stride of 1, what is the jump at layer 1?
> a) 0
> b) 1
> c) 2
> d) 3
>> [!success]- Answer
>> b) 1

> [!question] If layer 3 has a stride of 2, and the jump at layer 2 is 1, what is the jump at layer 3?
> a) 1
> b) 2
> c) 3
> d) 4
>> [!success]- Answer
>> b) 2

### Base cases and incremental growth

Two questions on where the receptive-field calculation starts and what a new 3×3 stride-1 layer adds.

> [!question] What is the base case for receptive field size calculation?
> a) R_0 = 0
> b) R_0 = 1
> c) R_0 = K_0
> d) R_0 = S_0
>> [!success]- Answer
>> b) R_0 = 1

> [!question] What happens to the receptive field when we add a new convolutional layer with 3×3 filters and stride 1?
> a) It decreases by 2 pixels
> b) It increases by 2 pixels
> c) It remains the same
> d) It doubles in size
>> [!success]- Answer
>> b) It increases by 2 pixels

## Matching

Six matching questions connect sizes to layers, formulas to their descriptions, layer properties to their effects, concepts to their intuitions, layer characteristics to worked calculations, and statements to their truth values. Two questions reuse a right-hand entry for two left-hand items while another right-hand entry goes unmatched, so anchor each pair on its mechanism rather than on elimination.

### Receptive field sizes by layer

One question pairing each size with the layer description that produces it.

> [!question] Match the receptive field sizes with their corresponding layer descriptions in a typical CNN.
>> [!example] Receptive Field Sizes
>> a) 3×3
>> b) 5×5
>> c) 7×7
>> d) 15×15
>
>> [!example] Layer Descriptions
>> n) First convolutional layer with 3×3 filters
>> o) Second convolutional layer with 3×3 filters
>> p) Third convolutional layer with 3×3 filters and stride 2
>> q) Deep layer in a network with multiple 3×3 layers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

### Formulas and base cases

One question pairing each formula with what it computes.

> [!question] Match the mathematical formulas with their descriptions.
>> [!example] Formulas
>> a) j_L = j_{L-1} × S_L
>> b) R_L = R_{L-1} + (K_L - 1) × j_{L-1}
>> c) R_0 = 1
>> d) j_0 = 1
>
>> [!example] Descriptions
>> n) Base case for receptive field size calculation
>> o) Base case for jump calculation
>> p) Formula for computing jump at layer L
>> q) Formula for computing receptive field size at layer L
>
>> [!success]- Answer
>> a) -> p)
>> b) -> q)
>> c) -> n)
>> d) -> o)

### Layer properties and their effects

One question on what larger kernels, larger strides, more layers, and smaller padding do. Two left-hand items share one effect, and the resolution effect is the entry no property claims.

> [!question] Match the layer properties with their effects on receptive field.
>> [!example] Layer Properties
>> a) Larger kernel size
>> b) Larger stride
>> c) More layers
>> d) Smaller padding
>
>> [!example] Effects
>> n) Increases receptive field size
>> o) Increases effective stride (jump)
>> p) Decreases feature map resolution
>> q) Has minimal effect on receptive field size
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> n)
>> d) -> q)

### Concepts and intuitions

One question pairing the vocabulary with the intuition behind it.

> [!question] Match the concepts with their intuitive explanations.
>> [!example] Concepts
>> a) Receptive field
>> b) Jump (effective stride)
>> c) Window analogy
>> d) Base case
>
>> [!example] Explanations
>> n) Distance between adjacent pixels in the original input image
>> o) A neuron's view of the input image as a window
>> p) The starting point of calculations (R_0 = 1, j_0 = 1)
>> q) Region of input that influences a neuron's output
>
>> [!success]- Answer
>> a) -> q)
>> b) -> n)
>> c) -> o)
>> d) -> p)

### Layer-by-layer calculations

One question working through four stacked layers and the R and j values each produces.

> [!question] Match the network layer characteristics with their receptive field calculations.
>> [!example] Layer Characteristics
>> a) First layer: 3×3 kernel, stride 1
>> b) Second layer: 3×3 kernel, stride 1
>> c) Third layer: 3×3 kernel, stride 2
>> d) Fourth layer: 3×3 kernel, stride 1
>
>> [!example] Receptive Field Calculations
>> n) R = 3, j = 1
>> o) R = 5, j = 1
>> p) R = 7, j = 2
>> q) R = 9, j = 2
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> q)

### Statements and their truth values

One question sorting four claims about receptive fields into true and false.

> [!question] Match the statements about receptive fields with their correctness.
>> [!example] Statements
>> a) Neurons with small receptive fields capture fine-grained details
>> b) Receptive field size decreases with network depth
>> c) The jump represents the stride between adjacent pixels in the original input
>> d) Base case for jump is j_0 = 1
>
>> [!example] Correctness
>> n) True
>> o) False
>> p) True
>> q) False
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)
>> d) -> n)

## See also

- [[Receptive Fields and 1x1 Convolutions]]
- [[The Convolution Operation]]
- [[Strides - Skipping Pixels and Downsampling]]
- [[The Output Spatial Dimension Formula]]
- [[Hierarchical Feature Extraction]]
- [[Padding - Mathematics, Edge Effects, and Valid vs Same]]
- [[The Convolution Operation Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[Glossary MOC]]
