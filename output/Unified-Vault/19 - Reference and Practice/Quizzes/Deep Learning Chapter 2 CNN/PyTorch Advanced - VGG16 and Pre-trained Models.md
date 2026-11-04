---
title: PyTorch Advanced - VGG16 and Pre-trained Models
type: example
aliases:
  - "Q23 - PyTorch Advanced - VGG16 and Pre-trained Models"
  - "PyTorch Advanced - VGG16 and Pre-trained Models Quiz"
  - "VGG16 and Pre-trained Models Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - pytorch
  - torchvision
  - vgg16
  - pretrained-models
  - transfer-learning
  - batch-normalization
sources:
  - "Q23 - PyTorch Advanced - VGG16 and Pre-trained Models"
created_index: 37
---

This quiz bank practices the advanced PyTorch workflow around VGG16 and pre-trained models: loading torchvision architectures through the modern weights API, understanding where downloaded weights live and how large they get, and keeping Dropout and BatchNorm well-behaved at inference time. Its twenty-eight questions — ten true-or-false, eight multiple choice, and ten matching — cover weights='DEFAULT' against weights=None and the explicit weight enums, the TORCH_HOME-controlled cache, VGG16-BN's normalization role, and the model.features, model.avgpool, and model.classifier decomposition. The walkthrough lives in [[06 - Computer Vision/Training and Transfer Learning/PyTorch Advanced - VGG16 and Pre-trained Models|PyTorch Advanced - VGG16 and Pre-trained Models]], with the architecture itself in [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]] and the adaptation strategies in [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: four on the weights API and the download cache, four on VGG16's influence and the ImageNet corpus behind its pre-training, and two on what model.eval() actually changes. The false statements invert the API's semantics — DEFAULT standing in for random weights, pretrained=True still recommended in PyTorch 2.0+ — or let train-time randomness survive into inference.

### The weights API and its cache

Four statements on the torchvision.models entry point, the meaning of weights='DEFAULT', the system-dependent cache directory and its TORCH_HOME override, and the status of the older pretrained=True flag.

> [!question] Pre-trained models in PyTorch can be loaded using the torchvision.models module.
>> [!success]- Answer
>> True

> [!question] The weights='DEFAULT' parameter loads random weights instead of pre-trained ones.
>> [!success]- Answer
>> False

> [!question] PyTorch caches pre-trained weights in a system-dependent directory, which can be changed using the TORCH_HOME environment variable.
>> [!success]- Answer
>> True

> [!question] Using pretrained=True is still the recommended way to load pre-trained weights in PyTorch 2.0+.
>> [!success]- Answer
>> False

### VGG16, VGG16-BN, and ImageNet

Four statements on the architecture's historical influence, the training role of its Batch Normalization layers, the scale of the ImageNet corpus, and the size of the VGG16-BN weights file.

> [!question] Batch Normalization layers in VGG16-BN help stabilize and accelerate training.
>> [!success]- Answer
>> True

> [!question] The VGG16 architecture was one of the most influential CNN architectures.
>> [!success]- Answer
>> True

> [!question] The ImageNet dataset contains 1.2 million images across 1000 classes.
>> [!success]- Answer
>> True

> [!question] The VGG16-BN weights file is approximately 558 MB in size.
>> [!success]- Answer
>> True

### Evaluation-mode behavior

Two statements on whether layers keep their training behavior under model.eval() and whether Dropout keeps dropping neurons once it is set.

> [!question] When using model.eval(), all layers in the neural network behave exactly the same as during training.
>> [!success]- Answer
>> False

> [!question] When using model.eval(), Dropout layers remain active and continue to randomly drop neurons.
>> [!success]- Answer
>> False

## Multiple choice

Eight questions work from the weights API through normalization and caching to inference discipline. Several options quote plausible spellings — weights='IMAGENET', load_weights=True — that the API does not accept, so match the exact parameter the modern interface defines.

### The weights API

Four questions on the recommended loading parameter in PyTorch 2.0+, the effect of weights=None, the meaning of the VGG16_BN_Weights.IMAGENET1K_V1 enum, and the purpose of the torchvision.models module.

> [!question] What is the recommended way to load pre-trained weights in PyTorch 2.0+?
> a) pretrained=True
> b) weights='DEFAULT'
> c) weights='IMAGENET'
> d) load_weights=True
>> [!success]- Answer
>> b) weights='DEFAULT'

> [!question] What happens when you set weights=None when loading a VGG16-BN model?
> a) It loads the best available pre-trained weights
> b) It loads weights trained on a different dataset
> c) It loads the architecture with random weights
> d) It raises an error
>> [!success]- Answer
>> c) It loads the architecture with random weights

> [!question] What does the VGG16_BN_Weights.IMAGENET1K_V1 specify?
> a) The model should be trained on ImageNet with 1K classes, version 1 weights
> b) The model should use 1K batch normalization layers
> c) The model is designed for images of size 1K x 1K pixels
> d) The model uses version 1 of the VGG architecture
>> [!success]- Answer
>> a) The model should be trained on ImageNet with 1K classes, version 1 weights

> [!question] What is the purpose of the torchvision.models module?
> a) To visualize neural network architectures
> b) To provide pre-built implementations of famous architectures with pre-trained weights
> c) To optimize neural network models for deployment
> d) To create custom neural network layers
>> [!success]- Answer
>> b) To provide pre-built implementations of famous architectures with pre-trained weights

### Normalization and caching

Two questions on what the Batch Normalization layer does inside VGG16-BN and where the downloaded weights are cached on a Linux system.

> [!question] What does the Batch Normalization layer in VGG16-BN do?
> a) Reduces the number of parameters in the model
> b) Normalizes the activations after each convolution to stabilize and accelerate training
> c) Prevents overfitting by randomly dropping neurons
> d) Compresses the model size for faster inference
>> [!success]- Answer
>> b) Normalizes the activations after each convolution to stabilize and accelerate training

> [!question] Where are pre-trained weights cached on a Linux system?
> a) /usr/local/lib/python3.x/site-packages/torch/weights
> b) ~/.cache/torch/hub/checkpoints/
> c) /tmp/pytorch_weights
> d) /var/lib/torch/weights
>> [!success]- Answer
>> b) ~/.cache/torch/hub/checkpoints/

### Inference mode and the limits of transfer

Two questions on why model.eval() matters for inference and on the one benefit pre-trained models cannot guarantee.

> [!question] Why is model.eval() important when using a pre-trained model for inference?
> a) It enables gradient computation for fine-tuning
> b) It ensures consistent behavior by turning off layers like Dropout and BatchNorm
> c) It increases the model's accuracy
> d) It reduces the model's memory footprint
>> [!success]- Answer
>> b) It ensures consistent behavior by turning off layers like Dropout and BatchNorm

> [!question] Which of the following is NOT a benefit of using pre-trained models?
> a) Saves training time and computational resources
> b) Provides better performance with limited data
> c) Guarantees optimal performance for any task
> d) Leverages features learned from large datasets
>> [!success]- Answer
>> c) Guarantees optimal performance for any task

## Matching

Ten matching questions assemble the full picture: the three ways to specify weights and when each fits, how Dropout, BatchNorm, and Conv2d behave once evaluation mode is set, the anatomy of VGG16 and its PyTorch attributes, the transfer-learning vocabulary, and how file size grows from VGG16 through VGG16-BN to VGG19-BN. The weight-method triplet appears three times — against descriptions, use cases, and characteristics — so anchor each pairing on what the method guarantees rather than on its position in the list.

### Weight loading methods

Three questions pairing the same three loading methods with their descriptions, their appropriate use cases, and their reproducibility characteristics, the last group swapping the explicit enum for the general method.

> [!question] Match the weight loading methods with their descriptions.
>> [!example] Methods
>> a) weights='DEFAULT'
>> b) weights=None
>> c) weights=VGG16_BN_Weights.IMAGENET1K_V1
>
>> [!example] Descriptions
>> n) Loads the architecture with random weights
>> o) Loads the best available pre-trained weights
>> p) Specifies the exact weight version for reproducibility
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the PyTorch model loading methods with their appropriate use cases.
>> [!example] Methods
>> a) weights='DEFAULT'
>> b) weights=None
>> c) weights=VGG16_BN_Weights.IMAGENET1K_V1
>
>> [!example] Use Cases
>> n) When you need to reproduce a specific version of a pre-trained model
>> o) When you want to transfer learning to a new but related task
>> p) When you want to train a model from scratch on a completely different dataset
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the weight specification methods with their characteristics.
>> [!example] Methods
>> a) weights='DEFAULT'
>> b) weights=None
>> c) Using explicit weight enums
>
>> [!example] Characteristics
>> n) Loads random initialization for training from scratch
>> o) Provides reproducibility by specifying exact weight versions
>> p) Uses the best available weights without specifying exact version
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Layer behavior across modes

Two questions on how Dropout, BatchNorm, and Conv2d behave under model.eval() and on each layer's impact on inference consistency, with ReLU joining the second group.

> [!question] Match the layers with their behavior during model.eval().
>> [!example] Layers
>> a) Dropout
>> b) BatchNorm
>> c) Conv2d
>
>> [!example] Behavior
>> n) Uses running statistics instead of batch statistics
>> o) Always active and computes the same output for the same input
>> p) Randomly drops neurons during training but is disabled during eval
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the layers with their impact on model behavior during inference.
>> [!example] Layers
>> a) Dropout
>> b) BatchNorm
>> c) ReLU
>
>> [!example] Impact
>> n) Behaves consistently during inference without randomness
>> o) Can produce different outputs for the same input if not handled properly
>> p) Always applies the same non-linear transformation
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Anatomy of VGG16

Two questions matching the architecture's component layers with their roles and the PyTorch model attributes with the submodules they contain.

> [!question] Match the components of the VGG16 architecture with their descriptions.
>> [!example] Components
>> a) Convolutional layers
>> b) Fully connected layers
>> c) Max pooling layers
>
>> [!example] Descriptions
>> n) Reduce spatial dimensions of feature maps
>> o) Extract features from input images
>> p) Perform final classification based on extracted features
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the PyTorch model attributes with their purposes.
>> [!example] Attributes
>> a) model.features
>> b) model.avgpool
>> c) model.classifier
>
>> [!example] Purposes
>> n) Contains the final classification layers
>> o) Contains the convolutional and pooling layers
>> p) Contains the average pooling layer that reduces spatial dimensions
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Transfer learning vocabulary and model states

Two questions on the terms transfer learning, fine-tuning, and feature extraction, and on which model state each evaluation scenario calls for.

> [!question] Match the terms with their definitions in the context of pre-trained models.
>> [!example] Terms
>> a) Transfer learning
>> b) Fine-tuning
>> c) Feature extraction
>
>> [!example] Definitions
>> n) Using a pre-trained model as a fixed feature extractor and only training the classifier
>> o) Adapting a pre-trained model to a new task by training both the feature extractor and classifier
>> p) Leveraging knowledge gained from solving one problem to solve a different but related problem
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the model evaluation scenarios with the appropriate model state.
>> [!example] Scenarios
>> a) Training a model from scratch
>> b) Performing inference on a pre-trained model
>> c) Fine-tuning a pre-trained model on a new dataset
>
>> [!example] Model States
>> n) model.train()
>> o) model.eval()
>> p) Depends on the specific part of the code
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### File sizes across variants

One question on how the weights file grows from VGG16 without BatchNorm to VGG16 with BatchNorm to VGG19 with BatchNorm.

> [!question] Match the model loading options with their memory requirements.
>> [!example] Options
>> a) VGG16 without BatchNorm
>> b) VGG16 with BatchNorm
>> c) VGG19 with BatchNorm
>
>> [!example] Memory Requirements
>> n) Largest file size due to more parameters and additional BatchNorm parameters
>> o) Smaller file size compared to VGG19-BN
>> p) Larger file size compared to VGG16 without BatchNorm due to additional BatchNorm parameters
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

## See also

- [[06 - Computer Vision/Training and Transfer Learning/PyTorch Advanced - VGG16 and Pre-trained Models|PyTorch Advanced - VGG16 and Pre-trained Models]]
- [[06 - Computer Vision/Training and Transfer Learning/PyTorch Implementation Basics|PyTorch Implementation Basics]]
- [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/PyTorch Implementation Basics|PyTorch Implementation Basics]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Batch Normalization|Batch Normalization]]
- [[Glossary MOC]]
