#!/usr/bin/env python3
"""EXT-010 probe round 4: PyTorch API tokens and leftover alias forms.

Word-boundary matching means underscore-suffixed API names need the FULL
token (e.g. 'kaiming_uniform_') as the needle — the trailing underscore is
a word character, so 'kaiming_uniform' cannot match 'kaiming_uniform_'.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCH_010 = REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl"
BATCH_011 = REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl"

PROBES = [
    "xavier_uniform_", "xavier_normal_", "kaiming_uniform_", "kaiming_normal_",
    "nn.init", "calculate_gain", "reset_parameters", "nn.init.calculate_gain",
    "nn.Linear", "nn.Conv2d", "BatchNorm2d", "torch.nn", "torch",
    "fan_in", "fan_out", "fan-in", "fan-out",
    "clip", "clip the gradients", "clip the gradient", "clipped",
    "last layer", "first layers", "early layer", "output layer",
    "residual network", "residual networks", "residual block", "residual blocks",
    "batch norm", "BN", "loss curve", "loss plot", "LR",
    "activation functions", "activation function", "activations",
    "backprop", "backward pass", "weight initialization", "initialization schemes",
    "Glorot initialization", "Xavier initialization", "Kaiming initialization",
    "vanishing gradient problem", "vanishing gradients", "exploding gradients",
    "exploding gradient problem", "learning rates", "initialise", "initialisation",
    "zeros", "ones", "eye", "normal_", "uniform_", "constant_",
    "skip connection", "skip connections", "residual connection",
    "residual connections", "residuals", "residual",
    "norm", "norms", "weight decay", "momentum", "nesterov",
    "std", "sigma_w", "sqrt", "6", "gain", "nonlinearity",
    "orthogonal", "sparse", "sparsity", "goldilocks", "catastrophic",
    "N(0, 1)", "N(0, 0.01)", "standard deviation", "zero-centered",
    "vanishing", "exploding", "saturates", "saturated", "saturation",
    "multiply", "multiplication", "shrink", "decay", "attenuate",
    "dampen", "die out", "extinguish", "wash out",
    "residual stream", "pre-norm", "post-norm", "prenorm", "postnorm",
    "embedding", "embeddings", "projection", "linear layer",
    "sigmoid", "tanh", "ReLU", "rectified", "dying", "dead",
    "vanishing gradient problems", "LSTM", "GRU", "gated",
    "Zhang", "Santurkar", "Ioffe", "Szegedy", "He et al", "Glorot and Bengio",
]

def main() -> int:
    kus = []
    for path in (BATCH_010, BATCH_011):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))
    by_vault = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r["excerpt"])
    vault_text = {v: "\n".join(e).casefold() for v, e in by_vault.items()}

    def match(text, needle):
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    missing = []
    for p in PROBES:
        m = match(vault_text["master-ai"], p)
        c = match(vault_text["ai-course"], p)
        mark = ("M" if m else "-") + ("C" if c else "-")
        if mark == "--":
            missing.append(p)
        print(f"{p}={mark}", end="  ")
        if (PROBES.index(p) + 1) % 6 == 0:
            print()
    print()
    print("MISSING-BOTH:", missing)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
