#!/usr/bin/env python3
"""S23/SYNTH-001: anchored lint repairs for area-14 CODE_PYTHON_SYNTAX errors.

Two defects, both verbatim-source fence-label artifacts (F-0031 precedent:
the OUTPUT satisfies the lint while the code body stays byte-identical —
the audit's code fingerprint compares bodies, not labels):

1. "Vector Storage with pgvector.md" ~line 168: the source note "02 - Vector
   Storage with pgvector.md" (master-ai, lines 162-173) embeds ONE fence that
   mixes a bare SQL INSERT with async Python, labelled ```python. A
   python-labelled fence must ast-parse (lint CODE_PYTHON_SYNTAX); a mixed
   SQL/Python block cannot. Repair: relabel the fence ```python -> ```text.
   Body unchanged byte-for-byte; the block is genuinely mixed-language.

2. "Guardrails.md" ~line 100: the source note "04 - Guardrails.md"
   (master-ai, lines 84-96) labels a NeMo Guardrails COLANG config fence as
   ```python. Colang is a DSL, not Python. Repair: relabel ```python ->
   ```text. Body unchanged byte-for-byte.

Both repairs keep the fenced CONTENT verbatim (whitespace-insensitive
contract) and keep the audit code fingerprints intact (omission.py
_code_bodies extracts bodies regardless of label except markdown/md).
Anchored, asserted, idempotent.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGETS = [
    {
        "file": REPO / "output/Unified-Vault/14 - Inference and Production/AI Infrastructure/Vector Storage with pgvector.md",
        "bad": "```python\n# On insert, just store the text\nINSERT INTO documents (title, content) VALUES (?, ?) RETURNING id;",
        "good": "```text\n# On insert, just store the text\nINSERT INTO documents (title, content) VALUES (?, ?) RETURNING id;",
        "why": "mixed SQL+Python fence (source: master-ai '02 - Vector Storage with pgvector.md' lines 162-173)",
    },
    {
        "file": REPO / "output/Unified-Vault/14 - Inference and Production/Production AI/Guardrails.md",
        "bad": "```python\n# Example NeMo Guardrails config\ndefine user ask medical advice",
        "good": "```text\n# Example NeMo Guardrails config\ndefine user ask medical advice",
        "why": "Colang DSL fence mislabelled python (source: master-ai '04 - Guardrails.md' lines 84-96)",
    },
]


def main() -> int:
    for t in TARGETS:
        text = t["file"].read_text(encoding="utf-8")
        if t["good"] in text and t["bad"] not in text:
            print(f"already repaired (idempotent no-op): {t['file'].name}")
            continue
        assert t["bad"] in text, f"anchor not found in {t['file'].name} — refusing to guess"
        fixed = text.replace(t["bad"], t["good"], 1)
        assert t["good"] in fixed and t["bad"] not in fixed
        t["file"].write_text(fixed, encoding="utf-8")
        print(f"repaired: {t['file'].name} — {t['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
