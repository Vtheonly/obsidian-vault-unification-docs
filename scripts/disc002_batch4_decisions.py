#!/usr/bin/env python3
"""DISC-002 session 4 (batch 4): emit the 60 review decisions as JSONL.

Method (same as batch 3): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch3 state,
session-4 fresh-clone replay), a 51-term definitional-treatment coverage
probe (scripts/disc002_batch4_probe.py, results in
/home/z/my-project/scratch/disc002-batch4-probe.json), targeted corpus
verification for boundary cases (triangle inequality, batch size, weight
sharing, loss-spikes/stability, perceptron history), and an independent
subagent cross-check of the judgment calls.

Result: 36 cover (evidence-cited) + 24 reject. No new confirmed gaps.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/concept-candidates/002-disc002-decisions-batch4.jsonl")

R = "GLM-5.3 orchestrator, DISC-002 session 4 (batch 4, subagent cross-checked)"

decisions = [
    # ---- covers (36) ----
    ("CG-9fa92af1d71c", "cover",
     "fragment of Batch Normalization mechanics; dedicated treatments in both vaults: ai-course '04.3 - Training Dynamics and Stability/05. Batch Normalization.md' (Overview 'normalizing the activations at each layer' ~line 21 + code comment ':367 BatchNorm: normalizes activations per channel') and master-ai '07 - Transformers/Components/04 - Normalization Layers.md' ('### BatchNorm (Ioffe & Szegedy, 2015)' + per-channel/per-batch normalization mechanics)."),
    ("CG-b63f691c37b7", "cover",
     "single perceptron is defined where used: master-ai '04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md:16' ('A single perceptron computes: y = sigma(sum w_i x_i + b)') under '## The Perceptron'; ai-course '09 - Quizzes/Q9 - The Perceptron and the Chain Rule.md:83' reinforces the single-perceptron XOR limitation."),
    ("CG-1d04a03302c4", "cover",
     "fragment of 'receptive field grows'; receptive-field concept has dedicated treatments: ai-course '02. The Mathematics of Receptive Fields and 1x1 Convolutions.md' ('## Receptive Field: Definition and Intuitive Explanation') and 'Receptive field grows linearly with depth' at :208; master-ai '26 - Papers/Efficient Attention/18 - Longformer 2020.md' ('### Receptive Field Grows Slowly')."),
    ("CG-c68459879ddf", "cover",
     "fragment lexically naming covered 'receptive field' growth mechanics; same treatments as its sibling: ai-course '02. The Mathematics of Receptive Fields and 1x1 Convolutions.md' (definition heading + :208 growth law) and master-ai '18 - Longformer 2020.md' growth heading."),
    ("CG-10a6e5498ba2", "cover",
     "triangle inequality has explicit mathematical treatments: master-ai '02 - Mathematics/Linear Algebra/02 - Dot Product.md:96' (norm form '||x+y|| <= ||x|| + ||y||', derived from Cauchy-Schwarz) and '03 - Cosine Similarity.md:152,307' (metric-axiom form with worked cosine counterexample and angular-distance alternative); KL notes only use it in property lists."),
    ("CG-325f57a7fdb5", "cover",
     "universal approximation is covered: master-ai '01 - Perceptrons and MLPs.md' '### Universal Approximation Theorem'; ai-course '03. Artificial Neural Networks (ANN) - Comprehensive.md:416' area (linear-layers-cannot-learn-complex-shapes + activation stacking argument)."),
    ("CG-d030ad0ba955", "cover",
     "fragment of the Adam bias-correction mechanism; covered by ai-course '08. Loss Functions and Optimizers Deep Dive.md:296' ('Because m_t and v_t are initialized at zero, they are biased toward zero' + bias-correction treatment) and master-ai '02 - Mathematics/Optimization/13 - Adam Derivation.md' (full bias-correction derivation with hat-m/hat-v)."),
    ("CG-e16f8c5797a3", "cover",
     "fragment of depthwise separable convolution; depthwise step is defined at ai-course '05. Evolution of CNN Architectures.md:262' ('1. Depthwise convolution: Apply a separate D_K x ...') and the dedicated operator note '01. Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped.md'."),
    ("CG-6443a3875623", "cover",
     "verb form of the named failure-mode family 'training instability'; dedicated treatment master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' ('## Why Loss Spikes Happen': bad data batches, numerical instability, optimizer state, LR issues, genuine model instability + detection sections) — same precedent as batch-3 'training diverges'."),
    ("CG-368415ac8545", "cover",
     "fragment of 'full bidirectional context'; covered by master-ai '26 - Papers/Transformers/03 - BERT 2018.md' ('### Bidirectional Context') and master-ai '06 - Contextual Embeddings ELMo to BERT.md:285'."),
    ("CG-232f0d97ad8e", "cover",
     "RNN cell computation has dedicated treatment: master-ai '04 - Neural Networks/Architectures/04 - RNN LSTM GRU.md' ('### 4. The actual computation inside the RNN cell'); ai-course '03. Backpropagation Through Time (BPTT).md:18' works the vanilla cell equations."),
    ("CG-a463d5220223", "cover",
     "comparative fragment of the batch-size trade-off; dedicated section ai-course '04. Hyperparameters and Network Configuration.md:166' ('### 2.2 Batch Size: Small vs. Large Trade-offs', small-batch subsection :176 defining small-batch generalization behavior cited by Keskar et al. 2016 context); master-ai '05 - Loss Spikes and Stability.md' lists 'reduce batch' as the instability remedy."),
    ("CG-26288d969a6b", "cover",
     "weight vector is defined at point of use: master-ai '01 - Perceptrons and MLPs.md:24' ('w in R^n is the weight vector') and ai-course '01. Foundations and Philosophy - Summary.md:39' ('w = [w_1,...,w_n]^T in R^n is the weight vector')."),
    ("CG-92ed4b39ae99", "cover",
     "additive noise model is treated: ai-course '06 - Image Processing/04. Frequency Domain and Restoration/4.4 Image Degradation and Noise Models.md:111' (Wiener filter for blur + additive noise) and '07. Quiz/Q1.md:49' (additive-noise formula IB(i,j)=IP(i,j)+B(i,j) with answer); multiplicative contrast at :55."),
    ("CG-5a63a91c7875", "cover",
     "fragment of the ReLU non-saturation property; covered at ai-course '03. Activation and Pooling Layers.md:78' ('ReLU has a constant gradient of 1 for all positive inputs') and '02. Core Operators and Geometry - Summary.md:1188'."),
    ("CG-0cf5ace680c9", "cover",
     "depthwise separable convolution has dedicated corpus treatments: ai-course '04. VGG and Classic Architectures - Summary.md' ('##### Depthwise Separable Convolution Cost'), '05. Evolution of CNN Architectures.md:262' (two-step decomposition with FLOP comparison), master-ai '04 - Neural Networks/Architectures/03 - CNNs.md:286' (Q&A definition)."),
    ("CG-f42eff690e03", "cover",
     "filter-application mechanics covered: ai-course '02. Core Operators and Geometry - Summary.md:28' ('one 3D filter applied to a multi-channel input produces exactly one 2D output feature map') plus '01. The Convolution Operation Deep Dive.md' sliding-window treatment."),
    ("CG-7e86c8fd5372", "cover",
     "fragment lexically naming covered 'bidirectional context': master-ai '26 - Papers/Transformers/03 - BERT 2018.md' ('### Bidirectional Context') and '06 - Contextual Embeddings ELMo to BERT.md:285' (masked-LM predicting from full bidirectional context vs standard LM)."),
    ("CG-6f9c3a8168e8", "cover",
     "inverse FFT step is taught: ai-course '4.3 Frequency Domain Filtering.md:19' (pipeline step 6 'Inverse FFT: g = IFFT(G)' with the full filtering workflow) and '06. Concepts (ML Perspective)/05. The Fourier Transform in Imaging.md' ('# 4. Compute the inverse FFT')."),
    ("CG-ff08e685a1a4", "cover",
     "per-parameter learning rates covered: ai-course '08. Loss Functions and Optimizers Deep Dive.md' ('#### Why Adam Is Powerful: Adaptive Per-Parameter Learning Rates') and master-ai '13 - Adam Derivation.md' (per-coordinate scaling derivation); Hessian-diagonal connection at ai-course '08. Multivariate Calculus - Jacobians and Hessians.md:96'."),
    ("CG-21d790434a7b", "cover",
     "fragment of depthwise separable convolution (same family as CG-0cf5ace680c9); same treatments: ai-course '05. Evolution of CNN Architectures.md:262', '##### Depthwise Separable Convolution Cost' summary section, master-ai '03 - CNNs.md:286'."),
    ("CG-664e5b20045b", "cover",
     "adaptive per-parameter rates covered: ai-course '#### Why Adam Is Powerful: Adaptive Per-Parameter Learning Rates' heading; master-ai '12 - Optimization Essentials.md:446' and '13 - Adam Derivation.md:118' (AdamW nuance: weight decay multiplied by eta uniformly, not the adaptive per-parameter rate)."),
    ("CG-4e03c0382c23", "cover",
     "approximate posterior is defined at point of use: ai-course '10.2 - Variational Autoencoders/01. From Autoencoder to VAE - Learning a Distribution.md:71' ('The encoder q_phi(z|x) is an approximate posterior — an approximation to the true posterior p(z|x)') and '03. The KL Divergence Loss.md:69' (ELBO KL term between approximate posterior and prior)."),
    ("CG-29bf94098107", "cover",
     "corrupted input is a defined technique element in two domains: ai-course '02. Denoising Autoencoders and Sparse Autoencoders.md:33' (loss compares to original x, not corrupted x-tilde) and master-ai '14 - Interpretability/Mechanistic/04 - Activation Patching and Causal Tracing.md:64' (clean vs corrupted input setup)."),
    ("CG-a4ab9bef58a9", "cover",
     "element-wise product has dedicated treatments: ai-course '02. Core Operators and Geometry - Summary.md' ('# Element-wise product and sum' convolution step) and master-ai '02 - Dot Product.md:300' (dot-vs-element-wise/Hadamard distinction)."),
    ("CG-284d953bdc99", "cover",
     "identity shortcut covered by residual-connection treatments: ai-course '08. The Degradation Problem and Residual Connections.md:94' (mermaid 'Identity Shortcut' skip path) and '09. ResNet Bottleneck Blocks.md' (code comment 'If None, the identity shortcut is used'); master-ai '07 - Transformers/Architecture/03 - Residual Connections.md'."),
    ("CG-3888b262f852", "cover",
     "image preprocessing covered: ai-course '05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md' ('torchvision.transforms: image preprocessing and augmentation pipelines') and master-ai '27 - Projects/Capstones/10 - Build a Vision-Language Model.md' ('### Image Preprocessing Mismatch')."),
    ("CG-20ffb9b34594", "cover",
     "image tensor is the tensor-shape/format convention material (batch-3 'input shape' precedent): master-ai '02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md:29' ('## Shape Conventions in Deep Learning'), ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md:106' ('### How Tensor Shapes Flow Through Layers'), in-situ '04. The Fully Connected Layer and Flattening.md:54' ([Batch, 3, 224, 224])."),
    ("CG-42a583a034f3", "cover",
     "layer activations covered by ANN/MLP treatments: ai-course '07. Multi-Layer Perceptron and Backpropagation.md:76' (Hidden Layer Activations notation a^(h)) and '03. Artificial Neural Networks (ANN) - Comprehensive.md:519' ('Step 2: Hidden Layer Activations')."),
    ("CG-b5b975d09484", "cover",
     "multiple heads covered: master-ai '06 - Attention Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md' ('## Why Multiple Heads?'); Medusa/EAGLE multiple-decoding-heads variant at master-ai '26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md'."),
    ("CG-4ecce4efc274", "cover",
     "running sum covered by online-softmax treatments: master-ai '06 - Attention Mechanisms/Efficient Attention/11 - FlashAttention.md:170' (running max m_i, running sum l_i; '# Rescale running sum' rescaling comments) ; dataset-mean running accumulation at ai-course '04.3 - Training Dynamics and Stability/07. Data Augmentation.md:506'."),
    ("CG-eb617453c416", "cover",
     "standard convolutions covered: master-ai '24 - Research Frontiers/Hybrid Architectures/04 - Hyena and Long Convolutions.md:21' (O(N*k) complexity discussion) plus the convolution-operation treatments both vaults ('01. The Convolution Operation Deep Dive.md'; the MobileNet standard-vs-separable comparison at '05. Evolution of CNN Architectures.md:258')."),
    ("CG-3c84f3b830a9", "cover",
     "symmetric activations covered by initialization treatments: ai-course '04.3 - Training Dynamics and Stability/01. Weight Initialization.md:784' ('Xavier/Glorot initialization preserves activation and gradient variance for symmetric activations like sigmoid and tanh'; Kaiming counterpart for asymmetric ReLU)."),
    ("CG-cdfb019681a5", "cover",
     "fragment lexically naming covered 'gradient accumulation': master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md' ('### Gradient accumulation'), '27 - Projects/Capstones/11 - Build a Distributed Training Pipeline.md' ('## Step 6: Gradient Accumulation'), ai-course '02. Common Mistakes and How to Fix Them.md:22' (design-choice rationale)."),
    ("CG-0b9079e7b9d0", "cover",
     "variational autoencoders have a dedicated corpus treatment: ai-course '10 - Generative Models/10.2 - Variational Autoencoders/' (full folder: autoencoder-to-VAE, KL divergence loss, etc.) and master-ai '02 - Mathematics/Probability/09 - Gaussian Distribution.md' ('### Variational Autoencoders (VAEs)')."),
    ("CG-9457a78122e8", "cover",
     "fragment of the one-parameter-per-filter / weight-sharing mechanics; in-situ treatment ai-course '05. Processing 3D Volumes, Depth Summation, and Biases.md:57' callout ('exactly one bias parameter per filter — not one per channel, not one per spatial position, not one per output pixel') and dedicated '### Weight Sharing' at '02. Core Operators and Geometry - Summary.md:509' (precedent: batch-2 spatial-positions/weight-sharing cover)."),
    # ---- rejects (24) ----
    ("CG-1c7ba1752297", "reject",
     "Non-concept noise (prose-fragment): counting phrase 'from one image and pastes it onto [another]'. Note: CutMix/Cutout augmentation mechanics are covered by ai-course '07. Data Augmentation.md:249'."),
    ("CG-42cf3add47b4", "reject",
     "Non-concept noise (generic-vocabulary): 'model architectures' is a generic compound (torchvision import comment, coverage-audit phrasing), not a distinct concept. Note: specific architectures each have dedicated corpus treatments."),
    ("CG-f7aff6e98e62", "reject",
     "Non-concept noise (prose-fragment): 'one sequence' counting prose in the self-attention generalization narrative. Note: self-attention is covered by dedicated notes in both vaults."),
    ("CG-a33aa2de23e5", "reject",
     "Non-concept noise (code-identifier): Python stdlib module used in import statements. Note: file I/O idioms appear incidentally in pipeline code examples; not a corpus concept in dependency position."),
    ("CG-fbeddeff6c6a", "reject",
     "Non-concept noise (citation-fragment): partial author citation 'Szegedy et'. Note: Inception material is covered by ai-course '07. Inception Architecture Deep Dive.md' and the receptive-fields/1x1 note."),
    ("CG-6c4867903a51", "reject",
     "Non-concept noise (citation-fragment): author citation 'Szegedy et al'. Note: BatchNorm attribution covered at master-ai '04 - Normalization Layers.md' ('### BatchNorm (Ioffe & Szegedy, 2015)'); Inception covered as above."),
    ("CG-f006e05c1500", "reject",
     "Non-concept noise (prose-fragment): 'new dimension' generic phrase. Note: ResNeXt cardinality ('the number of parallel paths') is covered by ai-course '01. Advanced Convolutional Operators' and '05. Evolution of CNN Architectures.md'."),
    ("CG-fdc560687b1d", "reject",
     "Non-concept noise (prose-fragment): 'add complexity' is incremental-modeling advice. Note: the start-simple-then-add-capacity guidance is covered in-situ at ai-course '08. Data Preparation and MLP Implementation.md:24'."),
    ("CG-605ee1f00916", "reject",
     "Non-concept noise (prose-fragment): 'desired output' is generic end-to-end-learning phrasing. Note: end-to-end feature learning is covered by ai-course '01. Introduction and Foundations of CNNs.md:207' and '02. Core Architecture and Philosophy.md'."),
    ("CG-676b43c7c1f2", "reject",
     "Non-concept noise (prose-fragment): 'actual computation' is discourse phrasing. Note: RNN-cell computation is covered by master-ai '04 - RNN LSTM GRU.md' ('### 4. The actual computation inside the RNN cell')."),
    ("CG-afcf4d8a4255", "reject",
     "Non-concept noise (citation-fragment): author surname citation. Note: BatchNorm is covered by dedicated treatments in both vaults; attribution recorded at master-ai '04 - Normalization Layers.md'."),
    ("CG-c7d16986fe21", "reject",
     "Non-concept noise (citation-fragment): historical-person surname. Note: the Minsky/Papert perceptron-critique story is told in-situ at ai-course '01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/05. Evolution and History of Deep Learning.md:28' (1969 XOR proof, first AI Winter) and corroborated in master-ai '01 - Perceptrons and MLPs.md'."),
    ("CG-27d36af84a72", "reject",
     "Non-concept noise (prose-fragment): counting phrase 'one attention distribution/operation'. Note: multi-head attention is covered by master-ai '05 - Multi-Head Attention.md'."),
    ("CG-7b189cb01096", "reject",
     "Non-concept noise (generic-vocabulary): 'average value' is generic statistical phrasing; each use-site concept has its own dedicated treatment (GAP in pooling notes, KNN regression mean at '01. KNN - Comprehensive.md:680', Bellman value at master-ai '07 - MDPs and Bellman Equations.md:87')."),
    ("CG-8301600ff693", "reject",
     "Non-concept noise (prose-fragment): 'every token attends to every other token' describes full attention; synonymy-only parent (batch-3 token-attends precedent). Note: self-attention mechanics are covered by dedicated notes in both vaults."),
    ("CG-88ada76c3207", "reject",
     "Non-concept noise (generic-vocabulary): positional phrase; the probe hit is a code comment ('Check ratio of first to last layer gradient'), not a concept treatment. Note: gradient-norm diagnostics are covered in-situ by the vanishing-gradient note."),
    ("CG-a5310d1e7f33", "reject",
     "Non-concept noise (prose-fragment): 'layers receive' is subject-verb prose about gradient flow. Note: vanishing/exploding propagation is covered by ai-course '03. The Vanishing and Exploding Gradient Problems.md'."),
    ("CG-7c132c9a860b", "reject",
     "Non-concept noise (code-identifier): matplotlib styling parameter. Note: plotting workflow covered by ai-course '04. Matplotlib - Static Data Visualization.md'."),
    ("CG-ccc549eebf95", "reject",
     "Non-concept noise (code-identifier): matplotlib API method. Note: same dedicated Matplotlib note covers the save/export workflow."),
    ("CG-c15bd69f83e3", "reject",
     "Non-concept noise (prose-fragment): discourse phrase 'sometimes called'. Note: the neuron/perceptron/unit aliasing is stated in-situ at ai-course '01. Introduction and Foundations of CNNs.md:9'."),
    ("CG-87ad956a3431", "reject",
     "Non-concept noise (numeric-fragment): epsilon constant literal. Note: its role as Adam epsilon / numerical guard is covered by the optimizer notes (ai-course '08. Loss Functions and Optimizers Deep Dive.md:496')."),
    ("CG-d795271b79c8", "reject",
     "Non-concept noise (numeric-fragment): example-specific channel count ('produces 32 output channels'). Note: Inception branch mechanics covered by ai-course '07. Inception Architecture Deep Dive.md:176'."),
    ("CG-8b461ac09f82", "reject",
     "Non-concept noise (prose-fragment): 'across classes' averaging prose. Note: macro/micro/weighted averaging is covered by ai-course '02. Model Evaluation Metrics Beyond Accuracy.md:245' comparison table."),
    ("CG-7f31b3dfb7a1", "reject",
     "Non-concept noise (prose-fragment): 'attention gives [capability]' discourse. Note: attention benefits are covered by the self-attention/Transformer treatments in both vaults."),
]

records = []
for i, (cid, action, rationale) in enumerate(decisions, 1):
    records.append({
        "candidate_id": cid,
        "decision_id": f"D-DISC002-B4-{i:04d}",
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
