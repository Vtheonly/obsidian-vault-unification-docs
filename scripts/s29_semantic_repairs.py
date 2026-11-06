#!/usr/bin/env python3
"""VERIF-001 repairs (F-0035..F-0039): anchored, probe-idempotent.

Each repair:
  - probe mode: report whether the anchor is present and whether the target
    state is already achieved;
  - apply only when needed; verify after; a second run is a no-op;
  - records before/after evidence in reports/synthesis/s29-semantic-repairs.json.

Run with --probe to only report. Run without to apply.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
VAULT = REPO / "output/Unified-Vault"
REPORT = REPO / "reports/synthesis/s29-semantic-repairs.json"
PROBE_ONLY = "--probe" in sys.argv


def repair_1_quantization(root: Path):
    """F-0036: restore 'quantization' to the Conceptual Interview Questions 2
    coverage list in Current Iteration Log.md."""
    p = root / "20 - Vault and Project Context/Current Iteration Log.md"
    text = p.read_text(encoding="utf-8")
    anchor = "[[Speculative Decoding|spec decoding]], [[DPO|DPO variants]]"
    target = "[[Speculative Decoding|spec decoding]], [[Quantization|quantization]], [[DPO|DPO variants]]"
    done = target in text
    applicable = anchor in text
    return p, applicable, done, (lambda t: t.replace(anchor, target, 1)) if applicable and not done else None, "F-0036"


def repair_2_mha_links(root: Path):
    """F-0035: add the two dropped See-Also links to Multi-Head Attention.md."""
    p = root / "08 - Attention and Transformers/Attention Mechanism/Multi-Head Attention.md"
    text = p.read_text(encoding="utf-8")
    anchor = "- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]\n"
    addition = ("- [[10 - Large Language Models/Context and KV Cache/KV Cache Mechanics|KV Cache Mechanics]]\n"
                "- [[16 - Interpretability and Research/Interpretability/Mechanistic Interpretability|Mechanistic Interpretability]]\n")
    done = "[[10 - Large Language Models/Context and KV Cache/KV Cache Mechanics|KV Cache Mechanics]]" in text
    applicable = anchor in text
    return p, applicable, done, (lambda t: t.replace(anchor, anchor + addition, 1)) if applicable and not done else None, "F-0035"


def repair_3_stutter(root: Path):
    """F-0037: collapse the tripled phrase in Logistic Regression.md."""
    p = root / "04 - Machine Learning/Regression/Logistic Regression.md"
    text = p.read_text(encoding="utf-8")
    bad = "a fascinating mathematical coincidence: a fascinating mathematical coincidence: a fascinating mathematical coincidence:"
    good = "a fascinating mathematical coincidence:"
    done = bad not in text and good in text
    applicable = bad in text
    return p, applicable, done, (lambda t: t.replace(bad, good, 1)) if applicable and not done else None, "F-0037"


def repair_4_huber(root: Path):
    """F-0038: remove the 2nd and 3rd duplicate French-labels blocks in
    Loss Functions.md (keep the first)."""
    p = root / "04 - Machine Learning/Optimization Algorithms/Loss Functions.md"
    text = p.read_text(encoding="utf-8")
    block = ("The original course material wrote the same definition with French condition labels — "
             "worth recognizing because it is the form the exercise notes use:\n"
             "\n"
             "$$ L_\\delta(y, \\hat{y}) = \\begin{cases} \\frac{1}{2}(y - \\hat{y})^2 & \\text{si } |y - \\hat{y}| \\le \\delta \\\\ "
             "\\delta(|y - \\hat{y}| - \\frac{1}{2}\\delta) & \\text{sinon} \\end{cases} $$\n"
             "\n"
             "where *si* means \"if\" and *sinon* means \"otherwise\".\n")
    count = text.count(block)
    done = count == 1
    applicable = count == 3
    def apply(t: str) -> str:
        assert t.count(block) == 3
        first = t.find(block)
        # remove the two later occurrences
        t = t[:first + len(block)] + t[first + len(block):].replace(block, "", 2)
        return t
    return p, applicable, done, apply if applicable and not done else None, "F-0038"


def repair_5_knn(root: Path):
    """F-0039: merge the dangling ': underfitting and high bias' into the
    Large K heading (parallel to Small K form)."""
    p = root / "04 - Machine Learning/Nearest Neighbors/K-Nearest Neighbors.md"
    text = p.read_text(encoding="utf-8")
    old = ("### Large K\n"
           "\n"
           "At the other extreme, $k=20$ or $k=100$ smooths the boundary so aggressively that local structure disappears and the model underfits — the majority class dominates every neighborhood.\n"
           ": underfitting and high bias\n")
    new = ("### Large K: underfitting and high bias\n"
           "\n"
           "At the other extreme, $k=20$ or $k=100$ smooths the boundary so aggressively that local structure disappears and the model underfits — the majority class dominates every neighborhood.\n")
    done = new in text and old not in text
    applicable = old in text
    return p, applicable, done, (lambda t: t.replace(old, new, 1)) if applicable and not done else None, "F-0039"


def main() -> int:
    repairs = [repair_1_quantization, repair_2_mha_links, repair_3_stutter,
               repair_4_huber, repair_5_knn]
    results = []
    any_applied = False
    for fn in repairs:
        p, applicable, done, apply_fn, fid = fn(VAULT)
        rec = {"finding_id": fid, "file": str(p.relative_to(REPO)),
               "probe": {"anchor_applicable": applicable, "already_done": done}}
        if not applicable and not done:
            rec["status"] = "ERROR: anchor not found and target not present"
            results.append(rec)
            continue
        if done:
            rec["status"] = "already-done (no-op)"
        elif PROBE_ONLY:
            rec["status"] = "probe: applicable, not yet applied"
        else:
            before = p.read_text(encoding="utf-8")
            after = apply_fn(before)
            p.write_text(after, encoding="utf-8")
            rec["status"] = "applied"
            rec["bytes_before"] = len(before.encode("utf-8"))
            rec["bytes_after"] = len(after.encode("utf-8"))
            any_applied = True
            # verify idempotency immediately: re-probe
            _, appl2, done2, _, _ = fn(VAULT)
            rec["verify"] = {"anchor_applicable_after": appl2, "done_after": done2}
            if not done2:
                rec["status"] = "ERROR: post-apply verification failed"
        results.append(rec)

    if not PROBE_ONLY:
        REPORT.write_text(json.dumps(
            {"command": "s29_semantic_repairs", "probe_only": False,
             "results": results}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
    for r in results:
        print(f"{r['finding_id']}: {r['status']}"
              + (f" ({r['bytes_before']}->{r['bytes_after']} bytes)" if "bytes_before" in r else ""))
    errs = [r for r in results if r["status"].startswith("ERROR")]
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
