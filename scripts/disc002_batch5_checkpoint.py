#!/usr/bin/env python3
"""DISC-002 session 5: write the checkpoint file and the session summary report."""
from __future__ import annotations

import json
from pathlib import Path

CKPT = Path("state/checkpoints/checkpoint-2026-10-30-disc002-session5.json")
SUMMARY = Path("reports/discovery/disc002-session5-summary.json")

checkpoint = {
    "checkpoint_id": "checkpoint-2026-10-30-disc002-session5",
    "recorded_utc": "2026-10-30",
    "task_id": "DISC-002",
    "task_status": "in_progress",
    "stage": "disc002-review-batch5-complete (fresh-clone verification + F-0020 fix + batch-5 tranche)",
    "baseline_verification": {
        "tests": "662/662 passed (python3 -m pytest tests/ -q, before any mutation; reports/discovery/disc002-session5-baseline-pytest.json)",
        "selftest": "vu selftest ok (mandatory_checks_passed: true)",
        "immutability_start": "both vaults byte-identical to committed manifests at session start (reports/discovery/disc002-session5-manifest-{ai-course,master-ai}.json; 0 added/removed/changed)",
        "immutability_end": "both vaults byte-identical after all operations (reports/discovery/disc002-session5-manifest-end-{ai-course,master-ai}.json; 0 added/removed/changed)",
        "git_state": "HEAD == origin/main == 203c171 at session start, clean tree",
    },
    "adr0010_replay_verification": {
        "driver": "scripts/disc002_batch5_replay.py (repo-relative; drives the vu CLI as subprocesses in one tool call per F-0016)",
        "regeneration": "vu discover-gaps over all 70 batches (recorded args from reports/discovery/disc002-full-corpus-run.json): 60,154 candidates (reports/discovery/disc002-s5-replay-full.json)",
        "decision_chain_replay": "r1 (--decided-utc 2026-10-28T00:45:00Z) -> r2 (01:30:00Z) -> batch2 (02:30:00Z) -> batch3 (2026-10-28T05:30:00Z) -> batch4 (2026-10-30T13:05:00Z) on the CLI-regenerated candidates (reports/discovery/disc002-s5-replay-{r1,r2,batch2,batch3,batch4}.json)",
        "index_content_identical_to_committed": True,
        "content_comparison_method": "parsed-record equality (json.loads per line), per F-0019 — raw sha256 not compared",
        "validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-s5-replay-validate.json)",
    },
    "f0020_fix": {
        "finding": "F-0020: `python -m vault_unification.cli` was a silent no-op — module import without a __main__ guard; exit 0, no output, no files written",
        "discovered": "first run of scripts/disc002_batch5_replay.py: all seven CLI steps returned 0 while zero output files appeared (scratch stayed empty)",
        "fix": "added `if __name__ == \"__main__\": raise SystemExit(main())` to src/vault_unification/cli.py",
        "regression_test": "tests/test_cli.py::test_module_cli_execution_is_not_a_silent_noop (happy path --version must print; failure path discovery-validate with missing file must exit 1 with an error)",
        "recorded": "state/findings.jsonl (F-0020, status: fixed, severity: medium)",
    },
    "batch5_review": {
        "tranche_selection": "scripts/disc002_batch5_tranche.py (repo-relative): fragmented_derivation OR score>=0.8 OR contexts>=10, score-desc, excluding reviewed; 60 of 4,934 matching (51,912 unreviewed provisional)",
        "method": "individual evidence review + scripts/disc002_batch5_probe.py (41-term definitional-treatment coverage probe) + targeted corpus verification for boundary cases (generative-model glossary entry, center-crop rationale, flat-minima treatments in both vaults, Inception branch concatenation, focal-loss/class-imbalance treatments, omit-bias math reason, patch-representation treatments, VAE-decoder role in latent diffusion, initialization-sensitivity statements, BN/Dropout train-eval mode sections) + independent subagent cross-check of 14 judgment calls",
        "subagent_cross_check": "14/14 AGREE; 4 citation path corrections incorporated (recurring omission of the '05 - Convolutional Neural Networks (CNN)/' chapter-level parent for ai-course notes; one missing '01 - Foundations and Overview/' parent); verified line numbers adopted (:193 BN deterministic comment, :269 augmentation transform pipeline comment, :684 checkpoint comment, five Bahdanau title-quote locations)",
        "decisions": "20 cover (evidence-cited) + 40 reject (prose-fragment 9, generic-vocabulary 22, code-identifier 2, citation-fragment 7 — counted by rationale stem)",
        "new_confirmed_gaps": 0,
        "decisions_file": "state/concept-candidates/002-disc002-decisions-batch5.jsonl (60 records, decision ids D-DISC002-B5-0001..0060)",
        "decided_utc": "2026-10-30T15:30:00Z",
        "apply_report": "reports/discovery/disc002-decide-batch5.json (decisions_applied: 1463 = 1153+44+86+60+60+60 cumulative chain)",
        "post_validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-validate-batch5.json)",
        "post_index": "reports/discovery/disc002-index-batch5.json (60,154 records indexed)",
        "post_statuses": {
            "provisional_candidate": 51852,
            "already_covered": 7001,
            "rejected": 1298,
            "confirmed_gap": 2,
            "deferred": 1,
        },
        "delta_verification": "exact: -60 provisional, +20 already_covered, +40 rejected; confirmed_gap and deferred unchanged",
    },
    "next_task": {
        "summary": "DISC-002 continuation: batch-6+ review tranches (reuse scripts/disc002_batch5_{tranche,probe,decisions}.py pattern with new decision ids D-DISC002-B6-****), then per-domain semantic classification of the 69,185 dossier-extension overlap pairs, then disposition assignment, then GATED synthesis",
        "resume": "docs/agent-handoff/next-agent.md",
    },
}

CKPT.write_text(json.dumps(checkpoint, indent=1) + "\n", encoding="utf-8")
print("wrote", CKPT)

summary = {
    "report_meta": {
        "command": "session5-summary",
        "framework_version": "0.9.0",
        "utc_timestamp": "2026-10-30T15:30:00Z",
        "task_id": "DISC-002",
        "session": "5 (fresh-clone verification + F-0020 fix + batch-5 review tranche)",
        "git_commit_at_start": "203c1715"[:7] + " (203c171)",
    },
    "baseline_verification": {
        "tests": "662/662 passed at session start (reports/discovery/disc002-session5-baseline-pytest.json)",
        "selftest": "ok: true (vu selftest)",
        "immutability_start": "both vaults 0 added/0 removed/0 changed vs committed manifests (reports/discovery/disc002-session5-manifest-{ai-course,master-ai}.json)",
        "adr0010_replay": {
            "regeneration": "vu discover-gaps over all 70 batches per the recorded args: 60,154 candidates (reports/discovery/disc002-s5-replay-full.json)",
            "decision_chain": "r1 (2026-10-28T00:45:00Z) -> r2 (01:30:00Z) -> batch2 (02:30:00Z) -> batch3 (2026-10-28T05:30:00Z) -> batch4 (2026-10-30T13:05:00Z) replayed on the CLI-regenerated candidates",
            "index_content_identical_to_committed": True,
            "validate": "valid: true; 60,154 records; 0 errors",
        },
    },
    "f0020": {
        "title": "`python -m vault_unification.cli` was a silent no-op (exit 0, no output)",
        "status": "fixed + regression-tested (tests/test_cli.py::test_module_cli_execution_is_not_a_silent_noop)",
        "impact_avoided": "any scripted pipeline using that invocation form would silently skip work while observing exit 0",
    },
    "batch5_review": {
        "tranche_selection": "scripts/disc002_batch5_tranche.py: same signal rule as batches 3-4 (fragmented_derivation OR score>=0.8 OR contexts>=10), score-desc; 60 of 4,934 matching (51,912 total unreviewed provisional)",
        "method": "individual evidence review + scripts/disc002_batch5_probe.py (41-term definitional-treatment coverage probe) + targeted corpus verification for boundary cases + independent subagent cross-check of 14 judgment calls",
        "subagent_cross_check": "14/14 AGREE; 4 citation path corrections incorporated",
        "decisions": "20 cover (evidence-cited) + 40 reject (prose-fragment 9, generic-vocabulary 22, code-identifier 2, citation-fragment 7, counted by rationale stem)",
        "new_confirmed_gaps": 0,
        "decisions_file": "state/concept-candidates/002-disc002-decisions-batch5.jsonl (60 records)",
        "decided_utc": "2026-10-30T15:30:00Z",
        "apply_report": "reports/discovery/disc002-decide-batch5.json (decisions_applied: 1463 cumulative)",
        "post_statuses": {
            "provisional_candidate": 51852,
            "already_covered": 7001,
            "rejected": 1298,
            "confirmed_gap": 2,
            "deferred": 1,
        },
        "post_validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-validate-batch5.json)",
        "post_index": "reports/discovery/disc002-index-batch5.json; index delta-verified exactly (-60 provisional, +20 covered, +40 rejected)",
    },
    "remaining": {
        "review_tranches": "~4,874 unreviewed provisional candidates still match the signal rule (batch-6+)",
        "dossier_extension_classification": "69,185 candidate pairs across six domains (semantic classification pending, no bulk absorption)",
        "disposition_assignment": "release-blocking, follows classification",
    },
}

SUMMARY.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
print("wrote", SUMMARY)
