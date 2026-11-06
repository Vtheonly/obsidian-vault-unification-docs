#!/usr/bin/env python3
"""S28: close the 9 open findings with verified resolution evidence.

Every closure cites machine-verified evidence produced this session (or the
verified output state). Source-characteristic findings (F-0001/2/3/10/11)
close as RESOLVED-SOURCE-CHARACTERISTIC: the immutable sources keep the
characteristic; the OUTPUT vault is machine-verified clean. Conflict findings
(F-0007/8/9) close with the in-output treatment evidence. F-0014 closes with
the s28 grep pass.

Idempotent: re-running is a no-op (status already resolved -> skip).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FINDINGS = REPO / "state/findings.jsonl"

RESOLUTIONS = {
    "F-0001": {
        "status": "resolved",
        "resolution": (
            "Source characteristic, permanently handled: the trailing-space parent "
            "directory is part of the immutable source layout; every tool resolves "
            "roots via the explicit VAULT_ROOTS mapping (source-vaults/AI /AI Course, "
            "source-vaults/AI /Master AI). Sources verified byte-identical to the "
            "committed manifests at s28 start, mid (gap treatments), and end "
            "(276/276 + 333/333; reports/synthesis/s28-immutable-*.json)."
        ),
    },
    "F-0002": {
        "status": "resolved",
        "resolution": (
            "Source characteristic (14 AI Course source notes with unclosed fences/"
            "math blocks); the extractor's authoritative fence state machine (L-04 "
            "fix) segments them deterministically and the KU fidelity checks pass. "
            "OUTPUT verified clean: lint-artifacts over all 544 notes = 0 errors, 0 "
            "unclosed fences (reports/synthesis/s28-lint-final.json); full-corpus "
            "audit 0 findings (reports/synthesis/s28-final-full-corpus-audit.json)."
        ),
    },
    "F-0003": {
        "status": "resolved",
        "resolution": (
            "Source characteristic (175 broken wikilinks inside the immutable ai-course "
            "source). OUTPUT verified clean: vu check-links over the unified vault = "
            "11,999 links checked, 0 problems (reports/synthesis/s28-final-check-"
            "links.json); lint 0 errors. Broken source links never propagated: link "
            "targets were rewritten to resolved canonical notes during synthesis."
        ),
    },
    "F-0007": {
        "status": "resolved",
        "resolution": (
            "Treated in synthesis with explicit reconciliation: 04 - Machine Learning/"
            "Tree-Based Models/Gradient Boosting.md preserves BOTH datings and "
            "reconciles them ('the library itself first appeared in 2014, while the "
            "famous Chen and Guestrin paper was published in 2016, so both dates "
            "circulate'; timeline summary 'XGBoost is the original (2014 library, "
            "2016 paper), LightGBM followed in 2017, CatBoost appeared 2017-2018'). "
            "Term markers for both claims verified present by the full-corpus audit."
        ),
    },
    "F-0008": {
        "status": "resolved",
        "resolution": (
            "Treated in synthesis with an explicit terminology warning: 04 - Machine "
            "Learning/Model Evaluation/Model Evaluation Metrics.md distinguishes "
            "ranking MAP ('mean average precision over ranked lists') from the "
            "detection metric mAP@IoU ('averages precision over IoU thresholds and "
            "classes') and cross-links [[Computer Vision Evaluation Metrics]] for the "
            "detection family. Both senses preserved with their own formulas."
        ),
    },
    "F-0009": {
        "status": "resolved",
        "resolution": (
            "Treated in synthesis via keep-both preservation: 05 - Neural Network "
            "Foundations/Training Dynamics and Stability/Weight Initialization.md "
            "retains BOTH source statements verbatim ('Biases are initialized to "
            "zero' and 'the bias is initialized from a uniform distribution "
            "U(-1/sqrt(fan_in), 1/sqrt(fan_in))') in adjacent paragraphs, so the "
            "source-level inconsistency is visible to the reader rather than silently "
            "adjudicated (the s27 keep-both rule for source contradictions)."
        ),
    },
    "F-0010": {
        "status": "resolved",
        "resolution": (
            "Source characteristic (54 intentional folder-target links inside the "
            "ai-course source); subsumed by F-0003's resolution. The output vault has "
            "no folder-target ambiguity: check-links 11,999/0 problems."
        ),
    },
    "F-0011": {
        "status": "resolved",
        "resolution": (
            "Source characteristic (338 broken + 29 ambiguous wikilinks inside the "
            "immutable master-ai source). OUTPUT verified clean: check-links 11,999/0 "
            "problems, lint 0 errors, 0 ambiguous basenames (LINK_AMBIGUOUS is an "
            "error-level lint check; reports/synthesis/s28-lint-final.json)."
        ),
    },
    "F-0014": {
        "status": "resolved",
        "resolution": (
            "s28 F-0014 grep pass over the ENTIRE 544-note vault: 0 occurrences of "
            "heading-shaped 'END OF FILE' / 'File Name' markers anywhere (heading or "
            "content form). Extends the s24 verification (areas 01-14) to all areas "
            "incl. 15-20. The marker KUs are accounted via their ledger dispositions; "
            "none were copied as knowledge headings."
        ),
    },
}


def main() -> int:
    records = []
    with FINDINGS.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    changed = 0
    for r in records:
        fid = r.get("finding_id")
        if fid in RESOLUTIONS and r.get("status") == "open":
            r.update(RESOLUTIONS[fid])
            r["resolved_by"] = "s28 orchestrator (SYNTH-001 final phase, 2026-11-06)"
            changed += 1
    if changed:
        with FINDINGS.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter(r.get("status") for r in records)
    print(f"findings updated: {changed} | statuses now: {dict(c)}")
    still_open = [r["finding_id"] for r in records if r.get("status") == "open"]
    if still_open:
        print("still open:", still_open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
