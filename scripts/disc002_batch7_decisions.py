#!/usr/bin/env python3
"""DISC-002 session 7 (batch 7): emit the 60 review decisions as JSONL.

Method (same as batches 3-6): individual evidence review of the 60
highest-signal unreviewed provisional candidates (post-batch6 state,
session-7 fresh replay), a definitional-treatment coverage probe
(scripts/disc002_batch7_probe.py, 58 terms, results in
/home/z/my-project/scratch/disc002-batch7-probe.json), targeted corpus
verification for citations (scripts/disc002_batch7_verify.py, 58 locator
checks, all OK), and an independent subagent cross-check of 27 judgment
calls (15 covers + 1 confirm_gap + 1 merge + 10 borderline rejects):
27/27 AGREE, with corrections incorporated (val citations upgraded from
mermaid node labels to real headings '## 2. Validation Set (15%)' :267 /
'## What Is the Validation Step?' :368 with chapter-level parent paths;
ingestion citation upgraded from the worked-example step :420 to the
definitional '### Indexing (offline, batch)' :54-60; deepseek-r1 cover
strengthened with the dedicated paper note '26 - Papers/2024-2026/12 -
DeepSeek-R1 2025.md').

Result: 15 cover (evidence-cited) + 1 confirm_gap (async def — third
confirmed gap overall) + 1 merge (await -> async def) + 43 reject.

Candidate IDs are taken from the selection file (scratch
disc002-batch7-selected.json) and asserted against it, so a wrong ID
fails loudly instead of silently deciding the wrong candidate.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/concept-candidates/002-disc002-decisions-batch7.jsonl")
SELECTED = Path("/home/z/my-project/scratch/disc002-batch7-selected.json")

R = "GLM-5.3 orchestrator, DISC-002 session 7 (batch 7, subagent cross-checked 27/27)"

# term -> (action, rationale[, merge_into])
DECISIONS_BY_TERM = {
    "angle": ("reject",
     "Non-concept noise (homonym): geometric angle vs 'from a different angle' idiom "
     "vs rotation angle. Note: the technical senses are covered in-situ — the "
     "geometric definition at master-ai '02 - Mathematics/Linear Algebra/02 - Dot "
     "Product.md:52' ('where θ is the angle between the two vectors') and '03 - "
     "Cosine Similarity.md:12' ('It measures the **angle** between them'); θ "
     "notation at ai-course '01 - Foundations and Overview/01.2 - Mathematical "
     "Foundations/01. Mathematical Notation (ML Course).md:39'; rotation angles in "
     "augmentation at ai-course '05 - Convolutional Neural Networks (CNN)/06. Chapter "
     "Summaries (Aggregated)/05. Normalization, Regularization and Augmentation - "
     "Summary.md'."),
    "ignoring": ("reject",
     "Non-concept noise (gerund, generic vocabulary): 'ignoring' spans 'ignoring "
     "the bias term', 'ignoring inter-strategy differences', and misc prose; no "
     "definitional treatment needed anywhere."),
    "practitioners": ("reject",
     "Non-concept noise (generic noun): 'practitioners' is audience framing prose "
     "('practitioners use...', 'interviewers ask practitioners...'), not a concept."),
    "challenge": ("reject",
     "Non-concept noise (generic noun): 'challenge' spans 'training challenges', "
     "'benchmark challenges', and misc prose; each specific challenge is treated "
     "in-situ by its own topic note."),
    "gqa mqa": ("cover",
     "the GQA/MQA/MLA modern-attention variants have a dedicated note: master-ai "
     "'06 - Attention Mechanisms/Modern Attention/14 - GQA MQA MLA.md' ('## MQA "
     "(Multi-Query Attention, Shazeer 2019)' :26, '## GQA (Grouped-Query Attention, "
     "Ainslie et al. 2023)' :38, '## MLA (Multi-head Latent Attention, DeepSeek 2024)' "
     ":52, '## Worked Example: KV Cache Size Comparison' :170), reinforced by master-ai "
     "'06 - Attention Mechanisms/Multi-Head Attention/05 - Multi-Head Attention.md:101,128' "
     "(per-variant sections) and the dedicated paper note '26 - Papers/Efficient "
     "Attention/29 - GQA 2024.md'."),
    "gqa mqa mla": ("cover",
     "same dedicated treatment as the 'gqa mqa' candidate: master-ai '06 - Attention "
     "Mechanisms/Modern Attention/14 - GQA MQA MLA.md' covers all three variants "
     "definitionally (MQA :26, GQA :38, MLA :52) including the KV-cache-size analysis "
     "(:113) and the MLA absorb-the-projection trick (:136); cross-referenced from "
     "master-ai '06 - Attention Mechanisms/MOC.md:28' and '15 - Sliding Window "
     "Attention.md:292'."),
    "mqa mla": ("cover",
     "same dedicated treatment: master-ai '06 - Attention Mechanisms/Modern Attention/"
     "14 - GQA MQA MLA.md' treats both surface forms of the pair (MQA :26, MLA :52), "
     "plus master-ai '08 - LLMs/Context and KV Cache/02 - KV Cache Mechanics.md' "
     "('## Why GQA / MQA / MLA Matter for KV Cache')."),
    "proper": ("reject",
     "Non-concept noise (adjective): 'proper' is a correctness qualifier ('proper "
     "initialization', 'proper normalization') applied inside other topics' "
     "treatments."),
    "val": ("reject",
     "Non-concept noise (code abbreviation): 'val' is the code/table/mermaid "
     "abbreviation of validation (val_loss, val_acc, val_loader). Note: the "
     "validation concept has real dedicated treatments — ai-course '01 - Foundations "
     "and Overview/01.1 - AI, ML, and DL Hierarchy/08. Foundations of Machine "
     "Learning (Summary).md:267' ('## 2. Validation Set (15%)'), :293 ('### Why "
     "Validation Matters'), :366/:368 ('# The Validation Step (Deep Dive)' / '## "
     "What Is the Validation Step?') — and batch 6 already covered the eval-set "
     "concept (D-DISC002-B6)."),
    "dpo derivation": ("cover",
     "the DPO derivation has a dedicated note: master-ai '12 - Fine-Tuning/DPO/04 - DPO "
     "Derivation.md' ('# DPO Derivation' :8, '## The Derivation' :26 with the full "
     "five-step chain :28/:38/:48/:56/:72, '## Variants' :134 covering IPO/KTO/SimPO/"
     "ORPO, '## Worked Example' :160); cross-referenced from master-ai '02 - "
     "Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md:150,344' and "
     "'02 - Mathematics/Statistics/16 - Estimators and Bias.md:293'."),
    "factors": ("reject",
     "Non-concept noise (generic noun): 'factors' spans 'two factors' in "
     "chain-rule products, 'depends on many factors', and misc prose; the "
     "chain-rule factor treatment is in-situ at ai-course '03. Understanding the "
     "Math Notation - Chain Rule and wrt.md'."),
    "merges": ("reject",
     "Non-concept noise (generic verb, multi-sense): the GRU gate-merge fact is "
     "explained in-situ at ai-course '07 - Sequence Models and RNNs/07.2 - LSTM and "
     "GRU/02. GRU - Simplifying the LSTM.md:12,74' ('Merges the forget and input "
     "gates into a single **update gate**'); the vault-management merge notes "
     "(ai-course README.md:888) are project bookkeeping, not knowledge concepts."),
    "strongest": ("reject",
     "Non-concept noise (superlative adjective): 'strongest' spans 'strongest "
     "baseline', 'strongest signals', and misc prose."),
    "potential": ("reject",
     "Non-concept noise (generic adjective): 'potential' spans 'potential debris', "
     "'has potential', 'potential energy' metaphors, and misc prose; no "
     "definitional treatment needed."),
    "providing": ("reject",
     "Non-concept noise (gerund): 'providing' is connective prose ('providing a "
     "clear signal', 'providing the model with...')."),
    "anything": ("reject",
     "Non-concept noise (pronoun): 'anything' spans 'anything from images to text' "
     "and misc prose fragments."),
    "bfloat16": ("cover",
     "bfloat16/bf16 has dedicated definitional treatments: master-ai '11 - "
     "Training/Optimization/04 - Mixed Precision Training.md' ('### FP16 (IEEE 754 "
     "half-precision)' :34, '### BF16 (Brain Float 16, Google)' :57 under '## The "
     "Three Formats' :32, also FP8 :78), plus usage guidance at master-ai '06 - "
     "Attention Mechanisms/Self-Attention/04 - Self-Attention.md:389' (FP32 "
     "accumulation / BF16 for large d_k) and '02 - Mathematics/Linear Algebra/02 - Dot "
     "Product.md:264' (overflow in fp16/bf16 mixed precision)."),
    "deepseek-r1 2025": ("cover",
     "DeepSeek-R1 has multiple dedicated treatments: master-ai '09 - Foundation "
     "Models/Reasoning Models/03 - Reasoning Models.md:34' ('## DeepSeek-R1 (Jan "
     "2025)'), '10 - Model Architecture Research/Open Source/01 - DeepSeek "
     "Architecture.md:77' ('## DeepSeek-R1: Reasoning on V3'), '24 - Research "
     "Frontiers/Reasoning/06 - Test-Time Compute Scaling.md:110', and the dedicated "
     "paper note '26 - Papers/2024-2026/12 - DeepSeek-R1 2025.md' (:8)."),
    "ingestion": ("cover",
     "the RAG ingestion stage has dedicated treatments: master-ai '17 - RAG/Ingestion "
     "and Retrieval/01 - RAG Pipeline Overview.md' ('### Indexing (offline, batch)' "
     ":54-60, the ingestion/indexing stage of the pipeline), '27 - Projects/Capstones/"
     "14 - Build a Multimodal RAG Pipeline.md:198' ('## Step 4: Ingestion Pipeline' "
     "with a full ingest_document implementation), '27 - Projects/Capstones/21 - Build "
     "a Knowledge-Graph Construction Pipeline.md:55' ('## Step 1: Document Ingestion "
     "and Chunking')."),
    "logical": ("reject",
     "Non-concept noise (adjective): 'logical' spans 'logical and mathematically "
     "sound', logical operators, and logical reasoning; no coherent single concept."),
    "difficulty": ("reject",
     "Non-concept noise (generic noun): 'difficulty' spans the Glorot-Bengio paper "
     "title quoted at ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/01. Weight "
     "Initialization.md:195', Capsule-Network prose, and misc difficulty talk; the "
     "training-difficulty analysis itself is the vanishing/exploding-gradient "
     "topic, which has dedicated notes."),
    "multiplying": ("reject",
     "Non-concept noise (gerund): 'multiplying' spans multiply-accumulate prose and "
     "misc arithmetic narration; the matmul mechanics have dedicated treatments "
     "(master-ai '02 - Mathematics/Linear Algebra/04 - Matrix Multiplication.md')."),
    "one token": ("reject",
     "Non-concept noise (quantifier phrase): 'one token at a time' is the "
     "autoregressive-generation description, explained in-situ at ai-course '07 - "
     "Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. "
     "The Encoder-Decoder Pattern - Conditional Generation.md:32,46'; the token "
     "concept itself has the dedicated master-ai '05 - NLP Fundamentals/"
     "Tokenization/01 - Tokenization Overview.md' plus BPE/WordPiece notes."),
    "per step": ("reject",
     "Non-concept noise (quantifier phrase): 'per step' spans the LSTM cost table "
     "('Weights per step' at ai-course '07 - Sequence Models and RNNs/07.2 - LSTM "
     "and GRU/01. LSTM - Gates as Learned Traffic Controllers.md:124'), "
     "per-step-gradient prose, and misc quantifiers."),
    "per-request": ("reject",
     "Non-concept noise (quantifier phrase): 'per-request' is a cost/latency "
     "modifier; the per-request cost-tracking topic is treated at master-ai '21 - "
     "LLMOps and MLOps/Pipelines/01 - LLMOps vs MLOps.md:191' ('### Per-request "
     "cost tracking') and per-request batching at '13 - Inference/Serving/06 - "
     "Continuous Batching Deep Dive.md'."),
    "10 model": ("reject",
     "Non-concept noise (vault-management prose fragment): '10 model' comes from "
     "master-ai '00 - Vault Management/Architecture Decisions.md:685' ('8 chapter "
     "10 model arch notes') — chapter numbering in project bookkeeping, not a "
     "concept."),
    "proposed": ("reject",
     "Non-concept noise (past participle): 'proposed' spans 'proposed method', "
     "'proposed architecture', and misc prose."),
    "ref": ("reject",
     "Non-concept noise (code identifier): 'ref' is a code variable/reference "
     "shorthand (git refs, ref= parameters, variable names) in code examples."),
    "asked": ("reject",
     "Non-concept noise (past participle): 'asked' is interview-prose narration "
     "('asked to classify', 'when asked...')."),
    "light": ("reject",
     "Non-concept noise (adjective, homonym): 'light' spans 'in light of', "
     "light-colored pixels, and lightweight models; no coherent single concept."),
    "operating": ("reject",
     "Non-concept noise (gerund, homonym): 'operating' spans warehouse robots "
     "(operations), the PATH installation prose, and classification-threshold "
     "operating points; each specific sense is treated in-situ by its own topic "
     "(ROC thresholds at ai-course '03 - Machine Learning/03.6 - Model Evaluation/"
     "02. Model Evaluation Metrics Beyond Accuracy.md')."),
    "analogous": ("reject",
     "Non-concept noise (adjective): 'analogous' is comparison prose ('analogous "
     "to...', 'is analogous...')."),
    "avoiding": ("reject",
     "Non-concept noise (gerund): 'avoiding' spans 'avoiding overfitting', "
     "'avoiding catastrophic forgetting', and misc prose; each specific avoidance "
     "topic has its own dedicated treatment."),
    "await": ("merge",
     "'await' is the same concept as 'async def' (the Python async/await execution "
     "model): 5 of 6 evidence files are shared with candidate CG-00366e34ee82 "
     "(master-ai '19 - MCP/Architecture/01 - MCP Overview.md:407', '19 - MCP/"
     "Components/02 - MCP Components.md:271', '19 - MCP/Integration/04 - MCP "
     "Enterprise Integration.md:379', '18 - Memory Systems/Vector Memory/04 - Vector "
     "Memory Backends.md:343', '16 - Multi-Agent Systems/Enterprise/04 - Enterprise "
     "Multi-Agent Architectures.md:222'); merging into CG-00366e34ee82, the "
     "confirmed-gap record for the concept.", "CG-00366e34ee82"),
    "substantially": ("reject",
     "Non-concept noise (adverb): 'substantially' is degree prose ('substantially "
     "faster', 'substantially different')."),
    "weight updates": ("cover",
     "the weight-update concept has dedicated treatments: ai-course '03 - Machine "
     "Learning/03.2 - Optimization Algorithms/07. Gradient Descent - The Update Rule "
     "and Convergence.md' (:1 dedicated note, '## 6.3 The Gradient Descent Update "
     "Rule' :73), ai-course '04 - Neural Networks and Deep Learning Foundations/04.1 "
     "- Neural Network Basics/03. Artificial Neural Networks (ANN) - Comprehensive.md' "
     "('### The Update Rule' :264, '### Final Weight Update (Δw)' :656), and the LoRA "
     "low-rank weight-update treatment at master-ai '02 - Mathematics/Linear Algebra/"
     "04 - Matrix Multiplication.md:327'."),
    "low-level features": ("cover",
     "low-level features are treated definitionally: ai-course '05 - Convolutional "
     "Neural Networks (CNN)/06. Chapter Summaries (Aggregated)/01. Foundations and "
     "Philosophy - Summary.md:493' ('#### Low-Level Features (Early Layers)' with "
     "edge/Gabor/color-opponent definitional bullets) and the dedicated note ai-course "
     "'05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/02. "
     "Hierarchical Feature Extraction.md' ('#### Layer 1 — Low-Level Features (Edges "
     "and Gradients)' :9); master-ai '04 - Neural Networks/Architectures/03 - CNNs."
     "md:40' ('### 4. Hierarchical features')."),
    "maintaining": ("reject",
     "Non-concept noise (gerund): 'maintaining' spans 'maintaining the ratio', "
     "'maintaining a cache', and misc prose."),
    "specified": ("reject",
     "Non-concept noise (past participle): 'specified' spans 'specified batch "
     "size', 'unless specified otherwise', and misc prose."),
    "checking": ("reject",
     "Non-concept noise (gerund): 'checking' spans 'checking for NaN', 'checking "
     "gradients', and misc prose; the specific checks belong to their debugging "
     "topics."),
    "natural language": ("reject",
     "Non-concept noise (generic domain descriptor): 'natural language' names the "
     "unstructured-data domain; NLP has dedicated treatments (master-ai '05 - NLP "
     "Fundamentals/' chapter, ai-course '01 - Foundations and Overview/01.1 - AI, "
     "ML, and DL Hierarchy/06. Applications of Deep Learning.md:54' '## Natural "
     "Language Processing (Text / Audio)'; CLIP's natural-language supervision at "
     "master-ai '23 - Multimodal AI/Vision-Language/02 - CLIP.md')."),
    "representing": ("reject",
     "Non-concept noise (gerund): 'representing' spans 'representing words as "
     "vectors', 'representing the data', and misc prose; embeddings have dedicated "
     "treatments (master-ai '09 - Foundation Models/Embedding Models/')."),
    "showing": ("reject",
     "Non-concept noise (gerund): 'showing' is demonstration prose ('showing the "
     "model', 'plots showing...')."),
    "centered": ("reject",
     "Non-concept noise (past participle): 'centered' — the centering step is "
     "covered in-situ at ai-course '03 - Machine Learning/03.8 - Dimensionality "
     "Reduction/01. Principal Component Analysis (PCA).md:32' ('1. **Center the "
     "data:** subtract the mean of each feature, so the data is centered at the "
     "origin') and :42 (SVD of the centered data matrix)."),
    "tuple": ("cover",
     "tuples have a dedicated section: ai-course '02 - Python and Data Tooling/02.2 - "
     "Python Programming Essentials/03. Data Structures - Lists, Tuples, and Sets.md' "
     "('## 3.2 Tuples' :28 with '**Definition:** Ordered, **immutable** collection' "
     ":30, unpacking :37); used definitionally at master-ai '02 - Mathematics/Linear "
     "Algebra/01 - Vectors.md:16' ('A vector x in R^n is an ordered tuple of n real "
     "numbers') and master-ai '03 - Machine Learning/Reinforcement Learning/07 - MDPs "
     "and Bellman Equations.md:39' (MDP tuple)."),
    "unnecessary": ("reject",
     "Non-concept noise (adjective): 'unnecessary' spans 'unnecessary computation', "
     "'unnecessary tokens', and misc prose; the underlying efficiency topics (e.g. "
     "KV-cache reuse, early stopping) have their own dedicated treatments."),
    "upstream": ("reject",
     "Non-concept noise (homonym): the backprop 'upstream gradient' is defined "
     "in-situ at master-ai '04 - Neural Networks/Training/06 - Backpropagation.md:48' "
     "('The key quantity at each node is the **upstream gradient** — ∂L/∂(node "
     "output)') and :59, reinforced by master-ai '02 - Mathematics/Calculus/10 - "
     "Gradient and Chain Rule.md:88,242' and ai-course '04.2 - Backpropagation Deep "
     "Dive/04. Backpropagation and Gradient Flow in CNNs.md:460'; the "
     "upstream-services sense is covered by the MCP gateway notes (master-ai '19 - "
     "MCP/Integration/04 - MCP Enterprise Integration.md:284,322')."),
    "async def": ("confirm_gap",
     "async def: Python's async/await execution model (coroutines, the event loop, "
     "cooperative scheduling, asyncio.to_thread for blocking I/O) is used in "
     "implementation position in 17 master-ai files ('async def' 53 occurrences; "
     "'await' 77 occurrences in 20 files: MCP notes 19-x, agent frameworks 25-x, "
     "capstones 27-x including 08/15/16/18/23, memory systems 18-x, infrastructure "
     "20-x, production 22-x) but has NO definitional treatment anywhere in the "
     "corpus: ai-course, whose Python curriculum teaches variables through "
     "iterators/generators ('02 - Python and Data Tooling/'), contains ZERO "
     "occurrences of async/await/asyncio/coroutine/event loop (verified corpus-wide; "
     "its generators note '07. Iterators, Generators, and Memory Efficiency.md' "
     "covers yield/lazy evaluation and stops one step short of coroutines); "
     "master-ai only warns operationally — '27 - Projects/Capstones/08 - Build an "
     "MCP Server.md:296' ('MCP handlers are async. If you do blocking I/O (file "
     "reads, network calls), you'll block the event loop and the server will appear "
     "hung. Use asyncio.to_thread() or aiofiles'), :299, :351 ('use async def for "
     "every tool/resource/prompt handler; never block the event loop'), '19 - MCP/"
     "Components/02 - MCP Components.md:329' ('Use async I/O; don't block event "
     "loop'), '16 - Multi-Agent Systems/Enterprise/04 - Enterprise Multi-Agent "
     "Architectures.md:222' ('Use async patterns (LangGraph, async/await)') — and "
     "the one-line characteristics bullet '19 - MCP/Architecture/01 - MCP "
     "Overview.md:105' does not explain the mechanism. The capstones REQUIRE writing "
     "async code, so the dependency position is established. Destination: dedicated "
     "section in the unified vault's Python-tooling/MCP-implementation treatment "
     "(what async/await means, coroutine suspension, event-loop scheduling, "
     "asyncio.to_thread, when blocking I/O stalls an MCP server — grounded in the "
     "corpus's own warnings and code)."),
    "generic": ("reject",
     "Non-concept noise (adjective): 'generic' spans 'generic framework', 'generic "
     "vocabulary', 'generic model' prose."),
    "locally": ("reject",
     "Non-concept noise (adverb): 'locally' spans 'locally optimal', 'computed "
     "locally', and misc prose; local minima have dedicated treatments in the "
     "optimization notes."),
    "pipeline overview": ("cover",
     "the training-pipeline overview has dedicated treatments: ai-course '05 - "
     "Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and "
     "Interpretability/01. The Full Training Pipeline End-to-End Checklist.md:10' "
     "('## Pipeline Overview', five phases) and '06. Chapter Summaries (Aggregated)/"
     "07. Scaling, Pipeline and Interpretability - Summary.md:621' ('### 3.1 Pipeline "
     "Overview'), plus the dedicated master-ai '17 - RAG/Ingestion and Retrieval/01 - "
     "RAG Pipeline Overview.md'."),
    "rag pipeline overview": ("cover",
     "the RAG pipeline overview is itself a dedicated note: master-ai '17 - RAG/"
     "Ingestion and Retrieval/01 - RAG Pipeline Overview.md' (:9 '# RAG Pipeline "
     "Overview', indexing/query stages and design decisions), cross-referenced from "
     "master-ai '02 - Mathematics/Linear Algebra/03 - Cosine Similarity.md:284' and "
     "'26 - Papers/Agents and RAG/35 - RAG 2020.md:194'."),
    "read-only": ("reject",
     "Non-concept noise (adjective): 'read-only' is a permission qualifier; the "
     "MCP read-only-resources topic is treated at master-ai '19 - MCP/Architecture/"
     "01 - MCP Overview.md:108-110' ('### Resources', 'Read-only data sources the "
     "LLM can access') and read-only HiTL actions at '15 - AI Agents/Autonomy/09 - "
     "Human-in-the-Loop Patterns.md:264'."),
    "reset": ("reject",
     "Non-concept noise (code comment/prose, homonym): 'reset' spans "
     "optimizer.zero_grad code comments (ai-course '04. Backpropagation and "
     "Gradient Flow in CNNs.md:259' 'Reset all parameter gradients to zero'), "
     "training-loop resets, and misc prose; the zero_grad practice is treated "
     "in-situ in the training-pipeline notes."),
    "doubling": ("reject",
     "Non-concept noise (gerund): 'doubling' — the channel-doubling rationale is "
     "explained in-situ at ai-course '04 - Neural Networks and Deep Learning "
     "Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and "
     "Network Configuration.md:36' ('The doubling pattern is not arbitrary — it "
     "follows the principle that each halving of spatial resolution...'); the "
     "He-init variance halving/doubling is treated in-situ at '08. Data Preparation "
     "and MLP Implementation.md:128'."),
    "memory backends": ("cover",
     "memory backends have a dedicated note: master-ai '18 - Memory Systems/Vector "
     "Memory/04 - Vector Memory Backends.md' (:9 '# 04 — Vector Memory Backends', "
     "'## Why Vector Databases Exist' :14, '## The Major Options' :22 with "
     "pgvector/Pinecone/Qdrant/Weaviate/Milvus and HNSW/IVF/PQ/DiskANN); "
     "cross-referenced from master-ai '18 - Memory Systems/Operations/03 - Memory "
     "Operations.md:184'."),
    "surrounding": ("reject",
     "Non-concept noise (adjective/gerund): 'surrounding' spans 'surrounding "
     "pixels/context' prose; the neighborhood concept is treated in-situ by the "
     "spatial-filtering and receptive-field notes."),
    "vector memory backends": ("cover",
     "verbatim title match with the dedicated note: master-ai '18 - Memory Systems/"
     "Vector Memory/04 - Vector Memory Backends.md' (:9); also the '### Vector "
     "Memory' section of master-ai '00 - Vault Management/Master Roadmap.md' and the "
     "interview treatment at '29 - Interview Prep/Conceptual/01 - Conceptual "
     "Interview Questions.md'."),
    "audit log": ("cover",
     "audit logging has dedicated definitional treatments: master-ai '16 - Multi-Agent "
     "Systems/Enterprise/04 - Enterprise Multi-Agent Architectures.md:141' ('### Audit "
     "Log' — immutable record of every decision), '19 - MCP/Security/03 - MCP "
     "Security.md' ('### Audit Logging' :116 with who/when/what/why, prose :123, "
     "'### Audit Logging Standards' :224), '19 - MCP/Integration/04 - MCP Enterprise "
     "Integration.md:92' ('### Audit Log')."),
    "extracting": ("reject",
     "Non-concept noise (gerund): 'extracting' spans 'extracting features', "
     "'extracting data', and misc prose; feature extraction has dedicated "
     "treatments (ai-course '05 - Convolutional Neural Networks (CNN)/03. "
     "Architecture and Connectivity/02. Hierarchical Feature Extraction.md')."),
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
            "decision_id": f"D-DISC002-B7-{i:04d}",
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
