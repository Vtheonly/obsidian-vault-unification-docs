#!/usr/bin/env python3
"""DISC-002 session 6 (batch 6): emit the 60 review decisions as JSONL.

Method (same as batches 3-5): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch5 state,
session-6 fresh replay), a definitional-treatment coverage probe
(scripts/disc002_batch6_probe.py, results in
/home/z/my-project/scratch/disc002-batch6-probe.json), targeted corpus
verification for citations (scripts/disc002_batch6_verify.py), and an
independent subagent cross-check of 15 judgment calls: 15/15 AGREE, with
path completions and two evidence upgrades incorporated (ai-course paths
must carry their chapter-level parents; master-ai
'28 - Glossary/03 - Notation Conventions.md:54' supplies the diag(x)
definitional entry for the diagonal cover; master-ai
'02 - Mathematics/Probability/09 - Gaussian Distribution.md' strengthens
the randn cover; '06 - Tensors and Broadcasting.md:258' recharacterized
as a code comment, cited as in-situ usage only).

Result: 5 cover (evidence-cited) + 55 reject. No new confirmed gaps.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/concept-candidates/002-disc002-decisions-batch6.jsonl")

R = "GLM-5.3 orchestrator, DISC-002 session 6 (batch 6, subagent cross-checked)"

decisions = [
    # ---- covers (5) ----
    ("CG-bce6ebd3e75c", "cover",
     "random-normal sampling has dedicated and definitional treatments: master-ai "
     "'02 - Mathematics/Probability/09 - Gaussian Distribution.md' ('## Definition' :14-16, with "
     "'x = torch.randn(1000)  # standard normal' :102) and ai-course '02 - Python and Data Tooling/"
     "02.3 - Essential Python Libraries/01. NumPy - Numerical Computation and Arrays.md:34' "
     "('randn = np.random.randn(3, 2)   # Standard Normal distribution (Mean=0, Std=1)'); in-situ "
     "rationale headings ai-course '05 - Convolutional Neural Networks (CNN)/05. Pipeline, "
     "Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md:368' "
     "('# We use random values (randn) because the actual...') and '04. Exercises Solved and "
     "Explained.md:1576' ('# Using randn (random normal) because it's fast and produces non-zero "
     "values'); derivation uses master-ai '06 - Attention Mechanisms/Self-Attention/04 - "
     "Self-Attention.md:179' (product of two independent standard normal random variables) and "
     "master-ai '04 - Neural Networks/Foundations/02 - Activation Functions.md:75' (GELU, Phi is "
     "the standard normal CDF)."),
    ("CG-b529f3824b55", "cover",
     "the eval-set concept has dedicated sections and definition sentences in master-ai: "
     "'27 - Projects/Capstones/13 - Build a RAG Evaluation Harness.md:56,72' (eval dataset as "
     "{query, expected_answer, relevant_doc_ids} triples; '# Example: a small eval set for a "
     "documentation RAG'), '17 - RAG/Ingestion and Retrieval/01 - RAG Pipeline Overview.md:343' "
     "('### Building an Evaluation Set'), '21 - LLMOps and MLOps/Pipelines/01 - LLMOps vs "
     "MLOps.md:155,157' ('All provide eval set management, multi-metric evaluation...'; 'The eval "
     "set itself is a living artifact'), and '09 - Foundation Models/Embedding Models/06 - "
     "Embedding Model Training.md:198' (build a small domain eval set as the most reliable signal "
     "for production fitness); the classical split counterpart is covered at ai-course "
     "'01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine "
     "Learning (Summary).md:267,324' ('## 2. Validation Set (15%)', '## 3. Test Set (15%)')."),
    ("CG-cbda84f8b856", "cover",
     "scikit-learn's role has dedicated section headings and guidance sentences: ai-course "
     "'02 - Python and Data Tooling/02.4 - Data Cleaning and Preprocessing/05. Categorical "
     "Encoding and Text Normalization.md:63' ('# Using sklearn (better for ML pipelines, handles "
     "unseen categories):'), '05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries "
     "(Aggregated)/01. Foundations and Philosophy - Summary.md:815' ('### 1.12.3. PyTorch and "
     "Scikit-Learn Implementation'), '07. Scaling, Pipeline and Interpretability - "
     "Summary.md:462' ('### 2.11 Computing Metrics in PyTorch and Scikit-Learn'), '03 - Machine "
     "Learning/03.1 - Regression/07. Lab - Guide Complet Régression Linéaire et Deep Learning "
     "(MNIST).md:27' ('### 2. Analyse du Code (Scikit-Learn)'), and '03 - Machine Learning/03.6 - "
     "Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md:302' ('using PyTorch for "
     "model inference and scikit-learn for metric computation ... standard workflow'); master-ai "
     "worked example at '03 - Machine Learning/Unsupervised Learning/04 - Clustering and "
     "Dimensionality Reduction.md:100'; K-Means n_init=10 default at ai-course '03 - Machine "
     "Learning/03.5 - K-Means Clustering/01. K-Means Clustering.md:154'."),
    ("CG-b299100d0604", "cover",
     "probability distribution is defined and treated directly: ai-course '01 - Foundations and "
     "Overview/01.2 - Mathematical Foundations/07. Probability and Statistics for ML.md:12' ('A "
     "**random variable** X is a variable whose value is uncertain, described by a probability "
     "distribution.') under '## Random variables and distributions'; master-ai '08 - LLMs/Sampling/"
     "03 - Sampling Strategies.md:246' ('## The Probability Distribution View'); master-ai "
     "'02 - Mathematics/Probability/07 - Probability Essentials.md:335' ('A language model is a "
     "probability distribution over token sequences'); softmax conversion at ai-course '03 - "
     "Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep "
     "Dive.md:22'."),
    ("CG-0b80ace43394", "cover",
     "the diagonal-matrix concept has definitional treatments: master-ai '28 - Glossary/03 - "
     "Notation Conventions.md:54' ('diag(x): diagonal matrix with x on the diagonal') and "
     "'02 - Mathematics/Linear Algebra/05 - Matrix Decomposition.md:43' ('Lambda is a diagonal "
     "matrix of eigenvalues'); ai-course '01 - Foundations and Overview/01.2 - Mathematical "
     "Foundations/00. Linear Algebra Fundamentals.md:52' (Trace = sum of diagonal), :71 (Lambda "
     "diagonal in eigendecomposition), :91 (Sigma diagonal in SVD); applied treatments ai-course "
     "'07 - Sequence Models and RNNs/07.1 - Motivation and Recurrence/03. Backpropagation Through "
     "Time (BPTT).md:79' ('diag(1 - h_t^2) — a diagonal matrix whose entries lie in [0, 1]') and "
     "master-ai '02 - Mathematics/Calculus/11 - Jacobians and Hessians.md:224' ('Adam is a "
     "diagonal preconditioner (using the diagonal of the empirical Hessian)'); supporting in-situ "
     "usage only: master-ai '02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md:258' "
     "('# 6. Diagonal extraction' — a code comment inside a code block)."),
    # ---- rejects (55) ----
    ("CG-00a377570459", "reject",
     "Non-concept noise (generic-vocabulary): adjective ('appropriate metric/method/rotation'). "
     "Note: metric-selection guidance is covered in-situ by ai-course '03 - Machine Learning/"
     "03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md:209,239' "
     "(macro/micro-averaging guidance) and the adaptive-optimizer treatments at '03.2 - "
     "Optimization Algorithms/01. Gradient Descent Optimization (DL Course).md:170'."),
    ("CG-d11be03e7fb5", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('writing Python scripts/code'). Note: IDE "
     "and environment guidance covered by ai-course '02 - Python and Data Tooling/02.1 - Python "
     "Environment Setup/03. IDEs and Development Environments.md:26,35'."),
    ("CG-d97bd29c3170", "reject",
     "Non-concept noise (generic-vocabulary): participial prose ('leading to much faster "
     "convergence', 'leading to unstable updates'). Note: the underlying trade-offs are covered "
     "by the mini-batch update-frequency treatment ('01. Gradient Descent Optimization (DL "
     "Course).md:270') and the initialization-sensitivity treatments ('08. Loss Functions and "
     "Optimizers Deep Dive.md:543')."),
    ("CG-588ec7dada83", "reject",
     "Non-concept noise (possessive prose-fragment): possessive of 'network' ('network's layers/"
     "weights/predicted probability'). Note: the network concept is covered by the dedicated "
     "ANN/MLP notes (ai-course '04 - Neural Networks and Deep Learning Foundations/04.1 - Neural "
     "Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md')."),
    ("CG-5f9f41af2465", "reject",
     "Non-concept noise (generic-vocabulary): noun ('set elements', 'environment elements', "
     "'matrix elements'). Note: set uniqueness defined at ai-course '02 - Python and Data "
     "Tooling/02.2 - Python Programming Essentials/03. Data Structures - Lists, Tuples, and "
     "Sets.md:46'; matrix entries covered by the linear-algebra notes."),
    ("CG-498e0e3f3e00", "reject",
     "Non-concept noise (generic-vocabulary): verb ('Pandas introduces NaN', 'paper introduces "
     "X'). Note: NaN handling covered by the Pandas note ('02 - Python and Data Tooling/02.3 - "
     "Essential Python Libraries/02. Pandas - Data Manipulation and Series.md:52' — Missing Data "
     "callout); each paper's introduction story is covered by its dedicated paper note."),
    ("CG-b956d60d001a", "reject",
     "Non-concept noise (generic-vocabulary): participle ('causing Newton's method to stall', "
     "'causing overfitting'). Note: the underlying failure modes are covered by the Hessian "
     "treatments ('01 - Foundations and Overview/01.2 - Mathematical Foundations/08. Multivariate "
     "Calculus - Jacobians and Hessians.md:85-86') and multicollinearity at '03 - Machine "
     "Learning/03.1 - Regression/03. Linear Regression (DL Perspective).md:126'."),
    ("CG-778628b6e7eb", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('choosing the right architecture/"
     "hyperparameters'). Note: architecture selection is covered by the dedicated ai-course note "
     "'08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/04. Choosing "
     "the Right Architecture.md' and hyperparameter selection by '04 - Neural Networks and Deep "
     "Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network "
     "Configuration.md'."),
    ("CG-9c34bd03df15", "reject",
     "Non-concept noise (generic-vocabulary): participle ('allowing multi-layered networks to "
     "learn', 'allowing AI to generate images'). Note: the backpropagation history is covered "
     "in-situ at '05. Evolution and History of Deep Learning.md:34' and the GAN creation story "
     "at :56."),
    ("CG-b475a697bb9e", "reject",
     "Non-concept noise (generic-vocabulary): adjective (external/ third-party data folder; "
     "'external concentric rings' padding prose). Note: covered in-situ by ai-course '02 - "
     "Python and Data Tooling/02.1 - Python Environment Setup/06. Project Structure and Best "
     "Practices.md:15' and '05 - Convolutional Neural Networks (CNN)/02. Core Operators and "
     "Geometry/06. Padding - Mathematics, Edge Effects, and Valid vs Same.md:63'."),
    ("CG-f1112cbf80ba", "reject",
     "Non-concept noise (generic-vocabulary): superlative ('the simplest model'). Note: the "
     "linear-regression framing is covered in-situ by '03 - Machine Learning/03.1 - Regression/"
     "03. Linear Regression (DL Perspective).md:3' and gradient descent as backbone at '01. "
     "Gradient Descent Optimization (DL Course).md:3'."),
    ("CG-947950cc2211", "reject",
     "Non-concept noise (generic-vocabulary): past participle ('achieved convergence'). Note: "
     "convergence treated at '01 - Foundations and Overview/01.2 - Mathematical Foundations/06. "
     "Gradients and Gradient Descent.md:224'."),
    ("CG-116f269b9a5b", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('moving data forward/backward', 'moving "
     "to the right'). Note: feedforward/backpropagation definitions covered at '05. Derivatives, "
     "Power Rule, and the Chain Rule.md:53' and the descent-direction rule at '06. Gradients and "
     "Gradient Descent.md:140'."),
    ("CG-0cae87f063e9", "reject",
     "Non-concept noise (generic-vocabulary): noun ('ability to learn/generalize'). Note: the ML "
     "definition is covered at '01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/"
     "01. Introduction to Machine Learning.md:6'; the validation/test exam metaphor at '08. "
     "Foundations of Machine Learning (Summary).md:702'."),
    ("CG-377a78d1d7a4", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('keeping the first occurrence', 'keeping "
     "b constant'). Note: duplicate handling covered at '02 - Python and Data Tooling/02.4 - "
     "Data Cleaning and Preprocessing/02. Duplicate Detection and Record Linkage.md:29'; "
     "partial-derivative semantics at '01. Gradient Descent Optimization (DL Course).md:220'."),
    ("CG-92b0de9225d0", "reject",
     "Non-concept noise (generic-vocabulary): past participle ('algorithmically generated random "
     "numbers', 'Generated Image'). Note: initialization is covered by the dedicated "
     "weight-initialization notes (in-situ bridge at '05 - Convolutional Neural Networks (CNN)/"
     "01. Foundations and Philosophy/03. The Bridge - From Basic Convolution to Learned "
     "Weights.md:46'); style transfer is covered at '06. Chapter Summaries (Aggregated)/04. VGG "
     "and Classic Architectures - Summary.md:531-548'."),
    ("CG-1bdce86c74ce", "reject",
     "Non-concept noise (homonym): spans square matrix, square root, squared error, and literal "
     "uses. Note: every sense has its own treatment — square matrix at ai-course '01 - "
     "Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra "
     "Fundamentals.md:65' (eigenvector definition) and '06 - Image Processing/03. Spatial "
     "Filtering and Neighborhood Processing/3.1 The Mechanics of Spatial Filtering.md:6' (kernel "
     "as a small square matrix); square root has the dedicated note '08 - Attention and "
     "Transformers/08.1 - The Attention Mechanism/03. Scaled Dot-Product Attention - Why the "
     "Square Root.md:1' plus master-ai '02 - Mathematics/Optimization/14 - Learning Rate "
     "Schedules.md:89' ('### Inverse square root'); squared errors are covered by the MSE notes."),
    ("CG-13cd9f176e28", "reject",
     "Non-concept noise (generic-vocabulary): verb ('released in 1991', 'if released'). Note: "
     "Python history covered at '02 - Python and Data Tooling/02.1 - Python Environment Setup/"
     "01. Python Language Overview.md:5'; model-release tracking is vault-management meta "
     "(master-ai Research Queue)."),
    ("CG-fed5d70657b9", "reject",
     "Non-concept noise (generic-vocabulary): adjective (unique elements/keys/tokens). Note: "
     "set/dict uniqueness defined in-situ at ai-course '02 - Python and Data Tooling/02.2 - "
     "Python Programming Essentials/03. Data Structures - Lists, Tuples, and Sets.md:46' and "
     "'04. Dictionaries and Key Value Management.md:6'."),
    ("CG-1e87ddc81578", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('finding a mapping function'). Note: the "
     "supervised-learning definition is covered at '01 - Foundations and Overview/01.1 - AI, ML, "
     "and DL Hierarchy/08. Foundations of Machine Learning (Summary).md:23'; the accuracy-flaw "
     "discussion at :1012."),
    ("CG-771184ffed6b", "reject",
     "Non-concept noise (generic-vocabulary): preposition ('including outliers'). No concept in "
     "dependency position."),
    ("CG-f610aac2084f", "reject",
     "Non-concept noise (generic-vocabulary): noun ('the rest of the data/weights'). Note: "
     "partial-derivative isolation covered at '01 - Foundations and Overview/01.2 - Mathematical "
     "Foundations/04. Partial vs. Ordinary Derivatives.md:28'; SVM support-vector coverage at "
     "'03 - Machine Learning/03.4 - Support Vector Machines (SVM)/01. SVM - Course "
     "Overview.md:101'."),
    ("CG-11abddceee0b", "reject",
     "Non-concept noise (generic-vocabulary): adjective ('corresponding input value/rows'). "
     "Note: gradient-by-input weighting covered at '03 - Machine Learning/03.1 - Regression/03. "
     "Linear Regression (DL Perspective).md:42'; parameter roles at :15."),
    ("CG-1646020caa37", "reject",
     "Non-concept noise (generic-vocabulary): numeric-scale prose (100 million parameters, 1.4 "
     "million images, 1 million users). Note: ImageNet scale at '05. Evolution and History of "
     "Deep Learning.md:46'; parameter-count black-box discussion at '04. Machine Learning vs "
     "Deep Learning.md:75'; memory-efficiency comparison at '02 - Python and Data Tooling/02.2 - "
     "Python Programming Essentials/07. Iterators, Generators, and Memory Efficiency.md:35'."),
    ("CG-aafdc0a2fdb6", "reject",
     "Non-concept noise (generic-vocabulary): participle ('requiring pandas 2.0 features', "
     "'requiring the practitioner to guess'). Note: version-management guidance covered at "
     "'04. Virtual Environments and Package Management.md:9'; the PReLU learnable-slope "
     "advantage at '06. Activation Functions in Deep Learning.md:58'."),
    ("CG-4e51d8f3659b", "reject",
     "Non-concept noise (generic-vocabulary): verb/noun ('when the model claims a patient is "
     "sick' — precision prose; 'unresolved factual claims' — vault-management meta). Note: "
     "precision semantics covered at '01 - Foundations and Overview/01.1 - AI, ML, and DL "
     "Hierarchy/08. Foundations of Machine Learning (Summary).md:1016'; multi-head "
     "interpretability at '08 - Attention and Transformers/08.1 - The Attention Mechanism/04. "
     "Multi-Head Attention - Parallel Relationship Patterns.md:60'."),
    ("CG-372f3b0dd3bc", "reject",
     "Non-concept noise (generic-vocabulary): quantifier/adjective ('vast majority of tasks'; "
     "majority vote/label/class). Note: every technical sense is covered in-situ — KNN majority "
     "vote at '03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors "
     "(KNN) - Comprehensive.md:178,613' ('Step 2: Majority Vote'), self-consistency majority "
     "vote at master-ai '26 - Papers/Agents and RAG/38 - Self-Consistency 2022.md:46,69' "
     "('Majority vote' heading), majority-class imbalance at '03 - Machine Learning/03.6 - Model "
     "Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md:13'."),
    ("CG-d3e79a1fd34d", "reject",
     "Non-concept noise (generic-vocabulary): pronoun ('score 100% but learn nothing', 'changes "
     "nothing'). Note: the train/test-separation rationale covered at '08. Foundations of "
     "Machine Learning (Summary).md:148'; the constant-term derivative discussion at '05. "
     "Derivatives, Power Rule, and the Chain Rule.md:316'."),
    ("CG-6a89a91746f8", "reject",
     "Non-concept noise (generic-vocabulary): adverb ('strictly categorized', 'strictly "
     "unstructured'). Note: the learning-type taxonomy is covered at '08. Foundations of "
     "Machine Learning (Summary).md:61' and the ML-vs-DL comparison at '04. Machine Learning vs "
     "Deep Learning.md:61'."),
    ("CG-560b90fde79a", "reject",
     "Non-concept noise (generic-vocabulary): adjective ('after a certain amount of data', "
     "'certain epochs'). Note: the data-scaling plateau is covered at '04. Machine Learning vs "
     "Deep Learning.md:30'; AI-winters history at '05. Evolution and History of Deep "
     "Learning.md:3'."),
    ("CG-5f136eb5018c", "reject",
     "Non-concept noise (generic-vocabulary): adverb/comparative (earlier layers, stop training "
     "earlier, derived earlier). Note: early-stopping guidance covered at '08. Foundations of "
     "Machine Learning (Summary).md:190'; the depth-dependent gradient asymmetry at '04 - "
     "Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. "
     "Weight Initialization.md:112'."),
    ("CG-8c44c8672219", "reject",
     "Non-concept noise (generic-vocabulary): noun spanning unrelated mechanisms (biological "
     "neuron signals; gradient/learning signals; misc prose). Note: biological signaling is "
     "covered at ai-course '04 - Neural Networks and Deep Learning Foundations/04.1 - Neural "
     "Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md:18,360' (dendrites "
     "receive electrical signals); ResNet gradient-flow signals at :819,:965."),
    ("CG-13f85701534d", "reject",
     "Non-concept noise (code-identifier): the loop variable in 'for name, param in "
     "model.named_parameters()' (ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding "
     "Gradient Problems.md:646,833,986'). Note: the parameter concept itself has a definitional "
     "treatment at '04. Hyperparameters and Network Configuration.md:5' (parameters = weights "
     "and biases learned during training, as opposed to hyperparameters set before training)."),
    ("CG-2c7475af29cc", "reject",
     "Non-concept noise (generic-vocabulary): adjective (irrelevant outliers/docs/features). "
     "Note: outlier disposition covered at '02 - Python and Data Tooling/02.4 - Data Cleaning "
     "and Preprocessing/03. Outlier Detection and Treatment Methods.md:52'; the precision "
     "rationale at '02. Model Evaluation Metrics Beyond Accuracy.md:504'; the SVM "
     "support-vector misconception at '01. SVM - Course Overview.md:101'."),
    ("CG-f9b5dca77a67", "reject",
     "Non-concept noise (generic-vocabulary): comparative adjective ('broader field', 'broader "
     "boundaries'). Note: the DL-within-CS context is covered at '03. Deep Learning Definition "
     "and Context.md:7'; the RBF sigma trade-off at '06. The Kernel Trick.md:51'."),
    ("CG-83cc7d07dd0c", "reject",
     "Non-concept noise (generic-vocabulary): adjective (diverse data/variations). Note: the "
     "symmetry-breaking rationale at '01. Weight Initialization.md:50'; augmentation diversity "
     "at '07. Data Augmentation.md:25'."),
    ("CG-c257a64dac07", "reject",
     "Non-concept noise (generic-vocabulary): adverb ('reducing the error rate by nearly half'). "
     "Note: AlexNet history covered at '05. Evolution and History of Deep Learning.md:48'; the "
     "loss-landscape discussion at '01. Gradient Descent Optimization (DL Course).md:77'."),
    ("CG-3d2ac435a6d8", "reject",
     "Non-concept noise (generic-vocabulary): adverb ('fails silently', 'silently discard'). "
     "Note: the BN train/eval misconception is covered by the dedicated 'Training vs. Evaluation "
     "Mode (CRITICAL)' sections at ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md:116-143' "
     "and the Common-Mistakes note."),
    ("CG-50d7af692619", "reject",
     "Non-concept noise (generic-vocabulary): participle ('assuming a CSV file', 'assuming "
     "parameters constant'). Note: coordinate descent covered at '01 - Foundations and Overview/"
     "01.2 - Mathematical Foundations/01. Mathematical Notation (ML Course).md:99'; the "
     "data-loading idiom is in-situ code."),
    ("CG-db0dbf874ded", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('passing data through layers', 'students "
     "passing'). Note: the systematic chain-rule application is covered at '05. Derivatives, "
     "Power Rule, and the Chain Rule.md:372'; the grade-filtering example is in-situ exercise "
     "code."),
    ("CG-8cbe42417604", "reject",
     "Non-concept noise (generic-vocabulary): comparative (shorter patience, shorter "
     "multiplication chain). Note: ReduceLROnPlateau patience guidance at '08. Loss Functions "
     "and Optimizers Deep Dive.md:492'; the depth-dependent gradient magnitude at '01. Weight "
     "Initialization.md:112'."),
    ("CG-08bf7f28b267", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('storing and inverting it is infeasible', "
     "'storing terabytes'). Note: Hessian infeasibility covered at '08. Multivariate Calculus - "
     "Jacobians and Hessians.md:85'; big-data volume traits at '01 - Foundations and Overview/"
     "01.3 - Data Science Foundations/07. Exercise 1 - Identifying Applications and "
     "Roles.md:17'; KV-cache storage is covered by the dedicated master-ai '08 - LLMs/Context "
     "and KV Cache' folder."),
    ("CG-e24cf778084b", "reject",
     "Non-concept noise (generic-vocabulary): past participle (compressed axis/patch/"
     "representation). Note: the compressed-representation concept is defined at ai-course "
     "'08 - Attention and Transformers/08.4 - Encoder Decoder and the Design Space/02. The "
     "Information Bottleneck and Latent Space.md:22' ('The latent space is a compressed "
     "representation'); ROC-axis compression and pooling compression are covered in-situ by "
     "their own notes."),
    ("CG-e685216f64f6", "reject",
     "Non-concept noise (generic-vocabulary): numeric prose ('hundreds or a few thousand "
     "examples', 'hundreds of weights'). Note: the small-data regime is covered at '04. Machine "
     "Learning vs Deep Learning.md:46'; the multi-parameter error at '04. Partial vs. Ordinary "
     "Derivatives.md:19'."),
    ("CG-4844233cd987", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('predicting continuous values', "
     "'Predicting Numbers'). Note: the regression definition is covered at '02. Types of "
     "Learning.md:29' and the taxonomy diagram at '08. Foundations of Machine Learning "
     "(Summary).md:69'."),
    ("CG-362cfba571fb", "reject",
     "Non-concept noise (generic-vocabulary): adverb ('strongly motivated to avoid', 'strongly "
     "punishes'). Note: MSE error-scaling covered at '02. Loss Functions and Cost "
     "Optimization.md:15'; the cross-entropy confidence penalty at :75."),
    ("CG-3cc03090c05a", "reject",
     "Non-concept noise (generic-vocabulary): noun ('two-part team' metaphor; engineering-team "
     "prose). Note: the backprop-computes/GD-updates division is covered at '05. Derivatives, "
     "Power Rule, and the Chain Rule.md:38' and '06. Gradients and Gradient Descent.md:157'."),
    ("CG-11ac946e7f56", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('creating a dataset', 'creating a "
     "mask'). Note: the dataset-creation role is covered at '01. Introduction to Machine "
     "Learning.md:40'; the segmentation definition at '06. Applications of Deep "
     "Learning.md:30'."),
    ("CG-3302f4756ed6", "reject",
     "Non-concept noise (generic-vocabulary): gerund ('trying to fit a complex curve', 'what "
     "are we trying to solve'). Note: underfitting symptoms covered at '08. Foundations of "
     "Machine Learning (Summary).md:183'; problem-framing at '04. The Complete Data Science "
     "Workflow.md:24'."),
    ("CG-89c6344893c9", "reject",
     "Non-concept noise (generic-vocabulary): proximity adjective (spatially adjacent elements/"
     "pixels). Note: the spatial-correlation rationale is covered in-situ at ai-course '04 - "
     "Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. "
     "Dropout and Regularization.md:315,347' (Dropout2d drops entire channels because "
     "spatially adjacent elements are highly correlated)."),
    ("CG-d24e33837501", "reject",
     "Non-concept noise (generic-vocabulary): past participle ('weights are cached', cached "
     "KV). Note: both technical senses have dedicated treatments — pre-trained weight caching "
     "at ai-course '05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, "
     "and PyTorch/03. PyTorch Advanced - VGG16 and Pre-trained Models.md:49' ('Where Are the "
     "Weights Cached?' callout) plus the quiz '09 - Quizzes and Question Banks/02. Deep "
     "Learning - Chapter 2 (CNN)/Q23 - PyTorch Advanced - VGG16 and Pre-trained Models.md:61'; "
     "the KV cache has the dedicated master-ai note '08 - LLMs/Context and KV Cache/02 - KV "
     "Cache Mechanics.md:9' plus '06 - Attention Mechanisms/Modern Attention/14 - GQA MQA "
     "MLA.md:14' ('The Problem: KV Cache Size') and '15 - Sliding Window Attention.md:31' "
     "('The Trick: KV Cache Stays Small')."),
    ("CG-81543b5ffd38", "reject",
     "Non-concept noise (generic-vocabulary): gerund (removing duplicates/special chars/the "
     "mean). Note: each specific operation is covered in-situ — data cleaning at '04. The "
     "Complete Data Science Workflow.md:34', deduplication at '03. Data Structures - Lists, "
     "Tuples, and Sets.md:50', text normalization at '05. Categorical Encoding and Text "
     "Normalization.md:16', PCA mean-centering at '03 - Machine Learning/03.8 - Dimensionality "
     "Reduction/01. Principal Component Analysis (PCA).md:67'."),
    ("CG-3ae4c0f86ee6", "reject",
     "Non-concept noise (generic-vocabulary): noun/prose ('Likes StatQuest' subject; standalone "
     "subject; subject to change). Note: the partial-derivative analogy is in-situ at '05. "
     "Derivatives, Power Rule, and the Chain Rule.md:62'; the DS-definition Venn context at "
     "'01. Data Science Definition and Philosophy.md:15'."),
    ("CG-a9037b238318", "reject",
     "Non-concept noise (generic-vocabulary): adverb ('increasingly common'). Note: GAN history "
     "covered at '05. Evolution and History of Deep Learning.md:56'; gradient-highway "
     "innovations at '04. Backpropagation and Gradient Flow in CNNs.md:581'."),
    ("CG-a48024368ab2", "reject",
     "Non-concept noise (numeric prose): multiplier ('10x to 100x faster', 'off by 10x', '10x "
     "higher LR'). Note: every site is covered in-situ — NumPy C speed at ai-course '02 - "
     "Python and Data Tooling/02.3 - Essential Python Libraries/01. NumPy - Numerical "
     "Computation and Arrays.md:13', the MSE scale rationale at '03 - Machine Learning/03.6 - "
     "Model Evaluation/03. Regression Metrics - MAE, MSE, RMSE, R2, MAPE.md:39', "
     "discriminative LRs at '05 - Convolutional Neural Networks (CNN)/03. Architecture and "
     "Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md:573', the "
     "KV-cache speedup at master-ai '27 - Projects/Implementations/01 - Build Attention and "
     "Transformer From Scratch.md:319'."),
]

records = []
for i, (cid, action, rationale) in enumerate(decisions, 1):
    records.append({
        "candidate_id": cid,
        "decision_id": f"D-DISC002-B6-{i:04d}",
        "action": action,
        "rationale": rationale,
        "reviewer": R,
    })

assert len(records) == 60, f"expected 60 decisions, got {len(records)}"
ids = [r["candidate_id"] for r in records]
assert len(set(ids)) == 60, "duplicate candidate_ids"
OUT.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
from collections import Counter
print("wrote", OUT, "records:", len(records), "actions:", dict(Counter(r["action"] for r in records)))
