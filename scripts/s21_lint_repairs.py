#!/usr/bin/env python3
"""S21/SYNTH-001: lint repair pass for the areas 05+06 batch.

Fixes the four lint ERRORS found by `vu lint-artifacts` over the 127-note
vault (reports/synthesis/s21-lint-vault.json):

  1-3. FRONTMATTER_FIELD_TYPE (x3): alias entries containing a colon parsed
       as YAML mappings instead of strings -> quote the alias strings.
  4.   CODE_PYTHON_SYNTAX (x1): a python fence nested in a checklist item
       carried the item's 2-space indent, so its body fails ast.parse ->
       dedent the fence body to column 0 (whitespace-only change; the code
       itself is untouched).

The six lint WARNINGS are NOT repaired: they are verbatim source artifacts
(quiz `a) b) c) d)` option format, `[0,∞)` interval notation, a literal `$10`
price), documented in the session-21 records — altering them would violate
the verbatim-preservation contract.

Anchored, asserted, idempotent: re-running finds already-applied edits and
skips them. A failed or ambiguous anchor aborts with a non-zero exit.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"

# (relative path, unique old text, exact new text)
REPAIRS: list[tuple[str, str, str]] = [
    # 1. aliases with colons -> quoted strings (YAML mapping -> string)
    (
        "06 - Computer Vision/CNN Foundations and Philosophy/Demystifying Tensors - Volumes, Depth, and Data Formats.md",
        "  - Demystifying Tensors: Volumes, Depth, and Data Formats",
        '  - "Demystifying Tensors: Volumes, Depth, and Data Formats"',
    ),
    (
        "06 - Computer Vision/Image Fundamentals/Image Representation Types.md",
        "  - Image Representation: Bitmap vs. Vector",
        '  - "Image Representation: Bitmap vs. Vector"',
    ),
    (
        "06 - Computer Vision/Spatial Filtering/Gabor Filters.md",
        "  - In-Depth: Principles of Gabor Filtering",
        '  - "In-Depth: Principles of Gabor Filtering"',
    ),
    # 2. indented fence body inside a checklist item -> dedent to column 0
    (
        "06 - Computer Vision/Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "  ```python\n  transforms.Normalize(\n      mean=[0.485, 0.456, 0.406], \n      std=[0.229, 0.224, 0.225]\n  )\n  ```",
        "  ```python\ntransforms.Normalize(\n    mean=[0.485, 0.456, 0.406], \n    std=[0.229, 0.224, 0.225]\n)\n  ```",
    ),
]


def main() -> int:
    applied = 0
    skipped = 0
    for relpath, old, new in REPAIRS:
        path = VAULT / relpath
        if not path.is_file():
            print(f"FAIL: file not found: {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        if new in text and old not in text:
            skipped += 1  # already applied (idempotent)
            continue
        hits = text.count(old)
        if hits != 1:
            print(f"FAIL: anchor not unique ({hits} hits): {relpath}: {old[:60]!r}", file=sys.stderr)
            return 1
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        applied += 1
        print(f"applied: {relpath}: {old[:50]!r} -> {new[:50]!r}")
    import json

    print(
        json.dumps(
            {
                "script": "scripts/s21_lint_repairs.py",
                "repairs_declared": len(REPAIRS),
                "applied": applied,
                "already_applied": skipped,
                "idempotent": True,
                "warnings_left_untouched": "5x BRACKET_UNBALANCED (quiz a) options x4, [0,∞) interval x1) + 1x MATH_INLINE_ODD (literal $10 price) — verbatim source artifacts, documented",
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
