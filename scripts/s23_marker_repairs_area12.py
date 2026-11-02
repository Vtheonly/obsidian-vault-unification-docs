#!/usr/bin/env python3
"""S23/SYNTH-001: anchored marker repairs for area 12 (Generative Models) —
3 findings -> 0.

AF-001 '03.8' (The Autoencoder.md): source "01. The Autoencoder - Compression
  as Learning.md" L53 "visualize the latent space (via t-SNE or UMAP — see
  [[03.8 - Dimensionality Reduction]])". The source's note id was dropped;
  restored as historical context (session-22 note-ID precedent).

AF-002 'de-duplication' (Score-Based and Latent Diffusion.md): source
  "03. Score-Based and Latent Diffusion.md" L107 "The next steps in the vault
  are the remaining expansion phases: evaluation metrics, math foundations,
  classical ML, and de-duplication." The closing roadmap sentence was dropped;
  restored as historical context.

AF-003 '05.5' (Wasserstein GANs and Modern Variants.md): source "03.
  Wasserstein GANs and Modern Variants.md" L81 "The generator is a U-Net (see
  [[05.5 Deep Learning for Imaging]])". The source note id was dropped;
  restored as historical context.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"


def repair(path: Path, bad: str, good: str, finding: str) -> None:
    text = path.read_text(encoding="utf-8")
    # additive repairs keep `bad` as a substring of `good`; require exactly one
    if text.count(good) == 1 and text.count(bad) == (1 if bad in good else 0):
        print(f"already repaired (idempotent no-op): {finding}")
        return
    assert text.count(bad) == 1, (
        f"{finding}: anchor not found (or not unique) in {path.name} — refusing to guess"
    )
    fixed = text.replace(bad, good, 1)
    assert fixed.count(good) == 1
    if bad not in good:
        assert bad not in fixed
    path.write_text(fixed, encoding="utf-8")
    print(f"repaired {finding} in {path.name}")


def main() -> int:
    # AF-001 03.8
    repair(
        VAULT / "12 - Generative Models/Autoencoders/The Autoencoder.md",
        "visualize the latent space (via the dimensionality reduction tools t-SNE or UMAP — see [[t-SNE and UMAP]])",
        "visualize the latent space (via t-SNE or UMAP — see [[t-SNE and UMAP]]; in the course's numbering this is note 03.8, Dimensionality Reduction)",
        "AF-001",
    )
    # AF-002 de-duplication
    repair(
        VAULT / "12 - Generative Models/Diffusion Models/Score-Based and Latent Diffusion.md",
        "With diffusion, the four major families of generative models are complete: autoencoders (compression), VAEs (probabilistic generation), GANs (adversarial generation), and diffusion (iterative denoising).",
        "With diffusion, the four major families of generative models are complete: autoencoders (compression), VAEs (probabilistic generation), GANs (adversarial generation), and diffusion (iterative denoising). In the source course's reading order, the next steps after generative models are the expansion phases: evaluation metrics, math foundations, classical ML, and de-duplication.",
        "AF-002",
    )
    # AF-003 05.5
    repair(
        VAULT / "12 - Generative Models/GANs/Wasserstein GANs and Modern Variants.md",
        "The generator is a U-Net (see [[Deep Learning for Imaging]]); the discriminator judges pairs (input, output).",
        "The generator is a U-Net (see [[Deep Learning for Imaging]], course note 05.5); the discriminator judges pairs (input, output).",
        "AF-003",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
