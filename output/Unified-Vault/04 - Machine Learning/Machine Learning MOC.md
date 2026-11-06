---
title: Machine Learning MOC
type: overview
aliases: [Machine Learning Map of Content, ML MOC]
tags: [moc, machine-learning]
sources:
  - MOC
created_index: 6
---

This map of content organizes the machine learning area: classical supervised and unsupervised learning, model evaluation, generalization, and reinforcement learning. It is the entry point for the area and lists every note in a recommended reading order. Reinforcement learning matters more than you might think — PPO is the foundation of RLHF, which aligned every modern chatbot.

## Reading order

| # | Note | Sub-domain | Purpose |
|---|---|---|---|
| 01 | [[Regression Fundamentals]] | Supervised | What regression is; the X/y framing and model families. |
| 02 | [[04 - Machine Learning/Regression/Linear Regression\|Linear Regression]] | Supervised | The simplest model; the foundation, from scratch to the normal equations. |
| 03 | [[04 - Machine Learning/Regression/Logistic Regression\|Logistic Regression]] | Supervised | From regression to classification: sigmoid, log-loss, decision boundaries. |
| 04 | [[K-Nearest Neighbors]] | Supervised | Lazy learning, distance metrics, choosing K. |
| 05 | [[Support Vector Machines]] | Supervised | Maximum-margin separation; the widest street. |
| 06 | [[SVM Lagrangian Dual]] | Supervised | The full dual derivation behind the SVM solution. |
| 07 | [[Kernel Trick]] | Supervised | Non-linear separability through kernels. |
| 08 | [[Decision Trees]] | Supervised | Recursive partitioning with Gini and information gain. |
| 09 | [[Random Forests and Bagging]] | Supervised | Variance reduction by ensembling trees. |
| 10 | [[Gradient Boosting]] | Supervised | Still state of the art for tabular data. |
| 11 | [[Clustering]] | Unsupervised | K-Means, DBSCAN, hierarchical clustering. |
| 12 | [[Principal Component Analysis]] | Unsupervised | Linear dimensionality reduction via variance directions. |
| 13 | [[t-SNE and UMAP]] | Unsupervised | Nonlinear embeddings for visualization. |
| 14 | [[Model Evaluation Metrics]] | Evaluation | Accuracy, precision/recall, F1, ROC, calibration. |
| 15 | [[Regression Evaluation Metrics]] | Evaluation | MAE, MSE, RMSE, R2, MAPE and when to use each. |
| 16 | [[Clustering Evaluation Metrics]] | Evaluation | Silhouette, Davies-Bouldin, ARI, NMI. |
| 17 | [[Computer Vision Evaluation Metrics]] | Evaluation | IoU, mAP, Dice for detection and segmentation. |
| 18 | [[Bias Variance Tradeoff]] | Generalization | Why models under/overfit; the fundamental tension. |
| 19 | [[Regularization Techniques]] | Generalization | L1/L2, dropout, early stopping, label smoothing. |
| 20 | [[Loss Functions]] | Optimization | The objectives that training minimizes. |
| 21 | [[Gradient Descent]] | Optimization | The update rule that drives learning. |
| 22 | [[Optimizers and Learning Rate Schedulers]] | Optimization | SGD, momentum, Adam, and LR schedules. |
| 23 | [[Markov Decision Processes and Bellman Equations]] | Reinforcement Learning | The RL formalism. |
| 24 | [[Q-Learning and Deep Q Networks]] | Reinforcement Learning | Value-based RL. |
| 25 | [[Policy Gradients and Actor Critic]] | Reinforcement Learning | Policy-based RL. |
| 26 | [[Proximal Policy Optimization]] | Reinforcement Learning | **Required reading before RLHF.** |

## Sub-domains

- **Supervised learning** — notes 01–10: regression, classification, nearest neighbors, support vector machines, and tree-based models.
- **Unsupervised learning** — notes 11–13: clustering and dimensionality reduction.
- **Evaluation** — notes 14–17: metric families for classification, regression, clustering, and computer vision.
- **Generalization** — notes 18–19: the bias-variance tension and the techniques that manage it.
- **Optimization** — notes 20–22: loss functions, gradient descent, and the optimizer toolbox.
- **Reinforcement learning** — notes 23–26: MDPs, Q-learning, policy gradients, and PPO.

## Why this area matters

- **Classical ML is still the right tool for many problems.** Tabular data, small datasets, interpretable models — gradient boosting beats deep learning here.
- **RL is the foundation of RLHF.** Without understanding PPO, you can't understand how ChatGPT was aligned.
- **Evaluation is its own skill.** Most ML failures are evaluation failures: wrong metric, leaked test set, uncalibrated probabilities.

## Reading order recommendation

### If you're new to ML
Read all 26 notes in order. Expect roughly four to six weeks of part-time study.

### If you already know classical ML
Skip to note 23 (Markov Decision Processes) and read notes 23–26 for the RL foundation you need for RLHF.

### If you only have time for one note
Read [[Proximal Policy Optimization]] — it's the prerequisite for understanding RLHF.

## See also

- The mathematics behind ML (calculus, linear algebra, probability) lives in the Mathematics area.
- Neural networks and deep learning build directly on the optimization notes here.
- Fine-tuning is where PPO is put to work in RLHF; pretraining at scale extends the training notes.
