#!/usr/bin/env python3
"""EXT-010 scope-evidence probe: extract headings for candidate pairing files.

Read-only. Uses mdextract.extract_structure_text (CAP-003 authority) per the
EXT-005..009 rule that heading/construct detection must not be naive regex.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1] / "obsidian-vault-unification-docs"
sys.path.insert(0, str(REPO / "src"))

from vault_unification import mdextract  # noqa: E402

CANDIDATES = [
    # master-ai NN Training (the natural 01-03 counterpart family)
    "source-vaults/AI /Master AI/04 - Neural Networks/Training/07 - Initialization Schemes.md",
    "source-vaults/AI /Master AI/04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md",
    "source-vaults/AI /Master AI/04 - Neural Networks/Training/06 - Backpropagation.md",
    # master-ai 11-Training Optimization (the EXT-009-reserved counterpart)
    "source-vaults/AI /Master AI/11 - Training/Optimization/05 - Loss Spikes and Stability.md",
    "source-vaults/AI /Master AI/11 - Training/Optimization/04 - Mixed Precision Training.md",
    # ai-course 04.3 files 01-04 (unextracted remainder)
    "source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md",
    "source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md",
    "source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md",
    "source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md",
]

for rel in CANDIDATES:
    p = REPO / rel
    if not p.exists():
        print(f"### {rel}\nMISSING\n")
        continue
    text = p.read_text(encoding="utf-8")
    struct = mdextract.extract_structure_text(text)
    print(f"### {rel}")
    print(f"lines={len(text.splitlines())} bytes={p.stat().st_size}")
    for h in struct.get("headings", []):
        level = h.get("level", 1)
        print("  " * (level - 1) + f"L{level} " + h.get("text", ""))
    print()
