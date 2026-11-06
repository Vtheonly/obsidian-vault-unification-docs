#!/usr/bin/env python3
"""VERIF-001 closeout: task queue completion, current-state refresh,
session-29 checkpoint. Handoff and policy ledger are updated separately."""
import json
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"
CKPT = REPO / "state/checkpoints/checkpoint-2026-11-06-verif001-session29.json"

# ---- task queue: VERIF-001 -> completed ----
records = [json.loads(l) for l in QUEUE.open(encoding="utf-8") if l.strip()]
for t in records:
    if t["task_id"] == "VERIF-001":
        assert t["status"] == "in_progress"
        t["status"] = "completed"
        t["findings"] = ["F-0035", "F-0036", "F-0037", "F-0038", "F-0039",
                         "F-0040", "F-0041"]
        t["tests_run"] = [
            {
                "command": "python3 -m pytest -q (baseline / after last mutation)",
                "result": "752/752 -> 752/752 passed (1 initial sandbox-env subprocess failure resolved by editable reinstall, no code change)",
                "evidence": "session-29 terminal output; commit 02a576a message",
            },
            {
                "command": "vu audit-output (full corpus, s29 reproduction, pre-repair)",
                "result": "valid=true; 0 findings; 27,536 KUs; 544 files; 42,156 markers 0 missing — byte-identical stats to s28 report",
                "evidence": "reports/synthesis/s29-verify-full-corpus-audit.json",
            },
            {
                "command": "vu kureg-init + kureg-load x70 + kureg-apply-dispositions + kureg-validate (registry rebuild)",
                "result": "27,536 inserted / 27,536 applied / 0 revised; valid=true; Unaccounted=0; needs_review=0",
                "evidence": "scripts/s29_rebuild_registry.py run; /tmp/vk29-validate.json (commands recorded in script)",
            },
            {
                "command": "vu check-links --root output/Unified-Vault (before / after repairs)",
                "result": "11,999 links 0 problems -> 12,002 links 0 problems (+3 new links from F-0035/F-0036 repairs, all resolving)",
                "evidence": "reports/synthesis/s29-final-check-links.json (s28); /tmp/s29-links-post.json",
            },
            {
                "command": "vu lint-artifacts output/Unified-Vault (before / after repairs)",
                "result": "0 errors / 85 warnings / 754 infos both times",
                "evidence": "/tmp/s29-lint-post.json",
            },
            {
                "command": "vu audit-output (full corpus, post-repair)",
                "result": "valid=true; 0 findings; 42,156 markers 0 missing (repairs preserved everything)",
                "evidence": "reports/synthesis/s29-post-repair-full-corpus-audit.json",
            },
            {
                "command": "vu verify-manifest x2 (sources, after repairs)",
                "result": "ai-course 276/276 + master-ai 333/333 byte-identical",
                "evidence": "/tmp/s29-imm-ai.json, /tmp/s29-imm-ma.json",
            },
        ]
        t["notes"] = ("COMPLETED at session 29 (2026-11-06). Campaign evidence: "
                      "reports/synthesis/s29-semantic-campaign.json (aggregates), "
                      "reports/synthesis/s29-semantic-judgments.jsonl (246 judgments, "
                      "quotes mechanically verified), reports/synthesis/s29-semantic-sample.json "
                      "(deterministic sample), reports/synthesis/s29-semantic-repairs.json "
                      "(5 anchored repairs). 244/246 (99.2%) retained; 2 partial verdicts "
                      "repaired same-session; 0 absent; 0 Unaccounted impact. This deepens "
                      "the 'units semantically validated' evidence class beyond SYNTH-001's "
                      "per-area generation reviews; the §5.1 boundary (not a full per-unit "
                      "semantic proof) still stands.")
with QUEUE.open("w", encoding="utf-8") as fh:
    for t in records:
        fh.write(json.dumps(t, ensure_ascii=False) + "\n")

# ---- current state ----
state = json.loads(STATE.read_text(encoding="utf-8"))
state["current_task_id"] = "VERIF-001"
state["stage"] = "post-delivery-verification-complete"
state["notes"] = ("Vault delivered at session 28 (544/544 notes, all gates green; "
                  "reports/release/final-report.md). Session 29 independently reproduced the "
                  "final verification (full-corpus audit, registry rebuild, links, lint, "
                  "752/752 tests), then completed VERIF-001: stratified semantic "
                  "spot-verification of 246 KUs — 244/246 (99.2%) retained, 2 partial "
                  "verdicts repaired via anchored scripts, 2 source-inherited sic items "
                  "documented (F-0040/F-0041). Post-repair battery fully green "
                  "(reports/synthesis/s29-semantic-campaign.json).")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")

# ---- checkpoint ----
import subprocess
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                      cwd=REPO).stdout.strip()
ckpt = {
    "session": "29",
    "date": "2026-11-06",
    "task_id": "VERIF-001 — COMPLETED",
    "phase": "post-delivery-semantic-verification",
    "accelerated_mode": {
        "session_number": 29,
        "budget_sessions_consumed": 0,
        "budget_sessions_remaining": 0,
        "deliverable_metric_moved": "sampled KUs semantically verified with mechanically-verified destination evidence / stratified sample drawn",
        "before": 0,
        "after": 246,
        "denominator": 246,
        "failed_session": False,
        "cause_if_failed": None,
        "deadline_position": ("Project delivered at session 28 (deadline overrun closed under "
                              "policy §5.5). Session 29 is post-delivery verification deepening, "
                              "outside the ADR-0012 budget; it moved a NEW metric (semantic "
                              "spot-verification coverage) without touching the delivered "
                              "metric (544/544 notes, all gates still green)."),
    },
    "work_completed": [
        "Startup verification: pulled origin/main (8196869, s28 final delivery), normalized 2125 sandbox mode-only diffs, independently reproduced the full-corpus audit from committed state (ledger overlay rebuilt: valid=true, 0 findings, 27,536 KUs, 42,156 markers 0 missing — identical stats to s28), rebuilt the registry from 70 committed batches (27,536 applied, Unaccounted=0, needs_review=0), check-links 11,999/0, lint 0 errors/85 warnings, sources 276/276+333/333 byte-identical, 752/752 tests (after editable reinstall for the sandbox-recycled venv)",
        "VERIF-001 registered (task queue + current-state) with acceptance criteria; deterministic stratified sample of 246/27,536 KUs (0.89%) committed: census of tiny (disposition x unit_type) cells + Contextualized 42/Consolidated 121/Preserved 80 stratified (largest-remainder across unit types, even-spaced by ku_id, no RNG) + area floor >=2 KUs -> 20/20 areas; prose/list/callout deliberately overweighted (202/246) because math/code already carry verbatim fingerprints in the lexical marker net",
        "Judgment phase: 18 bounded subagent groups (4-18 KUs, <=293 KB note text each), each KU judged present/partial/absent/superseded-info-retained with 1-3 verbatim destination quotes; mechanical validation PASSED (246/246, every quote a whitespace-normalized substring of its cited destination note; order and coverage exact)",
        "Orchestrator independent re-review: 28/246 (11.4%) — all 4 non-present verdicts + 24 even-spaced present; 28/28 agreement; 1 judgment repaired for destination_note field conformance (verdict unchanged); 6 present verdicts deep-verified at full-context level (Q&A answers, 5-point lists, retargeted link chains); 2 subagent quality flags found non-reproducible (KNN 'repeated 3x' claims are 1x) and excluded from findings",
        "Results: 242 present + 2 superseded-info-retained + 2 partial + 0 absent = 244/246 (99.2%) retained; both partial verdicts orchestrator-confirmed by direct read",
        "Findings F-0035..F-0041 recorded (5 output defects + 2 source-inherited sic); 5 repaired via anchored probe-idempotent scripts/s29_semantic_repairs.py (double-run no-op verified): F-0035 MHA See-Also +2 path-form links, F-0036 quantization restored to coverage list, F-0037 tripled phrase collapsed, F-0038 Huber French-labels block de-tripled (first block kept verbatim), F-0039 KNN heading fragment merged; F-0040/F-0041 accepted sic (source-internal, keep-both convention)",
        "Post-repair battery: lint 0 errors/85 warnings; check-links 12,002 links 0 problems (+3 new all resolving); full-corpus audit valid=true 0 findings 42,156 markers 0 missing; 752/752 tests; sources 276/276+333/333 byte-identical",
        "Continuous commit-and-push: 02a576a (startup verification + VERIF-001 opened), 5361640 (campaign + repairs), both remote-verified 0/0 divergence",
    ],
    "changed_paths": [
        "output/Unified-Vault/08 - Attention and Transformers/Attention Mechanism/Multi-Head Attention.md (F-0035)",
        "output/Unified-Vault/20 - Vault and Project Context/Current Iteration Log.md (F-0036)",
        "output/Unified-Vault/04 - Machine Learning/Regression/Logistic Regression.md (F-0037)",
        "output/Unified-Vault/04 - Machine Learning/Optimization Algorithms/Loss Functions.md (F-0038)",
        "output/Unified-Vault/04 - Machine Learning/Nearest Neighbors/K-Nearest Neighbors.md (F-0039)",
        "state/synthesis/s29-semantic-sample.jsonl (committed sample)",
        "reports/synthesis/s29-*.json + s29-semantic-judgments.jsonl (evidence)",
        "state/findings.jsonl (+7 records; 5 fixed, 2 accepted)",
        "state/task-queue.jsonl (VERIF-001 completed), state/current-state.json",
        "scripts/s29_*.py (8 committed scripts)",
    ],
    "tests_run": [
        {"command": "python3 -m pytest -q", "result": "752/752 passed (start and after last mutation)"},
        {"command": "vu audit-output (full corpus x2)", "result": "valid=true 0 findings x2 (pre/post repair)"},
        {"command": "vu check-links", "result": "11,999 -> 12,002 links, 0 problems"},
        {"command": "vu lint-artifacts", "result": "0 errors / 85 warnings"},
        {"command": "vu kureg-init/load/apply/validate", "result": "27,536 applied, Unaccounted=0"},
        {"command": "vu verify-manifest x2", "result": "276/276 + 333/333 byte-identical"},
        {"command": "scripts/s29_validate_judgments.py", "result": "PASSED 246/246 quotes verified"},
        {"command": "scripts/s29_semantic_repairs.py x2 (apply + probe)", "result": "5 applied, second run all no-op"},
    ],
    "git_state": {
        "branch": "main",
        "head_before_this_checkpoint": head,
        "remote": "origin/main (verified 0/0 divergence after each push)",
        "pushes_this_session": ["02a576a", "5361640"],
        "working_tree": "clean after this commit (mode-only diffs normalized via core.fileMode=false)",
    },
    "open_findings": [
        "F-0016 open-operational (environment; documented, pre-existing)",
        "F-0018 partially-fixed (historical helper scripts; documented, pre-existing)",
        "F-0040 accepted sic (source-inherited wrong value in verbatim code block; correct value adjacent in prose)",
        "F-0041 accepted sic (source-inherited 7,000/7,300 arithmetic switch; preserved verbatim)",
    ],
    "next_task": {
        "candidates": [
            "Extend the semantic campaign to a second stratified sample (the committed sampler is parameterizable; a 246-KU increment per session is a proven bounded unit)",
            "Vault-wide See-Also cross-link audit (F-0035's remaining_risk names it; mechanical: every source See-Also link's target existence + carry-over check)",
            "Corpus-wide duplicate-phrase scan (F-0037/F-0038's remaining_risk; framework tool candidate)",
            "User-directed presentation changes to the area-20 archival layer (from the s28 handoff; none authorized yet)",
        ],
        "note": ("No task is queued; VERIF-001 completed the only open queue entry. The vault "
                 "remains delivered and green. Any of the candidates above can be registered "
                 "as VERIF-002 or a framework task on user direction; the semantic-campaign "
                 "extension and the See-Also audit are the natural continuations of this "
                 "session's work."),
    },
}
CKPT.write_text(json.dumps(ckpt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("checkpoint written:", CKPT.name)
print("task queue: VERIF-001 completed")
