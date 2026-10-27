#!/usr/bin/env python3
"""EXT-010: probe the actual training-stability batch vocabulary BEFORE
building the term map (EXT-004/EXT-005/EXT-009 rule: no invented entries;
pre-probe canonical terms AND aliases AND French contamination).

Reports, per candidate term/alias: which vaults contain it (word-boundary,
case-insensitive) inside KU excerpts. Also reports heading-only occurrences
(headings are not KU-excerpt evidence) and French probes.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCH_010 = REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl"
BATCH_011 = REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl"

CANDIDATES = {
    # --- initialization core ---
    "initialization": ["initialize", "initialized", "initialise"],
    "weight initialization": ["init schemes", "initialization schemes"],
    "symmetry problem": ["symmetric", "symmetry"],
    "zero initialization": ["all-zero", "zeros initialization", "zero init"],
    "Xavier": ["Glorot", "Xavier initialization", "Glorot initialization"],
    "He initialization": ["Kaiming", "He init", "Kaiming initialization"],
    "fan_in": ["fan out", "fan-out", "fan-in"],
    "variance": [],
    "activation": ["activations"],
    "ReLU": ["rectified linear"],
    "sigmoid": [],
    "tanh": [],
    "bias": ["bias initialization", "bias term"],
    "normal distribution": ["Gaussian", "N(0, 1)", "N(0, 0.01)", "N(0, 1)"],
    "uniform": [],
    "orthogonal": [],
    "sparse": ["sparsity"],
    "PyTorch": ["torch", "nn.Linear", "nn.Conv2d"],
    "default": ["defaults"],
    "leaky": ["Leaky ReLU"],
    # --- vanishing/exploding core ---
    "vanishing gradient": ["vanishing gradients", "vanishing"],
    "exploding gradient": ["exploding gradients", "exploding"],
    "gradient": ["gradients"],
    "Jacobian": ["Jacobian matrix", "Jacobians"],
    "backpropagation": ["backprop", "backward pass"],
    "forward pass": ["forward"],
    "chain rule": [],
    "compounding": ["compound", "compounded"],
    "saturation": ["saturated", "saturates"],
    "derivative": ["derivatives"],
    "product": ["products"],
    "exponential": [],
    "deep network": ["deep networks", "deep neural network", "deeper"],
    "layer": ["layers"],
    "early layers": ["early layer", "first layers"],
    "RNN": ["RNNs", "recurrent"],
    "LSTM": ["GRU", "gated"],
    "sequence": ["sequential", "long sequences"],
    "NaN": ["NaNs", "not a number"],
    "inf": ["infinity", "Inf"],
    "dying ReLU": ["dead neurons", "dead ReLU"],
    "PReLU": ["parametric ReLU", "parametric rectified"],
    "ELU": [],
    "skip connection": ["skip connections", "residual connection", "residual connections", "residual", "residuals"],
    "identity": ["identity mapping", "identity shortcut"],
    "batch normalization": ["BatchNorm", "batch norm", "BN", "batch-norm"],
    "LayerNorm": ["Layer Normalization", "layer normalization", "LN"],
    "RMSNorm": ["RMS norm"],
    "gradient clipping": ["clip", "clip_grad_norm", "clipping", "clip the gradients", "gradient clip"],
    "gradient norm": ["norm of the gradient", "gradient norms"],
    "gradient checking": ["numerical gradient", "gradient check"],
    "monitoring": ["monitor", "dashboard"],
    "diagnosis": ["diagnose", "diagnosing", "diagnostic"],
    "learning rate": ["LR", "learning rates"],
    "warmup": ["warm-up", "warm up"],
    "weight decay": [],
    "BPTT": ["backpropagation through time"],
    "attention": ["self-attention", "Transformer", "Transformers"],
    "transformer": ["Transformers", "transformers"],
    "ResNet": ["residual network", "residual networks"],
    "MLP": ["multilayer perceptron", "perceptron", "perceptrons", "multi-layer perceptron"],
    "CNN": ["convolutional", "convolution", "Conv2d"],
    "epoch": ["epochs"],
    "loss": ["loss function", "loss surface", "loss landscape"],
    "non-convex": ["nonconvex", "non convex"],
    "local minimum": ["local minima", "saddle point", "saddle points"],
    "signal": ["learning signal"],
    "training dynamics": ["dynamics"],
    "stability": ["stable", "instability", "unstable"],
    "scale": ["scaling", "scaled"],
    "explosion": ["explode", "explodes"],
    "initialization scale": ["scale of initialization"],
    "goldilocks": [],
    "too large": ["too big", "too high"],
    "too small": ["too low"],
    "oscillate": ["oscillation", "oscillations", "oscillates"],
    "diverge": ["divergence", "diverging", "diverges"],
    "converge": ["convergence", "converging", "converges"],
    "gradient descent": ["SGD", "stochastic gradient descent"],
    "update rule": ["updates", "update"],
    "initial weights": ["starting point", "start of training", "starting weights"],
    "weight": ["weights"],
    "matrix": ["matrices"],
    "eigenvalue": ["eigenvalues", "spectral"],
    "proof": ["prove", "proves", "proving"],
    "interview": ["interview question", "interview questions"],
    "pitfall": ["pitfalls", "common mistake", "common mistakes"],
    "failure mode": ["failure modes"],
    "production": [],
    "worked example": ["example"],
    "derivation": ["derive", "deriving", "derivations"],
    "covariance": [],
    "expected value": ["expectation", "E["],
    "independent": ["independently"],
    "assumption": ["assumptions"],
    "Residual stream": [],
    "LoRA": [],
    "MuP": ["Tensor Programs", "muP", "µP"],
    "Fixup": [],
    "T-Fixup": [],
    "LN": [],
    "weight tying": [],
    "catastrophic": ["catastrophe", "catastrophic forgetting"],
    "breakdown": ["breaks down"],
    "see also": [],
    "decision": ["dense", "sparsely"],
}

FRENCH_PROBES = [
    "initialisation des poids", "gradients évanescents", "disparition du gradient",
    "explosion du gradient", "rétropropagation", "fonction d'activation",
    "normalisation", "apprentissage profond", "réseaux de neurones",
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

    print(f"batch010 (master-ai) excerpts: {len(by_vault['master-ai'])}, batch011 (ai-course) excerpts: {len(by_vault['ai-course'])}")
    print()
    missing_both = []
    single_vault = []
    cross = []
    for term, aliases in CANDIDATES.items():
        statuses = {}
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            in_m = match(vault_text["master-ai"], needle)
            in_c = match(vault_text["ai-course"], needle)
            statuses[needle] = (in_m, in_c)
        term_m, term_c = statuses[term]
        if not term_m and not term_c:
            # check aliases
            if not any(s[0] or s[1] for s in statuses.values()):
                missing_both.append(term)
                continue
        if term_m and term_c:
            cross.append(term)
        else:
            single_vault.append((term, statuses))

    print("CROSS-VAULT terms (%d):" % len(cross))
    print(" ", ", ".join(sorted(cross)))
    print()
    print("SINGLE-VAULT or alias-limited terms (need per-form check):")
    for term, statuses in sorted(single_vault):
        forms = {n: ("M" if m else "-") + ("C" if c else "-") for n, (m, c) in statuses.items()}
        print(f"  {term}: {forms}")
    print()
    print("MISSING-BOTH candidates (drop from map):")
    print(" ", ", ".join(sorted(missing_both)))
    print()
    french_found = [p for p in FRENCH_PROBES if match(vault_text["ai-course"], p) or match(vault_text["master-ai"], p)]
    print("FRENCH probes found:", french_found if french_found else "none")

    # Frequency check for high-frequency content words per vault (catch vocabulary
    # I might have missed) — top 60 content-ish words per vault.
    print()
    stop = set("the a an and or of to in for is are as that this with by on at from it its be can will not but if then when we you they i s t d re ll ve m o c e n u x".split())
    for v in ("master-ai", "ai-course"):
        words = re.findall(r"[a-zA-Z][a-zA-Z_-]{3,}", vault_text[v])
        cnt = Counter(w.casefold() for w in words if w.casefold() not in stop)
        print(f"TOP-50 content words in {v}:")
        print(" ", ", ".join(f"{w}:{c}" for w, c in cnt.most_common(50)))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
