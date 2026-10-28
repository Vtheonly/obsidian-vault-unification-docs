#!/usr/bin/env python3
"""DISC-002 round-2 (r2) individual semantic review decisions.

Every decision below was made by the orchestrator from the candidate's own
evidence quotes (see reports/discovery/disc002-triage.json and the review
brief), with coverage cross-checks against already_covered anchor terms.
Rationale fields cite the specific evidence behind each decision.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "state/concept-candidates/002b-disc002-decisions-r2.jsonl"
DECIDED_UTC = "2026-10-28T01:30:00Z"
REVIEWER = "orchestrator-glm (individual evidence review)"

D = []


def dec(cid, action, rationale):
    D.append(
        {
            "candidate_id": cid,
            "decision_id": f"D002-R2-{cid}",
            "action": action,
            "rationale": rationale,
            "reviewer": REVIEWER,
        }
    )


# ---- CONFIRM_GAP: real gaps at complete coverage (first confirmed gaps) ----
dec(
    "CG-fe05f71fc6ba",
    "confirm_gap",
    "second moment: 23 independent contexts across both vaults use the moment "
    "concept (Adam beta_2, first/second moment accumulators, bias correction) "
    "with only in-passing glosses; the underlying statistical prerequisite "
    "(what a moment is, E[x], E[x^2], why an exponential moving average "
    "estimates it, why bias correction is needed) is never assembled. "
    "Destination: section in the math-foundations/optimizer treatment.",
)
dec(
    "CG-c8f6e1408dc2",
    "confirm_gap",
    "bradley-terry: 17 contexts with 9 derivation-position uses spread across "
    "three different master-ai math notes (Probability Essentials, Estimators "
    "and Bias, Entropy/Cross-Entropy/KL) while the definition exists only as "
    "a single line ('The Bradley-Terry model converts rewards to "
    "probabilities:'). The scattered BT likelihood/estimation fragments need "
    "one coherent section in the reward-model/RLHF treatment. Note: "
    "'bradley-terry model' is already_covered — the confirmed gap is the "
    "fragmentation, not the absence of any definition.",
)

# ---- DEFER: real families needing collective mapping before decision ----
dec(
    "CG-6528c7ae4dfe",
    "defer",
    "3d tensor: 21 cross-vault contexts, but bare 'tensor' is already_covered "
    "(387 contexts, 12 definition sites). The residual gap is the shape-"
    "convention material (HWC/CHW ordering, framework conventions, shape "
    "tracking through ops) which must be decided together with the sibling "
    "candidates 'tensor shape' (15 ctx), 'shape mismatch' (9 ctx) and the "
    "flattening/resizing family as one family review before choosing section "
    "vs standalone destination.",
)
dec(
    "CG-d58dff88b362",
    "defer",
    "log-softmax: 4 cross-vault contexts; partial inline treatments exist "
    "(loss note explains the stable computation; info-theory note warns "
    "against naive log(softmax)). Must be mapped with 'log-sum-exp' "
    "(CG-084bafd573c2, 8 ctx, provisional) and the already_covered "
    "'logsumexp'/'numerical stability' anchors as one numerical-stability "
    "family review: the family may already be adequately covered inside the "
    "covered anchors' notes.",
)
dec(
    "CG-b317cb629210",
    "defer",
    "reference policy: 14 contexts, derivation-heavy, all in master-ai math "
    "notes that USE the KL-anchored reference policy while the RLHF chapter "
    "('12 - Fine-Tuning/RLHF') and PPO notes plausibly define it. Next "
    "session must check the RLHF chapter's actual coverage before deciding "
    "cover vs confirm_gap.",
)
dec(
    "CG-86477f057e79",
    "defer",
    "ssd framework: 19 contexts in research-frontier/architecture notes using "
    "Mamba-2's state-space-duality framework; 'mamba-2' itself is "
    "already_covered (127 ctx, 12 defs). Next session must check the "
    "Mamba-2/SSD paper notes in '26 - Papers' before deciding cover vs "
    "confirm_gap.",
)

# ---- COVER: paraphrased/variant treatments exist (false positive gaps) ----
dec(
    "CG-08acb0b7a1a1",
    "cover",
    "relu activation: bare 'relu' is already_covered with 528 contexts and 12 "
    "definition sites; the vanishing-gradient/ReLU material this candidate "
    "collects lives inside that covered treatment. The lexical detector "
    "missed the definitions because they are table/list/mermaid formatted.",
)
dec(
    "CG-b473663fb61d",
    "cover",
    "l2 norm: the ai-course Mathematical Notation note defines it explicitly "
    "('Name: L2 Norm Squared ... General Definition: the Norm measures the "
    "length (magnitude) of a vector') in list format the definition patterns "
    "do not match; gradient-clipping notes additionally explain ||g|| "
    "computation. Covered.",
)
dec(
    "CG-c77b5b7b5952",
    "cover",
    "proper initialization: 'weight initialization' is already_covered (52 "
    "ctx, 11 defs) and the corpus has a dedicated Weight Initialization note "
    "(evidence itself links [[14. Weight In...]]); the training-stability "
    "dossier already includes initialization concepts.",
)
dec(
    "CG-704d8cf33aba",
    "cover",
    "upstream gradient: the backpropagation deep-dive file defines the "
    "convention at point of use ('the upstream gradient (the gradient "
    "flowing in from the layer above)') and uses it coherently across conv "
    "and pool backward passes within one dedicated treatment.",
)
dec(
    "CG-d6246bf8c7bd",
    "cover",
    "true convolution: the Convolution Operation Deep Dive gives the "
    "dedicated treatment — both formulas (true convolution vs "
    "cross-correlation), kernel flipping, the learnability argument, and the "
    "framework-convention caveat; 'cross-correlation' is already_covered.",
)
dec(
    "CG-ead2d1c4459f",
    "cover",
    "agent memory: master-ai has a dedicated '18 - Memory Systems' chapter "
    "(MOC, memory operations write/read/consolidate/decay/forget defined, "
    "MemGPT/Letta notes); 'memory operations' is already_covered (18 ctx, 4 "
    "defs).",
)
dec(
    "CG-e6b0487a7cfc",
    "cover",
    "cross entropy: hyphenation variant of 'cross-entropy' which is "
    "already_covered (182 contexts, 12 definition sites). Same concept, "
    "different surface form.",
)

# ---- REJECT: generic phrases, terminology, n-gram fragments, variants ----
_REJECTS = [
    ("CG-0a5d5946b737", "spatial position", "generic spatial-language phrase inside convolution/CNN mechanics; the stride/receptive-field content belongs to the convolution-operation treatment"),
    ("CG-74fc3287cde1", "different models", "generic comparative phrase spanning unrelated contexts (ensembles, color models, quizzes); not a concept"),
    ("CG-41d4bc5b6d48", "large batches", "comparative phrase; 'batch size' is already_covered (149 ctx, 12 defs) and the batch-size tradeoff content (flat minima, GPU utilization) belongs to that treatment"),
    ("CG-ac4ff159bdb0", "true class", "loss-function terminology (one-hot target class); part of the covered cross-entropy/one-hot material ('one-hot' already_covered, 45 ctx)"),
    ("CG-7d1712753acd", "val loss", "train/val methodology terminology; 'validation set' and 'early stopping' are already_covered; the train-vs-val curve content belongs to the overfitting/early-stopping treatment"),
    ("CG-0e2ae3f77c42", "validation loss", "same rationale as 'val loss': terminology of the covered validation/early-stopping material, 47 contexts notwithstanding"),
    ("CG-e74352b406e7", "majority class", "class-imbalance terminology (baseline predictor, accuracy paradox); belongs to the evaluation-metrics/imbalance treatment (evaluation dossier exists)"),
    ("CG-30c2a835f7ca", "large learning", "n-gram fragment of 'large learning rate'; 'learning rate' is already_covered (312 ctx, 12 defs)"),
    ("CG-c547c0d7df30", "previous step", "generic phrase (momentum's previous update, zero_grad semantics, pipeline steps); not a concept"),
    ("CG-3d52edf9c1f2", "evaluation metric", "covered by the evaluation domain (evaluation dossier with 33 concepts exists); the metric-vs-loss distinction is content within it"),
    ("CG-6a5fe2d454b9", "input activations", "generic phrase; the internal-covariate-shift content lives in the Batch Normalization notes which define the distribution-shift phenomenon"),
    ("CG-b72f93413bec", "different normalization", "comparative phrase; the ImageNet-normalization convention is transfer-learning content within the covered transfer-learning notes"),
    ("CG-6a203a2eeffe", "entire dataset", "generic phrase of batch/stochastic gradient-descent comparisons; covered by the gradient-descent material"),
    ("CG-975f30dec2e6", "human preferences", "generic phrase; the preference-learning concept is carried by the reward-model/Bradley-Terry treatment (see CG-c8f6e1408dc2)"),
    ("CG-8e8df9a27c43", "final linear", "n-gram fragment of 'final linear layer'; classifier-head content within transfer-learning/logits material"),
    ("CG-aa57752fabfb", "final linear layer", "classifier-head terminology; the logits/softmax/cross-entropy pipeline content is covered by the loss-function and transfer-learning treatments"),
    ("CG-cee7028d2159", "output step", "decoder time-step terminology of the attention/encoder-decoder material; not a standalone concept"),
    ("CG-8f86aa1d168c", "pil image", "library type name; the PIL/tensor conversion content is data-pipeline content within the augmentation/transform notes"),
    ("CG-5778a68ac024", "imagefolder", "torchvision class name; dataset-loading convention content within the training-pipeline notes"),
    ("CG-c2c6c4df02f8", "last convolutional layer", "Grad-CAM procedure step; interpretability content within the dedicated CNN-interpretability treatment"),
    ("CG-8b24892653ab", "last conv", "same rationale as 'last convolutional layer' (Grad-CAM procedure step, interpretability content)"),
    ("CG-455246920c86", "current mini-batch", "generic phrase; 'mini-batch' is already_covered (65 ctx, 9 defs); batch-statistics content lives in the BatchNorm/optimizer notes"),
    ("CG-57117ca90d2b", "llm call", "infrastructure terminology (cost/latency/tracing of calls); the observability content belongs to the production-AI/LLMOps treatments which discuss it in its proper context"),
    ("CG-f85359d746fb", "human eye", "perceptual rationale phrase (luminance sensitivity, cone density); the chroma-subsampling/graystone-weighting content belongs to the color-space and compression treatments"),
    ("CG-a6f4cc0b729e", "mamba-2's ssd framework", "possessive surface variant of the 'ssd framework' candidate (CG-86477f057e79, deferred for the family decision); mining artifact of the same concept"),
    ("CG-94f6e34bb3b9", "eagle-2's", "possessive surface variant; 'eagle-2' is already_covered (43 ctx, 2 defs)"),
    ("CG-b84b31b2ccde", "first convolution", "architecture-description phrase ('the first convolution in the block'); residual-block content within the covered CNN architecture treatments"),
    ("CG-e772086a7ed7", "random augmentations", "phrase of the covered data-augmentation concept (dedicated Data Augmentation note exists); the never-on-validation rule is content within it"),
    ("CG-cb26aa1f8f6d", "activation derivative", "f'(z) notation within the vanishing/exploding gradient product analysis; the dedicated notes derive the product formula where it is used"),
    ("CG-a68d2e72ea1d", "imagenet pre-trained", "transfer-learning content (pretrained weights + normalization conventions) within the covered transfer-learning treatment"),
    ("CG-674582e99f4e", "tool arguments", "tool-calling validation content within the dedicated Function Calling / hallucination notes (evidence quotes are from those notes themselves)"),
]
for cid, term, why in _REJECTS:
    dec(cid, "reject", f"{term}: {why}")

with open(OUT, "w", encoding="utf-8") as fh:
    for d in D:
        fh.write(json.dumps(d, sort_keys=True, ensure_ascii=False) + "\n")

from collections import Counter
print(Counter(d["action"] for d in D), "total:", len(D))
