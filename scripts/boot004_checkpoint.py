#!/usr/bin/env python3
"""BOOT-004: refresh state/current-state.json and write the checkpoint."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CURRENT_STATE = {
    "project": "Obsidian Vault Unification",
    "execution_environment": "Z AI / GLM 5.3 with available subagents",
    "stage": "framework_bootstrap",
    "status": "in_progress",
    "source_vaults_located": True,
    "source_vaults": [
        {
            "name": "Master AI",
            "path": "source-vaults/AI /Master AI",
            "note": "path contains a trailing space in parent directory 'AI ' (finding F-0001); always quote",
            "files": 333,
            "file_classes": {"markdown": 333},
            "baseline_manifest": "state/manifests/master-ai.jsonl",
            "bytes": 4601557,
            "source_location_record": "reports/bootstrap/boot-001-source-location.json",
        },
        {
            "name": "AI Course",
            "path": "source-vaults/AI /AI Course",
            "note": "path contains a trailing space in parent directory 'AI ' (finding F-0001); always quote",
            "files": 276,
            "file_classes": {"markdown": 276},
            "baseline_manifest": "state/manifests/ai-course.jsonl",
            "bytes": 3546362,
            "source_location_record": "reports/bootstrap/boot-001-source-location.json",
        },
    ],
    "source_inventory_complete": True,
    "knowledge_registry_initialized": True,
    "framework_foundation_built": True,
    "framework_foundation_tested": True,
    "framework_evidence": {
        "test_run": "reports/bootstrap/boot-004-pytest-report.json",
        "test_summary": "285 passed, 0 failed, 0 skipped",
        "capabilities": "reports/bootstrap/boot-004-capabilities.json",
        "setup_doc": "docs/FRAMEWORK_SETUP.md",
    },
    "verification_pilot_passed": True,
    "verification_pilot_evidence": {
        "pilot_report": "reports/bootstrap/boot-004-omission-pilot.json",
        "run_summary": "reports/bootstrap/boot-004-run-summary.json",
        "verdict": "pass",
        "detection_rate": "12/12",
        "localization_rate": "12/12",
        "false_negatives": 0,
        "false_positives_on_clean_baseline": 0,
        "defect_classes": 12,
        "immutability": "both vaults verified unchanged before and after (exit 0, four manifest reports)",
    },
    "output_synthesis_started": False,
    "last_verified_checkpoint": "state/checkpoints/checkpoint-2026-10-26-boot-004.json",
    "current_task_id": "EXT-001",
    "notes": "BOOT-000..BOOT-004 completed. Framework v0.3.0: 14 code-backed capabilities implemented-and-tested (285/285 tests), 2 planned (CAP-013 duplicates, CAP-014 coverage regression). The omission-detection hard gate (AGENTS.md 7.5) PASSED: synthetic paired-source fixture, 12 planted defects across the VERIFICATION_SPECIFICATION taxonomy, 12/12 detected AND localized to expected KU + destination, 0 false negatives, 0 false positives on the clean baseline; reusable real-work pipeline exposed as 'vu audit-output' (KU-batch validation, manifest drift, disposition/destination accounting, rare-term/equation/code marker retention, link integrity, heading-convention and prose-quality lint). Sources unchanged throughout. Canonical inventory complete: 609 markdown files, 1.16M words, ~2.03M tokens est. Canonical KU store still 0 records (no real extraction yet). Next: EXT-001 - deterministic KU extraction pipeline + first bounded real batch (suggest AI Course 03.1 - Regression, 7 files).",
    "corpus_statistics": {
        "files_total": 609,
        "markdown_files": 609,
        "words_total": 1157937,
        "words_outside_fences": 990007,
        "tokens_estimate_chars_div_4": 2027347,
        "headings_total": 12785,
        "per_vault": {
            "Master AI": {
                "files": 333,
                "words_total": 638004,
                "tokens_estimate": 1144484,
                "headings": 8610,
                "files_with_errors": 0,
            },
            "AI Course": {
                "files": 276,
                "words_total": 519933,
                "tokens_estimate": 882863,
                "headings": 4175,
                "files_with_errors": 14,
            },
        },
        "evidence": "reports/bootstrap/boot-002-inventory-summary.json",
    },
    "knowledge_registry": {
        "canonical_store": "state/knowledge-units/ (committed JSONL batches; ADR-0007)",
        "derived_index": "state/registries/ (git-ignored SQLite; rebuild via kureg-init + kureg-load)",
        "records": 0,
        "schema_version": "1.1 (ADR-0008: overlap_type + superseded_rationale)",
        "commands": "vu kureg-init / kureg-load / kureg-query / kureg-validate",
        "capability": "CAP-011 implemented-and-tested (reports/bootstrap/boot-004-capabilities.json)",
        "note": "mechanism only; real extraction has not started (EXT-001 is next)",
    },
}

CHECKPOINT = {
    "checkpoint_id": "CHK-2026-10-26-BOOT-004",
    "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "stage": "framework_bootstrap",
    "task_id": "BOOT-004",
    "task_status": "completed",
    "last_verified_state": {
        "framework_version": "0.3.0 + CAP-012 (omission pilot and output auditor)",
        "test_result": "285 passed, 0 failed, 0 skipped",
        "test_evidence": "reports/bootstrap/boot-004-pytest-report.json",
        "capabilities_evidence": "reports/bootstrap/boot-004-capabilities.json (14 implemented-and-tested, 2 planned)",
        "omission_pilot_evidence": {
            "pilot_report": "reports/bootstrap/boot-004-omission-pilot.json",
            "run_summary": "reports/bootstrap/boot-004-run-summary.json",
            "verdict": "pass",
            "detection": "12/12 defects detected",
            "localization": "12/12 localized to expected KU and destination note",
            "false_negatives": 0,
            "false_positives_on_clean_baseline": 0,
            "hard_gate": "PASSED - large-scale synthesis unblocked (AGENTS.md 7.5)",
        },
        "ku_schema_version": "1.1 (ADR-0008)",
        "registry_store": "state/knowledge-units/ (0 records; canonical, committed)",
        "source_immutability": {
            "master_ai": "reports/bootstrap/boot-004-immutable-{before,after}-master-ai.json (0 added/removed/changed)",
            "ai_course": "reports/bootstrap/boot-004-immutable-{before,after}-ai-course.json (0 added/removed/changed)",
        },
    },
    "changed_paths": [
        "src/vault_unification/omission.py",
        "src/vault_unification/cli.py",
        "src/vault_unification/capabilities.py",
        "src/vault_unification/__init__.py",
        "tests/test_omission.py",
        "tests/test_cli.py",
        "tests/test_capabilities.py",
        "docs/FRAMEWORK_SETUP.md",
        "scripts/boot004_pilot.py",
        "scripts/boot004_state_update.py",
        "reports/bootstrap/boot-004-*",
        "state/task-queue.jsonl",
        "state/current-state.json",
        "state/checkpoints/checkpoint-2026-10-26-boot-004.json",
        "docs/agent-handoff/next-agent.md",
    ],
    "next_task": {
        "task_id": "EXT-001",
        "title": "Build the deterministic KU extraction pipeline and extract the first bounded real batch",
        "status": "ready",
        "dependencies": ["BOOT-004"],
    },
    "open_findings": ["F-0001", "F-0002", "F-0003", "F-0004"],
    "explicit_non_claims": [
        "No knowledge units have been extracted from the real vaults; state/knowledge-units/ holds 0 records",
        "No semantic verification of real source content has occurred; the pilot verified the AUDITOR on synthetic data",
        "No synthesis output exists yet; output_synthesis_started is false",
        "Master AI has not been link-checked yet",
    ],
}


def main() -> int:
    with open(REPO_ROOT / "state" / "current-state.json", "w", encoding="utf-8") as handle:
        json.dump(CURRENT_STATE, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    checkpoint_path = REPO_ROOT / "state" / "checkpoints" / "checkpoint-2026-10-26-boot-004.json"
    with open(checkpoint_path, "w", encoding="utf-8") as handle:
        json.dump(CHECKPOINT, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("current-state.json and checkpoint written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
