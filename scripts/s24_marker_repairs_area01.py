#!/usr/bin/env python3
"""S24/SYNTH-001: anchored marker-retention repairs for area 01 (28 audit findings -> 0).

Root causes (all verbatim-source form artifacts, s23 precedent classes):
- underscore-vs-asterisk emphasis: the ai-course sources mark emphasis with
  _underscores_ (tokenizing to _faster, r-cnn_, _farabet, al._, pixel_,
  vehicle._, _example, _could_); the generated notes used *asterisks*.
  Repair: restore the source's underscore forms (identical rendering).
- ASCII-vs-typographic dashes: source '1950s-1980s', '1980s-2000s' vs note
  en-dashes (s23 '2-10x vs 2-10x' precedent). Repair: source-verbatim ASCII.
- singular-vs-plural / merged-hyphen wording: 'discussions', 'domain
  knowledge-based', 'unparalleled' dropped in paraphrase. Repair: restore
  the source word.
- mermaid label whitespace: the note stripped leading/trailing spaces inside
  node labels (' OVERFITTING', ' Always Plot', ' WRONG', ' Recommended',
  trailing spaces on the nine Compare labels); the code fingerprint is
  whitespace-sensitive inside labels (per-line rstrip only). One whole
  mermaid (the Mistake-2 'Caution' diagram, source lines 645-656) was
  dropped. Repair: restore verbatim, insert the dropped diagram.
- source file-series metadata: the 'Mathematical Notation and Symbols'
  source labels its five sections with **Filename:** `N. ....md` lines
  (tokens symbols.md, descent.md, rule.md, equation.md, function.md);
  restored as historical context (s23 note-ID precedent).
- math-span granularity: source '(e.g., $y, z$)' is ONE math span; the note
  split it into '$y$, $z$'. Repair: single span, source-verbatim.
- vault-meta gap claim: source 'the vault's second-biggest mathematical
  gap' -> restored as 'in the course's own accounting' (s23 course-numbering
  precedent).
- dropped connection: the source's Connections line 'reparameterization
  backprops through a Jacobian' (token 'backprops') restored with its link.

Each repair cites its finding id and source locator. Anchored, asserted,
idempotent. Sources immutable.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "output/Unified-Vault/01 - Foundations/AI ML and DL Hierarchy/Applications of Deep Learning.md"
INTRO = REPO / "output/Unified-Vault/01 - Foundations/AI ML and DL Hierarchy/Introduction to Machine Learning.md"
AIML = REPO / "output/Unified-Vault/01 - Foundations/AI ML and DL Hierarchy/AI vs ML vs DL.md"
NOTATION = REPO / "output/Unified-Vault/01 - Foundations/Mathematical Foundations/Mathematical Notation.md"
DERIV = REPO / "output/Unified-Vault/01 - Foundations/Mathematical Foundations/Derivatives and the Chain Rule.md"
PROB = REPO / "output/Unified-Vault/01 - Foundations/Mathematical Foundations/Probability and Statistics for ML.md"
HIST = REPO / "output/Unified-Vault/01 - Foundations/AI ML and DL Hierarchy/History and Evolution of AI.md"
JAC = REPO / "output/Unified-Vault/01 - Foundations/Mathematical Foundations/Jacobians and Hessians.md"

R = []  # (file, bad, good, why, probe)


def add(file, bad, good, why, probe=None):
    """probe: unique fragment of `good` that only exists once the repair is
    applied AND is not contained in `bad` (insertion repairs where good
    embeds bad need an explicit probe; the default good-fragment check is
    only safe when `bad` is not a substring of `good`)."""
    R.append((file, bad, good, why, probe))


# ---- Applications of Deep Learning -----------------------------------------
add(APP,
    "Deep learning has achieved superhuman performance in domains where data is unstructured and highly complex, which is why it is preferred for image recognition, speech recognition, and natural language processing.",
    "Deep learning has achieved superhuman performance in domains where data is unstructured and highly complex, and it is preferred because it demonstrates unparalleled performance in image recognition, speech recognition, and natural language processing.",
    "AF-025 'unparalleled' (src 06. Applications of Deep Learning.md line 3)")
add(APP,
    "(e.g., using the *Faster R-CNN* architecture)",
    "(e.g., using the _Faster R-CNN_ architecture)",
    "AF-001 '_faster' + AF-002 'r-cnn_' (src line 24: '_Faster R-CNN_')")
add(APP,
    "it classifies *every single pixel* in the image",
    "it classifies _every single pixel_ in the image",
    "AF-021 'pixel_' (src line 30: '_every single pixel_')")
add(APP,
    "(e.g., in the work of *Farabet et al.*)",
    "(e.g., in the work of _Farabet et al._)",
    "AF-019 '_farabet' + AF-020 'al._' (src line 33: '_Farabet et al._')")
add(APP,
    "__A self-driving car, for instance, uses CV to perceive the world, NLP to understand voice commands, and robotics to control the vehicle.__",
    "_A self-driving car, for instance, uses CV to perceive the world, NLP to understand voice commands, and robotics to control the vehicle._",
    "AF-009 'vehicle._' (src line 52: the underscore-italic Venn-diagram note ends '...control the vehicle._'; the note's bold wrap '__...__' replaced by the source's single-underscore wrap)")

# ---- Introduction to Machine Learning --------------------------------------
add(INTRO,
    "**Manual tuning** is domain-knowledge-based selection and iterative refinement.",
    "**Manual tuning** is domain knowledge-based selection and iterative refinement.",
    "AF-005 'knowledge-based' (src 08. Summary line 1140: 'Domain knowledge-based selection')")
add(INTRO,
    '        V4["OVERFITTING<br/>Adjust Hyperparameters"]',
    '        V4[" OVERFITTING<br/>Adjust Hyperparameters"]',
    "AF-003 code fingerprint (src lines 269-285: label has leading space)")
add(INTRO,
    '        V5["Continue Training"]',
    '        V5[" Continue Training"]',
    "AF-003 code fingerprint (src lines 269-285: label has leading space)")
for old, new in [
    ('C1["Training: Updates Weights"]', 'C1["Training: Updates Weights "]'),
    ('C2["Validation: Updates Weights"]', 'C2["Validation: Updates Weights "]'),
    ('C3["Test: Updates Weights"]', 'C3["Test: Updates Weights "]'),
    ('C4["Training: Used During Training"]', 'C4["Training: Used During Training "]'),
    ('C5["Validation: Used During Training"]', 'C5["Validation: Used During Training "]'),
    ('C6["Test: Used During Training"]', 'C6["Test: Used During Training "]'),
    ('C7["Training: Hyperparameter Tuning"]', 'C7["Training: Hyperparameter Tuning "]'),
    ('C8["Validation: Hyperparameter Tuning"]', 'C8["Validation: Hyperparameter Tuning "]'),
    ('C9["Test: Hyperparameter Tuning"]', 'C9["Test: Hyperparameter Tuning "]'),
]:
    add(INTRO, f"        {old}", f"        {new}",
        "AF-004 code fingerprint (src lines 538-557: labels carry trailing spaces)")
add(INTRO,
    '    K5["K=5<br/>Recommended"] --- K10["K=10<br/>More thorough"]',
    '    K5["K=5<br/> Recommended"] --- K10["K=10<br/>More thorough"]',
    "AF-015 code fingerprint (src lines 881-889: label has space after <br/>)")
add(INTRO,
    '    subgraph Always["Always Plot"]',
    '    subgraph Always[" Always Plot"]',
    "AF-016 code fingerprint (src lines 664-673: label has leading space)")
add(INTRO,
    '    subgraph Bad1["WRONG"]',
    '    subgraph Bad1[" WRONG"]',
    "AF-023 code fingerprint (src lines 627-638: label has leading space)")
add(INTRO,
    "**Mistake 2: training on validation later.** Sometimes people merge train + validation after tuning. This is allowed **only after all decisions are finished**.",
    "**Mistake 2: training on validation later.** Sometimes people merge train + validation after tuning. This is allowed **only after all decisions are finished**.\n\n```mermaid\nflowchart LR\n    subgraph Caution[\" Caution\"]\n        C1[\"Merging Train + Val<br/>after tuning\"]\n        C2[\"Allowed ONLY after<br/>ALL decisions finished\"]\n    end\n    \n    C1 --> C2\n    \n    style C2 fill:#FFA07A\n```",
    "AF-017 code fingerprint (src lines 645-656: the whole Caution mermaid was dropped; restored verbatim)",
    probe="subgraph Caution")

# ---- AI vs ML vs DL --------------------------------------------------------
add(AIML,
    "Dominant 1950s–1980s.",
    "Dominant 1950s-1980s.",
    "AF-007 '1950s-1980s' (src 02 - AI vs ML vs DL line 38, ASCII hyphen)")
add(AIML,
    "it is a precondition for meaningful regulatory and ethical discussion",
    "it is a precondition for meaningful regulatory and ethical discussions",
    "AF-022 'discussions' (src line 258: 'Regulatory and ethical discussions require precision')",
    probe="ethical discussions \u2014")
add(AIML,
    "A human expert must manually identify and extract features from raw data to feed into the model. For a self-driving car, a human writes code to find edges, circles (wheels), and colors. For a spam detector, a human might manually create features like \"contains the word 'FREE'\" or \"number of exclamation marks.\"",
    "A human expert must manually identify and extract features from raw data to feed into the model. _Example: For a self-driving car, a human writes code to find edges, circles (wheels), and colors. For a spam detector, a human might manually create features like \"contains the word 'FREE'\" or \"number of exclamation marks.\"_",
    "AF-006 '_example' (src 04. ML vs DL line 9: '_Example: ..._' underscore-italic block)",
    probe="_Example: For a self-driving car")

# ---- Mathematical Notation -------------------------------------------------
add(NOTATION,
    "## The gradient descent equations\n",
    "## The gradient descent equations\n\nThe section below consolidates what the course presented as a five-part series — `1. Mathematical Notation and Symbols.md`, `2. The Core Logic - Gradient Descent.md`, `3. Deriving the Gradient via Chain Rule.md`, `4. The Final Update Equation.md` and `5. Detailed Example - Tanh Function.md` — so those filenames, when cited in course discussions, map onto the parts that follow.\n",
    "AF-008/010/011/026/027 'symbols.md'/'function.md'/'descent.md'/'rule.md'/'equation.md' (src 02. Mathematical Notation and Symbols.md lines 9/117/29/55/97: the **Filename:** series labels, restored as historical context)",
    probe="five-part series")

# ---- Derivatives and the Chain Rule ---------------------------------------
add(DERIV,
    "treat **all other variables (e.g., $y$, $z$) as if they are just numbers (constants).**",
    "treat **all other variables (e.g., $y, z$) as if they are just numbers (constants).**",
    "AF-012 math 'y, z' (src 04. Partial vs. Ordinary Derivatives.md line 34: one math span)")
add(DERIV,
    "    Z2 --> W((Weight w)):::input\n    \n\n    classDef input",
    "    Z2 --> W((Weight w)):::input\n    \n    classDef input",
    "AF-013 code fingerprint (src 05. Derivatives line 366: one whitespace-only line, note had two)")

# ---- Probability and Statistics for ML ------------------------------------
add(PROB,
    "This note fills that gap: after working through it",
    "This note fills that gap — in the course's own accounting, the second-biggest mathematical gap its notes had to close: after working through it",
    "AF-014 'second-biggest' (src 07. Probability line 6: 'the vault's second-biggest mathematical gap', restored as course accounting)")

# ---- History and Evolution of AI ------------------------------------------
add(HIST,
    "multi-layer networks (which we now call MLPs) *could* solve XOR",
    "multi-layer networks (which we now call MLPs) _could_ solve XOR",
    "AF-018 '_could_' (src 05. Evolution line 30: '_could_' underscore emphasis)")
add(HIST,
    "Earlier attempts at deep learning (1980s–2000s) lacked all three.",
    "Earlier attempts at deep learning (1980s-2000s) lacked all three.",
    "AF-024 '1980s-2000s' (src 03 - A Brief History line 160, ASCII hyphen)")

# ---- Jacobians and Hessians (area-01 copy) --------------------------------
add(JAC,
    "the Jacobian $\\partial z / \\partial (\\mu, \\sigma)$ is what lets gradients flow through the sampling step. See [[The Reparameterization Trick]].",
    "the Jacobian $\\partial z / \\partial (\\mu, \\sigma)$ is what lets gradients flow through the sampling step — the reparameterization backprops through a Jacobian. See [[The Reparameterization Trick]] and [[The KL Divergence Loss]].",
    "AF-028 'backprops' (src 08. Multivariate Calculus line 4: 'reparameterization backprops through a Jacobian')")


def main() -> int:
    for file, bad, good, why, probe in R:
        text = file.read_text(encoding="utf-8")
        if probe is not None:
            done = probe in text and text.count(probe) == 1
        else:
            done = good in text and bad not in text
        if done:
            print(f"already repaired (idempotent no-op): {file.name} :: {why[:60]}")
            continue
        assert bad in text, f"anchor not found in {file.name} — refusing to guess :: {why}"
        fixed = text.replace(bad, good, 1)
        assert good in fixed, f"repair not applied in {file.name} :: {why}"
        if probe is not None:
            assert fixed.count(probe) == 1, f"probe count != 1 after repair in {file.name} :: {why}"
        file.write_text(fixed, encoding="utf-8")
        print(f"repaired: {file.name} — {why[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
