#!/usr/bin/env python3
"""EXT-010 probe round 2: refined candidates from round-1 findings.

Checks additional candidate vocabulary (method names, math-notation words,
stability vocabulary, cross-references to other domains) for in-scope
occurrence per vault before the term map is written.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCH_010 = REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl"
BATCH_011 = REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl"

ROUND2 = {
    "normalization": ["normalize", "normalizing"],
    "Kaiming": ["kaiming_uniform", "kaiming_normal", "Kaiming uniform", "Kaiming normal"],
    "Glorot": ["xavier_uniform", "xavier_normal", "Xavier uniform", "Xavier normal"],
    "spike": ["spikes", "loss spikes", "loss spike"],
    "momentum": [],
    "optimizer": ["optimizers", "Adam", "AdamW"],
    "batch size": ["batch-size"],
    "noise": [],
    "generalization": ["generalize"],
    "overfitting": ["overfit"],
    "covariate": ["internal covariate shift"],
    "numerical": ["numerical stability", "numerical instability"],
    "fp16": ["FP16", "float16", "BF16", "bf16", "fp32", "FP32"],
    "overflow": ["underflow"],
    "gradient flow": [],
    "activation function": ["activation functions"],
    "weight matrix": ["weight matrices", "matrices"],
    "neuron": ["neurons", "hidden units", "hidden unit"],
    "output": ["outputs"],
    "softmax": [],
    "cross-entropy": ["cross entropy"],
    "mean": ["expected"],
    "constant": ["constants"],
    "random": [],
    "seed": [],
    "reset_parameters": ["reset parameters"],
    "nonlinear": ["non-linearity", "nonlinearity", "non-linear"],
    "gain": [],
    "shortcut": ["shortcuts"],
    "plain network": ["plain networks", "plain"],
    "degradation": ["degrade", "degrades"],
    "residual block": ["residual blocks"],
    "residual stream": ["residual stream"],
    "skip": [],
    "saturation": ["saturates", "saturated"],
    "signal": ["learning signal", "signal"],
    "BPTT": ["backpropagation through time"],
    "cyclic": ["cycle", "cycles"],
    "information": [],
    "input": ["inputs"],
    "output layer": ["last layer", "final layer"],
    "shallow": ["shallower", "shallow network"],
    "width": ["wide", "wider"],
    "depth": ["deeper", "deep"],
    "hyperparameter": ["hyperparameters"],
    "tuning": ["tune", "tuned"],
    "dropout": [],
    "early stopping": [],
    "regularization": ["regularize", "regularized"],
    "data augmentation": ["augmentation"],
    "label smoothing": [],
    "co-adaptation": [],
    "transformers": ["Transformer", "transformer"],
    "LLM": ["LLMs", "language model"],
    "pretraining": ["pretrain", "pre-trained"],
    "GPT": [],
    "BERT": [],
    "residual connections": ["skip connections", "skip connection", "residual connection"],
    "checkpoint": ["checkpointing"],
    "horovod": [],
    "distributed": [],
    "epoch": ["epochs", "training loop"],
    "PyTorch default": ["default initialization", "default init", "defaults"],
    "manual init": ["manual initialization", "custom initialization", "custom init"],
    "verify": ["verifying", "verification"],
    "variance tracking": [],
    "fan_in vs fan_out": ["fan in", "fan out"],
    "activation statistics": ["activation statistic"],
    "weight norm": ["weight norms", "norm of the weights"],
    "gradient magnitude": ["magnitudes", "magnitude"],
    "norm": ["norms", "L2 norm", "1 norm", "2 norm"],
    "clip_grad_norm": ["clip_grad_norm_", "clip by norm", "clip by value", "clip by value"],
    "threshold": ["thresholds"],
    "ceiling": ["ceil", "ceilings"],
    "cap": ["capped"],
    "blow up": ["blowing up", "blows up", "blow past"],
    "implode": [],
    "wildly": [],
    "hall-of-mirrors": [],
    "vanishing gradient problem": ["vanishing gradient problems"],
    "exploding gradient problem": ["exploding gradient problems"],
    "catastrophic forgetting": [],
    "cliff": [],
    "flat": ["flat region", "plateau", "plateaus"],
    "saddle": ["saddle point", "saddle points"],
    "curvature": [],
    "critical": ["critically"],
    "hero": [],
    "zero center": ["zero-centered", "zero centered", "zero-mean"],
    "mean zero": [],
    "whitening": [],
    "decorrelated": [],
    "correlation": ["correlated"],
    "standard deviation": ["standard deviations", "std", "stddev"],
    "square root": ["sqrt"],
    "sqrt": [],
    "sigma": ["sigma_w"],
    "2/3": [],
    "6": ["sqrt(6)"],
    "2010": ["2015"],
    "Glorot and Bengio": ["He et al", "He et al."],
    "paper": ["papers"],
}

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

    for term, aliases in ROUND2.items():
        row = []
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            m = match(vault_text["master-ai"], needle)
            c = match(vault_text["ai-course"], needle)
            mark = ("M" if m else "-") + ("C" if c else "-")
            row.append(f"{needle}={mark}")
        print(f"{term}: " + ", ".join(row))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
