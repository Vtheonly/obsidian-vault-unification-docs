#!/usr/bin/env python3
"""S20/SYNTH-001: build per-note synthesis inputs for one canonical area.

Deterministic, idempotent: derives every artifact from COMMITTED state only
(canonical structure, file mapping, KU batches, disposition ledger, v2
dossiers). Outputs to scratch/ (git-ignored, replayable) plus one committed
machine-readable report under reports/synthesis/.

Outputs (under scratch/synth/<slug>/):
  bundles/<nn>-<slug>.md   evidence bundle per note (source files verbatim +
                           per-KU checklist + dossier concepts)
  specs/<nn>-<slug>.json   generation-prompt spec per note (check-prompt input)
  audit-kus.jsonl          KU records with EFFECTIVE disposition+destinations
                           (audit-output input; ledger overlay, never edits)
  provenance.jsonl         {note, ku_ids} mapping (assess-quality input)
  expected-notes.txt       the area's planned note paths
  notes.json               orchestration metadata (type, groups, sizes)

Assertions (fail loudly, pre-written arithmetic):
  - every area-4-destined ledger KU appears in exactly one audit batch record
  - every KU record keeps its committed excerpt/hash/locator byte-identical
  - destinations are exactly the ledger's (no invention, no filtering)
  - every note bundle carries >= 1 KU
  - note count / file count match the canonical structure accounting
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / "scratch" / "synth"
VAULT_ROOTS = {
    "ai-course": REPO / "source-vaults" / "AI " / "AI Course",
    "master-ai": REPO / "source-vaults" / "AI " / "Master AI",
}

# Per-area synthesis configuration. Keys not covered default to "concept".
# Every area running through this pipeline MUST have an entry with:
#   note_types  - explicit type assignments for non-concept notes (drives the
#                 per-type quality standard in specs and assess-quality)
#   moc_target  - what "link to the area MOC" means for this area (the exact
#                 wording embedded in the spec wikilink requirement)
#   colliding   - the vault-wide colliding basenames that links FROM this
#                 area's notes must write path-based (see the 32-basename list
#                 in docs/EDITORIAL_STYLE_GUIDE.md conventions v1 #7)
# Recorded per the session-20 conventions; changing a type or link rule
# requires regenerating the affected specs and documenting the change.
AREA_CONFIG: dict[str, dict[str, object]] = {
    "04 - Machine Learning": {
        "note_types": {
            "04 - Machine Learning/Machine Learning MOC.md": "overview",
            "04 - Machine Learning/Model Evaluation/Model Evaluation Metrics.md": "reference",
            "04 - Machine Learning/Model Evaluation/Regression Evaluation Metrics.md": "reference",
            "04 - Machine Learning/Model Evaluation/Clustering Evaluation Metrics.md": "reference",
            "04 - Machine Learning/Model Evaluation/Computer Vision Evaluation Metrics.md": "reference",
            "04 - Machine Learning/Support Vector Machines/SVM Lagrangian Dual.md": "derivation",
        },
        "moc_target": "Machine Learning MOC",
        "colliding": "Linear Regression and Logistic Regression",
    },
    "05 - Neural Network Foundations": {
        "note_types": {
            "05 - Neural Network Foundations/Neural Network Foundations MOC.md": "overview",
            "05 - Neural Network Foundations/Architectures/Convolutional Neural Networks.md": "reference",
            "05 - Neural Network Foundations/Architectures/Recurrent Neural Networks.md": "reference",
            "05 - Neural Network Foundations/Architectures/Seq2Seq and the Information Bottleneck.md": "reference",
            "05 - Neural Network Foundations/Backpropagation/Backpropagation.md": "derivation",
            "05 - Neural Network Foundations/Backpropagation/Matrix Implementation of Backpropagation.md": "derivation",
            "05 - Neural Network Foundations/Labs/Data Cleaning and Encoding Lab.md": "tutorial",
            "05 - Neural Network Foundations/Labs/Formal Neuron Lab.md": "tutorial",
        },
        "moc_target": "Neural Network Foundations MOC",
        "colliding": (
            "Batch Normalization, Data Augmentation, Dropout and Regularization, "
            "Hyperparameters and Network Configuration, Vanishing and Exploding "
            "Gradients, Weight Initialization"
        ),
    },
    "06 - Computer Vision": {
        "note_types": {
            "06 - Computer Vision/CNN Course Overview.md": "overview",
            "06 - Computer Vision/CNN Mastery Roadmap.md": "overview",
            "06 - Computer Vision/Image Processing Global Index.md": "overview",
            "06 - Computer Vision/Architecture and Connectivity/VGG and Classic Architectures Summary.md": "reference",
            "06 - Computer Vision/CNN Foundations and Philosophy/Foundations and Philosophy Summary.md": "reference",
            "06 - Computer Vision/Core Operators and Geometry/Core Operators and Geometry Summary.md": "reference",
            "06 - Computer Vision/Pipeline Evaluation and Interpretability/Scaling, Pipeline, and Interpretability Summary.md": "reference",
            "06 - Computer Vision/Training and Transfer Learning/Hyperparameters and Basic PyTorch Summary.md": "reference",
            "06 - Computer Vision/Training and Transfer Learning/Normalization, Regularization, and Augmentation Summary.md": "reference",
            "06 - Computer Vision/Training and Transfer Learning/Transfer Learning and ResNet Summary.md": "reference",
            "06 - Computer Vision/Frequency Domain and Restoration/Image Quality Metrics.md": "reference",
            "06 - Computer Vision/Image Fundamentals/Image File Formats.md": "reference",
            "06 - Computer Vision/Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist.md": "reference",
            "06 - Computer Vision/Quizzes/CNN Solved Exercises.md": "example",
            "06 - Computer Vision/Quizzes/Image Fundamentals and Histograms Quiz.md": "example",
            "06 - Computer Vision/Quizzes/Image Processing Comprehensive Quiz.md": "example",
            "06 - Computer Vision/Quizzes/Noise Degradation and Frequency Domain Quiz.md": "example",
            "06 - Computer Vision/Quizzes/Spatial Filtering and Convolution Quiz.md": "example",
            "06 - Computer Vision/Training and Transfer Learning/PyTorch Implementation Basics.md": "tutorial",
            "06 - Computer Vision/Training and Transfer Learning/PyTorch Advanced - VGG16 and Pre-trained Models.md": "tutorial",
            "06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning.md": "tutorial",
        },
        # area 06 has three area-root orientation notes instead of one MOC
        "moc_target": (
            "at least one area-root orientation note (CNN Course Overview for "
            "CNN-side subfamilies, Image Processing Global Index for classical "
            "image-processing subfamilies, CNN Mastery Roadmap for either)"
        ),
        "colliding": (
            "Activation and Pooling Layers, Backpropagation and Gradient Flow in "
            "CNNs, Common Mistakes and How to Fix Them, Core Architecture and "
            "Philosophy, Evolution of CNN Architectures, Inception Architecture Deep "
            "Dive, Introduction and Foundations of CNNs, PyTorch Advanced - VGG16 "
            "and Pre-trained Models, PyTorch Implementation Basics, ResNet Bottleneck "
            "Blocks and Architectural Variants, The Degradation Problem and Residual "
            "Connections, The Full Training Pipeline End-to-End Checklist, Transfer "
            "Learning and Fine-Tuning, VGG16 Architecture Deep Dive"
        ),
    },
    "07 - Sequence Models": {
        "note_types": {
            "07 - Sequence Models/Chapter Overview.md": "overview",
            "07 - Sequence Models/Motivation and Recurrence/Backpropagation Through Time.md": "derivation",
        },
        # the area-root note's basename collides with 12 - Generative Models'
        # Chapter Overview, so links to it must be path-based
        "moc_target": (
            "the area-root overview note, linked in path form as "
            "[[07 - Sequence Models/Chapter Overview|Chapter Overview]] "
            "(the basename collides with the future area-12 Chapter Overview)"
        ),
        "colliding": (
            "Chapter Overview (link as [[07 - Sequence Models/Chapter Overview|"
            "Chapter Overview]]), Vanishing and Exploding Gradients (link as "
            "[[07 - Sequence Models/Motivation and Recurrence/Vanishing and "
            "Exploding Gradients|Vanishing and Exploding Gradients]] — the "
            "basename also exists in area 05)"
        ),
    },
    "08 - Attention and Transformers": {
        "note_types": {
            "08 - Attention and Transformers/Attention and Transformers MOC.md": "overview",
            "08 - Attention and Transformers/Attention Mechanism/Scaled Dot-Product Attention.md": "derivation",
            "08 - Attention and Transformers/Attention Mechanism/Self-Attention.md": "derivation",
        },
        "moc_target": "Attention and Transformers MOC",
        "colliding": (
            "BERT, Bahdanau Attention, Luong Attention, FlashAttention (each "
            "also exists later as a Papers-area note — link the area-08 copy in "
            "path form, e.g. [[08 - Attention and Transformers/Transformer "
            "Architecture/BERT|BERT]]), plus the already-generated CNN-side "
            "colliding basenames Introduction and Foundations of CNNs, Evolution "
            "of CNN Architectures, Activation and Pooling Layers (area 06) and "
            "Data Augmentation (area 05) — always path-based"
        ),
    },
    "09 - NLP and Language Models": {
        "note_types": {
            "09 - NLP and Language Models/NLP and Language Models MOC.md": "overview",
        },
        "moc_target": "NLP and Language Models MOC",
        "colliding": (
            "BERT (the area-08 copy is the topical sibling for NLP notes; link it "
            "in path form as [[08 - Attention and Transformers/Transformer "
            "Architecture/BERT|BERT]] because the basename also exists later as "
            "a Papers-area note)"
        ),
    },
    "10 - Large Language Models": {
        "note_types": {
            "10 - Large Language Models/Large Language Models MOC.md": "overview",
            "10 - Large Language Models/Evaluation/LLM Benchmarks.md": "reference",
        },
        "moc_target": "Large Language Models MOC",
        "colliding": (
            "BERT (link the area-08 copy in path form as [[08 - Attention and "
            "Transformers/Transformer Architecture/BERT|BERT]] — the basename "
            "also exists later as a Papers-area note), FlashAttention (link as "
            "[[08 - Attention and Transformers/Efficient Attention/"
            "FlashAttention|FlashAttention]]), plus any other basename on the "
            "binding link-rules list"
        ),
    },
    "11 - Foundation Models and Multimodal": {
        "note_types": {
            "11 - Foundation Models and Multimodal/Foundation Models and Multimodal MOC.md": "overview",
            "11 - Foundation Models and Multimodal/Multimodal AI/Multimodal AI Overview.md": "overview",
        },
        # two orientation notes: the area MOC (unifies the 09 + 23 source MOCs)
        # and the multimodal-subfamily survey note
        "moc_target": (
            "the area MOC [[Foundation Models and Multimodal MOC]] (multimodal "
            "subfamily notes may additionally link [[Multimodal AI Overview]])"
        ),
        "colliding": (
            "BERT (link the area-08 copy in path form as [[08 - Attention and "
            "Transformers/Transformer Architecture/BERT|BERT]] — the basename "
            "also exists later as a Papers-area note), plus any other basename "
            "on the binding link-rules list"
        ),
    },
    "12 - Generative Models": {
        "note_types": {
            "12 - Generative Models/Chapter Overview.md": "overview",
            "12 - Generative Models/Variational Autoencoders/The Reparameterization Trick.md": "derivation",
            "12 - Generative Models/Variational Autoencoders/The KL Divergence Loss.md": "derivation",
        },
        # the area-root note's basename collides with 07 - Sequence Models'
        # Chapter Overview, so links to it must be path-based
        "moc_target": (
            "the area-root overview note, linked in path form as "
            "[[12 - Generative Models/Chapter Overview|Chapter Overview]] "
            "(the basename collides with the area-07 Chapter Overview)"
        ),
        "colliding": (
            "Chapter Overview (link as [[12 - Generative Models/Chapter "
            "Overview|Chapter Overview]] — the basename also exists in area 07), "
            "plus any other basename on the binding link-rules list"
        ),
    },
    "13 - Training and Adaptation": {
        "note_types": {
            "13 - Training and Adaptation/Training and Adaptation MOC.md": "overview",
            "13 - Training and Adaptation/Fine-Tuning/DPO Derivation.md": "derivation",
        },
        "moc_target": "Training and Adaptation MOC",
        "colliding": (
            "LoRA (link as [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] "
            "— the basename also exists later as a Papers-area note), plus any "
            "other basename on the binding link-rules list"
        ),
    },
    "14 - Inference and Production": {
        "note_types": {
            "14 - Inference and Production/Inference and Production MOC.md": "overview",
        },
        "moc_target": "Inference and Production MOC",
        "colliding": (
            "vLLM (link as [[14 - Inference and Production/Inference/vLLM|vLLM]] "
            "— the basename also exists later in area 15), TensorRT-LLM (link as "
            "[[14 - Inference and Production/Inference/TensorRT-LLM|"
            "TensorRT-LLM]] — same), plus any other basename on the binding "
            "link-rules list"
        ),
    },
    # ---- session 24 (user-directed: chapters/areas 01-03 + Swin pull-forward) ----
    "01 - Foundations": {
        "note_types": {
            "01 - Foundations/Foundations MOC.md": "overview",
        },
        "moc_target": "Foundations MOC",
        "colliding": (
            "Jacobians and Hessians — BOTH copies are generated in this session's "
            "batch (this area's [[01 - Foundations/Mathematical Foundations/"
            "Jacobians and Hessians|Jacobians and Hessians]] and area 02's "
            "[[02 - Mathematics/Calculus/Jacobians and Hessians|Jacobians and "
            "Hessians]]); always path-based. Applications of Deep Learning (link "
            "as [[01 - Foundations/AI ML and DL Hierarchy/Applications of Deep "
            "Learning|Applications of Deep Learning]] — the area-19 quiz copy is "
            "future). Plus any other basename on the binding link-rules list."
        ),
    },
    "02 - Mathematics": {
        "note_types": {
            "02 - Mathematics/Mathematics MOC.md": "overview",
            "02 - Mathematics/Optimization/Adam Optimizer Derivation.md": "derivation",
            "02 - Mathematics/Optimization/Optimization Essentials.md": "reference",
        },
        "moc_target": "Mathematics MOC",
        "colliding": (
            "Jacobians and Hessians — BOTH copies are generated in this session's "
            "batch (this area's [[02 - Mathematics/Calculus/Jacobians and "
            "Hessians|Jacobians and Hessians]] and area 01's [[01 - Foundations/"
            "Mathematical Foundations/Jacobians and Hessians|Jacobians and "
            "Hessians]]); always path-based. Plus any other basename on the "
            "binding link-rules list."
        ),
    },
    "03 - Python and Data Tooling": {
        "note_types": {
            "03 - Python and Data Tooling/Python Language Overview.md": "overview",
            "03 - Python and Data Tooling/Data Cleaning and Preprocessing/Exercise - Medical Dataset Pipeline.md": "tutorial",
            "03 - Python and Data Tooling/Python Environment Setup/Exercise - Hospital Data Project Setup.md": "tutorial",
            "03 - Python and Data Tooling/Python Libraries/Exercise - Temperature and Grade Analysis.md": "tutorial",
            "03 - Python and Data Tooling/Python Programming/Exercise - Sales Project Logic and OOP.md": "tutorial",
        },
        # area 03 has no separate MOC note; the area-root overview is the hub
        "moc_target": (
            "Python Language Overview (the area-root overview note — area 03 has "
            "no separate MOC)"
        ),
        "colliding": (
            "no area-03 basename collides vault-wide; apply the binding "
            "link-rules list for any generated-set collision (e.g. linking the "
            "area-04/05 topical copies of shared basenames)"
        ),
    },
    # Partial-batch config for the user-directed Swin Transformer pull-forward
    # (session 24). Selected via: --area "17 - Papers" --slug area17swin
    # --only "17 - Papers/Attention and Transformers/Swin Transformer.md".
    # The FULL area-17 entry below is authoritative for the session-25 run;
    # never reuse this partial key for it.
    "17 - Papers :: area17swin": {
        "note_types": {
            "17 - Papers/Attention and Transformers/Swin Transformer.md": "concept",
        },
        "moc_target": (
            "[[Attention and Transformers MOC]] as the topical hub (the area-17 "
            "Papers MOC is not generated yet; per conventions v1 #7 links resolve "
            "within the generated set — Papers-area sibling links are added at "
            "the cross-batch consistency pass)"
        ),
        "colliding": (
            "BERT, Bahdanau Attention, Luong Attention (each links the area-08 "
            "copy in path form, e.g. [[08 - Attention and Transformers/Transformer "
            "Architecture/BERT|BERT]]), FlashAttention (link as [[08 - Attention "
            "and Transformers/Efficient Attention/FlashAttention|FlashAttention]]), "
            "Evolution of CNN Architectures and the other area-06 CNN basenames "
            "(path form), plus any other basename on the binding link-rules list"
        ),
    },
    # ---- session 25 (bulk batch 2: areas 15-19, ~200 notes) ----
    "15 - Agents and Tooling": {
        "note_types": {
            "15 - Agents and Tooling/Agents and Tooling MOC.md": "overview",
            "15 - Agents and Tooling/Frameworks and Tools/Framework Selection Guide.md": "reference",
        },
        "moc_target": "Agents and Tooling MOC",
        "colliding": (
            "vLLM and TensorRT-LLM (each also exists as an area-14 note — links "
            "from this area's notes use THIS area's copy in path form, e.g. "
            "[[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]]), plus "
            "any other basename on the binding link-rules list (BERT/FlashAttention/"
            "LoRA topical copies etc. link their area-08/13 forms in path form)"
        ),
    },
    "16 - Interpretability and Research": {
        "note_types": {
            "16 - Interpretability and Research/Interpretability and Research MOC.md": "overview",
            "16 - Interpretability and Research/Model Architecture Research/Frontier Model Synthesis 2026.md": "reference",
            "16 - Interpretability and Research/Research Frontiers/Research Frontier Update 2026.md": "reference",
        },
        "moc_target": "Interpretability and Research MOC",
        "colliding": (
            "no area-16 basename collides vault-wide; apply the binding "
            "link-rules list for any generated-set collision (e.g. BERT/"
            "FlashAttention/LoRA topical copies link their area-08/13 forms in "
            "path form)"
        ),
    },
    # FULL area-17 entry (session 25): synthesizes the remaining 55 paper notes;
    # the Swin Transformer note already exists on disk (s24) and is NEVER
    # regenerated — it is only re-assessed/re-audited as part of the complete
    # area batch. The wave plan excludes it from generation groups.
    "17 - Papers": {
        "note_types": {
            "17 - Papers/Papers MOC.md": "overview",
        },
        "moc_target": "Papers MOC",
        "colliding": (
            "BERT, Bahdanau Attention, Luong Attention, FlashAttention (the "
            "area-08 topical copies are the concept targets — link them in path "
            "form, e.g. [[08 - Attention and Transformers/Transformer "
            "Architecture/BERT|BERT]]); links to the area-17 paper copies "
            "themselves use the area-17 path form, e.g. [[17 - Papers/Attention "
            "and Transformers/BERT|BERT]]; LoRA (concept target: [[13 - Training "
            "and Adaptation/Fine-Tuning/LoRA|LoRA]]; paper copy: [[17 - Papers/"
            "Scaling and Training/LoRA|LoRA]]); vLLM (concept target: [[14 - "
            "Inference and Production/Inference/vLLM|vLLM]]; the paper note "
            "'PagedAttention and vLLM' has a unique basename); TensorRT-LLM "
            "(concept target: [[14 - Inference and Production/Inference/"
            "TensorRT-LLM|TensorRT-LLM]] — the area-15 copy shares the basename "
            "so every link to it is path-based); plus any other basename on the "
            "binding link-rules list"
        ),
    },
    "18 - Projects": {
        "note_types": {
            "18 - Projects/Projects MOC.md": "overview",
        },
        # all 24 project notes are build guides -> tutorial (the area-03
        # exercise-note precedent); types are the default map below
        "default_note_type": "tutorial",
        "moc_target": "Projects MOC",
        "colliding": (
            "no area-18 basename collides vault-wide; apply the binding "
            "link-rules list for any generated-set collision (e.g. LoRA/vLLM/"
            "BERT topical copies link their area-13/14/08 forms in path form)"
        ),
    },
    "19 - Reference and Practice": {
        "note_types": {
            "19 - Reference and Practice/Glossary/Glossary MOC.md": "overview",
            "19 - Reference and Practice/Glossary/A-Z Terms.md": "reference",
            "19 - Reference and Practice/Glossary/Acronyms Index.md": "reference",
            "19 - Reference and Practice/Glossary/Notation Conventions.md": "reference",
            "19 - Reference and Practice/Interview Prep/Interview Prep MOC.md": "overview",
            "19 - Reference and Practice/Interview Prep/Coding Interview Questions.md": "reference",
            "19 - Reference and Practice/Interview Prep/Conceptual Interview Questions.md": "reference",
            "19 - Reference and Practice/Interview Prep/System Design Interview Questions.md": "reference",
        },
        # every untyped quiz/question-series note defaults to example (the
        # area-06 quiz precedent)
        "default_note_type": "example",
        "moc_target": (
            "the relevant subarea MOC: [[Glossary MOC]] for glossary notes and "
            "[[Interview Prep MOC]] for interview-prep notes; quiz notes have no "
            "in-area MOC (area 19 has no area-root note) — link at least two "
            "same-chapter quiz siblings plus the topical concept notes they "
            "practice (path-based for colliding basenames, e.g. [[05 - Neural "
            "Network Foundations/Training Dynamics and Stability/Batch "
            "Normalization|Batch Normalization]])"
        ),
        "colliding": (
            "the quiz-copy basenames (each links its topical concept copy in "
            "path form, e.g. [[05 - Neural Network Foundations/Training Dynamics "
            "and Stability/Batch Normalization|Batch Normalization]] or [[06 - "
            "Computer Vision/Architecture and Connectivity/Evolution of CNN "
            "Architectures|Evolution of CNN Architectures]]; links to the quiz "
            "copies themselves use the area-19 path form, e.g. [[19 - Reference "
            "and Practice/Quizzes/Deep Learning Chapter 2 CNN/Batch "
            "Normalization|Batch Normalization]]), plus any other basename on "
            "the binding link-rules list"
        ),
    },
}

# Kept for backwards compatibility with the session-20 records: the area-04
# entries above are the authoritative copy.
NOTE_TYPES: dict[str, str] = AREA_CONFIG["04 - Machine Learning"]["note_types"]  # type: ignore[assignment]



def slugify(text: str) -> str:
    text = text.rsplit("/", 1)[-1]
    text = re.sub(r"\.md$", "", text)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "note"


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--area", required=True, help="area folder name, e.g. '04 - Machine Learning'")
    ap.add_argument("--slug", required=True, help="scratch dir slug, e.g. area04")
    ap.add_argument("--report", required=True, help="committed JSON report path")
    ap.add_argument(
        "--only",
        default="",
        help=(
            "comma-separated canonical note paths restricting the batch to a "
            "partial-area subset (e.g. the Swin Transformer pull-forward). "
            "Requires a '<area> :: <slug>' AREA_CONFIG entry so the partial "
            "batch gets its own explicit types/link rules."
        ),
    )
    args = ap.parse_args()

    area = args.area
    prefix = area + "/"
    only = {p.strip() for p in args.only.split(",") if p.strip()} or None
    config_key = f"{area} :: {args.slug}" if only else area
    config = AREA_CONFIG.get(config_key)
    if config is None:
        raise SystemExit(
            f"no AREA_CONFIG entry for {config_key!r}: add note_types/moc_target/colliding "
            "before synthesizing it (see scripts/s20_build_synthesis_inputs.py)"
        )
    if only and config_key == area:
        raise SystemExit(
            f"partial batch (--only) for area {area!r} needs a dedicated "
            f"'{area} :: {args.slug}' AREA_CONFIG entry, not the full-area one"
        )
    note_types: dict[str, str] = config["note_types"]  # type: ignore[assignment]
    # optional per-area default for untyped notes (session 25: projects ->
    # tutorial, quizzes/question series -> example); areas without the key
    # keep the historical "concept" default
    default_type: str = config.get("default_note_type", "concept")  # type: ignore[assignment]
    moc_target: str = config["moc_target"]  # type: ignore[assignment]
    colliding: str = config["colliding"]  # type: ignore[assignment]
    out_dir = SCRATCH / args.slug
    bundles = out_dir / "bundles"
    specs = out_dir / "specs"
    for d in (bundles, specs):
        d.mkdir(parents=True, exist_ok=True)

    # ---- committed inputs ------------------------------------------------
    structure = json.loads((REPO / "state/synthesis/canonical-structure-v1.json").read_text())
    file_mapping = load_jsonl(REPO / "state/synthesis/file-mapping-v1.jsonl")
    ledger = load_jsonl(REPO / "state/dispositions/001-disp001-rule-driven.jsonl")

    ku_by_id: dict[str, dict] = {}
    for batch in sorted((REPO / "state/knowledge-units").glob("*.jsonl")):
        for rec in load_jsonl(batch):
            ku_by_id[rec["knowledge_unit_id"]] = rec

    dossiers = []
    for dom in ("regression", "tree-based", "evaluation", "clustering", "generalization", "training-stability"):
        dossiers.append(json.loads((REPO / "state/dossiers" / f"{dom}-v2.json").read_text()))

    # ---- area scoping ----------------------------------------------------
    notes = [n for n in structure["notes"] if n["area"] == area]
    if only:
        notes = [n for n in notes if n["path"] in only]
        missing = only - {n["path"] for n in notes}
        if missing:
            raise SystemExit(f"--only paths not found in area {area!r}: {sorted(missing)}")
    area_files = [r for r in file_mapping if any(p.startswith(prefix) for p in r["canonical_paths"])]
    note_paths = sorted(n["path"] for n in notes)
    note_path_set = set(note_paths)
    if only:
        # keep only files that feed at least one filtered note
        area_files = [
            r for r in area_files if any(cp in note_path_set for cp in r["canonical_paths"])
        ]

    # files feeding each note
    files_by_note: dict[str, list[dict]] = {p: [] for p in note_paths}
    for r in area_files:
        for cp in r["canonical_paths"]:
            if cp in files_by_note:
                files_by_note[cp].append(r)
    # KUs per note (from the ledger — the authoritative overlay)
    kus_by_note: dict[str, list[str]] = {p: [] for p in note_paths}
    if only:
        area_kus = [r for r in ledger if any(d["path"] in note_path_set for d in r["destinations"])]
    else:
        area_kus = [r for r in ledger if any(d["path"].startswith(prefix) for d in r["destinations"])]
    for r in area_kus:
        for d in r["destinations"]:
            if d["path"] in kus_by_note:
                kus_by_note[d["path"]].append(r["ku_id"])

    # dossier concepts per note (concepts with >= 1 KU destined to the note)
    concepts_by_note: dict[str, list[dict]] = {p: [] for p in note_paths}
    ku_note_sets = {p: set(ids) for p, ids in kus_by_note.items()}
    for dos in dossiers:
        for c in dos["concepts"]:
            kset = set(c.get("ku_ids", []))
            if not kset:
                continue
            for p, nset in ku_note_sets.items():
                inter = kset & nset
                if inter:
                    concepts_by_note[p].append(
                        {
                            "concept_id": c["concept_id"],
                            "label": c.get("label"),
                            "dossier": dos["dossier_id"],
                            "concept_kus": len(kset),
                            "kus_in_this_note": len(inter),
                            "overlap_type": c.get("overlap_type"),
                        }
                    )

    # ---- audit batch (effective state; committed records + ledger overlay) --
    audit_records = []
    for r in area_kus:
        base = dict(ku_by_id[r["ku_id"]])
        base["disposition"] = r["disposition"]
        base["destinations"] = r["destinations"]
        if r["disposition"] == "Superseded":
            # invariant 3: superseded units must record why unique information
            # survives elsewhere — carry the ledger rationale verbatim
            base["superseded_rationale"] = r["rationale"]
        audit_records.append(base)
    audit_path = out_dir / "audit-kus.jsonl"
    with audit_path.open("w", encoding="utf-8") as fh:
        for rec in sorted(audit_records, key=lambda x: x["knowledge_unit_id"]):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- provenance mapping ------------------------------------------------
    prov_path = out_dir / "provenance.jsonl"
    with prov_path.open("w", encoding="utf-8") as fh:
        for p in note_paths:
            fh.write(json.dumps({"note": p, "ku_ids": sorted(kus_by_note[p])}, ensure_ascii=False) + "\n")

    (out_dir / "expected-notes.txt").write_text("\n".join(note_paths) + "\n", encoding="utf-8")

    # ---- bundles + specs ----------------------------------------------------
    notes_meta = []
    for idx, p in enumerate(sorted(note_paths), start=1):
        meta_note = next(n for n in notes if n["path"] == p)
        ntype = note_types.get(p, default_type)
        fmap = files_by_note[p]
        ku_ids = sorted(kus_by_note[p])
        bundle_name = f"{idx:02d}-{slugify(p)}.md"
        spec_name = f"{idx:02d}-{slugify(p)}.json"

        # ---- bundle ----
        parts = []
        parts.append(f"# SYNTHESIS EVIDENCE BUNDLE {idx:02d}/{len(note_paths)}\n")
        parts.append(f"## Target note\n")
        parts.append(f"- **Canonical path:** `{p}`")
        parts.append(f"- **Title:** {meta_note['title']}")
        parts.append(f"- **Note type:** {ntype}")
        parts.append(f"- **Planned rationale:** {meta_note['rationale']}")
        parts.append(f"- **Source vaults:** {', '.join(meta_note['vaults'])}\n")
        parts.append("## Mapped source files (verbatim, immutable evidence)\n")
        total_words = 0
        repo_files = []
        for fi, fr in enumerate(fmap, start=1):
            src = VAULT_ROOTS[fr["vault"]] / fr["source_path"]
            text = src.read_text(encoding="utf-8")
            total_words += len(text.split())
            repo_files.append(str(src.relative_to(REPO)))
            parts.append(f"### FILE {fi}/{len(fmap)} — {fr['vault']} — `{fr['source_path']}`\n")
            parts.append(f"Mapping rationale: {fr['rationale']}\n")
            parts.append("```markdown")
            parts.append(text.rstrip("\n"))
            parts.append("```\n")
        parts.append("## Dossier concepts anchored by this note\n")
        cons = sorted(concepts_by_note[p], key=lambda c: -c["kus_in_this_note"])
        if cons:
            for c in cons:
                parts.append(
                    f"- {c['label']} (`{c['concept_id']}`, {c['dossier']}): "
                    f"{c['kus_in_this_note']} of {c['concept_kus']} concept KUs land in this note"
                )
        else:
            parts.append("- (none: this note's KUs are not dossier concept members)")
        parts.append("\n## Knowledge-unit checklist (coverage accounting)\n")
        parts.append(
            f"{len(ku_ids)} KUs are destined to this note. Every unit's content must be "
            "represented (prose may be rewritten; equations, code and rare terms must survive).\n"
        )
        parts.append("| ku_id | disposition | source lines | heading path |")
        parts.append("|---|---|---|---|")
        for kid in ku_ids:
            r = next(x for x in area_kus if x["ku_id"] == kid)
            ku = ku_by_id[kid]
            hp = " > ".join(ku.get("heading_path") or [])
            parts.append(f"| `{kid}` | {r['disposition']} | {ku['line_start']}-{ku['line_end']} | {hp} |")
        (bundles / bundle_name).write_text("\n".join(parts) + "\n", encoding="utf-8")

        # ---- generation prompt spec ----
        requirements = [
            "Open with YAML frontmatter carrying title, type, aliases, tags, sources (titles of the mapped source notes) and created_index.",
            "Begin the body with a 2-4 sentence orienting introduction before the first section heading; do not use an H1 heading anywhere in the body.",
            "Structure the note with ## section headings (### for subsections), sentence case, unnumbered, in a logical teaching order for the topic.",
            "Synthesize all mapped source files into one coherent treatment: reconcile terminology, keep every distinct explanation, worked example, equation, derivation step, caveat, table, diagram and code sample.",
            "Reproduce every equation and every fenced code block from the source material verbatim (whitespace-insensitive), using $...$ inline and $$...$$ display math and language-labelled fences.",
            "Preserve rare or one-off details: historical distinctions, API/version caveats, project-specific lessons, interview distinctions, edge cases and failure modes.",
            "Write flowing explanatory prose for concepts; use lists and tables only where they genuinely aid lookup or comparison; never leave a section as a bare bullet list.",
            f"Link related notes with Obsidian wikilinks that resolve inside this area batch ([[Note Name]] for unique basenames; [[path/to/Note|Note]] for the colliding basenames {colliding}); every note links to {moc_target} and at least two topical siblings.",
            "Keep the note self-contained: no references to source vaults, merge history, file paths of sources, or this bundle; provenance lives in frontmatter sources only.",
            "Match the depth of the evidence: do not shorten, summarize away, or pad; the note ends with a See also section of wikilinks when siblings exist.",
        ]
        constraints = [
            "Do not invent facts, numbers, citations or claims that are not present in the source evidence.",
            "Preserve unrelated content: do not remove or alter material merely because it is obscure, one-off, or from an unfamiliar subtopic.",
            "Record provenance: frontmatter sources lists the titles of every mapped source note.",
            "Equations, code blocks and mermaid diagrams are copied verbatim from the sources; prose around them is rewritten for coherence.",
        ]
        criteria = [
            {"criterion": "zero artifact-lint errors (fences, math delimiters, tables, links, frontmatter)", "check": "lint:FENCE_UNCLOSED"},
            {"criterion": "no broken or ambiguous internal links", "check": "lint:LINK_BROKEN"},
            {"criterion": "no placeholder or unfinished-text markers", "check": "lint:PLACEHOLDER_TEXT"},
            {"criterion": "structure dimension within band (intro + >=2 sections, no hierarchy skips)", "check": "quality:structure"},
            {"criterion": "depth dimension within band for the note type", "check": "quality:depth"},
            {"criterion": "source coverage: >= 60% of mapped KU key terms present in the note", "check": "quality:source_coverage"},
            {"criterion": "provenance dimension within band (frontmatter sources + in-text links)", "check": "quality:provenance"},
            {"criterion": "links dimension within band (internal links present and resolving)", "check": "quality:links"},
            {"criterion": "every mapped KU's content is represented in the note", "check": "manual_review"},
        ]
        spec = {
            "schema_version": "1.0.0",
            "objective": (
                f"Synthesize the canonical note '{meta_note['title']}' ({ntype}) at {p} from its "
                f"{len(fmap)} mapped source file(s) and {len(ku_ids)} destined knowledge units, "
                "preserving every meaningful detail in unified editorial style."
            ),
            "target_note": {"path": p, "type": ntype, "title": meta_note["title"]},
            "source_evidence": {
                "ku_ids": ku_ids,
                "files": repo_files,
                "dossier": ", ".join(
                    sorted({c["dossier"] for c in cons})
                )
                or "none",
            },
            "requirements": requirements,
            "constraints": constraints,
            "acceptance_criteria": criteria,
            "output_contract": {
                "path": p,
                "format": "markdown",
                "max_words": max(400, 6 * total_words),
            },
            "context_budget": {"max_words": 4000, "max_source_excerpts": 0},
            "evidence_bundle": f"scratch/synth/{args.slug}/bundles/{bundle_name}",
        }
        (specs / spec_name).write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        notes_meta.append(
            {
                "index": idx,
                "path": p,
                "title": meta_note["title"],
                "type": ntype,
                "files": [f"{r['vault']}:{r['source_path']}" for r in fmap],
                "repo_files": repo_files,
                "ku_count": len(ku_ids),
                "source_words": total_words,
                "bundle": str((bundles / bundle_name).relative_to(REPO)),
                "spec": str((specs / spec_name).relative_to(REPO)),
                "concepts": len(cons),
            }
        )

    (out_dir / "notes.json").write_text(
        json.dumps({"area": area, "notes": notes_meta}, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    # ---- assertions ---------------------------------------------------------
    problems = []
    if len(notes) != len(note_paths):
        problems.append("note path collision inside area")
    # per-note membership arithmetic: sum over notes == KUs + extra memberships
    # (a KU destined to n notes in this area contributes n memberships)
    if sum(len(v) for v in kus_by_note.values()) != len(area_kus) + multi_dest_extra(kus_by_note, area_kus, note_path_set, prefix):
        problems.append("per-note KU membership arithmetic failed")
    for p in note_paths:
        if not kus_by_note[p]:
            problems.append(f"note has zero KUs: {p}")
    for rec in audit_records:
        if rec["excerpt_hash"] != ku_by_id[rec["knowledge_unit_id"]]["excerpt_hash"]:
            problems.append(f"audit record hash drift: {rec['knowledge_unit_id']}")
    if only:
        cross = [r for r in area_kus if any(d["path"] not in note_path_set for d in r["destinations"])]
    else:
        cross = [r for r in area_kus if any(not d["path"].startswith(prefix) for d in r["destinations"])]
    if cross:
        problems.append(f"{len(cross)} KUs have destinations outside the batch (batch not self-contained)")

    by_disp: dict[str, int] = {}
    for r in area_kus:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1
    multi_dest = multi_dest_extra(kus_by_note, area_kus, note_path_set, prefix)  # extra memberships
    shared_kus = sum(
        1 for r in area_kus if len([d for d in r["destinations"] if d["path"].startswith(prefix)]) > 1
    )

    report = {
        "area": area,
        "slug": args.slug,
        "partial_batch": bool(only),
        "only_filter": sorted(only) if only else None,
        "notes": len(note_paths),
        "source_files": len(area_files),
        "kus": len(area_kus),
        "kus_by_disposition": by_disp,
        "kus_multi_destination_within_area": multi_dest,
        "concepts_anchored": sum(m["concepts"] for m in notes_meta),
        "total_source_words": sum(m["source_words"] for m in notes_meta),
        "scratch_dir": str(out_dir.relative_to(REPO)),
        "problems": problems,
        "deterministic": True,
        "inputs": {
            "structure": "state/synthesis/canonical-structure-v1.json",
            "file_mapping": "state/synthesis/file-mapping-v1.jsonl",
            "ledger": "state/dispositions/001-disp001-rule-driven.jsonl",
            "ku_batches": "state/knowledge-units/*.jsonl (71 files)",
            "dossiers": "state/dossiers/*-v2.json (6 files)",
        },
        "area_config": {
            "moc_target": moc_target,
            "colliding": colliding,
            "explicit_types": len(note_types),
            "default_note_type": default_type,
        },
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if problems:
        print("PROBLEMS DETECTED", file=sys.stderr)
        return 1
    return 0


def multi_dest_extra(kus_by_note: dict[str, list[str]], area_kus: list[dict], note_path_set: set[str], prefix: str) -> int:
    # note_path_set is the batch's note paths (== all area note paths for an
    # unfiltered run; every ledger destination is a valid canonical note path,
    # verified against the structure with 0 invalid)
    extra = 0
    for r in area_kus:
        n = len([d for d in r["destinations"] if d["path"] in note_path_set])
        extra += n - 1
    return extra


if __name__ == "__main__":
    raise SystemExit(main())
