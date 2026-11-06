#!/usr/bin/env python3
"""S27/SYNTH-001: anchored lint repairs for the areas 15-19 gate run.

Findings repaired (s27-lint-vault.json, run at HEAD 368b737 over all 527
on-disk notes):

R1-R3  CODE_PYTHON_SYNTAX (3 errors): the FlashAttention and Linformer paper
       notes fence the sources' PSEUDOCODE blocks (``S = Q K^T ...``) as
       ```python; they are not valid Python. The sources carry them as BARE
       fences (master-ai '26 - Papers/Efficient Attention/08 - FlashAttention
       2022.md' L31-35 and '19 - Linformer 2020.md' L35-41). F-0031
       fence-label precedent (sessions 23/25): the label is corrected to
       `text`, the fence CONTENT stays byte-identical.

R4-R10 LINK_AMBIGUOUS (12 errors, area 05): the area-19 quiz copies of
       'Backpropagation and Gradient Flow in CNNs' (s26 batch) made the
       pre-existing bare links in seven area-05 notes ambiguous. The
       s25-link-rules.md convention (generated set): links from generated-set
       notes use their own area's copy in path form
       [[05 - Neural Network Foundations/Backpropagation/Backpropagation and
       Gradient Flow in CNNs|...]]. The link TARGET is unchanged (same note);
       only the form is disambiguated.

R11    LINK_AMBIGUOUS (2 errors, area 17 Swin pull-forward, generated-set
       member per s25-link-rules.md): bare [[Evolution of CNN Architectures]]
       -> path form targeting the area-06 copy (same note as before the
       area-19 quiz copy existed).

R12    TABLE_CELL_MISMATCH (1 warning, area 19 Notation Conventions.md):
       the conflicts table's $|V|$ cell carries unescaped pipes that split
       the cell (6 cells vs 4 headers). s24 pipe-escaping precedent: escape
       the pipes in the cell AND add a keep-both prose sentence carrying the
       SOURCE-VERBATIM unescaped form (source: master-ai '28 - Glossary/
       03 - Notation Conventions.md' L218 'Use $|V|$ for vocab size.').

Probe-based idempotency (s24 incident lesson): every replacement probes the
defective form, asserts the expected occurrence count, replaces, and asserts
the post-condition; a second run is a complete no-op. Link repairs state the
expected per-file count explicitly and assert 0 remaining after.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

BP_BARE = "[[Backpropagation and Gradient Flow in CNNs]]"
BP_PATH = (
    "[[05 - Neural Network Foundations/Backpropagation/"
    "Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]]"
)
EVO_BARE = "[[Evolution of CNN Architectures]]"
EVO_PATH = (
    "[[06 - Computer Vision/Architecture and Connectivity/"
    "Evolution of CNN Architectures|Evolution of CNN Architectures]]"
)

# (file, bare, path_form, expected_count)
LINK_REPAIRS = [
    # MOC row 09 sits inside the reading-order TABLE: per the vault convention
    # (e.g. Machine Learning MOC L18) the alias pipe inside a table cell is
    # escaped as \| so the row keeps 4 cells.
    ("05 - Neural Network Foundations/Neural Network Foundations MOC.md", BP_BARE,
     "[[05 - Neural Network Foundations/Backpropagation/Backpropagation and Gradient Flow in CNNs\\|Backpropagation and Gradient Flow in CNNs]]", 1),
    ("05 - Neural Network Foundations/Backpropagation/Backpropagation.md", BP_BARE, BP_PATH, 2),
    ("05 - Neural Network Foundations/Backpropagation/Matrix Implementation of Backpropagation.md", BP_BARE, BP_PATH, 1),
    ("05 - Neural Network Foundations/Neural Network Basics/Artificial Neural Networks.md", BP_BARE, BP_PATH, 1),
    ("05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients.md", BP_BARE, BP_PATH, 3),
    ("05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization.md", BP_BARE, BP_PATH, 2),
    ("05 - Neural Network Foundations/Architectures/Convolutional Neural Networks.md", BP_BARE, BP_PATH, 2),
    ("17 - Papers/Attention and Transformers/Swin Transformer.md", EVO_BARE, EVO_PATH, 2),
]

# fence-label repairs: probe = "```python\n" + exact first content line
FENCE_REPAIRS = [
    {
        "id": "S27-LINT-R1",
        "file": "17 - Papers/Efficiency/FlashAttention.md",
        "probe": "```python\nS = Q K^T            # (N, N) matrix in HBM",
        "replacement": "```text\nS = Q K^T            # (N, N) matrix in HBM",
        "note": "F-0031: label python->text; pseudocode content byte-identical (source bare fence L31-35)",
    },
    {
        "id": "S27-LINT-R2",
        "file": "17 - Papers/Efficiency/Linformer.md",
        "probe": "```python\nS = Q K^T              # (N, N) — the expensive part",
        "replacement": "```text\nS = Q K^T              # (N, N) — the expensive part",
        "note": "F-0031: label python->text; pseudocode content byte-identical (source bare fence L35-38)",
    },
    {
        "id": "S27-LINT-R3",
        "file": "17 - Papers/Efficiency/Linformer.md",
        "probe": "```python\nK' = E_i K              # (k, d)  — E_i is a learned N×k projection",
        "replacement": "```text\nK' = E_i K              # (k, d)  — E_i is a learned N×k projection",
        "note": "F-0031: label python->text; pseudocode content byte-identical (source bare fence L38-41)",
    },
]

# S27-LINT-R13: convergence repair for the MOC table row. Repair run 1 wrote
# the row-09 path-form link with an UNESCAPED alias pipe, which splits the
# table cell (TABLE_CELL_MISMATCH: 5 cells vs 4 headers). The vault-wide MOC
# convention escapes the alias pipe inside table cells (e.g. Machine Learning
# MOC L18). This repair converges the row to that convention; link target and
# display text are unchanged.
MOC_ROW = {
    "id": "S27-LINT-R13",
    "file": "05 - Neural Network Foundations/Neural Network Foundations MOC.md",
    "probe": ("| 09 | [[05 - Neural Network Foundations/Backpropagation/Backpropagation and "
              "Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]] | Backpropagation | "
              "How gradients flow through convolutional and pooling layers. |"),
    "replacement": ("| 09 | [[05 - Neural Network Foundations/Backpropagation/Backpropagation and "
                    "Gradient Flow in CNNs\\|Backpropagation and Gradient Flow in CNNs]] | Backpropagation | "
                    "How gradients flow through convolutional and pooling layers. |"),
    "note": "table-cell alias pipe escaped per MOC convention (run-1 convergence)",
}

# keep-both prose carrier for R12 (insertion repair; embeds the anchor, so it
# uses an idempotence marker per the s24 PROSE_ANCHOR pattern)
NOTATION_ANCHOR = {
    "file": "19 - Reference and Practice/Glossary/Notation Conventions.md",
    "bad_cell": "| $V$    | Value matrix             | Vocabulary size (some papers)    | Use $|V|$ for vocab size.                   |",
    "good_cell": "| $V$    | Value matrix             | Vocabulary size (some papers)    | Use $\\|V\\|$ for vocab size.                   |",
    "insert_before": "## Code conventions",
    "carrier": (
        "One resolution deserves a spelling outside the grid: the $V$ row's rule keeps the "
        "cardinality notation for the vocabulary size exactly as the source writes it, "
        "$|V|$ — the table cell escapes those pipes only so the row renders with four columns.\n\n"
    ),
    "idempotence_marker": "the table cell escapes those pipes only so the row renders with four columns",
    "id": "S27-LINT-R12",
}


def main() -> int:
    failed = 0
    applied = 0
    skipped = 0

    # ---- fence-label repairs ----
    for r in FENCE_REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}")
            failed += 1
            continue
        text = path.read_text(encoding="utf-8")
        probe, repl = r["probe"], r["replacement"]
        n = text.count(probe)
        if n == 0:
            if repl in text:
                print(f"OK (already repaired): {r['id']} {r['file']}")
                skipped += 1
                continue
            print(f"FAILED: probe not found and repair not present: {r['id']}")
            failed += 1
            continue
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}")
            failed += 1
            continue
        new_text = text.replace(probe, repl, 1)
        path.write_text(new_text, encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert probe not in post, f"{r['id']}: probe still present after repair"
        assert post.count(repl) == 1, f"{r['id']}: repaired form not present exactly once"
        print(f"APPLIED: {r['id']} {r['file']} ({r['note']})")
        applied += 1

    # ---- link disambiguation repairs ----
    for file, bare, path_form, expected in LINK_REPAIRS:
        path = VAULT / file
        if not path.is_file():
            print(f"FAILED: missing file {file}")
            failed += 1
            continue
        text = path.read_text(encoding="utf-8")
        n = text.count(bare)
        if n == 0:
            if path_form in text:
                print(f"OK (already repaired): links {file}")
                skipped += 1
                continue
            print(f"FAILED: bare link absent and path form absent: {file}")
            failed += 1
            continue
        if n != expected:
            print(f"FAILED: {file} bare link count {n} != expected {expected}, refusing")
            failed += 1
            continue
        new_text = text.replace(bare, path_form)
        path.write_text(new_text, encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert bare not in post, f"{file}: bare link still present after repair"
        assert post.count(path_form) == expected, f"{file}: path form count wrong after repair"
        print(f"APPLIED: links {file}: {expected} bare -> path form")
        applied += 1

    # ---- notation table cell escape + keep-both carrier ----
    a = NOTATION_ANCHOR
    path = VAULT / a["file"]
    if not path.is_file():
        print(f"FAILED: missing file {a['file']}")
        failed += 1
    else:
        text = path.read_text(encoding="utf-8")
        if a["idempotence_marker"] in text:
            # already repaired: verify both sub-repairs present
            assert a["bad_cell"] not in text, f"{a['id']}: bad cell still present"
            assert a["good_cell"] in text, f"{a['id']}: good cell missing"
            print(f"OK (already repaired): {a['id']} {a['file']}")
            skipped += 1
        else:
            ok = True
            if text.count(a["bad_cell"]) == 1 and text.count(a["insert_before"]) == 1:
                new_text = text.replace(a["bad_cell"], a["good_cell"], 1)
                new_text = new_text.replace(a["insert_before"], a["carrier"] + a["insert_before"], 1)
                path.write_text(new_text, encoding="utf-8")
                post = path.read_text(encoding="utf-8")
                assert a["bad_cell"] not in post
                assert a["good_cell"] in post
                assert "$|V|$" in post, f"{a['id']}: keep-both verbatim form missing from carrier"
                assert post.count(a["idempotence_marker"]) == 1
                print(f"APPLIED: {a['id']} {a['file']} (cell escaped + keep-both carrier)")
                applied += 1
            else:
                cb, ci = text.count(a["bad_cell"]), text.count(a["insert_before"])
                if cb == 0 and a["good_cell"] in text:
                    print(f"PARTIAL: cell already escaped but carrier marker missing: {a['id']}")
                else:
                    print(f"FAILED: {a['id']} bad_cell count={cb}, anchor count={ci}")
                ok = False
                failed += 1

    # ---- S27-LINT-R13: MOC table-row alias-pipe convergence ----
    r = MOC_ROW
    path = VAULT / r["file"]
    if not path.is_file():
        print(f"FAILED: missing file {r['file']}")
        failed += 1
    else:
        text = path.read_text(encoding="utf-8")
        n = text.count(r["probe"])
        if n == 0:
            if r["replacement"] in text:
                print(f"OK (already repaired): {r['id']} {r['file']}")
                skipped += 1
            else:
                print(f"FAILED: probe not found and repair not present: {r['id']}")
                failed += 1
        elif n == 1:
            new_text = text.replace(r["probe"], r["replacement"], 1)
            path.write_text(new_text, encoding="utf-8")
            post = path.read_text(encoding="utf-8")
            assert r["probe"] not in post, f"{r['id']}: probe still present"
            assert post.count(r["replacement"]) == 1, f"{r['id']}: replacement missing"
            print(f"APPLIED: {r['id']} {r['file']} ({r['note']})")
            applied += 1
        else:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}")
            failed += 1

    print(f"\nsummary: applied={applied} skipped(already)= {skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
