"""EXT-001: persist verified task state after the first real KU extraction.

Updates (append-only / explicit-value writes, no silent merges):
- state/task-queue.jsonl: EXT-001 -> completed (tests_run evidence, outputs,
  notes incl. the 7-vs-6 scope-count correction); append EXT-002 (ready).
- state/findings.jsonl: append F-0005 (handoff scope-count discrepancy,
  resolved by evidence; recorded so future sessions trust repository
  evidence over handoff prose).
- state/current-state.json: framework v0.4.0 + CAP-016, registry 298 records,
  next task EXT-002.
- state/checkpoints/checkpoint-2026-10-26-ext-001.json: resumable checkpoint.

The work-commit hash is recorded in the follow-up state commit (same pattern
as BOOT-003/BOOT-004).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

TASK_QUEUE = REPO_ROOT / "state" / "task-queue.jsonl"
FINDINGS = REPO_ROOT / "state" / "findings.jsonl"
CURRENT_STATE = REPO_ROOT / "state" / "current-state.json"
CHECKPOINT = REPO_ROOT / "state" / "checkpoints" / "checkpoint-2026-10-26-ext-001.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---- task queue: EXT-001 completed + EXT-002 appended ----
tasks = read_jsonl(TASK_QUEUE)
ext001_tests_run = [
    {
        "command": "PYTHONPATH=src python3 -m pytest tests -q",
        "exit_code": 0,
        "result": "338 passed, 0 failed (285 pre-existing + 46 kuextract + 7 CLI additions incl. the extract-kus help entry)",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification run-tests --tests-dir tests --json-report reports/extraction/ext001-pytest-report.json",
        "exit_code": 0,
        "result": "338/338 passed; machine-readable report written",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification capabilities --verify --report reports/extraction/ext001-capabilities.json",
        "exit_code": 0,
        "result": "15 implemented-and-tested incl. new CAP-016, 2 planned; 323/323 referenced tests passed in the verification run",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification extract-kus --root 'source-vaults/AI /AI Course' --scope '03 - Machine Learning/03.1 - Regression' --vault-id ai-course --manifest state/manifests/ai-course.jsonl --out state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl --unclosed-fence-finding F-0002 --report reports/extraction/ext001-coverage.json",
        "exit_code": 0,
        "result": "6/6 files extracted (0 excluded, 0 failed); 298 KU records; units by type: prose 149, list 62, math_block 50, code_block 23, callout 10, table 3, quote 1; every file line-accounting consistent; batch self-validation valid",
    },
    {
        "command": "determinism check: second extract-kus run to a fresh path, then cmp",
        "exit_code": 0,
        "result": "byte-identical output (sha256 b3ffdf972203cbe804a69e1e3fc8b2f9f1118a8d6c713d79f799ae419831af4a); records contain no timestamps and IDs are content-derived",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification kureg-init --db state/registries/kuregistry.db --force && PYTHONPATH=src python3 -m vault_unification kureg-load --db state/registries/kuregistry.db --kus state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl --report reports/extraction/ext001-kureg-load.json",
        "exit_code": 0,
        "result": "298/298 records inserted, 0 errors, 0 skipped; counts_after_load: 298 Unaccounted",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification kureg-validate --db state/registries/kuregistry.db --report reports/extraction/ext001-kureg-validate.json",
        "exit_code": 0,
        "result": "valid=true; 0 errors; 0 warnings; 298 KUs; unaccounted_count 298 (expected: extraction claims no dispositions); 0 load anomalies",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification verify-manifest both vaults, before AND after extraction",
        "exit_code": 0,
        "result": "4 runs exit 0; 0 added/removed/changed; reports/extraction/ext001-immutable-{before,after}-{master-ai,ai-course}.json",
    },
    {
        "command": "excerpt fidelity check (ad hoc python, recorded in session notes): every record's excerpt vs the exact source line slice",
        "exit_code": 0,
        "result": "298/298 byte-exact excerpts; 298/298 excerpt hashes valid; 298/298 unique KU ids",
    },
    {
        "command": "independent subagent review (EXT-001-REVIEW, read-only)",
        "exit_code": 0,
        "result": "verdict PASS: 10/10 sampled rare details found with KU-id evidence; 100/100 headings present in heading_path; no span crosses a heading; no overlaps or type misclassifications; French diacritics and the oe ligature intact; no mojibake",
    },
]
for task in tasks:
    if task["task_id"] == "EXT-001":
        task["status"] = "completed"
        task["tests_run"] = ext001_tests_run
        task["outputs"] = [
            "src/vault_unification/kuextract.py (CAP-016 module)",
            "src/vault_unification/mdextract.py (extract_structure_text refactor: one shared construct-detection authority)",
            "CLI command: vu extract-kus",
            "tests/test_kuextract.py (46 tests) + tests/test_cli.py additions (7)",
            "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl (first real batch: 298 records)",
            "reports/extraction/ext001-coverage.json (denominators, per-file outcomes, line accounting)",
            "reports/extraction/ext001-pytest-report.json, ext001-capabilities.json",
            "reports/extraction/ext001-kureg-{init,load,validate}.json",
            "reports/extraction/ext001-immutable-{before,after}-{master-ai,ai-course}.json",
            "docs/FRAMEWORK_SETUP.md v0.4.0 (CAP-016 section)",
            "state/knowledge-units/README.md (batch accounting)",
        ]
        task["notes"] = (
            "Completed in continuation session (2026-10-26). Framework-first: new capability "
            "CAP-016 (deterministic KU extraction). SCOPE-COUNT CORRECTION: the BOOT-004 handoff "
            "and task record suggested '7 files' for AI Course 03.1 - Regression; the actual scope "
            "holds 6 files (numbering skips 06; no 06 file exists anywhere in the vault) - recorded "
            "as F-0005. Denominator = 6 actual files, all extracted. Design: structural segmentation "
            "(9 controlled unit types from Markdown block syntax); construct detection delegates to "
            "CAP-003 mdextract via a new extract_structure_text entry point (one authority, no drift); "
            "line-accounting invariant proves every line lands in exactly one bucket (unit span, "
            "heading context, excluded blank, excluded horizontal rule) - the invariant caught and "
            "prevented a real double-count bug during development (frontmatter unit span vs fm bucket). "
            "Extractor claims NO semantics: all 298 records disposition=Unaccounted, no overlap_type, "
            "no concept_ids, no destinations. F-0002 linkage implemented generically "
            "(--unclosed-fence-finding) and exercised in tests; none of the 6 scope files are in the "
            "F-0002 defect set (0 parse warnings in this batch). Independent review PASS (10/10 rare "
            "details incl. the 1/2m trick callout, simultaneous-update example, odds examples, French "
            "random_state=42 explanation; 100/100 headings; 0 boundary anomalies). Framework 0.3.0 -> "
            "0.4.0. Work commit hash to be recorded in the follow-up state commit."
        )
        break
else:
    raise SystemExit("EXT-001 not found in task queue")

ext002 = {
    "task_id": "EXT-002",
    "title": "Extract the paired Master AI regression domain batch (cross-vault evidence for overlap classification)",
    "status": "ready",
    "priority": "critical",
    "dependencies": ["EXT-001"],
    "inputs": [
        "source vaults (read-only): 'source-vaults/AI /Master AI' (333 files)",
        "state/manifests/master-ai.jsonl (baseline hashes)",
        "CAP-016 vu extract-kus (vault-id 'master-ai' - pinned; see FRAMEWORK_SETUP.md)",
        "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl (the AI Course side of the domain)",
    ],
    "outputs": [
        "KU batch under state/knowledge-units/ for the Master AI side of the linear/logistic regression domain (suggested scope: '03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md', 167 lines, 25 headings - the primary paired source per term search: 27 'regression' + 13 'logistic regression' matches; optionally the whole '03 - Machine Learning/Supervised Learning' folder, 2 files / 334 lines)",
        "extraction coverage report with explicit denominators",
        "registry rebuild + kureg-validate accounting evidence",
    ],
    "acceptance_criteria": [
        "Every file in the chosen scope has a verified extraction outcome or an explicit failure/exclusion disposition",
        "KU records validate against schema v1.1; kureg-load succeeds; kureg-validate reports 0 load anomalies",
        "Sources unchanged before/after (vu verify-manifest both vaults)",
        "Determinism: double run byte-identical",
        "No semantic dispositions claimed (all Unaccounted; overlap classification is EXT-003+ evidence-based work)",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not claim semantic preservation or cross-vault overlap from extraction counts",
        "Do not change the pinned vault-id for Master AI ('master-ai')",
    ],
    "findings": ["F-0001", "F-0005"],
}
tasks.append(ext002)
write_jsonl(TASK_QUEUE, tasks)
print(f"task queue updated: {len(tasks)} records (EXT-001 completed, EXT-002 ready)")

# ---- findings: F-0005 ----
findings = read_jsonl(FINDINGS)
f0005 = {
    "finding_id": "F-0005",
    "severity": "low",
    "category": "handoff-accuracy",
    "title": "BOOT-004 handoff and task record stated 7 files for the AI Course 03.1 Regression scope; actual count is 6",
    "affected_paths": [
        "docs/agent-handoff/next-agent.md (BOOT-004 version)",
        "state/task-queue.jsonl (EXT-001 original record)",
    ],
    "observed": "The BOOT-004 handoff suggested 'AI Course 03.1 - Regression, 7 files' and the EXT-001 task record echoed '7 files'. Repository evidence: the directory contains exactly 6 markdown files (01, 02, 03, 04, 05, 07 - numbering skips 06) and state/manifests/ai-course.jsonl holds exactly 6 records with the '03 - Machine Learning/03.1 - Regression/' prefix.",
    "expected_condition": "Handoff counts and denominators must be derived from repository evidence (manifests, inventory), not estimated; a fresh session that trusted the handoff could hunt for a missing 7th file or report a coverage gap.",
    "repair_recommendation": "Use the manifest as the denominator authority (done in EXT-001: denominator 6, 6/6 extracted). Handoffs should quote counts with their source (manifest path + record count).",
    "status": "resolved",
    "discovered_by": "EXT-001 session",
    "evidence": "ls and rg on 'source-vaults/AI /AI Course/03 - Machine Learning/03.1 - Regression/' show 6 .md files; rg '03.1 - Regression' state/manifests/ai-course.jsonl matches 6 records (lines 56-61); reports/extraction/ext001-coverage.json denominators.files_in_scope = 6.",
    "resolution": "EXT-001 extracted against the actual 6-file scope; task record corrected; this finding records the discrepancy so handoff claims remain verifiable.",
}
findings.append(f0005)
write_jsonl(FINDINGS, findings)
print(f"findings updated: {len(findings)} records (F-0005 appended)")

# ---- current-state.json ----
state = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))
state["stage"] = "extraction"
state["framework_foundation_evidence"] = {
    "test_run": "reports/extraction/ext001-pytest-report.json",
    "test_summary": "338 passed, 0 failed, 0 skipped",
    "capabilities": "reports/extraction/ext001-capabilities.json",
    "setup_doc": "docs/FRAMEWORK_SETUP.md",
}
state["knowledge_registry"]["records"] = 298
state["knowledge_registry"]["note"] = (
    "EXT-001 delivered the first real batch "
    "(state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl: 6/6 files from "
    "AI Course 03.1 - Regression, 298 structural KU records, all Unaccounted). "
    "Derived index rebuilt at state/registries/kuregistry.db (kureg-validate clean). "
    "Extraction claims no semantics; overlap/disposition classification is EXT-002+ work."
)
state["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-26-ext-001.json"
state["current_task_id"] = "EXT-002"
state["notes"] = (
    "EXT-001 completed: CAP-016 deterministic KU extraction (vu extract-kus) built, tested "
    "(46 unit + 7 CLI tests) and run on the first real bounded batch - AI Course "
    "'03 - Machine Learning/03.1 - Regression': 6/6 files extracted (handoff said 7; actual 6, "
    "F-0005), 298 KU records, line-accounting invariant consistent for every file, byte-exact "
    "excerpts (298/298), unique content-derived IDs, byte-identical determinism check, batch "
    "schema-valid, registry load 298/298 with 0 anomalies. Independent subagent review PASS "
    "(10/10 rare details, 100/100 headings, 0 boundary anomalies, French intact). Framework "
    "0.3.0 -> 0.4.0; 338/338 tests; capabilities: 15 implemented-and-tested, 2 planned "
    "(CAP-013 duplicates, CAP-014 coverage regression - both become relevant as batches grow). "
    "Sources unchanged before/after. Next: EXT-002 - extract the paired Master AI regression "
    "note (03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md) "
    "with vault-id 'master-ai' to enable evidence-based cross-vault overlap classification."
)
CURRENT_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")

# ---- checkpoint ----
checkpoint = {
    "checkpoint_id": "CHK-2026-10-26-EXT-001",
    "created_utc": "2026-10-26T00:00:00+00:00",
    "stage": "extraction",
    "task_id": "EXT-001",
    "task_status": "completed",
    "last_verified_state": {
        "framework_version": "0.4.0 + CAP-016 (deterministic KU extraction)",
        "test_result": "338 passed, 0 failed, 0 skipped",
        "test_evidence": "reports/extraction/ext001-pytest-report.json",
        "capabilities_evidence": "reports/extraction/ext001-capabilities.json (15 implemented-and-tested, 2 planned)",
        "ku_schema_version": "1.1 (ADR-0008)",
        "registry_store": "state/knowledge-units/ (298 records in 1 committed batch)",
        "derived_index": "state/registries/kuregistry.db (rebuilt; kureg-validate valid, 0 errors/warnings)",
        "first_batch": {
            "path": "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl",
            "sha256": "b3ffdf972203cbe804a69e1e3fc8b2f9f1118a8d6c713d79f799ae419831af4a",
            "files": "6/6 extracted, 0 excluded, 0 failed",
            "records": 298,
            "units_by_type": {"prose": 149, "list": 62, "math_block": 50, "code_block": 23, "callout": 10, "table": 3, "quote": 1},
            "dispositions": {"Unaccounted": 298},
            "coverage_report": "reports/extraction/ext001-coverage.json",
        },
        "independent_review": "EXT-001-REVIEW subagent verdict PASS (10/10 rare details, 100/100 headings, 0 anomalies)",
        "source_immutability": "reports/extraction/ext001-immutable-{before,after}-{master-ai,ai-course}.json (all 0 added/removed/changed)",
        "determinism": "second run byte-identical (cmp + sha256 recorded in tests_run)",
    },
    "changed_paths": [
        "src/vault_unification/kuextract.py",
        "src/vault_unification/mdextract.py",
        "src/vault_unification/cli.py",
        "src/vault_unification/capabilities.py",
        "src/vault_unification/__init__.py",
        "tests/test_kuextract.py",
        "tests/test_cli.py",
        "docs/FRAMEWORK_SETUP.md",
        "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl",
        "state/knowledge-units/README.md",
        "state/task-queue.jsonl",
        "state/current-state.json",
        "state/findings.jsonl",
        "state/checkpoints/checkpoint-2026-10-26-ext-001.json",
        "reports/extraction/ext001-*",
        "docs/agent-handoff/next-agent.md",
    ],
    "next_task": {
        "task_id": "EXT-002",
        "title": "Extract the paired Master AI regression domain batch",
        "status": "ready",
        "dependencies": ["EXT-001"],
    },
    "open_findings": ["F-0001", "F-0002", "F-0003", "F-0004", "F-0005"],
    "explicit_non_claims": [
        "The 298 extracted records have no dispositions, overlap classifications, concepts or destinations; semantic work has not started",
        "Only 6 of 609 source files have been extracted (1.0%); extraction coverage is NOT semantic preservation",
        "No synthesis output exists; output_synthesis_started is false",
        "CAP-013 (duplicate discovery) and CAP-014 (coverage/frequency regression) remain planned",
    ],
}
CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"checkpoint written: {CHECKPOINT}")
