#!/usr/bin/env python3
"""EXT-010: build the training-stability domain term map from ACTUAL batch
content.

Scope: batch 010 (master-ai '04 - Neural Networks/Training' files 07
Initialization Schemes + 08 Vanishing and Exploding Gradients, 2 files, 117
KUs) + batch 011 (ai-course '04.3 - Training Dynamics and Stability' files
01 Weight Initialization + 02 Weight Initialization Techniques + 03 The
Vanishing and Exploding Gradient Problems, 3 files, 382 KUs). 499 KUs total.

Guarantees enforced before writing state/term-maps/training-stability-domain-v1.json:
- every canonical term AND every alias actually occurs (case-insensitive,
  word-boundary) inside at least one KU excerpt in scope — no invented
  vocabulary (four probe rounds ran first: scripts/ext010_term_probe{,2,3,4}.py);
- per-term vault coverage is reported (cross-vault / single-vault preview);
- the map matches the CAP-013 terms format {term: [aliases]}; _-prefixed
  keys are documentation and ignored by the loader.

Writes reports/extraction/ext010-term-map-verification.json. Exits non-zero
on any unverified term/alias. Read-only with respect to source vaults.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_010 = REPO_ROOT / "state" / "knowledge-units" / "010-ext010-master-ai-training-stability.jsonl"
BATCH_011 = REPO_ROOT / "state" / "knowledge-units" / "011-ext010-ai-course-04.3-init-gradients.jsonl"
OUT = REPO_ROOT / "state" / "term-maps" / "training-stability-domain-v1.json"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext010-term-map-verification.json"

TERM_MAP: dict[str, list[str]] = {
    # --- initialization core ---
    "initialization": ["initialize", "initialized"],  # cross-vault
    "weight initialization": [],  # ai-course-only surface form; cross-vault pairing happens via Xavier/Kaiming/initialization keys
    "initialization schemes": [],  # cross-vault (master-ai file-title concept also appears in course text)
    "Xavier": ["Glorot", "Xavier initialization", "Glorot initialization", "Xavier uniform", "Xavier normal", "xavier_uniform_", "xavier_normal_"],
    "He initialization": ["Kaiming", "Kaiming initialization", "Kaiming uniform", "Kaiming normal", "kaiming_uniform_", "kaiming_normal_"],
    "fan_in": ["fan_out", "fan-in", "fan-out"],  # cross-vault; notation family for layer widths
    "symmetry problem": ["symmetric", "symmetry"],  # canonical course-only; aliases cross-vault (BRIDGE)
    "zero initialization": ["zero init", "zeros", "ones"],  # course canonical + master 'zero init' BRIDGE
    "normal distribution": ["Gaussian", "N(0, 1)", "N(0, 0.01)", "standard deviation", "std"],  # course canonical + master Gaussian BRIDGE
    "uniform": [],
    "orthogonal": [],  # ai-course-only
    "sparse": ["sparsity"],  # ai-course-only
    "goldilocks": [],  # ai-course-only
    "bias": [],  # cross-vault; sense: bias parameter init (NOT statistical bias)
    "variance": ["sigma_w"],  # cross-vault; sigma_w = master-ai init-scale notation also verified cross-vault
    "gain": [],  # ai-course-only (Xavier gain parameter)
    "derivation": ["derive"],  # course 'derivation' + master 'derive' BRIDGE
    "variance tracking": [],  # ai-course-only
    "default initialization": ["defaults", "default"],  # course canonical + cross-vault 'defaults'/'default'
    "nonlinearity": ["non-linear"],  # cross-vault + course alias
    # --- activation functions (vanishing-gradient context) ---
    "ReLU": ["rectified linear"],  # cross-vault
    "sigmoid": [],  # cross-vault
    "tanh": [],  # cross-vault
    "leaky": ["Leaky ReLU"],  # cross-vault
    "PReLU": ["parametric ReLU"],  # ai-course-only
    "ELU": [],  # ai-course-only
    "dying ReLU": ["dead neurons", "dead"],  # course canonical + master 'dead neurons' BRIDGE (same concept, different surface form)
    "saturation": ["saturates", "saturated"],  # cross-vault
    # --- PyTorch mechanics ---
    "PyTorch": ["torch", "torch.nn", "nn.init", "nn.Linear", "nn.Conv2d"],
    # --- vanishing/exploding core ---
    "vanishing gradient": ["vanishing gradients", "vanishing gradient problem", "vanishing"],
    "exploding gradient": ["exploding gradients", "exploding gradient problem", "exploding", "explosion"],
    "gradient": ["gradients"],
    "Jacobian": ["Jacobians"],
    "backpropagation": ["backprop", "backward pass"],
    "forward pass": ["forward"],
    "chain rule": [],
    "product": ["products", "multiply", "multiplication"],
    "exponential": [],
    "deep network": ["deep networks", "deep neural network", "deep"],
    "layer": ["layers", "early layers", "early layer", "output layer", "last layer", "linear layer", "hidden layer"],
    "neuron": ["neurons"],
    "RNN": ["RNNs", "recurrent"],  # master canonical + cross-vault aliases BRIDGE
    "LSTM": ["GRU"],  # master-ai-only
    "sequence": ["sequential", "long sequences"],  # course canonical + cross-vault aliases BRIDGE
    "NaN": ["inf", "infinity"],
    # --- solutions: residual family ---
    "skip connection": ["skip connections", "residual connection", "residual connections", "residual", "residuals"],  # course canonical + master/cross aliases
    "ResNet": ["residual network", "residual networks", "residual block", "residual blocks"],
    "identity": [],  # cross-vault: identity term/matrix/mapping in residual math
    "plain network": ["plain networks", "plain"],  # cross-vault ResNet-paper vocabulary
    # --- solutions: normalization family ---
    "batch normalization": ["BatchNorm", "batch norm", "BN", "BatchNorm2d", "Ioffe", "Szegedy"],  # course canonical + master 'BatchNorm' BRIDGE
    "LayerNorm": ["Layer Normalization", "layer normalization"],  # master canonical + course aliases BRIDGE
    "RMSNorm": [],  # master-ai-only
    "pre-norm": ["post-norm"],  # master-ai-only
    # --- solutions: gradient clipping family ---
    "gradient clipping": ["clip", "clipped", "clip_grad_norm_", "clip by norm", "clip by value", "clip the gradient", "threshold"],
    "gradient norm": ["gradient norms", "magnitude", "magnitudes", "norm", "norms"],  # sense-collision: see comment (gradient norm vs LayerNorm vs batch norm)
    # --- diagnosis / monitoring ---
    "monitor": ["monitoring"],  # cross-vault + course alias
    "diagnose": ["diagnostic"],  # cross-vault + course alias (the 'Comprehensive Diagnostic Dashboard' heading is heading-only, excluded per EXT-004 rule)
    "learning rate": ["learning rates", "LR"],
    "warmup": [],  # ai-course-only
    # --- loss-landscape / training dynamics ---
    "loss": ["loss curve", "loss plot", "loss landscape"],
    "non-convex": ["local minimum", "local minima", "saddle points"],
    "oscillations": ["oscillates"],  # course-only; the un-inflected 'oscillate' is absent from both batches (probe-verified)
    "diverge": ["divergence", "diverging", "diverges"],
    "converge": ["convergence", "converges"],
    "epoch": ["epochs", "training loop"],
    "gradient flow": [],
    "signal": ["learning signal"],  # ai-course-only
    "spikes": ["loss spikes"],  # cross-vault (instability symptom); 'loss spikes' master-ai-only
    "noise": [],  # cross-vault; metaphorical uses differ — see comment
    "numerical stability": ["numerical instability", "numerical", "overflow", "underflow"],
    "FP16": ["BF16"],  # master-ai-only
    "scale": ["scaling", "scaled"],  # sense-collision: init scale / residual-stream scaling / gradient scale — see comment
    "shrink": ["attenuate", "decay"],  # cross-vault 'shrink'; course 'attenuate'; master 'decay'
    "compound": [],  # ai-course-only (compounding effect)
    "cycle": ["self-reinforcing"],  # ai-course-only; the plural 'cycles' is absent (probe-verified)
    "catastrophic": [],  # ai-course-only
    "zero-centered": [],  # ai-course-only
    "flat": ["plateau", "plateaus"],  # cross-vault 'flat' + course 'plateau' + master 'plateaus'
    # --- architecture / era context ---
    "attention": ["self-attention"],  # master-ai mechanisms; course has a FALSE-FRIEND 'attention' sense — see comment
    "transformer": ["Transformer", "Transformers"],  # cross-vault via plural
    "MLP": [],  # master-ai-only
    "embedding": ["projection"],  # master-ai-only (transformer init recipe)
    "residual stream": [],  # master-ai-only
    "eigenvalue": ["eigenvalues", "spectral"],  # master-ai-only
    "LoRA": [],  # master-ai-only
    "MuP": ["Tensor Programs"],  # master-ai-only
    "Fixup": [],  # master-ai-only
    "GPT": [],  # master-ai-only
    "LLM": [],  # master-ai-only
    "Zhang": [],  # master-ai-only
    # --- citations ---
    "He et al": ["Glorot and Bengio"],  # cross-vault + course alias BRIDGE
    # --- hyperparameter/tuning adjacency ---
    "hyperparameter": ["hyperparameters"],  # course singular + cross-vault plural BRIDGE
    "tuning": ["tune", "tuned"],
    "weight matrix": ["weight matrices"],  # cross-vault + master alias
    "random": ["seed", "constant"],
    "input": ["inputs"],
    "output": ["outputs"],
    "width": ["wide", "wider", "depth", "deep", "shallow", "shallower"],
}

_COMMENT = (
    "Training-stability domain term/alias map for EXT-010 cross-vault "
    "candidate discovery (CAP-013). Canonical term -> aliases. Built from the "
    "actual content of batch 010 (master-ai '04 - Neural Networks/Training' "
    "files 07 Initialization Schemes + 08 Vanishing and Exploding Gradients, "
    "2 files, 117 KUs — a deliberate 2-of-3 partial-folder scope; 06 "
    "Backpropagation is excluded as a distinct autodiff/BPTT domain) and "
    "batch 011 (ai-course '04.3 - Training Dynamics and Stability' files 01 "
    "Weight Initialization + 02 Weight Initialization Techniques + 03 The "
    "Vanishing and Exploding Gradient Problems, 3 files, 382 KUs; three "
    "deterministic single-file runs concatenated in fixed order; file 04 "
    "Hyperparameters remains reserved for a future optimization/tuning pair "
    "per the EXT-009 scope note). Every term and alias is verified to occur "
    "inside at least one in-scope KU excerpt by scripts/ext010_term_map.py "
    "after four probe rounds (scripts/ext010_term_probe{,2,3,4}.py; "
    "reports/extraction/ext010-term-map-verification.json). HEADING-ONLY and "
    "ABSENT vocabulary correctly EXCLUDED (EXT-004 rule; probe-verified "
    "missing from BOTH batches): 'BPTT', 'backpropagation through time', "
    "'weight decay', 'weight tying', 'momentum', 'nesterov', 'gated', "
    "'covariance', 'gradient checking', 'calculate_gain', "
    "'reset_parameters', 'initialise', 'initialisation' (British spellings "
    "absent), 'co-adaptation', 'dropout', 'early stopping', 'regularization', "
    "'data augmentation', 'label smoothing', 'covariate shift', 'Adam', "
    "'AdamW', 'optimizer' (course-only word, excluded as anchor but present), "
    "'dampen', 'die out', 'extinguish', 'wash out', 'embeddings' (plural), "
    "'prenorm'/'postnorm' (hyphenless), 'interview'/'production' "
    "(heading-only in master-ai; headings are not KU-excerpt evidence), "
    "'variance tracking' IS included (course-only, verified). BRIDGE "
    "aliases deliberately connect different surface forms of the same "
    "concept across vaults: 'dying ReLU' (ai-course) with 'dead neurons' "
    "(master-ai); 'LayerNorm' (master-ai) with 'layer normalization' "
    "(ai-course); 'zero initialization' (ai-course) with 'zero init' "
    "(master-ai); 'RNN' (master-ai) with 'RNNs'/'recurrent' (both); "
    "'sequence' (ai-course) with 'sequential'/'long sequences'; "
    "'batch normalization' (ai-course) with 'BatchNorm' (master-ai); "
    "'He et al' (cross-vault) with 'Glorot and Bengio' (ai-course); "
    "'hyperparameter' (ai-course) with 'hyperparameters' (cross-vault); "
    "'derivation' (ai-course) with 'derive' (master-ai); 'diagnostic "
    "dashboard' (ai-course) with the diagnosis family; 'flat' (cross-vault) "
    "with 'plateau' (ai-course) and 'plateaus' (master-ai); 'shrink' "
    "(cross-vault) with 'attenuate' (ai-course) and 'decay' (master-ai). "
    "KNOWN SPURIOUS/SENSE-COLLISION SOURCES, recorded here so "
    "classification dismisses or adjudicates them with evidence: (1) "
    "'attention' — master-ai uses it for the self-attention mechanism "
    "(the Transformer solution to vanishing through recurrence; attention "
    "saturation; QK scaling), while ai-course uses it ONCE as the English "
    "idiom 'careful attention to initialization' (KU-6320fbea895ec3cf) — "
    "the course idiom sense must NEVER count as mechanism evidence; (2) "
    "'norm'/'norms' — gradient norm (both vaults, clipping/diagnosis), "
    "LayerNorm/RMSNorm/pre-norm (master-ai), batch norm (ai-course); the "
    "key is kept because the gradient-norm sense dominates both sides; (3) "
    "'spikes' — both vaults use it for loss-curve spikes as an instability "
    "symptom (genuine cross-vault sense), while 'loss spikes' as an "
    "LLM-operations topic is master-ai-only and links out to '11 - "
    "Training/Optimization/05 - Loss Spikes and Stability'; (4) 'noise' — "
    "master-ai 'training noise' (pitfall: ignoring loss spikes) vs "
    "ai-course 'deafening noise (overflow)' analogy — both metaphorical, "
    "not the irreducible-noise or augmentation senses of EXT-009; (5) "
    "'scale'/'scaling' — init scale (both), residual-stream scaling "
    "(master-ai), attention-score scaling (master-ai), gradient/update "
    "scale (both); (6) 'bias' — bias-parameter initialization (both), "
    "never the statistical-bias sense of the generalization domain; (7) "
    "'decay' (master-ai alias of 'shrink') — gradient shrinkage through "
    "depth, NOT weight decay (which is absent from both batches); (8) "
    "'zeros'/'ones' — constant-initialization tensors (both vaults), "
    "context distinguishes from zero-gradient statements. EXCLUDED "
    "weak/generic anchors (probe-verified present but deliberately not "
    "included because they generate noise without discriminating power, "
    "documented per the EXT-009 rule): 'mean', 'expected', 'E[' (math "
    "notation), 'information', 'input'/'output' ARE included but 'matrix' "
    "alone is folded into 'weight matrix', 'sqrt', 'mathbf', 'frac', "
    "'partial', 'mathcal', 'cdot', 'sigma' (bare LaTeX fragments), "
    "'critical', '2010', '2015' (dating anchors covered by Xavier/Kaiming/"
    "'He et al'/'Glorot and Bengio' keys), '6' (sqrt(6) appears only "
    "inside LaTeX \\sqrt{6} constructs). Keys starting with _ are "
    "documentation and ignored by the loader."
)

FRENCH_PROBES = [
    "initialisation des poids", "gradients évanescents", "disparition du gradient",
    "explosion du gradient", "rétropropagation", "fonction d'activation",
    "apprentissage profond", "réseaux de neurones",
]


def main() -> int:
    kus = []
    for path in (BATCH_010, BATCH_011):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))

    by_vault: dict[str, list[str]] = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r["excerpt"])
    vault_text = {v: "\n".join(excerpts).casefold() for v, excerpts in by_vault.items()}

    def match(text: str, needle: str) -> bool:
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    errors: list[str] = []
    coverage: dict[str, dict] = {}
    for term, aliases in TERM_MAP.items():
        entry: dict[str, object] = {}
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            in_v = {v: match(t, needle) for v, t in vault_text.items()}
            if not any(in_v.values()):
                errors.append(f"{label} {needle!r} (term {term!r}) occurs in NO in-scope excerpt")
            entry[needle] = {v: bool(ok) for v, ok in in_v.items()}
        coverage[term] = entry

    cross_vault_terms = [
        t for t, entry in coverage.items()
        if any(all(entry[n][v] for v in ("ai-course", "master-ai")) for n in entry)
    ]
    bridged_terms = [
        t for t, entry in coverage.items()
        if t not in cross_vault_terms
        and any(entry[n]["ai-course"] for n in entry)
        and any(entry[n]["master-ai"] for n in entry)
    ]

    french_found = [p for p in FRENCH_PROBES if match(vault_text["ai-course"], p) or match(vault_text["master-ai"], p)]

    report = {
        "command": "scripts/ext010_term_map.py",
        "scope_kus": len(kus),
        "scope": {
            "master-ai": "batch 010 (04 - Neural Networks/Training: 07 Initialization Schemes + 08 Vanishing and Exploding Gradients, 2 files, 117 KUs)",
            "ai-course": "batch 011 (04.3 files 01 Weight Initialization + 02 Weight Initialization Techniques + 03 The Vanishing and Exploding Gradient Problems, 3 files, 382 KUs)",
        },
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms": sorted(cross_vault_terms),
        "cross_vault_terms_count": len(cross_vault_terms),
        "bridged_terms": sorted(bridged_terms),
        "bridged_terms_count": len(bridged_terms),
        "french_probe": {
            "probes": FRENCH_PROBES,
            "found": french_found,
            "conclusion": (
                "no French vocabulary in scope; no French aliases included"
                if not french_found
                else f"French hits: {french_found} — adjudicate before including"
            ),
        },
        "per_term_coverage": coverage,
        "errors": errors,
        "ok": not errors,
    }
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1

    payload_out = {"_comment": _COMMENT, **dict(TERM_MAP)}
    OUT.write_text(json.dumps(payload_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms_count": len(cross_vault_terms),
        "bridged_terms_count": len(bridged_terms),
        "french_found": french_found,
        "out": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
