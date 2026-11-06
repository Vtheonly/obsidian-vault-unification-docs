#!/usr/bin/env python3
"""VERIF-001 registration: append the task to state/task-queue.jsonl,
refresh state/current-state.json, validate the queue against the schema."""
import json
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"

task = {
    "task_id": "VERIF-001",
    "title": "Post-delivery stratified semantic spot-verification of the unified vault",
    "status": "in_progress",
    "priority": "high",
    "dependencies": ["SYNTH-001"],
    "inputs": [
        "state/synthesis/s29-semantic-sample.jsonl (246 stratified KUs, deterministic)",
        "state/dispositions/001-disp001-rule-driven.jsonl (destinations + rationales)",
        "state/knowledge-units/*.jsonl (verbatim excerpts, byte-faithful)",
        "output/Unified-Vault/ (544 delivered notes, read-only during judging)",
        "reports/release/final-report.md (§5.1 limitation #1 being addressed)",
    ],
    "outputs": [
        "reports/synthesis/s29-semantic-judgments.jsonl (per-KU verdicts with verbatim destination evidence)",
        "reports/synthesis/s29-semantic-campaign.json (aggregate result with denominators)",
        "findings ledger entries for any partial/absent verdicts (stable IDs)",
        "task-queue/checkpoint/handoff updates",
    ],
    "acceptance_criteria": [
        "every one of the 246 sampled KUs receives exactly one judgment with a verdict from {present, partial, absent, superseded-info-retained}",
        "every judgment's destination evidence quotes are mechanically verified to appear verbatim in the cited destination note file",
        "the orchestrator independently re-reviews a subset of at least 25 judgments (>=10%) and records agreement/disagreement",
        "any partial/absent verdict becomes a findings-ledger entry with KU id, severity, source excerpt, destination note, and evidence",
        "aggregates report numerator/denominator per disposition, unit_type, and area, with the sampling method and its limitations stated",
        "no source-vault mutation; any output-vault repair goes through the sanctioned repair machinery with tests re-run after the last mutation",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not modify output notes during the judgment phase (read-only)",
        "Do not present spot-check coverage as full per-unit semantic proof (final-report §5.1 remains the honest boundary)",
        "Do not weaken the marker/audit machinery or its tests",
    ],
    "findings": [],
    "notes": ("Session 29 continuation work. The delivered vault (s28, 544/544) passed all "
              "release gates; s29 independently reproduced the full-corpus audit, registry "
              "rebuild, link check, lint, and 752/752 tests before starting this campaign. "
              "This task deepens evidence class 'units semantically validated' "
              "(VERIFICATION_SPECIFICATION.md Metrics) beyond the per-area generation reviews "
              "and spot audits performed during SYNTH-001."),
    "commit": None,
}

with QUEUE.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(task, ensure_ascii=False) + "\n")

# refresh current-state.json (minimal, accurate)
state = json.loads(STATE.read_text(encoding="utf-8"))
state["current_task_id"] = "VERIF-001"
state["stage"] = "post-delivery-verification"
state["notes"] = ("Vault delivered at session 28 (544/544 notes, all gates green; "
                  "reports/release/final-report.md). Session 29 independently reproduced the "
                  "final full-corpus audit (0 findings, 42,156 markers), registry rebuild "
                  "(Unaccounted=0), links (0 problems), lint (0 errors), and 752/752 tests, "
                  "then opened VERIF-001: stratified semantic spot-verification of 246 KUs "
                  "(state/synthesis/s29-semantic-sample.jsonl).")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")

# validate the queue against the schema (the suite enforces this too)
sys.path.insert(0, str(REPO / "src"))
from vault_unification import registry as reg  # noqa: E402

report = reg.validate_task_queue(QUEUE, REPO / "schemas/task.schema.json")
print("task queue valid:", report["valid"])
if report["errors"]:
    print(json.dumps(report["errors"], indent=1))
    sys.exit(1)
print("cross-checks:", report["cross_checks"]["status"])
print("VERIF-001 registered; current-state refreshed")
