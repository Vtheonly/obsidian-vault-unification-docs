#!/usr/bin/env python3
"""Session-31 (INTEG campaign setup) state closeout.

Registers INTEG-001 (completed, this session) and INTEG-002 (queued, next
session per campaign plan S32) in the task queue with schema validation,
updates state/current-state.json, and writes the session-31 checkpoint with
the mandatory accelerated_mode block.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from vault_unification import registry as reg  # noqa: E402

QUEUE = REPO / "state" / "task-queue.jsonl"
SCHEMA = json.loads((REPO / "schemas" / "task.schema.json").read_text())
CURRENT = REPO / "state" / "current-state.json"
CHECKPOINT = REPO / "state" / "checkpoints" / "checkpoint-2026-11-06-integ-session31.json"

INTEG_001 = {
    "task_id": "INTEG-001",
    "title": "Integration campaign setup: methodology, deterministic inventory parse, lexical coverage mechanism + first report (S31 of 15)",
    "status": "completed",
    "priority": "high",
    "dependencies": ["VERIF-002"],
    "inputs": [
        "index of the missing things.txt (user commit 77cf6cf; immutable input)",
        "commit message of 77cf6cf (authoritative methodology directive: audit-first, A/B/C/D strategies, 100% coverage hard gate, project-context authority, depth template)",
        "output/Unified-Vault/ (544 delivered notes, read-only during coverage scanning)",
        "docs/AGENT*.md binding rules (AGENTS.md sections 3, 7, 10, 12, 13)",
    ],
    "outputs": [
        "docs/INTEGRATION_CAMPAIGN_PLAN.md (binding campaign methodology: 15-session allocation S31-S45, decision rules, depth standard, verification gates, adaptive reallocation)",
        "src/vault_unification/integration.py (parse_integration_list + build_coverage + load_inventory_items; deterministic)",
        "CLI subcommands vu integ-inventory / vu integ-coverage (path-safe, atomic writes, JSON reports)",
        "tests/test_integration.py (37 tests incl. real-taxonomy regression pin and failure paths)",
        "state/integration/inventory-v1.jsonl (1,233 unique items, INT-0001.. in first-occurrence order)",
        "state/integration/clusters-v1.json (9 clusters, 81 sections, 24 context records, 85 excluded lines with reasons, noise block 719-802)",
        "state/integration/coverage-lexical-v1.jsonl (per-item lexical evidence)",
        "reports/integration/s31-inventory.json + s31-coverage-lexical.json (machine-readable, git-stamped)",
    ],
    "acceptance_criteria": [
        "every line of the taxonomy file is accounted for as item, context record, or documented exclusion with line number and reason (no silent drops)",
        "inventory parse is deterministic across re-runs (byte-identical outputs) and pinned by a regression test against the immutable input",
        "item ids are stable (INT-NNNN first-occurrence order); dedup folds British/American spelling; aliases split from trailing parentheticals incl. the LaTeX-escaped form",
        "master-index table rows contribute field items only; principal-concept columns resolve to existing item ids or are recorded unmatched (never create items)",
        "lexical coverage matches name+alias surfaces against note titles, frontmatter aliases, headings (numbering-stripped), and bodies with word-boundary Brit/US/plural-flexible regexes; bands title/heading/partial/body-multi/body-single/none",
        "lexical evidence is reported as evidence only, never as a coverage decision (documented limitation in the report and the plan section 5)",
        "no source-vault mutation; outputs written only to explicit path-safe destinations; sources verified byte-identical before and after",
        "full test suite green including the new tests; commands re-runnable from a fresh session via the committed reports",
    ],
    "forbidden_side_effects": [
        "Do not modify either source vault or the taxonomy file",
        "Do not modify output/Unified-Vault/ during coverage scanning (read-only)",
        "Do not create any integration decisions (A/B/C/D) in this task — decisions require the semantic judgment sessions (S32-S35)",
        "Do not weaken existing tests or lint/link/audit machinery",
    ],
    "findings": [],
    "notes": "Session 31 (first INTEG campaign session of 15). Two predecessor sessions were interrupted mid-implementation (uncommitted integration.py + campaign plan + partial CLI wiring were recovered from the working tree, reviewed line-by-line, completed, tested, and extended; the alias-split bug for LaTeX-escaped parentheticals was found by the new unit tests and fixed before any state was generated). Real-file parse: 1,283 raw / 1,233 unique items; cluster distribution SYNPATH 209, MAPDIG 81, MATHSOLVER 91, WEATHER 78, NLME 97, VAULTX 28, MASTER-INDEX 35, MEDNLP 368, 2D3D 291. Lexical first report over 544 notes: title 73 / heading 46 / partial 484 / body-multi 76 / body-single 18 / none 536 — the none band concentrates in SYNPATH/2D3D (geometric deep learning, NeRF/3D reconstruction vocabulary absent from both source vaults), consistent with the campaign's purpose. 44 of 81 master-index principal-concept crossrefs unmatched by exact/alias/folded surface matching (recorded; semantic phase resolves them).",
    "commit": None,
    "tests_run": [
        {"command": "python3 -m pytest tests/test_integration.py -q", "result": "37 passed"},
        {"command": "python3 -m pytest -q (full suite)", "result": "836 passed (799 baseline + 37 new)"},
        {"command": "vu integ-inventory (real taxonomy)", "result": "9 clusters / 81 sections / 1,283 raw / 1,233 unique / 85 excluded / source sha256 1b733ff5...; exit 0"},
        {"command": "vu integ-inventory determinism probe (re-run to /tmp, cmp)", "result": "inventory-v1.jsonl + clusters-v1.json byte-identical"},
        {"command": "vu integ-coverage (1,233 items vs 544 notes)", "result": "title 73 / heading 46 / partial 484 / body-multi 76 / body-single 18 / none 536; 22.7s; exit 0"},
        {"command": "vu integ-coverage determinism probe (re-run to /tmp, cmp)", "result": "coverage-lexical-v1.jsonl byte-identical"},
        {"command": "vu verify-manifest --root 'source-vaults/AI /AI Course' --manifest state/manifests/ai-course.jsonl", "result": "276/276 unchanged, exit 0"},
        {"command": "vu verify-manifest --root 'source-vaults/AI /Master AI' --manifest state/manifests/master-ai.jsonl", "result": "333/333 unchanged, exit 0"},
        {"command": "task-queue schema validation of INTEG-001 + INTEG-002", "result": "2/2 schema-valid (this script)"},
    ],
}

INTEG_002 = {
    "task_id": "INTEG-002",
    "title": "Semantic coverage judgments — MEDNLP cluster, 368 items (S32 of 15)",
    "status": "queued",
    "priority": "high",
    "dependencies": ["INTEG-001"],
    "inputs": [
        "state/integration/inventory-v1.jsonl (MEDNLP-cluster items; authoritative item list)",
        "state/integration/coverage-lexical-v1.jsonl (lexical evidence per item — substrate, never a decision)",
        "state/integration/clusters-v1.json (MEDNLP context records: navigation lines, group labels)",
        "output/Unified-Vault/ (544 notes, read-only during judging)",
    ],
    "outputs": [
        "state/integration/judgments-mednlp-v1.jsonl (one judgment per MEDNLP item: covered/partial/absent/equivalent + destination + verbatim evidence quote)",
        "reports/integration/s32-mednlp-judgments.json (aggregate with denominators + method)",
        "decision-ledger seeds for MEDNLP items (state/integration/decisions-v1.jsonl, opened S36)",
    ],
    "acceptance_criteria": [
        "every one of the 368 MEDNLP items receives exactly one judgment with a verdict from {covered, partial, absent, equivalent} at the campaign depth standard (plan section 5)",
        "every covered/equivalent judgment cites a destination note and a verbatim evidence quote mechanically verified as a substring of that note",
        "the orchestrator independently re-reviews at least 10% of judgments and records agreement/disagreement",
        "judging groups are bounded (context-budgeted) subagents; terminology-equivalence search is required in every judging prompt (lexical bands are hints, not verdicts)",
        "no source-vault or output-vault mutation during the judgment phase",
        "aggregate reports numerator/denominator with the sampling-free full-cluster method and its limitations",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults, the taxonomy file, or output notes",
        "Do not skip items or batch-reason over groups of items without per-item records",
        "Do not treat a lexical title/heading match as proof of semantic coverage",
    ],
    "findings": [],
    "notes": "Next session's bounded unit per campaign plan section 8 (S32). MEDNLP is the largest cluster (368 items) covering clinical NLP, medical terminologies (ICD-10, SNOMED CT, UMLS), drug databases, Transformer architectures in medical context, and medical vocabularies. Cluster context records constrain content: navigation line 'Open Medical-NLP-Reconstructed · Master Index'.",
    "commit": None,
    "tests_run": [],
}


def main() -> int:
    queue = [json.loads(ln) for ln in QUEUE.read_text().splitlines() if ln.strip()]
    existing = {t["task_id"] for t in queue}
    changed = False
    for row in (INTEG_001, INTEG_002):
        if row["task_id"] in existing:
            print(f"SKIP {row['task_id']}: already queued")
            continue
        queue.append(row)
        changed = True
        print(f"APPENDED {row['task_id']}")
    if not changed:
        print("task queue unchanged")
    else:
        # write first, then validate the whole queue (incl. dependency cross-checks)
        QUEUE.write_text(
            "".join(json.dumps(t, ensure_ascii=False) + "\n" for t in queue)
        )
    report = reg.validate_task_queue(QUEUE, REPO / "schemas" / "task.schema.json")
    if not report["valid"]:
        print(f"QUEUE INVALID: {report['errors']}")
        return 1
    print(f"FULL QUEUE VALID: {len(queue)} tasks")

    # current-state.json
    cs = json.loads(CURRENT.read_text())
    cs["current_task_id"] = "INTEG-002"
    cs["stage"] = "integration-campaign (S31 setup complete; S32 semantic audit next)"
    cs["notes"] = (
        "INTEG campaign (user directive commit 77cf6cf, 15-session budget S31-S45): "
        "setup complete at session 31 — methodology docs/INTEGRATION_CAMPAIGN_PLAN.md, "
        "deterministic inventory (1,233 unique items from the taxonomy), lexical "
        "coverage evidence over the 544 delivered notes. Next: semantic coverage "
        "judgments per cluster (S32 MEDNLP first)."
    )
    CURRENT.write_text(json.dumps(cs, indent=2, ensure_ascii=False) + "\n")
    print("current-state.json updated")

    # session-31 checkpoint
    checkpoint = {
        "session": 31,
        "task_id": "INTEG-001",
        "date": "2026-11-06",
        "phase": "integration-campaign-setup",
        "work_completed": [
            "recovered and reviewed the interrupted session's uncommitted WIP (integration.py, campaign plan, partial CLI wiring); completed the CLI handlers, inventory loader, and 37-test suite",
            "fixed the LaTeX-escaped alias-split bug found by the new tests (Output Projection (\\(W^O\\)) now yields alias W^O; 66 aliased items)",
            "generated the deterministic inventory: 1,283 raw / 1,233 unique items, 9 clusters, 81 sections, 85 documented exclusions (1 preamble + 84 transcript-noise lines 719-802), 24 context records",
            "generated the first lexical coverage report over the 544 delivered notes: title 73 / heading 46 / partial 484 / body-multi 76 / body-single 18 / none 536",
            "registered INTEG-001 (completed) and INTEG-002 (queued) in the task queue; wrote this checkpoint; updated handoff, README, policy ledger row 31",
        ],
        "changed_paths": [
            "docs/INTEGRATION_CAMPAIGN_PLAN.md (new; corrected item counts to the deterministic parse)",
            "src/vault_unification/integration.py (new module + alias fix)",
            "src/vault_unification/cli.py (integ-inventory / integ-coverage commands wired)",
            "tests/test_integration.py (new; 37 tests)",
            "state/integration/inventory-v1.jsonl",
            "state/integration/clusters-v1.json",
            "state/integration/coverage-lexical-v1.jsonl",
            "reports/integration/s31-inventory.json",
            "reports/integration/s31-coverage-lexical.json",
            "state/task-queue.jsonl (+2 rows)",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-11-06-integ-session31.json",
            "docs/ACCELERATED_COMPLETION_POLICY.md (ledger row 31)",
            "docs/agent-handoff/next-agent.md (rewritten for session 32)",
            "README.md (campaign status)",
        ],
        "tests_run": INTEG_001["tests_run"],
        "git_state": {
            "branch": "main",
            "base_commit": "77cf6cf (user taxonomy upload; HEAD at session start)",
            "session_commits": "recorded in the session commit message (this checkpoint is committed with them)",
            "push_verification": "per AGENTS.md section 13: push after this commit and verify the remote ref",
        },
        "open_findings": [
            "lexical none-band concentration in SYNPATH/2D3D clusters (geometric deep learning, NeRF/3D vocabulary absent from both source vaults) — expected genuinely-missing material for decision C in the campaign; semantic judgments will confirm",
            "44 of 81 master-index principal-concept crossrefs unmatched by surface matching — recorded; semantic phase resolves",
        ],
        "next_task": {
            "task_id": "INTEG-002",
            "title": "Semantic coverage judgments — MEDNLP cluster (368 items)",
            "dependencies": ["INTEG-001 (completed)"],
            "inputs": INTEG_002["inputs"],
            "outputs": INTEG_002["outputs"],
            "acceptance_criteria": INTEG_002["acceptance_criteria"],
            "resume": (
                "Follow AGENTS.md section 2 startup; read docs/INTEGRATION_CAMPAIGN_PLAN.md "
                "(binding) and this checkpoint; verify INTEG-001 evidence (reports/integration/s31-*.json, "
                "state/integration/*); then run the MEDNLP semantic judgment campaign per plan section 5 "
                "with bounded subagent groups, mechanically verified evidence quotes, and >=10% "
                "orchestrator re-review."
            ),
        },
        "accelerated_mode": {
            "session_number": 31,
            "budget_sessions_consumed": 1,
            "budget_sessions_remaining": 14,
            "deliverable_metric_moved": "campaign setup artifacts: inventory items parsed deterministically + lexical coverage evidence computed (setup session; the judgment/integration metrics begin at S32)",
            "before": "0 items inventoried; 0 lexical evidence rows; no campaign methodology registered",
            "after": "1,233/1,233 unique items inventoried with documented exclusions; 1,233/1,233 lexical evidence rows over 544 notes; binding methodology (docs/INTEGRATION_CAMPAIGN_PLAN.md) committed",
            "denominator": "1,233 unique taxonomy items (of 1,283 raw lines); 544 delivered notes",
            "failed_session": False,
            "cause_if_failed": None,
            "deadline_position": "INTEG campaign session 1 of 15 (S31-S45 per docs/INTEGRATION_CAMPAIGN_PLAN.md section 8); on plan",
        },
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
