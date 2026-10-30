#!/usr/bin/env python3
"""DISC-002 session 10 (batch 10): emit the 60 review decisions as JSONL.

Method (same as batches 3-9): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch9 state,
session-10 fresh replay), a FENCE-AWARE definitional-treatment coverage
probe (scripts/disc002_batch10_probe.py, 62 terms, results in
/home/z/my-project/scratch/disc002-batch10-probe.json — batch-10
improvement: heading detection uses the authoritative mdextract structure
state machine, so Python comments inside code fences can no longer
masquerade as headings), targeted corpus verification for citations
(scripts/disc002_batch10_verify.py, 91 locator checks, all OK after 9
pattern fixes — mostly **bold** markers and two wrong-file pointers), and
an independent subagent cross-check of 40 judgment calls: 40/40 AGREE.
Corrections incorporated after INDEPENDENT orchestrator verification:
ColPali 'embeds it via a VLM (PaliGemma)' quote is at :132 (line :12
carries the other in-situ mention); Transfer Learning ImageNet mean/std
values are at :564; several headings are ###-level (Perplexity :87/:90,
channel headings, Eval :50, ResNet :477, TF-IDF :210, Scaling Laws :45)
and Agent vs Workflow :97 is ##-level. ONE subagent erratum was itself
WRONG and rejected: '06. VGG16 Architecture Deep Dive.md' DOES mention
ImageNet (4 hits incl. the mean-RGB preprocessing at :131 and code
defaults :513/:620/:622) — the session-9 lesson (re-verify every
correction) applied again.

Gap candidates this tranche: 'unembedding' looked gap-shaped (no
'## unembedding' heading anywhere; used in dependency position at
Initialization Schemes :176/:238, Logit Lens :85, InstructGPT :52), but
resolves as COVER — the defining note spells it hyphenated: master-ai
'07 - Transformers/Components/06 - Embedding Layer.md:60' 'The output
layer (un-embedding) is also a R^{d x |V|} matrix' inside '## Tied vs
Untied Embeddings' :58. Probe lesson recorded: search hyphenation
variants before claiming absence. NO new confirmed gap (async def remains
the model; corpus total stays 3).

Result: 30 evidence-cited covers + 30 noise rejects, 0 new gaps, 0
merges, 0 defers.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SELECTED = Path("/home/z/my-project/scratch/disc002-batch10-selected.json")
OUT = REPO / "state/concept-candidates/002-disc002-decisions-batch10.jsonl"

REVIEWER = (
    "GLM-5.3 orchestrator, DISC-002 session 10 (batch 10, "
    "subagent cross-checked 40/40; corrections independently "
    "re-verified - one rejected)"
)

# (candidate_id, action, rationale) in tranche selection order.
DECISIONS = [
    ("CG-1ac08c6c786b", "reject",
     "Non-concept noise (English verb): 'considers' is a generic verb used in prose across KNN ('the model considers everyone a neighbor', ai-course '03.3 - KNN/01. KNN - Comprehensive.md:807'), SVM misconceptions (':101') and Random Forest feature subsets (':33'); 9 homonym clusters; no concept identity."),
    ("CG-47ded69e6402", "reject",
     "Non-concept noise (English adverb): 'deliberately' is prose filler (ai-course padding note ':150', local connectivity ':26', PyTorch design ':65'); 8 homonym clusters; no concept identity."),
    ("CG-315bc0c35975", "cover",
     "Citation fragment of the DPO paper, covered by dedicated notes: master-ai '26 - Papers/Alignment/09 - DPO 2023.md' (paper note) and '12 - Fine-Tuning/DPO/04 - DPO Derivation.md:8' ('# DPO Derivation'), plus heading treatments 'DPO's implicit KL' ('02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md:241'), 'In RLHF and DPO' ('07 - Probability Essentials.md:343'), 'In DPO' ('16 - Estimators and Bias.md:295'). Title-fragment family precedent (batch-8/9)."),
    ("CG-4f455b1d9ba9", "reject",
     "Non-concept noise (gerund): 'entering' is prose ('input data entering the neuron', 'signal entering the neuron', 'raw data entering the system'); 7 homonym clusters; no concept identity."),
    ("CG-9583d851819a", "reject",
     "Non-concept noise (English fragment): 'exactly one' is prose quantification ('touches the curve at exactly one point', 'contributes exactly one FP'); 2 homonym clusters; no concept identity."),
    ("CG-911eacb2e04b", "cover",
     "Fragment of 'final classification layer/head'; the classification head has dedicated treatments: ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/04. The Fully Connected Layer and Flattening.md:1' (H1 title '# 4.4 The Fully Connected Layer (Classification Head) and Flattening'), '### Replacing the Classification Head for Transfer Learning' ('09. ResNet Bottleneck Blocks and Architectural Variants.md:477'), master-ai '### Classification Head' ('26 - Papers/Transformers/21 - Vision Transformer ViT 2020.md:45'), and the definition 'A classification head is softmax regression' ('03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md:98')."),
    ("CG-476a8f393cb5", "cover",
     "False Positive Rate has dedicated definitional treatments: ai-course '03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md:50' ('### Type I Error (False Positive Rate)') with the definition sentence at :56 ('This is also called the **False Positive Rate (FPR)**. It measures the fraction of actual negatives that are incorrectly classified as positives') and the ROC formula at :257 ('False Positive Rate (FPR) = 1 - Specificity = FP/(FP+TN)'); mirrored in '07. Scaling, Pipeline and Interpretability - Summary.md:304-305'."),
    ("CG-afc513269611", "cover",
     "Mamba/Transformer hybrid architectures have dedicated notes and definitions: master-ai '24 - Research Frontiers/State Space Models/01 - SSMs Mamba and Frontiers.md:9' (dedicated note covering SSMs/Mamba/hybrids), '26 - Papers/2024-2026/30 - Kimi Linear 2025.md:11' ('Kimi Linear is Moonshot AI's hybrid architecture that combines linear attention (for cheap long-context processing...)'), '26 - Papers/2024-2026/41 - Jamba 2024.md' (dedicated paper note; :194 'Jamba's MoE on top of the hybrid architecture'), '10 - Model Architecture Research/Closed Source/11 - Kimi K3 Architecture.md:30' ('Linear-time hybrid architecture via SSM-Transformer interleaving'), and '06 - Attention Mechanisms/Self-Attention/04 - Self-Attention.md:359' ('The 2024-2026 trend is toward **hybrid architectures** (Mamba + attention, Jamba)')."),
    ("CG-086a21ad762b", "cover",
     "ImageNet normalization has a dedicated callout with the exact values: ai-course '05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md:563-564' ('> [!info] ImageNet Normalization Is Non-Negotiable ... mean = [0.485, 0.456, 0.406] and std = [0.229, 0.224, 0.225]'), '### CRITICAL: Pre-trained VGG16 expects ImageNet normalization' at '03. PyTorch Advanced - VGG16 and Pre-trained Models.md:663', '02. Common Mistakes and How to Fix Them.md:454' ('always use ImageNet normalization with pre-trained models'), and '06. VGG16 Architecture Deep Dive.md:131' ('preprocessed by subtracting the mean RGB value computed over the ImageNet training set')."),
    ("CG-f2f49ae48b74", "reject",
     "Non-concept noise (gerund): 'letting' is prose ('letting the gradients accumulate', 'letting the network learn the downsampling strategy', 'letting the cell state accumulate'); 6 homonym clusters; no concept identity."),
    ("CG-588e909b1a21", "cover",
     "Long-running agents have dedicated treatments: master-ai '15 - AI Agents/Autonomy/08 - Autonomous Agent Lifecycles.md:223' ('## Long-Running Agent Patterns' — dedicated section in the dedicated lifecycles note, batch-9 cover family) with checkpointing guidance at :114; '## 4. Autonomous Agent (Long-Running, Self-Directed)' ('15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application.md:97'); definitional use at '01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md:121' ('Autonomous agents: long-running agents that operate without continuous human oversight')."),
    ("CG-aad1cfd16bff", "cover",
     "Pure vector search is the explicit contrast case in dedicated hybrid-search treatments: master-ai '17 - RAG/Ingestion and Retrieval/02 - Chunking Hybrid Search Reranking.md' (dedicated note; '## Hybrid Search (BM25 + Vector)' :160; :162 'Pure vector search misses exact-match queries (product codes, names, error messages). Pure BM25 misses semantic matches. **Combine both**.'; :348 'pure vector search misses too many'), '05 - NLP Fundamentals/Pre-Transformer NLP/10 - BM25.md:53' ('## BM25 vs Vector Search') + :105, and '### Hybrid Search' ('09 - TF-IDF.md:210')."),
    ("CG-6007ba36fa0c", "cover",
     "BatchNorm running statistics have dedicated sections: ai-course '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md:116' ('## Training vs. Evaluation Mode (CRITICAL)') with EMA mechanics at :122-:128 and '### Evaluation Mode' :130 ('it uses the **saved running mean** and **saved running variance**' :132); freezing caveat at '05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md:459' ('the running statistics are NOT controlled by requires_grad'); VGG16 note :315."),
    ("CG-776ab4674b53", "reject",
     "Non-concept noise (possessive fragment): \"target's\" is prose ('interpretable in the target's units', 'takes the target's hidden states'); 3 homonym clusters; no concept identity."),
    ("CG-4b5ef691d415", "cover",
     "Gap-shaped but RESOLVED as cover: 'unembedding' is used in dependency position (master-ai '04 - Neural Networks/Training/07 - Initialization Schemes.md:176' 'Final unembedding: often initialized to zeros' under '### Output projection' :175; Q&A at :238; '14 - Interpretability/Mechanistic/02 - Logit Lens and Tuned Lens.md:85'; '26 - Papers/Alignment/07 - InstructGPT 2022.md:52') but a definitional treatment EXISTS — the defining note spells it hyphenated: '07 - Transformers/Components/06 - Embedding Layer.md:60' ('The output layer (un-embedding) is also a R^{d x |V|} matrix') inside '## Tied vs Untied Embeddings' :58 (with E_out = E_in^T tying discussion). Probe lesson for synthesis: consolidate unembedding/un-embedding/lm_head spellings; search hyphenation variants before claiming absence."),
    ("CG-8d5b3cf10a39", "cover",
     "Unlabeled data is defined in the dedicated learning-types notes: ai-course '01 - Foundations and Overview/01.1 - AI, ML, and DL Hierarchy/02. Types of Learning.md:40' ('In unsupervised learning, the model is trained on an **unlabeled dataset**'), '08. Foundations of Machine Learning (Summary).md:101', semi-supervised contrast at '04. Machine Learning vs Deep Learning.md:72', master-ai '01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md:52' and '26 - Papers/Transformers/14 - GPT-1 2018.md:47' ('Train on a large unlabeled corpus')."),
    ("CG-bec3aabc5116", "cover",
     "Fragment of the Chinchilla rule, covered by dedicated scaling-law treatments (batch-9 family): master-ai '26 - Papers/2024-2026/42 - Scaling Laws (Kaplan and Chinchilla).md:11' ('the optimal ratio is ~20 tokens per parameter, not ~5') with '### The Compute-Optimal Allocation' :45; '11 - Training/Pretraining/01 - Pretraining Objectives and Scaling Laws.md:135' ('compute-optimal training uses ~20 tokens per parameter'); '11 - Training/Data/03 - Data Pipelines and Deduplication.md:16'."),
    ("CG-6e9aac45adf0", "cover",
     "PyTorch API for Global Average Pooling, which has a dedicated note (pth precedent: API name whose underlying concept has dedicated sections): ai-course '05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md:1' (H1 title) with the worked GAP implementation '# Global Average Pooling using nn.AdaptiveAvgPool2d' :328; GAP section in '03. Activation and Pooling Layers.md:423'; GAP+Linear classifier pattern at '04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md:511'."),
    ("CG-ee231dba5e29", "reject",
     "Non-concept noise (month name): 'august' appears only as the date stamp of vault-management research-queue audits ('as of iteration 13 (August 2026)', 'As of August 2026, this is **Insufficient public evidence**'); vault-management provenance metadata, not a knowledge concept (batch-9 'Academic DL' label precedent)."),
    ("CG-2af565e64e2a", "reject",
     "Non-concept noise (date fragment): 'august 2026' is the research-queue audit date stamp in the same master-ai '00 - Vault Management' and model-architecture notes as the parent 'august' candidate; provenance metadata, not a concept."),
    ("CG-770ed20df1e8", "cover",
     "Base models have dedicated sections and definitions: master-ai '05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md:87' ('### For base models') contrasted with :90 ('### For instruction-tuned / chat models'); '01 - AI Foundations/03 - A Brief History of AI.md:82' ('## 6. Alignment and Chat Models (2022-2024)') with :84 ('Pretrained base models aren't useful chatbots — they need alignment. Alignment is the process of making a model follow instructions...'); '05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md:101' ('what makes a base model into a chat model'); '26 - Papers/2024-2026/12 - DeepSeek-R1 2025.md:31' ('## R1-Zero: Pure RL on a Base Model')."),
    ("CG-0cf36f771eef", "reject",
     "Non-concept noise (number word): 'billion' is a magnitude in FLOPs/parameter prose ('approximately 1.85 billion', 'a factor of 10 billion', '15.5 billion FLOPs'); 8 homonym clusters; no concept identity."),
    ("CG-ed8c331901ff", "cover",
     "Channels have dedicated conceptual sections: ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/03. The Bridge - From Basic Convolution to Learned Weights.md:115' ('### The Dimension of Depth (Channels)'), '04. Demystifying Tensors - Volumes, Depth, and Data Formats.md:76' ('### Understanding Feature Maps as Channels'), '05. Processing 3D Volumes, Depth Summation, and Biases.md:94' ('### Generating Multiple Output Channels'), plus '### Cross-Channel Mixing' ('02. The Mathematics of Receptive Fields and 1x1 Convolutions.md:229') and the multi-channel convolution section ('06. Chapter Summaries (Aggregated)/02. Core Operators and Geometry - Summary.md:267')."),
    ("CG-ef64a0914316", "cover",
     "Chat models have dedicated sections: master-ai '05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md:90' ('### For instruction-tuned / chat models') with the Q&A at :262 ('Why is PPL less meaningful for instruction-tuned chat models?'), '01 - AI Foundations/03 - A Brief History of AI.md:82', '05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md:101', and the dedicated note '12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md' (:16-:18 base-vs-instruction-tuned contrast: 'A pretrained base LLM continues text... An instruction-tuned model responds to instructions')."),
    ("CG-df22296d128a", "reject",
     "Non-concept noise (English homonym word): 'children' has three unrelated in-situ senses — decision-tree child nodes ('03.7 - Tree-Based Models/01. Decision Trees...md:37,:88'), the child-screening false-negative example ('03.6 - Model Evaluation/02...md:111'), and model.children() in code ('02. Core Architecture and Philosophy.md:229'); each explained in-situ; no concept identity."),
    ("CG-e84c9ed219d8", "cover",
     "Artifact-shaped term, but the underlying device-placement concept has dedicated sections (pth precedent: dedicated section vs in-situ comment is the line): ai-course '05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md:178' ('## Mistake 4: Data on Wrong Device' with What Happens/Symptoms/Explanation/Fix; :188 'PyTorch requires all tensors involved in an operation to be on the same device') and master-ai '25 - Frameworks and Tools/Serving/08 - Ollama and llama.cpp.md:195' ('### CPU vs. GPU' with tokens/sec comparisons)."),
    ("CG-c2a696829952", "reject",
     "Non-concept noise (number-format word): 'decimal' is prose about number formats ('Truncates the decimal part', 'Adds decimal', 'Number of decimal places'); 6 homonym clusters; no concept identity."),
    ("CG-8e1ddc39f301", "reject",
     "Non-concept noise (vault-management prose fragment): 'existing content' appears only in master-ai '00 - Vault Management/Architecture Decisions.md' iteration logs ('All existing content preserved (additions only, no deletions)'); vault-management metadata, not a knowledge concept."),
    ("CG-1e8b227c4afa", "cover",
     "Fragment of 'final convolutional layer', which has dedicated heading treatments: ai-course '05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/07. Scaling, Pipeline and Interpretability - Summary.md:1270' ('#### Step 2: Target the Last Convolutional Layer' — Grad-CAM); in-situ definitional treatments at '05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md:36' ('the final convolutional layer of a CNN produces feature maps that retain spatial information... The last convolutional layer represents a sweet spot') and the NiN design at '02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md:221' ('the final convolutional layer produces $C$ feature maps')."),
    ("CG-b3ee1e8db0dd", "cover",
     "The verifiable/non-verifiable domain distinction has a dedicated note: master-ai '26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md' ('## Approach B: Verifiable Rewards (RLVR)' :60; :152 '**Domain restriction**: only works for verifiable domains. Extending to non-verifiable domains is an open problem'; domains table :168 'Math, code, formal logic | Any (including non-ver...)'), plus '09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md:115' ('## 1. Verifiable Rewards (the key innovation)') and the open question at '24 - Research Frontiers/08 - 2026 Research Frontier Update.md:131'."),
    ("CG-5ac64a079919", "reject",
     "Peripheral model name with in-situ role explanations only (sso precedent): no dedicated PaliGemma note corpus-wide; master-ai '26 - Papers/Multimodal/48 - ColPali 2024.md:132' ('embeds it via a VLM (PaliGemma) using late interaction') and :12 ('using a vision-language model (PaliGemma + ColBERT-style late interaction)') explain its role in-situ, and :82 states 'the specific VLM is interchangeable' — the contribution is the ColPali pattern, not the base VLM; '26 - Papers/Multimodal/55 - SigLIP-2 2025.md:12' lists PaliGemma 2 among SigLIP-2-based VLMs. Not load-bearing for any derivation."),
    ("CG-d15ab47c831b", "reject",
     "Non-concept noise (adverb): 'physically' is prose ('physically update the weights', 'physically pushes the entire green squiggle', 'diagonal movement is physically or logically impossible'); 9 homonym clusters; no concept identity."),
    ("CG-9d3a9f337eab", "cover",
     "Spatial features have direct definitional sentences in dedicated notes: ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/06. VGG16 Architecture Deep Dive.md:349' ('The convolutional layers learn the spatial feature detectors that actually understand the image; the FC layers merely...'), '09. ResNet Bottleneck Blocks and Architectural Variants.md:117' ('This is where the actual spatial feature extraction happens — the 3×3 kernel mixes information from neighboring spatial locations'), and the GAP spatial-feature-map treatment at '02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md:294'; consistent with the batch-9 feature-extractor/front-end cover family."),
    ("CG-98fb31b9d1be", "reject",
     "Non-concept noise (verb fragment): 'zeroed' describes ReLU gradient zeroing ('would have been zeroed out — this is the dying ReLU problem', '04.2 - Backpropagation Deep Dive/04...md:136'), dropout masks ('Neurons zeroed out'), and BN zero-centering — each in-situ inside the dedicated notes for the underlying concepts; no concept identity of its own."),
    ("CG-e909de56d4d8", "cover",
     "Fragment of the ResNet degradation experiment, covered by the dedicated note: ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md:1' (H1 title; the 20-vs-56-layer experiment is the note's subject: :28, :39, :45) plus '05. Evolution of CNN Architectures.md:164' ('## 5. ResNet (2015): Solving the Degradation Problem') and :170."),
    ("CG-9f730cf5a80e", "cover",
     "Fragment of 'best validation loss'; early stopping and best-checkpoint selection have dedicated sections: ai-course '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md:212' ('### 2.3 Epochs and Early Stopping'; :244 'Restore the model to the checkpoint with the best validation loss'), '06. Dropout and Regularization.md:472' ('### Early Stopping'; :513 'save the model weights from the epoch with the best validation loss, not from the final epoch'), master-ai '03 - Machine Learning/Generalization/06 - Regularization Techniques.md:79' ('## Early Stopping')."),
    ("CG-3913124b98cc", "cover",
     "Color channels have direct definitional treatments: ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/04. Demystifying Tensors - Volumes, Depth, and Data Formats.md:11' ('An RGB image is not just a flat X x Y grid. It fundamentally has a 3rd dimension: **Color Channels**... a stack of three 2D grids (one for Red, one for Green, one for Blue)') and '01. Introduction and Foundations of CNNs.md:80' ('each pixel is a triplet (R, G, B) representing the red, green, and blue color channels, making the full image a 3D tensor of size H x W x 3')."),
    ("CG-6969df67b5e1", "reject",
     "Layer-index label/variable name, not a concept (default' precedent): 'Conv3' is the AlexNet table row label ('05. Evolution of CNN Architectures.md:59'), the ResNet bottleneck expand layer variable ('09. ResNet Bottleneck Blocks and Architectural Variants.md:259' self.conv3; mermaid node :93), and the VGG block label ('### 3.2 Block 1: Two Conv3-64 + MaxPool', '06. VGG16 Architecture Deep Dive.md:135'); the underlying concepts (ResNet bottleneck 1x1->3x3->1x1; VGG blocks) have their own dedicated notes."),
    ("CG-e34ffa902ef9", "reject",
     "Non-concept noise (English fragment): 'different model' is prose ('different model families use different naming conventions', 'Embedding model trained on different distribution', 'different model architecture'); 3 homonym clusters; no concept identity."),
    ("CG-96f45c56356e", "reject",
     "Prose fragment from the seq2seq bottleneck description ('The entire source sentence must pass through c', 'The entire source is squeezed into (h, c)'); the underlying information-bottleneck concept has its dedicated note (master-ai '04 - Neural Networks/Architectures/05 - Seq2Seq and the Information Bottleneck.md'), making the fragment itself noise."),
    ("CG-c80aaa634ba0", "reject",
     "Non-concept noise (gerund): 'fixing' is prose ('Before fixing it, you must find it', 'prioritize fixing the largest errors first', 'Without fixing the random seed'); 6 homonym clusters; no concept identity."),
    ("CG-0f60363ad09a", "reject",
     "Non-concept noise (homonym fragment): 'full context' has unrelated senses — translation prose ('understand the full context of a sentence'), MLM bidirectionality ('predicting a masked token... can use information from both sides'), the autoregressive-vs-parallel table ('Fill in masked tokens from full context'), and error printing ('report the error with full context'); each in-situ; no single concept identity."),
    ("CG-d3444db9e14c", "cover",
     "Fragment of 'higher training error' (the degradation finding): covered by the dedicated note ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md:39' ('The 56-layer network is strictly worse at fitting the training data than the 20-layer network') and '05. Evolution of CNN Architectures.md:168' ('deeper networks had **higher training error** than their shallower counterparts... not caused by overfitting or vanishing gradients')."),
    ("CG-05f00ea5d419", "cover",
     "The degradation finding has a dedicated note: ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md:45' ('the deeper network is **underfitting** relative to the shallower network. This is the opposite of overfitting') and '05. Evolution of CNN Architectures.md:170' ('The 56-layer network had **higher training error** than the 20-layer network, despite having strictly more capacity')."),
    ("CG-5da6c0b11db5", "cover",
     "Dedicated project note exists: master-ai '27 - Projects/Implementations/04 - Build a Mini MoE.md:9' ('# 04 — Build a Mini MoE'), wikilinked from '04 - Neural Networks/Foundations/01 - Perceptrons and MLPs.md:308' ('See [[15 - Mixture of Experts Transformer]] and [[04 - Build a Mini MoE]] for details'), with the MoE concept treatment at :296 ('## Mixture of Experts (MoE)') and the dedicated '15 - Mixture of Experts Transformer' note; project roadmap entries at '00 - Vault Management/Architecture Decisions.md:251,:535'."),
    ("CG-8bf47a8762b8", "reject",
     "Non-concept noise (MOC organizational fragment): 'note 04' is chapter-MOC navigation prose ('Self-Attention]] — note 04', 'Capabilities]] — note 04') in master-ai MOC files; vault navigation metadata, not a concept."),
    ("CG-9f8cba713c92", "reject",
     "Non-concept noise (MOC organizational fragment): 'note 05' is chapter-MOC navigation prose in the same master-ai MOC files ('Multi-Head Attention]] — note 05', 'Multimodal]] — note 05'); vault navigation metadata, not a concept."),
    ("CG-f2a8ca40cde6", "cover",
     "One-bias-per-filter is the subject of a dedicated note: ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/05. Processing 3D Volumes, Depth Summation, and Biases.md' — :57 ('A filter that produces a 62x62 output feature map still has only one bias value. That same bias value is added to every single output pixel'), :86 ('27 multiplications -> one summation -> add one bias -> apply ReLU -> produce one pixel'), :157 ('**Bias parameters:** One bias per filter. Total biases = 128'); worked example at '05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md:237'."),
    ("CG-831537718f28", "reject",
     "Non-concept noise (gerund): 'reaching' is prose ('before reaching the minimum', 'prevents the activations... from reaching extreme values', 'the gradient signal reaching them is too small'); 7 homonym clusters; no concept identity."),
    ("CG-71f1276ed4cf", "reject",
     "Prose fragment of convolution mechanics ('a 3x3 convolutional kernel slides across the 224x224 spatial grid', 'repeated thousands of times as the filter slides'); the convolution operation has its dedicated deep-dive note ('02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md'); the fragment itself is not a concept."),
    ("CG-a2f0cdf5f1e2", "cover",
     "Citation fragment of Snell et al. (2024), covered by the dedicated test-time-compute note: master-ai '24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md:8' ('# 06 — Test-Time Compute Scaling'), '09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md:152' ('## Test-Time Compute Scaling Law') with :154 ('Snell et al. (2024) showed that test-time compute scales: more thinking -> better answers, with diminishing returns') and the fourth-scaling-dimension treatment at :260, plus '24 - Research Frontiers/08 - 2026 Research Frontier Update.md:69' ('Snell et al. (2024) log-scaling law is now empirically validated at frontier scale'). Title-fragment family precedent."),
    ("CG-88605657b863", "cover",
     "Same Snell et al. (2024) citation fragment family as CG-a2f0cdf5f1e2: dedicated note '24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md:8' plus the scaling-law treatments at '09 - Foundation Models/Reasoning Models/03 - Reasoning Models.md:152,:154,:260' and '08 - 2026 Research Frontier Update.md:69'; also '29 - Interview Prep/Conceptual/06 - Conceptual Interview Questions 2.md:20' and '24 - Research Frontiers/State Space Models/01 - SSMs Mamba and Frontiers.md:75'."),
    ("CG-1c23e5273e14", "cover",
     "Same Snell et al. (2024) citation fragment family: dedicated note '24 - Research Frontiers/Reasoning/06 - Test-Time Compute Scaling.md:8' ('# 06 — Test-Time Compute Scaling') + '03 - Reasoning Models.md:152' ('## Test-Time Compute Scaling Law', :154 definition, :260 scaling-curve treatment) + '08 - 2026 Research Frontier Update.md:65' ('## Test-Time Compute Scaling (Note 06)') and :69. Title-fragment family precedent (batch-8/9)."),
    ("CG-f2d1f06d8c45", "reject",
     "Fragment of 'triangle inequality' references in metric-property discussions, each in-situ: ai-course '01 - Foundations and Overview/01.2 - Mathematical Foundations/07. Probability and Statistics for ML.md:166' ('Not a true distance (no triangle inequality)'), '10 - Generative Models/10.2 - Variational Autoencoders/03. The KL Divergence Loss.md:18', master-ai '02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md:87' and '02 - Mathematics/Linear Algebra/02 - Dot Product.md:96' (Cauchy-Schwarz derivation). The metric-vs-divergence distinction is explained in-situ at every use site; no dedicated triangle-inequality treatment is needed for this corpus."),
    ("CG-5ec249172f97", "reject",
     "Homonym fragment with two unrelated in-situ senses: KNN scale advice ('you **must normalize** your data (scale everything to 0-1)', '03.3 - KNN/01. KNN - Comprehensive.md:557,:684') vs 0-1 loss in bias-variance ('For 0-1 loss, the formula is non-monotonic in variance', master-ai '03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md:180'); each sense explained in-situ; no single concept identity."),
    ("CG-1533c479d765", "reject",
     "Non-concept noise (folder-name fragment): '04 neural' is the chapter-folder name fragment from master-ai vault-management and mermaid roadmap graphs ('NN[04 Neural Networks]'); vault navigation metadata, not a concept."),
    ("CG-76e065455620", "reject",
     "Non-concept noise (folder-name fragment): '04 neural networks' is the chapter-folder name in master-ai roadmap/MOC/navigation contexts; the neural-networks chapter itself is the destination structure, not an emergent concept."),
    ("CG-ed907354e2c7", "reject",
     "Artifact-shaped LR value fragment (default' precedent: in-situ code/recipe values only): 3e-4 appears only in recipes, tables and code — master-ai '02 - Mathematics/Optimization/14 - Learning Rate Schedules.md:122' ('Peak LR: 3e-4'), :238 (Llama 3 table row), :129 (llama_lr function), '12 - Optimization Essentials.md:352' (lr=3e-4 code) — with no dedicated definitional section for the 3e-4 default; the learning-rate CONCEPT has its dedicated notes, but the candidate is the value fragment."),
    ("CG-7adc1c36dbf9", "reject",
     "Vault-management provenance label (batch-9 'Academic DL' precedent): ADR-006 is the source-labelling convention for closed-source model architectures in master-ai '00 - Vault Management/Architecture Decisions.md' (:84 '## ADR-006 — Source-labelling convention...'), referenced operationally at '00 - Vault Management/Research Queue.md:13' ('Per ADR-006, every claim about a closed-source model must be labeled') and 'Next Iteration.md:80'; vault governance metadata, not a knowledge concept."),
    ("CG-f5836e46ed46", "cover",
     "Alignment methods have dedicated heading treatments: master-ai '10 - Model Architecture Research/Closed Source/08 - Claude Architecture.md:53' ('### Constitutional AI as the Alignment Method') with :20 ('trained with **Constitutional AI** (RLAIF) — Anthropic's alignment method') and the alignment-method comparison table :132; '26 - Papers/Alignment/31 - Constitutional AI 2022.md:11' ('CAI is the alignment method used by Anthropic for Claude'); '03 - Machine Learning/Reinforcement Learning/10 - PPO Deep Treatment.md:11' ('PPO is the algorithm behind RLHF — the alignment method that produced ChatGPT'); plus the dedicated alignment chapter ('26 - Papers/Alignment/')."),
]


def main() -> int:
    selected = json.loads(SELECTED.read_text())
    sel_ids = [s["candidate_id"] for s in selected]
    sel_terms = {s["candidate_id"]: s["term"] for s in selected}
    assert len(selected) == 60, f"expected 60 selected, got {len(selected)}"
    assert len(DECISIONS) == 60, f"expected 60 decisions, got {len(DECISIONS)}"

    # Loud failure on any ID/term mismatch against the selection file.
    for (cid, action, _), sel_id in zip(DECISIONS, sel_ids):
        assert cid == sel_id, (
            f"decision order mismatch: {cid} != selection {sel_id} "
            f"(term {sel_terms.get(cid)!r})"
        )

    records = []
    for i, (cid, action, rationale) in enumerate(DECISIONS, start=1):
        records.append({
            "decision_id": f"D-DISC002-B10-{i:04d}",
            "candidate_id": cid,
            "action": action,
            "rationale": rationale,
            "reviewer": REVIEWER,
        })

    from collections import Counter
    actions = Counter(r["action"] for r in records)
    print("actions:", dict(actions))
    with open(OUT, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} decisions -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
