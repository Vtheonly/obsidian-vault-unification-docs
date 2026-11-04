---
title: Data Augmentation
type: example
aliases:
  - "Q18 - Data Augmentation"
  - "Data Augmentation Quiz"
  - "CNN Data Augmentation Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - data-augmentation
  - invariance
  - geometric-transformations
  - color-jitter
  - generalization
sources:
  - "Q18 - Data Augmentation"
created_index: 27
---

This quiz bank practices data augmentation, the practice of artificially expanding a training dataset by applying transformations to the images already in it, for gains that can rival collecting substantially more data at essentially zero cost. Its twenty-eight questions — ten true-or-false, nine multiple choice, and nine matching — cover why CNNs need it (they process images as arrays of pixel values, with no innate understanding of the physical world), which technique teaches which invariance, and the accuracy, code, and storage economics of the practice. The concept note lives in [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]], next to the other generalization tools in [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: two on what augmentation is and what it buys, two on what CNNs do or do not bring to the table, three on which technique teaches which invariance, and three on the cost, storage, and necessity of the practice. The false statements swap the invariance pairings, overstate the cost of augmentation relative to collecting data, and misread how CNNs see images and how many parameters they carry.

### What augmentation is and what it buys

Two statements on the definition of the practice and the size of the gains it can deliver.

> [!question] Data augmentation is the practice of artificially expanding a training dataset by applying transformations to existing training images.
>> [!success]- Answer
>> True

> [!question] Data augmentation can provide gains comparable to collecting substantially more training data at essentially zero cost.
>> [!success]- Answer
>> True

### What CNNs do not bring to the table

Two statements on whether networks innately understand the physical world and whether modern convolutional architectures have fewer parameters than traditional neural networks.

> [!question] A CNN has an innate understanding of the physical world and knows that a cat is still a cat when viewed from a different angle.
>> [!success]- Answer
>> False

> [!question] Modern convolutional architectures typically have fewer parameters than traditional neural networks.
>> [!success]- Answer
>> False

### Which technique teaches which invariance

Three statements pairing horizontal flip, color jitter, and random crop with the invariances they teach.

> [!question] Horizontal flip augmentation teaches a CNN about translation invariance.
>> [!success]- Answer
>> False

> [!question] Color jitter augmentation teaches photometric invariance.
>> [!success]- Answer
>> True

> [!question] Random crop augmentation teaches a CNN about horizontal invariance.
>> [!success]- Answer
>> False

### Cost, storage, and necessity

Three statements on whether collecting more data is cheaper, whether augmentation is only for extremely small datasets, and whether it needs extra disk space.

> [!question] Collecting more data is generally cheaper and easier than implementing data augmentation.
>> [!success]- Answer
>> False

> [!question] Data augmentation is only necessary when the training dataset is extremely small.
>> [!success]- Answer
>> False

> [!question] Data augmentation requires substantial additional disk storage for the transformed images.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions work through the motivation and the mechanics: why augmentation is necessary, what it teaches, which technique teaches which invariance, and what it costs. Two of them are "NOT" questions — one asks for the reason that does not compel augmentation, the other for the transform that is not geometric — so read the direction of each stem twice.

### Why augmentation is necessary

Three questions on the reason that does not compel augmentation, the major benefit it delivers, and its primary purpose.

> [!question] Which of the following is NOT a compelling reason why data augmentation is necessary in practice?
> a) CNNs are data-hungry
> b) Collecting more data is expensive
> c) Real-world data is diverse
> d) CNNs cannot learn without data augmentation
>> [!success]- Answer
>> d) CNNs cannot learn without data augmentation

> [!question] What is a major benefit of data augmentation mentioned in the text?
> a) It reduces model complexity
> b) It improves validation accuracy by 2-5 percentage points
> c) It eliminates the need for human annotators
> d) It reduces computational requirements
>> [!success]- Answer
>> b) It improves validation accuracy by 2-5 percentage points

> [!question] What is the primary purpose of data augmentation?
> a) To reduce the size of the training dataset
> b) To teach the network specific invariance properties
> c) To replace the need for collecting real data
> d) To increase model complexity
>> [!success]- Answer
>> b) To teach the network specific invariance properties

### Invariances and the techniques that teach them

Three questions on what augmentation teaches a CNN, which technique teaches horizontal invariance, and what random crop teaches.

> [!question] What does data augmentation teach a CNN?
> a) The physical properties of objects
> b) Invariance properties
> c) How to label new images
> d) How to reduce model size
>> [!success]- Answer
>> b) Invariance properties

> [!question] Which augmentation technique teaches horizontal invariance?
> a) Random crop
> b) Color jitter
> c) Horizontal flip
> d) Rotation
>> [!success]- Answer
>> c) Horizontal flip

> [!question] What does random crop augmentation teach a CNN?
> a) Photometric invariance
> b) Translation invariance
> c) Scale invariance
> d) Rotation invariance
>> [!success]- Answer
>> b) Translation invariance

### Cost, transformations, and how CNNs see

Three questions on the cost relative to collecting and labeling new images, which transform is not geometric, and how CNNs process images.

> [!question] Compared to collecting and labeling new images, data augmentation is:
> a) More expensive
> b) About the same cost
> c) Essentially free
> d) More time-consuming
>> [!success]- Answer
>> c) Essentially free

> [!question] Which of the following is NOT a geometric transformation commonly used in data augmentation?
> a) Horizontal flip
> b) Color jitter
> c) Random crop
> d) Rotation
>> [!success]- Answer
>> b) Color jitter

> [!question] How do CNNs process images?
> a) As three-dimensional objects
> b) As arrays of pixel values
> c) With inherent understanding of physics
> d) With common sense about object behavior
>> [!success]- Answer
>> b) As arrays of pixel values

## Matching

Nine matching questions assemble the full argument: techniques paired to the invariances they teach, the reasons augmentation is necessary, the perceptual gaps of CNNs, the philosophy of encoding prior knowledge, and the concrete benefits. The groups are shuffled independently, so pair by meaning rather than by position.

### Techniques and the invariances they teach

Two questions pairing augmentation techniques with the type of invariance they teach, and with what must hold for the object to be preserved.

> [!question] Match the augmentation technique with the type of invariance it teaches.
>> [!example] Group A
>> a) Horizontal flip
>> b) Random crop
>> c) Color jitter
>
>> [!example] Group B
>> n) Translation invariance
>> o) Photometric invariance
>> p) Horizontal invariance
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the statements with the implications of data augmentation.
>> [!example] Group A
>> a) Horizontal flip augmentation
>> b) Random crop augmentation
>> c) Color jitter augmentation
>
>> [!example] Group B
>> n) Object preserved under left-right reflection
>> o) Object preserved under brightness changes
>> p) Object preserved when not centered
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

### Why augmentation is necessary

Two questions linking CNN properties and real-world facts to the concepts behind augmentation and to the reasons it is necessary.

> [!question] Match the statements with the corresponding concepts.
>> [!example] Group A
>> a) CNN has no concept of 3D space
>> b) Data augmentation is essentially free
>> c) CNNs are data-hungry
>
>> [!example] Group B
>> n) Requires millions of parameters
>> o) Processes images as pixel arrays
>> p) No additional disk storage needed
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the statements with the reasons for data augmentation necessity.
>> [!example] Group A
>> a) CNNs have millions of parameters
>> b) Real-world data is diverse
>> c) Collecting images requires expensive equipment
>
>> [!example] Group B
>> n) Models overfit with insufficient data
>> o) Simulates variations not in training set
>> p) High cost and effort of new data
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### What CNNs lack

Two questions on the properties CNNs lack — object permanence, common sense, gravity — and on the characteristics that follow from how they process images and learn.

> [!question] Match the statements with the corresponding properties of CNNs.
>> [!example] Group A
>> a) No notion of object permanence
>> b) No common sense about object behavior
>> c) No understanding of gravity
>
>> [!example] Group B
>> n) Cannot track objects across views
>> o) Cannot predict object interactions
>> p) Cannot interpret spatial relationships
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the statements with the corresponding characteristics of CNNs.
>> [!example] Group A
>> a) Upright cat and flipped cat are different patterns
>> b) CNN processes images as arrays
>> c) CNN must learn from data alone
>
>> [!example] Group B
>> n) No inherent understanding of transformations
>> o) No concept of semantic categories
>> p) Different from human vision
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### The philosophy of augmentation

Two questions on the aspects of augmentation — geometric transforms, learning from data alone, simulating real-world variations — and on the philosophy that each transformation encodes prior knowledge.

> [!question] Match the statements with the corresponding aspects of data augmentation.
>> [!example] Group A
>> a) Geometric transformations
>> b) CNNs have no concept of physical reality
>> c) Data augmentation provides benefits without new data collection
>
>> [!example] Group B
>> n) Modifies spatial arrangement of pixels
>> o) Requires learning from data alone
>> p) Simulates real-world variations
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the statements with the corresponding aspects of data augmentation philosophy.
>> [!example] Group A
>> a) Each transformation teaches a specific invariance
>> b) CNN has no lifetime of experience
>> c) Augmentation encodes prior knowledge
>
>> [!example] Group B
>> n) Different from human learning
>> o) About physical world properties
>> p) Not just adding variety
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### The concrete benefits

One question pairing the benefits of augmentation with their characteristics.

> [!question] Match the statements with the corresponding data augmentation benefits.
>> [!example] Group A
>> a) Improves validation accuracy
>> b) Requires few lines of code
>> c) No additional disk storage
>
>> [!example] Group B
>> n) On-the-fly transformations
>> o) 2-5 percentage points gain
>> p) Small computation increase
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

## See also

- [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[Normalization, Regularization, and Augmentation Summary]]
- [[Geometric Transformations and Interpolation]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Dropout and Regularization|Dropout and Regularization]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Loss Functions and Optimizers Deep Dive|Loss Functions and Optimizers Deep Dive]]
- [[Glossary MOC]]
