---
title: ResNet Bottleneck Blocks and Architectural Variants
type: example
aliases:
  - "Q12 - ResNet Bottleneck Blocks and Architectural Variants"
  - "ResNet Bottleneck Blocks and Architectural Variants Quiz"
  - "ResNet Bottleneck Blocks Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - resnet
  - bottleneck-blocks
  - batch-normalization
  - skip-connections
  - parameter-counting
sources:
  - "Q12 - ResNet Bottleneck Blocks and Architectural Variants"
created_index: 39
---

This quiz bank practices the engineering that let ResNet scale from ResNet-18 to ResNet-152: the Basic Block of two 3×3 convolutions, the 1×1 → 3×3 → 1×1 Bottleneck that compresses channels before the expensive spatial work, and the parameter arithmetic that justifies the swap. Its twenty-eight questions — ten true-or-false, nine multiple choice, and nine matching — cover which variant uses which block, what each convolution inside the bottleneck is for, the 36,864 and 73,728 parameter counts, and the residual concepts underneath. The deep dive lives in [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]], built on [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: three on the variant lineup, three on the interior of the two block designs, two on the parameter arithmetic, and two on the bottleneck principle. The false statements swap block assignments between shallow and deep variants and misstate the direction and originality of the bottleneck's channel compression.

### The variant lineup

Three statements on the five standard variants and what their numbers mean, the block used by the deep ones, and the block ResNet-18 uses.

> [!question] ResNet comes in five standard variants where the number indicates the total count of weighted layers.
>> [!success]- Answer
>> True

> [!question] The Basic Block is used in ResNet-50, ResNet-101, and ResNet-152.
>> [!success]- Answer
>> False

> [!question] ResNet-18 uses the Bottleneck Block design.
>> [!success]- Answer
>> False

### Inside the blocks

Three statements on the bottleneck's layer pattern, the job of its first 1×1 convolution, and where the Basic Block's skip connection lands.

> [!question] The Bottleneck Block contains three layers arranged in a 1×1 → 3×3 → 1×1 pattern.
>> [!success]- Answer
>> True

> [!question] The first 1×1 convolution in a Bottleneck Block expands the channel count.
>> [!success]- Answer
>> False

> [!question] In a Basic Block, the skip connection directly adds the input to the output after the second batch normalization.
>> [!success]- Answer
>> True

### Parameter arithmetic

Two statements on the cost of a 3×3 convolution with 64 input and output channels and of a whole Basic Block operating on 512 channels.

> [!question] The parameter count for a 3×3 convolution with 64 input and output channels is 36,864.
>> [!success]- Answer
>> True

> [!question] A Basic Block operating on 512 channels would require over 4.7 million parameters.
>> [!success]- Answer
>> True

### The bottleneck principle

Two statements on the Basic Block's cost at high channel counts and on whether reduce-operate-expand is unique to the Bottleneck Block.

> [!question] The Basic Block is more computationally expensive than the Bottleneck Block for deep networks with high channel counts.
>> [!success]- Answer
>> True

> [!question] The "reduce-operate-expand" principle is unique to the Bottleneck Block and not used in other architectures.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions work through the design and its arithmetic: which variants use which block, what the bottleneck's convolutions do, why it exists, and the parameter counts and batch-normalization details that follow. The numeric options sit close together — 36,864, 73,728, 147,456, 294,912 — so compute rather than recognize.

### Variants and their blocks

Two questions on which variants use the Basic Block and on what primarily differs between ResNet variants.

> [!question] Which ResNet variants use the Basic Block?
> a) ResNet-18 and ResNet-34
> b) ResNet-50 and ResNet-101
> c) ResNet-34 and ResNet-50
> d) ResNet-18 and ResNet-152
>> [!success]- Answer
>> a) ResNet-18 and ResNet-34

> [!question] What is the primary architectural difference between ResNet variants?
> a) The type of residual block used
> b) The stride value in convolutions
> c) The activation function
> d) The pooling method
>> [!success]- Answer
>> a) The type of residual block used

### Inside the Bottleneck

Two questions on the purpose of the first 1×1 convolution and on the block's output dimensionality relative to its input.

> [!question] In a Bottleneck Block, what is the purpose of the first 1×1 convolution?
> a) To expand the channel count
> b) To reduce the channel count
> c) To change the spatial dimensions
> d) To add non-linearity
>> [!success]- Answer
>> b) To reduce the channel count

> [!question] What is the output dimensionality of a Bottleneck Block compared to its input?
> a) Reduced
> b) Expanded
> c) The same
> d) Depends on the stride
>> [!success]- Answer
>> c) The same

### Why the Bottleneck exists

Two questions on the reason deeper variants adopt the Bottleneck and the principle it shares with the Inception module.

> [!question] Why is the Bottleneck Block used in deeper ResNet variants?
> a) It reduces the number of parameters
> b) It decreases computational cost while maintaining output dimensionality
> c) It improves gradient flow
> d) It reduces memory usage
>> [!success]- Answer
>> b) It decreases computational cost while maintaining output dimensionality

> [!question] What architectural principle is shared between the Bottleneck Block and the Inception module?
> a) Skip connections
> b) Batch normalization
> c) Reduce-operate-expand
> d) Depthwise separable convolutions
>> [!success]- Answer
>> c) Reduce-operate-expand

### Block mechanics and parameter counts

Three questions on the Basic Block's parameter count at 64 channels, what comes after each 3×3 convolution, and why convolutional biases go uncounted under batch normalization.

> [!question] What is the parameter count for a Basic Block operating on 64-channel feature maps?
> a) 36,864
> b) 73,728
> c) 147,456
> d) 294,912
>> [!success]- Answer
>> b) 73,728

> [!question] In a Basic Block, what comes after each 3×3 convolution?
> a) Activation function only
> b) Batch normalization only
> c) Batch normalization followed by ReLU activation
> d) ReLU activation followed by batch normalization
>> [!success]- Answer
>> c) Batch normalization followed by ReLU activation

> [!question] Why are convolutional biases not counted in the parameter calculation when batch normalization is used?
> a) They are set to zero
> b) They are redundant due to batch normalization's learnable bias
> c) They are automatically disabled
> d) They are included in the batch normalization parameters
>> [!success]- Answer
>> b) They are redundant due to batch normalization's learnable bias

## Matching

Nine matching questions assemble the full architecture: variants paired to block types and use cases, the interiors of both block designs, the stage-by-stage channel counts, and the residual concepts and optimization techniques underneath. The groups are shuffled independently, two variants can share one block type, and one listed block type matches no variant at all.

### Variants, blocks, and use cases

Two questions matching variants to their block types and to their typical use cases.

> [!question] Match the ResNet variant with its block type.
>> [!example] ResNet Variants
>> a) ResNet-18
>> b) ResNet-50
>> c) ResNet-152
>
>> [!example] Block Types
>> n) Basic Block
>> o) Bottleneck Block
>> p) Hybrid Block
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> o)

> [!question] Match the ResNet variants with their typical use cases.
>> [!example] Variants
>> a) ResNet-18/34
>> b) ResNet-50
>> c) ResNet-101/152
>
>> [!example] Use Cases
>> n) Very deep networks requiring high capacity
>> o) Balanced performance and efficiency
>> p) Limited computational resources
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### Inside the Basic Block

Two questions on the Basic Block's components and their descriptions, and on the order of operations through the block.

> [!question] Match the components of a Basic Block with their descriptions.
>> [!example] Components
>> a) 3×3 Convolution
>> b) Batch Normalization
>> c) Skip Connection
>
>> [!example] Descriptions
>> n) Adds the input directly to the output
>> o) Normalizes activations after convolution
>> p) Performs spatial feature extraction
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the residual block components with their order of operation.
>> [!example] Components
>> a) Input
>> b) Convolutions with BN and ReLU
>> c) Addition and Final ReLU
>
>> [!example] Order
>> n) First operation in block
>> o) Middle operation in block
>> p) Final operation in block
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Inside the Bottleneck Block

One question on the block's three layers and their functions.

> [!question] Match the layers in a Bottleneck Block with their functions.
>> [!example] Layers
>> a) First 1×1 Convolution
>> b) 3×3 Convolution
>> c) Second 1×1 Convolution
>
>> [!example] Functions
>> n) Expands channel count back to original size
>> o) Performs spatial feature extraction on compressed representation
>> p) Reduces channel count (compression)
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### Stages, channels, and computational impact

Two questions on ResNet stages and their typical channel counts, and on the computational impact of the architectural elements.

> [!question] Match the ResNet stages with their typical channel counts.
>> [!example] Stages
>> a) First stage
>> b) Middle stages
>> c) Final stage
>
>> [!example] Channel Counts
>> n) 64 channels
>> o) 128-256 channels
>> p) 512 channels
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the architectural elements with their computational impact.
>> [!example] Elements
>> a) Two 3×3 convolutions in Basic Block
>> b) 1×1 → 3×3 → 1×1 sequence in Bottleneck
>> c) High channel counts (512+)
>
>> [!example] Impact
>> n) High computational cost with large channel counts
>> o) Reduced computational cost through compression
>> p) Manageable cost with small channel counts
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### Residual concepts and their benefits

Two questions on degradation, residual learning, and projection shortcuts, and on what each optimization technique contributes in ResNet.

> [!question] Match the concepts with their definitions.
>> [!example] Concepts
>> a) Degradation Problem
>> b) Residual Learning
>> c) Projection Shortcut
>
>> [!example] Definitions
>> n) Using a 1×1 convolution to match dimensions when skip connection changes them
>> o) Learning the difference between input and output rather than the desired output directly
>> p) Deep networks' performance decreasing with added layers
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the optimization techniques with their benefits in ResNet.
>> [!example] Techniques
>> a) Bottleneck Design
>> b) Batch Normalization
>> c) Skip Connections
>
>> [!example] Benefits
>> n) Mitigates vanishing gradients
>> o) Normalizes layer inputs, stabilizing training
>> p) Reduces computational cost for deep networks
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

## See also

- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[06 - Computer Vision/Architecture and Connectivity/Inception Architecture Deep Dive|Inception Architecture Deep Dive]]
- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[Transfer Learning and ResNet Summary]]
- [[Residual Connections]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Inception Architecture Deep Dive|Inception Architecture Deep Dive]]
- [[Glossary MOC]]
