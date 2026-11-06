#!/usr/bin/env python3
"""BOOT-004 state update: mark task complete, append next task, refresh
current-state.json, and write the checkpoint. Idempotent-safe: reads the
queue, updates/creates records deterministically."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE = REPO_ROOT / "state" / "task-queue.jsonl"

BOOT004 = {
    "task_id": "BOOT-004",
    "title": "Build omission-detection pilot and verify the auditor",
    "status": "completed",
    "priority": "critical",
    "dependencies": ["BOOT-002", "BOOT-003"],
    "inputs": [
        "synthetic paired-source fixture content (deterministic constants)",
        "KU registry mechanism (CAP-011, mint_ku_id)",
        "docs/VERIFICATION_SPECIFICATION.md",
        "docs/TOOLING_FRAMEWORK.md sections 7 and 9",
    ],
    "outputs": [
        "src/vault_unification/omission.py (CAP-012: fixture builder, 12 declared defects, reusable audit pipeline, pilot orchestrator)",
        "CLI commands: vu audit-output, vu omission-pilot",
        "tests/test_omission.py + CLI tests (37 new tests)",
        "reports/bootstrap/boot-004-omission-pilot.json (canonical pilot evidence)",
        "reports/bootstrap/boot-004-run-summary.json (commands + exit codes)",
        "reports/bootstrap/boot-004-immutable-{before,after}-{master-ai,ai-course}.json",
    ],
    "acceptance_criteria": [
        "Injected unique-detail, equation, caveat, link, and style defects are detected or limitations explicitly documented",
        "Findings link to stable source-unit IDs",
        "Pilot does not modify original vaults",
    ],
    "forbidden_side_effects": [
        "Do not modify original vaults",
        "Do not begin large-scale synthesis before the pilot passes",
    ],
    "tests_run": [
        {
            "command": "python3 scripts/boot004_pilot.py",
            "exit_code": 0,
            "result": "verify-manifest both vaults exit 0 before AND after; omission-pilot exit 0 with verdict pass (12/12 detected, 12/12 localized, 0 FP, 0 FN); all step exit codes recorded in reports/bootstrap/boot-004-run-summary.json",
        },
        {
            "command": "PYTHONPATH=src python3 -m vault_unification run-tests --tests-dir tests --json-report reports/bootstrap/boot-004-pytest-report.json",
            "exit_code": 0,
            "result": "285 passed, 0 failed, 0 skipped (248 pre-existing + 37 new for CAP-012)",
        },
        {
            "command": "PYTHONPATH=src python3 -m vault_unification capabilities --verify --report reports/bootstrap/boot-004-capabilities.json",
            "exit_code": 0,
            "result": "14 implemented-and-tested (CAP-012 now code-backed), 2 planned (CAP-013, CAP-014); 270/270 referenced tests passed in the verification run",
        },
        {
            "command": "PYTHONPATH=src python3 -m vault_unification omission-pilot --dest <tempdir> --report reports/bootstrap/boot-004-omission-pilot.json",
            "exit_code": 0,
            "result": "verdict pass; detection_rate 12/12; localization_rate 12/12; false_positives 0; canonical machine-readable evidence",
        },
        {
            "command": "PYTHONPATH=src python3 -m vault_unification validate-registry --tasks state/task-queue.jsonl",
            "exit_code": 0,
            "result": "6 records, schema + cross-checks valid after the BOOT-004/EXT-001 update",
        },
    ],
    "findings": [],
    "notes": "Hard gate (AGENTS.md 7.5) now PASSED with recorded evidence: verdict pass; 12/12 defects detected; 12/12 localized to expected KU and destination note; 0 false negatives; 0 false positives on the clean baseline; 11 fixture KU records with minted stable IDs; fixture sources byte-identical before/after (in-report check). Defect classes: unique-detail-omission, equation-omission, derivation-step-omission, caveat-omission, equation-sign-alteration, obscure-concept-omission, link-break, heading-convention-change, prose-degradation, version-distinction-loss, accepted-output-drift, code-parameter-deletion (mirrors VERIFICATION_SPECIFICATION.md 'Deliberate omission tests' + section 6). Large-scale synthesis is unblocked. Auditor limitations documented in capabilities inventory, FRAMEWORK_SETUP.md and every report. Honesty test included: an injected undetectable paraphrase defect (DX99) FAILS the pilot by design (tests/test_omission.py::TestPilot::test_pilot_fails_when_defect_undetectable). Pilot fixture and mutated copies live only in temporary directories; committed evidence = report + script. Framework version bumped 0.2.0 -> 0.3.0. Commit hash to be recorded in the follow-up state commit.",
}

EXT001 = {
    "task_id": "EXT-001",
    "title": "Build the deterministic KU extraction pipeline and extract the first bounded real batch",
    "status": "ready",
    "priority": "critical",
    "dependencies": ["BOOT-004"],
    "inputs": [
        "source vaults (read-only): 'source-vaults/AI /Master AI' (333 files), 'source-vaults/AI /AI Course' (276 files)",
        "state/manifests/*.jsonl (baseline hashes)",
        "schemas/knowledge-unit.schema.json v1.1",
        "CAP-003 mdextract (structure), CAP-011 kuregistry (mint_ku_id, kureg-load)",
        "docs/KNOWLEDGE_AND_PROVENANCE.md, docs/EDITORIAL_STYLE_GUIDE.md",
    ],
    "outputs": [
        "new framework capability (e.g. CAP-016 vu extract-kus): deterministic segmentation of source notes into KU records with stable IDs, locators, excerpts and schema-valid batches",
        "first real KU batch under state/knowledge-units/ for ONE bounded domain (suggest AI Course '03 - Machine Learning/03.1 - Regression': 7 files)",
        "extraction coverage report with explicit denominators (files scanned, files yielding units, parse errors, excluded content and why)",
        "registry rebuilt + kureg-validate accounting evidence",
    ],
    "acceptance_criteria": [
        "Every file in the chosen scope is enumerated with a verified extraction outcome or an explicit failure/exclusion disposition",
        "KU records validate against schema v1.1 and cross-checks; kureg-load succeeds; kureg-validate reports 0 unaccounted-at-load anomalies",
        "Extraction is read-only: both source vault manifests unchanged before/after (vu verify-manifest)",
        "Extraction unit tests cover ordinary/boundary/malformed inputs (including unclosed-fence files, F-0002)",
        "No semantic dispositions are claimed by the extractor alone (extraction produces units + locators; overlap/disposition classification is later, evidence-based work)",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not claim semantic preservation from extraction counts",
        "Do not skip files because they are short, obscure or duplicated",
    ],
}


def main() -> int:
    records = []
    with open(QUEUE, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    boot004 = next((r for r in records if r.get("task_id") == "BOOT-004"), None)
    ext001 = next((r for r in records if r.get("task_id") == "EXT-001"), None)

    if boot004 is None:
        # replace the legacy schema-less record (no task_id field) if present
        legacy = next(
            (r for r in records if r.get("title", "").startswith("Build omission-detection")), None
        )
        if legacy is not None:
            records.remove(legacy)
        records.append(BOOT004)
    else:
        boot004.update(BOOT004)

    if ext001 is None:
        records.append(EXT001)
    else:
        ext001.update(EXT001)

    with open(QUEUE, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"task queue updated: {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
