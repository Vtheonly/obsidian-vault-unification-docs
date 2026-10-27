#!/usr/bin/env python3
"""REGEN-001 step 4: persist project state after the feat commit.

Updates (referencing the already-created feat commit hash so no record ever
claims completion before its commit exists):
- state/task-queue.jsonl: REGEN-0001 record -> completed with evidence;
- state/current-state.json: extraction state, framework version, next task;
- state/findings.jsonl: three new findings (stale test-count docs, the
  empty_section design contract, the END-OF-FILE marker source convention);
- state/checkpoints/checkpoint-2026-10-28-regen001.json: new checkpoint;
- README.md repository-status section; docs/agent-handoff/next-agent.md.

Run AFTER the feat commit; the state commit follows separately.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FEAT_COMMIT = sys.argv[1] if len(sys.argv) > 1 else "PENDING"

QUEUE = REPO_ROOT / "state" / "task-queue.jsonl"
STATE = REPO_ROOT / "state" / "current-state.json"
FINDINGS = REPO_ROOT / "state" / "findings.jsonl"
CHECKPOINT = REPO_ROOT / "state" / "checkpoints" / "checkpoint-2026-10-28-regen001.json"


def update_queue() -> None:
    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("task_id") == "REGEN-001" and rec.get("status") == "queued":
            rec.update(
                {
                    "status": "completed",
                    "priority": "critical",
                    "outputs": [
                        "src/vault_unification/kufidelity.py + vu ku-fidelity (CAP-022, framework 0.8.0): reusable batch-fidelity gate replacing the per-task fidelity scripts of EXT-001..010",
                        "state/knowledge-units/012-070-regen001-*.jsonl (59 batches, 578 files, 25,808 KUs)",
                        "reports/regen/regen001-revalidation.json (11 committed batches regenerate byte-identically; 1728/1728 records excerpt-byte-exact)",
                        "reports/regen/regen001-plan.json + regen001-extraction.json + per-batch coverage/fidelity reports",
                        "reports/regen/regen001-registry.json + regen001-kureg-validate.json (registry rebuilt from 70 batches + 7 overlays, green)",
                        "reports/regen/regen001-accounting.json (609/609 files covered exactly once, 27,536 KUs, ids globally unique)",
                        "reports/regen/regen001-final-pytest.json (full suite evidence, recorded by the state commit)",
                    ],
                    "acceptance_criteria": [
                        "All 609 source files and assets have explicit processing outcomes",
                        "Each KU retains source hash, exact locator, excerpt fidelity, and stable unique ID",
                        "Malformed or unsupported content is reported and never silently dropped",
                        "Batch reruns are deterministic and source manifests remain unchanged",
                        "Every KU receives a tracked disposition state; Unaccounted remains a release blocker",
                    ],
                    "tests_run": [
                        {
                            "command": "python3 -m pytest tests/ -q",
                            "result": "604/604 passed (576 baseline + 22 kufidelity unit tests + 5 CLI tests + 1 help parametrization)",
                            "evidence": "reports/regen/regen001-final-pytest.json",
                        },
                        {
                            "command": "vu capabilities --verify",
                            "result": "verified: true; 22 implemented-and-tested + 1 planned (CAP-014); CAP-022 verified by running its referenced test files",
                            "evidence": "session log (recorded in regen001-final-pytest.json notes)",
                        },
                        {
                            "command": "python3 scripts/regen001_revalidate.py",
                            "result": "11/11 committed batches regenerate byte-identically after double-runs; ku-fidelity ai-course 1370/1370 + master-ai 358/358 exact",
                            "evidence": "reports/regen/regen001-revalidation.json",
                        },
                        {
                            "command": "python3 scripts/regen001_extract.py",
                            "result": "59/59 batches extracted, double-run byte-identical, fidelity-verified; 578 files; two latent defects caught by the gates (empty_section heading contract; resume numbering instability) and fixed with regression tests / pinned numbering",
                            "evidence": "reports/regen/regen001-extraction.json + per-batch reports",
                        },
                        {
                            "command": "python3 scripts/regen001_registry.py",
                            "result": "70/70 batches loaded, 7/7 overlays applied, kureg-validate exit 0; accounting 276/276 + 333/333 files, 0 missing/extra/multi-batch, 27,536 KUs, 0 duplicate ids, 0 source hash mismatches",
                            "evidence": "reports/regen/regen001-registry.json + reports/regen/regen001-accounting.json",
                        },
                        {
                            "command": "vu verify-manifest on both vaults (before and after extraction)",
                            "result": "ai-course 276/276 unchanged, master-ai 333/333 unchanged, exit 0 both times",
                            "evidence": "session log + regen001-accounting.json source_hash_mismatches fields",
                        },
                    ],
                    "findings": ["F-0012", "F-0013", "F-0014"],
                    "notes": "completed 2026-10-28 in one session. Full corpus now extracted: 609/609 files, 27,536 KUs across 70 committed batches, every batch double-run byte-identical and byte-faithful to sources. All KUs remain disposition 'Unaccounted' by design (assignment is later work; Unaccounted blocks release). The 11 pre-restart batches were revalidated rather than regenerated. Two framework-level defects were caught by the new gates during the run and fixed: the fidelity checker's heading rule did not know the empty_section design contract, and the extraction driver derived batch numbering from directory contents (unstable across resumes; the 14 duplicate batches it minted were caught by the id-collision gate, verified byte-identical to their twins, deleted, and the numbering pinned). DISC-002 (corpus-wide discovery) is now unblocked.",
                    "commit": FEAT_COMMIT,
                }
            )
        out.append(json.dumps(rec, sort_keys=True))
    QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["stage"] = "regen001-full-corpus-extraction-complete"
    state["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-28-regen001.json"
    state["current_task_id"] = "DISC-002"
    state["framework_version"] = "0.8.0"
    state["knowledge_registry"]["records"] = 27536
    state["knowledge_registry"][
        "classifications"
    ] = "state/classifications/001-ext003-regression-overlap.jsonl (14 records) + 002-ext004-tree-based-overlap.jsonl (28 records) + 003-ext005-evaluation-overlap.jsonl (29 records) + 004-ext007-evaluation-addendum.jsonl (4 records) + 005-ext008-clustering-dimreduction-overlap.jsonl (27 records) + 006-ext009-generalization-overlap.jsonl (26 records) + 007-ext010-training-stability-overlap.jsonl (36 records, EXT-010; ADR-0009 pair-level overlay)"
    state["notes"] = (
        "REGEN-001 completed 2026-10-28 (feat commit "
        + FEAT_COMMIT
        + "): full-corpus re-extraction under the hardened pipeline. All 609 source files "
        "extracted into 70 committed batches (11 revalidated pre-restart + 59 new REGEN batches "
        "012-070); 27,536 KUs, every id globally unique; every batch double-run byte-identical "
        "and fidelity-verified by the NEW reusable gate vu ku-fidelity (CAP-022, framework "
        "0.8.0), which replaces the per-task fidelity scripts. Registry rebuilt from all 70 "
        "batches + 7 classification overlays; kureg-validate green; full-corpus accounting: "
        "276/276 ai-course + 333/333 master-ai files covered exactly once, 0 missing/extra/"
        "multi-batch, 0 source hash mismatches (both vaults byte-unchanged). Two latent defects "
        "were caught by the gates mid-run and fixed with regression tests: (1) the fidelity "
        "heading rule did not know the empty_section design contract (units sit ON their "
        "heading line; batches 014/015 first flagged it); (2) the extraction driver derived "
        "batch numbering from directory contents, so a resumed run renumbered the plan and "
        "minted 14 duplicate batches - caught by the id-collision gate, verified byte-identical "
        "to their twins, deleted, numbering pinned to the committed sequence. New findings "
        "F-0012 (stale 563-vs-576 test-count docs, now corrected), F-0013 (empty_section "
        "design contract), F-0014 (END-OF-FILE marker-heading source convention, 2 files). "
        "All 27,536 KUs remain 'Unaccounted' by design: disposition assignment is the "
        "release-blocking work after concept discovery. NEXT: DISC-002 - run corpus-wide "
        "emergent-concept discovery over the complete registry (the coverage gate is now "
        "OPEN at 609/609), review candidates via vu discovery-decide (semantic review is the "
        "agent's job; the tool collects evidence), reconcile dossiers, then gated synthesis."
    )
    state["phase_zero_rebaseline"]["full_corpus_extraction"] = {
        "task": "REGEN-001",
        "completed_utc": "2026-10-28",
        "files_extracted": 609,
        "batches": 70,
        "kus": 27536,
        "revalidation": "reports/regen/regen001-revalidation.json",
        "plan": "reports/regen/regen001-plan.json",
        "extraction": "reports/regen/regen001-extraction.json",
        "registry": "reports/regen/regen001-registry.json",
        "accounting": "reports/regen/regen001-accounting.json",
        "tests": "604/604 (reports/regen/regen001-final-pytest.json)",
    }
    STATE.write_text(json.dumps(state, indent=1, sort_keys=False) + "\n", encoding="utf-8")


def add_findings() -> None:
    new_findings = [
        {
            "finding_id": "F-0012",
            "title": "Checkpoint/README/handoff test-count text was stale (563) vs the recorded report (576)",
            "category": "documentation-defect",
            "severity": "low",
            "status": "resolved",
            "discovered_by": "REGEN-001 session (2026-10-28)",
            "observed": "The frame002 checkpoint, README repository-status and next-agent handoff all stated '563/563 tests' while reports/rebaseline/frame002-final-pytest.json records 576 passed; a fresh re-run also collected 576.",
            "evidence": "reports/rebaseline/frame002-final-pytest.json summary.passed=576 vs state/checkpoints/checkpoint-2026-10-27-frame002.json test_suite.result='563 passed'",
            "expected_condition": "Human-written state text must match the machine-generated report it cites.",
            "root_cause": "The prose kept an intermediate session count (563 at an earlier moment of FRAME-002) while the final report captured 576; the state text was never reconciled after the last test addition.",
            "impact": "Conservative undercount only (claimed fewer tests than actually passed); no work was claimed that did not exist, but the discrepancy erodes trust in handoff text.",
            "repair_recommendation": "Correct the stale numbers wherever cited; prefer citing the report path over restating numbers in prose.",
            "resolution": "Corrected in this session's README/checkpoint/handoff updates; regen001 records cite report paths.",
        },
        {
            "finding_id": "F-0013",
            "title": "empty_section KU design contract was undocumented outside extractor code (fidelity rule defect)",
            "category": "tool-defect",
            "severity": "medium",
            "status": "resolved",
            "discovered_by": "REGEN-001 session (2026-10-28)",
            "observed": "The new ku-fidelity gate flagged legitimate fresh-extraction units as 'span crosses heading line' because empty_section units sit exactly ON their heading line by extractor design (kuextract.py mints them with line_start=line_end=heading line so promised-but-empty sections are represented).",
            "evidence": "reports/regen/batch-014-fidelity.json + batch-015-fidelity.json (pre-fix); src/vault_unification/kuextract.py empty-section block; zero empty_section units existed in the 31 previously extracted files, so EXT-001..010 fidelity scripts never exercised this path",
            "expected_condition": "The fidelity checker enforces the extractor's actual design contract, not a stronger rule the extractor never promised.",
            "root_cause": "The heading-crossing rule was copied from the per-task fidelity scripts, which had only ever run on files without empty sections; the design contract lived only in extractor code comments.",
            "impact": "False failures on batches 014/015 during full-corpus processing; without the gate's failure the rule would have stayed latent for synthesis-time verification.",
            "repair_recommendation": "Unit-type-aware rule: empty_section spans must be exactly one heading line; all other unit types must not cross heading lines. Pin with regression tests on both sides.",
            "resolution": "Fixed in vault_unification.kufidelity with tests test_empty_section_on_heading_line_is_design_conformant and test_empty_section_not_on_heading_line_detected; batches 014/015 re-verified green.",
        },
        {
            "finding_id": "F-0014",
            "title": "Two AI Course files use 'END OF FILE / File Name' heading-shaped markers as final lines",
            "category": "source-characteristic",
            "severity": "low",
            "status": "open",
            "discovered_by": "REGEN-001 session (2026-10-28)",
            "observed": "KNN Comprehensive ends with '### END OF FILE: ...' and Fundamentals of Neural Networks contains '### File Name: ...' as content-free trailing heading lines; the extractor represents them as empty_section KUs (content preserved verbatim).",
            "evidence": "source-vaults/AI /AI Course/03 - Machine Learning/03.3 - K-Nearest Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - Comprehensive.md line 737; source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning Foundations/04.1 - Neural Network Basics/01. Fundamentals of Neural Networks.md line 212",
            "expected_condition": "Source conventions are preserved verbatim; synthesis must not reproduce file-marker headings as knowledge headings in the unified vault.",
            "root_cause": "Authoring convention in the source vault (file-boundary markers), not a defect.",
            "impact": "If synthesized notes copy these marker headings, the output vault would inherit meaningless headings; the KUs themselves are correctly accounted.",
            "repair_recommendation": "At synthesis time, map these marker units to contextual/no-heading destinations rather than note headings; do not drop them silently.",
        },
    ]
    existing = FINDINGS.read_text(encoding="utf-8").splitlines() if FINDINGS.exists() else []
    existing_ids = set()
    for line in existing:
        if line.strip():
            existing_ids.add(json.loads(line).get("finding_id"))
    with FINDINGS.open("a", encoding="utf-8") as fh:
        for f in new_findings:
            if f["finding_id"] not in existing_ids:
                fh.write(json.dumps(f, sort_keys=True) + "\n")


def write_checkpoint() -> None:
    checkpoint = {
        "checkpoint_id": "checkpoint-2026-10-28-regen001",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "task_ids_completed": [
            "BOOT-000",
            "BOOT-001",
            "BOOT-002",
            "BOOT-003",
            "BOOT-004",
            "EXT-001",
            "EXT-002",
            "EXT-003",
            "EXT-004",
            "EXT-005",
            "EXT-006",
            "EXT-007",
            "EXT-008",
            "EXT-009",
            "EXT-010",
            "REBASE-000",
            "AUDIT-011",
            "FRAME-001",
            "DISC-001",
            "FRAME-002",
            "REGEN-001",
        ],
        "task_ids_open": ["DISC-002"],
        "framework_version": "0.8.0",
        "feat_commit": FEAT_COMMIT,
        "test_suite": {
            "command": "python3 -m pytest tests/ -q",
            "result": "604 passed",
            "evidence": "reports/regen/regen001-final-pytest.json",
        },
        "capabilities": {
            "verified": True,
            "implemented_and_tested": 22,
            "planned": 1,
        },
        "extraction_state": {
            "files_extracted": 609,
            "files_total": 609,
            "batches": 70,
            "kus": 27536,
            "revalidated_pre_restart_batches": 11,
            "new_regen_batches": 59,
            "classifications": 164,
            "dossiers": 6,
            "all_kus_disposition": "Unaccounted",
        },
        "source_immutability": {
            "ai-course": "276/276 unchanged (manifest verify exit 0, before and after)",
            "master-ai": "333/333 unchanged (manifest verify exit 0, before and after)",
        },
        "next": [
            "DISC-002: corpus-wide emergent-concept discovery over the complete registry (coverage gate now open at 609/609), candidate review via vu discovery-decide, dossier reconciliation",
            "then disposition assignment and gated synthesis (every batch: check-prompt -> generation -> lint -> assess -> drift -> gate -> repair)",
        ],
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    update_queue()
    update_state()
    add_findings()
    write_checkpoint()
    print("state updated: task-queue, current-state, findings, checkpoint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
