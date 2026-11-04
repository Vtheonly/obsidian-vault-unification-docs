---
title: The Convolution Operation Deep Dive
type: example
aliases:
  - "Q3 - The Convolution Operation Deep Dive"
  - "The Convolution Operation Deep Dive Quiz"
  - "Convolution Operation Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - convolution
  - filters
  - kernels
  - feature-maps
  - activation-maps
  - sliding-dot-product
  - stride
  - padding
sources:
  - "Q3 - The Convolution Operation Deep Dive"
created_index: 40
---

This quiz bank practices the convolution operation itself — filters, kernels, feature maps, and the sliding dot product at the heart of every CNN. Its thirty questions cover filter geometry across grayscale, RGB, and volumetric inputs, the difference between learned and hand-crafted features, how feature maps are read as heat maps, and how stride, padding, and filter count shape the operation. The mechanics are developed in [[The Convolution Operation]] and [[From Basic Convolution to Learned Weights]]; decide on an answer before unfolding it.

## True or false

Ten statements open the quiz: two on the filter-versus-kernel vocabulary, two on filter size and depth, one on where filter values come from, three on feature maps, and two on the operation and what multiple filters produce. The false statements confuse neighboring ideas — filters the size of the whole input, hand-crafted fixed weights, output always matching input size — so check each against what a convolution actually does.

### Filter versus kernel

Two statements on whether the two terms are identical, and how some frameworks draw the 2D-versus-3D distinction.

> [!question] In signal processing, the terms "filter" and "kernel" have exactly the same meaning.
>> [!success]- Answer
>> False

> [!question] In some frameworks, "kernel" refers to the 2D weight matrix while "filter" refers to the full 3D weight tensor.
>> [!success]- Answer
>> True

### Filter size and depth

Two statements on how big a filter is relative to its input, and what depth an RGB filter carries.

> [!question] Filters and kernels are always the same size as the input they are applied to.
>> [!success]- Answer
>> False

> [!question] A filter applied to an RGB image with 3 color channels would have dimensions 3×3×3.
>> [!success]- Answer
>> True

### Learned, not hand-crafted

One statement on where filter values come from.

> [!question] The values in a filter are typically hand-crafted and fixed during training.
>> [!success]- Answer
>> False

### Feature maps

Three statements on the feature map's other name, what its values mean, and whether its size tracks the input's.

> [!question] Feature maps are also called activation maps.
>> [!success]- Answer
>> True

> [!question] Feature maps highlight where specific patterns appear in the input, with high values indicating strong detection of the pattern.
>> [!success]- Answer
>> True

> [!question] The size of the output feature map is always the same as the input size.
>> [!success]- Answer
>> False

### The sliding dot product and multiple filters

Two statements on how the operation is best understood and what happens when several filters see the same input.

> [!question] Convolution in CNNs can be understood as a sliding dot product operation.
>> [!success]- Answer
>> True

> [!question] When applying multiple filters to the same input, each filter produces a separate feature map.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions cover the purpose and anatomy of a filter, the sliding dot product view, how to read a feature map, what happens when many filters are stacked, and what training does to filter values. Wrong options quote real CNN vocabulary in the wrong role — averaging, concatenating, normalizing — so anchor each answer to the exact question asked.

### The purpose and anatomy of a filter

Three questions on what a filter is for, its dimensions on RGB input, and its typical shape.

> [!question] What is the primary purpose of a filter in a convolutional neural network?
> a) To reduce the dimensionality of the input
> b) To extract specific types of features from the input
> c) To normalize the input values
> d) To activate neurons in the next layer
>> [!success]- Answer
>> b) To extract specific types of features from the input

> [!question] What dimensions would a filter have for an RGB image input?
> a) 3×3
> b) 5×5
> c) 3×3×3
> d) 5×5×3
>> [!success]- Answer
>> c) 3×3×3

> [!question] What is typically the shape of a filter in CNNs?
> a) Always 3×3
> b) Always square (e.g., 3×3, 5×5, 7×7)
> c) Always rectangular
> d) The same as the input shape
>> [!success]- Answer
>> b) Always square (e.g., 3×3, 5×5, 7×7)

### The sliding dot product

Two questions on the best one-line description of convolution, and what fixes the pattern a filter detects.

> [!question] What is the convolution operation best described as?
> a) A sliding average
> b) A sliding dot product
> c) A matrix multiplication
> d) A max operation
>> [!success]- Answer
>> b) A sliding dot product

> [!question] In the context of CNNs, what determines what pattern a filter detects?
> a) The size of the filter
> b) The stride value
> c) The values in the filter
> d) The padding size
>> [!success]- Answer
>> c) The values in the filter

### Reading feature maps

Two questions on what a feature map is and how it looks when visualized.

> [!question] What does a feature map represent in a CNN?
> a) The input to the next layer
> b) The weights learned during training
> c) A 2D array showing the strength of a filter's response at each spatial location
> d) The activation values of all neurons in the network
>> [!success]- Answer
>> c) A 2D array showing the strength of a filter's response at each spatial location

> [!question] How can feature maps be interpreted visually?
> a) As heat maps highlighting where specific patterns appear
> b) As color representations of the input
> c) As probability distributions
> d) As error maps
>> [!success]- Answer
>> a) As heat maps highlighting where specific patterns appear

### Many filters, one output volume

Two questions on what multiple filters produce, and what the stacked result looks like.

> [!question] What happens when multiple filters are applied to the same input?
> a) They are averaged together
> b) Only the strongest filter's output is kept
> c) Each filter produces a separate feature map
> d) They are concatenated into a single large matrix
>> [!success]- Answer
>> c) Each filter produces a separate feature map

> [!question] What is the output when multiple filters are applied to an input and stacked along the channel dimension?
> a) A 2D array
> b) A 3D output tensor
> c) A 1D vector
> d) A scalar value
>> [!success]- Answer
>> b) A 3D output tensor

### Learned, not hand-crafted

One question on the fate of filter values during training.

> [!question] What happens to filter values during training in a CNN?
> a) They remain fixed as hand-crafted values
> b) They are learned from the data
> c) They are randomly initialized and never updated
> d) They are normalized to a standard range
>> [!success]- Answer
>> b) They are learned from the data

## Matching

Ten matching questions pair the vocabulary with its definitions, the components and parameters with their roles, filter geometry with input type, the arithmetic inside each slide with its effect, and the feature-map readings with their meanings. The groups are shuffled independently, so match from meaning rather than position.

### Terms and community conventions

Two questions on the three core terms, and on who uses "filter" and "kernel" interchangeably versus who distinguishes them.

> [!question] Match the terms with their definitions.
>> [!example] Group A
>> a) Filter
>> b) Kernel
>> c) Feature Map
>
>> [!example] Group B
>> n) A small matrix of learnable weights used to extract features
>> o) The output produced by applying a single filter to the entire input
>> p) Sometimes used interchangeably with "filter" to refer to the weight matrix
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

> [!question] Match the framework conventions with their terminology.
>> [!example] Group A
>> a) Some frameworks
>> b) Most practitioners
>> c) Signal processing
>
>> [!example] Group B
>> n) Use "filter" and "kernel" interchangeably
>> o) Distinguish between kernel (2D) and filter (3D)
>> p) Have slightly different connotations for filter and kernel
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Components, parameters, and their roles

Two questions on what filter values, feature maps, and stride each do, then on the knobs of the operation: stride, padding, and number of filters.

> [!question] Match the components with their roles in convolution.
>> [!example] Group A
>> a) Filter values
>> b) Feature map
>> c) Stride
>
>> [!example] Group B
>> n) Determines what pattern the filter detects
>> o) Shows where a specific feature is present in the input
>> p) Controls how much the filter moves each step
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the convolution parameters with their functions.
>> [!example] Group A
>> a) Stride
>> b) Padding
>> c) Number of filters
>
>> [!example] Group B
>> n) Controls how much the filter moves each step
>> o) Adds extra pixels around the input
>> p) Determines how many different features are extracted
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Filter geometry across input types

Two questions on what filter size, depth, and values each control, and on the filter depth demanded by grayscale, RGB, and volume inputs.

> [!question] Match the filter components with their purposes.
>> [!example] Group A
>> a) Filter size
>> b) Filter depth
>> c) Filter values
>
>> [!example] Group B
>> n) Matches the number of channels in the input
>> o) Determines the spatial extent of the pattern detection
>> p) Determines what specific pattern is detected
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the input types with their filter dimensions.
>> [!example] Group A
>> a) Grayscale image
>> b) RGB image
>> c) Volume data (e.g., medical scan)
>
>> [!example] Group B
>> n) 3×3×3
>> o) 3×3×1
>> p) 3×3×D (where D is the depth of the input)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### The arithmetic and its signatures

Two questions on the three mathematical steps inside each slide, and on what a vertical-edge filter, an RGB input, and multiple filters each produce.

> [!question] Match the mathematical operations with their effects.
>> [!example] Group A
>> a) Dot product
>> b) Element-wise multiplication
>> c) Summation
>
>> [!example] Group B
>> n) Combines all products to produce a single output value
>> o) Multiplies corresponding elements of filter and input patch
>> p) Measures similarity between filter and input patch
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the characteristics with their descriptions.
>> [!example] Group A
>> a) Vertical edge detection filter
>> b) RGB image input
>> c) Multiple filters applied to same input
>
>> [!example] Group B
>> n) Produces high values at vertical transitions
>> o) Has 3 channels (red, green, blue)
>> p) Results in multiple feature maps
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Reading the map, learned or hand-crafted

Two questions on what high, low, and zero values in a feature map mean, and on hand-crafted features, learned features, and feature visualization.

> [!question] Match the interpretations with their visual representations.
>> [!example] Group A
>> a) High values in feature map
>> b) Low values in feature map
>> c) Zero values in feature map
>
>> [!example] Group B
>> n) Strong detection of pattern at that location
>> o) No significant pattern detected
>> p) Weak or no detection of pattern
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

> [!question] Match the learning concepts with their descriptions.
>> [!example] Group A
>> a) Hand-crafted features
>> b) Learned features in CNN
>> c) Feature visualization
>
>> [!example] Group B
>> n) Network discovers useful patterns from data
>> o) Understanding what patterns each filter detects
>> p) Predefined patterns designed by experts
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

## See also

- [[The Convolution Operation]]
- [[From Basic Convolution to Learned Weights]]
- [[Strides - Skipping Pixels and Downsampling]]
- [[Padding - Mathematics, Edge Effects, and Valid vs Same]]
- [[The Output Spatial Dimension Formula]]
- [[Demystifying Tensors - Volumes, Depth, and Data Formats]]
- [[Processing 3D Volumes, Depth Summation, and Biases]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[Hierarchical Feature Extraction]]
- [[Dot Product]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[The Mathematics of Receptive Fields and 1x1 Convolutions]]
- [[Advanced Pooling Mechanisms and Global Average Pooling]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]]
- [[Model Evaluation Metrics Beyond Accuracy]]
- [[Glossary MOC]]
