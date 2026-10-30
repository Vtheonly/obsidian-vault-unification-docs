#!/usr/bin/env python3
"""DISC-002 session 8 (batch 8): emit the 60 review decisions as JSONL.

Method (same as batches 3-7): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch7 state,
session-8 fresh replay), a definitional-treatment coverage probe
(scripts/disc002_batch8_probe.py, 86 terms, results in
/home/z/my-project/scratch/disc002-batch8-probe.json), targeted corpus
verification for citations (scripts/disc002_batch8_verify.py, 67 locator
checks, all OK after 4 pattern fixes), and an independent subagent
cross-check of 28 judgment calls (16 covers + 12 borderline rejects):
28/28 AGREE; corrections incorporated (unfrozen citation :210 not :212;
bert-family leap :109 not :110; chapter 13 = MOC + 7 notes; chapter 10 =
16 model notes + MOC + 2026 Synthesis; float32 prose anchor :427; SiLU
definition rests on Activation Functions.md:97 + Perceptrons/MLPs.md:206 —
the FFN Deep SwiGLU heading does not mention SiLU).

Result: 29 cover (evidence-cited) + 0 confirm_gap + 0 merge + 31 reject.
No new confirmed gap this tranche: the three gap-shaped candidates
(typing, computation graph, bilinear) all turned out to have real
definitional treatments (dynamic typing section; computation-graph
sections in both vaults; dedicated interpolation note).

Candidate IDs are taken from the selection file (scratch
disc002-batch8-selected.json) and asserted against it, so a wrong ID
fails loudly instead of silently deciding the wrong candidate.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/concept-candidates/002-disc002-decisions-batch8.jsonl")
SELECTED = Path("/home/z/my-project/scratch/disc002-batch8-selected.json")

R = "GLM-5.3 orchestrator, DISC-002 session 8 (batch 8, subagent cross-checked 28/28)"

# term -> (action, rationale[, merge_into])
DECISIONS_BY_TERM = {
    # ---------------- covers (29) ----------------
    "mcp overview": ("cover",
     "dedicated note exists: master-ai '19 - MCP/Architecture/01 - MCP "
     "Overview.md' ('# 01 - MCP' title with TL;DR defining MCP; aliases include "
     "'MCP Overview'), wikilinked from master-ai '00 - Vault Management/Research "
     "Queue.md:104', '01 - AI Foundations/03 - A Brief History of AI.md:100,149', "
     "'19 - MCP/Components/02 - MCP Components.md:354' and '27 - Projects/"
     "Mini-Projects/03 - Build a Mini Agent.md:478'."),
    "reasoning capability": ("cover",
     "dedicated treatments exist: master-ai '09 - Foundation Models/Reasoning "
     "Models/03 - Reasoning Models.md' ('## What Makes a Reasoning Model' :14 "
     "with the definition at :16), master-ai '24 - Research Frontiers/Reasoning/"
     "06 - Test-Time Compute Scaling.md' ('## The Reasoning Model Wave "
     "(2024-2025)' heading) and master-ai '08 - LLMs/Evaluation/06 - LLM "
     "Benchmarks.md' ('## Reasoning Model Benchmarks - The New Frontier' :205); "
     "the phrase 'reasoning capability' is the property those notes define."),
    "13 inference": ("cover",
     "chapter-level treatment exists: master-ai '13 - Inference' chapter (MOC "
     "plus 7 notes — 8 .md files including the MOC — covering Serving/KV "
     "Cache/Quantization/Speculative Decoding/Constrained Decoding), wikilinked "
     "as the inference-engineering pillar from master-ai '01 - AI Foundations/01 "
     "- What Is AI Engineering.md:46' and '04 - The Modern AI Stack.md:80' and "
     "cross-referenced from master-ai '06 - Attention Mechanisms/MOC.md:66'."),
    "ppo deep": ("cover",
     "dedicated note exists: master-ai '03 - Machine Learning/Reinforcement "
     "Learning/10 - PPO Deep Treatment.md' ('# 10 - PPO Deep Treatment' title), "
     "the stated prerequisite for RLHF (master-ai '03 - Machine Learning/MOC.md:"
     "24,49')."),
    "ppo deep treatment": ("cover",
     "same dedicated treatment as the 'ppo deep' candidate: master-ai '03 - "
     "Machine Learning/Reinforcement Learning/10 - PPO Deep Treatment.md' "
     "covers both surface forms of the title; cross-referenced from master-ai "
     "'03 - Machine Learning/Reinforcement Learning/07 - MDPs and Bellman "
     "Equations.md:120,172' and '12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md:"
     "158'."),
    "test data": ("cover",
     "definitional treatments exist: ai-course '01 - Foundations and Overview/"
     "01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine Learning "
     "(Summary).md' ('## 3. Test Set (15%)' :324 with purpose table :339-343 and "
     "golden rule :362), ai-course '05 - Convolutional Neural Networks (CNN)/05. "
     "Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline "
     "End-to-End Checklist.md' ('### Run on Test Set' heading), the leakage "
     "DANGER callout in ai-course '02 - Python and Data Tooling/02.4 - Data "
     "Cleaning and Preprocessing/04. Feature Scaling and Normalization.md:111' "
     "('Never fit the scaler on the full dataset'), and master-ai eval notes "
     "('05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md:217,229' "
     "contamination; '21 - LLMOps and MLOps/Pipelines/01 - LLMOps vs MLOps.md:"
     "113,147' eval-driven development)."),
    "bert-family": ("cover",
     "dedicated treatments exist: master-ai '07 - Transformers/Encoder Models/07 "
     "- BERT.md' ('## BERT Family' :64 with comparison table :66-73) and "
     "master-ai '05 - NLP Fundamentals/Embeddings/06 - Contextual Embeddings "
     "ELMo to BERT.md' (static-to-contextual leap at :109); usage in-situ at "
     "master-ai '05 - NLP Fundamentals/Tokenization/03 - WordPiece.md:108,113' "
     "(WordPiece requirement for BERT-family)."),
    "computation graph": ("cover",
     "definitional treatments exist in BOTH vaults: master-ai '02 - Mathematics/"
     "Calculus/10 - Gradient and Chain Rule.md' ('## Backpropagation = Chain "
     "Rule Applied to a Computation Graph' :78), ai-course '04 - Neural Networks "
     "and Deep Learning Foundations/04.1 - Neural Network Basics/02. Neural "
     "Network Architecture and Notation.md' ('### The Computational Graph (Full "
     "Forward Path)' heading), ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and "
     "Gradient Flow in CNNs.md:399' ('## 13.8 The Computational Graph and "
     "torch.no_grad()' + :403 explanation), and master-ai '04 - Neural Networks/"
     "Training/06 - Backpropagation.md:129' (retain_graph memory-leak "
     "treatment)."),
    "float32": ("cover",
     "dedicated treatment exists: master-ai '11 - Training/Optimization/04 - "
     "Mixed Precision Training.md' ('## Master Weights in FP32' :110 with "
     "rationale :112-116; the FP32/FP16/BF16 precision treatment), the ToTensor "
     "conversion prose in ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation."
     "md:427' ('[0, 255] (uint8) to [0.0, 1.0] (float32)'), and the NumPy "
     "homogeneous-dtype rule in ai-course '02 - Python and Data Tooling/02.3 - "
     "Essential Python Libraries/01. NumPy - Numerical Computation and Arrays."
     "md:8' ('all int64 or all float32')."),
    "partial derivative": ("cover",
     "dedicated note exists: ai-course '01 - Foundations and Overview/01.2 - "
     "Mathematical Foundations/04. Partial vs. Ordinary Derivatives.md' "
     "(title-level; the critical rule 'treat all other variables as if they are "
     "just numbers (constants)'), master-ai '02 - Mathematics/Calculus/10 - "
     "Gradient and Chain Rule.md' ('## Partial Derivatives' heading with the "
     "holding-other-variables definition), and ai-course '01 - Foundations and "
     "Overview/01.2 - Mathematical Foundations/01. Mathematical Notation (ML "
     "Course).md:92' ('Name: Partial Derivative... General Definition')."),
    "typing": ("cover",
     "definitional treatment exists for the dominant sense: ai-course '02 - "
     "Python and Data Tooling/02.2 - Python Programming Essentials/01. "
     "Variables, Operators, and Type Casting.md' ('## 1.1 Variables and Dynamic "
     "Typing' :3; definition :7 'Unlike statically typed languages (like C++ or "
     "Java), Python is dynamically typed. You do not declare the type of the "
     "variable; the interpreter infers it at runtime'). The type-hints half is "
     "explained in-situ by the notes that depend on it: master-ai '25 - "
     "Frameworks and Tools/Agent Frameworks/11 - PydanticAI.md:11' ('leverage "
     "Python type hints to define agent inputs, outputs, tool schemas, and "
     "dependencies') and '15 - Semantic Kernel.md:229' ('its type hints become "
     "the JSON schema the LLM sees'); dynamic-typing performance caveat at "
     "ai-course '04 - Neural Networks and Deep Learning Foundations/04.1 - "
     "Neural Network Basics/04. The Perceptron and the Chain Rule.md:167'. The "
     "'from typing import' surface (18 master-ai + 2 ai-course files) is code "
     "usage; static typing/type annotations have zero corpus occurrences, but "
     "the core typing concept IS defined, so this is not a gap."),
    "10 model architecture": ("cover",
     "chapter-level treatment exists: master-ai '10 - Model Architecture "
     "Research' chapter (MOC plus 16 model notes — 9 Open Source + 7 Closed "
     "Source — plus '2026 Frontier Model Synthesis.md'), wikilinked as the "
     "architecture pillar from master-ai '01 - AI Foundations/06 - Map of the "
     "Field.md:105,117' and maintained by master-ai '00 - Vault Management/"
     "Remaining Work.md:13,73'."),
    "augmentations": ("cover",
     "dedicated note exists: ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/07. Data "
     "Augmentation.md' ('# 18. Data Augmentation' title; the critical "
     "never-on-validation rule :377,734) plus master-ai '03 - Machine Learning/"
     "Generalization/06 - Regularization Techniques.md' ('## Data Augmentation' "
     "heading) and master-ai '26 - Papers/Transformers/54 - DeiT v2 2024.md' "
     "('### 5. Updated Data Augmentation')."),
    "conv layers": ("cover",
     "dedicated treatments exist: ai-course '05 - Convolutional Neural Networks "
     "(CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep "
     "Dive.md' ('# 3. The Convolution Operation Deep Dive' title), ai-course "
     "'05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries "
     "(Aggregated)/02. Core Operators and Geometry - Summary.md' ('#### Example "
     "A: Standard Conv Layer' heading) with the VGG conv-layer tables at "
     "ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and "
     "Connectivity/06. VGG16 Architecture Deep Dive.md:25,433', and master-ai "
     "'04 - Neural Networks/Architectures/03 - CNNs.md' ('Hierarchical "
     "features')."),
    "instructgpt 2022": ("cover",
     "dedicated paper note exists: master-ai '26 - Papers/Alignment/07 - "
     "InstructGPT 2022.md' ('# 07 - InstructGPT (Ouyang et al., 2022)' title) "
     "plus master-ai '07 - Transformers/Decoder Models/09 - GPT Family "
     "Evolution.md' ('### GPT-3.5 / InstructGPT (2022)' heading); the DPO note "
     "derives from its objective (master-ai '26 - Papers/Alignment/09 - DPO "
     "2023.md:31')."),
    "silu": ("cover",
     "definitional treatments exist: master-ai '04 - Neural Networks/Foundations/"
     "02 - Activation Functions.md' ('### SwiGLU' :95 with the SiLU definition "
     "at :97) and master-ai '04 - Neural Networks/Foundations/01 - Perceptrons "
     "and MLPs.md' ('### SwiGLU' :198, formula :203, SiLU definition :206: "
     "SwiGLU(x) = SiLU(W1 x) * (W2 x)); reinforced by master-ai '07 - "
     "Transformers/Components/05 - Feed-Forward Network Deep.md' ('### SwiGLU "
     "(Llama, Mistral, Gemma, Qwen)' :51) and master-ai '02 - Mathematics/"
     "Optimization/12 - Optimization Essentials.md:331' (nn.SiLU code). Note "
     "(cross-check): the FFN Deep SwiGLU section itself does not mention SiLU; "
     "the SiLU definition rests on the two foundations notes."),
    "agent vs": ("cover",
     "title fragment of the dedicated note master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' ('# Agent vs "
     "Workflow vs LLM Application' :7, '## The Spectrum' :12), wikilinked from "
     "master-ai '01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic "
     "AI.md:158,292' and master-ai '08 - LLMs/Capabilities/04 - In-Context "
     "Learning.md:255'."),
    "channel depth": ("cover",
     "dedicated treatment exists: ai-course '05 - Convolutional Neural Networks "
     "(CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth "
     "Summation, and Biases.md:5' ('**The Rule:** A filter in a CNN must "
     "*always* match the exact channel depth of the input volume it is "
     "convolving over'), the output-dimension formula note ai-course '05 - "
     "Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. "
     "The Output Spatial Dimension Formula.md' (K refers only to spatial dims), "
     "and the channel-progression exercises at ai-course '05 - Convolutional "
     "Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. "
     "Exercises Solved and Explained.md:379' (32->64->128 while halving "
     "spatial)."),
    "embedder": ("cover",
     "dedicated treatments exist: master-ai '09 - Foundation Models/Embedding "
     "Models/02 - Embedding Models for Retrieval.md' ('## What Makes a "
     "\"Retrieval Embedding Model\"?' :14, definition :16-20), master-ai '09 - "
     "Foundation Models/Embedding Models/06 - Embedding Model Training.md' "
     "('# 06' title :8), and master-ai '07 - Transformers/Encoder Models/07 - "
     "BERT.md:106' (BGE/E5 as the RAG standard embedders)."),
    "unfrozen": ("cover",
     "dedicated treatment exists: ai-course '05 - Convolutional Neural Networks "
     "(CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning "
     "and Fine-Tuning.md' ('## Strategy 1: Feature Extraction (Freeze "
     "Everything)' :67; the Strategy 2/3 unfreeze ladder :185), ai-course '05 - "
     "Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/02. "
     "Core Architecture and Philosophy.md:294,300' ('Front-end partially "
     "unfrozen' / 'All layers unfrozen'), and master-ai '23 - Multimodal AI/"
     "Fusion Architectures/06 - Cross-Modal Attention.md:210' ('### Freezing "
     "vs. Fine-Tuning Encoders')."),
    "vs workflow": ("cover",
     "title fragment of the same dedicated note: master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' (:7 title, "
     ":12 '## The Spectrum'); all six 'agent vs'/'vs workflow'/'workflow "
     "vs'/'agent vs workflow'/'vs llm' fragments map to this one note."),
    "vs workflow vs": ("cover",
     "title fragment of the same dedicated note: master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' (:7 title, "
     ":12 '## The Spectrum')."),
    "workflow vs": ("cover",
     "title fragment of the same dedicated note: master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' (:7 title, "
     ":12 '## The Spectrum')."),
    "agent vs workflow": ("cover",
     "title fragment of the same dedicated note: master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' (:7 title, "
     ":12 '## The Spectrum')."),
    "bilinear": ("cover",
     "dedicated note exists: ai-course '06 - Image Processing/03. Spatial "
     "Filtering and Neighborhood Processing/3.7 Geometric Transformations and "
     "Interpolation.md' with real headings '### Nearest-neighbor interpolation' "
     ":90, '### Bilinear interpolation' :98, '### Bicubic interpolation' :108; "
     "the algebraic sense is covered in-situ by master-ai '02 - Mathematics/"
     "Linear Algebra/02 - Dot Product.md:93' ('Bilinear: linear in each "
     "argument'); ViT position-embed usage at master-ai '07 - Transformers/"
     "Variants/13 - Vision Transformer ViT.md:177'."),
    "draft head": ("cover",
     "definitional treatments exist: master-ai '26 - Papers/Efficient Attention/"
     "51 - EAGLE-3 2025.md:23' ('EAGLE-2 trains the draft head on top of a "
     "frozen target model'), master-ai '26 - Papers/Efficient Attention/52 - "
     "MTP Multi-Token Prediction.md:12' ('produces a natural draft head that "
     "can be used for speculative decoding'), master-ai '13 - Inference/"
     "Speculative Decoding/05 - Speculative Decoding.md' ('## Draft Model "
     "Choices' :61; acceptance/rejection resampling equivalence :48), and the "
     "MTP-vs-EAGLE distinction at master-ai '29 - Interview Prep/Conceptual/06 "
     "- Conceptual Interview Questions 2.md:111'."),
    "output validation": ("cover",
     "dedicated treatments exist: master-ai '22 - Production AI/Security/01 - "
     "LLM Security and Prompt Injection.md' ('### 2. Output validation' :64 "
     "with definition :65), master-ai '19 - MCP/Security/03 - MCP Security."
     "md:60' ('validate tool call arguments against schemas and policies') "
     "plus the defense-in-depth mapping :107, and master-ai '25 - Frameworks "
     "and Tools/Agent Frameworks/10 - CrewAI.md' ('### Output Validation' "
     ":190, :192)."),
    "predicted class": ("cover",
     "definitional treatment exists: ai-course '03 - Machine Learning/03.6 - "
     "Model Evaluation/01. Model Evaluation and Metrics.md:40' ('It compares "
     "the **Predicted Class** against the **Actual Class**') and ai-course '01 "
     "- Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/08. "
     "Foundations of Machine Learning (Summary).md:983' ('The matrix compares "
     "the **Predicted Class** against the **Actual Class** (Ground Truth)')."),
    "vs llm": ("cover",
     "title fragment of the same dedicated note: master-ai '15 - AI Agents/"
     "Architecture/01 - Agent vs Workflow vs LLM Application.md' (:7 title, "
     ":12 '## The Spectrum')."),

    # ---------------- rejects (31) ----------------
    "virtually": ("reject",
     "Non-concept noise (adverb): 'virtually no learning', 'virtually zero', "
     "misc prose; no definitional treatment needed anywhere."),
    "wasting": ("reject",
     "Non-concept noise (gerund): 'wasting dimensionality', 'wasting "
     "computation', 'wasting training time' — prose inside other topics' "
     "treatments."),
    "attending": ("reject",
     "Non-concept noise (gerund of attention usage): the attention concept has "
     "a dedicated chapter — master-ai '06 - Attention Mechanisms/MOC.md:7' "
     "('# 06 - Attention Mechanisms MOC') and ai-course '08 - Attention and "
     "Transformers' — and the self-attends prose lives inside ai-course '07 - "
     "Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/03. "
     "From RNNs to Attention - The Historical Bridge.md:41'."),
    "solving": ("reject",
     "Non-concept noise (gerund): 'solving the equations', 'solving non-linearly "
     "separable problems' — prose inside the treatments that teach those "
     "procedures."),
    "large gradients": ("reject",
     "Non-concept noise (adjective-noun phrase): the pathology is covered by "
     "the dedicated note ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and "
     "Exploding Gradient Problems.md' ('# 15. The Vanishing and Exploding "
     "Gradient Problems' :1), and GOSS is defined in-situ at ai-course '03 - "
     "Machine Learning/03.7 - Tree-Based Models/03. Gradient Boosting and "
     "XGBoost.md:95' ('keeps all samples with large gradients and randomly "
     "samples those with small gradients')."),
    "performing": ("reject",
     "Non-concept noise (gerund): 'performing Backpropagation', 'performing "
     "feature selection', 'how a system is performing' — prose."),
    "dividing": ("reject",
     "Non-concept noise (gerund): 'dividing by the maximum absolute value', "
     "'dividing a population into groups', 'dividing a space' — prose inside "
     "the scaling/clustering/SVM treatments."),
    "ensuring": ("reject",
     "Non-concept noise (gerund): 'ensuring the insight leads to a decision', "
     "'ensuring gradient descent can find the minimum' — prose."),
    "normalizing": ("reject",
     "Non-concept noise (gerund): the normalization family has dedicated notes "
     "— ai-course '02 - Python and Data Tooling/02.4 - Data Cleaning and "
     "Preprocessing/04. Feature Scaling and Normalization.md' ('# 4. Feature "
     "Scaling and Normalization' :1) and ai-course '04 - Neural Networks and "
     "Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. "
     "Batch Normalization.md' ('# 16. Batch Normalization' :1) — and the "
     "softmax-normalize explanation lives at ai-course '04 - Neural Networks "
     "and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/01. "
     "Backpropagating to the Output Layer.md:70'."),
    "person": ("reject",
     "Non-concept noise (generic noun): 'identifying a person, a horse, and a "
     "dog', 'a blindfolded person', 'Sick person predicted as Sick' — example "
     "prose in application/analogy contexts."),
    "rejection": ("reject",
     "Non-concept noise (homonym): rejection sampling is covered in-situ by "
     "master-ai '13 - Inference/Speculative Decoding/05 - Speculative "
     "Decoding.md' (:48 'acceptance/rejection resampling is mathematically "
     "equivalent to sampling from p directly'; :197 accept with probability "
     "min(1, p/q)), clinical TN/FP by the confusion-matrix treatments "
     "(ai-course '03 - Machine Learning/03.6 - Model Evaluation/02. Model "
     "Evaluation Metrics Beyond Accuracy.md:29,37,39'), and HITL rejection by "
     "master-ai '15 - AI Agents/Autonomy/09 - Human-in-the-Loop Patterns.md:"
     "309'; CAI's rejection-sampling stage in-situ at master-ai '26 - Papers/"
     "Alignment/31 - Constitutional AI 2022.md:43-49'."),
    "relatively": ("reject",
     "Non-concept noise (adverb): 'relatively simple', 'relatively flat "
     "region', 'relatively robust' — prose."),
    "subtracting": ("reject",
     "Non-concept noise (gerund): the subtract-the-gradient rule has dedicated "
     "treatments — ai-course '03 - Machine Learning/03.2 - Optimization "
     "Algorithms/07. Gradient Descent - The Update Rule and Convergence.md:122' "
     "('> [!tip] Why do we subtract a negative?'), ai-course '01 - Foundations "
     "and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient "
     "Descent.md:137,140', ai-course '03 - Machine Learning/03.2 - Optimization "
     "Algorithms/01. Gradient Descent Optimization (DL Course).md:231'."),
    "2-5": ("reject",
     "Non-concept noise (numeric range artifact): '+-2-5%', '2-5 percentage "
     "points', '2-5 new code/worked examples' — measurement ranges, not a "
     "concept."),
    "2026-08-08": ("reject",
     "Non-concept noise (date artifact): a vault-management frontmatter date "
     "from master-ai '00 - Vault Management/Architecture Decisions.md:440,375,"
     "493' — source-vault bookkeeping, not knowledge content."),
    "e1f5fe": ("reject",
     "Non-concept noise (markup artifact): a mermaid CSS fill-color value "
     "('style A fill:#e1f5fe') quoted from diagram code fences in ai-course "
     "notes; not a concept."),
    "gradient-based": ("reject",
     "Non-concept noise (adjective phrase): 'gradient-based optimization', "
     "'gradient-based one-side sampling' — the gradient-descent family has "
     "dedicated notes in both vaults (ai-course '03.2 - Optimization "
     "Algorithms' chapter; master-ai '02 - Mathematics/Optimization')."),
    "eliminating": ("reject",
     "Non-concept noise (gerund): 'eliminating the need for one-hot encoding', "
     "'eliminating the autograd overhead', 'eliminating manual feature "
     "engineering' — prose inside the topics that teach those wins."),
    "included": ("reject",
     "Non-concept noise (past participle): 'if frozen parameters are included, "
     "the optimizer wastes memory', 'may be included within the filter's "
     "receptive field' — prose."),
    "properly": ("reject",
     "Non-concept noise (adverb): 'properly regularized', 'learn properly', "
     "'properly normalized' — prose."),
    "successful": ("reject",
     "Non-concept noise (adjective): 'almost all successful CNN architectures', "
     "'the original Inception architecture was so successful' — prose."),
    "tested": ("reject",
     "Non-concept noise (past participle): the trained-on-ground-truth/"
     "tested-on-own-outputs contrast is the exposure-bias concept, covered by "
     "the dedicated note ai-course '07 - Sequence Models and RNNs/07.3 - "
     "Sequence to Sequence and Encoder-Decoder/02. Teacher Forcing and "
     "Exposure Bias.md' ('# 02. Teacher Forcing and Exposure Bias' :1; '## The "
     "catch - exposure bias' :43) and ai-course '08 - Attention and "
     "Transformers/08.4 - Encoder Decoder and the Design Space/03. "
     "Autoregressive vs Parallel Encoding.md:65'."),
    "wrong answers": ("reject",
     "Non-concept noise (phrase): the concept is hallucination, covered by the "
     "dedicated note master-ai '08 - LLMs/Limitations/05 - Hallucination.md' "
     "('## What Is Hallucination?' :14; :223 'confident wrong answers are "
     "common. Confidence is not calibration.')."),
    "csv": ("reject",
     "Non-concept noise (file-format term): used in-situ — pandas read_csv at "
     "ai-course '02 - Python and Data Tooling/02.3 - Essential Python "
     "Libraries/03. DataFrames - Deep Dive and Operations.md:17', data-storage "
     "format comparison at ai-course '01 - Foundations and Overview/01.3 - "
     "Data Science Foundations/01. Data Science Definition and Philosophy.md:46' "
     "('Relational Databases (SQL), CSV, Excel'), and the TP3 lab actually "
     "creates a CSV (ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.4 - Labs/02. TP3 - Data Cleaning, Normalization, and "
     "Encoding - Solution Guide.md:102'). No definitional treatment needed for "
     "a file format in dependency position."),
    "extract features": ("reject",
     "Non-concept noise (phrase): feature extraction is covered in-situ — "
     "ai-course '01 - Foundations and Overview/01.1 - AI, ML, and DL "
     "Hierarchy/04. Machine Learning vs Deep Learning.md:9' ('A human expert "
     "must manually extract relevant features'; '## Feature Engineering: The "
     "Core Difference' :5) and ai-course '05 - Convolutional Neural Networks "
     "(CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of "
     "CNNs.md:238' (end-to-end training eliminating manual feature "
     "engineering)."),
    "memory usage": ("reject",
     "Non-concept noise (phrase): in-situ treatments — the optimizer memory "
     "table at ai-course '03 - Machine Learning/03.2 - Optimization "
     "Algorithms/08. Loss Functions and Optimizers Deep Dive.md:357' ('2 extra "
     "buffers per parameter') and the no_grad memory-leak treatment at "
     "ai-course '04 - Neural Networks and Deep Learning Foundations/04.2 - "
     "Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in "
     "CNNs.md:399' ('## 13.8 The Computational Graph and torch.no_grad()')."),
    "resizing": ("reject",
     "Non-concept noise (gerund): image resizing is used in-situ by the "
     "torchvision transform pipelines (ai-course '04.3/07. Data "
     "Augmentation.md:74' RandomResizedCrop) and the Grad-CAM heatmap "
     "upsampling (ai-course '05 - Convolutional Neural Networks (CNN)/05. "
     "Pipeline, Evaluation, and Interpretability/03. Demystifying the Black "
     "Box - CNN Interpretability.md:355'."),
    "fraud": ("reject",
     "Non-concept noise (application-domain noun): fraud-detection use-case "
     "mentions at ai-course '01 - Foundations and Overview/01.1 - AI, ML, and "
     "DL Hierarchy/06. Applications of Deep Learning.md:81' and class examples "
     "at ai-course '03 - Machine Learning/03.1 - Regression/04. Logistic "
     "Regression.md:3' ('Fraud vs. Not Fraud'); never a heading or definition "
     "corpus-wide."),
    "gdpr": ("reject",
     "Non-concept noise (external regulation): treated in-situ by the "
     "right-to-explanation discussion at ai-course '05 - Convolutional Neural "
     "Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. "
     "Demystifying the Black Box - CNN Interpretability.md:22' and the Q26 "
     "quiz note; the PII note adds '### GDPR (European Union)' in-situ at "
     "master-ai '22 - Production AI/Security/05 - PII and Data Leakage.md:165' "
     "— a compliance reference, not a knowledge concept for the curriculum."),
    "operatorname": ("reject",
     "Non-concept noise (LaTeX markup artifact): '\\operatorname{...}' commands "
     "from display-math blocks in ai-course chapter summaries; not a concept."),
    "preceding": ("reject",
     "Non-concept noise (adjective): 'the preceding layers', 'the preceding "
     "conv layer', 'preceding layers Theta' — positional prose inside the "
     "batch-norm/backprop treatments that use it."),
}


def main() -> int:
    selected = json.loads(SELECTED.read_text())
    by_term = {s["term"]: s["candidate_id"] for s in selected}

    missing = set(by_term) - set(DECISIONS_BY_TERM)
    extra = set(DECISIONS_BY_TERM) - set(by_term)
    assert not missing, f"terms without decisions: {sorted(missing)}"
    assert not extra, f"decisions for unselected terms: {sorted(extra)}"

    records = []
    for i, sel in enumerate(selected, 1):
        term = sel["term"]
        cid = sel["candidate_id"]
        item = DECISIONS_BY_TERM[term]
        action, rationale = item[0], item[1]
        rec = {
            "action": action,
            "candidate_id": cid,
            "decision_id": f"D-DISC002-B8-{i:04d}",
            "rationale": rationale,
            "reviewer": R,
        }
        if action == "merge":
            rec["merge_into"] = item[2]
        records.append(rec)

    with open(OUT, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    from collections import Counter
    counts = Counter(r["action"] for r in records)
    print(f"wrote {len(records)} decisions to {OUT}")
    print("actions:", dict(counts))
    print("all decision candidate_ids taken from the selection file (asserted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
