#!/usr/bin/env python3
"""DISC-002 session 3: emit the batch-3 decision file (60 candidates).

Standard (per merge lesson + batch1/batch2 precedents):
- cover: the concept the term denotes has a source treatment; rationale carries
  file:line citations. Fragments of covered concepts get cover when the
  fragment lexically names the covered parent concept (gradient-accumulation
  precedent; subagent-verified scaling-laws / training-diverges cases).
- reject: non-concept noise (prose-fragment without conceptual denotation,
  generic vocabulary, code fragment, citation fragment, example-specific
  noun). KUs remain dispositioned independently at synthesis.
- The token-attends reject records the boundary rule explicitly: fragments
  whose parent is only recoverable by synonymy (not lexically) are noise.

Review provenance: orchestrator individual evidence review + coverage probes
(scripts/disc002_batch3_probe.py) + independent subagent cross-check of the
16 judgment calls (3 disagreements, all resolved by orchestrator re-verification
of the cited treatments).
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/home/z/my-project/obsidian-vault-unification-docs/state/concept-candidates/"
           "002-disc002-decisions-batch3.jsonl")

R = "GLM-5.3 orchestrator, DISC-002 session 3 (batch 3, subagent cross-checked)"

# (candidate_id, action, rationale)
DECISIONS = [
    # ---- covers: fragments of covered concepts ----
    ("CG-4abab356557f", "cover",
     "fragment of 'first fully connected layer'; the fully-connected-layer concept has "
     "dedicated treatment (ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations "
     "and Philosophy/02. Core Architecture and Philosophy.md:184' weight-matrix treatment; "
     "'02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md:133' "
     "flatten-before-FC mechanics; dedicated note '04. The Fully Connected Layer and "
     "Flattening.md')."),
    ("CG-4ee4ac4753bc", "cover",
     "fragment of 'first fully connected layer' (same family as CG-4abab356557f); covered "
     "by the FC-layer treatments incl. dedicated note '04. The Fully Connected Layer and "
     "Flattening.md' and PyTorch implementation notes (self.fc1 = nn.Linear, "
     "ai-course '02. PyTorch Implementation Basics.md:295')."),
    ("CG-cc93453f4f84", "cover",
     "verb-phrase fragment whose head names the covered 'scaling laws' concept; dedicated "
     "sections at master-ai '11 - Training/Pretraining/01 - Pretraining Objectives and "
     "Scaling Laws.md:114' (definition sentence begins 'Scaling laws predict how model "
     "loss ... scales with parameters, data, and compute') and dedicated paper note "
     "'26 - Papers/2024-2026/42 - Scaling Laws (Kaplan and Chinchilla).md'."),
    ("CG-059f536e7663", "cover",
     "fragment is the verb form of the named failure mode 'training divergence'; dedicated "
     "treatment master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' "
     "(aliases: Loss Divergence, NaN Loss; cause/detection/recovery sections; :12, :163, "
     ":268) plus symptom tables in '13 - Adam Derivation.md:296' and "
     "'14 - Learning Rate Schedules.md:18'."),
    # ---- covers: tensor/shape family ----
    ("CG-f057ac271f60", "cover",
     "unsqueeze as a shape-manipulation op is treated in master-ai '02 - Mathematics/"
     "Linear Algebra/06 - Tensors and Broadcasting.md:81' ('The fix is usually to "
     "unsqueeze or reshape to add a size-1 dimension in the right place'), :199 "
     "(stride/contiguity table), :215 (right-alignment worked example), and the GQA "
     "repeat_kv pattern at :392; ai-course CNN interpretability notes (:117-119 area) "
     "show unsqueeze(0) adding the batch dimension."),
    ("CG-b2b72c0811a2", "cover",
     "shape-convention material has dedicated treatments in both vaults: master-ai "
     "'02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md:29' "
     "('## Shape Conventions in Deep Learning': dense/image/sequence/attention/KV-cache "
     "conventions, PyTorch vs TensorFlow, mismatch warning) and ai-course '05 - "
     "Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying "
     "Tensors - Volumes, Depth, and Data Formats.md:106' ('### How Tensor Shapes Flow "
     "Through Layers' with worked trace). Input-shape usages (VGG16 tables, exercise "
     "checks) are downstream of these treatments. NOTE for synthesis planner: consolidate "
     "with the deferred tensor-shape family evidence ('3d tensor', 'tensor shape', "
     "'shape mismatch', flattening/resizing) when assembling the destination section."),
    ("CG-e5454cab50b0", "cover",
     "feature dimension is treated where it matters: LayerNorm mechanics (ai-course "
     "'08 - Attention and Transformers/08.2 - The Transformer Architecture/03. The "
     "Transformer Encoder Block.md:86' 'normalizes across the feature dimension'), "
     "BatchNorm matching (ai-course '05. Batch Normalization.md' num_features), and "
     "linear attention cost note (master-ai '13 - Linear Attention.md:41')."),
    # ---- covers: attention family ----
    ("CG-3104877d98ae", "cover",
     "attention scores (QK^T before softmax) are covered by the self-attention treatment "
     "(master-ai '06 - Attention Mechanisms/Self-Attention/04 - Self-Attention.md') and "
     "explicitly related to dot products at master-ai '02 - Mathematics/Linear Algebra/"
     "02 - Dot Product.md:325' ('attention scores are dot products (Q · K)')."),
    ("CG-6b88a096d68c", "cover",
     "attention patterns covered by dedicated sections: master-ai '26 - Papers/Efficient "
     "Attention/20 - BigBird 2020.md' ('## The Three Attention Patterns'), Longformer "
     "(18) and Swin (23) pattern treatments, plus interpretability context (master-ai "
     "'14 - Interpretability/Mechanistic/01 - Mechanistic Interpretability.md')."),
    ("CG-99325a8ac340", "cover",
     "attention cost scaling covered at master-ai '06 - Attention Mechanisms/"
     "Self-Attention/04 - Self-Attention.md:208' ('The O(n^2) scaling is the fundamental "
     "limitation of standard attention. Doubling the context length quadruples the "
     "attention cost') and ai-course ViT design decisions note (:76)."),
    ("CG-1ea18586e1a1", "cover",
     "attention head concept covered by the multi-head attention treatment (master-ai "
     "'06 - Attention Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md:16' "
     "'A single attention head computes one weighted average of value vectors'), "
     "head-specialization section in mechanistic interpretability note, and induction-"
     "head Q&A in self-attention note (:457)."),
    ("CG-161cd2fbb3e8", "cover",
     "bidirectional context covered by dedicated BERT section: master-ai '26 - Papers/"
     "Transformers/03 - BERT 2018.md' ('### Bidirectional Context'), with encoder "
     "contrast treatments in ai-course 08.4 (autoregressive vs parallel encoding)."),
    ("CG-01d4fa949eb2", "cover",
     "retrieval-augmented generation covered by the dedicated master-ai '17 - RAG' "
     "section ('01 - RAG Pipeline Overview.md:12') and paper note '26 - Papers/Agents "
     "and RAG/35 - RAG 2020.md:174'; hallucination-note RAG section also treats it."),
    # ---- covers: ML/stat concepts ----
    ("CG-5ab01bf5d927", "cover",
     "training error is covered by the bias-variance/overfitting treatments: master-ai "
     "'03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md:31' "
     "(fit-quality table: 'Training error low; test error close to training') and "
     "ai-course '08. The Degradation Problem and Residual Connections.md:43'."),
    ("CG-8c4f3aa35924", "cover",
     "human feedback as RLHF core is covered by the alignment-paper set: master-ai "
     "'26 - Papers/Alignment/07 - InstructGPT 2022.md:15,120' (RLHF definition and "
     "Claude RLAIF contrast), '50 - Process Reward Models 2023.md:20', plus reward-model "
     "material; glossary entry exists (RLHF)."),
    ("CG-d50491e66d01", "cover",
     "deep neural networks covered definitionaly at master-ai '01 - AI Foundations/02 - "
     "AI vs ML vs DL vs GenAI vs Agentic AI.md:12' ('DL is ML with deep neural networks') "
     "and by the vanishing/exploding gradient treatments (ai-course '03. The Vanishing "
     "and Exploding Gradient Problems.md:13')."),
    ("CG-7e35c086422f", "cover",
     "linear separability covered: master-ai '04 - Neural Networks/Foundations/01 - "
     "Perceptrons and MLPs.md:107' (XOR not linearly separable, single hyperplane), "
     "logistic-regression pitfall (master-ai '02 - Linear and Logistic Regression.md:155'), "
     "SVM overview headings (ai-course 03.4)."),
    ("CG-4e257d202bb4", "cover",
     "exact-match vs semantic matching distinction is treated in the lexical-search notes: "
     "master-ai '05 - NLP Fundamentals/Pre-Transformer NLP/09 - TF-IDF.md:197,325' "
     "('keyword queries ... exact match matters; embeddings may miss it') and "
     "'10 - BM25.md:319' ('BM25 finds exact matches; embeddings may match semantically "
     "similar but wrong items'); Redis exact-match caching pattern (master-ai '20 - AI "
     "Infrastructure/Serving/01 - Production AI Stack.md:252')."),
    ("CG-4fc47d389dc4", "cover",
     "global minimum covered by convexity treatments: master-ai '02 - Mathematics/"
     "Optimization/12 - Optimization Essentials.md:227' ('For convex functions, every "
     "local minimum is a global minimum'), logistic convex-bowl (ai-course '04. Logistic "
     "Regression.md:73'), SVM bowl (ai-course '05. The Dual Representation and Dot "
     "Products.md:24')."),
    ("CG-19c9da2c12a7", "cover",
     "hyperplane covered geometrically: master-ai '02 - Mathematics/Linear Algebra/02 - "
     "Dot Product.md:112' ('w·x + b = 0 defines a hyperplane in input space'), vector-"
     "roles note ('01 - Vectors.md:53'), logistic decision-boundary pitfall (:155)."),
    ("CG-3c0ad8e13aeb", "cover",
     "top-k covered as a decoding strategy: master-ai '08 - LLMs/Sampling/03 - Sampling "
     "Strategies.md:12,69-115' (dedicated '## Top-k Sampling' section with implementation) "
     "and MoE router formula Softmax(TopK(W_g x)) at master-ai '07 - Transformers/"
     "Variants/15 - Mixture of Experts Transformer.md:28'; glossary entry exists."),
    ("CG-ad242f12059b", "cover",
     "small gradients are the vanishing-gradient subject: ai-course '03. The Vanishing "
     "and Exploding Gradient Problems.md' (dedicated treatment) and Adam per-parameter "
     "adaptation (master-ai '12 - Optimization Essentials.md:267' 'parameters with small "
     "gradients get larger effective LR')."),
    ("CG-5cb7eafd5149", "cover",
     "forget gate covered by dedicated LSTM treatments: master-ai '04 - Neural Networks/"
     "Architectures/04 - RNN LSTM GRU.md' ('### Forget gate') and ai-course '07.2 - LSTM "
     "and GRU/01. LSTM - Gates as Learned Traffic Controllers.md:30' (f_t in [0,1]^h is "
     "the forget gate, per-dimension memory-keep semantics)."),
    ("CG-4f98e6893f28", "cover",
     "parameter updates covered by optimizer treatments: ai-course '03.2 - Optimization "
     "Algorithms/08. Loss Functions and Optimizers Deep Dive.md:7' (gradient signal that "
     "drives parameter updates), Adam effective-step analysis (:649), flat-minima/"
     "updates-per-epoch material ('04. Hyperparameters and Network Configuration.md:180')."),
    ("CG-9909904d0b5d", "cover",
     "quantization error covered: master-ai '13 - Inference/Quantization/03 - "
     "Quantization.md:344' (GPTQ error compensation), coding-interview GPTQ walkthrough "
     "('05 - Coding Interview Questions 3.md:564'), and image bit-depth definition "
     "(ai-course '1.1 What is a Digital Image.md:46' 'Quantization error is the "
     "difference between the true continuous intensity and ...')."),
    ("CG-6fdbc31b9d63", "cover",
     "cropping covered by augmentation/geometry treatments: ai-course '06 - Image "
     "Processing/03. Spatial Filtering and Neighborhood Processing/3.7 Geometric "
     "Transformations and Interpolation.md:141' ('Random rotation, scaling, and cropping "
     "are standard augmentations for training CNNs') and pipeline checklist "
     "deterministic resizing/cropping step; resize-before-center-crop idiom in "
     "PyTorch advanced note."),
    ("CG-a0ac51d4aae1", "cover",
     "eigenvectors covered by linear-algebra treatments: master-ai '02 - Mathematics/"
     "Linear Algebra/05 - Matrix Decomposition.md:37' (definition: direction A only "
     "stretches by lambda without rotating), ai-course '00. Linear Algebra "
     "Fundamentals.md:71' (eigendecomposition A = Q Lambda Q^T), PCA usage "
     "('01. Principal Component Analysis (PCA).md:35')."),
    ("CG-9f130da0c292", "cover",
     "'high recall' usage is part of the threshold-selection/metric trade-off treatments: "
     "ai-course '03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation "
     "Metrics Beyond Accuracy.md:107' (medical screening should optimize for high "
     "recall even at the cost of false positives); recall metric defined in the "
     "evaluation-metrics dossier domain."),
    ("CG-a258a752c15a", "cover",
     "hyperbolic (tanh) covered by activation-function treatments: ai-course '03. "
     "Artificial Neural Networks (ANN) - Comprehensive.md' ('### E. Hyperbolic Tangent "
     "(tanh)'), '06. Activation Functions in Deep Learning.md' ('### 2. Tanh (Hyperbolic "
     "Tangent)'), notation note (:122 tanh definition and range)."),
    ("CG-3b5f1a21e91f", "cover",
     "ResNet variants covered: ai-course '09. ResNet Bottleneck Blocks and Architectural "
     "Variants.md:361' ('ResNet Architecture Variants Table' — five standard variants, "
     "blocks per stage, block type) plus transfer-learning summary note Part 5 heading."),
    ("CG-c2519378b46e", "cover",
     "encoder-decoder RNN covered by seq2seq bottleneck treatments: master-ai '06 - "
     "Attention Mechanisms/Origins/01 - Origins of Attention.md:16' ('neural machine "
     "translation used an encoder-decoder RNN: 1. An encoder RNN (LSTM/GRU) reads the "
     "source sentence') and ai-course '07.3 .../01. The Encoder-Decoder Pattern - "
     "Conditional Generation.md:96' (bottleneck statement)."),
    ("CG-fc215657aa8f", "cover",
     "tool use covered by agent/MCP treatments: master-ai '19 - MCP/Components/02 - MCP "
     "Components.md' ('### When to Use Tools') and ReAct pattern note (:473 'the model "
     "can use tools while reasoning')."),
    ("CG-e20272221113", "cover",
     "KL divergence loss covered by a dedicated note: ai-course '10 - Generative Models/"
     "10.2 - Variational Autoencoders/03. The KL Divergence Loss.md' plus VAE-note "
     "sections and master-ai distillation capstone ('# KL divergence loss' section)."),
    ("CG-109bc2716e3e", "cover",
     "same treatment as 'divergence loss': dedicated ai-course note '03. The KL "
     "Divergence Loss.md' + probability-foundations cross-links ('07. Probability and "
     "Statistics for ML.md:4')."),
    ("CG-980b2ad12707", "cover",
     "model sizes covered: master-ai '26 - Papers/Transformers/05 - T5 2019.md' "
     "('### Model Sizes' enumerating T5 variants) and MuP transfer-across-model-sizes "
     "treatments ('14 - Learning Rate Schedules.md:206', '07 - Initialization "
     "Schemes.md:245')."),
    ("CG-99ac71937719", "cover",
     "possessive paraphrase of 'model parameters', which has dedicated treatment: "
     "ai-course '01.2 - Mathematical Foundations/01. Mathematical Notation (ML "
     "Course).md' ('## 2. Model Parameters and Prediction') and optimizer/autodiff "
     "usages (master-ai '10 - Gradient and Chain Rule.md:115')."),
    ("CG-9df256cd5956", "cover",
     "'last good' is the fragment of 'last good checkpoint'; the checkpoint-rollback "
     "protocol has dedicated treatment: master-ai '11 - Training/Optimization/05 - Loss "
     "Spikes and Stability.md:163-174' (rollback protocol with code), :211 (checkpoint "
     "cadence: keep last 3-5), :268 (Q&A), and '27 - Projects/Implementations/05 - "
     "Build a Tiny LLM Trainer.md:390,417'."),
    ("CG-71fc1712d61f", "cover",
     "JPEG format/pipeline covered by image-processing treatments: ai-course '06 - Image "
     "Processing/01. Fundamentals of Digital Images/1.7 The Color Image Processing "
     "Pipeline.md:110-134' ('JPEGs are heavily processed ... YCbCr + chroma subsampling "
     "+ DCT + quantization introduces block artifacts') and '1.3 Resolution and Bit "
     "Depth.md:44'; dedicated file-formats note exists (1.5)."),
    # ---- rejects: non-concept noise ----
    ("CG-8b837a81a43e", "reject",
     "Non-concept noise (prose-fragment): possessive fragment ('the target draft's "
     "distribution' in speculative-decoding importance sampling); the underlying "
     "rejection-sampling concept is covered by the speculative-decoding treatment."),
    ("CG-08ae88e8e5fe", "reject",
     "Non-concept noise (generic-vocabulary): comparative prose phrase with no "
     "conceptual denotation; the learning-rate/n_estimators tradeoff that produces it "
     "is covered by the gradient-boosting treatments."),
    ("CG-01a85906e051", "reject",
     "Non-concept noise (generic-vocabulary): comparative phrase from fine-tuning "
     "guidance (smaller vs larger model on small datasets); no conceptual denotation."),
    ("CG-5cf462ad5710", "reject",
     "Non-concept noise (generic-vocabulary): comparative phrase; model-scale guidance "
     "is covered by the fine-tuning/transfer-learning treatments."),
    ("CG-2ab7852dd390", "reject",
     "Non-concept noise (prose-fragment): prepositional phrase from the gradient-"
     "descent direction explanation ('we subtract because the gradient points toward "
     "steepest ascent'); covered by gradient-descent treatments."),
    ("CG-31290191404b", "reject",
     "Non-concept noise (prose-fragment): 'flow directly' from the residual-connection "
     "explanation; the residual/identity-mapping concept is covered by the ResNet "
     "treatments."),
    ("CG-9e2ec20ba94b", "reject",
     "Non-concept noise (prose-fragment): 'current input' from RNN/backprop context "
     "descriptions; the time-step mechanics are covered by the sequence-model and "
     "backprop treatments."),
    ("CG-6f76bc4b657e", "reject",
     "Non-concept noise (generic-vocabulary): 'different parts' from initialization "
     "sensitivity prose; no conceptual denotation."),
    ("CG-e117d6f4815e", "reject",
     "Non-concept noise (prose-fragment): 'variance across' from LayerNorm/k-fold "
     "descriptions; both the normalization-across-features and cross-validation "
     "variance concepts are covered by their treatments."),
    ("CG-60f3827265b9", "reject",
     "Non-concept noise (prose-fragment): fragment of 'low training error' from the "
     "underfitting/overfitting diagram context; covered by the fit-quality treatments."),
    ("CG-dd44dd820698", "reject",
     "Non-concept noise (generic-vocabulary): README metric-table label ('Source file "
     "count'); project metadata, not a knowledge concept."),
    ("CG-1ae81a410928", "reject",
     "Non-concept noise (generic-vocabulary): profession title used as audience "
     "framing; no conceptual denotation."),
    ("CG-09daa86eee84", "reject",
     "Non-concept noise (generic-vocabulary): generic programming verb spanning "
     "unrelated contexts (Python exercise data parsing, ReAct action parsing, PDF "
     "extraction difficulty, JSON-RPC parse error); each specific context is covered "
     "by its own treatment; no unifying concept treatment exists or is needed."),
    ("CG-b2770a9bd9c4", "reject",
     "Non-concept noise (prose-fragment): subject-verb fragment ('the CLS token "
     "attends to random patches'). Boundary rule recorded: unlike 'scaling laws "
     "predict'/'training diverges', this fragment does not lexically name its parent "
     "concept (attention); the parent is recoverable only by synonymy, and the "
     "attention mechanism is covered by dedicated self-attention treatments."),
    ("CG-6dc91c8fb121", "reject",
     "Non-concept noise (numeric fragment): depth literal from receptive-field growth "
     "discussion; the arithmetic is covered by the receptive-field treatment."),
    ("CG-4c8b46dd597a", "reject",
     "Non-concept noise (citation fragment): author surname (Ioffe and Szegedy, "
     "BatchNorm); the BatchNorm contribution is covered by the normalization "
     "treatments."),
    ("CG-8670a0dd8093", "reject",
     "Non-concept noise (citation fragment): global-index cross-reference; not a "
     "knowledge concept."),
    ("CG-f6f6df76cd78", "reject",
     "Non-concept noise (code-fragment): Python try/except idiom from the sales-project "
     "parsing exercise; error handling is course-tooling content, not a corpus concept."),
    ("CG-aa253bcfbf9e", "reject",
     "Non-concept noise (code/math fragment): truncated infinity literal inside a "
     "gradient-clipping code block."),
    ("CG-848a8a476bf3", "reject",
     "Non-concept noise (example-specific): example noun from embedding/polysemy "
     "illustrations ('bank' disambiguated by 'river'); the contextual-embedding concept "
     "is covered by the embeddings treatments."),
    ("CG-b9d0af31aa4b", "reject",
     "Non-concept noise (example-specific): example noun phrase illustrating static-"
     "embedding polysemy limitation (river bank vs financial bank); covered by the "
     "embeddings treatments."),
    ("CG-2fff61c522a3", "reject",
     "Non-concept noise (example-specific application noun): fraud detection is used "
     "only as an application example (Type I/II error framing, DL applications list); "
     "the ML content around it is covered by the evaluation-metrics treatments."),
]


def main() -> int:
    records = []
    for i, (cid, action, rationale) in enumerate(DECISIONS, 1):
        records.append({
            "candidate_id": cid,
            "decision_id": f"D-DISC002-B3-{i:04d}",
            "action": action,
            "rationale": rationale,
            "reviewer": R,
        })
    OUT.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )
    from collections import Counter
    counts = Counter(r["action"] for r in records)
    ids = [r["candidate_id"] for r in records]
    assert len(ids) == len(set(ids)) == 60, f"expected 60 unique, got {len(ids)}"
    print(f"wrote {len(records)} decisions to {OUT}")
    print(f"actions: {dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
