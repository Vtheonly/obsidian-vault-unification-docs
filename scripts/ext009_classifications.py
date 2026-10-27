#!/usr/bin/env python3
"""EXT-009: generalization / regularization domain classifications.

Generates state/classifications/006-ext009-generalization-overlap.jsonl
from batches 008 (master-ai '03 - Machine Learning/Generalization' — 01 Bias
Variance Tradeoff + 06 Regularization Techniques, 2 files, 106 KUs) and 009
(ai-course '04.3 - Training Dynamics and Stability' files 05 Batch
Normalization + 06 Dropout and Regularization + 07 Data Augmentation — the
regularization-relevant subset of that folder, 3 of 7 files, 234 KUs), over
the CAP-013 discovery output (reports/extraction/ext009-overlap-candidates.json:
2961 pairs, 40 cross-vault topics, 5 topics truncated at the 250-pair cap).

Overlap judgments (26 records: 21 Semantic Duplicate, 3 Partial Overlap,
2 Complementary Content — OC-ext009-0026 added at review per EXT-009-REVIEW
CG-1/R1), each with byte-exact quote evidence.

Verification before writing (exit non-zero on ANY failure):
  X1 every evidence quote is a byte-exact substring of the referenced KU's
     excerpt in the new batch files;
  X1b evidence source_path equals the KU's source_path;
  X2 every evidence quote sits byte-exact at its stated lines in the
     ORIGINAL source file (EXT-005-REVIEW precedent; 0 off-by-one tolerance)
     and every stated line lies inside the KU's own span;
  X3 every record is cross-vault (both ai-course and master-ai in ku_ids);
  X4 evidence ku_ids == record ku_ids exactly;
  X5 every KU id exists in the new batches;
  X6 the record set validates against schemas/overlap-classification.schema.json;
  X7 classification ids are unique and sequential;
  X8 no duplicate quote strings anywhere in the file;
  X9 committed classification files 001-005 are byte-unchanged (append-only).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCHES = [
    REPO / "state/knowledge-units/008-ext009-master-ai-generalization.jsonl",
    REPO / "state/knowledge-units/009-ext009-ai-course-04.3-regularization.jsonl",
]
COMMITTED = [
    REPO / "state/classifications/001-ext003-regression-overlap.jsonl",
    REPO / "state/classifications/002-ext004-tree-based-overlap.jsonl",
    REPO / "state/classifications/003-ext005-evaluation-overlap.jsonl",
    REPO / "state/classifications/004-ext007-evaluation-addendum.jsonl",
    REPO / "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl",
]
OUT = REPO / "state/classifications/006-ext009-generalization-overlap.jsonl"
SCHEMA = REPO / "schemas/overlap-classification.schema.json"

CLASSIFIED_BY = "EXT-009 orchestrator (Z AI / GLM 5.3 session, 2026-10-27)"
DATE = "2026-10-27"
TASK_ID = "EXT-009"

M01 = "03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md"
M06 = "03 - Machine Learning/Generalization/06 - Regularization Techniques.md"
C05 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md"
C06 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md"
C07 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md"

METHOD = (
    "Evidence-based classification per EXT-003..008 pattern: CAP-013 "
    "discovery over batches 008+009 (reports/extraction/"
    "ext009-overlap-candidates.json, 2961 pairs, 40 cross-vault topics) was "
    "read in full against both batches' KU excerpts and the original source "
    "lines; overlap clusters were judged per docs/KNOWLEDGE_AND_PROVENANCE.md "
    "section 7 (pair-level relationship types, separate from disposition). "
    "Every evidence quote is a byte-exact fragment verified inside the KU "
    "excerpt AND at the original source lines before writing (chain X1-X9 in "
    "this script). Single-vault elaborations are recorded inside rationales "
    "as vault-specific content, not as separate cross-vault records: "
    "master-ai-only in scope — the bias-variance decomposition derivation "
    "and its assumptions, cross-entropy/Domingos treatment, double descent / "
    "Zhang et al. 2017 / interpolation regimes, learning-curve signatures, "
    "LLM-specific levers (LoRA rank, SFT epochs, prompt overfitting, "
    "self-consistency), elastic net + ridge/lasso prior interpretations, "
    "weight tying, transformer/LLM-specific regularization lists, and the "
    "text/audio augmentation technique lists; ai-course-only in scope — the "
    "BatchNorm four-step mathematics, internal covariate shift + the "
    "Santurkar et al. 2018 caveat, running statistics / EMA / momentum, "
    "model.eval() BN mechanics, batch-size effects incl. the batch-size-1 "
    "breakdown, GroupNorm/LayerNorm/InstanceNorm alternatives, "
    "Conv-BN-ReLU placement debate, conv bias=False reasoning, Dropout2d, "
    "Bernoulli-mask + expected-value algebra, VGG parameter counts, "
    "mixup/cutmix/RandAugment mechanics, RandomResizedCrop parameters, "
    "Gaussian-noise and random-erasing implementations, ToTensor/Normalize "
    "mechanics, ImageNet statistics, and the invariance philosophy of "
    "augmentation. Sense-collision vocabulary documented in the term map "
    "(noise / translation / shift / scaling / inference / bias / variance) "
    "was adjudicated per pair with evidence, never by term count. "
    "Independent review: EXT-009-REVIEW (read-only) must PASS before commit."
)

CANDIDATE_REF = (
    "reports/extraction/ext009-overlap-candidates.json + -pairs.jsonl "
    "(CAP-013 over batches 008/009, terms generalization-domain-v1.json) + "
    "committed batches 008/009"
)

RECORDS = [
    {
        "classification_id": "OC-ext009-0001",
        "task_id": TASK_ID,
        "topic": "Overfitting means fitting the training data well while failing on unseen data; the training-vs-validation/test gap is the diagnostic",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a3d5d1f07d12fb4f", "KU-05e62c2d5014acd8", "KU-92a81afc5b276bf8"],
        "evidence": [
            {"ku_id": "KU-a3d5d1f07d12fb4f",
             "quote": "Models can fit training data perfectly but generalize poorly",
             "source_path": M06,
             "lines": [15]},
            {"ku_id": "KU-05e62c2d5014acd8",
             "quote": "Training error very low; test error much higher.",
             "source_path": M01,
             "lines": [32]},
            {"ku_id": "KU-92a81afc5b276bf8",
             "quote": "An overfit model performs exceptionally well on the training set but poorly on the validation and test sets.",
             "source_path": C06,
             "lines": [13]},
            {"ku_id": "KU-92a81afc5b276bf8",
             "quote": "This gap between training performance and validation performance is the hallmark of overfitting and the primary diagnostic signal that regularization is needed.",
             "source_path": C06,
             "lines": [13]},
        ],
        "rationale": (
            "Both vaults define overfitting by the same two-part claim: the "
            "model fits/performances well on training data AND fails to "
            "generalize, with the train-vs-held-out gap as the identifying "
            "signature. Master-ai states it compactly in its regularization "
            "motivation ('fit training data perfectly but generalize "
            "poorly') and in the bias-variance regime table's overfitting "
            "row ('Training error very low; test error much higher.'); the "
            "course devotes its opening section to the same claim, calling "
            "the gap 'the hallmark of overfitting'. The framings differ in "
            "conceptual apparatus (master-ai table row expresses it as the "
            "high-variance regime — see OC-ext009-0024 for the framing "
            "difference; the course uses the memorization framing with the "
            "student analogy) but the shared claim is duplicated. Related: "
            "OC-ext009-0002 (detection procedure), OC-ext009-0003 (causes)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0002",
        "task_id": TASK_ID,
        "topic": "Detect overfitting by monitoring training vs validation loss/accuracy on held-out data; the divergence point marks its onset",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-5465d83e21153c84", "KU-bdf957f03f050500", "KU-6013f98fb637f9a6"],
        "evidence": [
            {"ku_id": "KU-5465d83e21153c84",
             "quote": "**Training error low, validation error much higher** → high variance (overfitting). Fix: more data, regularization, simpler model, early stopping.",
             "source_path": M01,
             "lines": [86]},
            {"ku_id": "KU-bdf957f03f050500",
             "quote": "**Always have a held-out validation set.** You cannot diagnose bias-variance from training loss alone.",
             "source_path": M01,
             "lines": [114]},
            {"ku_id": "KU-6013f98fb637f9a6",
             "quote": "The most reliable way to detect overfitting is to monitor both the training loss (or accuracy) and the validation loss (or accuracy) during training.",
             "source_path": C06,
             "lines": [21]},
            {"ku_id": "KU-6013f98fb637f9a6",
             "quote": "The point at which validation loss starts increasing while training loss continues decreasing is called the **divergence point**, and it marks the onset of overfitting.",
             "source_path": C06,
             "lines": [21]},
        ],
        "rationale": (
            "Both vaults prescribe the same detection procedure: watch both "
            "curves on held-out data; the low-train/high-validation "
            "divergence is the overfitting signature. Master-ai's "
            "diagnosis list gives the pattern plus fixes, and its production "
            "implications make held-out validation mandatory ('You cannot "
            "diagnose bias-variance from training loss alone'); the course "
            "gives the same prescription and names the divergence point. "
            "Vault-specific: the course's numeric gap calibration (2-5 "
            "points healthy, 20+ serious, at L27) and the 99%/75% example "
            "(L27 of the same section) are course-only; master-ai's "
            "learning-curve-by-training-size diagnostics (L115, "
            "L254-269) "
            "are master-only. Related: OC-ext009-0001 (definition), "
            "OC-ext009-0016 (early stopping acts at exactly this divergence "
            "point)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0003",
        "task_id": TASK_ID,
        "topic": "Overfitting arises from excess model capacity relative to the training data: the model fits noise / memorizes instead of learning generalizable features",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-ac676c6254348c94", "KU-a2b55286da56e327", "KU-0ce2394b60e97e47"],
        "evidence": [
            {"ku_id": "KU-ac676c6254348c94",
             "quote": "Variance increases (model fits noise).",
             "source_path": M01,
             "lines": [49]},
            {"ku_id": "KU-a2b55286da56e327",
             "quote": "A high-degree polynomial fit to 10 points has high variance.",
             "source_path": M01,
             "lines": [23]},
            {"ku_id": "KU-0ce2394b60e97e47",
             "quote": "A model with millions of parameters can easily memorize a dataset of only thousands of examples.",
             "source_path": C06,
             "lines": [33]},
            {"ku_id": "KU-0ce2394b60e97e47",
             "quote": "The model has so many degrees of freedom that it can fit the training data perfectly without needing to learn generalizable features.",
             "source_path": C06,
             "lines": [33]},
        ],
        "rationale": (
            "The shared claim: capacity beyond what the data supports causes "
            "overfitting, because the model fits noise/memorizes rather than "
            "extracting generalizable structure. Master-ai expresses it in "
            "bias-variance language ('Variance increases (model fits "
            "noise)' plus the canonical high-degree-polynomial example); the "
            "course expresses the same claim in capacity language ('death "
            "by capacity', memorization). This is a judgment classification "
            "per the EXT-003 precedent: the two vaults use different "
            "vocabularies for one phenomenon, and the identification rests "
            "on the quoted claims, not on term counts. Vault-specific: the "
            "course's other two causes (too little data as a separate "
            "bullet and too many epochs at L34-35) and master-ai's full "
            "complexity-vs-error U-curve (L48-50, L56-62) are "
            "single-vault elaborations; the modern-regime caveat (deep nets "
            "generalizing despite capacity, master-ai L56-62, 184-201) has "
            "no course counterpart in scope. Related: OC-ext009-0001, "
            "OC-ext009-0024."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0004",
        "task_id": TASK_ID,
        "topic": "Regularization is the family of techniques that prevent overfitting by constraining the model; the canonical members are L1/L2 (weight decay), dropout, early stopping, data augmentation, and label smoothing",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-8d9a2c63ae27d1cc", "KU-912b55f98ace322a", "KU-a91968f779904bd7"],
        "evidence": [
            {"ku_id": "KU-8d9a2c63ae27d1cc",
             "quote": "Regularization = any technique that prevents overfitting by constraining the model. L1/L2 penalties, dropout, weight decay, early stopping, data augmentation, label smoothing, batch norm.",
             "source_path": M06,
             "lines": [11]},
            {"ku_id": "KU-912b55f98ace322a",
             "quote": "While Dropout is the most popular explicit regularization technique, it is part of a broader family of methods that combat overfitting.",
             "source_path": C06,
             "lines": [384]},
            {"ku_id": "KU-a91968f779904bd7",
             "quote": "the regularization toolkit includes L2 weight decay (penalizing large weights), L1 regularization (encouraging sparsity), early stopping (halting training at the optimal point), and label smoothing (preventing overconfidence).",
             "source_path": C06,
             "lines": [589]},
        ],
        "rationale": (
            "Both vaults define regularization the same way (techniques "
            "against overfitting via constraint) and enumerate essentially "
            "the same toolkit. Master-ai's TL;DR lists L1/L2, dropout, "
            "weight decay, early stopping, data augmentation, label "
            "smoothing and batch norm; the course's summary lists L2 weight "
            "decay, L1, early stopping and label smoothing around its "
            "dropout centerpiece, and its comparison table (L550-557) "
            "additionally rows dropout and batch normalization. The member "
            "sets coincide (batch norm appears in both via the table/TL;DR; "
            "data augmentation is taught in the course's dedicated file 07 "
            "— see OC-ext009-0021). Vault-specific: master-ai additionally "
            "covers elastic net, weight tying, and transformer/LLM-specific "
            "regularizers (L127-140); the course additionally frames the "
            "family around explicit-vs-implicit techniques. Related records "
            "0005-0022 carry the per-technique overlaps."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0005",
        "task_id": TASK_ID,
        "topic": "L2 regularization (weight decay) adds a squared-weight penalty to the loss, shrinking weights toward zero and yielding smoother decision boundaries that generalize better",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-6aac08208c91a4b4", "KU-8b7b0cc57d97927c", "KU-a5fab64b9d930285", "KU-69b30d0ea2dc08d1"],
        "evidence": [
            {"ku_id": "KU-6aac08208c91a4b4",
             "quote": "R(\\mathbf{w}) = \\|\\mathbf{w}\\|_2^2 = \\sum_i w_i^2",
             "source_path": M06,
             "lines": [30]},
            {"ku_id": "KU-8b7b0cc57d97927c",
             "quote": "Shrinks weights toward zero (but rarely to exactly zero).",
             "source_path": M06,
             "lines": [33]},
            {"ku_id": "KU-a5fab64b9d930285",
             "quote": "L2 regularization, also called **weight decay**, adds a penalty term to the loss function that discourages large weights",
             "source_path": C06,
             "lines": [388]},
            {"ku_id": "KU-69b30d0ea2dc08d1",
             "quote": "Small weights produce smoother, less complex decision boundaries, which tend to generalize better.",
             "source_path": C06,
             "lines": [392]},
        ],
        "rationale": (
            "Formula-level and purpose-level duplication: both vaults give "
            "the same L2 penalty (master-ai R(w)=||w||_2^2=sum w_i^2; "
            "course L_total = L_original + lambda sum w_j^2 at L390) and "
            "the same mechanistic story — discouraging large weights, "
            "shrinking toward zero, smoother/less complex decision "
            "boundaries that generalize better. Per the EXT-003 precedent "
            "this is partly a judgment classification: the formulas use "
            "different notation (R(w) vs L_total; lambda in both), and "
            "formula identity is invisible to term matching. Vault-specific: "
            "master-ai's Gaussian-prior/MAP interpretation (L33) and the "
            "course's decaying-update algebra w <- (1-2*eta*lambda)w - ... "
            "(L396) are complementary derivations, not duplicated claims. "
            "Related: OC-ext009-0006 (AdamW decoupling), OC-ext009-0007 "
            "(L1 contrast), OC-ext009-0009 (typical values)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0006",
        "task_id": TASK_ID,
        "topic": "In adaptive optimizers, L2 must be implemented as decoupled weight decay (AdamW), applying the decay directly to the weights rather than through the gradient; prefer AdamW over Adam + weight_decay",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a824c50137150b54", "KU-36d3158c44730403"],
        "evidence": [
            {"ku_id": "KU-a824c50137150b54",
             "quote": "In optimizers like AdamW, L2 is implemented as **decoupled weight decay** (multiply weights by $1 - \\eta \\lambda$ each step) rather than as a gradient penalty.",
             "source_path": M06,
             "lines": [35]},
            {"ku_id": "KU-36d3158c44730403",
             "quote": "AdamW (Loshchilov & Hutter, 2019) implements **decoupled weight decay**, applying the decay directly to the weights rather than through the gradient.",
             "source_path": C06,
             "lines": [427]},
            {"ku_id": "KU-36d3158c44730403",
             "quote": "Always prefer AdamW over Adam + weight_decay.",
             "source_path": C06,
             "lines": [427]},
        ],
        "rationale": (
            "Both vaults make the same precise optimizer-level claim: "
            "decoupled weight decay applies to weights directly, not via "
            "the gradient, and AdamW is the right implementation. "
            "Master-ai states the mechanism with the per-step multiplier "
            "(1 - eta*lambda); the course adds the reason standard "
            "Adam+weight_decay interacts badly with adaptive learning "
            "rates and makes the recommendation explicit. Vault-specific: "
            "the course's code block shows both optimizers side by side "
            "(L402-424); master-ai links to its Adam-derivation note "
            "(outside KU excerpt, heading-adjacent context). The citation "
            "difference (course: Loshchilov & Hutter 2019; master-ai: no "
            "year in excerpt) is presentational."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0007",
        "task_id": TASK_ID,
        "topic": "L1 regularization penalizes absolute weight values and drives exact zeros (sparsity, feature selection), unlike L2 which shrinks but rarely zeroes; L1 is consequently less used in deep learning than L2",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-8aa83cca4a5990d0", "KU-8b7b0cc57d97927c", "KU-ddfa45e76bc3f17f", "KU-1b18784d8030bfc6"],
        "evidence": [
            {"ku_id": "KU-8aa83cca4a5990d0",
             "quote": "Produces **sparse** weights (many exactly zero). Useful for feature selection.",
             "source_path": M06,
             "lines": [42]},
            {"ku_id": "KU-8b7b0cc57d97927c",
             "quote": "The standard for neural networks.",
             "source_path": M06,
             "lines": [33]},
            {"ku_id": "KU-ddfa45e76bc3f17f",
             "quote": "The key difference from L2 regularization is that L1 encourages **exact zeros** in the weight matrix, producing **sparse** models where many weights are exactly zero.",
             "source_path": C06,
             "lines": [435]},
            {"ku_id": "KU-1b18784d8030bfc6",
             "quote": "L1 regularization is less commonly used in deep learning than L2, primarily because the sparsity it induces can be too aggressive for the dense, distributed representations that neural networks typically rely on.",
             "source_path": C06,
             "lines": [437]},
        ],
        "rationale": (
            "Both vaults state the L1 mechanism (absolute-value penalty -> "
            "exact zeros -> sparsity/feature selection) and the L1-vs-L2 "
            "contrast (L2 shrinks toward zero without reaching it — "
            "master-ai L33 quoted in OC-ext009-0005; course L435 derives "
            "the same contrast from the +/-1 vs 2w_j gradient shapes). Both "
            "also position L2 as the DL default, master-ai by calling L2 "
            "'The standard for neural networks' and the course by calling "
            "L1 'less commonly used in deep learning than L2' — the same "
            "positioning claim from opposite directions. Vault-specific: "
            "master-ai's Laplace-prior interpretation (L42) and elastic "
            "net (L45-50) are master-only; the course's manual "
            "l1_penalty PyTorch implementation (L439-470) is course-only; "
            "the course's interpretability/efficiency rationale (L437) "
            "extends the shared positioning claim. Note: 'lasso' and "
            "'elastic net' occur in master-ai body text but the course "
            "side never names them — not evidence of a name-level match, "
            "only of the mechanism match recorded here."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0008",
        "task_id": TASK_ID,
        "topic": "Biases (and normalization parameters) are excluded from the L2/weight-decay penalty",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b7f8fa23e460ebb9", "KU-69b30d0ea2dc08d1"],
        "evidence": [
            {"ku_id": "KU-b7f8fa23e460ebb9",
             "quote": "**Don't apply weight decay to biases or norm parameters** — they don't have a regularization interpretation.",
             "source_path": M06,
             "lines": [176]},
            {"ku_id": "KU-69b30d0ea2dc08d1",
             "quote": "biases are typically excluded from the penalty",
             "source_path": C06,
             "lines": [392]},
        ],
        "rationale": (
            "Both vaults exclude bias parameters from the weight penalty. "
            "The shared core is the bias exclusion; master-ai extends it to "
            "norm parameters and gives the rationale (no regularization "
            "interpretation) plus the implementation hint (parameter "
            "groups), while the course states the exclusion parenthetically "
            "in the L2 formula explanation and again in its manual L1 "
            "implementation (weights-only parameter filter at L455-456, "
            "master-ai extension to norm parameters is a master-only "
            "addition to the shared claim, not a divergence."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0009",
        "task_id": TASK_ID,
        "topic": "Typical weight-decay values and their tuning context (moderate defaults; stronger for AdamW than SGD-CNN training)",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-b7f8fa23e460ebb9", "KU-a5f74256be30d4ef"],
        "evidence": [
            {"ku_id": "KU-b7f8fa23e460ebb9",
             "quote": "**Weight decay of 0.01–0.1** is a reasonable default for most training. Tune on validation.",
             "source_path": M06,
             "lines": [173]},
            {"ku_id": "KU-a5f74256be30d4ef",
             "quote": "# Common values: 1e-4 (mild) to 1e-2 (strong)",
             "source_path": C06,
             "lines": [407]},
            {"ku_id": "KU-a5f74256be30d4ef",
             "quote": "# For most CNN training, 1e-4 to 5e-4 is a good starting point",
             "source_path": C06,
             "lines": [408]},
        ],
        "rationale": (
            "Shared element: both vaults give concrete weight-decay value "
            "guidance anchored at overlapping ranges (master-ai 0.01-0.1 "
            "default; course 1e-4..1e-2 with 1e-4..5e-4 for CNN/SGD and "
            "1e-2 shown for AdamW at L422). The validation anchor is "
            "explicit only on the master-ai side ('Tune on validation', "
            "L173); the course's weight-decay code and prose never "
            "mention validation. Partial rather than semantic: "
            "the guidance targets different training regimes — master-ai "
            "speaks for AdamW-era LLM-scale defaults (0.01-0.1, "
            "'a reasonable default for most training' at L173, "
            "exemplified by its AdamW worked example weight_decay=0.01 "
            "at L161 and framed by the modern-LLM-recipe context at "
            "L167), the "
            "course for SGD-CNN recipes (1e-4..5e-4) — so the "
            "recommendations are compatible but context-dependent, and "
            "synthesis must keep both ranges with their referents rather "
            "than merging them. The course evidence is a code-block KU "
            "whose comments carry the values — transparent framing per the "
            "OC-ext008-0021 precedent (code KUs may evidence shared "
            "elements when the claim lives in the code/comments)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0010",
        "task_id": TASK_ID,
        "topic": "Dropout mechanism: during training randomly set a fraction p of neurons/activations to zero; at test time use the full network",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-dffd060992d910a5", "KU-1846c2a3c8c577a1"],
        "evidence": [
            {"ku_id": "KU-dffd060992d910a5",
             "quote": "During training, randomly set a fraction $p$ of activations to zero. At test time, use all activations (scaled to compensate).",
             "source_path": M06,
             "lines": [54]},
            {"ku_id": "KU-1846c2a3c8c577a1",
             "quote": "Dropout is a regularization technique that, during each forward pass in training, randomly \"drops\" (sets to zero) a fraction of neurons in a layer.",
             "source_path": C06,
             "lines": [58]},
        ],
        "rationale": (
            "Both vaults define dropout identically at the mechanism level: "
            "per-forward-pass random zeroing of a fraction p during "
            "training, full network at test. Master-ai compresses it to "
            "two sentences (activations; scaled to compensate — the "
            "scaling half is recorded separately in OC-ext009-0011); the "
            "course adds per-neuron independence and the Bernoulli mask "
            "algebra (L62-72), which is course-only elaboration of the "
            "shared mechanism. Related: OC-ext009-0011 (inverted-dropout "
            "scaling), OC-ext009-0012 (eval-mode discipline), "
            "OC-ext009-0013 (why it works)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0011",
        "task_id": TASK_ID,
        "topic": "Inverted dropout: survivors are scaled by 1/(1-p) during training so that expected outputs are preserved and no test-time adjustment is needed",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b57933c8b5bce1f0", "KU-1846c2a3c8c577a1", "KU-d64c3f1ff258b05b"],
        "evidence": [
            {"ku_id": "KU-b57933c8b5bce1f0",
             "quote": "PyTorch's `nn.Dropout` uses \"inverted dropout\" (scales during training), so no test-time adjustment is needed.",
             "source_path": M06,
             "lines": [181]},
            {"ku_id": "KU-1846c2a3c8c577a1",
             "quote": "the remaining neurons have their outputs scaled up by a factor of $\\frac{1}{1-p}$. This scaling is critical and is called **inverted dropout**",
             "source_path": C06,
             "lines": [58]},
            {"ku_id": "KU-d64c3f1ff258b05b",
             "quote": "at test time, we use all neurons with no scaling, and the expected output matches the expected output during training.",
             "source_path": C06,
             "lines": [74]},
        ],
        "rationale": (
            "Both vaults state the inverted-dropout design and its purpose: "
            "scale during training by 1/(1-p) (master-ai via the "
            "PyTorch-behavior framing; the course via the exact factor and "
            "its expected-value preservation E[h~_i]=h_i derived at L72), "
            "so evaluation needs no adjustment. Master-ai additionally "
            "notes the historical contrast (old frameworks scaled at test "
            "time) — master-only context. The pseudocode implementations "
            "(master-ai mask/(1-p) at L56-63; course nn.Dropout p=0.5 "
            "walkthrough at L161-198) are independent expressions of the "
            "same design, not additional claims."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0012",
        "task_id": TASK_ID,
        "topic": "Never apply dropout at inference; forgetting model.eval() before evaluation is a common silent bug — always switch modes explicitly",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b57933c8b5bce1f0", "KU-e2fade691f1b99c8", "KU-ee136aa501cf3e45"],
        "evidence": [
            {"ku_id": "KU-b57933c8b5bce1f0",
             "quote": "**Dropout at test time** — never apply dropout during inference. Always check `model.eval()`.",
             "source_path": M06,
             "lines": [180]},
            {"ku_id": "KU-e2fade691f1b99c8",
             "quote": "During evaluation (inference), Dropout is **completely disabled**. No neurons are dropped — every neuron is active and uses its full, unmodified output.",
             "source_path": C06,
             "lines": [138]},
            {"ku_id": "KU-ee136aa501cf3e45",
             "quote": "Always, always call `model.eval()` before running inference, and `model.train()` before resuming training.",
             "source_path": C06,
             "lines": [153]},
        ],
        "rationale": (
            "Both vaults carry the same operational discipline: dropout "
            "must be off at inference, model.eval()/model.train() are the "
            "switches, and forgetting is a common silent failure. "
            "Master-ai phrases it as a pitfall; the course devotes a full "
            "section plus a warning callout ('one of the most common bugs "
            "in deep learning... does not raise any error'). "
            "Vault-specific: the course's Monte-Carlo-dropout aside "
            "(intentional stochastic inference for uncertainty, L142) is "
            "course-only. The same model.eval() discipline governs "
            "BatchNorm on the course side (file 05, L142-143 callout) — "
            "the BN-specific mechanics (running statistics) are course-only "
            "in scope; master-ai has no BN train/eval content in scope."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0013",
        "task_id": TASK_ID,
        "topic": "Why dropout works: it prevents neuron co-adaptation and behaves as ensemble/model averaging over sub-networks",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-51e16f7ca33a80dc", "KU-1396f3ea49e151a4", "KU-4f6fcccc0aba49d9", "KU-35c47d029dfcff49"],
        "evidence": [
            {"ku_id": "KU-51e16f7ca33a80dc",
             "quote": "**Ensemble effect**: each forward pass uses a different sub-network. Like bagging, but at the activation level.",
             "source_path": M06,
             "lines": [67]},
            {"ku_id": "KU-51e16f7ca33a80dc",
             "quote": "**Noise injection**: prevents co-adaptation (no neuron can rely on any other specific neuron being present).",
             "source_path": M06,
             "lines": [68]},
            {"ku_id": "KU-51e16f7ca33a80dc",
             "quote": "**Approximates model averaging** over exponentially many sub-networks.",
             "source_path": M06,
             "lines": [69]},
            {"ku_id": "KU-1396f3ea49e151a4",
             "quote": "Dropout breaks these co-adaptations by making it impossible for any neuron to rely on any specific other neuron being present.",
             "source_path": C06,
             "lines": [109]},
            {"ku_id": "KU-4f6fcccc0aba49d9",
             "quote": "Dropout effectively trains an **ensemble** of neural networks during a single training run.",
             "source_path": C06,
             "lines": [113]},
            {"ku_id": "KU-35c47d029dfcff49",
             "quote": "the full network can be interpreted as an **approximate ensemble average** of all the sub-networks seen during training.",
             "source_path": C06,
             "lines": [115]},
        ],
        "rationale": (
            "The strongest structural match in this domain: both vaults "
            "explain dropout through the same reasons, in the same order of "
            "prominence — co-adaptation prevention (master-ai 'no neuron "
            "can rely on any other specific neuron being present'; course "
            "'impossible for any neuron to rely on any specific other "
            "neuron being present' — near-verbatim) and the "
            "ensemble/model-averaging interpretation (both: sub-networks, "
            "bagging-like, approximate ensemble average). The third reason "
            "differs: master-ai frames it as noise injection, the course "
            "as redundant representations (plus a Bayesian/Gal & Ghahramani "
            "aside, L121, course-only) — complementary framings of the "
            "same noise-robustness idea, noted for synthesis. The course's "
            "co-adaptation example (cat-face detector from ears+whiskers "
            "neurons, L107) is course-only elaboration. Related: "
            "OC-ext009-0023 (why averaging helps)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0014",
        "task_id": TASK_ID,
        "topic": "Standard dropout rates: strongest (~0.5) on large fully connected / hidden layers, weaker elsewhere; modern practice uses little or no dropout because other regularizers suffice",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-05e7a613b0b6f785", "KU-b8db22e905dfdfaa", "KU-a815459bcd3d5df0", "KU-c551b121821ab609", "KU-f454ef1318368321"],
        "evidence": [
            {"ku_id": "KU-05e7a613b0b6f785",
             "quote": "- Input layer: 0.1–0.2.\n- Hidden layers: 0.3–0.5.",
             "source_path": M06,
             "lines": [72, 73]},
            {"ku_id": "KU-b8db22e905dfdfaa",
             "quote": "Modern LLMs use **very little dropout** because they rely on data scale and other regularizers.",
             "source_path": M06,
             "lines": [77]},
            {"ku_id": "KU-a815459bcd3d5df0",
             "quote": "The value $p = 0.5$ was the original recommendation from the Dropout paper and remains the standard default for FC layers.",
             "source_path": C06,
             "lines": [343]},
            {"ku_id": "KU-c551b121821ab609",
             "quote": "Some modern architectures (ResNet, EfficientNet) achieve sufficient regularization through Batch Normalization alone and use $p = 0$.",
             "source_path": C06,
             "lines": [351]},
            {"ku_id": "KU-f454ef1318368321",
             "quote": "if you are using BN in a network, you should reduce the Dropout rate or remove Dropout entirely.",
             "source_path": C05,
             "lines": [533]},
        ],
        "rationale": (
            "Shared elements: (a) the strongest dropout belongs on the "
            "largest fully-connected/hidden layers, with weaker values "
            "elsewhere (master-ai hidden 0.3-0.5 + input 0.1-0.2; course "
            "FC 0.5 standard, conv 0.2-0.3 per its table at L355-360); "
            "(b) modern practice strongly reduces or omits dropout because "
            "other regularization suffices — master-ai attributes this to "
            "data scale in LLMs, the course to BatchNorm in ResNet/"
            "EfficientNet, and the course's file-05 guidance makes the "
            "reduce-when-BN-present rule explicit. Partial rather than "
            "semantic: the specific rate tables target different "
            "architectures (master-ai's transformer-focused input/attention/"
            "FFN values vs the course's CNN-focused FC/conv values), so "
            "the numbers are complementary context-specific guidance, not "
            "duplicates; only the shape of the guidance (strong on FC, "
            "light elsewhere, trending to zero in modern practice) is "
            "duplicated. Synthesis should keep both tables with their "
            "referents."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0015",
        "task_id": TASK_ID,
        "topic": "Dropout/regularizer placement: never on the output layer; concentrate where parameter count and overfitting risk are highest (the large FC layers)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b57933c8b5bce1f0", "KU-93c72dcb72560df5", "KU-62af384e5050dfdb"],
        "evidence": [
            {"ku_id": "KU-b57933c8b5bce1f0",
             "quote": "**Forgetting to apply regularization to all relevant layers** — typically you skip the output layer.",
             "source_path": M06,
             "lines": [183]},
            {"ku_id": "KU-93c72dcb72560df5",
             "quote": "Dropout should **never** be applied after the final output layer.",
             "source_path": C06,
             "lines": [374]},
            {"ku_id": "KU-62af384e5050dfdb",
             "quote": "**apply Dropout where overfitting risk is highest**, which typically means the largest fully connected layers.",
             "source_path": C06,
             "lines": [366]},
        ],
        "rationale": (
            "Shared claim: the output layer is excluded from dropout/"
            "regularization. Master-ai states it as a pitfall (skip the "
            "output layer); the course states it absolutely ('never') with "
            "the reasoning that zeroed predictions are meaningless. The "
            "concentrate-on-large-FC principle is explicit in the course "
            "(with the VGG-16 100M-parameter example at L370, course-only) "
            "and implicit in master-ai's rate table (hidden layers get the "
            "strongest values, OC-ext009-0014) — recorded as part of this "
            "cluster because the course's placement section and master-ai's "
            "pitfall govern the same placement decision. The course's "
            "Linear-ReLU-Dropout ordering convention (L378) is course-only."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0016",
        "task_id": TASK_ID,
        "topic": "Early stopping: halt training when validation loss stops improving (patience-based), and keep the checkpoint from the best-validation epoch",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-756e1177e18287d2", "KU-bf545b7a84be1551", "KU-e872f67a8b4b97b5", "KU-e0b8b7e81c307f9f", "KU-78e888bebd79929f"],
        "evidence": [
            {"ku_id": "KU-756e1177e18287d2",
             "quote": "Halt training when validation loss stops improving (or starts worsening)",
             "source_path": M06,
             "lines": [81]},
            {"ku_id": "KU-bf545b7a84be1551",
             "quote": "**The cheapest, most reliable regularizer.** Always use it unless you have a strong reason not to.",
             "source_path": M06,
             "lines": [99]},
            {"ku_id": "KU-e872f67a8b4b97b5",
             "quote": "monitor the validation loss during training, and stop training when the validation loss stops improving and starts increasing.",
             "source_path": C06,
             "lines": [474]},
            {"ku_id": "KU-e0b8b7e81c307f9f",
             "quote": "early stopping is implemented with a **patience** parameter: training continues until the validation loss has failed to improve for `patience` consecutive epochs.",
             "source_path": C06,
             "lines": [476]},
            {"ku_id": "KU-78e888bebd79929f",
             "quote": "you should always save the model weights from the epoch with the best validation loss, not from the final epoch.",
             "source_path": C06,
             "lines": [513]},
        ],
        "rationale": (
            "Both vaults teach the identical technique: stop at the "
            "validation-loss divergence, implement with patience, restore/"
            "keep the best-validation checkpoint. Master-ai's pseudocode "
            "(L83-97: best_val, patience, waited, save_checkpoint) and the "
            "course's implementation (L478-510: same structure plus "
            "load_state_dict at the end) are the same algorithm; the "
            "course's save-best-not-final callout matches master-ai's "
            "checkpoint saving. Vault-specific: master-ai's endorsement "
            "strength ('cheapest, most reliable regularizer... Always use "
            "it') has no course equivalent; the course's patience value "
            "guidance (5-20 epochs, L476) is course-only; master-ai's "
            "patience is 3 in pseudocode. Early stopping also appears as a "
            "course-range credit in OC-ext004-0010 (tree-domain, different "
            "sources) — consistent, not duplicative. Related: OC-ext009-0002 (the "
            "divergence point being monitored)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0017",
        "task_id": TASK_ID,
        "topic": "Label smoothing: replace one-hot targets with soft targets (smoothing ~0.1) to prevent overconfidence",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-e06059c050c4a443", "KU-6ae3e0a7a7570d68", "KU-ff2b20e6eedcb3d7", "KU-d003d59f52c01995", "KU-97ca84434b43aa8d"],
        "evidence": [
            {"ku_id": "KU-e06059c050c4a443",
             "quote": "Instead of one-hot targets `[0, 0, 1, 0]`, use smoothed targets `[0.033, 0.033, 0.9, 0.033]` (smoothing factor $\\epsilon = 0.1$).",
             "source_path": M06,
             "lines": [113]},
            {"ku_id": "KU-6ae3e0a7a7570d68",
             "quote": "- Prevents the model from becoming overconfident.\n- Acts as calibration regularization.",
             "source_path": M06,
             "lines": [115, 116]},
            {"ku_id": "KU-ff2b20e6eedcb3d7",
             "quote": "Label smoothing replaces hard 0/1 target labels with soft targets that distribute a small amount of probability mass across all classes.",
             "source_path": C06,
             "lines": [517]},
            {"ku_id": "KU-d003d59f52c01995",
             "quote": "$\\alpha$ is the smoothing parameter (typically 0.1)",
             "source_path": C06,
             "lines": [521]},
            {"ku_id": "KU-97ca84434b43aa8d",
             "quote": "Label smoothing prevents this by distributing some probability mass to incorrect classes, which prevents the logits from growing too large and encourages the model to maintain a small degree of uncertainty.",
             "source_path": C06,
             "lines": [523]},
        ],
        "rationale": (
            "Both vaults define label smoothing the same way — soft targets "
            "spreading probability mass across incorrect classes — with the "
            "same canonical strength (0.1) and the same purpose (prevent "
            "overconfidence; master-ai adds the calibration framing, the "
            "course the logit-magnitude mechanism). Both even illustrate "
            "with the same ~0.9-on-the-true-class example (master-ai "
            "4-class vector [0.033, 0.033, 0.9, 0.033]; course 10-class "
            "[0.01 x 9, 0.9] at L521). Vault-specific: master-ai's "
            "provenance (Szegedy et al. 2016, Inception) and "
            "used-in-some-LLM-training note (L117); the course's "
            "CrossEntropyLoss(label_smoothing=0.1) implementation (L525-544) "
            "and its robustness-to-distribution-shift rationale (L523). "
            "Notation differs (epsilon vs alpha) — presentational."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0018",
        "task_id": TASK_ID,
        "topic": "Batch normalization has a regularization side effect: the noise of mini-batch statistics acts like dropout-style noise and improves generalization (though weaker than dropout)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-882d3292c5bc7a61", "KU-702618d2571d4302", "KU-55ae61981a802fde"],
        "evidence": [
            {"ku_id": "KU-882d3292c5bc7a61",
             "quote": "BatchNorm normalizes activations using batch statistics. As a side effect, the noise from batch statistics acts as a regularizer.",
             "source_path": M06,
             "lines": [121]},
            {"ku_id": "KU-702618d2571d4302",
             "quote": "it acts as a regularizer, reducing overfitting even without explicit regularization techniques like Dropout.",
             "source_path": C05,
             "lines": [215]},
            {"ku_id": "KU-702618d2571d4302",
             "quote": "Each mini-batch computes its own mean and variance, which are noisy estimates of the true population statistics. This noise is injected into the normalization process",
             "source_path": C05,
             "lines": [215]},
            {"ku_id": "KU-55ae61981a802fde",
             "quote": "The regularizing effect of BN is not as strong as that of Dropout, which is why some practitioners still use both together.",
             "source_path": C05,
             "lines": [217]},
        ],
        "rationale": (
            "Both vaults make the same causal claim: BN's use of noisy "
            "mini-batch statistics injects noise that regularizes and "
            "improves generalization beyond its optimization benefits. "
            "Master-ai compresses it to two sentences; the course gives "
            "the mechanism (per-batch statistics as noisy estimates, "
            "analogous to dropout noise) and the strength comparison "
            "(milder than dropout — course-only). Vault-specific, "
            "course-only: the whole BN apparatus (ICS motivation, "
            "four-step math, running statistics, eval-mode mechanics, "
            "batch-size effects, GN/LN/IN alternatives, placement debate) "
            "has no master-ai counterpart in scope — master-ai's BN "
            "coverage is exactly this one paragraph plus the "
            "LayerNorm-preferred-in-Transformers note (L123), whose "
            "cross-vault counterpart (course file 05, L551) is recorded "
            "separately in OC-ext009-0026. The "
            "BN-with-dropout usage guidance is recorded in "
            "OC-ext009-0014."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0019",
        "task_id": TASK_ID,
        "topic": "Too much regularization causes underfitting: watch training loss and regularize less if it cannot decrease",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b57933c8b5bce1f0", "KU-f454ef1318368321"],
        "evidence": [
            {"ku_id": "KU-b57933c8b5bce1f0",
             "quote": "**Too much regularization** — underfits. Watch training loss; if it can't go down, regularize less.",
             "source_path": M06,
             "lines": [182]},
            {"ku_id": "KU-f454ef1318368321",
             "quote": "using full-strength Dropout alongside BN can result in over-regularization, where the model underfits because too much noise is injected during training.",
             "source_path": C05,
             "lines": [533]},
        ],
        "rationale": (
            "Both vaults state the over-regularization -> underfitting "
            "principle. Master-ai states it as a general pitfall with the "
            "diagnostic (training loss cannot go down); the course states "
            "it in the specific BN+Dropout combination context. The shared "
            "claim is the principle itself; the contexts are complementary "
            "and both must be preserved at synthesis. Master-ai's "
            "underfitting concept more broadly (high-bias regime, its "
            "diagnosis and fixes at L26-33, 85-94 of the bias-variance "
            "file) has no course-side counterpart in scope — the course "
            "only underfit-family wording in these three files is the verb "
            "'underfits' inside this very quote; the noun 'underfitting' "
            "and its diagnosis apparatus are master-only (probe-verified "
            "in the term map: 'underfitting'/'underfit' master-ai only)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0020",
        "task_id": TASK_ID,
        "topic": "Regularization deliberately trades training performance for generalization: a regularized model can be better despite lower training accuracy",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a3d5d1f07d12fb4f", "KU-05daab826792e22c"],
        "evidence": [
            {"ku_id": "KU-a3d5d1f07d12fb4f",
             "quote": "Regularization trades a small increase in training loss for a larger reduction in test loss",
             "source_path": M06,
             "lines": [15]},
            {"ku_id": "KU-05daab826792e22c",
             "quote": "the regularized model is actually better — it generalizes more reliably even though its training accuracy is lower.",
             "source_path": C06,
             "lines": [50]},
        ],
        "rationale": (
            "Both vaults state the core bargain of regularization: accept "
            "worse training metrics to gain generalization. Master-ai "
            "states it as the general trade; the course demonstrates it "
            "with the 92/88 vs 89/89 example (in the same callout as the "
            "quote) and generalizes to 'Always compare validation metrics, "
            "not training metrics' — course-only operationalization. "
            "Master-ai's mechanism list for the trade (limiting capacity, "
            "adding noise, encouraging simpler solutions, L16-18) "
            "overlaps the course's noise-injection framing but is kept "
            "here as rationale context rather than separate evidence "
            "because the course states no capacity-limiting mechanism "
            "list."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0021",
        "task_id": TASK_ID,
        "topic": "Data augmentation: artificially expand the training set with label-preserving transformations; the practical remedy when data is limited, especially for vision",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-40510aab1d3530df", "KU-ef3a7b46104d1929", "KU-02809b63c8feef72", "KU-37ae54e552881289", "KU-9d3544c2dcde095a"],
        "evidence": [
            {"ku_id": "KU-40510aab1d3530df",
             "quote": "Artificially expand the training data via label-preserving transformations",
             "source_path": M06,
             "lines": [103]},
            {"ku_id": "KU-ef3a7b46104d1929",
             "quote": "Effective when data is limited. Especially powerful for vision — ImageNet training relies heavily on augmentation.",
             "source_path": M06,
             "lines": [109]},
            {"ku_id": "KU-02809b63c8feef72",
             "quote": "Data augmentation is the practice of artificially expanding a training dataset by applying transformations to existing training images",
             "source_path": C07,
             "lines": [5]},
            {"ku_id": "KU-37ae54e552881289",
             "quote": "Data augmentation is the most practical way to increase effective data size.",
             "source_path": C07,
             "lines": [21]},
            {"ku_id": "KU-9d3544c2dcde095a",
             "quote": "data augmentation often improves validation accuracy by 2–5 percentage points with virtually no downside.",
             "source_path": C07,
             "lines": [28]},
        ],
        "rationale": (
            "Near-verbatim definition match: master-ai 'Artificially expand "
            "the training data via label-preserving transformations' vs "
            "course 'artificially expanding a training dataset by applying "
            "transformations to existing training images' — the shared "
            "claim includes the label-preserving condition (the course "
            "states it as the domain-awareness rule, 'does the resulting "
            "image still have the same label?', L120-121). Both also agree "
            "on positioning: the remedy when data is limited / the "
            "practical way to increase effective data, especially in "
            "vision (master-ai: ImageNet reliance; course: CNN-focused "
            "treatment). Vault-specific: master-ai's text/audio modality "
            "lists (L106-107) are master-only in scope; the course's "
            "invariance-teaching philosophy (L15), 'doubles the dataset' "
            "flip arithmetic (L40), and cost framing (essentially free, "
            "L28) are course-only. Related: OC-ext009-0022 (the technique "
            "inventory), OC-ext009-0025 (train-only rule)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0022",
        "task_id": TASK_ID,
        "topic": "The standard vision-augmentation inventory: flips, crops, rotation, color jitter (plus mixup/cutmix as advanced image techniques)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a787b4fbedd9be3d", "KU-4175c9f4f8f2a4c5"],
        "evidence": [
            {"ku_id": "KU-a787b4fbedd9be3d",
             "quote": "- **Images**: flip, crop, rotate, color jitter, mixup, cutmix.",
             "source_path": M06,
             "lines": [105]},
            {"ku_id": "KU-4175c9f4f8f2a4c5",
             "quote": "Geometric transformations (flips, crops, rotations) modify the spatial arrangement of pixels, while pixel-level transformations (color jitter, Gaussian noise, random erasing) modify intensity values.",
             "source_path": C07,
             "lines": [734]},
            {"ku_id": "KU-4175c9f4f8f2a4c5",
             "quote": "Advanced augmentation techniques like Mixup, CutMix, and RandAugment provide further gains by combining images or using learned augmentation policies.",
             "source_path": C07,
             "lines": [734]},
        ],
        "rationale": (
            "Master-ai's six-item image list (flip, crop, rotate, color "
            "jitter, mixup, cutmix) is item-for-item covered by the "
            "course's dedicated sections and summary: geometric flips/"
            "crops/rotations, pixel-level color jitter, and the advanced "
            "mixup/cutmix category. The shared claim is that these are the "
            "standard vision augmentations. Depth differs massively "
            "(master-ai: one list line; course: three files' worth of "
            "per-technique treatment) — depth is not a type criterion. "
            "Vault-specific: the course's Gaussian noise / random erasing / "
            "RandAugment / RandomResizedCrop-parameter coverage and "
            "domain-caution table (L717-728) are course-only; master-ai's "
            "mechanics for mixup/cutmix are NOT stated in scope (its "
            "in-scope content is the list entry plus a paper citation at "
            "L190) — so no separate mixup/cutmix-mechanics record exists; "
            "the course's mixup formula (L242-243) and cutmix area-weighted "
            "labeling (L249) are course-only elaborations."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0023",
        "task_id": TASK_ID,
        "topic": "Averaging multiple models (ensembling/bagging) yields more accurate, more robust predictions than any single model",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-3600ad4fde6afdfc", "KU-35c47d029dfcff49"],
        "evidence": [
            {"ku_id": "KU-3600ad4fde6afdfc",
             "quote": "Bagging (random forests, gradient boosting) trains many high-variance models and averages them. Variance scales down as $1/\\sqrt{M}$ with $M$ independent models.",
             "source_path": M01,
             "lines": [66]},
            {"ku_id": "KU-35c47d029dfcff49",
             "quote": "Ensemble averaging is a well-established technique in machine learning: the average prediction of many models is consistently more accurate and more robust than the prediction of any single model.",
             "source_path": C06,
             "lines": [115]},
        ],
        "rationale": (
            "Shared element: the claim that averaging many models beats any "
            "single model. Master-ai grounds it quantitatively in "
            "bias-variance theory (variance ~ sigma^2/M scaling, bagging "
            "as the classical instance, random forests as decorrelated "
            "averaging); the course grounds it qualitatively in error "
            "cancellation ('different models make different errors') in "
            "the dropout-as-ensemble context. Partial rather than "
            "semantic: the master-ai claim is the variance-reduction "
            "theorem with a 1/sqrt(M) rate; the course claim is the "
            "robustness intuition without rates — same conclusion, "
            "different evidential depth and context. The averaging-reduces-"
            "variance family also appears tree/RF-scoped in the tree "
            "domain — OC-ext004-0005 (averaging many trees reduces "
            "variance), OC-ext004-0016 (bagging mechanics), and "
            "OC-ext004-0026 (RF ensemble formula vs the course-side "
            "sigma^2/B variance analysis) — those records "
            "are scoped to tree ensembles with disjoint sources; this "
            "record is the general claim. Both connect to "
            "OC-ext009-0013 (dropout as implicit ensembling): master-ai "
            "explicitly ('Like bagging, but at the activation level'), the "
            "course as approximate ensemble average. Master-ai's "
            "production note (ensembling expensive but reliable, L117) is "
            "master-only."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0024",
        "task_id": TASK_ID,
        "topic": "Complementary framings of the overfitting phenomenon: master-ai's bias-variance decomposition apparatus vs the course's memorization/train-gap framing",
        "overlap_type": "Complementary Content",
        "ku_ids": ["KU-93065c9a5a291a96", "KU-92a81afc5b276bf8"],
        "evidence": [
            {"ku_id": "KU-93065c9a5a291a96",
             "quote": "Every model's error decomposes into **bias** (systematic error from too simple a model) + **variance** (sensitivity to the training sample) + **irreducible noise**. Underfit = high bias; overfit = high variance.",
             "source_path": M01,
             "lines": [12]},
            {"ku_id": "KU-92a81afc5b276bf8",
             "quote": "the model has memorized the training examples — including their noise and idiosyncrasies — rather than learning the underlying patterns that would allow it to make accurate predictions on new inputs.",
             "source_path": C06,
             "lines": [13]},
        ],
        "rationale": (
            "Complementary Content per ADR-0009: the two vaults explain the "
            "same phenomenon with different conceptual apparatus, and both "
            "apparatuses must survive synthesis. Master-ai possesses the "
            "full theoretical machinery — the decomposition formula, its "
            "derivation and assumptions, the U-curve, double descent, "
            "LLM-era complications — none of which the course states in "
            "these three files (the term map probe found 'bias-variance' "
            "as a phrase only in master-ai). The course possesses the "
            "practical framing — memorization including noise, the "
            "student analogy (L17), the numeric gap calibration — and "
            "never invokes decomposition language. This is not a "
            "duplication (the claims are about the same phenomenon but "
            "assert different content) nor a mere gap: the two framings "
            "are complementary teaching of one concept, the EXT-005 "
            "OC-0025 calibration precedent. Synthesis should merge the "
            "phenomenon while keeping both the theoretical and practical "
            "presentations."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0025",
        "task_id": TASK_ID,
        "topic": "Complementary evaluation-data hygiene rules: master-ai's leakage discipline (tune on validation, evaluate once on test) vs the course's deterministic-transforms rule (never augment validation/test data)",
        "overlap_type": "Complementary Content",
        "ku_ids": ["KU-7b051b86c10d5da1", "KU-e505772836e129f9", "KU-3ef4ccdf82541f8b"],
        "evidence": [
            {"ku_id": "KU-7b051b86c10d5da1",
             "quote": "**Tuning hyperparameters on the test set** — leakage. Always tune on validation, evaluate once on test.",
             "source_path": M01,
             "lines": [122]},
            {"ku_id": "KU-e505772836e129f9",
             "quote": "**random augmentations must only be applied to training data**, never to validation or test data.",
             "source_path": C07,
             "lines": [262]},
            {"ku_id": "KU-3ef4ccdf82541f8b",
             "quote": "Random augmentations make the validation loss and accuracy stochastic — the same model evaluated twice on the same data could produce different results.",
             "source_path": C07,
             "lines": [378]},
        ],
        "rationale": (
            "Complementary Content: both rules protect the integrity of "
            "held-out evaluation data, but they guard against different "
            "failure modes. Master-ai's rule prevents selection leakage "
            "(hyperparameter tuning on the test set); the course's rule "
            "prevents stochastic contamination (random transforms making "
            "validation metrics non-reproducible, defeating overfitting "
            "detection, model comparison, and checkpoint selection). "
            "Neither vault states the other's rule in scope, and neither "
            "rule subsumes the other — a synthesis that kept only one "
            "would lose a genuine protection. This follows the EXT-005 "
            "OC-0025 precedent of recording complementary treatments of "
            "one topic (here: evaluation-set hygiene). The master-ai "
            "test-set discipline quoted here also anchors OC-ext005-0029 "
            "in the evaluation domain (same master-ai source file, "
            "different course counterpart) — consistent, not duplicative. "
            "Related: "
            "OC-ext009-0002 (why trustworthy validation metrics matter)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext009-0026",
        "task_id": TASK_ID,
        "topic": "LayerNorm (not BatchNorm) is the standard normalization for Transformer/sequence architectures, because sequence lengths and batch statistics vary",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-bbd3111786c76e44", "KU-c35e357516d553a7"],
        "evidence": [
            {"ku_id": "KU-bbd3111786c76e44",
             "quote": "in NLP/Transformers, BatchNorm is rarely used — LayerNorm/RMSNorm is preferred because sequence lengths vary",
             "source_path": M06,
             "lines": [123]},
            {"ku_id": "KU-c35e357516d553a7",
             "quote": "Layer Normalization is the standard choice for Transformer architectures and sequence models, where batch sizes may vary and the concept of \"batch statistics\" is less meaningful",
             "source_path": C05,
             "lines": [551]},
        ],
        "rationale": (
            "Both vaults state the same preference claim: for "
            "Transformer/sequence architectures, LayerNorm is the "
            "standard and BatchNorm is not. Master-ai states it as a "
            "one-line note (BatchNorm rarely used; LayerNorm/RMSNorm "
            "preferred because sequence lengths vary); the course "
            "states it as the concluding sentence of its Layer "
            "Normalization subsection (the standard choice for "
            "Transformer architectures and sequence models, where "
            "batch sizes may vary and 'batch statistics' is less "
            "meaningful). The differently-phrased reasons (sequence "
            "lengths vs batch sizes) are the same underlying fact — "
            "normalization statistics that vary with the input "
            "composition — aimed at NLP vs CV audiences. "
            "Vault-specific: master-ai's RMSNorm mention and its "
            "See-Also link to the Transformers Normalization Layers "
            "note are master-only; the course's per-sample statistics "
            "mechanics (mean/variance over the C x H x W elements of "
            "each sample), its deterministic-normalization remark, "
            "and the GN/IN alternatives context are course-only. "
            "Related: OC-ext009-0018 (the same master-ai section's "
            "BN-regularization claim, where this note's "
            "cross-vault counterpart was first disclosed). Record "
            "added as OC-ext009-0026 at review per EXT-009-REVIEW "
            "CG-1/R1: the cluster was surfaced by CAP-013 discovery "
            "under both the 'transformer' and 'normalization' topics "
            "but had no record, and OC-ext009-0018's earlier "
            "rationale wrongly called the note master-only."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
]


def load_kus() -> dict[str, dict]:
    kus: dict[str, dict] = {}
    for path in BATCHES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                kus[r["knowledge_unit_id"]] = r
    return kus


def source_root(source_id: str) -> Path:
    vault = source_id.split(":", 1)[0]
    sub = "Master AI" if vault == "master-ai" else "AI Course"
    return REPO / "source-vaults" / "AI " / sub


def committed_hashes() -> dict[str, str]:
    return {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in COMMITTED
    }


def main() -> int:
    failures: list[str] = []
    kus = load_kus()
    hashes_before = committed_hashes()

    for rec in RECORDS:
        cid = rec["classification_id"]
        # X5: KU ids exist.
        for kid in rec["ku_ids"]:
            if kid not in kus:
                failures.append(f"{cid}: unknown KU id {kid}")
        # X4: evidence ku_ids == record ku_ids.
        ev_ids = {e["ku_id"] for e in rec["evidence"]}
        if ev_ids != set(rec["ku_ids"]):
            failures.append(f"{cid}: evidence ku_ids != record ku_ids")
        # X3: cross-vault.
        vaults = {kus[k]["source_id"].split(":")[0]
                  for k in rec["ku_ids"] if k in kus}
        if vaults != {"ai-course", "master-ai"}:
            failures.append(f"{cid}: not cross-vault ({vaults})")
        for ev in rec["evidence"]:
            ku = kus.get(ev["ku_id"])
            if ku is None:
                continue
            # X1: byte-exact inside the KU excerpt.
            if ev["quote"] not in ku["excerpt"]:
                failures.append(f"{cid}: quote NOT byte-exact in excerpt of "
                                f"{ev['ku_id']}: {ev['quote'][:80]!r}")
            # X1b: evidence source_path must equal the KU's source_path.
            if ev["source_path"] != ku["source_path"]:
                failures.append(f"{cid}: source_path mismatch for {ev['ku_id']}")
            # X2: byte-exact at the stated ORIGINAL source lines.
            src = source_root(ku["source_id"]) / ku["source_path"]
            lines = src.read_text(encoding="utf-8").splitlines()
            lo, hi = min(ev["lines"]), max(ev["lines"])
            if not (1 <= lo <= hi <= len(lines)):
                failures.append(f"{cid}: line range {lo}-{hi} outside "
                                f"{ku['source_path']} ({len(lines)} lines)")
                continue
            # every stated line must lie inside the KU's own span
            if not (ku["line_start"] <= lo and hi <= ku["line_end"]):
                failures.append(f"{cid}: stated lines {lo}-{hi} outside KU span "
                                f"{ku['line_start']}-{ku['line_end']} for {ev['ku_id']}")
            slice_text = "\n".join(lines[lo - 1: hi])
            if ev["quote"] not in slice_text:
                failures.append(f"{cid}: quote NOT at stated source lines "
                                f"{ev['lines']} of {ku['source_path']}: {ev['quote'][:80]!r}")
        # duplicate evidence entries within record
        quotes = [e["quote"] for e in rec["evidence"]]
        if len(quotes) != len(set(quotes)):
            failures.append(f"{cid}: duplicate evidence quotes within record")

    # X7: unique, sequential ids.
    ids = [r["classification_id"] for r in RECORDS]
    if len(ids) != len(set(ids)):
        failures.append("duplicate classification ids")
    for i, cid in enumerate(ids, start=1):
        if not cid.endswith(f"-{i:04d}"):
            failures.append(f"non-sequential id {cid}")

    # X8: no duplicate quote strings anywhere in the file.
    all_quotes = [e["quote"] for r in RECORDS for e in r["evidence"]]
    if len(all_quotes) != len(set(all_quotes)):
        seen: set[str] = set()
        for q in all_quotes:
            if q in seen:
                failures.append(f"duplicate quote across file: {q[:80]!r}")
            seen.add(q)

    # X6: schema validation.
    import jsonschema
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for rec in RECORDS:
        for err in validator.iter_errors(rec):
            failures.append(f"{rec['classification_id']}: schema: "
                            f"{err.message} at {list(err.absolute_path)}")

    if failures:
        print("VERIFICATION FAILURES:")
        for f in failures:
            print("  -", f)
        return 1

    # X9: committed classification files byte-unchanged (we never touch them;
    # assert the hashes recorded before the run still match after validation).
    hashes_after = committed_hashes()
    for p, h in hashes_before.items():
        if hashes_after[p] != h:
            print(f"X9 FAILURE: committed file changed during run: {p}")
            return 1

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                for r in RECORDS),
        encoding="utf-8",
    )
    types: dict[str, int] = {}
    for r in RECORDS:
        types[r["overlap_type"]] = types.get(r["overlap_type"], 0) + 1
    participating = sorted({k for r in RECORDS for k in r["ku_ids"]})
    print(f"wrote {OUT.relative_to(REPO)}: {len(RECORDS)} records "
          f"({', '.join(f'{v} {k}' for k, v in sorted(types.items()))}), "
          f"{len(participating)} participating KUs, "
          f"{sum(len(r['evidence']) for r in RECORDS)} byte-exact quotes "
          f"(all verified in excerpts AND at original source lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
