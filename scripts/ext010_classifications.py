#!/usr/bin/env python3
"""EXT-010: training-stability domain classifications.

Generates state/classifications/007-ext010-training-stability-overlap.jsonl
from batches 010 (master-ai '04 - Neural Networks/Training' files 07
Initialization Schemes + 08 Vanishing and Exploding Gradients, 2 files, 117
KUs) and 011 (ai-course '04.3 - Training Dynamics and Stability' files 01
Weight Initialization + 02 Weight Initialization Techniques + 03 The
Vanishing and Exploding Gradient Problems, 3 files, 382 KUs), over the
CAP-013 discovery output (reports/extraction/ext010-overlap-candidates.json:
7486 pairs, 68 cross-vault topics, 21 topics truncated at the 250-pair cap).

Overlap judgments: 36 records (32 Semantic Duplicate, 3 Partial Overlap,
1 Complementary Content), each with byte-exact quote evidence.

Verification before writing (exit non-zero on ANY failure):
  X1  every evidence quote is a byte-exact substring of the referenced KU's
      excerpt in the new batch files;
  X1b evidence source_path equals the KU's source_path;
  X2  every evidence quote is MACHINE-LOCATED at its original source lines:
      the locator finds every occurrence of the quote in the source file,
      keeps occurrences fully inside the KU's own span, requires EXACTLY ONE
      in-span occurrence, records the covered line range, and re-verifies
      the quote byte-exact inside the joined slice of those lines
      (EXT-005-REVIEW precedent, 0 tolerance). Lines are LOCATED by the
      script, never hand-typed — eliminating the hand-typed line-number
      error class found by EXT-009-REVIEW (R2);
  X3  every record is cross-vault (both ai-course and master-ai in ku_ids);
  X4  evidence ku_ids == record ku_ids exactly;
  X5  every KU id exists in the new batches;
  X6  the record set validates against schemas/overlap-classification.schema.json;
  X7  classification ids are unique and sequential;
  X8  no duplicate quote strings anywhere in the file;
  X9  committed classification files 001-006 are byte-unchanged (append-only);
  X10 (post-write, registry step) kureg-apply-overlap accepts the file.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCHES = [
    REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl",
    REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl",
]
COMMITTED = [
    REPO / "state/classifications/001-ext003-regression-overlap.jsonl",
    REPO / "state/classifications/002-ext004-tree-based-overlap.jsonl",
    REPO / "state/classifications/003-ext005-evaluation-overlap.jsonl",
    REPO / "state/classifications/004-ext007-evaluation-addendum.jsonl",
    REPO / "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl",
    REPO / "state/classifications/006-ext009-generalization-overlap.jsonl",
]
OUT = REPO / "state/classifications/007-ext010-training-stability-overlap.jsonl"
SCHEMA = REPO / "schemas/overlap-classification.schema.json"

CLASSIFIED_BY = "EXT-010 orchestrator (Z AI / GLM 5.3 session, 2026-10-27)"
DATE = "2026-10-27"
TASK_ID = "EXT-010"

M07 = "04 - Neural Networks/Training/07 - Initialization Schemes.md"
M08 = "04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md"
C01 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md"
C02 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md"
C03 = "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md"

METHOD = (
    "Evidence-based classification per EXT-003..009 pattern: CAP-013 discovery over "
    "batches 010+011 (reports/extraction/ext010-overlap-candidates.json, 7486 pairs, "
    "68 cross-vault topics, 21 truncated at the 250-pair cap) was read against both "
    "batches' KU excerpts (full digest review of all 117 master-ai KUs and all 382 "
    "ai-course KUs) and the original source lines; overlap clusters were judged per "
    "docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (pair-level relationship types, "
    "separate from disposition). Every evidence quote is a byte-exact fragment "
    "verified inside the KU excerpt AND machine-located at its exact original source "
    "lines before writing (chain X1-X10 in this script; lines are LOCATED by the "
    "script, not hand-typed - eliminating the hand-typed line-number error class "
    "found by EXT-009-REVIEW R2). Single-vault elaborations are recorded inside "
    "rationales as vault-specific content, not as separate cross-vault records: "
    "master-ai-only in scope - the transformer init recipe (GPT-2 std 0.02, "
    "embedding d_model^-1/2, residual scaling 1/sqrt(2N), zero unembedding with the "
    "log(vocab) initial-loss rationale, pre-norm), LoRA A-Kaiming/B-zero specifics "
    "(code, failure-table row, interview rationale), MuP / Tensor Programs / Fixup, "
    "bias-init specials (LSTM forget gate 1.0, output-layer inverse class "
    "frequency, final unembedding zeros), the GELU/SiLU extension of He init, the "
    "LSTM/GRU gated-architecture and attention-as-solution families (the course's "
    "four solutions do not include them), transformer-specific explosion contexts "
    "(QK^T scaling and softmax saturation, FP16 attention instability, 50+-layer "
    "residual dependence, GPT/Llama/Mistral recipe naming), the spectral-radius / "
    "eigenvalue formalism, the 20-layer MNIST worked table, and the Hochreiter "
    "1991 / Pascanu 2013 references; ai-course-only in scope - the non-convex "
    "loss-landscape treatment (2^N saddle-point estimate, parachute analogy), the "
    "volume-knob and telephone analogies, the N(0,0.01)/N(0,1) numeric variance "
    "analyses (512-wide layer: Var 0.0512 / 512; saturation-induced vanishing for "
    "N(0,1)), the Goldilocks naming, the sigmoid 0.25 maximization derivation and "
    "per-point derivative values, the tanh derivative table, the alpha^(L-l) "
    "compounding table, dying-ReLU probability/mechanics detail, the PReLU/ELU/SELU/"
    "LeCun variant coverage, orthogonal and sparse init implementations, the "
    "BatchNorm gamma=1/beta=0 default rationale, the BN partners-not-substitutes and "
    "reduces-init-sensitivity treatment, the when-init-matters-vs-not conditions "
    "(shallow nets, warmup, transfer learning), PyTorch-default documentation "
    "(Kaiming uniform a=sqrt(5), bias schemes), the variance-tracking hook "
    "implementation, clip-threshold guidance (0.5/1.0/5.0/10.0), the monitoring / "
    "safe-step / diagnostic-dashboard code, and the four-solutions mermaid/table "
    "summaries. Sense-collision vocabulary documented in the term map (attention "
    "idiom vs mechanism; spikes; the norm family; scale; decay-as-shrinkage vs "
    "weight decay) was adjudicated per pair with evidence, never by term count. "
    "Terminology nuances recorded in rationales rather than classified as "
    "conflicts: master-ai 'averaged the two' vs course 'harmonic mean' for the "
    "Xavier compromise (both correct for 2/(n_in+n_out)); master-ai "
    "'eigenvalues/spectral radius' vs course 'largest singular value' for the RNN "
    "explosion criterion (same matrix-growth condition; the singular-value form is "
    "the norm-precise one). Dating is consistent across vaults (Glorot & Bengio "
    "2010; He et al. 2015) - no F-0007-style discrepancy. NEW FINDING F-0009 "
    "(recorded in state/findings.jsonl and cross-referenced from OC-ext010-0033/"
    "0036): the course is internally inconsistent about the PyTorch Conv2d default "
    "BIAS initialization (file 01 says zeros; file 02 and the course's own "
    "Linear-section say uniform on (-1/sqrt(fan_in), 1/sqrt(fan_in)), the latter "
    "matching PyTorch's actual reset_parameters). Independent review: EXT-010-REVIEW "
    "(read-only) must PASS before commit."
)

CANDIDATE_REF = (
    "reports/extraction/ext010-overlap-candidates.json + -pairs.jsonl "
    "(CAP-013 over batches 010/011, terms training-stability-domain-v1.json) + "
    "committed batches 010/011"
)

RECORDS = [
    {
        "classification_id": "OC-ext010-0001",
        "task_id": TASK_ID,
        "topic": "Gradients through deep networks are products of many per-layer factors (Jacobians); factors below 1 make the product decay exponentially toward zero (vanishing), factors above 1 make it grow exponentially toward infinity (exploding)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-125a1155a78d32a3", "KU-fbb663cb34004375", "KU-373a9344bd8b2e1a", "KU-8e5d82607988a9fe", "KU-7d6d5d2d2fabec94", "KU-8dc70b34a90d35b4"],
        "evidence": [
            {"ku_id": "KU-125a1155a78d32a3", "quote": r"""Backpropagation through a deep network multiplies many Jacobians:""", "source_path": M08},
            {"ku_id": "KU-fbb663cb34004375", "quote": r"""If most factors have norm < 1, the product decays exponentially with depth — gradients reaching early layers are near zero, so those layers don't learn. **Vanishing gradient.**""", "source_path": M08},
            {"ku_id": "KU-373a9344bd8b2e1a", "quote": r"""If most factors have norm > 1, the product grows exponentially — gradients reach early layers as huge values, weights explode, training diverges. **Exploding gradient.**""", "source_path": M08},
            {"ku_id": "KU-8e5d82607988a9fe", "quote": r"""If each factor is < 1, the product → 0 (vanishing). If > 1, the product → ∞ (exploding). Both prevent learning in deep layers.""", "source_path": M08},
            {"ku_id": "KU-7d6d5d2d2fabec94", "quote": r"""When each term in this product is less than one, the product shrinks exponentially toward zero (vanishing). When each term is greater than one, the product grows exponentially toward infinity (exploding).""", "source_path": C03},
            {"ku_id": "KU-8dc70b34a90d35b4", "quote": r"""This product of Jacobians is the source of both the vanishing and exploding gradient problems.""", "source_path": C03},
        ],
        "rationale": (
            "Both vaults present the same mechanism as the root cause of both "
            "pathologies: backpropagation through depth multiplies many per-layer "
            "factors, and the product's behavior is decided by whether the factors "
            "sit below or above 1. Master-ai states it compactly (Jacobian product; "
            "norm < 1 decays exponentially; norm > 1 grows exponentially; TL;DR "
            "'product -> 0 / -> infinity'), while the course opens its chapter with "
            "the identical claim in product-of-terms language, derives the "
            "scalar-case fundamental equation, and states the three-way rule "
            "(<1 vanish, >1 explode, ~1 stable). Depth of apparatus differs "
            "(master-ai adds the spectral-radius bound and the RNN specialization "
            "classified in OC-ext010-0019; the course adds the alpha-to-the-(L-l) "
            "compounding table classified with the demonstrations in "
            "OC-ext010-0027) but the mechanism claim itself is duplicated. Related: "
            "OC-ext010-0014 (sigmoid ceiling), OC-ext010-0004/0005 (init-scale "
            "failure modes), OC-ext010-0017 (exploding causes and symptoms)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0002",
        "task_id": TASK_ID,
        "topic": "Initialization determines whether and how well training converges (master-ai frames it as control of activation/gradient magnitudes; the course frames it as the starting point on the loss landscape)",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-902460e71973e997", "KU-ef860a3e3a3e0183", "KU-76c740979e561244", "KU-b24cf92ce597d653"],
        "evidence": [
            {"ku_id": "KU-902460e71973e997", "quote": r"""At step 0, before any training, the network does a forward pass with random weights. The init determines:""", "source_path": M07},
            {"ku_id": "KU-ef860a3e3a3e0183", "quote": r"""Bad init = training never converges, or converges to a bad solution.""", "source_path": M07},
            {"ku_id": "KU-76c740979e561244", "quote": r"""The point where you start on this landscape, determined entirely by the initial values of the weights, profoundly influences which region of the landscape you will explore, how quickly you will converge, and whether you will converge at all.""", "source_path": C01},
            {"ku_id": "KU-b24cf92ce597d653", "quote": r"""There are three concrete reasons why initialization determines training outcomes.""", "source_path": C01},
        ],
        "rationale": (
            "Partial Overlap. Shared claim: initialization determines convergence "
            "outcomes. Master-ai states it from the signal-propagation side ('At "
            "step 0 ... the init determines:' activation magnitudes, gradient "
            "magnitudes, symmetry breaking; 'Bad init = training never converges, "
            "or converges to a bad solution'), and the course states the same "
            "outcome claim from the optimization-landscape side (the starting "
            "point 'profoundly influences ... how quickly you will converge, and "
            "whether you will converge at all', backed by its three-reasons "
            "enumeration: convergence speed, convergence at all, final "
            "performance - including the converges-to-a-bad-solution case). "
            "Substantial unique material on both sides keeps this from being a "
            "Semantic Duplicate: master-ai's magnitude/symmetry mechanics (see "
            "OC-ext010-0003) versus the course's non-convex landscape apparatus "
            "(local minima, saddle points, flat regions, the 2^N-saddle-points "
            "estimate, and the parachute-landing analogy - course-only). "
            "Synthesis should merge the outcome claim once and keep both framings "
            "as complementary explanations. Related: OC-ext010-0006 (variance "
            "calibration), OC-ext010-0034 (pre-2010 history)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0003",
        "task_id": TASK_ID,
        "topic": "Zero (or any identical-constant) initialization fails by the symmetry problem: all neurons in a layer compute the same output, receive the same gradient, make identical updates, collapsing the layer to a single effective neuron",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-94ac29ccf586a35f", "KU-daf4eae9ecf8efee", "KU-7da12c8f153d4961", "KU-901aeb152608ad7d", "KU-ca8fd98afd178942", "KU-cc13c084ce6528be"],
        "evidence": [
            {"ku_id": "KU-94ac29ccf586a35f", "quote": r"""- **Symmetry breaking**: if all weights are equal, all neurons in a layer compute the same thing — wasted capacity.""", "source_path": M07},
            {"ku_id": "KU-daf4eae9ecf8efee", "quote": r"""- **Zero init for all weights** — every neuron computes the same thing (symmetric), no learning. Always use random init for weights.""", "source_path": M07},
            {"ku_id": "KU-7da12c8f153d4961", "quote": r"""This cycle repeats forever — the network is permanently stuck in a symmetric state, and it might as well have a single neuron per layer.""", "source_path": C01},
            {"ku_id": "KU-901aeb152608ad7d", "quote": r"""A layer with $m$ neurons that all produce identical outputs and receive identical updates is functionally equivalent to a layer with a single neuron that has been replicated $m$ times.""", "source_path": C01},
            {"ku_id": "KU-ca8fd98afd178942", "quote": r"""every single active filter natively computes the identical exact same gradients internally and therefore learns the identical exact same topological features""", "source_path": C02},
            {"ku_id": "KU-cc13c084ce6528be", "quote": r"""it breaks the symmetry by giving each filter a different starting point, which leads to different outputs, different gradients, and ultimately different learned features.""", "source_path": C02},
        ],
        "rationale": (
            "Semantic Duplicate with complementary depth. Master-ai states the "
            "symmetry failure twice in compact form - as a design requirement "
            "('if all weights are equal, all neurons in a layer compute the same "
            "thing - wasted capacity') and as a pitfall ('Zero init for all "
            "weights - every neuron computes the same thing (symmetric), no "
            "learning. Always use random init for weights'). The course derives "
            "the full mechanism in file 01 (identical outputs f(0), identical "
            "upstream gradients, identical updates, the forever-repeating cycle, "
            "and the layer-equivalent-to-one-replicated-neuron conclusion) and "
            "restates it for CNN filters in file 02 (identical gradients mean "
            "identical learned features; random init gives each filter a "
            "different starting point). Course-only elaborations preserved in the "
            "KUs and recorded here rather than as separate records: the "
            "compounding of symmetry across layers (KU-983fb8c919270999) and the "
            "generalization that ANY identical constant, not just zero, triggers "
            "the failure (callout KU-5f674f41cf61f045). Related: OC-ext010-0036 "
            "(bias init - the zero-WEIGHTS pitfall is distinct from the "
            "zero-BIAS standard)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0004",
        "task_id": TASK_ID,
        "topic": "Too-large initial weights make activations and gradients grow exponentially with depth, overflowing to inf/NaN and diverging training",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-daf4eae9ecf8efee", "KU-ac093cefaffb9896", "KU-045f0ae5a89b09e7", "KU-88e7ac04edae1514", "KU-95a2a6e1d9403a4b"],
        "evidence": [
            {"ku_id": "KU-daf4eae9ecf8efee", "quote": r"""- **Init too large** — activations explode; gradients explode; training diverges.""", "source_path": M07},
            {"ku_id": "KU-ac093cefaffb9896", "quote": r"""After $L$ layers, the magnitude of the activations grows as:""", "source_path": C01},
            {"ku_id": "KU-045f0ae5a89b09e7", "quote": r"""The activations will overflow to `inf` (infinity), and the loss will become `NaN` (Not a Number).""", "source_path": C01},
            {"ku_id": "KU-88e7ac04edae1514", "quote": r"""The result is that gradients are astronomically large, causing weight updates so massive that the parameters bounce wildly around the loss landscape without ever settling into a minimum.""", "source_path": C01},
            {"ku_id": "KU-95a2a6e1d9403a4b", "quote": r"""After 50 layers, the activations may overflow the numerical representation (becoming NaN or Infinity), causing the entire training process to crash.""", "source_path": C02},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults derive the explosion: with large "
            "weights, each layer multiplies activations (and each backward step "
            "multiplies Jacobians) by a factor exceeding 1, so magnitudes grow "
            "exponentially with depth until they overflow the floating-point "
            "range. Master-ai states it as a pitfall line ('Init too large - "
            "activations explode; gradients explode; training diverges') and as "
            "an exploding-gradient cause ('Bad init: weights too large at start' "
            "- the full master-ai causes list is classified in OC-ext010-0017). "
            "The course works the quantitative example (activation magnitude on "
            "the order of (n*c)^L; the 10-layer, n=1000, c=10 case reaching "
            "10^40 against the ~3.4e38 32-bit ceiling; overflow to inf; NaN "
            "loss) and adds the oscillatory-divergence description, with file "
            "02 giving the 50-layer CNN restatement. The numeric detail is "
            "course-only depth recorded here, not separately classified. "
            "Related: OC-ext010-0005 (too-small mirror), OC-ext010-0035 "
            "(NaN-first diagnosis), OC-ext010-0017 (causes and symptoms)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0005",
        "task_id": TASK_ID,
        "topic": "Too-small initial weights make activations and gradients shrink exponentially with depth; the network collapses toward a constant function and early layers stay frozen",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-daf4eae9ecf8efee", "KU-122a8f13c8d3292a", "KU-af0c2a892bc6c267", "KU-f28ff61f691d0bb5", "KU-7491a330351bce86"],
        "evidence": [
            {"ku_id": "KU-daf4eae9ecf8efee", "quote": r"""- **Init too small** — activations vanish; gradients vanish; training stalls.""", "source_path": M07},
            {"ku_id": "KU-122a8f13c8d3292a", "quote": r"""The network has collapsed to a constant function — it predicts the same output for every input — and the loss is constant, providing no useful gradient signal for learning.""", "source_path": C01},
            {"ku_id": "KU-af0c2a892bc6c267", "quote": r"""The result is a network where the early feature extraction layers are frozen at their (terrible) initial values, while only the later layers can adapt. This fundamentally undermines the purpose of depth — the whole point of deep networks is to learn hierarchical features, but if the early layers cannot learn, the hierarchy is broken.""", "source_path": C01},
            {"ku_id": "KU-f28ff61f691d0bb5", "quote": r"""These two failure modes — explosion with large weights and vanishing with small weights — illustrate the **Goldilocks principle** of weight initialization: the weights must be **just right**. Too large, and the network explodes; too small, and it vanishes.""", "source_path": C01},
            {"ku_id": "KU-7491a330351bce86", "quote": r"""The network appears to train, but the early layers never actually learn meaningful features.""", "source_path": C02},
        ],
        "rationale": (
            "Semantic Duplicate, mirror image of OC-ext010-0004. Master-ai: "
            "'Init too small - activations vanish; gradients vanish; training "
            "stalls.' The course derives the mechanism: activations shrink "
            "exponentially (order (n*epsilon)^L), the network collapses to a "
            "constant function with constant loss and no learning signal, and "
            "early-layer gradients decay exponentially so the early feature "
            "layers stay frozen while later layers adapt slowly - breaking the "
            "depth hierarchy; file 02 restates the 50-layer consequence ('the "
            "network appears to train, but the early layers never actually learn "
            "meaningful features'). The course additionally NAMES the two-sided "
            "principle (Goldilocks: the weights must be just right) - quoted "
            "here as the umbrella over records 0004/0005. Related: "
            "OC-ext010-0016 (early-layer consequence), OC-ext010-0006 (why "
            "calibration is the fix)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0006",
        "task_id": TASK_ID,
        "topic": "Random initialization must be variance-calibrated to the architecture: uncalibrated Gaussians N(0,0.01) and N(0,1) fail because activation variance drifts from layer to layer",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a6473bc011beb806", "KU-fe97a4aad8fcec8b", "KU-c2b2ffce9a915e88", "KU-7a623bd03784450b", "KU-07eeae952c3ed03c"],
        "evidence": [
            {"ku_id": "KU-a6473bc011beb806", "quote": r"""We want $\text{Var}(\mathbf{y}) \approx \text{Var}(\mathbf{x})$ (activations don't blow up or vanish).""", "source_path": M07},
            {"ku_id": "KU-fe97a4aad8fcec8b", "quote": r"""Without these schemes, deep networks (10+ layers) were untrainable — activations exploded or vanished.""", "source_path": M07},
            {"ku_id": "KU-c2b2ffce9a915e88", "quote": r"""The key insight that leads to principled initialization schemes is this: **we should initialize weights so that the variance of the activations remains approximately constant as signals propagate forward through the network, and the variance of the gradients remains approximately constant as they propagate backward**.""", "source_path": C01},
            {"ku_id": "KU-7a623bd03784450b", "quote": r"""Two common but problematic choices are $\mathcal{N}(0, 0.01)$ (standard deviation 0.01) and $\mathcal{N}(0, 1)$ (standard deviation 1.0). Both fail, but for opposite reasons.""", "source_path": C01},
            {"ku_id": "KU-07eeae952c3ed03c", "quote": r"""a standard Gaussian random uniform initialization actively fails dynamically in deep CNN architectures because statistical mathematical variance destructively shrinks or violently explodes as matrix data continuously passes through 50+ sequentially connected active hierarchical layers""", "source_path": C02},
        ],
        "rationale": (
            "Semantic Duplicate on the central claim: random initialization "
            "breaks symmetry but only works if its variance is calibrated to "
            "the architecture, because uncalibrated variance drifts from layer "
            "to layer. Master-ai encodes the requirement as the "
            "variance-preservation goal ('We want Var(y) ~ Var(x) ... don't blow "
            "up or vanish'; 'Without these schemes, deep networks (10+ layers) "
            "were untrainable'). The course makes the identical point as its "
            "root-cause statement (the key-insight sentence: keep activation "
            "variance constant forward and gradient variance constant "
            "backward) and demonstrates it with the two canonical bad choices "
            "N(0, 0.01) and N(0, 1) ('Both fail, but for opposite reasons'); "
            "file 02 agrees ('a standard Gaussian random uniform initialization "
            "actively fails dynamically in deep CNN architectures'). "
            "Course-only numeric analyses (the 512-wide Var 0.0512 / 512 "
            "computations, the pre-2010 dating, and the saturation-induced "
            "vanishing for N(0,1)) stay in the KUs. Related: OC-ext010-0007 "
            "(the two conditions), OC-ext010-0034 (history)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0007",
        "task_id": TASK_ID,
        "topic": "Xavier's defining conditions: keep activation variance constant forward (Var(w) = 1/n_in) and gradient variance constant backward (Var(w) = 1/n_out)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-854bfa01f3cc6cde", "KU-9012d03c1f1f0ee3", "KU-4defd141c81dcaec", "KU-f6a7a3c739afd695", "KU-41494822772ce781", "KU-4d2f92d1f4d88361"],
        "evidence": [
            {"ku_id": "KU-854bfa01f3cc6cde", "quote": r"""\text{Var}(W_{ij}) = \frac{1}{n_{\text{in}}}""", "source_path": M07},
            {"ku_id": "KU-9012d03c1f1f0ee3", "quote": r"""For the backward pass, gradients flow through $\mathbf{W}^T$, and the analogous condition gives $\text{Var}(W_{ij}) = \frac{1}{n_{\text{out}}}$.""", "source_path": M07},
            {"ku_id": "KU-4defd141c81dcaec", "quote": r"""To keep $\text{Var}(y) = \text{Var}(x)$ (activations don't grow/shrink), we need $\sigma_W^2 = 1/n_{\text{in}}$.""", "source_path": M07},
            {"ku_id": "KU-f6a7a3c739afd695", "quote": r"""This is the **forward pass condition**: the variance of the weights should be the reciprocal of the fan-in to maintain activation variance during the forward pass.""", "source_path": C01},
            {"ku_id": "KU-41494822772ce781", "quote": r"""This is the **backward pass condition**: the variance of the weights should be the reciprocal of the fan-out to maintain gradient variance during the backward pass.""", "source_path": C01},
            {"ku_id": "KU-4d2f92d1f4d88361", "quote": r"""1. **Forward pass**: The variance of the activations should be the same at every layer""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults derive the two variance-preservation "
            "conditions that define principled initialization. Master-ai: the "
            "forward pass wants Var(W_ij) = 1/n_in (from Var(y) = n_in * Var(W) * "
            "Var(x) with Var(y) = Var(x)), and the backward pass through the "
            "transposed weights gives the analogous 1/n_out ('gradients flow "
            "through W^T'); its detailed section repeats both. The course: the "
            "same forward condition boxed ('the variance of the weights should "
            "be the reciprocal of the fan-in'), the same backward condition "
            "boxed ('reciprocal of the fan-out to maintain gradient "
            "variance'), plus the explicit two-condition statement (activation "
            "variance the same at every layer; gradient variance the same at "
            "every layer) and the i.i.d. / zero-mean / zero-bias assumptions "
            "underlying the derivation. Course-only: the assumptions list and "
            "boxed presentation; master-ai-only: the compact W^T observation. "
            "Related: OC-ext010-0008 (the compromise between the conditions), "
            "OC-ext010-0012 (fan_in/fan_out modes operationalize them)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0008",
        "task_id": TASK_ID,
        "topic": "Because n_in and n_out differ, Glorot & Bengio (2010) combined the forward and backward conditions into the Xavier variance 2/(n_in + n_out)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b1fa47861af6cea2", "KU-188f52ea134e8362", "KU-07b9bf06f47cd2bc", "KU-d7e04eec15dcee33"],
        "evidence": [
            {"ku_id": "KU-b1fa47861af6cea2", "quote": r"""Glorot & Bengio (2010) proposed averaging the forward and backward conditions:""", "source_path": M07},
            {"ku_id": "KU-188f52ea134e8362", "quote": r"""Glorot & Bengio (2010) averaged the two: $\sigma_W^2 = 2/(n_{\text{in}} + n_{\text{out}})$. This balances forward and backward stability — neither perfect, but both acceptable.""", "source_path": M07},
            {"ku_id": "KU-07b9bf06f47cd2bc", "quote": r"""Glorot and Bengio proposed a **compromise** that satisfies both conditions on average by taking the harmonic mean of the two constraints:""", "source_path": C01},
            {"ku_id": "KU-d7e04eec15dcee33", "quote": r"""It ensures that the geometric mean of the forward and backward variance ratios is approximately 1, providing a balanced trade-off that works well in practice.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate with a terminology nuance recorded, not a "
            "conflict. Because n_in differs from n_out in general, the two "
            "conditions of OC-ext010-0007 cannot hold simultaneously; both "
            "vaults state that Glorot & Bengio (2010) resolved this by "
            "combining them into Var = 2/(n_in + n_out). Master-ai says they "
            "'proposed averaging the forward and backward conditions' and "
            "later 'averaged the two ... balances forward and backward "
            "stability - neither perfect, but both acceptable'; the course "
            "says they took 'the harmonic mean of the two constraints' and "
            "adds that the result makes the geometric mean of the forward and "
            "backward variance ratios approximately 1. Averaging, harmonic "
            "mean of the two variances, and geometric-mean-of-ratios are three "
            "correct characterizations of the same formula; synthesis should "
            "present one derivation and may note the alternative "
            "characterizations as remarks. Related: OC-ext010-0007 (the "
            "conditions being combined), OC-ext010-0009 (the samplers)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0009",
        "task_id": TASK_ID,
        "topic": "Xavier sampling formulas: normal N(0, sqrt(2/(n_in+n_out))) and uniform U(-sqrt(6/(n_in+n_out)), sqrt(6/(n_in+n_out)))",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-a2c8bb32a1df0045", "KU-9d28dd79d9d3626e", "KU-50e2ba5e625f6e19", "KU-d5cebf7c144b8842"],
        "evidence": [
            {"ku_id": "KU-a2c8bb32a1df0045", "quote": r"""Sample from $\mathcal{N}\left(0, \frac{2}{n_{\text{in}} + n_{\text{out}}}\right)$ or $\mathcal{U}\left(-\sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}, \sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}\right)$.""", "source_path": M07},
            {"ku_id": "KU-9d28dd79d9d3626e", "quote": r"""$$\boxed{w \sim U\left(-\sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}, \;\; \sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}\right)}$$""", "source_path": C01},
            {"ku_id": "KU-50e2ba5e625f6e19", "quote": r"""$$\boxed{w \sim \mathcal{N}\left(0, \;\; \sqrt{\frac{2}{n_{\text{in}} + n_{\text{out}}}}\right)}$$""", "source_path": C01},
            {"ku_id": "KU-d5cebf7c144b8842", "quote": r"""The uniform distribution is sometimes preferred because it has a hard bound on the maximum weight value, which can provide a slight safety margin against outlier weights.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults give the same two instantiations "
            "of the Xavier variance: normal with mean 0 and variance "
            "2/(n_in+n_out), and uniform on +/- sqrt(6/(n_in+n_out)) (the "
            "uniform's a^2/3 variance matched to the Xavier variance). "
            "Master-ai gives both in one line; the course derives the uniform "
            "bound (a = sqrt(6/(n_in+n_out))), boxes both samplers, notes the "
            "N(0, sigma) notation convention (standard deviation, consistent "
            "with PyTorch's xavier_normal_), and adds the course-only "
            "rationale that the uniform's hard bound gives a safety margin "
            "against outlier weights. Related: OC-ext010-0008 (where the "
            "variance comes from), OC-ext010-0010 (which activations it "
            "serves), OC-ext010-0032 (the PyTorch API for these samplers)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0010",
        "task_id": TASK_ID,
        "topic": "Xavier initialization is designed for symmetric, saturating activations (tanh, sigmoid) that are approximately linear near zero",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-27f3165fb72fe284", "KU-98b2ab4e3f598489", "KU-b2e1ea1cba2731fc"],
        "evidence": [
            {"ku_id": "KU-27f3165fb72fe284", "quote": r"""Designed for **symmetric activations** (tanh, sigmoid) where the activation is roughly linear near 0 and saturates away from 0. Xavier keeps activations in the linear regime.""", "source_path": M07},
            {"ku_id": "KU-98b2ab4e3f598489", "quote": r"""Xavier initialization is designed for **symmetric activation functions** that are approximately linear near zero, specifically:""", "source_path": C01},
            {"ku_id": "KU-b2e1ea1cba2731fc", "quote": r"""Sigmoid is less well-suited because it is not zero-centered (its output is always positive, with $\sigma(0) = 0.5$), which violates assumption 5 in our derivation.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults scope Xavier initialization to "
            "symmetric, saturating activations that are approximately linear "
            "near zero: master-ai 'Designed for symmetric activations (tanh, "
            "sigmoid) where the activation is roughly linear near 0 and "
            "saturates away from 0. Xavier keeps activations in the linear "
            "regime'; the course states the same and lists the members "
            "(sigmoid with max derivative 0.25 at zero, tanh with derivative 1 "
            "at zero, softsign), explaining the approximately-"
            "variance-preserving-near-zero property. Course-only depth "
            "preserved in the KUs: tanh is better suited because it is "
            "zero-centered while sigmoid is not (sigma(0) = 0.5), violating "
            "the derivation's zero-mean assumption - Xavier still works with "
            "sigmoid but less effectively. Related: OC-ext010-0013 (the "
            "matching rule), OC-ext010-0014/0015 (the derivative ceilings), "
            "OC-ext010-0007 (the conditions Xavier serves)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0011",
        "task_id": TASK_ID,
        "topic": "He/Kaiming (2015): ReLU zeros out about half its inputs, halving the variance, so the init variance must be doubled to 2/n_in",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-e7262bbf02e5e577", "KU-e238433a59aa6e90", "KU-c1eb22f33e1b3670", "KU-9b7c6b2b841a7ac8", "KU-e4ad481af694c09b"],
        "evidence": [
            {"ku_id": "KU-e7262bbf02e5e577", "quote": r"""He et al. (2015) observed that ReLU zeros out half its inputs, so the variance is halved. The fix: double the init variance.""", "source_path": M07},
            {"ku_id": "KU-e238433a59aa6e90", "quote": r"""He et al. (2015) observed that ReLU zeros out ~half the inputs: $y_j = \text{ReLU}(\sum_i W_{ji} x_i)$. The variance of the active (non-zero) outputs is halved. To compensate, double the init variance: $\sigma_W^2 = 2/n_{\text{in}}$.""", "source_path": M07},
            {"ku_id": "KU-c1eb22f33e1b3670", "quote": r"""This is the **Kaiming/He initialization** formula. The extra factor of 2 in the numerator (compared to the forward-only Xavier condition $\text{Var}(w) = \frac{1}{n_{\text{in}}}$) compensates for the factor of $\frac{1}{2}$ introduced by ReLU.""", "source_path": C01},
            {"ku_id": "KU-9b7c6b2b841a7ac8", "quote": r"""More importantly, the variance of the ReLU output is approximately half the variance of the input:""", "source_path": C01},
            {"ku_id": "KU-e4ad481af694c09b", "quote": r"""The factor of 2 accounts for the fact that ReLU zeroes out approximately half of the activations, effectively halving the variance at each layer.""", "source_path": C02},
        ],
        "rationale": (
            "Semantic Duplicate, derived on both sides. He et al. (2015) "
            "observed that ReLU zeros out about half its inputs, halving the "
            "effective variance; compensating requires doubling the init "
            "variance to 2/n_in. Master-ai states this twice (summary section "
            "and detailed derivation - an intra-vault repetition that "
            "synthesis should fold into one derivation); the course derives it "
            "(Var(ReLU(z)) approximately half Var(z); the E[ReLU(z)^2] = "
            "sigma^2/2 computation with the exact sigma^2/2 * (1 - 1/pi) "
            "term; the factor-of-two compensation boxed) and notes the "
            "shrink-by-2-per-layer consequence of not compensating; file 02 "
            "restates it for CNN filters with the K x K x C_in fan-in. Both "
            "vaults date it He et al. (2015) - consistent, no F-0007-style "
            "discrepancy. Related: OC-ext010-0012 (samplers and fan modes), "
            "OC-ext010-0013 (what happens if you use Xavier with ReLU), "
            "OC-ext010-0021 (PReLU from the same paper)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0012",
        "task_id": TASK_ID,
        "topic": "Kaiming sampling formulas (N(0, sqrt(2/n_in)) and U(-sqrt(6/n_in), sqrt(6/n_in))) and the fan_in vs fan_out modes mapping to forward- vs backward-pass variance preservation",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-30680e067be8168f", "KU-ceb4e6cb31a70b63", "KU-4ea5c6bc127bc946", "KU-f1f1392705a2564f", "KU-4647ca1ef76b499a"],
        "evidence": [
            {"ku_id": "KU-30680e067be8168f", "quote": r"""Sample from $\mathcal{N}\left(0, \frac{2}{n_{\text{in}}}\right)$ or $\mathcal{U}\left(-\sqrt{\frac{6}{n_{\text{in}}}}, \sqrt{\frac{6}{n_{\text{in}}}}\right)$.""", "source_path": M07},
            {"ku_id": "KU-ceb4e6cb31a70b63", "quote": r"""nn.init.kaiming_normal_(conv.weight, mode='fan_in', nonlinearity='relu')""", "source_path": M07},
            {"ku_id": "KU-4ea5c6bc127bc946", "quote": r"""$$\boxed{w \sim \mathcal{N}\left(0, \;\; \sqrt{\frac{2}{n_{\text{in}}}}\right)}$$""", "source_path": C01},
            {"ku_id": "KU-f1f1392705a2564f", "quote": r"""Kaiming initialization can be computed using either the fan-in ($n_{\text{in}}$) or fan-out ($n_{\text{out}}$) of the layer. The choice affects whether the initialization preserves variance in the forward pass or the backward pass:""", "source_path": C01},
            {"ku_id": "KU-4647ca1ef76b499a", "quote": r"""- **`fan_in` mode** (default in PyTorch): Uses $\text{Var}(w) = \frac{2}{n_{\text{in}}}$. This preserves variance in the **forward pass**.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults give the Kaiming samplers - "
            "normal N(0, sqrt(2/n_in)) and uniform on +/- sqrt(6/n_in) - and "
            "both connect the fan_in/fan_out choice to the forward/backward "
            "conditions of OC-ext010-0007: master-ai via its W^T analysis and "
            "its worked code (kaiming_normal_ with mode='fan_in', "
            "nonlinearity='relu'); the course explicitly ('Kaiming "
            "initialization can be computed using either the fan_in or the "
            "fan_out ... preserves variance in the forward pass or the "
            "backward pass'), naming fan_in as the PyTorch default that "
            "preserves the forward pass and fan_out for the backward pass. "
            "Course-only detail: the convolutional fan computation (n_in = "
            "C_in x k x k, n_out = C_out x k x k, with the Conv2d(64, 128, 3) "
            "worked example). Related: OC-ext010-0011 (the factor of 2), "
            "OC-ext010-0033 (PyTorch's defaults build on these)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0013",
        "task_id": TASK_ID,
        "topic": "Init must match the activation: Xavier/Glorot for tanh/sigmoid, He/Kaiming for ReLU; Xavier-on-ReLU is about 2x too small (slow, suboptimal) and Kaiming-on-sigmoid saturates",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-33caf0d68e851a19", "KU-bcab972c995e13f6", "KU-eaef0936919ebbfe", "KU-38b1833efd0758bb", "KU-99e193f8b36e6bcf"],
        "evidence": [
            {"ku_id": "KU-33caf0d68e851a19", "quote": r"""The two main schemes: **Xavier (Glorot)** for tanh/sigmoid, **He (Kaiming)** for ReLU.""", "source_path": M07},
            {"ku_id": "KU-bcab972c995e13f6", "quote": r"""Xavier's $\sigma_W^2 = 2/(n_{\text{in}} + n_{\text{out}})$ is too small by ~2×. The network trains but slower and may converge to worse solutions.""", "source_path": M07},
            {"ku_id": "KU-eaef0936919ebbfe", "quote": r"""- **ReLU or Leaky ReLU activations** → Kaiming/He initialization""", "source_path": C01},
            {"ku_id": "KU-38b1833efd0758bb", "quote": r"""Using Xavier with ReLU will cause the activations to vanish over many layers, while using Kaiming with sigmoid may cause them to saturate.""", "source_path": C01},
            {"ku_id": "KU-99e193f8b36e6bcf", "quote": r"""This means that if we use Xavier initialization (which assumes the activation preserves variance), the actual variance of the activations will **shrink by a factor of 2 at each layer**.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. The matching rule - Xavier/Glorot for "
            "tanh/sigmoid, He/Kaiming for ReLU-family - is stated by "
            "master-ai's TL;DR, by the course's rule-of-thumb callout "
            "(including 'when in doubt, use Kaiming'), and by course file "
            "02's practical takeaway. Both vaults also quantify the mismatch "
            "direction: master-ai's interview answer (Xavier on ReLU 'works' "
            "but is suboptimally calibrated, too small by about 2x, training "
            "slower and possibly converging to worse solutions) and the "
            "course (Xavier assumes variance preservation, so with ReLU the "
            "activation variance shrinks by a factor of 2 at each layer; "
            "'Using Xavier with ReLU will cause the activations to vanish "
            "over many layers, while using Kaiming with sigmoid may cause "
            "them to saturate'). Master-ai's pitfall list adds the mix-up "
            "warning (Xavier with ReLU, He with tanh -> slow or unstable "
            "training). ReLU-family coverage differs complementarily "
            "(master-ai adds GELU/SiLU; the course adds Leaky/PReLU/ELU/SELU "
            "with the Leaky variance formula) - recorded as in-scope "
            "single-vault detail, not separately classified. Related: "
            "OC-ext010-0011, OC-ext010-0021 (PReLU provenance), "
            "OC-ext010-0010."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0014",
        "task_id": TASK_ID,
        "topic": "The sigmoid derivative is capped at 0.25 (at x=0) and saturates toward zero away from the origin, so gradients shrink by at least 4x per sigmoid layer",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b5227ef8a4524679", "KU-beba6bfcb4e83382", "KU-a7c0ef301f034cdd", "KU-39b1a3dd17ed2fdb"],
        "evidence": [
            {"ku_id": "KU-b5227ef8a4524679", "quote": r"""- **Sigmoid / tanh**: derivatives are ≤ 0.25 (sigmoid) or ≤ 1 (tanh), and saturate to 0 away from the origin. Multiplying many small derivatives → 0.""", "source_path": M08},
            {"ku_id": "KU-beba6bfcb4e83382", "quote": r"""This derivative has a **maximum value of 0.25**, which occurs at $x = 0$ where $\sigma(0) = 0.5$.""", "source_path": C03},
            {"ku_id": "KU-a7c0ef301f034cdd", "quote": r"""The maximum derivative of 0.25 means that every time the gradient passes through a sigmoid activation, it is multiplied by at most 0.25 (and often much less).""", "source_path": C03},
            {"ku_id": "KU-39b1a3dd17ed2fdb", "quote": r"""This is far below the precision of 32-bit floating-point numbers (which have approximately 7 decimal digits of precision). The gradient has effectively been rounded to zero, and the weights in the early layers will never be updated.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Master-ai states the sigmoid ceiling in one "
            "line as part of where-vanishing-happens ('derivatives are <= 0.25 "
            "(sigmoid)... saturate to 0 away from the origin. Multiplying "
            "many small derivatives -> 0'); the course devotes a full section "
            "to it: the derivative sigma'(x) = sigma(x)(1 - sigma(x)) has "
            "maximum value 0.25 at x = 0 (with the maximization derivation), "
            "per-point values (about 0.197 at x=1, 0.105 at x=2, 0.007 at "
            "x=5), the best-case 10-layer product 0.25^10 (about "
            "one-millionth), and the realistic 0.1^10 = 1e-10 underflow "
            "argument against 32-bit precision, plus the saturation-tails "
            "picture. The shared claim (sigmoid caps per-layer gradient gain "
            "at 0.25 and saturates) is fully duplicated; the quantitative "
            "derivation is course-only depth preserved in the KUs. Related: "
            "OC-ext010-0015 (tanh), OC-ext010-0027 (worked demonstrations), "
            "OC-ext010-0001 (mechanism), OC-ext010-0022 (normalization as the "
            "saturation fix)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0015",
        "task_id": TASK_ID,
        "topic": "tanh is better than sigmoid (maximum derivative 1.0 at x=0, four times sigmoid's 0.25) but still saturates for large |x|, so gradients still vanish through many layers, just more slowly",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b5227ef8a4524679", "KU-ab075742f9f4c42d", "KU-d2960cfebed59c99"],
        "evidence": [
            {"ku_id": "KU-b5227ef8a4524679", "quote": r"""or ≤ 1 (tanh), and saturate to 0 away from the origin""", "source_path": M08},
            {"ku_id": "KU-ab075742f9f4c42d", "quote": r"""The maximum derivative of tanh is 1.0 (at $x = 0$), which is four times better than sigmoid's maximum of 0.25. However, tanh still saturates for large $|x|$, and the derivative drops rapidly:""", "source_path": C03},
            {"ku_id": "KU-d2960cfebed59c99", "quote": r"""Even with tanh, the average derivative across all neurons in a typical network is well below 1, and the gradient still vanishes through many layers — just more slowly than with sigmoid.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Master-ai's where-it-happens line covers "
            "tanh in the same breath as sigmoid ('<= 1 (tanh), and saturate "
            "to 0 away from the origin'); the course gives tanh its own "
            "treatment: derivative 1 - tanh^2 with maximum 1.0 at zero "
            "('four times better than sigmoid's maximum of 0.25'), the decay "
            "table (1.0 / about 0.42 / 0.07 / 0.01 at x = 0/1/2/3), and the "
            "conclusion that the average derivative is still below 1 so "
            "gradients still vanish through many layers - 'just more slowly "
            "than with sigmoid'. Both vaults thus agree tanh ameliorates but "
            "does not solve activation-side vanishing. Course-only: the "
            "derivative table and the zero-centered framing. Related: "
            "OC-ext010-0014 (sigmoid), OC-ext010-0022 (normalization as the "
            "saturation fix), OC-ext010-0020 (ReLU as the real fix)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0016",
        "task_id": TASK_ID,
        "topic": "Consequence of vanishing gradients: early layers learn extremely slowly or not at all, so the learned feature hierarchy breaks (early feature extractors stay at random initialization)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-fbb663cb34004375", "KU-07fbed4bd4d89af6", "KU-61ac03ebecf3abdc", "KU-3c1228359e57cea6"],
        "evidence": [
            {"ku_id": "KU-fbb663cb34004375", "quote": r"""gradients reaching early layers are near zero, so those layers don't learn""", "source_path": M08},
            {"ku_id": "KU-07fbed4bd4d89af6", "quote": r"""- **Vanishing**: early layers don't change during training (their gradient norms are near zero). Loss decreases slowly or plateaus.""", "source_path": M08},
            {"ku_id": "KU-61ac03ebecf3abdc", "quote": r"""the early layers, which are responsible for extracting low-level features (edges, textures, patterns), are stuck at their random initialization, while the late layers try to compensate by learning complex mappings from random features to the correct output.""", "source_path": C03},
            {"ku_id": "KU-3c1228359e57cea6", "quote": r"""If these layers cannot learn, the entire network operates on essentially random features, and its performance is severely limited.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate on the practical consequence: vanishing "
            "gradients leave early layers essentially untrained. Master-ai: "
            "'early layers don't change during training (their gradient "
            "norms are near zero). Loss decreases slowly or plateaus' and "
            "'gradients reaching early layers are near zero, so those layers "
            "don't learn.' The course develops the consequence: the "
            "late/middle/early gradient pattern, early feature-extraction "
            "layers stuck at random initialization while late layers "
            "compensate, the broken feature hierarchy, and the CNN-specific "
            "severity (early conv layers are the general edge/corner/texture "
            "detectors; if they cannot learn, the network runs on "
            "essentially random features). The CNN-feature framing is "
            "course-only elaboration; the core claim is duplicated. Related: "
            "OC-ext010-0005 (small-init vanishing), OC-ext010-0026 (how to "
            "detect it), OC-ext010-0001 (mechanism)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0017",
        "task_id": TASK_ID,
        "topic": "Exploding gradients: causes (poor init, too-high learning rate with positive feedback) and symptom signature (NaN loss/weights, violent oscillations, huge weights), with sudden catastrophic onset",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-d9ed35416db0348a", "KU-07fbed4bd4d89af6", "KU-627b0a41f841cf02", "KU-a3adbd8f7d0a8c55", "KU-cbf3b81fb0df5cc1", "KU-3de165df55ed7ff8"],
        "evidence": [
            {"ku_id": "KU-d9ed35416db0348a", "quote": r"""- **Large learning rates**: each step overshoots, weights grow, next step's gradients grow more — positive feedback.""", "source_path": M08},
            {"ku_id": "KU-07fbed4bd4d89af6", "quote": r"""- **Exploding**: loss becomes NaN or spikes wildly. Gradient norms are huge.""", "source_path": M08},
            {"ku_id": "KU-627b0a41f841cf02", "quote": r"""The most common cause of exploding gradients is **poor weight initialization** combined with **learning rates that are too high**.""", "source_path": C03},
            {"ku_id": "KU-a3adbd8f7d0a8c55", "quote": r"""This self-reinforcing cycle can cause the network to diverge within a single training step.""", "source_path": C03},
            {"ku_id": "KU-cbf3b81fb0df5cc1", "quote": r"""**NaN loss**: The loss function returns `NaN` (Not a Number), which occurs when the activations or gradients overflow beyond the range of floating-point numbers.""", "source_path": C03},
            {"ku_id": "KU-3de165df55ed7ff8", "quote": r"""exploding gradients can occur suddenly and catastrophically. A network can be training normally for hundreds of epochs and then suddenly produce `NaN` loss in a single step.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults enumerate the causes and the "
            "symptom signature of exploding gradients. Causes: master-ai "
            "lists RNN eigenvalues > 1, large learning rates (positive "
            "feedback: overshoot, weights grow, next gradients grow more), "
            "and bad init; the course names 'poor weight initialization "
            "combined with learning rates that are too high' as most common, "
            "adds the self-reinforcing cycle that can diverge within a "
            "single training step, and lists uncalibrated init, too-high LR, "
            "missing normalization, and RNN long sequences. Symptoms: "
            "master-ai 'loss becomes NaN or spikes wildly. Gradient norms "
            "are huge'; the course's five-symptom list (NaN loss - most "
            "dramatic and permanent once reached; NaN weights spreading "
            "corruption; wildly oscillating loss; extremely large weight "
            "values; sudden spikes) and its suddenness callout (hundreds of "
            "epochs of normal training, then NaN in a single step - harder "
            "to anticipate, easier to detect). The RNN-specific cause is "
            "classified separately in OC-ext010-0019. Related: "
            "OC-ext010-0018 (spikes as warnings), OC-ext010-0024 (clipping "
            "as the response), OC-ext010-0035 (NaN-first diagnosis)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0018",
        "task_id": TASK_ID,
        "topic": "Loss-curve spikes are instability warnings that must be investigated (often gradient explosions / too-high init variance), not dismissed as training noise",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-ff7bc655b9104574", "KU-1f9c00801fd2da3e", "KU-6190577c79303924", "KU-1a9bcdfcb287055c"],
        "evidence": [
            {"ku_id": "KU-ff7bc655b9104574", "quote": r"""| Training unstable (loss spikes) | Init variance too high | Reduce init std; use residual scaling |""", "source_path": M07},
            {"ku_id": "KU-1f9c00801fd2da3e", "quote": r"""- **Loss spikes** during training are often gradient explosions. Investigate before continuing.""", "source_path": M08},
            {"ku_id": "KU-6190577c79303924", "quote": r"""- **Ignoring loss spikes** as "training noise" → often a sign of impending divergence.""", "source_path": M08},
            {"ku_id": "KU-1a9bcdfcb287055c", "quote": r"""occasional massive spikes indicate that the gradient has temporarily exploded in some part of the network. These spikes are warning signs that the network is on the edge of instability.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate on the operational lesson: loss-curve spikes "
            "are instability warnings demanding investigation, not noise to "
            "ignore. Master-ai encodes it three ways - the init failure-table "
            "row (unstable loss spikes -> init variance too high -> reduce "
            "init std / use residual scaling), the production list ('Loss "
            "spikes during training are often gradient explosions. "
            "Investigate before continuing'), and the pitfall ('Ignoring "
            "loss spikes as training noise -> often a sign of impending "
            "divergence'). The course states the same from the symptom side "
            "(massive spikes indicate a temporarily exploded gradient; "
            "'warning signs that the network is on the edge of instability') "
            "and from the clipping side (clipping is the safety net for the "
            "occasional spikes that precede divergence). Related: "
            "OC-ext010-0017 (symptoms), OC-ext010-0024 (clipping), "
            "OC-ext010-0026 (monitoring)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0019",
        "task_id": TASK_ID,
        "topic": "RNNs are especially vulnerable: the same recurrent weight matrix is applied at every timestep, so the gradient product raises one matrix to a high power and its growth factor (spectral radius / largest singular value) decides everything",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b5227ef8a4524679", "KU-60305e78a726e866", "KU-e8e7dfeef517632c", "KU-35d3ce89749d047c"],
        "evidence": [
            {"ku_id": "KU-b5227ef8a4524679", "quote": r"""- **RNNs**: same weights applied at each timestep, so backprop through time multiplies the same Jacobian $T$ times. After 100 timesteps, even a small per-step factor becomes negligible.""", "source_path": M08},
            {"ku_id": "KU-60305e78a726e866", "quote": r"""- $\rho(\mathbf{W}) < 1$: vanishing — can't learn long-range dependencies.""", "source_path": M08},
            {"ku_id": "KU-e8e7dfeef517632c", "quote": r"""This is why RNNs can't remember dependencies > 20-50 timesteps. LSTMs and GRUs mitigate (gates control the effective Jacobian) but don't fully solve. Transformers (with attention) bypass this entirely — no sequential Jacobian product.""", "source_path": M08},
            {"ku_id": "KU-35d3ce89749d047c", "quote": r"""In RNNs, the same weight matrix is applied at every time step, so the gradient product involves the same matrix raised to a high power. If the largest singular value of this matrix is greater than 1, the gradient grows exponentially with the sequence length.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate with a terminology nuance recorded rather "
            "than treated as conflict. Shared claim: RNNs are maximally "
            "exposed because the same recurrent matrix is applied at every "
            "timestep, so the gradient product raises one matrix to a high "
            "power; its growth factor then decides everything, and practical "
            "dependency horizons collapse. Master-ai: 'same weights applied "
            "at each timestep, so backprop through time multiplies the same "
            "Jacobian T times'; the spectral-radius trichotomy (rho < 1 "
            "vanishing - can't learn long-range; rho > 1 exploding - "
            "diverges; rho = 1 stable but hard to achieve); 'RNNs can't "
            "remember dependencies > 20-50 timesteps. LSTMs and GRUs "
            "mitigate... but don't fully solve. Transformers (with attention) "
            "bypass this entirely.' The course: 'the same weight matrix is "
            "applied at every time step, so the gradient product involves the "
            "same matrix raised to a high power,' and explicitly flags the "
            "RNN case as 'closely related but distinct' from the feedforward "
            "case. Nuance: master-ai says eigenvalues/spectral radius, the "
            "course says largest singular value - both describe the same "
            "matrix-growth criterion (the singular-value form is the "
            "norm-precise one); synthesis should use one consistently. "
            "Master-ai-only in scope: the LSTM cell-state additive-highway "
            "explanation and attention-as-bypass (the course's four "
            "solutions include neither). Related: OC-ext010-0001 "
            "(mechanism), OC-ext010-0028 (solution families)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0020",
        "task_id": TASK_ID,
        "topic": "ReLU as the activation-side fix: derivative exactly 1 for active neurons (0 otherwise), no saturation on the positive side, so the gradient passes through unattenuated and very deep networks become trainable",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-c876698a06efa3ed", "KU-3fa0a0938b81d642", "KU-b5f33ba01d6c9868", "KU-053edd65d2767106"],
        "evidence": [
            {"ku_id": "KU-c876698a06efa3ed", "quote": r"""ReLU's derivative is 0 or 1 — no saturation for positive inputs. This largely eliminates vanishing gradients from the activation side.""", "source_path": M08},
            {"ku_id": "KU-3fa0a0938b81d642", "quote": r"""The Jacobian product through ReLU is a product of 1s (for active neurons) — no exponential decay.""", "source_path": M08},
            {"ku_id": "KU-b5f33ba01d6c9868", "quote": r"""Unlike sigmoid (maximum derivative 0.25) or tanh (maximum derivative 1.0 but typically much less), ReLU's derivative of 1 does not attenuate the gradient at all.""", "source_path": C03},
            {"ku_id": "KU-053edd65d2767106", "quote": r"""Combined with proper initialization (Kaiming/He initialization, which accounts for the fact that roughly half the neurons are inactive), ReLU allows stable gradient flow through networks with hundreds of layers.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults make ReLU the activation-side "
            "fix: derivative exactly 1 for active neurons, 0 otherwise - no "
            "saturation on the positive side, so the gradient passes through "
            "unattenuated. Master-ai: 'ReLU's derivative is 0 or 1 - no "
            "saturation for positive inputs. This largely eliminates "
            "vanishing gradients from the activation side' and 'The Jacobian "
            "product through ReLU is a product of 1s (for active neurons) - "
            "no exponential decay.' The course: the derivative-is-exactly-1 "
            "statement, the product-of-ones equation, 'This is the "
            "fundamental reason ReLU enables training of very deep "
            "networks,' and the explicit pairing of ReLU with Kaiming init "
            "(which accounts for roughly half the neurons being inactive) "
            "for stable gradient flow through hundreds of layers. The "
            "course's 'single most important innovation' callout is "
            "course-only emphasis; the dying-ReLU caveat is classified "
            "separately in OC-ext010-0021. Related: OC-ext010-0011 "
            "(Kaiming), OC-ext010-0021 (dying ReLU), OC-ext010-0022 (BN)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0021",
        "task_id": TASK_ID,
        "topic": "The dying ReLU problem (permanently inactive neurons with zero gradient) and the Leaky ReLU / PReLU fixes (small non-zero negative-side gradient; learned slope from the same He et al. 2015 paper)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-3fa0a0938b81d642", "KU-fc6929d23fffe71e", "KU-9bf1c9ae3984c380", "KU-016c4c34c82848dd"],
        "evidence": [
            {"ku_id": "KU-3fa0a0938b81d642", "quote": r"""But if too many neurons are inactive ("dead ReLUs"), the gradient is 0 — a different problem. Leaky ReLU (derivative = 0.01 for $x < 0$) avoids dead neurons.""", "source_path": M08},
            {"ku_id": "KU-fc6929d23fffe71e", "quote": r"""However, ReLU introduces a new problem: the **dying ReLU**. When a neuron's pre-activation $z$ is negative for all training examples, its gradient is zero for all examples, and the neuron can never recover.""", "source_path": C03},
            {"ku_id": "KU-9bf1c9ae3984c380", "quote": r"""For negative inputs, the gradient is $\alpha$ instead of 0. This ensures that even neurons with negative pre-activations receive a small but non-zero gradient, allowing them to potentially recover from a bad configuration.""", "source_path": C03},
            {"ku_id": "KU-016c4c34c82848dd", "quote": r"""PReLU was introduced in the same paper as Kaiming initialization (He et al., 2015) and was used to achieve human-level performance on ImageNet for the first time.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults flag ReLU's failure mode and "
            "its leaky fix: master-ai 'if too many neurons are inactive "
            "(dead ReLUs), the gradient is 0 - a different problem. Leaky "
            "ReLU (derivative = 0.01 for x < 0) avoids dead neurons'; the "
            "course gives the full treatment - the dying-ReLU definition "
            "(pre-activation negative for all training examples; gradient "
            "zero; never recover), causes (bad init; a large update pushing "
            "the neuron permanently negative), the ~50% active fraction "
            "under Kaiming, capacity reduction, Leaky ReLU's small non-zero "
            "alpha gradient enabling recovery, and PReLU (learned alpha, "
            "introduced in the same He et al. 2015 paper as Kaiming init, "
            "first human-level ImageNet result). The PReLU/ELU/SELU variant "
            "coverage is course-only in scope (master-ai covers GELU/SiLU "
            "instead - see OC-ext010-0013). Related: OC-ext010-0020 (ReLU "
            "solution), OC-ext010-0011 (He init)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0022",
        "task_id": TASK_ID,
        "topic": "Normalization (BatchNorm/LayerNorm) as a stability solution: normalizing activations keeps them at a stable scale, preventing multiplicative blow-up/shrinkage and activation saturation",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-b864b359c372cfe5", "KU-06388879634eb15d", "KU-1132b69bf86c135f", "KU-4bd54a7ef07ae071"],
        "evidence": [
            {"ku_id": "KU-b864b359c372cfe5", "quote": r"""Normalizing activations keeps them at a stable scale, preventing the multiplicative blow-up or shrinkage.""", "source_path": M08},
            {"ku_id": "KU-06388879634eb15d", "quote": r"""The key insight is that by centering the pre-activations around zero and scaling them to unit variance, BatchNorm ensures that the activations are always in the **linear region** of the activation function (for sigmoid/tanh) or in the **active region** (for ReLU, where $z > 0$). This prevents saturation, which is the primary mechanism of vanishing gradients.""", "source_path": C03},
            {"ku_id": "KU-1132b69bf86c135f", "quote": r"""BatchNorm prevents them from entering the saturated tails of sigmoid or tanh, where the gradient is near zero.""", "source_path": C03},
            {"ku_id": "KU-4bd54a7ef07ae071", "quote": r"""This self-correcting behavior is the key to BatchNorm's effectiveness.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate on the normalization solution claim. "
            "Master-ai states it generically for LayerNorm/BatchNorm "
            "('Normalizing activations keeps them at a stable scale, "
            "preventing the multiplicative blow-up or shrinkage') with "
            "LayerNorm preferred in its transformer context; the course "
            "develops BatchNorm specifically (Ioffe & Szegedy 2015): "
            "normalize pre-activations to zero mean / unit variance so "
            "activations stay in the linear region (sigmoid/tanh) or active "
            "region (ReLU), which prevents saturation; plus the "
            "self-correcting scale control (weights grow -> normalization "
            "reduces pre-activation scale; weights shrink -> it amplifies) "
            "and the gradient-scale analysis (gamma over "
            "sqrt(sigma_B^2 + epsilon)). Course-only in scope: the "
            "reduces-init-sensitivity treatment and the "
            "partners-not-substitutes caveat (BatchNorm does not break "
            "symmetry); master-ai-only: the LayerNorm/RMSNorm preference for "
            "transformers. Related: OC-ext010-0014 (saturation), "
            "OC-ext010-0028 (solution families), OC-ext010-0033 (the BN "
            "gamma/beta defaults)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0023",
        "task_id": TASK_ID,
        "topic": "Residual connections fix vanishing gradients: y = x + F(x) has Jacobian I + dF/dx, so the identity term guarantees gradient flow (at least the next layer's gradient) and makes 100+ layer networks trainable",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-30a6abf7d2e95e61", "KU-7990b94e5161009e", "KU-fa4a3ffa21b23899", "KU-d6f053d850bf6326", "KU-e9a40eb64de71774", "KU-fcdb1370f4da4b45"],
        "evidence": [
            {"ku_id": "KU-30a6abf7d2e95e61", "quote": r"""The gradient through the residual highway is 1 (identity). So even if $F$'s gradient is tiny, the total gradient is at least 1 — early layers still receive gradient.""", "source_path": M08},
            {"ku_id": "KU-7990b94e5161009e", "quote": r"""The identity term $\mathbf{I}$ ensures the gradient can flow directly, even if $\frac{\partial F}{\partial \mathbf{x}}$ vanishes. This is why 100+ layer networks are trainable with residuals.""", "source_path": M08},
            {"ku_id": "KU-fa4a3ffa21b23899", "quote": r"""This is the single biggest fix for vanishing gradients in deep networks. ResNet enabled 100+ layer CNNs; Transformers rely on residuals for the same reason.""", "source_path": M08},
            {"ku_id": "KU-d6f053d850bf6326", "quote": r"""The critical term is the **$+\mathbf{I}$** (the identity matrix). Even if the Jacobian $\frac{\partial F}{\partial \mathbf{a}^{(l-1)}}$ is very small (which would cause vanishing gradients in a plain network), the identity term ensures that the gradient is at least $\frac{\partial \mathcal{L}}{\partial \mathbf{a}^{(l)}}$, which is the gradient from the next layer.""", "source_path": C03},
            {"ku_id": "KU-e9a40eb64de71774", "quote": r"""The gradient from the output is transmitted **perfectly** to the input through the skip connections, regardless of how many layers the network has. This is the mathematical guarantee that makes ResNet possible — the skip connections provide a "gradient highway" that ensures the learning signal always reaches the early layers.""", "source_path": C03},
            {"ku_id": "KU-fcdb1370f4da4b45", "quote": r"""Even in the worst case where all $J_l = 0$ (meaning the residual functions $F_l$ are completely "flat" and provide no gradient), this product reduces to:""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate with complementary depth. Both vaults derive "
            "the residual guarantee: y = x + F(x) has Jacobian I + dF/dx, and "
            "the identity term ensures gradient flow even when F's gradient "
            "vanishes. Master-ai: 'The gradient through the residual highway "
            "is 1 (identity)... the total gradient is at least 1'; 'This is "
            "the single biggest fix... ResNet enabled 100+ layer CNNs; "
            "Transformers rely on residuals for the same reason'; 'This is "
            "why 100+ layer networks are trainable with residuals.' The "
            "course adds the rigorous stack proof - the product of (J_l + I) "
            "across blocks reduces to I in the worst case where every J_l = "
            "0, so the output gradient reaches the input perfectly "
            "regardless of depth ('gradient highway') - plus the implemented "
            "ResidualBlock and the highway-lanes framing. The worst-case "
            "proof and the code are course-only depth; master-ai adds the "
            "interview-scale claim (without residuals 50+ layers untrainable; "
            "with residuals 1000+ work). Related: OC-ext010-0001 "
            "(mechanism), OC-ext010-0028 (families), OC-ext010-0016 "
            "(what happens without it)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0024",
        "task_id": TASK_ID,
        "topic": "Gradient clipping mechanism: cap the gradient norm at threshold c by rescaling (direction preserved), bounding the update at lr*c; norm clipping is standard (c = 1.0) and preferred over value clipping which can distort direction",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-1546e5342b078734", "KU-c8a664838d8cc36e", "KU-dd23e6b4b54543af", "KU-3287f37867d5962e", "KU-adbda0345528f585", "KU-2257bfaaf1952095", "KU-3c8fb407d7f93421", "KU-32b1dde0ac8ea1de"],
        "evidence": [
            {"ku_id": "KU-1546e5342b078734", "quote": r"""Norm clipping preserves gradient direction; value clipping (per-element) can distort direction.""", "source_path": M08},
            {"ku_id": "KU-c8a664838d8cc36e", "quote": r"""Essential for transformer training. Typical $c = 1.0$. Doesn't fix the underlying cause but prevents training divergence.""", "source_path": M08},
            {"ku_id": "KU-dd23e6b4b54543af", "quote": r"""\text{if } \|\nabla L\| > c: \nabla L \leftarrow c \cdot \frac{\nabla L}{\|\nabla L\|}""", "source_path": M08},
            {"ku_id": "KU-3287f37867d5962e", "quote": r"""torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)""", "source_path": M08},
            {"ku_id": "KU-adbda0345528f585", "quote": r"""**Clip by norm**: Scale the entire gradient vector so that its L2 norm does not exceed a threshold. This preserves the direction of the gradient while limiting its magnitude.""", "source_path": C03},
            {"ku_id": "KU-2257bfaaf1952095", "quote": r"""When the gradient norm exceeds $c$, the gradient is scaled down so that its norm is exactly $c$. The direction of the gradient is preserved — only its magnitude is reduced.""", "source_path": C03},
            {"ku_id": "KU-3c8fb407d7f93421", "quote": r"""This ensures that the maximum size of the weight update (in the L2 norm sense) is bounded by $\eta \cdot c$, where $\eta$ is the learning rate.""", "source_path": C03},
            {"ku_id": "KU-32b1dde0ac8ea1de", "quote": r"""grad_norm = utils.clip_grad_norm_(""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults define clipping mechanically: "
            "cap the gradient norm at a threshold c by rescaling (to c times "
            "g over its norm), preserving direction and bounding the update "
            "size. Master-ai: the cap formula, 'Essential for transformer "
            "training. Typical c = 1.0,' and the direction rule ('Norm "
            "clipping preserves gradient direction; value clipping "
            "(per-element) can distort direction'). The course: the two "
            "variants (clip by value - can change direction; clip by norm - "
            "preserves direction, the commonly used one), the piecewise "
            "formula, the L2-norm definition, the update bound (learning rate "
            "times c, so even a 1000x explosion cannot produce a "
            "catastrophic step), and the threshold guidance (too small: "
            "always clipped, training crawls; too large: no protection; the "
            "1.0-5.0 sweet spot; monitor typical norms and set c slightly "
            "above - course-only guidance). Both agree on the standard "
            "value: master-ai names max norm 1.0 as standard in GPT/Llama/"
            "Mistral recipes; the course's typical values include 1.0. "
            "Related: OC-ext010-0025 (limits), OC-ext010-0018 (spikes), "
            "OC-ext010-0026 (monitoring)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0025",
        "task_id": TASK_ID,
        "topic": "Clipping is symptomatic treatment, not a root-cause fix: it cannot help vanishing gradients and must not become a crutch masking bad init/LR/architecture (frequent clipping is a red flag)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-543a2f6023bb2705", "KU-fbfd469a708b4d50", "KU-a5cf7aa628be249e"],
        "evidence": [
            {"ku_id": "KU-543a2f6023bb2705", "quote": r"""This prevents the explosion from causing divergence, but doesn't help with vanishing (you can't clip a 0 gradient to be larger). Standard for Transformers (typical $c = 1.0$).""", "source_path": M08},
            {"ku_id": "KU-fbfd469a708b4d50", "quote": r"""It does not address the root cause of exploding gradients (poor initialization, bad architecture, or excessively high learning rate) — it merely prevents the most catastrophic symptom (divergence to `NaN`).""", "source_path": C03},
            {"ku_id": "KU-a5cf7aa628be249e", "quote": r"""If you find that your gradients are frequently being clipped (more than 10% of the time), this is a sign that something else is wrong. Investigate the root cause before relying on clipping as a permanent solution.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate on the philosophy: clipping is symptomatic "
            "treatment, not a root-cause fix, and must not become a crutch. "
            "Master-ai: 'This prevents the explosion from causing divergence, "
            "but doesn't help with vanishing (you can't clip a 0 gradient to "
            "be larger).' The course: 'It does not address the root cause of "
            "exploding gradients (poor initialization, bad architecture, or "
            "excessively high learning rate) - it merely prevents the most "
            "catastrophic symptom (divergence to NaN),' the "
            "use-all-four-together recommendation, and the red-flag callout "
            "(clipped more than 10% of the time means something else is "
            "wrong - investigate the root cause before relying on clipping "
            "as a permanent solution). Master-ai's production rule ('Always "
            "use gradient clipping for transformer training. Max norm 1.0 is "
            "standard') and the course's safety-net framing (with the first "
            "three solutions in place, explosions are rare and clipping may "
            "never trigger, but it prevents a single bad step from destroying "
            "the run) agree operationally. Related: OC-ext010-0024 "
            "(mechanism), OC-ext010-0028 (combined use)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0026",
        "task_id": TASK_ID,
        "topic": "Primary diagnostic practice: log gradient norms per layer (healthy training has roughly constant norms across layers; steady decline means vanishing, spikes mean instability) and monitor from the very first steps",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-bd9f37fd90f0682d", "KU-1f9c00801fd2da3e", "KU-6190577c79303924", "KU-4db86cd3c5687e79", "KU-5a441e4da19b84eb"],
        "evidence": [
            {"ku_id": "KU-bd9f37fd90f0682d", "quote": r"""To diagnose: log gradient norms per layer per step. A healthy training run has roughly constant gradient norms across layers.""", "source_path": M08},
            {"ku_id": "KU-1f9c00801fd2da3e", "quote": r"""- **Monitor gradient norms** per layer. Sudden spikes → instability. Steady decline → vanishing.""", "source_path": M08},
            {"ku_id": "KU-6190577c79303924", "quote": r"""- **No gradient logging** → can't diagnose issues when they appear.""", "source_path": M08},
            {"ku_id": "KU-4db86cd3c5687e79", "quote": r"""The most direct way to diagnose gradient flow problems is to monitor the norm of the gradients at each layer during training.""", "source_path": C03},
            {"ku_id": "KU-5a441e4da19b84eb", "quote": r"""By monitoring gradient norms from the very first step, you can detect vanishing or exploding gradients early and adjust your initialization, learning rate, or architecture before wasting hours of training time.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults prescribe per-layer "
            "gradient-norm logging as the primary diagnostic and warn "
            "against flying blind. Master-ai: 'To diagnose: log gradient "
            "norms per layer per step. A healthy training run has roughly "
            "constant gradient norms across layers'; 'Monitor gradient "
            "norms per layer. Sudden spikes -> instability. Steady decline "
            "-> vanishing'; 'No gradient logging -> can't diagnose issues "
            "when they appear'; plus its diagnose_gradients code "
            "(max/min ratio thresholds 1000/100). The course: 'The most "
            "direct way to diagnose gradient flow problems is to monitor the "
            "norm of the gradients at each layer during training' (with the "
            "vanishing/exploding/healthy/NaN interpretation guide), the "
            "monitor_gradient_norms implementation, and the early-detection "
            "callout (by the time loss is NaN the weights are corrupted and "
            "must be re-initialized; monitor from the very first step and "
            "adjust init/LR/architecture before wasting hours). The code "
            "implementations differ (complementary artifacts for synthesis); "
            "the diagnostic claim is duplicated. Related: OC-ext010-0017 "
            "(symptoms), OC-ext010-0030 (init-side verification), "
            "OC-ext010-0035 (NaN priority)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0027",
        "task_id": TASK_ID,
        "topic": "Worked numerical demonstrations of sigmoid-network gradient decay (master-ai's 20-layer MNIST norm table vs the course's 0.25-decay diagram and alpha^(L-l) compounding table) - distinct artifacts illustrating the same exponential decay",
        "overlap_type": "Complementary Content",
        "ku_ids": ["KU-e74a8671d37d9b03", "KU-1f55cb93c50ea2e5", "KU-d7cb54212a66bf74", "KU-9523b57f763ee919"],
        "evidence": [
            {"ku_id": "KU-e74a8671d37d9b03", "quote": r"""Train a 20-layer plain MLP (no residuals, sigmoid activations) on MNIST. Log the gradient norm at each layer:""", "source_path": M08},
            {"ku_id": "KU-1f55cb93c50ea2e5", "quote": r"""Layer 1's gradients are 8 orders of magnitude smaller than layer 20's — it's effectively not learning.""", "source_path": M08},
            {"ku_id": "KU-d7cb54212a66bf74", "quote": r"""With $\alpha = 0.5$ (which is typical for sigmoid networks), the gradient after just 10 layers is $0.5^{10} \approx 0.001$ of its original value.""", "source_path": C03},
            {"ku_id": "KU-9523b57f763ee919", "quote": r"""The gradient at layer $l$ in a sigmoid network with $L$ total layers is approximately $0.25^{L-l}$ times the gradient at the output.""", "source_path": C03},
        ],
        "rationale": (
            "Complementary Content: the two vaults provide DIFFERENT worked "
            "numerical demonstrations of the same exponential-decay "
            "phenomenon, and both must be preserved at synthesis as separate "
            "illustrations - neither is a duplicate of the other. "
            "Master-ai's worked example: a 20-layer plain MLP (no residuals, "
            "sigmoid) on MNIST with a per-layer gradient-norm table running "
            "1.0 at layer 20 down to 1e-8 at layer 1 ('8 orders of "
            "magnitude smaller... effectively not learning'), plus the "
            "healthy contrast (ReLU + residuals + LayerNorm keeps norms "
            "within one order of magnitude). The course's demonstrations: "
            "the per-layer 0.25-decay mermaid diagram (1.0 at layer 10 down "
            "to 3.8e-6 at layer 1), the 0.25^(L-l) visualization callout, "
            "and the alpha^(L-l) compounding table (0.9^50 ~ 0.005; 0.5^50 ~ "
            "1e-15; 2.0^50 ~ 1e15, versus 32-bit resolution ~1e-7). The "
            "shared underlying claim is classified in OC-ext010-0001/0014; "
            "THIS record exists so neither demonstration is dropped as a "
            "'duplicate' - they are distinct artifacts with different "
            "numbers, depths, and pedagogical devices. Related: "
            "OC-ext010-0014 (sigmoid ceiling), OC-ext010-0016 (early-layer "
            "effect)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0028",
        "task_id": TASK_ID,
        "topic": "Solution families for vanishing/exploding gradients and their deliberate combination in modern architectures (master-ai enumerates seven families incl. gates/attention/init; the course enumerates four; both say they are used together and enable very deep networks)",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-d649bbed1e800d4e", "KU-1f9c00801fd2da3e", "KU-7699d605c52510dc", "KU-8bd0cc12896496a0", "KU-60db14933bbeb92a"],
        "evidence": [
            {"ku_id": "KU-d649bbed1e800d4e", "quote": r"""- Every Transformer architecture choice — residuals, LayerNorm, ReLU/SwiGLU, init scheme — is partly motivated by avoiding vanishing/exploding gradients.""", "source_path": M08},
            {"ku_id": "KU-1f9c00801fd2da3e", "quote": r"""- **Use a known-good architecture** (Transformer with residuals + RMSNorm + SwiGLU) rather than inventing your own. The vanishing/exploding gradient issues have been engineered out.""", "source_path": M08},
            {"ku_id": "KU-7699d605c52510dc", "quote": r"""The deep learning community has developed four major solutions to these problems. Each addresses the issue from a different angle, and in practice, modern architectures use all four together for maximum effectiveness.""", "source_path": C03},
            {"ku_id": "KU-8bd0cc12896496a0", "quote": r"""Modern deep learning architectures use **all four solutions together**:""", "source_path": C03},
            {"ku_id": "KU-60db14933bbeb92a", "quote": r"""This combination of techniques is what enables the training of networks with hundreds or even thousands of layers, such as ResNet-152, DenseNet-264, and the deep transformers used in modern NLP and computer vision models.""", "source_path": C03},
        ],
        "rationale": (
            "Partial Overlap on the solution-family enumeration and its "
            "combined use. Shared claim: modern deep architectures "
            "deliberately combine the stability solutions, and that "
            "combination is what makes very deep networks trainable - "
            "master-ai ('Every Transformer architecture choice - residuals, "
            "LayerNorm, ReLU/SwiGLU, init scheme - is partly motivated by "
            "avoiding vanishing/exploding gradients'; 'Use a known-good "
            "architecture... The vanishing/exploding gradient issues have "
            "been engineered out') and the course ('four major solutions... "
            "modern architectures use all four together'; 'Modern deep "
            "learning architectures use all four solutions together'; the "
            "combination 'enables... ResNet-152, DenseNet-264, and the deep "
            "transformers'). The families differ in breadth: master-ai's "
            "comparison table enumerates seven (ReLU family, residual "
            "connections, LayerNorm/BatchNorm, He/Xavier init, gradient "
            "clipping, LSTM/GRU gates, attention) while the course "
            "enumerates four (ReLU + variants, BatchNorm, residual "
            "connections, gradient clipping), treating initialization in "
            "its own chapter and omitting gated/attention families. The "
            "overlap is partial: the four course families are a subset of "
            "master-ai's seven; the combined-use claim is duplicated. "
            "Synthesis should enumerate the union and credit both framings. "
            "Related: OC-ext010-0020/0022/0023/0024 (the individual "
            "families), OC-ext010-0019 (gates and attention as "
            "master-ai-only families in this scope)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0029",
        "task_id": TASK_ID,
        "topic": "Fine-tuning rule: the initialization IS the pretrained weights - do not re-init them; only newly added layers need explicit initialization, and that init matters much less",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-cee3ae9e620e9e93", "KU-43e790f77b1f0efb", "KU-9113fddbf23c257a"],
        "evidence": [
            {"ku_id": "KU-cee3ae9e620e9e93", "quote": r"""- For **fine-tuning**, init is the pretrained weights — you don't re-init. But you do init the **new** parameters (LoRA's B matrix starts at zero, for example).""", "source_path": M07},
            {"ku_id": "KU-43e790f77b1f0efb", "quote": r"""- **Don't re-init when fine-tuning** — start from pretrained weights.""", "source_path": M07},
            {"ku_id": "KU-9113fddbf23c257a", "quote": r"""**Transfer learning / Fine-tuning**: When you start from pre-trained weights (e.g., a ResNet trained on ImageNet), the initialization is the pre-trained weights, which are already in a good region of the loss landscape.""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate on the fine-tuning rule, with master-ai-only "
            "LoRA depth. Shared claim: when fine-tuning, the initialization "
            "IS the pretrained weights - you do not re-initialize them; only "
            "newly added layers need explicit init, and that init matters "
            "much less. Master-ai: 'For fine-tuning, init is the pretrained "
            "weights - you don't re-init. But you do init the new "
            "parameters' plus 'Don't re-init when fine-tuning - start from "
            "pretrained weights.' The course: 'Transfer learning / "
            "Fine-tuning: ... the initialization is the pre-trained weights, "
            "which are already in a good region of the loss landscape... You "
            "only need to initialize the new layers... much less critical.' "
            "Master-ai-only in scope (recorded, not separately classified): "
            "the LoRA special case (A Kaiming, B zero, so delta-W = 0 at "
            "start; the fine-tune-degrades failure row for B-not-zero; the "
            "LoRALinear code; and the interview rationale that random A and "
            "B would perturb the base model). Related: OC-ext010-0013 "
            "(matching rule for fresh training), OC-ext010-0030 "
            "(verification practice)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0030",
        "task_id": TASK_ID,
        "topic": "Verify initialization empirically: forward a random input through the freshly initialized network and check that activation magnitudes/variances stay roughly constant across layers",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-43e790f77b1f0efb", "KU-4c5ec2f689be8e70", "KU-9154ee7a2678f518"],
        "evidence": [
            {"ku_id": "KU-43e790f77b1f0efb", "quote": r"""- **For custom architectures**, think carefully about init. Test that activation magnitudes are roughly constant across layers at initialization (forward a random input, log per-layer norms).""", "source_path": M07},
            {"ku_id": "KU-4c5ec2f689be8e70", "quote": r"""One of the best ways to verify that your initialization is correct is to track the variance of activations at each layer during a forward pass with random input. If the variance remains roughly constant across layers, the initialization is well-calibrated.""", "source_path": C01},
            {"ku_id": "KU-9154ee7a2678f518", "quote": r"""If you notice that the variance systematically decreases across layers, your initialization is too conservative — try increasing the weight scale (e.g., switch from Xavier to Kaiming).""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults prescribe the same verification "
            "practice for custom architectures: forward a random input "
            "through the freshly initialized network and check that "
            "activation magnitudes/variances stay roughly constant across "
            "layers. Master-ai: 'Test that activation magnitudes are roughly "
            "constant across layers at initialization (forward a random "
            "input, log per-layer norms).' The course: 'track the variance of "
            "activations at each layer during a forward pass with random "
            "input. If the variance remains roughly constant across layers, "
            "the initialization is well-calibrated,' with its VarianceTracker "
            "hook implementation and the debugging callout (variance "
            "decreasing -> too conservative, increase the scale, e.g. switch "
            "Xavier to Kaiming; increasing -> too aggressive). The hook "
            "implementation and the drift-remediation mapping are course-only "
            "depth. Related: OC-ext010-0006 (the calibration goal), "
            "OC-ext010-0026 (gradient-side monitoring)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0031",
        "task_id": TASK_ID,
        "topic": "Seed and scheme fixing for reproducibility: run-to-run variance traces to unfixed seeds/initialization; reproduce results with the same init scheme and random seed",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-ff7bc655b9104574", "KU-66e2f18ec3e1969b", "KU-557bf14b92becf87"],
        "evidence": [
            {"ku_id": "KU-ff7bc655b9104574", "quote": r"""| Different runs give very different results | Init seed not fixed | Set torch.manual_seed; document seed in config |""", "source_path": M07},
            {"ku_id": "KU-66e2f18ec3e1969b", "quote": r"""| Different runs give very different results | Init variance; no seed | Set seed; use He/Xavier init |""", "source_path": M08},
            {"ku_id": "KU-557bf14b92becf87", "quote": r"""If you need to reproduce a specific result, you must use the same initialization scheme (and the same random seed).""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults connect run-to-run variance to "
            "unfixed seeds/initialization and prescribe fixing the seed (and "
            "matching init) for reproducibility. Master-ai states it in BOTH "
            "failure tables - the init note ('Different runs give very "
            "different results | Init seed not fixed | Set "
            "torch.manual_seed; document seed in config') and the gradients "
            "note ('Different runs give very different results | Init "
            "variance; no seed | Set seed; use He/Xavier init'). The course "
            "states it in the when-init-matters section (reproducing "
            "research results requires the same initialization scheme and "
            "the same random seed, since different initializations can "
            "yield different final accuracies even with identical "
            "hyperparameters). Related: OC-ext010-0033 (defaults), "
            "OC-ext010-0002 (why the starting point matters)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0032",
        "task_id": TASK_ID,
        "topic": "PyTorch manual-initialization workflow: torch.nn.init functions applied in place (xavier_normal_, kaiming_normal_ with fan_in/relu, kaiming_uniform_), biases zeroed, and a recursive init function applied via model.apply()",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-ceb4e6cb31a70b63", "KU-a1adbd202f549e3c", "KU-73c9712ccf3d8d42", "KU-61d1abd4ad302190"],
        "evidence": [
            {"ku_id": "KU-ceb4e6cb31a70b63", "quote": r"""nn.init.xavier_normal_(linear.weight)""", "source_path": M07},
            {"ku_id": "KU-a1adbd202f549e3c", "quote": r"""init.kaiming_uniform_(linear.weight,""", "source_path": C01},
            {"ku_id": "KU-73c9712ccf3d8d42", "quote": r"""The standard approach is to define an initialization function that recursively visits every module in the model and applies the appropriate initialization based on the module type.""", "source_path": C01},
            {"ku_id": "KU-61d1abd4ad302190", "quote": r"""model.apply(init_weights)""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate (practice-level). Both vaults demonstrate the "
            "same PyTorch manual-initialization workflow: the torch.nn.init "
            "functions applied in place, bias zeroed, and a recursive init "
            "function applied via model.apply(). Master-ai's worked example: "
            "xavier_normal_ on a Linear for tanh, kaiming_normal_ with "
            "mode='fan_in', nonlinearity='relu' on a Conv2d, normal_ std 0.02 "
            "for a transformer-style layer, zeros_ for bias. The course: the "
            "same API family (xavier_normal_, xavier_uniform_, "
            "kaiming_normal_ fan_in relu, kaiming_uniform_, zeros_ on bias), "
            "the init_weights function pattern recursively applied with "
            "model.apply(init_weights), the Xavier variant for sigmoid/tanh "
            "networks, and the advanced orthogonal/sparse initializers "
            "(course-only). Master-ai-only: the transformer-style std-0.02 "
            "example. Related: OC-ext010-0033 (defaults), OC-ext010-0012 "
            "(fan modes), OC-ext010-0036 (bias)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0033",
        "task_id": TASK_ID,
        "topic": "Rely on / know the PyTorch default initializations: master-ai endorses the framework defaults as well-chosen; the course documents them (Conv2d and Linear use Kaiming Uniform, fan_in, a = sqrt(5))",
        "overlap_type": "Partial Overlap",
        "ku_ids": ["KU-43e790f77b1f0efb", "KU-bde76c74d3c8678a", "KU-1324d50530a9206a", "KU-e5251c5a48599a25"],
        "evidence": [
            {"ku_id": "KU-43e790f77b1f0efb", "quote": r"""- **Use the default inits from PyTorch/HuggingFace** — they're well-chosen for the standard architectures.""", "source_path": M07},
            {"ku_id": "KU-bde76c74d3c8678a", "quote": r"""PyTorch initializes `Conv2d` weights using **Kaiming Uniform** with `fan_in` mode and `a = sqrt(5)` (where `a` is the negative slope of the Leaky ReLU, used to compute the gain).""", "source_path": C01},
            {"ku_id": "KU-1324d50530a9206a", "quote": r"""Fully-connected (`Linear`) layers use the same initialization as `Conv2d`: Kaiming Uniform with $a = \sqrt{5}$.""", "source_path": C01},
            {"ku_id": "KU-e5251c5a48599a25", "quote": r"""In PyTorch, `torch.nn.Conv2d` uses **Kaiming uniform initialization** by default.""", "source_path": C02},
        ],
        "rationale": (
            "Partial Overlap. Master-ai recommends relying on framework "
            "defaults without specifying them ('Use the default inits from "
            "PyTorch/HuggingFace - they're well-chosen for the standard "
            "architectures'); the course documents the defaults themselves: "
            "Conv2d and Linear both use Kaiming Uniform with fan_in mode and "
            "a = sqrt(5), which simplifies to U(-sqrt(1/n_in), sqrt(1/n_in)) "
            "- 'a slightly more conservative initialization than the standard "
            "Kaiming Uniform,' a historical artifact that works well in "
            "practice (with the bounded-support rationale in its callout) - "
            "and course file 02 agrees ('In PyTorch, torch.nn.Conv2d uses "
            "Kaiming uniform initialization by default'). The shared content "
            "is the endorsement of framework defaults; the specification is "
            "course-only, hence Partial Overlap. CAVEAT recorded for "
            "synthesis (finding F-0009): the course is internally "
            "inconsistent about the Conv2d BIAS default - file 01 says "
            "'Biases are initialized to zero' while file 02 (and the "
            "course's own Linear section) give the uniform bound "
            "(-1/sqrt(fan_in), 1/sqrt(fan_in)), the latter matching PyTorch's "
            "actual reset_parameters; the WEIGHT-default documentation is "
            "consistent across both course files and both vaults. Related: "
            "OC-ext010-0012 (Kaiming), OC-ext010-0036 (bias standard), "
            "F-0009."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0034",
        "task_id": TASK_ID,
        "topic": "Historical placement: before 2010, ad-hoc/uncalibrated initialization kept deep networks untrainable; principled initialization (Glorot & Bengio 2010, He et al. 2015) was a prerequisite for the deep-learning revolution",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-fe97a4aad8fcec8b", "KU-5b3c49a84a4303ca", "KU-42ff10a0ac6c4bd4", "KU-d5526008203e1c1f", "KU-796a79418fdf7393"],
        "evidence": [
            {"ku_id": "KU-fe97a4aad8fcec8b", "quote": r"""Without these schemes, deep networks (10+ layers) were untrainable — activations exploded or vanished. Xavier/He init was a prerequisite for the deep learning revolution.""", "source_path": M07},
            {"ku_id": "KU-5b3c49a84a4303ca", "quote": r"""- Glorot & Bengio (2010), *Understanding the Difficulty of Training Deep Feedforward Neural Networks*.""", "source_path": M07},
            {"ku_id": "KU-42ff10a0ac6c4bd4", "quote": r"""Before 2010, practitioners used ad-hoc initializations that often failed for networks deeper than 3-4 layers.""", "source_path": C01},
            {"ku_id": "KU-d5526008203e1c1f", "quote": r"""This initialization was common in the early days of deep learning (before 2010) and is one reason why deep networks were considered impossible to train — the weights were simply too small for gradients to propagate through many layers.""", "source_path": C01},
            {"ku_id": "KU-796a79418fdf7393", "quote": r"""Without ReLU, batch normalization, residual connections, and gradient clipping, training networks deeper than a few layers would remain essentially impossible.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate. Both vaults place the schemes historically: "
            "before 2010, ad-hoc/uncalibrated initialization kept deep "
            "networks untrainable, and principled initialization was a "
            "prerequisite for the deep-learning revolution. Master-ai: "
            "'Without these schemes, deep networks (10+ layers) were "
            "untrainable - activations exploded or vanished. Xavier/He init "
            "was a prerequisite for the deep learning revolution' (citing "
            "Glorot & Bengio 2010 and He et al. 2015 in Further Reading). "
            "The course: the N(0, 0.01) era 'is one reason why deep networks "
            "were considered impossible to train'; 'Before 2010, "
            "practitioners used ad-hoc initializations that often failed for "
            "networks deeper than 3-4 layers. Glorot and Bengio's analysis "
            "showed that the failure was not fundamental'; and the "
            "gradients-side parallel ('Without ReLU, batch normalization, "
            "residual connections, and gradient clipping, training networks "
            "deeper than a few layers would remain essentially impossible'). "
            "Dating is consistent across both vaults (Glorot & Bengio 2010; "
            "He et al. 2015) - unlike the F-0007 boosted-tree case, no "
            "reconciliation finding is needed. Course-only: the "
            "opened-the-door-to-VGG/ResNet remark; master-ai-only: the "
            "Hochreiter 1991 and Pascanu 2013 references. Related: "
            "OC-ext010-0006 (calibration), OC-ext010-0028 (combined "
            "solutions), OC-ext010-0011 (He 2015)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0035",
        "task_id": TASK_ID,
        "topic": "Diagnostic priority when loss goes NaN: suspect exploding gradients / too-large weights first (check init, add clipping, reduce LR) before blaming the data pipeline or loss function",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-66e2f18ec3e1969b", "KU-736533dfa2352573", "KU-231d2e1095fb8954"],
        "evidence": [
            {"ku_id": "KU-66e2f18ec3e1969b", "quote": r"""| Training diverges (loss → NaN) | Exploding gradients | Add gradient clipping; reduce LR; check init |""", "source_path": M08},
            {"ku_id": "KU-736533dfa2352573", "quote": r"""If your training loop produces `NaN` loss within the first few iterations, the most common cause is that the weights are too large, causing activation and gradient overflow. Before debugging your data pipeline or loss function, check your weight initialization.""", "source_path": C01},
            {"ku_id": "KU-231d2e1095fb8954", "quote": r"""If the loss becomes `NaN` at any point, it indicates that the gradients have exploded and corrupted the weights. This is a critical failure that requires immediate intervention.""", "source_path": C03},
        ],
        "rationale": (
            "Semantic Duplicate on the diagnostic priority: NaN loss early in "
            "training points at too-large weights / exploding gradients, and "
            "initialization should be checked before blaming the data "
            "pipeline or loss function. Master-ai's gradients failure table: "
            "'Training diverges (loss -> NaN) | Exploding gradients | Add "
            "gradient clipping; reduce LR; check init.' The course: 'If your "
            "training loop produces NaN loss within the first few iterations, "
            "the most common cause is that the weights are too large, causing "
            "activation and gradient overflow. Before debugging your data "
            "pipeline or loss function, check your weight initialization,' "
            "and from the gradients file: 'If the loss becomes NaN at any "
            "point, it indicates that the gradients have exploded and "
            "corrupted the weights. This is a critical failure that requires "
            "immediate intervention.' Related: OC-ext010-0004 (explosion), "
            "OC-ext010-0017 (symptoms), OC-ext010-0026 (monitoring), "
            "OC-ext010-0024 (clipping response)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext010-0036",
        "task_id": TASK_ID,
        "topic": "Bias initialization standard: zeros is the simple, standard default for bias parameters (with documented exceptions on the master-ai side)",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": ["KU-76aba79684bf4c0f", "KU-f36687797fee3162", "KU-a1adbd202f549e3c"],
        "evidence": [
            {"ku_id": "KU-76aba79684bf4c0f", "quote": r"""- **Standard**: zeros. Simple, works fine.""", "source_path": M07},
            {"ku_id": "KU-f36687797fee3162", "quote": r"""Biases are initialized to zero.""", "source_path": C01},
            {"ku_id": "KU-a1adbd202f549e3c", "quote": r"""init.zeros_(linear.bias)""", "source_path": C01},
        ],
        "rationale": (
            "Semantic Duplicate on the shared claim, scoped deliberately: "
            "zeros is the standard, simple bias initialization. Master-ai's "
            "dedicated bias-init list opens 'Standard: zeros. Simple, works "
            "fine' (before its special cases); the course states 'Biases are "
            "initialized to zero' within its PyTorch-defaults narrative and "
            "its manual-init code zeroes biases throughout (zeros_ on bias in "
            "the apply-pattern). The overlap is the RECOMMENDATION, not the "
            "PyTorch-default attribution: master-ai's special cases (LSTM "
            "forget-gate bias 1.0; output-layer bias to inverse class "
            "frequency; final unembedding zeros) are master-ai-only in scope, "
            "and the course's attribution of a zero-bias default to PyTorch "
            "Conv2d is internally contradicted by its own file 02 and "
            "Linear-section uniform statement - recorded as finding F-0009 "
            "and cross-referenced from OC-ext010-0033, to be reconciled at "
            "synthesis (PyTorch's actual reset_parameters uses a uniform "
            "bound for Conv2d/Linear biases). Related: OC-ext010-0033 "
            "(defaults), F-0009."
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


def locate(quote: str, file_lines: list[str], span_lo: int, span_hi: int) -> list[int]:
    """X2 locator: find the quote's ORIGINAL source lines inside the KU span.

    Returns the full contiguous line range covered by the (unique) in-span
    occurrence. Raises ValueError when the quote is absent from the span or
    ambiguous (multiple in-span occurrences).
    """
    text = "\n".join(file_lines)
    occurrences: list[tuple[int, int]] = []
    start = 0
    while True:
        i = text.find(quote, start)
        if i == -1:
            break
        lo = text.count("\n", 0, i) + 1
        hi = text.count("\n", 0, i + len(quote) - 1) + 1
        occurrences.append((lo, hi))
        start = i + 1
    in_span = [(lo, hi) for (lo, hi) in occurrences
               if span_lo <= lo and hi <= span_hi]
    if not in_span:
        raise ValueError(
            f"quote not found inside KU span {span_lo}-{span_hi} "
            f"(file-wide occurrences: {occurrences})")
    if len(in_span) > 1:
        raise ValueError(
            f"quote has {len(in_span)} in-span occurrences {in_span} - "
            f"extend the quote for uniqueness")
    lo, hi = in_span[0]
    return list(range(lo, hi + 1))


def main() -> int:
    failures: list[str] = []
    kus = load_kus()
    hashes_before = committed_hashes()

    populated: list[dict] = []
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

        new_evidence: list[dict] = []
        source_cache: dict[str, list[str]] = {}
        for ev in rec["evidence"]:
            ku = kus.get(ev["ku_id"])
            if ku is None:
                continue
            if not ev["quote"].strip():
                failures.append(f"{cid}: empty quote for {ev['ku_id']}")
                continue
            # X1: byte-exact inside the KU excerpt.
            if ev["quote"] not in ku["excerpt"]:
                failures.append(
                    f"{cid}: X1 quote NOT byte-exact in excerpt of "
                    f"{ev['ku_id']}: {ev['quote'][:80]!r}")
            # X1b: evidence source_path must equal the KU's source_path.
            if ev["source_path"] != ku["source_path"]:
                failures.append(f"{cid}: source_path mismatch for {ev['ku_id']}")
            # X2: machine-locate at original source lines.
            if ku["source_path"] not in source_cache:
                src = source_root(ku["source_id"]) / ku["source_path"]
                source_cache[ku["source_path"]] = src.read_text(
                    encoding="utf-8").splitlines()
            file_lines = source_cache[ku["source_path"]]
            try:
                lines = locate(ev["quote"], file_lines,
                               ku["line_start"], ku["line_end"])
            except ValueError as exc:
                failures.append(f"{cid}: X2 {exc} [ku {ev['ku_id']}]")
                lines = [0]
            lo, hi = min(lines), max(lines)
            if ev["quote"] not in "\n".join(file_lines[lo - 1:hi]):
                failures.append(
                    f"{cid}: X2 recheck failed for {ev['ku_id']} at {lo}-{hi}")
            new_evidence.append({**ev, "lines": lines})
        # duplicate evidence entries within record
        quotes = [e["quote"] for e in rec["evidence"]]
        if len(quotes) != len(set(quotes)):
            failures.append(f"{cid}: duplicate evidence quotes within record")
        populated.append({**rec, "evidence": new_evidence})

    # X7: unique, sequential ids.
    ids = [r["classification_id"] for r in RECORDS]
    if len(ids) != len(set(ids)):
        failures.append("duplicate classification ids")
    for i, cid in enumerate(ids, start=1):
        if not cid.endswith(f"-{i:04d}"):
            failures.append(f"non-sequential id {cid}")

    # X8: no duplicate quote strings anywhere in the file.
    all_quotes = [e["quote"] for r in populated for e in r["evidence"]]
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
    for rec in populated:
        for err in validator.iter_errors(rec):
            failures.append(
                f"{rec['classification_id']}: schema: {err.message} "
                f"at {list(err.absolute_path)}")

    if failures:
        print("VERIFICATION FAILURES:")
        for f in failures:
            print("  -", f)
        return 1

    # X9: committed classification files byte-unchanged.
    hashes_after = committed_hashes()
    for p, h in hashes_before.items():
        if hashes_after[p] != h:
            print(f"X9 FAILURE: committed file changed during run: {p}")
            return 1

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                for r in populated),
        encoding="utf-8",
    )
    types: dict[str, int] = {}
    for r in populated:
        types[r["overlap_type"]] = types.get(r["overlap_type"], 0) + 1
    participating = sorted({k for r in populated for k in r["ku_ids"]})
    print(f"wrote {OUT.relative_to(REPO)}: {len(populated)} records "
          f"({', '.join(f'{v} {k}' for k, v in sorted(types.items()))}), "
          f"{len(participating)} participating KUs, "
          f"{sum(len(r['evidence']) for r in populated)} byte-exact quotes "
          f"(all machine-located at original source lines; X1-X9 green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
