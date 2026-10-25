"""EXT-002: persist verified task state after the second real KU extraction.

Updates (append-only / explicit-value writes, no silent merges):
- state/task-queue.jsonl: EXT-002 -> completed (tests_run evidence, outputs,
  notes); append EXT-003 (ready).
- state/findings.jsonl: append F-0006 (keyword false-positive hazard for
  cross-vault overlap classification, surfaced by the EXT-002 review).
- state/current-state.json: registry 363 records in 2 batches, next task
  EXT-003.
- state/checkpoints/checkpoint-2026-10-26-ext-002.json: resumable checkpoint.

The work-commit hash is recorded in the follow-up state commit (same pattern
as BOOT-003/BOOT-004/EXT-001).
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
CHECKPOINT = REPO_ROOT / "state" / "checkpoints" / "checkpoint-2026-10-26-ext-002.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


WORK_COMMIT_PLACEHOLDER = "<WORK_COMMIT>"

TESTS_RUN = [
    {
        "command": "PYTHONPATH=src python3 -m pytest tests -q (session startup verification)",
        "exit_code": 0,
        "result": "338 passed, 0 failed — matches the EXT-001 handoff claim before any EXT-002 work",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification selftest",
        "exit_code": 0,
        "result": "ok=true; mandatory checks passed (startup verification)",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification extract-kus --root 'source-vaults/AI /Master AI' --scope '03 - Machine Learning/Supervised Learning' --vault-id master-ai --manifest state/manifests/master-ai.jsonl --out state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl --report reports/extraction/ext002-coverage.json",
        "exit_code": 0,
        "result": "2/2 files extracted (0 excluded, 0 failed); 65 KU records; units by type: prose 31, list 16, math_block 10, code_block 3, frontmatter 2, callout 2, table 1; line accounting consistent for both files (167/167 each); batch self-validation valid",
    },
    {
        "command": "determinism check: second extract-kus run to a fresh path, then cmp",
        "exit_code": 0,
        "result": "byte-identical output (sha256 e0ef12187b3792dbdc9e2868a31ff7a77f57eb4809fc3ad09aab6663d5871118); evidence reports/extraction/ext002-determinism.json",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification kureg-init --db state/registries/kuregistry.db --force && kureg-load batch 001 && kureg-load batch 002",
        "exit_code": 0,
        "result": "298 + 65 = 363 records inserted, 0 errors, 0 skipped; reports/extraction/ext002-kureg-{init,load-batch1,load-batch2}.json",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification kureg-validate --db state/registries/kuregistry.db --report reports/extraction/ext002-kureg-validate.json",
        "exit_code": 0,
        "result": "valid=true; 0 errors; 0 warnings; 363 KUs; unaccounted_count 363 (expected: extraction claims no dispositions)",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification verify-manifest both vaults, before AND after extraction",
        "exit_code": 0,
        "result": "4 runs exit 0; 0 added/removed/changed (333 master-ai + 276 ai-course unchanged); reports/extraction/ext002-immutable-{before,after}-{master-ai,ai-course}.json",
    },
    {
        "command": "python3 scripts/ext002_fidelity.py",
        "exit_code": 0,
        "result": "65/65 byte-exact excerpts; 65/65 excerpt hashes valid; 65 unique IDs; vault-id master-ai on every record; source hashes agree with baseline manifest; no unit span crosses a real heading (heading detection delegated to mdextract.extract_structure_text — a naive '#' matcher false-positives on Python comments inside code fences)",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification run-tests --tests-dir tests --json-report reports/extraction/ext002-pytest-report.json",
        "exit_code": 0,
        "result": "338/338 passed; no framework changes made in EXT-002 (existing CAP-016 consumed as-is)",
    },
    {
        "command": "PYTHONPATH=src python3 -m vault_unification capabilities --verify --report reports/extraction/ext002-capabilities.json",
        "exit_code": 0,
        "result": "15 implemented-and-tested, 2 planned (CAP-013, CAP-014) — unchanged from EXT-001, as expected",
    },
    {
        "command": "independent review by EXT-002-REVIEW subagent (read-only; report reports/extraction/ext002-review.md)",
        "exit_code": 0,
        "result": "verdict PASS: 32/32 rare details present with KU-id evidence (16 per source file), 40/40 headings covered (22 + 18, counted via mdextract), 0 boundary anomalies (0 span overlaps, 0 heading crossings, 0 type misclassifications; line accounting independently reproduced 93+22+52=167 and 105+18+44=167), 65/65 records structurally pure (disposition Unaccounted, no overlap_type, master-ai prefix, verification_status pending), in-memory re-run of kuextract.segment_note reproduces all 65 units exactly, 7 factual cross-vault topic pairs listed with one KU-id per side; two forward-looking cautions -> F-0006 and EXT-003 method notes",
    },
    {
        "command": "orchestrator spot-check of EXT-002-REVIEW evidence (protocol: subagent results reviewed before acceptance)",
        "exit_code": 0,
        "result": "4/4 sampled KU-ids verified real with claimed content (ridge closed form KU-d45e836332e307c8, sklearn C=1/lambda KU-0b46cce8095bdcf5, SOTA-2026 callout KU-5c20f9686292a5bb, comparison table KU-af74852cfc1d5771); cross-vault softmax pair confirmed (master-ai formula KU-74814e20d567d124 vs ai-course activation='softmax' usage KU-d758cb4d3ebb7e4d)",
    },
]


def update_task_queue(work_commit: str) -> None:
    records = read_jsonl(TASK_QUEUE)
    for record in records:
        if record["task_id"] == "EXT-002":
            record["status"] = "completed"
            record["outputs"] = [
                "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl (65 KU records; scope decision: whole '03 - Machine Learning/Supervised Learning' folder, 2 files / 334 lines — the task record's optional wider scope, chosen so the tree-based file also receives its verified outcome now; the primary regression pairing is '02 - Linear and Logistic Regression.md')",
                "reports/extraction/ext002-coverage.json (2/2 files extracted, 0 excluded, 0 failed; line accounting 167/167 per file)",
                "reports/extraction/ext002-determinism.json (double run byte-identical)",
                "reports/extraction/ext002-kureg-{init,load-batch1,load-batch2,validate}.json (363 KUs total, 0 anomalies)",
                "reports/extraction/ext002-immutable-{before,after}-{master-ai,ai-course}.json (sources unchanged)",
                "reports/extraction/ext002-fidelity.json (65/65 byte-exact excerpts, unique IDs, manifest hash agreement)",
                "reports/extraction/ext002-pytest-report.json (338/338), ext002-capabilities.json (15+2)",
                "reports/extraction/ext002-review.md (independent EXT-002-REVIEW verdict PASS)",
                "scripts/ext002_fidelity.py (reusable fidelity check for this batch)",
            ]
            record["tests_run"] = TESTS_RUN
            record["findings"] = ["F-0001", "F-0005", "F-0006"]
            # NOTE: the schema-legal field is 'commit' (task.schema.json); an
            # early draft of this script wrote 'work_commit' and
            # validate-registry rejected it — fixed before the work commit.
            record["commit"] = work_commit
            record["notes"] = (
                "EXT-002 consumed existing CAP-016 without framework changes (test count stays 338/338). "
                "Scope: whole 'Supervised Learning' folder (2 files) — explicitly permitted by this task record; "
                "both files received verified outcomes, no half-extracted folder left behind. The regression "
                "pairing for EXT-003 is '02 - Linear and Logistic Regression.md' (35 KUs); the second file "
                "'03 - Decision Trees and Gradient Boosting.md' (30 KUs) pairs with AI Course 03.7 - Tree-Based "
                "Models for a later batch. Independent review: 32/32 rare details, 40/40 headings, 0 anomalies, "
                "65/65 structurally pure, in-memory extractor re-run reproduces the batch exactly. Cross-vault "
                "observation (evidence for EXT-003, not a classification): 7 topic pairs with KU-ids on both "
                "sides — MSE, normal equations, gradient descent, logistic sigmoid, binary cross-entropy, "
                "softmax, sklearn usage; Master-AI-only so far: ridge/L2, lasso/L1, MAP/prior interpretations, "
                "calibration/temperature scaling, O(d^3) caveat. See F-0006 for the keyword false-positive "
                "hazard before any term-matching overlap tooling."
            )
        if record["task_id"] == "EXT-003" and record.get("status") == "queued":
            record["status"] = "ready"
    if not any(r["task_id"] == "EXT-003" for r in records):
        records.append(
            {
                "task_id": "EXT-003",
                "title": "Build CAP-013 cross-vault candidate discovery and classify overlap for the regression domain (evidence-based)",
                "status": "ready",
                "priority": "critical",
                "dependencies": ["EXT-002"],
                "inputs": [
                    "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl (298 KUs, ai-course side)",
                    "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl (65 KUs, master-ai side; regression file = 35 KUs)",
                    "reports/extraction/ext002-review.md (7 evidenced cross-vault topic pairs — starting hypotheses, NOT classifications)",
                    "state/findings.jsonl F-0006 (keyword false-positive hazard: word-boundary matching + excerpt-level confirmation required)",
                    "schemas/knowledge-unit.schema.json (overlap_type + superseded_rationale fields, v1.1)",
                ],
                "outputs": [
                    "new framework capability CAP-013 (duplicate/near-duplicate/related-content candidate discovery) with word-boundary term matching, machine-readable candidate pairs, unit tests, CLI, docs",
                    "evidence-based overlap_type assignments (Exact Duplicate / Semantic Duplicate / Partial Overlap / Complementary Content / Conflict or Historical Difference) for the regression-domain KU pairs, recorded as new classification records or registry updates — NOT by editing committed batches",
                    "updated dispositions where evidence justifies (dispositions remain separate from overlap_type per docs/KNOWLEDGE_AND_PROVENANCE.md section 7)",
                ],
                "acceptance_criteria": [
                    "CAP-013 implemented and tested (normal, boundary, malformed inputs; word-boundary matching verified against the F-0006 false-positive cases: 'bridge' must not match 'ridge'; mermaid L1[...] node labels must not match L1 regularization without excerpt confirmation)",
                    "every candidate pair carries evidence (matched terms/aliases with positions, excerpt references) — no semantic claims from counts alone",
                    "overlap classification decisions are recorded with rationale and remain reversible/reviewable",
                    "existing batches are not edited (append-only); registry cross-checks pass; full test suite passes",
                    "sources unchanged before/after",
                ],
                "forbidden_side_effects": [
                    "Do not modify source vaults",
                    "Do not edit committed KU batches",
                    "Do not collapse overlap_type into disposition",
                    "Do not assign dispositions/overlap without recorded evidence",
                ],
                "findings": ["F-0006"],
            }
        )
    write_jsonl(TASK_QUEUE, records)


def append_finding() -> None:
    records = read_jsonl(FINDINGS)
    if any(r["finding_id"] == "F-0006" for r in records):
        return
    records.append(
        {
            "finding_id": "F-0006",
            "severity": "medium",
            "category": "tooling-hazard",
            "title": "Naive substring term matching produces false positives that would corrupt cross-vault overlap classification (EXT-003+)",
            "affected_paths": [
                "future CAP-013 candidate discovery",
                "any term-based overlap or frequency tooling",
            ],
            "observed": "EXT-002-REVIEW confirmed: substring search for 'ridge' matches 'b' + 'ridge' in AI Course text (English word 'bridge'), and searches for 'L1'/'L2' match mermaid diagram node labels like 'L1[...]'/'L2[...]' in the AI Course regression batch. A naive grep-based candidate discovery would therefore report spurious ridge/lasso coverage in the AI Course vault (the review verified the course batch contains ZERO genuine ridge/lasso/regularization content).",
            "expected_condition": "Overlap candidate discovery (CAP-013) and any term-frequency tooling must use word-boundary-aware matching (with alias lists) AND excerpt-level human/LLM confirmation before recording any overlap classification; substring counts must never be presented as semantic evidence.",
            "repair_recommendation": "Implement CAP-013 with word-boundary regex matching + alias support + excerpt-context capture; add regression tests using the exact false-positive cases ('bridge' vs 'ridge', mermaid 'L1['/'L2[' nodes, code-fence interiors excluded or flagged separately).",
            "status": "open",
            "discovered_by": "EXT-002-REVIEW (independent review subagent), confirmed by orchestrator",
            "evidence": "reports/extraction/ext002-review.md (Check 5 cautions); state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl (mermaid + 'bridge' content)",
            "resolution": "",
        }
    )
    write_jsonl(FINDINGS, records)


def update_current_state() -> None:
    state = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))
    state["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-26-ext-002.json"
    state["current_task_id"] = "EXT-003"
    state["knowledge_registry"]["records"] = 363
    state["knowledge_registry"]["note"] = (
        "EXT-001 + EXT-002 delivered 2 committed batches (363 structural KU records, all Unaccounted): "
        "001-ext001-ai-course-03.1-regression.jsonl (298 KUs, 6 files) + "
        "002-ext002-master-ai-supervised-learning.jsonl (65 KUs, 2 files incl. the regression pairing file). "
        "Derived index rebuilt at state/registries/kuregistry.db (kureg-validate clean, 0 warnings). "
        "Extraction claims no semantics; overlap/disposition classification (EXT-003) requires CAP-013 with "
        "word-boundary matching per F-0006."
    )
    state["notes"] = (
        "EXT-002 completed: extracted the whole Master AI '03 - Machine Learning/Supervised Learning' folder "
        "(2/2 files, 65 KUs; regression pairing file '02 - Linear and Logistic Regression.md' = 35 KUs, "
        "decision-trees file = 30 KUs for a later AI-Course-03.7 pairing). Consumed existing CAP-016 "
        "(no framework changes; 338/338 tests). Byte-identical determinism; line accounting 167/167 per file; "
        "65/65 byte-exact excerpts + manifest-hash agreement (scripts/ext002_fidelity.py); registry 363 KUs, "
        "0 anomalies; sources unchanged before/after. Independent EXT-002-REVIEW verdict PASS (32/32 rare "
        "details, 40/40 headings, 0 boundary anomalies, 65/65 structurally pure, in-memory extractor re-run "
        "reproduces the batch exactly); orchestrator spot-checked the review evidence. New finding F-0006 "
        "(open): naive substring matching false-positives ('bridge'->'ridge', mermaid L1[/L2[ labels) — "
        "CAP-013 must use word-boundary matching + excerpt confirmation. Next: EXT-003 — build CAP-013 and "
        "classify overlap for the regression domain from the 7 evidenced topic-pair hypotheses in "
        "reports/extraction/ext002-review.md (hypotheses, not classifications)."
    )
    CURRENT_STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def write_checkpoint(work_commit: str) -> None:
    checkpoint = {
        "checkpoint_id": "CHK-2026-10-26-EXT-002",
        "created_utc": "2026-10-25T22:20:00+00:00",
        "stage": "extraction",
        "task_id": "EXT-002",
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.4.0 (unchanged; EXT-002 consumed CAP-016 as-is)",
            "test_result": "338 passed, 0 failed, 0 skipped",
            "test_evidence": "reports/extraction/ext002-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext002-capabilities.json (15 implemented-and-tested, 2 planned)",
            "ku_schema_version": "1.1 (ADR-0008)",
            "registry_store": "state/knowledge-units/ (363 records in 2 committed batches)",
            "derived_index": "state/registries/kuregistry.db (rebuilt with both batches; kureg-validate valid, 0 errors/warnings)",
            "second_batch": {
                "path": "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
                "sha256": "e0ef12187b3792dbdc9e2868a31ff7a77f57eb4809fc3ad09aab6663d5871118",
                "files": "2/2 extracted, 0 excluded, 0 failed",
                "records": 65,
                "units_by_type": {
                    "prose": 31,
                    "list": 16,
                    "math_block": 10,
                    "code_block": 3,
                    "frontmatter": 2,
                    "callout": 2,
                    "table": 1,
                },
                "dispositions": {"Unaccounted": 65},
                "coverage_report": "reports/extraction/ext002-coverage.json",
            },
            "independent_review": "EXT-002-REVIEW subagent verdict PASS (32/32 rare details, 40/40 headings, 0 anomalies, 65/65 pure); orchestrator spot-check confirmed sampled evidence",
            "source_immutability": "reports/extraction/ext002-immutable-{before,after}-{master-ai,ai-course}.json (all 0 added/removed/changed)",
            "determinism": "second run byte-identical (cmp exit 0; sha256 in reports/extraction/ext002-determinism.json)",
            "work_commit": work_commit,
        },
        "changed_paths": [
            "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
            "state/knowledge-units/README.md",
            "state/task-queue.jsonl",
            "state/current-state.json",
            "state/findings.jsonl",
            "state/checkpoints/checkpoint-2026-10-26-ext-002.json",
            "reports/extraction/ext002-*",
            "scripts/ext002_fidelity.py",
            "docs/agent-handoff/next-agent.md",
        ],
        "next_task": {
            "task_id": "EXT-003",
            "title": "Build CAP-013 cross-vault candidate discovery and classify overlap for the regression domain",
            "status": "ready",
            "dependencies": ["EXT-002"],
        },
        "open_findings": ["F-0001", "F-0002", "F-0003", "F-0006"],
        "explicit_non_claims": [
            "The 363 extracted records have no dispositions, overlap classifications, concepts or destinations; semantic work has not started",
            "Only 8 of 609 source files have been extracted (1.3%); extraction coverage is NOT semantic preservation",
            "The 7 cross-vault topic pairs in reports/extraction/ext002-review.md are observational hypotheses with KU-id evidence, NOT overlap classifications",
            "No synthesis output exists; output_synthesis_started is false",
            "CAP-013 (duplicate discovery) and CAP-014 (coverage/frequency regression) remain planned",
        ],
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    work_commit = sys.argv[1] if len(sys.argv) > 1 else WORK_COMMIT_PLACEHOLDER
    update_task_queue(work_commit)
    append_finding()
    update_current_state()
    write_checkpoint(work_commit)
    print("state updated: task-queue (EXT-002 completed, EXT-003 ready), findings (+F-0006), current-state, checkpoint")
    if work_commit == WORK_COMMIT_PLACEHOLDER:
        print("NOTE: work commit hash is a placeholder — record the real hash in the state commit (same pattern as EXT-001)")


if __name__ == "__main__":
    main()
