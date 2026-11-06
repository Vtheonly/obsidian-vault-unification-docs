#!/usr/bin/env python3
"""DISC-002 session 6: write the checkpoint file and the session summary report."""
from __future__ import annotations

import json
from pathlib import Path

CKPT = Path("state/checkpoints/checkpoint-2026-10-30-disc002-session6.json")
SUMMARY = Path("reports/discovery/disc002-session6-summary.json")

checkpoint = {
    "checkpoint_id": "checkpoint-2026-10-30-disc002-session6",
    "recorded_utc": "2026-10-30",
    "task_id": "DISC-002",
    "task_status": "in_progress",
    "stage": "disc002-review-batch6-complete (six-round replay re-verification + batch-6 tranche)",
    "baseline_verification": {
        "tests": "663/663 passed (python3 -m pytest tests/ -q --json-report, before any mutation; reports/discovery/disc002-session6-baseline-pytest.json)",
        "immutability_start": "both vaults byte-identical to committed manifests at session start (reports/discovery/disc002-session6-manifest-{ai-course,master-ai}.json; 0 added/removed/changed)",
        "immutability_end": "both vaults byte-identical after all operations (reports/discovery/disc002-session6-manifest-end-{ai-course,master-ai}.json; 0 added/removed/changed)",
        "git_state": "HEAD == origin/main == 75a22ed at session start, clean tree",
    },
    "adr0010_replay_verification": {
        "driver": "scripts/disc002_batch6_replay.py (repo-relative; extends the batch-5 replay with the batch-5 decide round — six rounds total)",
        "regeneration": "vu discover-gaps over all 70 batches (recorded args from reports/discovery/disc002-full-corpus-run.json): 60,154 candidates (reports/discovery/disc002-s6-replay-full.json)",
        "decision_chain_replay": "r1 (--decided-utc 2026-10-28T00:45:00Z) -> r2 (01:30:00Z) -> batch2 (02:30:00Z) -> batch3 (2026-10-28T05:30:00Z) -> batch4 (2026-10-30T13:05:00Z) -> batch5 (15:30:00Z) on the CLI-regenerated candidates (reports/discovery/disc002-s6-replay-{r1,r2,batch2,batch3,batch4,batch5}.json)",
        "index_content_identical_to_committed": True,
        "content_comparison_method": "parsed-record equality (json.loads per line), per F-0019 — raw sha256 not compared",
        "validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-s6-replay-validate.json)",
    },
    "batch6_review": {
        "tranche_selection": "scripts/disc002_batch6_tranche.py (repo-relative; reads scratch/disc002-s6-batch5.jsonl): fragmented_derivation OR score>=0.8 OR contexts>=10, score-desc, excluding reviewed; 60 of 4,874 matching (51,852 unreviewed provisional; brief + pool stats + selected.json in /home/z/my-project/scratch/disc002-batch6-*)",
        "tranche_character": "this tranche is dominated by generic English vocabulary and prose fragments (verbs, gerunds, adjectives, adverbs, numeric prose, one possessive); only a minority are technical fragments (randn, eval set, sklearn, probability distribution, diagonal, and the technical senses of majority/square/cached/param/signals/adjacent/10x)",
        "method": "individual evidence review of all 60 brief blocks + scripts/disc002_batch6_probe.py (34-term definitional-treatment coverage probe, results /home/z/my-project/scratch/disc002-batch6-probe.json) + targeted citation verification (scripts/disc002_batch6_verify.py, 37 locator checks) + independent subagent cross-check of 15 judgment calls (5 proposed covers + 10 borderline rejects)",
        "subagent_cross_check": "15/15 AGREE (5 cover, 10 reject upheld; no confirm_gap warranted); corrections incorporated: path completions for ai-course chapter-level parents (recurring), two evidence upgrades — master-ai '28 - Glossary/03 - Notation Conventions.md:54' supplies the diag(x) definitional entry for the diagonal cover (the '06 - Tensors and Broadcasting.md:258' '# 6. Diagonal extraction' is a code comment inside a code block, recharacterized as in-situ usage only) and master-ai '02 - Mathematics/Probability/09 - Gaussian Distribution.md' (Definition section :14-16, randn usage :102) strengthens the randn cover; additional dedicated Scikit-Learn sections recorded ('07. Scaling, Pipeline and Interpretability - Summary.md:462', '03.1 - Regression/07. Lab - Guide Complet... (MNIST).md:27')",
        "decisions": "5 cover (evidence-cited: randn, eval set, sklearn, probability distribution, diagonal) + 55 reject (generic-vocabulary 49, prose-fragment/possessive 3, code-identifier 1, homonym 1, numeric prose 1 — counted by rationale stem)",
        "new_confirmed_gaps": 0,
        "decisions_file": "state/concept-candidates/002-disc002-decisions-batch6.jsonl (60 records, decision ids D-DISC002-B6-0001..0060)",
        "decided_utc": "2026-10-30T16:30:00Z",
        "apply_report": "reports/discovery/disc002-decide-batch6.json (decisions_applied: 1523 = 1153+44+86+60+60+60+60 cumulative chain)",
        "post_validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-validate-batch6.json)",
        "post_index": "reports/discovery/disc002-index-batch6.json (60,154 records indexed)",
        "post_statuses": {
            "provisional_candidate": 51792,
            "already_covered": 7006,
            "rejected": 1353,
            "confirmed_gap": 2,
            "deferred": 1,
        },
        "delta_verification": "exact: -60 provisional, +5 already_covered, +55 rejected; confirmed_gap and deferred unchanged",
    },
    "next_task": {
        "summary": "DISC-002 continuation: batch-7+ review tranches (reuse scripts/disc002_batch6_{tranche,probe,decisions}.py pattern with new decision ids D-DISC002-B7-**** and CAND pointed at the post-batch6 state), then per-domain semantic classification of the 69,185 dossier-extension overlap pairs, then disposition assignment, then GATED synthesis",
        "resume": "docs/agent-handoff/next-agent.md",
    },
}

CKPT.write_text(json.dumps(checkpoint, indent=1) + "\n", encoding="utf-8")
print("wrote", CKPT)

summary = {
    "report_meta": {
        "command": "session6-summary",
        "framework_version": "0.9.0",
        "utc_timestamp": "2026-10-30T16:30:00Z",
        "task_id": "DISC-002",
        "session": "6 (six-round replay re-verification + batch-6 review tranche)",
        "git_commit_at_start": "75a22ed",
    },
    "baseline_verification": {
        "tests": "663/663 passed at session start (reports/discovery/disc002-session6-baseline-pytest.json; 662 at session-5 start + the F-0020 regression test added then)",
        "immutability_start": "both vaults 0 added/0 removed/0 changed vs committed manifests (reports/discovery/disc002-session6-manifest-{ai-course,master-ai}.json)",
        "adr0010_replay": {
            "regeneration": "vu discover-gaps over all 70 batches per the recorded args: 60,154 candidates (reports/discovery/disc002-s6-replay-full.json)",
            "decision_chain": "r1 (2026-10-28T00:45:00Z) -> r2 (01:30:00Z) -> batch2 (02:30:00Z) -> batch3 (2026-10-28T05:30:00Z) -> batch4 (2026-10-30T13:05:00Z) -> batch5 (15:30:00Z) replayed on the CLI-regenerated candidates",
            "index_content_identical_to_committed": True,
            "validate": "valid: true; 60,154 records; 0 errors",
        },
    },
    "batch6_review": {
        "tranche_selection": "scripts/disc002_batch6_tranche.py: same signal rule as batches 3-5 (fragmented_derivation OR score>=0.8 OR contexts>=10), score-desc; 60 of 4,874 matching (51,852 total unreviewed provisional)",
        "method": "individual evidence review + scripts/disc002_batch6_probe.py (34-term definitional-treatment coverage probe) + targeted citation verification (scripts/disc002_batch6_verify.py) + independent subagent cross-check of 15 judgment calls",
        "subagent_cross_check": "15/15 AGREE; path completions and two evidence upgrades incorporated (glossary diag(x) entry; Gaussian Distribution note)",
        "decisions": "5 cover (evidence-cited) + 55 reject (generic-vocabulary 49, prose-fragment/possessive 3, code-identifier 1, homonym 1, numeric prose 1, counted by rationale stem)",
        "new_confirmed_gaps": 0,
        "decisions_file": "state/concept-candidates/002-disc002-decisions-batch6.jsonl (60 records)",
        "decided_utc": "2026-10-30T16:30:00Z",
        "apply_report": "reports/discovery/disc002-decide-batch6.json (decisions_applied: 1523 cumulative)",
        "post_statuses": {
            "provisional_candidate": 51792,
            "already_covered": 7006,
            "rejected": 1353,
            "confirmed_gap": 2,
            "deferred": 1,
        },
        "post_validate": "valid: true; 60,154 records; 0 errors (reports/discovery/disc002-validate-batch6.json)",
        "post_index": "reports/discovery/disc002-index-batch6.json; index delta-verified exactly (-60 provisional, +5 covered, +55 rejected)",
    },
    "remaining": {
        "review_tranches": "~4,814 unreviewed provisional candidates still match the signal rule (batch-7+)",
        "dossier_extension_classification": "69,185 candidate pairs across six domains (semantic classification pending, no bulk absorption)",
        "disposition_assignment": "release-blocking, follows classification",
    },
}

SUMMARY.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
print("wrote", SUMMARY)
