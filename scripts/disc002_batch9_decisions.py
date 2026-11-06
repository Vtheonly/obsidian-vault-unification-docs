#!/usr/bin/env python3
"""DISC-002 session 9 (batch 9): emit the 60 review decisions as JSONL.

Method (same as batches 3-8): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch8 state,
session-9 fresh replay), a definitional-treatment coverage probe
(scripts/disc002_batch9_probe.py, 82 terms, results in
/home/z/my-project/scratch/disc002-batch9-probe.json), targeted corpus
verification for citations (scripts/disc002_batch9_verify.py, 139 locator
checks, all OK after 4 pattern fixes: mobilenet pointwise 1×1 unicode,
1x1-note real heading — the probe's '# 1x1 convolution' hit was a Python
comment in a fence at :312, real heading '## 1×1 Convolutions: Why They
Seem Useless' :223; strides note real title '# 2.3 Strides'; import
comment path 03.2/08), and an independent subagent cross-check of 28
judgment calls: 28/28 AGREE; corrections incorporated after INDEPENDENT
orchestrator verification (SSO usage is 18 word-boundary occurrences
across 3 notes incl. MCP Marketplace :372 — the original '3x in 2 notes'
framing came from the candidate's 4 evidence quotes only; Data Prep
'determines model capacity' is :174 not :175; BatchNorm running_mean
comment is :192 not :194; BPE.md:261 is a real in-situ UTF-8 definition;
'04.3/04. Hyperparameters and Network Configuration.md:15' is a direct
definitional treatment of 'representational capacity'; the
Autonomous-Agent-Lifecycles note's aliases include 'Agent Lifecycles'
:6; attention-layer headings exist — '### Full Attention Layers' Kimi
Linear :62). Two subagent corrections were themselves WRONG and rejected
after verification: the AI-vs-ML wikilink IS at :292 (subagent claimed
:293), and the LaTeX gen cluster DOES exist as
\\mathcal{L}_{\\text{gen}} at '05. Normalization, Regularization and
Augmentation - Summary.md:14' (the subagent searched without the
\\text{} wrapper).

Result: 35 cover (evidence-cited) + 0 confirm_gap + 0 merge + 25 reject.
No new confirmed gap this tranche: the gap-shaped candidates all have
real definitional treatments (representational capacity: direct
definition at 04.3/04:15; utf-8: in-situ definition at BPE.md:261; sso:
peripheral enterprise integration term whose identity/auth role is
explained in-situ at every use site and is not load-bearing for any
derivation — adjudicated reject, not gap).

Candidate IDs are taken from the selection file (scratch
disc002-batch9-selected.json) and asserted against it, so a wrong ID
fails loudly instead of silently deciding the wrong candidate.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/concept-candidates/002-disc002-decisions-batch9.jsonl")
SELECTED = Path("/home/z/my-project/scratch/disc002-batch9-selected.json")

R = "GLM-5.3 orchestrator, DISC-002 session 9 (batch 9, subagent cross-checked 28/28)"

# term -> (action, rationale[, merge_into])
DECISIONS_BY_TERM = {
    # ---------------- covers (35) ----------------
    "vs llm application": ("cover",
     "dedicated note exists: master-ai '15 - AI Agents/Architecture/01 - "
     "Agent vs Workflow vs LLM Application.md' ('# Agent vs Workflow vs LLM "
     "Application' title :7), wikilinked from master-ai '00 - Vault "
     "Management/Architecture Decisions.md:574', '01 - AI Foundations/02 - "
     "AI vs ML vs DL vs GenAI vs Agentic AI.md:292' and '08 - LLMs/"
     "Capabilities/04 - In-Context Learning.md:255'."),
    "workflow vs llm": ("cover",
     "same dedicated note as the 'vs llm application' candidate: master-ai "
     "'15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM "
     "Application.md' covers both surface n-gram fragments of its title "
     "(batch-8 title-fragment family precedent); usage sites master-ai '01 "
     "- AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md:292' "
     "and '08 - LLMs/Capabilities/04 - In-Context Learning.md:255'."),
    "adaptive learning": ("cover",
     "adaptive learning rates are definitional treatments: master-ai '02 - "
     "Mathematics/Optimization/12 - Optimization Essentials.md' ('## Adam' "
     ":82; 'LAMB — layer-wise adaptive learning rates' :128) plus the "
     "dedicated '13 - Adam Derivation.md' ('# 13 - Adam Derivation Deep "
     "Dive'); ai-course '03 - Machine Learning/03.2 - Optimization "
     "Algorithms/08. Loss Functions and Optimizers Deep Dive.md' ('### "
     "Adam: The Modern Default Optimizer' :296) and '04 - Neural Networks "
     "and Deep Learning Foundations/04.3 - Training Dynamics and "
     "Stability/04. Hyperparameters and Network Configuration.md:284' "
     "('Adam combines the ideas of momentum and adaptive learning rates'). "
     "Corpus-wide the only sense is the optimizer sense (subagent-verified "
     "22/22 hits are adaptive learning rates)."),
    "dropout rate": ("cover",
     "definitional treatments exist: ai-course '04 - Neural Networks and "
     "Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. "
     "Dropout and Regularization.md' (dedicated note; degrees-of-freedom "
     "rationale :33) plus master-ai '03 - Machine Learning/Generalization/"
     "06 - Regularization Techniques.md' ('## Dropout (Srivastava et al., "
     "2014)') and the hyperparameter glosses at ai-course '01 - Foundations "
     "and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of "
     "Machine Learning (Summary).md:500' ('Dropout Rate | Fraction of "
     "neurons to drop') and '04.1 - Neural Network Basics/08. Data "
     "Preparation and MLP Implementation.md:175' ('Regularization strength "
     "($\\lambda$, dropout rate)')."),
    "agent lifecycles": ("cover",
     "dedicated note exists: master-ai '15 - AI Agents/Autonomy/08 - "
     "Autonomous Agent Lifecycles.md' ('# 08 — Autonomous Agent "
     "Lifecycles' title :9; aliases include 'Agent Lifecycles' :6; 'six "
     "phases of an autonomous agent lifecycle' :306), wikilinked from "
     "master-ai '15 - AI Agents/Autonomy/09 - Human-in-the-Loop "
     "Patterns.md:288,319' and '15 - AI Agents/MOC.md:22,32'."),
    "ai 2022": ("cover",
     "title fragment of the 'Constitutional AI 2022' paper note: "
     "master-ai '26 - Papers/Alignment/31 - Constitutional AI 2022.md' "
     "(dedicated paper note, title '# 31 — Constitutional AI (Bai et al., "
     "2022)') plus '26 - Papers/Alignment/07 - InstructGPT 2022.md'; "
     "treatments at master-ai '01 - AI Foundations/03 - A Brief History "
     "of AI.md:87' ('Constitutional AI (Anthropic, 2022) — RLAIF') and "
     "'10 - Model Architecture Research/Closed Source/08 - Claude "
     "Architecture.md' ('### Constitutional AI as the Alignment Method' "
     ":53; link :146). Batch-8 'instructgpt 2022' fragment precedent."),
    "autonomous agent lifecycles": ("cover",
     "dedicated note exists: master-ai '15 - AI Agents/Autonomy/08 - "
     "Autonomous Agent Lifecycles.md' (full-title form of the candidate; "
     "'# 08 — Autonomous Agent Lifecycles' :9; lifecycle phases :306)."),
    "constitutional ai 2022": ("cover",
     "dedicated paper note exists: master-ai '26 - Papers/Alignment/31 - "
     "Constitutional AI 2022.md' ('# 31 — Constitutional AI (Bai et al., "
     "2022)'); further treatments at master-ai '10 - Model Architecture "
     "Research/Closed Source/08 - Claude Architecture.md' ('### "
     "Constitutional AI as the Alignment Method' :53) and '01 - AI "
     "Foundations/03 - A Brief History of AI.md:87'."),
    "convolutional base": ("cover",
     "definitional treatments exist: ai-course '05 - Convolutional Neural "
     "Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture "
     "and Philosophy.md' ('## The Two-Part Architecture: Front-End and "
     "Back-End'; '## The Front-End: Feature Extractor'; ':5 the Front-End "
     "(also called the Feature Extractor or the convolutional base)') plus "
     "'04. Training, Transfer Learning, and PyTorch/01. Transfer Learning "
     "and Fine-Tuning.md' ('.features (convolutional base)')."),
    "exploding gradient problem": ("cover",
     "dedicated treatments exist in BOTH vaults: master-ai '04 - Neural "
     "Networks/Training/08 - Vanishing and Exploding Gradients.md' "
     "('### Exploding gradient'), ai-course '04 - Neural Networks and Deep "
     "Learning Foundations/04.3 - Training Dynamics and Stability/03. The "
     "Vanishing and Exploding Gradient Problems.md' (dedicated note, '# "
     "15.' title) and '07 - Sequence Models and RNNs/07.1 - Motivation "
     "and Recurrence/04. The Vanishing and Exploding Gradient Problem in "
     "RNNs.md' (RNN-specific dedicated note) plus '02. Weight "
     "Initialization Techniques.md' ('#### The Exploding Gradient "
     "Problem')."),
    "input spatial": ("cover",
     "definitional treatments exist: ai-course '05 - Convolutional Neural "
     "Networks (CNN)/02. Core Operators and Geometry/01. The Convolution "
     "Operation Deep Dive.md:240' ('$W$ = input spatial dimension' in the "
     "output-size formula legend), the dedicated '05. The Output Spatial "
     "Dimension Formula.md' ('# 2.1 The Output Spatial Dimension Formula') "
     "and '05 - Convolutional Neural Networks (CNN)/05. Pipeline, "
     "Evaluation, and Interpretability/04. Exercises Solved and "
     "Explained.md:30' ('$W$ is the input spatial dimension (width or "
     "height)')."),
    "pth'": ("cover",
     "the .pth checkpoint/state_dict concept has dedicated definitional "
     "treatment: ai-course '05 - Convolutional Neural Networks (CNN)/04. "
     "Training, Transfer Learning, and PyTorch/03. PyTorch Advanced - "
     "VGG16 and Pre-trained Models.md' ('## 7. model.state_dict(): Saving "
     "and Loading' :543; '### 7.1 What is a state_dict?' :545; definition "
     ":547; 'checkpoint_weights.pth' inside the defining code) plus "
     "'06. Chapter Summaries (Aggregated)/04. VGG and Classic "
     "Architectures - Summary.md:1424' ('A model's state_dict is a "
     "standard Python dictionary that maps each parameter layer to its "
     "corresponding tensor weights'). Distinguished from the batch-8 "
     "'csv' reject, which had no definitional treatment anywhere."),
    "representational capacity": ("cover",
     "direct definitional treatment of the exact phrase exists: ai-course "
     "'04 - Neural Networks and Deep Learning Foundations/04.3 - Training "
     "Dynamics and Stability/04. Hyperparameters and Network "
     "Configuration.md:15' ('The number of filters in a convolutional "
     "layer directly determines the representational capacity of that "
     "layer') plus '04.1 - Neural Network Basics/08. Data Preparation and "
     "MLP Implementation.md:174' ('determines model capacity'), '04.3/06. "
     "Dropout and Regularization.md:33' (degrees-of-freedom rationale), "
     "'05 - CNN/02. Core Operators and Geometry/02. The Mathematics of "
     "Receptive Fields and 1x1 Convolutions.md:277' ('The bottleneck does "
     "reduce the representational capacity') and master-ai '04 - Neural "
     "Networks/Foundations/01 - Perceptrons and MLPs.md:306' (MoE capacity "
     "at fixed inference cost)."),
    "attention layer": ("cover",
     "definitional treatments exist: master-ai '06 - Attention "
     "Mechanisms/Self-Attention/04 - Self-Attention.md:51' ('The "
     "projections give the model $3d^2$ learnable parameters per "
     "attention layer'), real headings '### Full Attention Layers' "
     "(master-ai '26 - Papers/2024-2026/30 - Kimi Linear 2025.md:62') and "
     "'### 4. Gated Cross-Attention Layers' (master-ai '26 - "
     "Papers/Multimodal/37 - Flamingo 2022.md:61'), and the "
     "attention-per-layer ratio treatments at master-ai '26 - "
     "Papers/2024-2026/30 - Kimi Linear 2025.md:42' and '41 - Jamba "
     "2024.md:192'."),
    "bert 2018": ("cover",
     "dedicated paper note exists: master-ai '26 - Papers/Transformers/03 "
     "- BERT 2018.md' ('# 03' title; pretrain-finetune paradigm per the "
     "papers MOC :18), plus master-ai '05 - NLP Fundamentals/Embeddings/"
     "06 - Contextual Embeddings ELMo to BERT.md' (dedicated note) and "
     "'07 - Transformers/Encoder Models/07 - BERT.md' ('## BERT Family' "
     ":64)."),
    "main path": ("cover",
     "definitional treatments exist: ai-course '05 - Convolutional Neural "
     "Networks (CNN)/03. Architecture and Connectivity/08. The "
     "Degradation Problem and Residual Connections.md' ('pushing the "
     "weights of the convolutions in the main path toward zero' :132; "
     "'the main path output $F(x)$' :351) and '04 - Neural Networks and "
     "Deep Learning Foundations/04.1 - Neural Network Basics/03. "
     "Artificial Neural Networks (ANN) - Comprehensive.md:813' ('Even if "
     "main path has vanishing gradients, skip path preserves them')."),
    "open-weights llm": ("cover",
     "dedicated treatments exist: master-ai '10 - Model Architecture "
     "Research/Open Source/03 - Llama Family Architecture.md' ('### Open "
     "Weights Enabled Adoption'; 'Standardized open-weights LLM design' "
     ":156), '05 - Qwen Family Architecture.md' ('China's leading "
     "open-weights LLM' :11) and the Closed Source comparisons "
     "('## How This Compares to Open-Weights' in '07 - GPT-4 Inferred "
     "Architecture.md')."),
    "pointwise": ("cover",
     "definitional treatments exist: ai-course '05 - Convolutional Neural "
     "Networks (CNN)/03. Architecture and Connectivity/05. Evolution of "
     "CNN Architectures.md:264' ('Pointwise convolution (1×1): Apply a "
     "$1 \\times 1 \\times C_{\\text{in}} \\times C_{\\text{out}}$ "
     "convolution to mix channels'), the dedicated 1×1 note '02. The "
     "Mathematics of Receptive Fields and 1x1 Convolutions.md' ('## 1×1 "
     "Convolutions: Why They Seem Useless and What They Actually Do' "
     ":223; '### Cross-Channel Mixing' :229), '07. Inception "
     "Architecture Deep Dive.md:27' and '06. Chapter Summaries "
     "(Aggregated)/04. VGG and Classic Architectures - Summary.md' "
     "('#### 2. Pointwise Convolution')."),
    "relu activations": ("cover",
     "dedicated treatments exist: master-ai '04 - Neural Networks/"
     "Foundations/02 - Activation Functions.md' ('## The ReLU Family'; "
     "'### ReLU (Rectified Linear Unit)') and ai-course '04 - Neural "
     "Networks and Deep Learning Foundations/04.1 - Neural Network "
     "Basics/01. Fundamentals of Neural Networks.md' ('### 2. ReLU "
     "(Rectified Linear Unit)'), plus the Kaiming/He rule table at "
     "'04.3/02. Weight Initialization Techniques.md:57' ('Kaiming (He) "
     "Normal | ReLU activations')."),
    "tokens per parameter": ("cover",
     "definitional treatments exist: master-ai '26 - Papers/2024-2026/42 "
     "- Scaling Laws (Kaplan and Chinchilla).md:11' ('the optimal ratio "
     "is ~20 tokens per parameter, not ~5'), '11 - Training/Pretraining/"
     "01 - Pretraining Objectives and Scaling Laws.md' ('### Chinchilla "
     "(Hoffmann et al., 2022) — The Corrective'; 'compute-optimal "
     "training uses ~20 tokens per parameter' :135) and '11 - Training/"
     "Data/03 - Data Pipelines and Deduplication.md:16' ('you need ~20 "
     "tokens per parameter')."),
    "utf-8": ("cover",
     "in-situ definitional treatment exists: master-ai '05 - NLP "
     "Fundamentals/Tokenization/02 - BPE.md:261' ('UTF-8 encodes every "
     "Unicode codepoint as a sequence of 1-4 bytes. There are exactly 256 "
     "possible byte values (0x00 to 0xFF)') plus '## Byte-Level BPE' "
     "(:49), '04 - SentencePiece.md:174-176' (byte-fallback: 'If a "
     "character isn't in the vocab, decompose it into UTF-8 bytes') and "
     "'01 - Tokenization Overview.md:159' (multi-byte UTF-8 sequences, "
     "the non-English tax). What UTF-8 IS is defined in-situ — not a gap."),
    "12 fine-tuning": ("cover",
     "chapter-level treatment exists: master-ai '12 - Fine-Tuning' "
     "chapter (MOC plus DPO/RLHF/PEFT/Instruction Tuning notes; "
     "'PEFT/01 - LoRA.md' dedicated note), wikilinked from master-ai '01 "
     "- AI Foundations/04 - The Modern AI Stack.md:70' and '06 - Map of "
     "the Field.md' (:103,:126; 'chapter 12 (Fine-Tuning)' prose :161). "
     "Batch-8 chapter-fragment precedent ('13 inference')."),
    "direct preference": ("cover",
     "fragment of 'Direct Preference Optimization': dedicated treatments "
     "master-ai '12 - Fine-Tuning/DPO/04 - DPO Derivation.md' (TL;DR "
     "definition :11 'Direct Preference Optimization (Rafailov et al., "
     "2023) simplifies RLHF') and the dedicated paper note '26 - "
     "Papers/Alignment/09 - DPO 2023.md'."),
    "direct preference optimization": ("cover",
     "dedicated treatments exist: master-ai '12 - Fine-Tuning/DPO/04 - "
     "DPO Derivation.md' (TL;DR definition :11; full derivation note) "
     "and master-ai '26 - Papers/Alignment/09 - DPO 2023.md' (dedicated "
     "paper note with alias 'Direct Preference Optimization')."),
    "output tensor": ("cover",
     "definitional treatments exist: ai-course '05 - Convolutional Neural "
     "Networks (CNN)/01. Foundations and Philosophy/02. Core Architecture "
     "and Philosophy.md:182' ('the network produces a 3D output tensor. "
     "Let us say this tensor has dimensions $H' \\times W' \\times C'$'), "
     "'05. Processing 3D Volumes, Depth Summation, and Biases.md:144' "
     "('**Output Tensor:** [Batch: 32, Channels: 128, Height: 62, Width: "
     "62]') and '06. Chapter Summaries (Aggregated)/02. Core Operators "
     "and Geometry - Summary.md' ('### Final Output Tensor' :191)."),
    "preference pairs": ("cover",
     "definitional treatments exist: master-ai '12 - Fine-Tuning/DPO/04 - "
     "DPO Derivation.md:58' ('The reward model is trained on preference "
     "pairs $(y_w, y_l)$ (winner, loser) using the Bradley-Terry model'), "
     "'26 - Papers/Alignment/09 - DPO 2023.md:77' ('binary classification "
     "loss on preference pairs'), '01 - AI Foundations/04 - The Modern AI "
     "Stack.md:42' and '12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md:105'."),
    "previous-token": ("cover",
     "definitional treatments exist: master-ai '06 - Attention "
     "Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md:86' "
     "('**Previous-token heads** — always attend to position $t-1$'), "
     "'08 - LLMs/Capabilities/04 - In-Context Learning.md:151' "
     "(induction-head circuit step 1) and '14 - Interpretability/"
     "Mechanistic/01 - Mechanistic Interpretability.md:266'."),
    "retrieval-augmented generation": ("cover",
     "dedicated chapter exists: master-ai '17 - RAG/' with 'Ingestion and "
     "Retrieval/01 - RAG Pipeline Overview.md:12' (TL;DR definition 'A "
     "RAG (Retrieval-Augmented Generation) pipeline retrieves relevant "
     "documents from a knowledge base'), the paper note '26 - "
     "Papers/Agents and RAG/35 - RAG 2020.md' and the '08 - LLMs/"
     "Limitations/05 - Hallucination.md' section ('### "
     "Retrieval-Augmented Generation (RAG)')."),
    "running stats": ("cover",
     "dedicated note covers the concept: ai-course '04 - Neural Networks "
     "and Deep Learning Foundations/04.3 - Training Dynamics and "
     "Stability/05. Batch Normalization.md' ('# 2. Uses the running_mean "
     "and running_var saved during training' :192; 'EMA momentum for "
     "running stats update' :284; train/eval table :506) plus '05 - "
     "Convolutional Neural Networks (CNN)/04. Training, Transfer "
     "Learning, and PyTorch/03. PyTorch Advanced - VGG16 and "
     "Pre-trained Models.md:103' ('The running statistics are a better "
     "estimate of the population statistics')."),
    "source sentence": ("cover",
     "definitional treatments exist: master-ai '04 - Neural Networks/"
     "Architectures/05 - Seq2Seq and the Information Bottleneck.md' "
     "(dedicated note; 'The entire source sentence must pass through "
     "$\\mathbf{c}$' :45; 'reverse the source sentence' :163), '06 - "
     "Attention Mechanisms/Origins/01 - Origins of Attention.md:18' "
     "('An **encoder RNN** (LSTM/GRU) reads the source sentence word by "
     "word') and '26 - Papers/Attention Origins/01 - Bahdanau Attention "
     "2014.md:11'."),
    "stride-2": ("cover",
     "definitional treatments exist: ai-course '04 - Neural Networks and "
     "Deep Learning Foundations/04.3 - Training Dynamics and Stability/"
     "04. Hyperparameters and Network Configuration.md:89' ('**Stride-2 "
     "convolutions as an alternative to pooling**'), the dedicated note "
     "'05 - Convolutional Neural Networks (CNN)/02. Core Operators and "
     "Geometry/07. Strides - Skipping Pixels and Downsampling.md' ('# "
     "2.3 Strides: Skipping Pixels and Downsampling') and '02. The "
     "Mathematics of Receptive Fields and 1x1 Convolutions.md:76' "
     "(receptive-field jump doubling)."),
    "unnormalized": ("cover",
     "definitional treatment exists: ai-course '03 - Machine Learning/"
     "03.2 - Optimization Algorithms/08. Loss Functions and Optimizers "
     "Deep Dive.md:22' ('**Softmax**: Converts the raw logits "
     "(unnormalized scores) output by the model into a probability "
     "distribution over the $C$ classes') plus the logits shape table at "
     "master-ai '02 - Mathematics/Linear Algebra/06 - Tensors and "
     "Broadcasting.md:328-329' ('Logits | (B, N, V) | V = vocab size')."),
    "value function": ("cover",
     "definitional treatments exist: master-ai '03 - Machine Learning/"
     "Reinforcement Learning/09 - Policy Gradients and Actor Critic.md'"
     "(':11 combine a policy (\"actor\") with a value function "
     "(\"critic\")'), '07 - MDPs and Bellman Equations.md' ('### 3. "
     "Actor-Critic (A2C, A3C, PPO)'; :120) and '10 - PPO Deep "
     "Treatment.md:66' ('**Value function loss** $L^{\\text{VF}} = "
     "(V_\\theta(s_t) - G_t)^2$')."),
    "additive attention": ("cover",
     "definitional treatments exist: master-ai '06 - Attention "
     "Mechanisms/Origins/02 - Bahdanau Attention.md:40' ('This is called "
     "**additive attention** because it combines the two vectors through "
     "a sum inside the $\\tanh$'), '03 - Luong Attention.md:12' "
     "(additive-to-multiplicative simplification) and '01 - Origins of "
     "Attention.md:125'."),
    "chapter 07": ("cover",
     "chapter-level treatment exists: ai-course '07 - Sequence Models and "
     "RNNs' chapter ('00. Chapter Overview.md' plus subfolders 07.1-07.4 "
     "with dedicated notes), the referent of the prose mentions ('This is "
     "the most important note in Chapter 07' at '07.4 - Sequence Modeling "
     "Pitfalls and Limits/01. The Bottleneck Problem - Why One Vector Is "
     "Not Enough.md:6'; 'This is the last note in Chapter 07' at "
     "'03. From RNNs to Attention - The Historical Bridge.md:6'). "
     "Batch-8 chapter-fragment precedent ('13 inference')."),
    # ---------------- rejects (25) ----------------
    "academic dl": ("reject",
     "Non-concept noise (vault-management source-taxonomy label): "
     "'Academic DL' is a source-folder name from the original course "
     "vault; appears in exactly ONE file corpus-wide (ai-course "
     "README.md, 52 occurrences, e.g. :390, :560, :762) as "
     "folder-mapping documentation."),
    "academic ml": ("reject",
     "Non-concept noise (vault-management source-taxonomy label): "
     "'Academic ML' is a source-folder name; README-only (ai-course "
     "README.md, 41 occurrences, e.g. :507, :735, :785, :809)."),
    "default'": ("reject",
     "Non-concept noise (markup artifact): the Python string literal "
     "'DEFAULT' in models.vgg16_bn(weights='DEFAULT') code; the meaning "
     "is explained in-situ at the use sites (ai-course '05 - "
     "Convolutional Neural Networks (CNN)/04. Training, Transfer "
     "Learning, and PyTorch/03. PyTorch Advanced - VGG16 and "
     "Pre-trained Models.md:27' plus the :32-38 comments), but unlike "
     "'pth''s state_dict there is no dedicated definitional section — "
     "code-comment treatment only."),
    "globally": ("reject",
     "Non-concept noise (adverb): 'install Python globally' (Virtual "
     "Environments :11), 'globally mapped' (Local Connectivity :9), "
     "'Globally, there might be more Crocodiles' (KNN :550); 13 homonym "
     "clusters; no unified concept."),
    "lesson": ("reject",
     "Non-concept noise (generic noun): '[!IMPORTANT] Lesson from this "
     "Exercise' callouts (KNN :267), 'The FC bottleneck lesson' (VGG16 "
     "Deep Dive :888), 'training recipe lesson' phrasing; 11 homonym "
     "clusters; the pedagogical content is preserved in its host notes."),
    "bn1": ("reject",
     "Non-concept noise (code identifier): self.bn1 = nn.BatchNorm2d "
     "attribute names in ResNet block code (ai-course '08. The "
     "Degradation Problem and Residual Connections.md:262' and '09. "
     "ResNet Bottleneck Blocks and Architectural Variants.md:241'); the "
     "BatchNorm concept itself is covered by the dedicated '05. Batch "
     "Normalization.md' note and master-ai '03 - Machine "
     "Learning/Generalization/06 - Regularization Techniques.md'."),
    "bn2": ("reject",
     "Non-concept noise (code identifier): self.bn2 = nn.BatchNorm2d "
     "(ai-course '08. The Degradation Problem and Residual "
     "Connections.md:278', '09. ResNet Bottleneck Blocks and "
     "Architectural Variants.md:253'); same treatment as bn1."),
    "demonstrating": ("reject",
     "Non-concept noise (gerund): 'demonstrating that scale...' "
     "(Evolution of DL :59), 'Example demonstrating the difference' "
     "(Metrics :185), '# ...demonstrating that skip connections' (code "
     "comment, Vanishing/Exploding :627); 9 homonym clusters."),
    "gen": ("reject",
     "Non-concept noise (multi-sense fragment): LaTeX loss subscript "
     "$\\mathcal{L}_{\\text{gen}}$ (Normalization Summary :14), mermaid "
     "node label 'mask gen' (Vision Foundation Models :146), 'Hopper Gen "
     "| Ampere Gen' GPU table columns (GPU Infrastructure :17), 'async "
     "def gen()' generator function (Production AI Stack :365), "
     "get_squares_gen iterator helper; 7 homonym clusters; no unified "
     "concept."),
    "records": ("reject",
     "Non-concept noise (generic noun): 'records' as data rows, DNS "
     "records, log records, medical records across both vaults; the "
     "specific technical senses are preserved in their host notes."),
    "degrees": ("reject",
     "Non-concept noise (generic multi-sense noun): rotation angles "
     "(RandomRotation(degrees=15), Data Augmentation :104), degrees of "
     "freedom (Dropout and Regularization :33), hue/temperature senses; "
     "9 homonym clusters; every technical sense is covered in-situ by "
     "its host note."),
    "tool's": ("reject",
     "Non-concept noise (generic possessive): 'the tool's schema' "
     "(Hallucination :194), 'the tool's output' (ReAct :50), 'the tool's "
     "parameter descriptions' (Function Calling :462); the tool-calling "
     "concepts are covered by the dedicated master-ai '15 - AI Agents/"
     "Tool Calling/04 - Function Calling.md' note."),
    "transformed": ("reject",
     "Non-concept noise (past participle): 'the gradient is transformed "
     "in a specific way' (CNN backprop :549), 'transformed into a "
     "probability distribution' prose; 9 homonym clusters; the "
     "underlying transform content is preserved in its host notes."),
    "uses running": ("reject",
     "Non-concept noise (verb-phrase fragment): code comments such as "
     "'BatchNorm uses running stats' / 'eval uses running BN stats' "
     "(Batch Normalization :506, PyTorch Advanced, Core Architecture "
     ":233); the underlying running-statistics concept is covered by "
     "this same tranche's 'running stats' cover decision."),
    "arbitrarily": ("reject",
     "Non-concept noise (adverb): 'arbitrarily large datasets' (Linear "
     "Regression :133), 'the arbitrarily chosen Number of filters' (3D "
     "Volumes :138); 8 homonym clusters."),
    "compressing": ("reject",
     "Non-concept noise (gerund): 'compressing the spatial boundaries' "
     "(Strides :78), 'compressing the channel dimensions' (Bottleneck "
     "Summary :922), 'compress the entire source sentence' (Seq2Seq); 9 "
     "homonym clusters; each technical sense is preserved in-situ."),
    "fake": ("reject",
     "Non-concept noise (generic adjective): 'fake' GAN samples, 'fake "
     "data' quiz phrasing; the GAN real/fake discriminative concept is "
     "covered in-situ by the ai-course '10 - Generative Models/10.3 - "
     "GANs/' notes (e.g. WGAN-GP critic treatment :46)."),
    "limited data": ("reject",
     "Non-concept noise (generic phrase): 'with limited data' transfer "
     "scenarios (Q19 quiz :217, Foundations Summary :874, VGG Summary "
     ":118); the small-data transfer-learning guidance is preserved "
     "in-situ by the dedicated '01. Transfer Learning and Fine-Tuning' "
     "note (:24 comparison table)."),
    "network module": ("reject",
     "Non-concept noise (import-comment artifact): 'import torch.nn as "
     "nn  # Neural network module' comments inside code fences (ai-course "
     "'03.2 - Optimization Algorithms/08. Loss Functions and Optimizers "
     "Deep Dive.md:88,144', '03.6 - Model Evaluation/02. Model "
     "Evaluation Metrics Beyond Accuracy.md:310', '04.3/01. Weight "
     "Initialization.md:629'); corpus-wide the phrase occurs only in "
     "import comments; the PyTorch nn module usage is preserved in the "
     "code."),
    "neural network module": ("reject",
     "Non-concept noise (import-comment artifact): same evidence as "
     "'network module' — the phrase occurs only inside 'import torch.nn "
     "as nn' code comments; no standalone concept to cover."),
    "substituting": ("reject",
     "Non-concept noise (gerund in derivations): 'Substituting (1 - "
     "a_i^2) into our Grand Formula' (Notation :139), 'Substituting the "
     "line equation' (Linear Regression :70), 'substituting $\\hat{y} = "
     "\\sigma(wX + b)$' (Logistic Regression :135); 14 derivation "
     "usages, 8 homonym clusters; the derivations themselves are "
     "preserved in their host notes."),
    "sso": ("reject",
     "Non-concept noise (peripheral enterprise-infrastructure "
     "integration term): 18 word-boundary occurrences across 3 notes "
     "(master-ai '16 - Multi-Agent Systems/Enterprise/04 - Enterprise "
     "Multi-Agent Architectures.md' :35,:93; '19 - MCP/Integration/04 - "
     "MCP Enterprise Integration.md' :60,:78,:163,:319,:379; '27 - "
     "Projects/Capstones/18 - Build an MCP Marketplace.md:372'); "
     "'single sign-on' spelled out: zero corpus-wide. The identity/auth "
     "role is explained in-situ at every use site ('Integrates with "
     "enterprise SSO (Okta, Azure AD, etc.). Maps users to tenants, "
     "roles, and permissions'; gateway 'Authenticates clients (OAuth "
     "2.0, SSO integration)') and no derivation or required code "
     "comprehension depends on a formal SSO definition — unlike async "
     "def (syntax pervading code the reader must parse), SSO is a "
     "mention-level integration point. Adjudicated reject, not a "
     "confirmed gap (subagent cross-check agreed)."),
    "100x": ("reject",
     "Non-concept noise (numeric-magnitude artifact): '10x to 100x "
     "faster than standard Python lists' (NumPy :13), 'an outlier 100x "
     "larger than expected' (Loss Functions :16), '100x smaller' "
     "learning rate comment (Transfer Learning :332); 4 homonym "
     "clusters."),
    "cameras": ("reject",
     "Non-concept noise (generic noun): surveillance cameras (Data "
     "Augmentation :160), digital cameras (Image Representation :21), "
     "camera feeds (Applications :72); 6 homonym clusters; the imaging "
     "content is preserved in its host notes."),
    "command": ("reject",
     "Non-concept noise (generic noun): 'A loop command' sigma metaphor "
     "(Mathematical Notation :79), 'Command Prompt on Windows' "
     "(Installation :39), 'Add Python to PATH' from any command prompt "
     "(:13); 8 homonym clusters; the CLI setup content is preserved "
     "in-situ."),
}


def main() -> int:
    selected = json.loads(SELECTED.read_text())
    id2term = {s["candidate_id"]: s["term"] for s in selected}
    if len(selected) != 60:
        raise SystemExit(f"expected 60 selected candidates, got {len(selected)}")

    missing = [t for t in id2term.values() if t not in DECISIONS_BY_TERM]
    extra = [t for t in DECISIONS_BY_TERM if t not in id2term.values()]
    if missing or extra:
        raise SystemExit(f"decision-map mismatch: missing={missing} extra={extra}")

    lines = []
    for i, s in enumerate(selected, 1):
        term = s["term"]
        action, rationale = DECISIONS_BY_TERM[term][:2]
        rec = {
            "candidate_id": s["candidate_id"],
            "decision_id": f"D-DISC002-B9-{i:04d}",
            "action": action,
            "rationale": rationale,
            "reviewer": R,
        }
        lines.append(json.dumps(rec, ensure_ascii=False, sort_keys=True))

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    n_cover = sum(1 for t in DECISIONS_BY_TERM.values() if t[0] == "cover")
    n_reject = sum(1 for t in DECISIONS_BY_TERM.values() if t[0] == "reject")
    n_gap = sum(1 for t in DECISIONS_BY_TERM.values() if t[0] == "confirm_gap")
    n_merge = sum(1 for t in DECISIONS_BY_TERM.values() if t[0] == "merge")
    print(f"wrote {len(lines)} decisions to {OUT}")
    print(f"cover={n_cover} reject={n_reject} confirm_gap={n_gap} merge={n_merge}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
