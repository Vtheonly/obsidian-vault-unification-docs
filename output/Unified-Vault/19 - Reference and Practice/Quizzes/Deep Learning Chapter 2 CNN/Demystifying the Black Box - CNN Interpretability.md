---
title: Demystifying the Black Box - CNN Interpretability
type: example
aliases:
  - "Q26 - Demystifying the Black Box - CNN Interpretability"
  - "CNN Interpretability Quiz"
  - "Demystifying the Black Box Quiz"
  - "Grad-CAM Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - interpretability
  - explainability
  - grad-cam
  - heatmap
  - medical-diagnosis
  - autonomous-driving
  - gdpr
  - eu-ai-act
sources:
  - "Q26 - Demystifying the Black Box - CNN Interpretability"
created_index: 28
---

This quiz bank practices CNN interpretability — the toolkit for answering why a network predicted what it did, and the regulations that increasingly demand an answer. Its twenty-nine questions cover the black-box problem and why high accuracy alone does not guarantee meaningful learning, the Grad-CAM pipeline that turns gradients and the last convolutional layer into a class-specific heatmap, and the domain requirements that run from medical diagnosis and autonomous driving through debugging to GDPR's right to explanation, the EU AI Act, and FDA oversight. The concepts are developed in [[CNN Interpretability]] and [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]], with the surrounding evaluation pipeline in [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: two on the black-box problem itself, four on Grad-CAM and the layer it reads, and four on where interpretability is demanded — medicine, driving, and the regulatory frameworks. The false statements claim accuracy is a sufficient substitute for explanation, so ask what each claim would let you skip verifying.

### The black box problem

Two statements on why CNNs are called black boxes and on what high accuracy does and does not guarantee.

> [!question] Convolutional Neural Networks are often referred to as "black boxes" because we don't know why they make certain predictions.
>> [!success]- Answer
>> True

> [!question] High accuracy in a CNN model guarantees that it has learned meaningful patterns.
>> [!success]- Answer
>> False

### Grad-CAM and the layer it reads

Four statements on what Grad-CAM produces, when it was introduced, and why the last convolutional layer is the layer to read — plus one claim that reverses the feature hierarchy.

> [!question] Grad-CAM produces a heatmap highlighting regions of an input image that are important for a CNN's prediction of a particular class.
>> [!success]- Answer
>> True

> [!question] Grad-CAM was introduced in 2017 by Selvaraju et al.
>> [!success]- Answer
>> True

> [!question] The last convolutional layer of a CNN has the highest spatial resolution and semantic richness.
>> [!success]- Answer
>> True

> [!question] Earlier layers in a CNN capture high-level semantic features while later layers capture low-level features.
>> [!success]- Answer
>> False

### Regulation and high-stakes domains

Four statements on the right to explanation, the 2024 EU AI Act, and whether accuracy alone is enough in medical diagnosis and autonomous driving.

> [!question] The European Union's General Data Protection Regulation (GDPR) includes a "right to explanation" for automated system decisions.
>> [!success]- Answer
>> True

> [!question] The EU AI Act passed in 2024 strengthens interpretability requirements for high-risk AI systems.
>> [!success]- Answer
>> True

> [!question] In medical diagnosis, interpretability is not important as long as the model achieves high accuracy.
>> [!success]- Answer
>> False

> [!question] Autonomous driving systems do not require interpretability as long as they make correct decisions.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions move from what interpretability is for, through the mechanics of Grad-CAM and the layer it targets, to the shortcuts a diagnostic CNN might exploit and what regulators require. The Grad-CAM options are close cousins of one another — several describe true facts about the network — so match each option to the exact question being asked.

### What interpretability is for

Two questions on which domain does not strictly require interpretability and on what interpretability reveals when debugging a model.

> [!question] Which of the following is NOT a domain where interpretability is critical?
> a) Autonomous Driving
> b) Medical Diagnosis
> c) Image Classification
> d) Legal Compliance
>> [!success]- Answer
>> c) Image Classification

> [!question] Why is interpretability important for debugging and model improvement?
> a) It allows engineers to increase model accuracy
> b) It reveals data quality issues and architectural problems
> c) It reduces the training time
> d) It decreases model complexity
>> [!success]- Answer
>> b) It reveals data quality issues and architectural problems

### How Grad-CAM works

Four questions on Grad-CAM's purpose, the "sweet spot" layer, the key insight behind the method, and the first step of the process.

> [!question] What is the primary purpose of Grad-CAM?
> a) To increase the accuracy of CNNs
> b) To identify which spatial locations influence a CNN's prediction for a specific class
> c) To reduce the computational complexity of CNNs
> d) To generate new images
>> [!success]- Answer
>> b) To identify which spatial locations influence a CNN's prediction for a specific class

> [!question] Which layer in a CNN is considered the "sweet spot" for Grad-CAM?
> a) The first convolutional layer
> b) The last fully connected layer
> c) The last convolutional layer
> d) The pooling layer
>> [!success]- Answer
>> c) The last convolutional layer

> [!question] What is the key insight behind Grad-CAM?
> a) Earlier layers capture both spatial and semantic information
> b) The last convolutional layer retains spatial information and has semantic richness
> c) Fully connected layers contain the most important features
> d) Pooling layers preserve spatial information
>> [!success]- Answer
>> b) The last convolutional layer retains spatial information and has semantic richness

> [!question] What is the first step in the Grad-CAM process?
> a) Backprop gradient to last conv layer
> b) Get feature maps from last conv layer
> c) Forward pass to get predicted class
> d) Upsample and overlay on original image
>> [!success]- Answer
>> c) Forward pass to get predicted class

### Shortcuts, regulation, and the right to explanation

Three questions on the spurious feature a medical CNN might learn, what the FDA requires of AI-based diagnostic tools, and what GDPR's right to explanation allows.

> [!question] According to the text, what might a CNN trained for medical diagnosis learn to exploit?
> a) Clinically relevant features
> b) Hospital watermarks
> c) Patient names
> d) Image resolution
>> [!success]- Answer
>> b) Hospital watermarks

> [!question] What does the FDA require for AI-based diagnostic tools?
> a) Maximum accuracy
> b) Evidence that decisions are based on clinically relevant features
> c) Minimum computational requirements
> d) Open-source implementation
>> [!success]- Answer
>> b) Evidence that decisions are based on clinically relevant features

> [!question] What does the "right to explanation" in GDPR allow individuals to do?
> a) Request deletion of their data
> b) Understand why an automated system made a decision about them
> c) Opt out of automated decision-making
> d) Access all their data
>> [!success]- Answer
>> b) Understand why an automated system made a decision about them

## Matching

Ten matching questions pair the Grad-CAM pipeline steps and components with their roles, the CNN layers and techniques with their characteristics, the application domains with their requirements and benefits, and the failure scenarios with their causes. The two groups in each question are shuffled independently, so reconstruct each mapping from meaning rather than position.

### The Grad-CAM pipeline

Two questions on the six steps of the method in order and on the role each mathematical component plays.

> [!question] Match the following Grad-CAM steps with their descriptions.
>> [!example] Steps
>> a) Forward pass → Get predicted class c
>> b) Backprop gradient ∂yᶜ/∂Aᵏ to last conv layer
>> c) Weighted combination + ReLU → Lᶜ
>> d) Global avg pool gradients → weights αₖ
>> e) Upsample & overlay on original image
>> f) Target last conv layer → Get feature maps Aᵏ
>
>> [!example] Descriptions
>> n) Combine feature maps with gradient weights and apply ReLU
>> o) Calculate average of gradients across spatial dimensions to get importance weights
>> p) Identify the class the model is predicting
>> q) Compute gradients of the class score with respect to feature maps
>> r) Resize the heatmap to match original image size and overlay
>> s) Extract feature maps from the last convolutional layer
>
>> [!success]- Answer
>> a) -> p)
>> b) -> q)
>> c) -> n)
>> d) -> o)
>> e) -> r)
>> f) -> s)

> [!question] Match the following components of Grad-CAM with their roles.
>> [!example] Components
>> a) Feature maps Aᵏ
>> b) Gradients ∂yᶜ/∂Aᵏ
>> c) Weights αₖ
>> d) ReLU on Lᶜ
>
>> [!example] Roles
>> n) Spatial information from last conv layer
>> o) Importance weights for each feature map
>> p) Gradient information showing influence on class prediction
>> q) Ensuring only positive contributions are highlighted
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)
>> d) -> q)

### Layers and techniques

Two questions on the characteristics of the earlier, later, and last convolutional layers, and on what distinguishes Grad-CAM from simpler activation mapping and other gradient-based methods.

> [!question] Match the following CNN layers with their primary characteristics.
>> [!example] Layers
>> a) Earlier layers
>> b) Later layers
>> c) Last convolutional layer
>
>> [!example] Characteristics
>> n) Capture high-level semantic features
>> o) Represent a sweet spot with both spatial and semantic information
>> p) Capture low-level features
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the following interpretability techniques with their purposes.
>> [!example] Techniques
>> a) Grad-CAM
>> b) Simple Activation Mapping
>> c) Gradient-based methods
>
>> [!example] Purposes
>> n) Shows where the model looks for a specific class
>> o) Shows general regions the model looks at
>> p) Uses gradient information to highlight important regions
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Domains, applications, and regulation

Three questions on the interpretability requirement of each domain, on the benefit interpretability brings to each application, and on what each regulatory framework demands.

> [!question] Match the following domains with their specific interpretability requirements.
>> [!example] Domains
>> a) Autonomous Driving
>> b) Medical Diagnosis
>> c) Legal Compliance
>> d) Debugging and Model Improvement
>
>> [!example] Requirements
>> n) Evidence that decisions are based on clinically relevant features
>> o) Verification that models attend to correct visual features
>> p) Understanding why an automated system made a decision
>> q) Revealing data quality issues and architectural problems
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

> [!question] Match the following CNN interpretability applications with their benefits.
>> [!example] Applications
>> a) Medical diagnosis
>> b) Autonomous driving
>> c) Model debugging
>
>> [!example] Benefits
>> n) Building trust with doctors and patients
>> o) Verifying detection of correct visual features
>> p) Identifying data quality issues and architectural problems
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following regulatory frameworks with their requirements.
>> [!example] Frameworks
>> a) GDPR
>> b) EU AI Act
>> c) FDA regulations for AI
>
>> [!example] Requirements
>> n) "Right to explanation" for automated decisions
>> o) Strengthened requirements for high-risk AI systems
>> p) Evidence that AI-based tools make decisions based on clinically relevant features
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Failure modes and model properties

Three questions on diagnosing failure scenarios from their causes, on what model properties imply for interpretability, and on the vocabulary — class-discriminative, coarse heatmap, spatial resolution — used to describe heatmaps.

> [!question] Match the following model failure scenarios with their potential causes.
>> [!example] Scenarios
>> a) Model achieves high accuracy but fails in deployment
>> b) Model performs well on training data but poorly on validation data
>> c) Model makes consistent errors on specific image types
>
>> [!example] Causes
>> n) Overfitting to spurious features in training data
>> o) Learning irrelevant features that correlate with labels
>> p) Dataset bias or insufficient diversity
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the following model properties with their implications for interpretability.
>> [!example] Properties
>> a) High accuracy
>> b) Exploiting shortcuts
>> c) Learning meaningful patterns
>
>> [!example] Implications
>> n) Model makes predictions for the right reasons
>> o) Model may fail catastrophically in new environments
>> p) Does not guarantee meaningful learning
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the following concepts with their definitions in the context of CNN interpretability.
>> [!example] Concepts
>> a) Class-discriminative
>> b) Coarse heatmap
>> c) Spatial resolution
>
>> [!example] Definitions
>> n) Ability to distinguish between different classes
>> o) Detailed spatial information about where features are located
>> p) Low-resolution visualization showing important regions
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

## See also

The topical concept notes this quiz practices, its sibling quizzes in the same chapter, and adjacent reading on evaluation and interpretability:

- [[CNN Interpretability]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[Model Evaluation Metrics Beyond Accuracy]]
- [[Mechanistic Interpretability]]
- [[Convolutional Neural Networks]]
