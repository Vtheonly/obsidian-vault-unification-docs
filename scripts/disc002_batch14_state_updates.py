#!/usr/bin/env python3
"""DISC-002 session 14 (batch 14): persist findings, task-queue, current-state, checkpoint."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FINDINGS = REPO / "state/findings.jsonl"
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-01-disc002-session14.json"

QUEUE_NOTES = (
    "DISC-002 IN PROGRESS - session 14 (2026-11-01). Baseline independently "
    "re-verified at session start: clean tree with HEAD == origin/main == "
    "2d577cd; 663/663 tests after the documented editable install "
    "(reports/discovery/disc002-session14-baseline-pytest.json; the "
    "fresh-sandbox setup 'python3 -m pip install -e .' was run FIRST this "
    "time — the session-13 lesson held, no failed baseline run); both "
    "vaults byte-identical to committed manifests at session start "
    "(reports/discovery/disc002-session14-manifest-{ai-course,master-ai}."
    "json; 0 added/removed/changed). ADR-0010 replay extended to FOURTEEN "
    "decide rounds via scripts/disc002_batch14_replay.py (r1+r2+batch2.."
    "batch13 replayed with recorded --decided-utc values, then "
    "discovery-index) — CONTENT-IDENTICAL to the committed index (60,154 "
    "records; status counts matched exactly: 51,372/7,197/1,580/3/1/1; "
    "validate green; F-0019 heeded; replay ran clean on the FIRST try; "
    "post-batch13 chain state preserved at scratch/disc002-s14-batch13."
    "jsonl). ONE NEW TOOLING DEFECT found and fixed IN SESSION: F-0021 — "
    "the probe family's fence_spans treated an UNCLOSed code fence "
    "(mdextract end_line=null, closed=false) as a zero/None span because "
    "f.get('end_line', start) does not default an explicit null; the "
    "batch-14 probe crashed with TypeError on the 'fill:#' term family "
    "and was fixed to extend unclosed spans to EOF (scripts/"
    "disc002_batch14_probe.py). The batch-10..13 probes share the latent "
    "defect but never triggered it (no probed term matched a def pattern "
    "inside an unclosed fence). BATCH 14 REVIEW TRANCHE: 60 highest-signal "
    "unreviewed provisional candidates (4,394 matching the signal rule of "
    "51,372 unreviewed — exactly the session-13 handoff prediction; "
    "scripts/disc002_batch14_tranche.py, repo-relative, CAND at scratch/"
    "disc002-s14-batch13.jsonl). Tranche character: mixed — generic "
    "fragments and artifacts (prose fragments 'different results'/'visual "
    "information'/'answer questions'/'image content'/'large errors'/'local "
    "structure'/'pure transformers'/'semantically meaningful'/'small "
    "weights'/'state across'/'across runs'/'correct answers'/'produces "
    "garbage'/'model families'/'network architectures'/'modern models'/"
    "'modern long-context'/'modern long-context models'/'scales better'/"
    "'single hidden'/'times 4096'/'16 patches'/'1000-class'/'51cf66'/"
    "'vdots', verb fragments 'every spatial'/'every spatial position'/"
    "'add positional'/'attended'/'frees'/'gradient points'/'learn "
    "different'/'scales better'/'sequence attends'/'use linear'/'use "
    "relu'/'across multiple gpus', citation-format fragments 'goodfellow "
    "et'/'goodfellow et al'/'radford et'/'radford et al', code fragments "
    "'every row'/'model saved', truncated phrase 'exponential moving') "
    "plus a strong technical minority (bounding boxes, conditional "
    "generation, loss curve, causality, encoder-decoder models, sora, "
    "low-rank approximation, manhattan distance, non-contiguous, "
    "parameter update, input space, lr scheduler, neural network "
    "architecture, transformer blocks, gradient explosion, ml engineer, "
    "scalar loss). Method: individual evidence review of all 60 brief "
    "blocks + FENCE-AWARE definitional-treatment coverage probe (scripts/"
    "disc002_batch14_probe.py, ~290 terms, scratch/disc002-batch14-probe."
    "json; F-0021 fixed mid-run) + 178-check targeted citation "
    "verification (scripts/disc002_batch14_verify.py, all OK after five "
    "pattern fixes: design-space paraphrase, heading-number prefix '4. "
    "Hierarchical features', formula-on-next-line 'The update rule:', "
    "'to break symmetry' phrasing, bold-marker '**Checkpoint selection**') "
    "+ independent subagent cross-check of ALL 60 judgment calls: 60/60 "
    "first-pass AGREE (SECOND consecutive fully-agreeing tranche). The "
    "subagent flagged TEN cosmetic citation errata; ALL TEN independently "
    "re-verified against the corpus and ACCEPTED (one off-by-one line — "
    "the IoU definition sits at :20, cited as :21 — and nine heading-"
    "LEVEL markers: '### Correlation, Not Causation', '### Doesn't "
    "Explain Causation', '### Encoder-Decoder Models' (Roadmap), '### "
    "Outliers', '### 4. Hierarchical features', '#### The Adam Parameter "
    "Update', '# 2. Neural Network Architecture', '#### The Exploding "
    "Gradient Problem', '### ML Engineer'/'### 4. Machine Learning "
    "Engineer', '### 2. ReLU (Rectified Linear Unit)'). ROOT CAUSE of the "
    "level slips: the verify script's require_heading checks use '^#+' "
    "which matches ANY heading level, so exact-level mismatches pass — "
    "SIXTH session where subagent-erratum re-verification was required, "
    "and this time it caught a verify-script blind spot the orchestrator's "
    "own tool could not see. ONE FURTHER level slip found by the "
    "orchestrator's OWN post-fix level audit ('### One-stage detectors: "
    "YOLO and SSD' at Detection and Segmentation.md:69, cited as '##') — "
    "the symmetric self-verification discipline. NO NEW CONFIRMED GAP "
    "(the nearest misses — exponential moving average and the loss curve "
    "— were probed adversarially by the subagent and both have in-situ "
    "definitional treatments). Decisions: 17 evidence-cited covers + 43 "
    "noise rejects applied (--decided-utc 2026-11-01T03:30:00Z), validate "
    "green, index regenerated and delta-verified PASS ON THE FIRST TRY "
    "(60 changes: 17+43; 60,094 unchanged; counts match the pre-written "
    "arithmetic 51,372-60 / 7,197+17 / 1,580+43; the expectation side "
    "was written down BEFORE the apply). CURRENT: 51,312 provisional / "
    "7,214 already_covered / 1,623 rejected / 3 confirmed_gap (second "
    "moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: "
    "batch-15+ review tranches (4,334 still match the signal rule); "
    "per-domain semantic classification of the dossier-extension overlap "
    "pairs; then disposition assignment before gated synthesis."
)

# --- 1. append F-0021 to findings.jsonl ---
f0021 = {
    "finding_id": "F-0021",
    "category": "tooling-defect",
    "severity": "medium",
    "status": "fixed-in-session",
    "title": "Probe fence_spans mishandled unclosed code fences (explicit null end_line)",
    "discovered_by": "DISC-002 session 14 (2026-11-01)",
    "observed": (
        "scripts/disc002_batch14_probe.py crashed with TypeError: '<=' not "
        "supported between instances of 'int' and 'NoneType' while probing "
        "the mermaid-color term family ('fill:#'): a file with an UNCLOSed "
        "code fence produced a fence span whose end element was None."
    ),
    "expected_condition": (
        "Every code-fence span used by the fence-aware probe must be a "
        "(start, end) pair of integers; an unclosed fence extends to EOF."
    ),
    "root_cause": (
        "mdextract reports end_line=null with closed=false for unclosed "
        "fences; the probe's fence_spans used f.get('end_line', start), "
        "which only defaults when the KEY is absent — an explicit JSON "
        "null slips through as None. The batch-10..13 probes (and their "
        "docstring comment 'mdextract reports end_line as the last line') "
        "share the latent defect."
    ),
    "evidence": (
        "src/vault_unification/mdextract.py _flush_fence (end_line None "
        "when unclosed, 'closed': end_line is not None, lines 153-167); "
        "the session-14 crash traceback in the tool log; the fixed "
        "scripts/disc002_batch14_probe.py fence_spans(struct, total_lines)."
    ),
    "impact": (
        "Batches 10-13 were NOT affected in practice: no probed term in "
        "those tranches matched a definition pattern inside an unclosed "
        "fence, so no heading/def classification changed. Had it "
        "triggered, an in-fence '#'-comment or def-pattern hit could have "
        "been misclassified as out-of-fence coverage evidence."
    ),
    "repair": (
        "fence_spans now takes total_lines and maps end_line None -> "
        "total_lines (span extends to EOF). Applied in "
        "scripts/disc002_batch14_probe.py; future probe scripts must copy "
        "the batch-14 pattern, not the batch-13 one."
    ),
    "verification": (
        "The fixed probe re-ran to completion: 290 terms, exit 0, results "
        "at scratch/disc002-batch14-probe.json. The 173 pre-fix OK verify "
        "checks were unaffected (fence classification identical for all "
        "closed-fence files)."
    ),
    "regression_prevention": (
        "Batch-15+ probe scripts MUST use the F-0021-fixed fence_spans "
        "signature (struct, total_lines). Optionally add a unit test with "
        "an unclosed-fence fixture if the probe logic is promoted into "
        "the framework package."
    ),
    "remaining_risk": (
        "The batch-10..13 probe scripts in the repo still contain the "
        "latent defect (historical artifacts, not re-run); their JSON "
        "results remain valid per the impact analysis."
    ),
}
with open(FINDINGS, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(f0021, ensure_ascii=False) + "\n")

# --- 2. update the DISC-002 task-queue entry ---
lines = QUEUE.read_text(encoding="utf-8").splitlines()
queue = [json.loads(l) for l in lines if l.strip()]
for t in queue:
    if t.get("task_id") == "DISC-002":
        t["notes"] = QUEUE_NOTES
        if "F-0021" not in t.get("findings", []):
            t["findings"] = t.get("findings", []) + ["F-0021"]
        break
else:
    raise SystemExit("DISC-002 task not found in queue")
with open(QUEUE, "w", encoding="utf-8") as fh:
    for t in queue:
        fh.write(json.dumps(t, ensure_ascii=False) + "\n")

# --- 3. update current-state.json ---
state = json.loads(STATE.read_text(encoding="utf-8"))
state["stage"] = "disc002-review-batch14-done"
state["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-11-01-disc002-session14.json"
state["notes"] = (
    "DISC-002 in progress; session 14 re-verified the baseline (663/663 "
    "tests at start — the editable install was run FIRST, so no failed "
    "baseline run this time; both vaults byte-identical to manifests at "
    "start, HEAD == origin/main == 2d577cd), extended the ADR-0010 replay "
    "to FOURTEEN decide rounds (content-identical to the committed index "
    "on the first try; expected 51,372/7,197/1,580/3/1/1 matched "
    "exactly), found and fixed ONE new tooling defect (F-0021: probe "
    "fence_spans mishandled unclosed fences' explicit-null end_line; "
    "fixed to extend to EOF, batch-10..13 probes carry the latent defect "
    "but never triggered it), and completed the batch-14 review tranche: "
    "60 highest-signal unreviewed candidates (4,394 matching the signal "
    "rule — exactly the session-13 prediction), ~290-term fence-aware "
    "coverage probe + 178-check citation verification (all OK after five "
    "pattern fixes) + independent subagent cross-check of ALL 60 judgment "
    "calls: 60/60 first-pass AGREE (second consecutive fully-agreeing "
    "tranche). TEN subagent errata flagged and ALL independently "
    "re-verified and ACCEPTED (one off-by-one IoU line :20 vs :21, nine "
    "heading-LEVEL markers — root cause: the verify script's '^#+' "
    "require_heading pattern matches any level, a blind spot the "
    "subagent caught); ONE further level slip found by the orchestrator's "
    "own post-fix audit ('### One-stage detectors' at :69). Decisions: "
    "17 evidence-cited covers + 43 noise rejects applied (--decided-utc "
    "2026-11-01T03:30:00Z), validate green, index regenerated and "
    "delta-verified PASS on the first try (counts match the pre-written "
    "arithmetic 51,372-60 / 7,197+17 / 1,580+43). NO NEW CONFIRMED GAP "
    "(nearest misses 'exponential moving average' and 'loss curve' both "
    "have in-situ definitional treatments). CURRENT: 51,312 provisional / "
    "7,214 already_covered / 1,623 rejected / 3 confirmed_gap (second "
    "moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: "
    "batch-15+ review tranches (4,334 still match the signal rule); "
    "per-domain semantic classification of the dossier-extension overlap "
    "pairs; then disposition assignment before gated synthesis."
)
dz = state["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]
dz["final_statuses"] = {
    "provisional_candidate": 51312,
    "already_covered": 7214,
    "rejected": 1623,
    "confirmed_gap": 3,
    "merged": 1,
    "deferred": 1,
}
dz["decisions_chain"] = dz["decisions_chain"] + [
    "state/concept-candidates/002-disc002-decisions-batch14.jsonl (60)"
]
dz["replay_decided_utc"]["batch14"] = "2026-11-01T03:30:00Z"
state["phase_zero_rebaseline"]["disc002_full_corpus_discovery"] = dz
STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# --- 4. write the session checkpoint ---
checkpoint = {
    "checkpoint_id": "checkpoint-2026-11-01-disc002-session14",
    "task_id": "DISC-002",
    "written_utc": "2026-11-01T03:30:00Z",
    "session_summary": {
        "baseline_verification": (
            "Clean tree at session start with HEAD == origin/main == "
            "2d577cd (git status, git log verified). Fresh-sandbox setup "
            "run FIRST per the session-13 lesson: 'python3 -m pip install "
            "-e .' before pytest — the baseline passed 663/663 on the "
            "first run (reports/discovery/disc002-session14-baseline-"
            "pytest.json; no failed un-installed run this session). Both "
            "vaults byte-identical to committed manifests at session "
            "start (reports/discovery/disc002-session14-manifest-"
            "{ai-course,master-ai}.json; 0 added/removed/changed). "
            "Committed index verified via replay (below): 60,154 records, "
            "51,372/7,197/1,580/3/1/1 — matching the session-13 handoff "
            "exactly."
        ),
        "adr0010_replay": (
            "FOURTEEN decide rounds replayed via scripts/"
            "disc002_batch14_replay.py (r1 2026-10-28T00:45:00Z, r2 "
            "01:30:00Z, batch2 02:30:00Z, batch3 05:30:00Z, batch4 "
            "2026-10-30T13:05:00Z, batch5 15:30:00Z, batch6 16:30:00Z, "
            "batch7 2026-10-31T00:30:00Z, batch8 01:30:00Z, batch9 "
            "03:00:00Z, batch10 05:30:00Z, batch11 08:00:00Z, batch12 "
            "10:30:00Z, batch13 13:30:00Z), then discovery-index — "
            "CONTENT-IDENTICAL to the committed index (60,154 records; "
            "51,372/7,197/1,580/3/1/1; F-0019 content-comparison; the "
            "replay ran clean on the FIRST try; validate green; reports/"
            "discovery/disc002-s14-replay-*.json; post-batch13 chain "
            "state preserved at scratch/disc002-s14-batch13.jsonl)."
        ),
        "f0021_defect": (
            "NEW tooling defect found and fixed in session: the probe "
            "family's fence_spans mishandled UNCLOSed code fences — "
            "mdextract reports end_line=null with closed=false, and "
            "f.get('end_line', start) does not default an explicit null, "
            "so the span comparison crashed (TypeError) when the "
            "batch-14 probe hit the 'fill:#' mermaid-color term family. "
            "Fixed: unclosed spans extend to EOF (total_lines). Recorded "
            "as F-0021 in state/findings.jsonl with full impact analysis "
            "(batches 10-13 unaffected: no probed term matched a def "
            "pattern inside an unclosed fence). Future probes MUST copy "
            "the batch-14 fence_spans signature."
        ),
        "batch14_tranche": (
            "60 highest-signal unreviewed provisional candidates selected "
            "(scripts/disc002_batch14_tranche.py; 4,394 matching the "
            "signal rule of 51,372 unreviewed — exactly the session-13 "
            "handoff prediction; CAND at scratch/disc002-s14-batch13."
            "jsonl). Method: individual evidence review of all 60 brief "
            "blocks + fence-aware definitional-treatment coverage probe "
            "(scripts/disc002_batch14_probe.py, ~290 terms, scratch/"
            "disc002-batch14-probe.json) + 178-check targeted citation "
            "verification (scripts/disc002_batch14_verify.py — all OK "
            "after five pattern fixes: a paraphrased design-space quote "
            "replaced with the verbatim '(the RNN version of this design "
            "space)'; heading-number prefix '### 4. Hierarchical "
            "features'; 'The update rule:' formula on the following line; "
            "'to break symmetry (so neurons learn different features)' "
            "phrasing; '**Checkpoint selection**: save checkpoints "
            "periodically' bold markers and :206 line) + independent "
            "subagent cross-check of ALL 60 judgment calls: 60/60 "
            "first-pass AGREE (second consecutive fully-agreeing "
            "tranche). The subagent flagged TEN cosmetic citation errata; "
            "ALL TEN were INDEPENDENTLY RE-VERIFIED against the corpus "
            "and ACCEPTED: the IoU definitional sentence is at :20 (was "
            "cited :21; the formula is at :22) and nine heading-LEVEL "
            "markers were wrong ('### Correlation, Not Causation' "
            "Probing.md:84; '### Doesn't Explain Causation' Logit Lens:"
            "146; '### Encoder-Decoder Models' Roadmap:210; '### "
            "Outliers' Linear Regression from Scratch:282; '### 4. "
            "Hierarchical features' CNNs:40; '#### The Adam Parameter "
            "Update' Hyperparameters Summary:387; '# 2. Neural Network "
            "Architecture' Fundamentals:40; '#### The Exploding Gradient "
            "Problem' Weight Init Techniques:20; '### ML Engineer' AI "
            "Engineer Roles:74 / '### 4. Machine Learning Engineer' "
            "Careers:32; '### 2. ReLU (Rectified Linear Unit)' "
            "Fundamentals:145). ROOT CAUSE: the verify script's "
            "require_heading uses '^#+' which matches ANY heading level, "
            "so exact-level citation slips pass — the subagent caught a "
            "verify-script blind spot (sixth consecutive session where "
            "subagent-erratum re-verification was required; it cut both "
            "ways again: all ten were right this time). ONE further "
            "level slip found by the orchestrator's OWN post-fix audit: "
            "'### One-stage detectors: YOLO and SSD' at Detection and "
            "Segmentation.md:69 (cited '##')."
        ),
        "decisions_and_delta": (
            "Decisions emitted by scripts/disc002_batch14_decisions.py -> "
            "state/concept-candidates/002-disc002-decisions-batch14.jsonl "
            "(IDs D-DISC002-B14-0001..0060; candidate IDs asserted against "
            "the selection file). 17 covers + 43 rejects. Applied with "
            "'vu discovery-decide --decided-utc 2026-11-01T03:30:00Z' "
            "(reports/discovery/disc002-s14-decide-batch14.json; "
            "decisions_applied 2004 cumulative — consistent with the "
            "committed chain: batch-12 replay decide reported 1884, "
            "+60 batch13 +60 batch14). Delta verification PASSED ON THE "
            "FIRST TRY (scripts/disc002_batch14_delta.py; expectation "
            "arithmetic pre-written: 51,372-60 / 7,197+17 / 1,580+43): 60 "
            "status changes (17 provisional->already_covered, 43 "
            "provisional->rejected), 60,094 unchanged, history cleanly "
            "appended for all 60, final counts 51,312/7,214/1,623/3/1/1 "
            "exactly as expected. Index regenerated (60,154 records; "
            "reports/discovery/disc002-s14-index-postbatch14.json) and "
            "'vu discovery-validate' green (0 errors; reports/discovery/"
            "disc002-s14-validate-postbatch14.json)."
        ),
        "no_new_gap": (
            "NO NEW CONFIRMED GAP this tranche. The subagent probed the "
            "two nearest misses adversarially: 'exponential moving "
            "average' has an operational definition at Batch "
            "Normalization.md:122-128 ('updated using an exponential "
            "moving average (EMA)... preferred over a simple average "
            "because it gives more weight to recent batches') plus the "
            "momentum-velocity gloss (Optimizers Deep Dive:272), and the "
            "loss curve has the LR-range-test operational definition "
            "(Hyperparameters:140 'plotting the loss. The optimal "
            "learning rate is typically near the steepest point of the "
            "loss curve') plus the learning-curve definitional treatment "
            "(master-ai Bias Variance Tradeoff:254-256). Gap-shaped "
            "candidates resolved: 'sora' COVER via in-situ glosses "
            "(Multimodal AI Overview:72-73 heading + 'Text-to-video "
            "generation. Minutes-long, high quality.'; DiT and FLUX:114 "
            "'Sora (OpenAI's video generation model) uses a DiT-based "
            "architecture' — the OpenHermes named-entity precedent); "
            "'causality' COVER via the interpretability domain ("
            "activation patching 'gold standard for establishing "
            "causality' :11; probing 'Correlation, Not Causation' :84; "
            "logit lens 'Doesn't Explain Causation' :146) plus the "
            "regression-assumption framing; 'goodfellow et al'/'radford "
            "et al' REJECTED as citation-format fragments whose entity/"
            "model sides are covered (batch-13 goodfellow cover; "
            "dedicated CLIP/GPT-2/GAN notes); 'vdots' REJECTED as a "
            "LaTeX artifact (lfloor/rfloor/cos/sin batch-13 precedent). "
            "Corpus confirmed_gap total stays 3 (second moment, "
            "bradley-terry, async def)."
        ),
    },
    "tests_and_evidence": {
        "baseline_pytest": "reports/discovery/disc002-session14-baseline-pytest.json (663/663)",
        "manifest_checks": [
            "reports/discovery/disc002-session14-manifest-ai-course.json (0 diff)",
            "reports/discovery/disc002-session14-manifest-master-ai.json (0 diff)",
        ],
        "replay_reports": "reports/discovery/disc002-s14-replay-*.json (14 rounds + index + validate)",
        "probe_results": "scratch/disc002-batch14-probe.json (~290 terms)",
        "citation_verification": "scripts/disc002_batch14_verify.py (178/178 OK)",
        "subagent_cross_check": "60/60 first-pass AGREE; 10 errata flagged, all 10 independently re-verified and accepted; 1 additional self-audited level slip fixed",
        "decide_report": "reports/discovery/disc002-s14-decide-batch14.json",
        "delta_report": "scratch/disc002-batch14-delta.json (PASS first try)",
        "index_report": "reports/discovery/disc002-s14-index-postbatch14.json",
        "validate_report": "reports/discovery/disc002-s14-validate-postbatch14.json (0 errors)",
        "final_pytest": "reports/discovery/disc002-session14-final-pytest.json (to be run after the last mutation; recorded here once available)",
    },
    "git_state_at_write": "to be filled after commit; see the state commit message",
    "next_task": (
        "DISC-002 batch-15 review tranche: copy the batch-14 script "
        "pattern (scripts/disc002_batch14_{replay,tranche,probe,decisions,"
        "verify,delta}.py -> batch15; CAND at scratch/disc002-s15-batch14."
        "jsonl after a fifteen-round replay; decision IDs D-DISC002-"
        "B15-****). Use the F-0021-FIXED fence_spans from the batch-14 "
        "probe (signature fence_spans(struct, total_lines)); consider "
        "level-exact heading patterns in the verify script (the '^#+' "
        "blind spot). Expected pool: 4,334 matching the signal rule of "
        "51,312 unreviewed. After the tranches: dossier-extension "
        "classification, then disposition assignment before gated "
        "synthesis."
    ),
}
CHECKPOINT.write_text(json.dumps(checkpoint, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print("state updates written:")
print(" -", FINDINGS, "(F-0021 appended)")
print(" -", QUEUE, "(DISC-002 notes updated)")
print(" -", STATE, "(stage/notes/final_statuses/chain/batch14 utc)")
print(" -", CHECKPOINT)
