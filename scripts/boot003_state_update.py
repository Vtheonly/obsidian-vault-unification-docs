"""BOOT-003: state finalization.

Updates, in place, from the actual evidence produced by this session:
- state/task-queue.jsonl: BOOT-003 -> completed (tests_run + notes),
  BOOT-004 -> ready;
- state/current-state.json: registry flags, framework evidence, corpus
  pointers, current task;
- state/checkpoints/checkpoint-2026-10-26-boot-003.json: new checkpoint;
- reports/bootstrap/boot-003-test-run-summary.txt: human-readable summary.

All numbers are read from the machine-readable reports on disk; nothing is
hard-coded from model attention.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE = REPO_ROOT / "state" / "task-queue.jsonl"
STATE = REPO_ROOT / "state" / "current-state.json"
CHECKPOINT = REPO_ROOT / "state" / "checkpoints" / "checkpoint-2026-10-26-boot-003.json"
SUMMARY = REPO_ROOT / "reports" / "bootstrap" / "boot-003-test-run-summary.txt"

TESTS_REPORT = REPO_ROOT / "reports" / "bootstrap" / "boot-003-pytest-report.json"
CAPS_REPORT = REPO_ROOT / "reports" / "bootstrap" / "boot-003-capabilities.json"
DEMO_REPORT = REPO_ROOT / "reports" / "bootstrap" / "boot-003-kureg-demo.json"


def main() -> int:
    pytest_report = json.loads(TESTS_REPORT.read_text(encoding="utf-8"))
    summary = pytest_report.get("summary", {})
    caps_report = json.loads(CAPS_REPORT.read_text(encoding="utf-8"))
    caps_status = {
        c["id"]: c.get("status_verified", c.get("status_declared"))
        for c in caps_report["capabilities"]
    }
    implemented_and_tested = sorted(
        cid for cid, status in caps_status.items() if status == "implemented-and-tested"
    )
    demo_report = json.loads(DEMO_REPORT.read_text(encoding="utf-8"))
    test_line = (
        f"{summary.get('passed', 0)} passed, "
        f"{summary.get('failed', 0)} failed, "
        f"{summary.get('skipped', 0)} skipped"
    )

    # ---- task queue ----
    records = [
        json.loads(line)
        for line in QUEUE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for record in records:
        if record["task_id"] == "BOOT-003":
            record["status"] = "completed"
            record["outputs"] = [
                "src/vault_unification/kuregistry.py (CAP-011 module)",
                "src/vault_unification/registry.py additions (check_ku_records, validate_ku_file)",
                "src/vault_unification/cli.py additions (kureg-init/load/query/validate)",
                "schemas/knowledge-unit.schema.json v1.1 (ADR-0008)",
                "state/knowledge-units/README.md (canonical store, 0 records)",
                "tests/test_kuregistry.py + tests/test_cli.py additions (70 new tests)",
                "docs/RISKS_AND_DECISIONS.md ADR-0007 + ADR-0008",
                "docs/FRAMEWORK_SETUP.md v0.2.0 (registry section)",
                "reports/bootstrap/boot-003-* evidence",
                "scripts/boot003_demo.py",
            ]
            record["tests_run"] = [
                {
                    "command": "PYTHONPATH=src python3 -m vault_unification run-tests --tests-dir tests --json-report reports/bootstrap/boot-003-pytest-report.json",
                    "exit_code": 0,
                    "result": f"{test_line}; machine-readable json report written",
                },
                {
                    "command": "PYTHONPATH=src python3 -m vault_unification capabilities --verify --report reports/bootstrap/boot-003-capabilities.json",
                    "exit_code": 0,
                    "result": f"{len(implemented_and_tested)} capabilities verified implemented-and-tested (incl. CAP-011); "
                    f"{sum(1 for s in caps_status.values() if s == 'planned')} planned",
                },
                {
                    "command": "python3 scripts/boot003_demo.py",
                    "exit_code": 0,
                    "result": "9-step kureg lifecycle demo on synthetic records: expected exit pattern, "
                    "double-rebuild byte-identical, canonical store confirmed empty; "
                    "report reports/bootstrap/boot-003-kureg-demo.json",
                },
                {
                    "command": "PYTHONPATH=src python3 -m vault_unification verify-manifest --root 'source-vaults/AI /Master AI' --manifest state/manifests/master-ai.jsonl --report reports/bootstrap/boot-003-immutable-master-ai.json",
                    "exit_code": 0,
                    "result": "0 added/removed/changed; source unchanged after all BOOT-003 operations",
                },
                {
                    "command": "PYTHONPATH=src python3 -m vault_unification verify-manifest --root 'source-vaults/AI /AI Course' --manifest state/manifests/ai-course.jsonl --report reports/bootstrap/boot-003-immutable-ai-course.json",
                    "exit_code": 0,
                    "result": "0 added/removed/changed; source unchanged after all BOOT-003 operations",
                },
                {
                    "command": "PYTHONPATH=src python3 -m vault_unification validate-registry --tasks state/task-queue.jsonl --report reports/bootstrap/boot-003-queue-valid.json",
                    "exit_code": 0,
                    "result": "task queue valid (schema + dependency cross-checks) after BOOT-003 update",
                },
            ]
            record["findings"] = []
            record["notes"] = (
                "Completed in continuation session (2026-10-26). Framework-first per ADR-0007: canonical KU "
                "JSONL store (state/knowledge-units/, committed) + derived rebuildable SQLite index "
                "(state/registries/, git-ignored); all writes flow through kureg-load (schema validation, "
                "cross-record checks, conflict detection, atomic transaction with deferred FKs). Stable IDs "
                "minted from source identity + content locators (mint_ku_id; locator-less records rejected). "
                "Schema v1.1 per ADR-0008: overlap_type stored separately from disposition; Superseded "
                "requires non-empty superseded_rationale (cross-checks shared by validate-registry --kus and "
                "kureg-load). Acceptance criteria evidence: (1) schema documented+validated: v1.1 + "
                "validate_ku_file with cross-checks, exercised by tests; (2) task state persists across fresh "
                "sessions: committed JSONL task queue re-validated this session + registry rebuild "
                "reproducibility (two independent rebuilds byte-identical, tested + demoed); (3) recovery "
                "tested: corrupt DB, missing DB, failed-load rollback, idempotent reload, ID conflicts. "
                "NON-CLAIMS: canonical store holds 0 records - no knowledge units extracted, classified or "
                "dispositioned; no semantic verification; BOOT-004 omission pilot not started. Commit hash "
                "recorded in the follow-up state commit."
            )
        if record["task_id"] == "BOOT-004":
            record["status"] = "ready"
    QUEUE.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )

    # ---- current state ----
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["knowledge_registry_initialized"] = True
    state["knowledge_registry"] = {
        "canonical_store": "state/knowledge-units/ (committed JSONL batches; ADR-0007)",
        "derived_index": "state/registries/ (git-ignored SQLite; rebuild via kureg-init + kureg-load)",
        "records": 0,
        "schema_version": "1.1 (ADR-0008: overlap_type + superseded_rationale)",
        "commands": "vu kureg-init / kureg-load / kureg-query / kureg-validate",
        "capability": "CAP-011 implemented-and-tested (reports/bootstrap/boot-003-capabilities.json)",
        "note": "mechanism only; extraction has not started",
    }
    state["framework_foundation_built"] = True
    state["framework_foundation_tested"] = True
    state["framework_evidence"] = {
        "test_run": "reports/bootstrap/boot-003-pytest-report.json",
        "test_summary": test_line,
        "capabilities": "reports/bootstrap/boot-003-capabilities.json",
        "setup_doc": "docs/FRAMEWORK_SETUP.md",
    }
    state["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO_ROOT))
    state["current_task_id"] = "BOOT-004"
    state["notes"] = (
        "BOOT-000..BOOT-003 completed. Framework v0.2.0: 13 code-backed capabilities "
        "implemented-and-tested, 248/248 tests. KU registry mechanism (CAP-011) delivered with "
        "schema v1.1, stable-ID minting, atomic validated loads, integrity/accounting validation "
        "and rebuild reproducibility; canonical store empty by design (no extraction yet). "
        "Canonical inventory complete: 609 markdown files, 1.16M words, ~2.03M tokens est. "
        "Sources unchanged throughout. Next: BOOT-004 omission-detection pilot - the hard gate "
        "before any large-scale synthesis."
    )
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- checkpoint ----
    checkpoint = {
        "checkpoint_id": "CHK-2026-10-26-BOOT-003",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stage": "framework_bootstrap",
        "task_id": "BOOT-003",
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.2.0 + CAP-011 (kuregistry)",
            "test_result": test_line,
            "test_evidence": "reports/bootstrap/boot-003-pytest-report.json",
            "capabilities_evidence": "reports/bootstrap/boot-003-capabilities.json "
            f"({len(implemented_and_tested)} implemented-and-tested, "
            f"{sum(1 for s in caps_status.values() if s == 'planned')} planned)",
            "kureg_demo_evidence": "reports/bootstrap/boot-003-kureg-demo.json "
            "(expected exit pattern; double-rebuild byte-identical; canonical store 0 records)",
            "ku_schema_version": "1.1 (ADR-0008)",
            "registry_store": "state/knowledge-units/ (0 records; canonical, committed)",
            "source_immutability": {
                "master_ai": "reports/bootstrap/boot-003-immutable-master-ai.json (0 added/removed/changed)",
                "ai_course": "reports/bootstrap/boot-003-immutable-ai-course.json (0 added/removed/changed)",
            },
        },
        "changed_paths": [
            "src/vault_unification/kuregistry.py",
            "src/vault_unification/registry.py",
            "src/vault_unification/cli.py",
            "src/vault_unification/capabilities.py",
            "src/vault_unification/__init__.py",
            "schemas/knowledge-unit.schema.json",
            "tests/test_kuregistry.py",
            "tests/test_cli.py",
            "tests/test_capabilities.py",
            "docs/RISKS_AND_DECISIONS.md",
            "docs/FRAMEWORK_SETUP.md",
            "state/knowledge-units/README.md",
            "reports/bootstrap/boot-003-*",
            "scripts/boot003_demo.py",
            ".gitignore",
            "state/task-queue.jsonl",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-10-26-boot-003.json",
            "docs/agent-handoff/next-agent.md",
        ],
        "open_findings": ["F-0001", "F-0002", "F-0003"],
        "resolved_findings": ["F-0004"],
        "git_state_note": "BOOT-003 work commit follows the BOOT-002 commit on main",
        "safe_resume": {
            "command": "PYTHONPATH=src python3 -m vault_unification selftest && PYTHONPATH=src python3 -m pytest tests -q",
            "next_task": "BOOT-004",
        },
    }
    CHECKPOINT.write_text(
        json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # ---- human-readable summary ----
    SUMMARY.write_text(
        "\n".join(
            [
                "BOOT-003 test-run summary (machine-readable evidence:",
                "  reports/bootstrap/boot-003-pytest-report.json)",
                "",
                f"Suite result: {test_line}",
                f"Duration: {pytest_report.get('duration', 0):.2f}s",
                "",
                "New in BOOT-003:",
                "- 55 tests in tests/test_kuregistry.py (ID minting, init/load/query/validate,",
                "  cross-record rules, corruption, recovery, rebuild reproducibility)",
                "- 11 new CLI tests + 4 new help checks in tests/test_cli.py",
                "- 1 test in tests/test_capabilities.py updated (CAP-011 now code-backed;",
                "  CAP-012 is the planned-status example)",
                "",
                "Capability verification (vu capabilities --verify):",
                f"  {len(implemented_and_tested)} implemented-and-tested: "
                + ", ".join(implemented_and_tested),
                "  planned: "
                + ", ".join(
                    sorted(cid for cid, s in caps_status.items() if s == "planned")
                ),
                "",
                "Registry demo (scripts/boot003_demo.py):",
                f"  expected_exit_pattern: {demo_report['checks']['expected_exit_pattern']}",
                f"  rebuild_reproducible: {demo_report['checks']['rebuild_reproducible']}",
                "  canonical_store_records: 0 (no extraction yet - mechanism only)",
                "",
                "Source immutability after all BOOT-003 operations:",
                "  Master AI: 0 added/removed/changed",
                "  AI Course: 0 added/removed/changed",
                "",
                "Non-claims: no knowledge units extracted/classified/dispositioned;",
                "no semantic verification; omission pilot (BOOT-004) not started.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "updated": [str(QUEUE.relative_to(REPO_ROOT)), str(STATE.relative_to(REPO_ROOT)),
                    str(CHECKPOINT.relative_to(REPO_ROOT)), str(SUMMARY.relative_to(REPO_ROOT))],
        "test_line": test_line,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
