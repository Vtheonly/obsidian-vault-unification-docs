---
title: Core Architecture and Philosophy
type: example
aliases:
  - "Q2 - Core Architecture and Philosophy"
  - "Core Architecture and Philosophy Quiz"
  - "CNN Core Architecture Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - front-end
  - back-end
  - feature-hierarchy
  - relu
  - pooling
  - translation-invariance
  - transfer-learning
sources:
  - "Q2 - Core Architecture and Philosophy"
created_index: 26
---

This quiz bank practices the core architecture of convolutional neural networks: the split of every CNN into a feature-extracting front-end and a classifying back-end, and the design philosophy of decomposing visual recognition that stands behind it. Its twenty-eight questions cover the hierarchy of features that emerges automatically from training — from Gabor-like edge detectors to semantically meaningful object parts — the jobs that ReLU and pooling do inside a Conv → ReLU → Pool block, and why the generic low-level features that emerge are what make transfer learning work. The concepts are developed in [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]] and [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]], with the operators themselves treated in [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: three on the two-part front-end/back-end design, four on the hierarchy of features, and three on the ReLU and pooling operators and their order. The false statements reverse the division of labor between the two parts or credit pooling with costs it does not have, so weigh each claim against what each component actually contributes.

### The two-part design

Three statements on what the front-end and back-end are each responsible for, and on the decomposability insight that motivated the split.

> [!question] Every Convolutional Neural Network is organized into two fundamentally distinct functional parts: the Front-End and the Back-End.
>> [!success]- Answer
>> True

> [!question] The front-end of a CNN is responsible for performing the actual classification in the learned representation space.
>> [!success]- Answer
>> False

> [!question] The fundamental insight behind the two-part CNN design is that visual recognition cannot be meaningfully decomposed into sub-problems.
>> [!success]- Answer
>> False

### The feature hierarchy

Four statements on where the hierarchy of features comes from and how generic or task-specific the features at each level are.

> [!question] The hierarchy of features in CNNs emerges automatically from the training process and architectural constraints.
>> [!success]- Answer
>> True

> [!question] Low-level features in CNNs are highly specific to the training dataset and vary significantly across different models.
>> [!success]- Answer
>> False

> [!question] High-level features in CNNs are the most task-specific and are heavily influenced by the training dataset.
>> [!success]- Answer
>> True

> [!question] Mid-level features in CNNs combine low-level edges and textures into larger patterns that represent object parts and simple shapes.
>> [!success]- Answer
>> True

### The block operators

Three statements on what ReLU and pooling contribute inside a block, and on the order in which the block's operations run.

> [!question] ReLU introduces non-linearity to the network and sparsifies the feature map by setting negative values to zero.
>> [!success]- Answer
>> True

> [!question] The order of operations in CNN blocks is always Pool → Conv → ReLU to ensure optimal feature extraction.
>> [!success]- Answer
>> False

> [!question] Pooling operations reduce spatial dimensions but increase the computational cost for subsequent layers.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions move from the jobs of the two functional parts through the feature hierarchy that connects them to the operators that build it. The wrong options often describe a real property but assign it to the wrong component — pooling credited with non-linearity, the front-end with classification — so check which component each option is actually describing.

### Front-end and back-end

Two questions on the primary function of each of the two functional parts.

> [!question] What is the primary function of the front-end in a CNN?
> a) Classifying input images into categories
> b) Extracting progressively more abstract features from raw pixels
> c) Reducing the spatial dimensions of input images
> d) Initializing the weights of the network
>> [!success]- Answer
>> b) Extracting progressively more abstract features from raw pixels

> [!question] Which of the following statements about the back-end of a CNN is most accurate?
> a) It consists of convolutional layers that detect features in the input
> b) It maps high-level features extracted by the front-end to output categories
> c) It is responsible for reducing the spatial dimensions of the input
> d) It uses pooling operations to introduce non-linearity
>> [!success]- Answer
>> b) It maps high-level features extracted by the front-end to output categories

### How the levels relate

Two questions on the way low-, mid-, and high-level features build on one another, and on why that layering makes transfer learning effective.

> [!question] Which of the following best describes the relationship between low-level, mid-level, and high-level features in CNNs?
> a) They are independent of each other and serve different purposes
> b) Mid-level features are more universal than low-level features
> c) High-level features are built upon mid-level features, which are built upon low-level features
> d) All feature levels are learned simultaneously during training
>> [!success]- Answer
>> c) High-level features are built upon mid-level features, which are built upon low-level features

> [!question] What makes transfer learning effective in CNNs?
> a) The high-level features learned on one dataset are universally applicable to all tasks
> b) The low-level features learned on one dataset are just as useful for different domains
> c) The entire network architecture needs to be redesigned for each new task
> d) The pooling operations are task-specific and must be retrained
>> [!success]- Answer
>> b) The low-level features learned on one dataset are just as useful for different domains

### What each level does not look like

Two questions asking which characteristics do NOT belong to low-level and high-level features respectively.

> [!question] Which of the following is NOT a typical characteristic of low-level features in CNNs?
> a) They detect simple, local features like edges and color gradients
> b) They are highly generic and useful for virtually any visual task
> c) They represent entire object categories and semantic attributes
> d) They are nearly identical across CNNs trained on different datasets
>> [!success]- Answer
>> c) They represent entire object categories and semantic attributes

> [!question] Which of the following is NOT a typical characteristic of high-level features in CNNs?
> a) They are highly abstract and semantically meaningful
> b) They encode entire object parts and object categories
> c) They are the most universal across different training datasets
> d) They are heavily influenced by the specific classes the model was trained to recognize
>> [!success]- Answer
>> c) They are the most universal across different training datasets

### Operators and their order

Three questions on the purpose of ReLU, the purpose of pooling, and why Conv → ReLU → Pool is the conventional sequence.

> [!question] What is the main purpose of the ReLU activation function in a CNN?
> a) To reduce spatial dimensions of feature maps
> b) To introduce non-linearity and sparsify feature maps
> c) To combine multiple feature maps into one
> d) To normalize the input data
>> [!success]- Answer
>> b) To introduce non-linearity and sparsify feature maps

> [!question] What is the primary purpose of pooling operations in CNNs?
> a) To increase the spatial resolution of feature maps
> b) To introduce non-linearity into the network
> c) To reduce computational cost and provide translation invariance
> d) To initialize the weights of the network
>> [!success]- Answer
>> c) To reduce computational cost and provide translation invariance

> [!question] Why is the order of operations in CNN blocks typically Conv → ReLU → Pool?
> a) This order minimizes computational complexity
> b) This order ensures that pooling selects from non-negative activations meaningful for feature detection
> c) This order is arbitrary and any sequence would produce similar results
> d) This order maximizes the number of parameters in the network
>> [!success]- Answer
>> b) This order ensures that pooling selects from non-negative activations meaningful for feature detection

## Matching

Nine matching questions pair the parts and operators of a CNN with their roles, the feature levels with concrete examples, and the design concepts with their purposes. The two groups in each question are shuffled independently, so reconstruct each mapping from meaning rather than position.

### The parts, their concepts, and their operators

Two questions mapping the front-end, back-end, transfer learning, and feature hierarchy to their definitions, and the four block operators to their jobs.

> [!question] Match the design concept with its description.
>> [!example] Group A
>> a) Front-end
>> b) Back-end
>> c) Transfer learning
>> d) Feature hierarchy
>
>> [!example] Group B
>> n) Decomposes visual recognition into feature extraction and classification
>> o) Builds more abstract representations from simpler ones across layers
>> p) Uses knowledge from one task to improve performance on another
>> q) Maps high-level features to output categories
>
>> [!success]- Answer
>> a) -> n)
>> b) -> q)
>> c) -> p)
>> d) -> o)

> [!question] Match the CNN operator with its function.
>> [!example] Group A
>> a) ReLU activation
>> b) Pooling operation
>> c) Convolution operation
>> d) Fully connected layer
>
>> [!example] Group B
>> n) Reduces spatial dimensions and provides translation invariance
>> o) Extracts local patterns from input feature maps
>> p) Maps features to output categories in the back-end
>> q) Introduces non-linearity and sparsifies feature maps
>
>> [!success]- Answer
>> a) -> q)
>> b) -> n)
>> c) -> o)
>> d) -> p)

### The feature hierarchy, level by level

Three questions on what each feature level represents, on the concrete examples attached to each level, and on which network layers learn which features.

> [!question] Match the item with its description.
>> [!example] Group A
>> a) Low-level features
>> b) Mid-level features
>> c) High-level features
>> d) Convolution operation
>
>> [!example] Group B
>> n) Combines edges and textures into object parts and simple shapes
>> o) Detects simple, local features like edges and color gradients
>> p) Maps high-level features to output categories
>> q) Learns highly abstract and semantically meaningful representations
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> q)
>> d) -> p)

> [!question] Match the feature example with its description.
>> [!example] Group A
>> a) Gabor-like filters
>> b) Object parts
>> c) Semantic attributes
>> d) Simple shapes
>
>> [!example] Group B
>> n) Complex features like a dog's snout or car wheel assembly
>> o) Basic geometric forms like circles, rectangles, triangles
>> p) Filters that detect edges at various orientations
>> q) Properties like "furry" or "metallic"
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> q)
>> d) -> o)

> [!question] Match the network layer with its description.
>> [!example] Group A
>> a) Early layers
>> b) Middle layers
>> c) Late layers
>> d) Output layer
>
>> [!example] Group B
>> n) Learn features that are highly abstract and semantically meaningful
>> o) Detect simple, local features like edges and color gradients
>> p) Combine mid-level patterns into representations encoding object categories
>> q) Use softmax to produce class probabilities
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)
>> d) -> q)

### Downsampling, invariance, and vocabulary

Three questions on the pooling variants and their relatives, on the invariance and sparsity concepts, and on the receptive-field and map terminology.

> [!question] Match the pooling or convolution type with its characteristic.
>> [!example] Group A
>> a) Max pooling
>> b) Average pooling
>> c) Strided convolution
>> d) Dilated convolution
>
>> [!example] Group B
>> n) Reduces spatial dimensions by taking maximum values in regions
>> o) Expands receptive field without increasing parameters
>> p) Reduces spatial dimensions by averaging values in regions
>> q) Moves filter by multiple pixels at each step
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> q)
>> d) -> o)

> [!question] Match the concept with its description.
>> [!example] Group A
>> a) Translation invariance
>> b) Weight sharing
>> c) Sparse coding
>> d) Feature sparsity
>
>> [!example] Group B
>> n) Same filter applied at every location in the input
>> o) Setting negative values to zero in feature maps
>> p) Algorithm that learns filters similar to CNNs
>> q) Robustness to small spatial shifts in input
>
>> [!success]- Answer
>> a) -> q)
>> b) -> n)
>> c) -> p)
>> d) -> o)

> [!question] Match the term with its description.
>> [!example] Group A
>> a) Receptive field
>> b) Activation map
>> c) Feature map
>> d) Pooling stride
>
>> [!example] Group B
>> n) Indicates where a pattern was detected in the input
>> o) The area of the input that a neuron "sees"
>> p) The distance between pooling operations
>> q) Output after applying non-linear activation to feature map
>
>> [!success]- Answer
>> a) -> o)
>> b) -> q)
>> c) -> n)
>> d) -> p)

### The biological analogy

One question anchoring the CNN's parts to the visual machinery that inspired them — Hubel and Wiesel's cells and the visual cortex.

> [!question] Match the item with its description.
>> [!example] Group A
>> a) Hubel and Wiesel cells
>> b) CNN front-end
>> c) CNN back-end
>> d) Visual cortex
>
>> [!example] Group B
>> n) Analogous to how humans process visual information
>> o) Detects simple features like oriented edges
>> p) Transforms pixels into abstract feature representations
>> q) Maps features to desired output categories
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> q)
>> d) -> n)

## See also

The topical concept notes this quiz practices, its sibling quizzes in the same chapter, and adjacent reading on the operators and the feature hierarchy:

- [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[06 - Computer Vision/Architecture and Connectivity/Hierarchical Feature Extraction|Hierarchical Feature Extraction]]
- [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[Convolutional Neural Networks]]
- [[Activation Functions]]
