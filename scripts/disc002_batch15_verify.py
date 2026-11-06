#!/usr/bin/env python3
"""Targeted corpus verification for batch-15 cover/reject citations.

Prints exact line numbers for each claimed locator so the rationales carry
machine-resolvable citations (vault-relative paths with line numbers).

Fence-aware by construction: every check is matched against content lines,
and heading checks are additionally verified against the authoritative
mdextract heading list, so a Python comment inside a code fence can no
longer pass as a heading citation.

LEVEL-EXACT HEADING DISCIPLINE (new in batch 15, per the session-14
'^#+' blind-spot lesson and the session-14 checkpoint recommendation):
every require_heading=True check MUST use a level-exact pattern of the
form '^### ' (1-6 literal '#' followed by a space) — the batch-14
require_heading patterns used '^#+', which matches ANY heading level and
let exact-level citation slips pass (nine flagged errata in session 14).
This script REJECTS any require_heading pattern that is not level-exact
(guard at startup), and a '^### Foo' pattern cannot match a '## Foo' or
'#### Foo' line by regex construction, so a level mismatch now FAILS
loudly.

Session-13/14/15 lessons applied: heading LEVELS checked exactly (## vs
### vs ####), note titles that differ from filenames (the padding note's
title is '# 2.2 Padding: Mathematics, Edge Effects, and Valid vs. Same'
though the FILE is '06. Padding - Mathematics, Edge Effects, and Valid
vs Same.md'), **bold** markers inside patterns, term-separated
definitions, the glossary indexes checked before any acronym-absence
claim, and regex-vs-LaTeX escaping (in a regex, \\t means TAB and \\c is
a bad escape — literal '\\times'/'\\vdots' need '\\\\times'/'\\\\vdots'
inside patterns; \\* is needed for literal asterisks; in-fence '#'
comments like the Mini Agent's '# Web search' are checked as LINES, not
headings).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402

VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

# (vault, path, pattern, note, require_heading)
# require_heading=True additionally asserts the matched line is a REAL
# heading per the authoritative fence-aware mdextract extraction, AND the
# pattern must be LEVEL-EXACT ('^### ...', never '^#+ ...').
LEVEL_EXACT_RE = re.compile(r"^#\ #{1,6}\ ?")  # placeholder, real guard below

CHECKS = [
    # --- covers: class index family (#4) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"^### 7\.1 Input Format: Raw Logits \(NOT Softmax Probabilities\)", "logits input format heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"where \$x\$ is the vector of logits and \$y\$ is the correct class index\.", "class index symbol gloss", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"^### 7\.2 Target Format: Integer Class Indices \(NOT One-Hot Vectors\)", "class indices target format heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"The second argument should be a 1D tensor of \*\*integer class indices\*\* in the range", "class indices definition", False),
    # --- covers: output spatial size family (#30) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"^# 2\.1 The Output Spatial Dimension Formula", "output spatial formula note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"\$\$O = \\left\\lfloor \\frac\{W - K \+ 2P\}\{S\} \\right\\rfloor \+ 1\$\$", "master spatial formula", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"^#### \$O\$ — Output Size", "output size variable heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/05. The Output Spatial Dimension Formula.md", r"The final resulting dimension length along the axis being computed", "output size definition", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"^### How Stride Affects Output Size", "stride output size heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/06. Padding - Mathematics, Edge Effects, and Valid vs Same.md", r"^### Same Padding \(The \"Half\" Formula\)", "same padding half formula heading", True),
    # --- covers: vlm backbone family (#49) ---
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"^### Vision-Language Model Backbone", "colpali vlm backbone heading", True),
    ("master-ai", "26 - Papers/Multimodal/48 - ColPali 2024.md", r"— VLM backbone; ColPali uses similar vision\+language fusion", "colpali blip2 vlm backbone ref", False),
    ("master-ai", "23 - Multimodal AI/Vision-Language/01 - Multimodal AI Overview.md", r"^## Vision-Language Models", "vision-language models heading", True),
    ("master-ai", "07 - Transformers/Encoder Models/07 - BERT.md", r"^## BERT as Embedding Backbone", "bert embedding backbone heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"^### Freezing the Backbone for Feature Extraction", "freezing backbone heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"ResNet-50 is the most widely used backbone for transfer learning in computer vision", "resnet50 backbone transfer learning", False),
    # --- covers: memories family (#51) ---
    ("master-ai", "07 - Transformers/Components/05 - Feed-Forward Network Deep.md", r"^### 1\. It's where knowledge is stored", "ffn knowledge stored heading", True),
    ("master-ai", "07 - Transformers/Components/05 - Feed-Forward Network Deep.md", r"FFNs act as \*\*key-value memories\*\*", "ffn key-value memories", False),
    ("master-ai", "18 - Memory Systems/Operations/03 - Memory Operations.md", r"Agent memory is not a passive store — it is an active system with operations", "memory operations tldr", False),
    ("master-ai", "18 - Memory Systems/Types/01 - Memory Types.md", r"namespace memories per user", "memory types namespace", False),
    # --- covers: pre-trained model family (#53) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"you begin with a model that has already learned useful representations from a large dataset", "pretrained model definition", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"You take the pre-trained convolutional base", "pretrained base feature extraction", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"Wrong Normalization = Broken Pre-Trained Model", "broken pretrained model warning", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md", r"the pre-trained weights, which are already in a good region of the loss landscape", "pretrained weights loss landscape", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"Most pre-trained model repositories \(PyTorch Hub, TensorFlow Hub, timm\)", "pretrained model repositories", False),
    # --- covers: preference data family (#54) ---
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"It directly optimizes the policy from preference data via a closed-form loss", "dpo preference data tldr", False),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"Train a \*\*reward model\*\* \$r_\\phi\(x, y\)\$ on preference data", "dpo reward model on preference data", False),
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"The reward model is trained on preference pairs \$\(y_w, y_l\)\$ \(winner, loser\) using the Bradley-Terry model", "preference pairs format definition", False),
    ("master-ai", "12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md", r"train a reward model on preference data, then use PPO to optimize the policy", "rlhf preference data pipeline", False),
    ("master-ai", "12 - Fine-Tuning/RLHF/05 - RLHF with PPO.md", r"scores how good a response \$y\$ is for a prompt \$x\$, based on human preferences", "reward model human preferences", False),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"\*\*Reward modeling\*\* requires a separate training run on preference data", "dpo2023 reward modeling preference data", False),
    # --- covers: mamba-2 family (#55) ---
    ("master-ai", "24 - Research Frontiers/State Space Models/02 - Mamba-2 and Structured Attention.md", r"^# 02 — Mamba-2 and Structured State Space Duality", "mamba-2 ssd note title", True),
    ("master-ai", "26 - Papers/2024-2026/45 - Mamba-2 2024.md", r"^## The Key Idea: Structured State Space Duality \(SSD\)", "mamba-2 ssd key idea heading", True),
    ("master-ai", "24 - Research Frontiers/State Space Models/01 - SSMs Mamba and Frontiers.md", r"^### Mamba-2 \(Dao & Gu, 2024\)", "mamba-2 dao gu heading", True),
    ("master-ai", "10 - Model Architecture Research/Open Source/09 - MiniMax 3 Architecture.md", r"different from Mamba-2's SSD and from Kimi Linear's hybrid", "minimax mamba-2 ssd attribution", False),
    ("master-ai", "24 - Research Frontiers/Hybrid Architectures/03 - RWKV and RetNet.md", r"later formalized by Mamba-2's SSD", "rwkv retnet mamba-2 ssd", False),
    ("master-ai", "10 - Model Architecture Research/2026 Frontier Model Synthesis.md", r"Mamba-2's SSD framework", "frontier synthesis mamba-2 ssd", False),
    # --- covers: rule-based family (#56) ---
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"Not all AI is ML \(rule-based systems are AI but not ML\)", "rule-based ai not ml", False),
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"^### Use Symbolic AI \(Rules\) When:", "use symbolic ai rules heading", True),
    ("master-ai", "01 - AI Foundations/02 - AI vs ML vs DL vs GenAI vs Agentic AI.md", r"all DL is ML; all ML is AI", "containment framing", False),
    ("master-ai", "22 - Production AI/Security/05 - PII and Data Leakage.md", r"^### Rule-Based Detection", "rule-based detection heading", True),
    ("master-ai", "26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md", r"the verifier is rule-based", "rlvr rule-based verifier", False),
    ("master-ai", "27 - Projects/Capstones/20 - Build an RLHF Pipeline with PPO.md", r"the reward is a rule-based verifier \(math grader, test runner\)", "capstone rule-based verifier", False),
    # --- covers: web search family (#57) ---
    ("master-ai", "15 - AI Agents/Reasoning/03 - ReAct Pattern.md", r"If it needs fresh information \(a calculation, a web search, a database query\), it's stuck", "react fresh information limitation", False),
    ("master-ai", "27 - Projects/Mini-Projects/03 - Build a Mini Agent.md", r"an LLM, two tools \(web search \+ calculator\), a tool-call loop", "mini agent tool set", False),
    ("master-ai", "27 - Projects/Mini-Projects/03 - Build a Mini Agent.md", r"Calls tools \(web search, calculator\) with appropriate arguments", "mini agent calls tools", False),
    ("master-ai", "27 - Projects/Mini-Projects/03 - Build a Mini Agent.md", r"^# Web search$", "mini agent web search section (in-fence comment, LINE check)", False),
    ("master-ai", "15 - AI Agents/Reasoning/03 - ReAct Pattern.md", r"ReAct works with any tool: web search, code execution, database queries", "react tool-agnostic list", False),
    ("master-ai", "19 - MCP/Components/02 - MCP Components.md", r"Dynamic data retrieval \(database queries, API calls, web search\)", "mcp dynamic data retrieval", False),
    # --- covers: output node family (#58) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/01. Fundamentals of Neural Networks.md", r"^### 3\. Output Node", "output node heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/01. Backpropagating to the Output Layer.md", r"^# 7\. Backpropagating to the Output Layer", "backprop output layer note title", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/01. Backpropagating to the Output Layer.md", r"the error at the output node before the weight was applied", "output node error definition", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule and Convergence.md", r"is exactly the same for all parameters connected to this output node", "output node gradient reuse", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"Because the output layer node combines all parameters to form the prediction", "output layer node shortcut", False),
    # --- covers: chat template family (#59) ---
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"^# 03 - Instruction Tuning and Chat Templates", "instruction tuning chat templates note title", True),
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"^### ChatML \(used by many models, including Qwen, some Mistral\)", "chatml heading", True),
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"What is a chat template and why does using the wrong one cause silent quality loss\?", "chat template qa", False),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"Chat template markers \(ChatML, etc\.\)", "chat template markers gloss", False),
    ("master-ai", "05 - NLP Fundamentals/Tokenization/01 - Tokenization Overview.md", r"The choice of chat template and special tokens is a major part of \*\*instruction tuning\*\*", "chat template choice", False),
    ("master-ai", "25 - Frameworks and Tools/Serving/12 - TGI.md", r"^### Chat Template Support", "tgi chat template support heading", True),
    # --- covers: paging family (#60) ---
    ("master-ai", "26 - Papers/Efficient Attention/10 - PagedAttention vLLM 2023.md", r"^## The Key Idea: Paging the KV Cache", "paging the kv cache heading", True),
    ("master-ai", "13 - Inference/KV Cache/02 - PagedAttention.md", r"^# PagedAttention", "pagedattention note title", True),
    ("master-ai", "08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md", r"^### PagedAttention \(vLLM\)", "kv mechanics pagedattention heading", True),
    ("master-ai", "08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md", r"Without paging: each request reserves a contiguous block of memory for its worst-case sequence length", "paging without/with contrast", False),
    ("master-ai", "08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md", r"PagedAttention achieves 2-4× higher throughput than non-paged KV cache management", "pagedattention throughput", False),
    ("master-ai", "13 - Inference/Serving/06 - Continuous Batching Deep Dive.md", r"Without paging, you must reserve worst-case memory per request", "continuous batching paging", False),
    ("master-ai", "25 - Frameworks and Tools/Serving/12 - TGI.md", r"the paging-based KV cache memory management that vLLM pioneered", "tgi paging-based kv cache", False),
    # --- rejects: backpropagation computes family (#1) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/05. Derivatives, Power Rule, and the Chain Rule.md", r"Backpropagation computes the compass direction", "compass direction metaphor", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"Backpropagation computes the compass direction", "compass direction metaphor rnn", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"backpropagation computes \$\\frac\{\\partial L\}\{\\partial w\}\$ for every parameter", "backprop computes gradients", False),
    # --- rejects: vault-management meta-prose family (#2, #9, #18, #19, #22, #25, #29) ---
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"Read each candidate note to identify concrete gaps", "candidate note process", False),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"Expanded each note substantially", "note substantially process", False),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"- Missing sections \(e\.g\., \"Interview Questions\"", "missing sections checklist", False),
    ("master-ai", "00 - Vault Management/Architecture Decisions.md", r"only add, never remove", "never remove rule", False),
    # --- rejects: cheap draft family (#3) ---
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"used as cheap draft models for speculative decoding", "cheap draft models prose", False),
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"^### 1\. Speculative decoding", "ngram speculative decoding heading", True),
    ("master-ai", "13 - Inference/Speculative Decoding/05 - Speculative Decoding.md", r"^## Draft Model Choices", "draft model choices heading", True),
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"Previous speculative decoding required training and serving a draft model", "two-model problem", False),
    # --- rejects: classification networks family (#5) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"covers image classification in depth", "cnn chapter classification coverage", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/08. Modern Computer Vision Tasks/01. Modern Computer Vision Tasks - Detection and Segmentation.md", r"\| \*\*Classification\*\* \| One label per image \|", "classification task table row", False),
    ("master-ai", "04 - Neural Networks/Architectures/03 - CNNs.md", r"Stack 5–50 of these, then a dense head for classification", "cnns dense head classification", False),
    # --- rejects: clear/previous gradients family (#6, #7, #8, #36) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"# Clear previous gradients", "clear previous gradients comment", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"^### 13\.6\.1 `optimizer\.zero_grad\(\)`", "zero_grad heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"gradients are \*added\* to the existing `\.grad` values rather than replacing them", "accumulation default", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/02. Common Mistakes and How to Fix Them.md", r"^## Mistake 1: Forgetting `optimizer\.zero_grad\(\)`", "zero_grad mistake heading", True),
    ("master-ai", "02 - Mathematics/Optimization/12 - Optimization Essentials.md", r"PyTorch accumulates gradients by default\. Always call `opt\.zero_grad\(\)` before", "optimization essentials zero_grad", False),
    # --- rejects: convert pil family (#10) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"randomly crop and resize the image \(augmentation\)", "resnet transform pipeline", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"This must be applied AFTER transforms\.ToTensor\(\) because it operates", "totensor vs pil", False),
    # --- rejects: early stopping triggered family (#11, #43) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"patience_counter \+= 1", "patience counter", False),
    ("master-ai", "03 - Machine Learning/Generalization/06 - Regularization Techniques.md", r"^## Early Stopping", "early stopping heading", True),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"^### 2\.3 Epochs and Early Stopping", "epochs early stopping heading", True),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"for `patience` consecutive epochs, multiply the learning rate by `factor`", "reducelronplateau patience", False),
    # --- rejects: f'epoch artifact family (#12) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"print\(f'Epoch \[\{epoch\+1\}/\{num_epochs\}\], '", "f-string epoch print", False),
    # --- rejects: fine-tuning pre-trained family (#13) ---
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md", r"fine-tuning pre-trained models", "fine-tuning pretrained prose", False),
    ("master-ai", "00 - Vault Management/Master Roadmap.md", r"^## 12 — Fine-Tuning", "roadmap fine-tuning heading", True),
    # --- rejects: global avg pool family (#14, #15) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"^# 6\. Advanced Pooling Mechanisms and Global Average Pooling", "gap note title", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"Global Average Pooling \(GAP\) as a Modern Alternative", "gap modern alternative summary", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"Step 2: Target last conv layer", "gradcam mermaid step", False),
    ("master-ai", "07 - Transformers/Variants/13 - Vision Transformer ViT.md", r"global average pooling works too, but `\[CLS\]` is the ViT default", "vit gap vs cls", False),
    # --- rejects: gpu transfer family (#16) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"Calling `model\.to\('cuda'\)` moves all registered parameters to the GPU", "device management definition", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"\.to\(device\) moves ALL parameters to the GPU", "to device moves all", False),
    # --- rejects: hessian / newton family (#17, #21, #28) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/08. Multivariate Calculus - Jacobians and Hessians.md", r"uses the Hessian for faster convergence, but is infeasible in DL due to the Hessian's", "hessian infeasible prose", False),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"^## The Hessian", "master hessian heading", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/08. Multivariate Calculus - Jacobians and Hessians.md", r"^## The Hessian", "course hessian heading", True),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"Newton's method uses the Hessian to take a more informed step", "newton informed step", False),
    ("master-ai", "02 - Mathematics/Calculus/11 - Jacobians and Hessians.md", r"^## Newton's Method", "newton method heading", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/08. Multivariate Calculus - Jacobians and Hessians.md", r"^### Second-order optimization: Newton's method", "second-order newton heading", True),
    ("master-ai", "02 - Mathematics/Probability/07 - Probability Essentials.md", r"Newton's method uses the Hessian directly", "fisher newton hessian", False),
    # --- rejects: need paired family (#23) ---
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"doesn't need paired preferences — only binary good/bad labels", "kto paired preferences", False),
    # --- rejects: negative error family (#24) ---
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/02. Mathematical Notation and Symbols.md", r"Assume \$E = \\frac\{1\}\{2\}\(Target - Output\)\^2\$", "squared error notation", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"The most intuitive way to calculate the error is a simple subtraction", "error subtraction", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md", r"The error is positive, meaning our guess was too low", "error sign interpretation", False),
    # --- rejects: new fc / new layer family (#26, #27) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"replace the original classifier head with a new, randomly initialized classifier", "replace classifier head", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"Replace the final Linear layer", "replace final linear layer", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md", r"Replace the 1000-class FC with a 10", "replace 1000-class fc", False),
    # --- rejects: overall accuracy family (#31) ---
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"micro-averaged precision, recall, and F1 are all equal to the overall accuracy", "micro equals overall accuracy", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md", r"# Overall accuracy: fraction of correct predictions", "overall accuracy comment", False),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/01. Model Evaluation and Metrics.md", r"^### 1\. Accuracy", "accuracy heading", True),
    ("ai-course", "03 - Machine Learning/03.6 - Model Evaluation/01. Model Evaluation and Metrics.md", r"\$\$Accuracy = \\frac\{TP \+ TN\}\{TP \+ TN \+ FP \+ FN\}", "accuracy formula", False),
    # --- rejects: per-channel means family (#32) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"mean=\[0\.485, 0\.456, 0\.406\], std=\[0\.229, 0\.224, 0\.225\]", "imagenet per-channel stats", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"^### Why Per-Channel Normalization\?", "per-channel normalization heading", True),
    # --- rejects: pool gradients family (#33) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"the gradient flows \*\*only to the element that was the maximum\*\*", "max pool backward routing", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"How max pooling routes gradients", "max pooling routes comment", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"\| Max pool gradients \| Routed entirely to the maximum element", "max pool gradients table row", False),
    # --- rejects: positive contributions family (#34) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/04. Advanced Pooling Mechanisms and Global Average Pooling.md", r"multiply each channel by its weight", "cam einsum weighting", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md", r"^## 2\. Grad-CAM: Gradient-weighted Class Activation Mapping", "grad-cam heading", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md", r"^### \(Optional\) Grad-CAM Visualizations", "gradcam visualizations heading", True),
    # --- rejects: predicts hidden family (#35) ---
    ("master-ai", "26 - Papers/Efficient Attention/49 - Medusa and EAGLE 2024.md", r"predicts hidden features \(smoother, more predictable\)", "eagle predicts hidden features", False),
    # --- rejects: prompt-derived / repetitive content family (#37, #40) ---
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"build a prompt-derived n-gram model for speculative decoding\?", "prompt-derived ngram qa", False),
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"Feed the \$K\$ tokens to the expensive LLM for verification", "k tokens verification", False),
    # --- rejects: randomly flip family (#38) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"transforms include data augmentation to prevent overfitting", "resnet augmentation comment", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"^# 18\. Data Augmentation", "data augmentation note title", True),
    # --- rejects: releasing family (#39) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"leak \(each iteration adds a new", "graph leak prose", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"PyTorch frees \(deletes\) the computational graph after the backward pass", "frees computational graph", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"releasing the graph", "releasing the graph comment", False),
    # --- rejects: right edge family (#41) ---
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"consider the convolution operation as a sliding window", "sliding window derivation", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/06. Padding - Mathematics, Edge Effects, and Valid vs Same.md", r"^# 2\.2 Padding: Mathematics, Edge Effects, and Valid vs\. Same", "padding note title", True),
    # --- rejects: second conv family (#42) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md", r"# Batch normalization after second conv", "second conv code comment", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md", r"^# 3\. The Convolution Operation Deep Dive", "conv deep dive note title", True),
    # --- rejects: total samples family (#44) ---
    ("ai-course", "03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md", r"Global Context \(\$k=9\$\)", "knn global context", False),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/01. Mathematical Notation (ML Course).md", r"list with 5 items, \$n=5\$", "n items notation gloss", False),
    # --- rejects: tulu family (#45) ---
    ("master-ai", "12 - Fine-Tuning/DPO/04 - DPO Derivation.md", r"\(Zephyr, OpenHermes, Tulu, many Llama fine-tunes\)", "dpo derivation tulu list", False),
    ("master-ai", "12 - Fine-Tuning/Instruction Tuning/03 - Instruction Tuning and Chat Templates.md", r"\(OpenHermes, Tulu\) are trained mostly on synthetic data", "instruction tuning tulu list", False),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"\(Zephyr, OpenHermes, Tulu, Starling\)", "dpo2023 tulu starling list", False),
    ("master-ai", "26 - Papers/Alignment/09 - DPO 2023.md", r"\(Zephyr, OpenHermes, Tulu\) was largely enabled by DPO", "dpo2023 tulu wave list", False),
    # --- rejects: update learning rate family (#46, #47) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"# Update learning rate", "update learning rate comment", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md", r"scheduler\.step\(\)", "scheduler step", False),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"^# 14 - Learning Rate Schedules", "lr schedules note title", True),
    ("master-ai", "02 - Mathematics/Optimization/14 - Learning Rate Schedules.md", r"The learning rate is the single most important hyperparameter\. A good schedule: warmup", "lr schedules tldr", False),
    # --- rejects: update step family (#48) ---
    ("ai-course", "03 - Machine Learning/03.1 - Regression/03. Linear Regression (DL Perspective).md", r"Incorrect \(sequential\):\*\* New \$\\theta_0 = 1 - \\alpha\(0\.5\) = 0\.5\$", "sequential update incorrect", False),
    ("ai-course", "03 - Machine Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule and Convergence.md", r"^# 6\. Gradient Descent — The Update Rule and Convergence", "update rule note title", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/06. Gradients and Gradient Descent.md", r"is an optimization algorithm that uses the gradient to minimize a function", "gradient descent definition", False),
    # --- rejects: zero-padding added family (#50) ---
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md", r"# stride: step size of the convolution", "conv config comment", False),
    # --- subagent-erratum re-verification additions (all 12 accepted errata + 4 strengthening citations) ---
    ("master-ai", "05 - NLP Fundamentals/Language Modeling/07 - N-gram Language Models.md", r"^# 07 - N-gram Language Models", "ngram note title :9", True),
    ("ai-course", "01 - Foundations and Overview/01.2 - Mathematical Foundations/01. Mathematical Notation (ML Course).md", r"^# Mathematical Notation in Linear Regression: A Deep Dive", "notation note title :3", True),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"# Training transforms include data augmentation to prevent overfitting", "training transforms comment :594", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"# RandomResizedCrop: randomly crop and resize the image \(augmentation\)", "randomresizedcrop comment :595", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"# RandomHorizontalFlip: randomly flip the image horizontally \(augmentation\)", "randomhorizontalflip comment :596", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/09. ResNet Bottleneck Blocks and Architectural Variants.md", r"# ToTensor: convert PIL image to PyTorch tensor", "totensor convert pil comment :597", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.2 - Backpropagation Deep Dive/04. Backpropagation and Gradient Flow in CNNs.md", r"Why accumulation is the default", "why accumulation default :265", False),
    ("ai-course", "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md", r"> \[!warning\] Wrong Normalization = Broken Pre-Trained Model", "warning callout title :479", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/02. PyTorch Implementation Basics.md", r"Python float, releasing the graph", "releasing the graph :575", False),
    ("master-ai", "27 - Projects/Mini-Projects/03 - Build a Mini Agent.md", r"- web_search: Search the web for current information\.", "web_search registry gloss :150", False),
    ("master-ai", "27 - Projects/Mini-Projects/03 - Build a Mini Agent.md", r"def web_search\(query: str, max_results: int = 5\) -> str:", "web_search implementation :59", False),
    ("master-ai", "28 - Glossary/Terms/A-Z Terms.md", r"\*\*Chat template\*\* — format for wrapping user/assistant messages", "glossary chat template :48", False),
    ("master-ai", "28 - Glossary/Terms/A-Z Terms.md", r"\*\*Memory\*\* — persistent state for agents", "glossary memory :166", False),
    ("master-ai", "28 - Glossary/Acronyms/Acronyms Index.md", r"\*\*VLM\*\* — Vision-Language Model", "acronyms vlm :202", False),
    ("ai-course", "05 - Convolutional Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and Philosophy - Summary.md", r"^### 1\.9\.3\. Global Average Pooling \(GAP\) as a Modern Alternative", "gap summary heading :635", True),
]

# Level-exact guard: every require_heading=True pattern must begin with a
# literal '^' + 1-6 '#' + one space (e.g. '^### Foo'). The batch-14 blind
# spot was '^#+', which matches any level.
_LEVEL_EXACT_GUARD = re.compile(r"^#{1,6} (?!#)")


def main() -> int:
    # guard: reject any non-level-exact heading pattern
    bad = [
        (note, pattern)
        for vault, path, pattern, note, require_heading in CHECKS
        if require_heading and not _LEVEL_EXACT_GUARD.match(pattern.lstrip("^")) or
        (require_heading and pattern.startswith("^#+"))
    ]
    bad = [b for b in bad if b]
    if bad:
        for note, pattern in bad:
            print(f"GUARD-FAIL [{note}] require_heading pattern is not level-exact: {pattern!r}")
        return 2

    ok = 0
    fail = 0
    for vault, path, pattern, note, require_heading in CHECKS:
        root = VAULTS[vault]
        fp = root / path
        if not fp.exists():
            print(f"MISSING FILE [{note}] {vault}/{path}")
            fail += 1
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        lines = text.split("\n")
        pat = re.compile(pattern)
        struct = extract_structure_text(text)
        heading_lines = {h["line"]: h["text"] for h in struct.get("headings", [])}
        found = False
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                if require_heading and i not in heading_lines:
                    continue
                status = "HEADING" if i in heading_lines else "LINE"
                print(f"OK   [{note}] {vault}/{path}:{i} ({status}) :: {line.strip()[:110]}")
                found = True
                ok += 1
                break
        if not found:
            print(f"FAIL [{note}] {vault}/{path} pattern={pattern!r}")
            fail += 1
    print(f"\n{ok} OK, {fail} FAIL, {len(CHECKS)} checks")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
