---
title: Deep Learning Definition and Context
type: example
aliases:
  - "Q1 - Deep Learning Definition and Context"
  - "Deep Learning Definition and Context Quiz"
  - "What Is Deep Learning Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - ai-hierarchy
  - representation-learning
  - feature-engineering
  - hierarchical-feature-learning
  - unstructured-data
  - neural-networks
sources:
  - "Q1 - Deep Learning Definition and Context"
created_index: 12
---

This quiz bank practices the definition of deep learning and its place in the nested hierarchy of artificial intelligence, machine learning and deep learning. Its thirty questions cover what the word "deep" actually refers to, representation learning as the automatic discovery of features from raw data, the layered progression from raw edges to whole objects, the mathematical foundations shared with the rest of machine learning, and the unstructured data types where deep learning excels. The concepts are developed in [[AI vs ML vs DL]] and [[Artificial Neural Networks]], with the application landscape in [[01 - Foundations/AI ML and DL Hierarchy/Applications of Deep Learning|Applications of Deep Learning]]; settle on an answer before unfolding it.

## True or false

Ten statements open the quiz: four on which field contains which, two on what "deep" means, two on manual versus learned features, and two on layered detection and shared mathematics. The false statements reverse the containment chain or romanticize the word "deep", so check the direction of every subset claim before committing.

### The hierarchy from AI to deep learning

Four statements on the nesting of the three fields, two of them deliberately inverted.

> [!question] Deep Learning is a sub-domain of Machine Learning.
>> [!success]- Answer
>> True

> [!question] Artificial Intelligence is a subset of Machine Learning.
>> [!success]- Answer
>> False

> [!question] Machine Learning is a subset of Artificial Intelligence.
>> [!success]- Answer
>> True

> [!question] All Machine Learning is Deep Learning.
>> [!success]- Answer
>> False

### What 'deep' actually means

Two statements on the architecture the word refers to and the misreading it invites.

> [!question] Deep Learning uses Artificial Neural Networks with multiple hidden layers.
>> [!success]- Answer
>> True

> [!question] The word 'deep' in Deep Learning refers to a profound understanding of data.
>> [!success]- Answer
>> False

### Manual engineering versus representation learning

Two statements on who builds the features in each paradigm.

> [!question] Traditional Machine Learning requires manual feature engineering.
>> [!success]- Answer
>> True

> [!question] Deep Learning performs Representation Learning automatically from raw data.
>> [!success]- Answer
>> True

### Layers and shared mathematics

Two statements on what successive layers learn to detect and what both fields share underneath.

> [!question] In Deep Learning, Layer 1 might detect raw edges while deeper layers detect whole objects.
>> [!success]- Answer
>> True

> [!question] Deep Learning and Machine Learning share mathematical foundations such as gradient descent and loss functions.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions trace the concept from the top of the hierarchy down: the broadest scope, the defining characteristic, the algorithms on each side, representation learning and the layer stack, the preferred data, and why depth makes previously intractable problems solvable. Several wrong options attach real properties to the wrong paradigm, so classify each option before choosing it.

### The hierarchy and the definition

Two questions on the broadest concept in the AI hierarchy and the defining characteristic of deep learning.

> [!question] Which of the following is the broadest concept in the AI hierarchy?
> a) Machine Learning
> b) Deep Learning
> c) Artificial Intelligence
> d) Neural Networks
>> [!success]- Answer
>> c) Artificial Intelligence

> [!question] What is the defining characteristic of Deep Learning?
> a) It uses decision trees
> b) It uses deep neural networks with multiple hidden layers
> c) It only works on tabular data
> d) It requires no data
>> [!success]- Answer
>> b) It uses deep neural networks with multiple hidden layers

### Algorithms, representations, and layers

Three questions on a traditional machine learning algorithm, what representation learning means, and what Layer 2 typically detects.

> [!question] Which algorithm is an example of traditional Machine Learning?
> a) Convolutional Neural Network
> b) Transformer
> c) Support Vector Machine
> d) Recurrent Neural Network
>> [!success]- Answer
>> c) Support Vector Machine

> [!question] What does Representation Learning mean in the context of Deep Learning?
> a) Humans manually define features
> b) The network automatically discovers useful features from raw data
> c) The data is represented in tables
> d) The output is always an image
>> [!success]- Answer
>> b) The network automatically discovers useful features from raw data

> [!question] In the layered architecture of Deep Learning, what does Layer 2 typically learn to detect?
> a) Raw pixels
> b) Raw edges and gradients
> c) Shapes formed by combining edges
> d) Nothing — only Layer 1 matters
>> [!success]- Answer
>> c) Shapes formed by combining edges

### Relationships, data, and architectures

Three questions on how ML and DL relate, the data deep learning excels at, and a canonical deep learning architecture.

> [!question] Which statement correctly describes the relationship between ML and DL?
> a) All Machine Learning is Deep Learning
> b) Deep Learning and Machine Learning are unrelated
> c) All Deep Learning is Machine Learning, but not all Machine Learning is Deep Learning
> d) Machine Learning is a subset of Deep Learning
>> [!success]- Answer
>> c) All Deep Learning is Machine Learning, but not all Machine Learning is Deep Learning

> [!question] What type of data does Deep Learning excel at processing?
> a) Only structured tabular data
> b) Only numerical data
> c) Unstructured data such as images, audio, and text
> d) Only text data
>> [!success]- Answer
>> c) Unstructured data such as images, audio, and text

> [!question] Which of the following is an example of a Deep Learning architecture?
> a) Random Forest
> b) Linear Regression
> c) Support Vector Machine
> d) Convolutional Neural Network
>> [!success]- Answer
>> d) Convolutional Neural Network

### Feature extraction and intractable problems

Two questions on the feature-extraction divide and why architectural depth unlocks problems traditional ML cannot solve.

> [!question] What distinguishes Deep Learning from traditional Machine Learning in terms of feature extraction?
> a) Deep Learning requires more human feature engineering
> b) Deep Learning automatically learns features while traditional ML requires manual feature engineering
> c) Both require the same amount of manual feature engineering
> d) Traditional ML learns features automatically
>> [!success]- Answer
>> b) Deep Learning automatically learns features while traditional ML requires manual feature engineering

> [!question] Why is Deep Learning able to tackle problems that are intractable for traditional ML?
> a) It uses less data
> b) Its architectural depth enables hierarchical representation learning
> c) It avoids using gradient descent
> d) It does not use loss functions
>> [!success]- Answer
>> b) Its architectural depth enables hierarchical representation learning

## Matching

Ten matching questions pair AI concepts with their scope, concepts with example algorithms, layers with what they detect, terms with definitions, data types with the approach that handles them, and properties with the paradigm they apply to. The two groups are shuffled independently, so match on meaning rather than position.

### Scope, examples, and layers

Three questions matching concepts to their scope, to key examples, and layers to what they learn to detect.

> [!question] Match the AI concept with its scope.
>> [!example] Group A
>> a) Artificial Intelligence
>> b) Machine Learning
>> c) Deep Learning
>
>> [!example] Group B
>> n) Broadest — any technique mimicking human intelligence
>> o) Subset of AI — statistical learning from data
>> p) Subset of ML — deep neural networks learning from raw data
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the concept with a key example.
>> [!example] Group A
>> a) AI
>> b) ML
>> c) DL
>
>> [!example] Group B
>> n) Logic rules, decision trees, expert systems
>> o) SVMs, Random Forests, Linear Regression
>> p) CNNs, RNNs, Transformers
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the layer with what it typically learns to detect.
>> [!example] Group A
>> a) Layer 1
>> b) Layer 2
>> c) Layer 3
>
>> [!example] Group B
>> n) Whole objects (faces, cars, animals)
>> o) Raw edges (simple gradients, lines)
>> p) Shapes (eyes, noses, corners)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Terms, data types, and algorithm categories

Three questions on representation learning versus feature engineering, structured versus unstructured data, and which category each algorithm belongs to.

> [!question] Match the term with its definition.
>> [!example] Group A
>> a) Representation Learning
>> b) Feature Engineering
>> c) Deep Architecture
>
>> [!example] Group B
>> n) Manual extraction of features by a human expert
>> o) Multiple hidden layers in a neural network
>> p) Automatic discovery of features from raw data
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the data type with the approach that best handles it.
>> [!example] Group A
>> a) Structured/tabular data
>> b) Unstructured raw data
>
>> [!example] Group B
>> n) Deep Learning excels
>> o) Traditional ML often sufficient
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the ML algorithm with its category.
>> [!example] Group A
>> a) Random Forest
>> b) CNN
>> c) SVM
>
>> [!example] Group B
>> n) Deep Learning
>> o) Traditional ML
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> o)

### Claims and application domains

Two questions sorting deep learning claims by correctness and matching domains to application examples.

> [!question] Match the statement about DL with its correctness.
>> [!example] Group A
>> a) DL is a subset of ML
>> b) DL requires manual feature engineering
>> c) DL uses ANNs with multiple hidden layers
>
>> [!example] Group B
>> n) True
>> o) False
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> n)

> [!question] Match the domain with a DL application example.
>> [!example] Group A
>> a) Computer Vision
>> b) NLP
>> c) Generative AI
>
>> [!example] Group B
>> n) Image classification, OCR, medical diagnosis
>> o) ChatGPT, Gemini, text generation
>> p) Translation, sentiment analysis
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

### Paradigm characteristics and shared properties

Two questions on which paradigm each characteristic belongs to and which field each property applies to.

> [!question] Match the characteristic with the correct paradigm.
>> [!example] Group A
>> a) Hierarchical feature learning
>> b) Manual feature extraction
>> c) Statistical algorithms like SVMs
>
>> [!example] Group B
>> n) Traditional ML
>> o) Deep Learning
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> n)

> [!question] Match the property with whether it applies to DL or traditional ML.
>> [!example] Group A
>> a) Learns directly from raw pixels
>> b) Requires domain expert for features
>> c) Shares math foundations like gradient descent
>
>> [!example] Group B
>> n) Applies to both DL and ML
>> o) Applies to DL only
>> p) Applies to traditional ML only
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

## See also

- [[AI vs ML vs DL]]
- [[Artificial Neural Networks]]
- [[Introduction to Machine Learning]]
- [[Convolutional Neural Networks]]
- [[Recurrent Neural Networks]]
- [[Machine Learning vs Deep Learning]]
- [[Evolution and History of Deep Learning]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Applications of Deep Learning|Applications of Deep Learning]]
- [[Multi-Layer Perceptron and Backpropagation]]
- [[Glossary MOC]]
