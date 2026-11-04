---
title: Model Evaluation Metrics Beyond Accuracy
type: example
aliases:
  - "Q21 - Model Evaluation Metrics Beyond Accuracy"
  - "Model Evaluation Metrics Beyond Accuracy Quiz"
  - "Evaluation Metrics Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - evaluation-metrics
  - accuracy
  - confusion-matrix
  - precision
  - recall
  - f1-score
  - specificity
  - class-imbalance
  - medical-diagnosis
  - fraud-detection
sources:
  - "Q21 - Model Evaluation Metrics Beyond Accuracy"
created_index: 36
---

This quiz bank practices the evaluation metrics that matter once accuracy stops being trustworthy. Its thirty-one questions cover the confusion matrix and its cells, precision, recall, the F1 score, and specificity, the behaviour of accuracy on balanced versus imbalanced datasets, and the asymmetric costs of false positives and false negatives in medical diagnosis and fraud detection. The underlying theory is developed in [[Model Evaluation Metrics]] and [[Computer Vision Evaluation Metrics]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: five on accuracy and how it behaves under class balance and imbalance, three on the confusion matrix and the metrics derived from it, and two on what each error type costs in medicine. The false statements invert well-known facts — accuracy as a universal metric, true positives defined as misclassifications — so check each claim against the definitions before committing.

### Accuracy, balance, and imbalance

Five statements on when accuracy is appropriate, what a majority-class predictor scores, and what high accuracy on an imbalanced dataset really guarantees.

> [!question] Accuracy is a reliable metric for all types of datasets.
>> [!success]- Answer
>> False

> [!question] A model that always predicts the majority class will always have high accuracy.
>> [!success]- Answer
>> True

> [!question] In a balanced dataset, accuracy is an appropriate evaluation metric.
>> [!success]- Answer
>> True

> [!question] In a dataset with 990 healthy patients and 10 diseased patients, a model that always predicts "healthy" will have 99% accuracy.
>> [!success]- Answer
>> True

> [!question] High accuracy on an imbalanced dataset guarantees good model performance.
>> [!success]- Answer
>> False

### The confusion matrix and its cells

Three statements on the scope of the confusion matrix, the definition of a true positive, and where precision and recall come from.

> [!question] A confusion matrix can only be used for binary classification problems.
>> [!success]- Answer
>> False

> [!question] True Positives represent instances where the model incorrectly identifies a negative case as positive.
>> [!success]- Answer
>> False

> [!question] Precision and recall are derived from the confusion matrix.
>> [!success]- Answer
>> True

### The price of each error type in medicine

Two statements on which error hurts more in diagnosis, and what a false positive does to a healthy patient.

> [!question] False negatives are generally more dangerous than false positives in medical diagnosis.
>> [!success]- Answer
>> True

> [!question] False positives in medical screening lead to unnecessary treatment and wasted resources.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions cover accuracy's blind spots, a worked accuracy computation, the definition of a confusion-matrix cell, and the precision-recall trade-off. Several wrong options describe a neighboring metric — recall's definition appears under precision's question, specificity's under recall's — so read each option against the exact wording of the claim.

### Where accuracy breaks

Two questions on accuracy's primary limitation and the dataset shape that makes it misleading.

> [!question] What is the primary limitation of accuracy as an evaluation metric?
> a) It's computationally expensive
> b) It doesn't account for class imbalance
> c) It only works for linear models
> d) It requires large datasets
>> [!success]- Answer
>> b) It doesn't account for class imbalance

> [!question] Which scenario would make accuracy a particularly misleading metric?
> a) A balanced dataset with equal representation of all classes
> b) A dataset with severe class imbalance
> c) A dataset with only one class
> d) A small dataset
>> [!success]- Answer
>> b) A dataset with severe class imbalance

### Computing accuracy from the cells

One worked numeric question: tally the four cells and divide by the total.

> [!question] A model has 100 true positives, 50 false positives, 20 false negatives, and 830 true negatives. What is the accuracy?
> a) 89%
> b) 93%
> c) 95%
> d) 97%
>> [!success]- Answer
>> b) 93%

### Inside the confusion matrix

One question pinning down the least glamorous cell, the true negative.

> [!question] In the confusion matrix, what does a True Negative represent?
> a) The model incorrectly predicts negative when the actual is positive
> b) The model correctly predicts negative when the actual is negative
> c) The model incorrectly predicts positive when the actual is negative
> d) The model correctly predicts positive when the actual is positive
>> [!success]- Answer
>> b) The model correctly predicts negative when the actual is negative

### Precision, recall, and the F1 score

Three questions on what precision measures, what a high-recall/low-precision profile indicates, and how the F1 score combines the two.

> [!question] What does a precision metric measure?
> a) The proportion of actual positives that are correctly identified
> b) The proportion of predicted positives that are actual positives
> c) The balance between precision and recall
> d) The overall model performance
>> [!success]- Answer
>> b) The proportion of predicted positives that are actual positives

> [!question] If a model has high recall but low precision, what does this indicate?
> a) The model makes many false alarms but catches most actual positives
> b) The model has balanced performance between precision and recall
> c) The model misses many actual positives but has few false alarms
> d) The model performs poorly on all metrics
>> [!success]- Answer
>> a) The model makes many false alarms but catches most actual positives

> [!question] What is the F1 score?
> a) The harmonic mean of precision and recall
> b) The arithmetic mean of precision and recall
> c) The minimum of precision and recall
> d) The maximum of precision and recall
>> [!success]- Answer
>> a) The harmonic mean of precision and recall

### Error costs and the negative class

Three questions on the costlier error in rare-disease diagnosis and fraud detection, and the metric that watches the negatives.

> [!question] In a medical diagnosis scenario with a rare disease, which type of error is typically more dangerous?
> a) False positive
> b) False negative
> c) Both are equally dangerous
> d) Neither is particularly dangerous
>> [!success]- Answer
>> b) False negative

> [!question] In fraud detection, which type of error is typically more costly?
> a) False positive (legitimate transaction flagged as fraud)
> b) False negative (fraudulent transaction missed)
> c) Both errors are equally costly
> d) Neither error is particularly costly
>> [!success]- Answer
>> b) False negative (fraudulent transaction missed)

> [!question] What is specificity?
> a) The proportion of actual negatives that are correctly identified
> b) The proportion of actual positives that are correctly identified
> c) The balance between precision and recall
> d) The overall model performance
>> [!success]- Answer
>> a) The proportion of actual negatives that are correctly identified

## Matching

Eleven matching questions pair confusion-matrix cells with their definitions, metrics with their formulas and properties, application domains with the metric each one demands, and error types with their real-world consequences. The groups are shuffled independently, so match from meaning rather than position.

### Confusion matrix cells and metric formulas

Two questions pairing the cells with their definitions and the metrics with their formulas.

> [!question] Match the confusion matrix components with their definitions.
>> [!example] Group A
>> a) True Positive
>> b) False Negative
>> c) False Positive
>
>> [!example] Group B
>> n) Model predicts positive when actual is negative
>> o) Model predicts positive when actual is positive
>> p) Model predicts negative when actual is positive
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the evaluation metrics with their formulas.
>> [!example] Group A
>> a) Precision
>> b) Recall
>> c) F1 Score
>
>> [!example] Group B
>> n) TP / (TP + FP)
>> o) 2 × (Precision × Recall) / (Precision + Recall)
>> p) TP / (TP + FN)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

### What each metric measures

Three questions on the primary focus of accuracy, specificity, and F1, the rates built from the matrix cells, and the mathematical properties of precision, recall, and F1.

> [!question] Match the metrics with what they primarily measure.
>> [!example] Group A
>> a) Accuracy
>> b) Specificity
>> c) F1 Score
>
>> [!example] Group B
>> n) Overall correctness of predictions
>> o) Ability to correctly identify negative cases
>> p) Balance between precision and recall
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the evaluation metrics with their focus areas.
>> [!example] Group A
>> a) True Positive Rate
>> b) False Positive Rate
>> c) True Negative Rate
>
>> [!example] Group B
>> n) Proportion of actual negatives incorrectly classified
>> o) Proportion of actual positives correctly classified
>> p) Proportion of actual negatives correctly classified
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the evaluation metrics with their mathematical properties.
>> [!example] Group A
>> a) Precision
>> b) Recall
>> c) F1 Score
>
>> [!example] Group B
>> n) Can be misleading with imbalanced data
>> o) Focuses on minimizing false positives
>> p) Harmonic mean of precision and recall
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Matching problems to metrics

Two questions assigning metrics to application domains: deadly-disease diagnosis, spam detection, credit card fraud detection, and sentiment analysis.

> [!question] Match the scenarios with their appropriate evaluation metrics.
>> [!example] Group A
>> a) Medical diagnosis of a deadly disease
>> b) Spam email detection
>> c) Credit card fraud detection
>
>> [!example] Group B
>> n) High recall (minimize false negatives)
>> o) High precision (minimize false positives)
>> p) Balanced precision and recall
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the classification problems with their appropriate evaluation metrics.
>> [!example] Group A
>> a) Rare disease detection
>> b) Spam filtering
>> c) Sentiment analysis
>
>> [!example] Group B
>> n) High recall (minimize false negatives)
>> o) High precision (minimize false positives)
>> p) Balanced metrics (F1 score)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### When errors cost differently

Two questions on the consequences of each error type in medical diagnosis, and on which metric to reach for when one error type is costlier than the other.

> [!question] Match the types of errors with their consequences in medical diagnosis.
>> [!example] Group A
>> a) False Positive
>> b) False Negative
>> c) True Negative
>
>> [!example] Group B
>> n) Patient receives unnecessary treatment
>> o) Patient's condition goes untreated
>> p) No unnecessary treatment or alarm
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the model evaluation scenarios with their appropriate metrics.
>> [!example] Group A
>> a) When false positives are very costly
>> b) When false negatives are very costly
>> c) When both types of errors have similar costs
>
>> [!example] Group B
>> n) High precision
>> o) High recall
>> p) Balanced precision and recall
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Metrics under class imbalance

Two questions on which metric suits which dataset shape, and how sensitive each metric family is to imbalance.

> [!question] Match the evaluation scenarios with their appropriate metrics.
>> [!example] Group A
>> a) Imbalanced dataset with important minority class
>> b) Balanced dataset with equal importance for all classes
>> c) When both false positives and false negatives are equally costly
>
>> [!example] Group B
>> n) Precision and recall
>> o) Accuracy
>> p) F1 Score
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the metric types with their sensitivity to class imbalance.
>> [!example] Group A
>> a) Accuracy
>> b) Precision and Recall
>> c) F1 Score
>
>> [!example] Group B
>> n) Highly sensitive to class imbalance
>> o) Moderately sensitive to class imbalance
>> p) Less sensitive to class imbalance
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

## See also

- [[Model Evaluation Metrics]]
- [[Computer Vision Evaluation Metrics]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[06 - Computer Vision/Pipeline Evaluation and Interpretability/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[CNN Interpretability]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Common Mistakes and How to Fix Them|Common Mistakes and How to Fix Them]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/The Full Training Pipeline End-to-End Checklist|The Full Training Pipeline End-to-End Checklist]]
- [[Demystifying the Black Box - CNN Interpretability]]
- [[Loss Functions and Optimizers Deep Dive]]
- [[The Convolution Operation Deep Dive]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]]
- [[Glossary MOC]]
