#!/usr/bin/env python3
"""DISC-002 session 15 (batch 15): persist task-queue, current-state, checkpoint.

No new finding this session (F-0021 fix held — the batch-15 probe ran the
F-0021-fixed fence_spans(struct, total_lines) clean, exit 0), so
state/findings.jsonl is NOT appended. The session-14 '^#+' verify blind
spot is closed STRUCTURALLY by the batch-15 verify script's level-exact
heading guard (every require_heading pattern must be '^### '-style; the
guard rejects '^#+' patterns) — a process improvement, not a defect.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state/task-queue.jsonl"
STATE = REPO / "state/current-state.json"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-01-disc002-session15.json"

QUEUE_NOTES = (
    "DISC-002 IN PROGRESS - session 15 (2026-11-01). Baseline independently "
    "re-verified at session start: clean tree with HEAD == origin/main == "
    "541d046; 663/663 tests after the documented editable install "
    "(reports/discovery/disc002-session15-baseline-pytest.json; the "
    "fresh-sandbox setup 'python3 -m pip install -e .' was run FIRST — "
    "the session-13/14 lesson held again, first-run pass); both vaults "
    "byte-identical to committed manifests at session start "
    "(reports/discovery/disc002-session15-manifest-{ai-course,master-ai}."
    "json; 0 added/removed/changed; 276+333 files). ADR-0010 replay "
    "extended to FIFTEEN decide rounds via scripts/disc002_batch15_replay."
    "py (r1+r2+batch2..batch14 replayed with recorded --decided-utc "
    "values, then discovery-index) — CONTENT-IDENTICAL to the committed "
    "index (60,154 records; status counts matched exactly: "
    "51,312/7,214/1,623/3/1/1; validate green; F-0019 heeded; replay ran "
    "clean on the FIRST try; post-batch14 chain state preserved as the "
    "CAND at scratch/disc002-s15-batch14.jsonl; session-15 environmental "
    "note: replay intermediates were deleted as consumed — the scratch "
    "volume could not hold sixteen ~259MB states — a disk constraint, "
    "not a semantic change; chain states are deterministic replays of "
    "committed inputs per ADR-0010). NO NEW TOOLING DEFECT: the batch-15 "
    "probe copied the F-0021-FIXED fence_spans(struct, total_lines) "
    "verbatim from scripts/disc002_batch14_probe.py and ran clean (267 "
    "terms, exit 0). BATCH 15 REVIEW TRANCHE: 60 highest-signal "
    "unreviewed provisional candidates (4,334 matching the signal rule "
    "of 51,312 unreviewed — exactly the session-14 handoff prediction; "
    "scripts/disc002_batch15_tranche.py, repo-relative, CAND at scratch/"
    "disc002-s15-batch14.jsonl). Tranche character: 50 fragmented_"
    "derivation fragments (verb fragments 'backpropagation computes'/"
    "'method uses'/'newton's method uses'/'predicts hidden'/'releasing'/"
    "'update learning', code-comment fragments 'clear gradients'/'clear "
    "previous'/'clear previous gradients'/'previous gradients'/'convert "
    "pil'/'early stopping triggered'/'stopping triggered'/'gpu "
    "transfer'/'load pre-trained resnet-50'/'new fc'/'new layer'/"
    "'randomly flip'/'second conv'/'update learning rate', f-string "
    "artifact 'f'epoch', prose fragments 'cheap draft'/'classification "
    "networks'/'fine-tuning pre-trained'/'global avg'/'global avg "
    "pool'/'hessian information'/'need paired'/'negative error'/"
    "'overall accuracy'/'per-channel means'/'pool gradients'/'positive "
    "contributions'/'prompt-derived'/'repetitive content'/'right edge'/"
    "'total samples'/'update step'/'zero-padding added'/'vlm backbone'-"
    "adjacent, and a seven-candidate VAULT-MANAGEMENT META-PROSE family "
    "from master-ai '00 - Vault Management/Architecture Decisions.md' — "
    "'candidate note'/'concrete gaps'/'identify concrete'/'identify "
    "concrete gaps'/'missing sections'/'never remove'/'note "
    "substantially' — the vault's own iteration-11 construction record, "
    "not learning content) plus a strong ten-term technical minority "
    "(memories, pre-trained model, preference data, mamba-2's, "
    "rule-based, web search, output node, chat template, paging, plus "
    "the gap-shaped named entity 'tulu'). Method: individual evidence "
    "review of all 60 brief blocks + FENCE-AWARE definitional-treatment "
    "coverage probe (scripts/disc002_batch15_probe.py, 267 terms, "
    "scratch/disc002-batch15-probe.json, F-0021-fixed fence_spans) + "
    "168-check targeted citation verification with the NEW LEVEL-EXACT "
    "heading discipline (scripts/disc002_batch15_verify.py — every "
    "require_heading pattern is '^### '-style level-exact and the "
    "script's startup guard REJECTS '^#+' patterns, closing the "
    "session-14 blind spot structurally; all OK after four pattern "
    "fixes: the f-string quote tail \"print(f'Epoch [{epoch+1}/"
    "{num_epochs}], '\", the '.to(device)' backtick removal, the "
    "'second conv' comment is '# Batch normalization after second "
    "conv', and the scheduler comment is '# Update learning rate') + "
    "independent subagent cross-check of ALL 60 judgment calls: 60/60 "
    "first-pass AGREE (THIRD consecutive fully-agreeing tranche). The "
    "subagent flagged TWELVE citation errata and four strengthening "
    "citations; ALL TWELVE independently re-verified against the corpus "
    "and ACCEPTED (three heading-LEVEL markers on sibling phrasings the "
    "orchestrator's bulk fix had missed — '## Mistake 1: Forgetting "
    "optimizer.zero_grad()', '# 6. Advanced Pooling Mechanisms and "
    "Global Average Pooling', '## Draft Model Choices'; the '[!warning] "
    "Wrong Normalization = Broken Pre-Trained Model' callout title sits "
    "at :479 with the body at :480; the 'gradients are *added*' clause "
    "at :263 with '**Why accumulation is the default**' at :265; the "
    "'a Python float, releasing the graph' comment belongs to PyTorch "
    "Implementation Basics.md:574-575, not to the Backprop CNNs note; "
    "the N-gram note title is '# 07 - N-gram Language Models' at :9 "
    "after frontmatter; the notation note title is at :3 not :1; the "
    "ResNet transform block is :594-597 — crop :595, flip :596, "
    "ToTensor :597) and ALL FOUR strengthening citations verified real "
    "and incorporated (Mini Agent 'web_search: Search the web for "
    "current information.' :150 and 'def web_search(query...)' :59; "
    "A-Z Terms '**Chat template** — format for wrapping user/assistant "
    "messages' :48 and '**Memory** — persistent state for agents' :166; "
    "Acronyms Index '**VLM** — Vision-Language Model' :202). SEVENTH "
    "consecutive session where subagent-erratum re-verification was "
    "required — this time all twelve were right, and the level-exact "
    "verify guard means the heading-level erratum CLASS is now "
    "structurally prevented (the subagent found no NEW heading-level "
    "error that the guard passed; the three it found were in rationale "
    "prose the machine checks had already fixed for the sibling "
    "phrasings). NO NEW CONFIRMED GAP (gap-watch verdict: none — the "
    "subagent independently confirmed 'tulu' has exactly 4 corpus "
    "occurrences, all bare example-list mentions with no gloss "
    "anywhere including both glossaries and quiz blocks, and is never "
    "in dependency position, so it fails the confirm_gap dependency "
    "test and the OpenHermes/Sora in-situ-gloss cover precedents do "
    "not apply — REJECT stands as the first bare-named-entity reject "
    "precedent; 'web search' is COVERED via operational treatments "
    "including the tool-registry gloss; 'chat template' additionally "
    "has the A-Z Terms glossary entry). Decisions: 12 evidence-cited "
    "covers (class index, output spatial size, vlm backbone, memories, "
    "pre-trained model, preference data, mamba-2's, rule-based, web "
    "search, output node, chat template, paging) + 48 noise rejects "
    "applied (--decided-utc 2026-11-01T04:15:00Z), validate green, "
    "index regenerated and delta-verified PASS ON THE FIRST TRY (60 "
    "changes: 12+48; 60,094 unchanged; counts match the pre-written "
    "arithmetic 51,312-60 / 7,214+12 / 1,623+48; the expectation side "
    "was written down BEFORE the apply; decisions_applied 2064 "
    "cumulative — consistent with the committed chain: batch-14 "
    "reported 2004). CURRENT: 51,252 provisional / 7,226 "
    "already_covered / 1,671 rejected / 3 confirmed_gap (second "
    "moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: "
    "batch-16+ review tranches (4,274 still match the signal rule — "
    "the session-15 prediction); per-domain semantic classification of "
    "the dossier-extension overlap pairs; then disposition assignment "
    "before gated synthesis."
)

# --- 1. (no findings append: no new defect found and fixed this session) ---

# --- 2. update the DISC-002 task-queue entry ---
lines = QUEUE.read_text(encoding="utf-8").splitlines()
queue = [json.loads(l) for l in lines if l.strip()]
for t in queue:
    if t.get("task_id") == "DISC-002":
        t["notes"] = QUEUE_NOTES
        break
else:
    raise SystemExit("DISC-002 task not found in queue")
with open(QUEUE, "w", encoding="utf-8") as fh:
    for t in queue:
        fh.write(json.dumps(t, ensure_ascii=False) + "\n")

# --- 3. update current-state.json ---
state = json.loads(STATE.read_text(encoding="utf-8"))
state["stage"] = "disc002-review-batch15-done"
state["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-11-01-disc002-session15.json"
state["notes"] = (
    "DISC-002 in progress; session 15 re-verified the baseline (663/663 "
    "tests at start — the editable install was run FIRST, first-run "
    "pass; both vaults byte-identical to manifests at start, HEAD == "
    "origin/main == 541d046), extended the ADR-0010 replay to FIFTEEN "
    "decide rounds (content-identical to the committed index on the "
    "first try; expected 51,312/7,214/1,623/3/1/1 matched exactly; "
    "disk-frugal intermediates — deleted as consumed, only the CAND "
    "scratch/disc002-s15-batch14.jsonl preserved), found NO new tooling "
    "defect (the F-0021-fixed fence_spans held: the batch-15 probe ran "
    "267 terms clean), and completed the batch-15 review tranche: 60 "
    "highest-signal unreviewed candidates (4,334 matching the signal "
    "rule — exactly the session-14 prediction), 267-term fence-aware "
    "coverage probe + 168-check citation verification with the NEW "
    "LEVEL-EXACT heading discipline (every require_heading pattern is "
    "'^### '-style and a startup guard rejects '^#+' — the session-14 "
    "blind spot closed structurally; all OK after four pattern fixes) + "
    "independent subagent cross-check of ALL 60 judgment calls: 60/60 "
    "first-pass AGREE (third consecutive fully-agreeing tranche). "
    "TWELVE subagent errata flagged and ALL independently re-verified "
    "and ACCEPTED (three sibling-phrasing heading-LEVEL markers, the "
    ":479/:480 warning callout anchor, the :263/:265 accumulation "
    "clause, the 'releasing the graph' note attribution, the N-gram "
    ":9 and notation :3 title anchors, the ResNet :594-597 transform "
    "block); FOUR strengthening citations verified and incorporated "
    "(Mini Agent web_search :59/:150; A-Z Terms chat template :48 and "
    "Memory :166; Acronyms Index VLM :202). Decisions: 12 evidence-"
    "cited covers + 48 noise rejects applied (--decided-utc "
    "2026-11-01T04:15:00Z), validate green, index regenerated and "
    "delta-verified PASS on the first try (counts match the pre-written "
    "arithmetic 51,312-60 / 7,214+12 / 1,623+48). NO NEW CONFIRMED GAP "
    "('tulu' adversarially probed: 4 bare example-list occurrences, no "
    "gloss anywhere, not dependency position — reject stands; 'web "
    "search' COVERED via operational treatments; 'chat template' "
    "additionally glossary-covered). CURRENT: 51,252 provisional / "
    "7,226 already_covered / 1,671 rejected / 3 confirmed_gap (second "
    "moment, bradley-terry, async def) / 1 merged / 1 deferred. NEXT: "
    "batch-16+ review tranches (4,274 still match the signal rule); "
    "per-domain semantic classification of the dossier-extension "
    "overlap pairs; then disposition assignment before gated synthesis."
)
dz = state["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]
dz["final_statuses"] = {
    "provisional_candidate": 51252,
    "already_covered": 7226,
    "rejected": 1671,
    "confirmed_gap": 3,
    "merged": 1,
    "deferred": 1,
}
dz["decisions_chain"] = dz["decisions_chain"] + [
    "state/concept-candidates/002-disc002-decisions-batch15.jsonl (60)"
]
dz["replay_decided_utc"]["batch15"] = "2026-11-01T04:15:00Z"
state["phase_zero_rebaseline"]["disc002_full_corpus_discovery"] = dz
STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# --- 4. write the session checkpoint ---
checkpoint = {
    "checkpoint_id": "checkpoint-2026-11-01-disc002-session15",
    "task_id": "DISC-002",
    "written_utc": "2026-11-01T04:15:00Z",
    "session_summary": {
        "baseline_verification": (
            "Clean tree at session start with HEAD == origin/main == "
            "541d046 (git status, git log verified). Fresh-sandbox setup "
            "run FIRST per the session-13/14 lesson: 'python3 -m pip "
            "install -e .' before pytest — the baseline passed 663/663 "
            "on the first run (reports/discovery/disc002-session15-"
            "baseline-pytest.json, 216.4s). Both vaults byte-identical "
            "to committed manifests at session start (reports/discovery/"
            "disc002-session15-manifest-{ai-course,master-ai}.json; 0 "
            "added/removed/changed; 276+333 files). Committed index "
            "verified via replay (below): 60,154 records, "
            "51,312/7,214/1,623/3/1/1 — matching the session-14 handoff "
            "exactly."
        ),
        "adr0010_replay": (
            "FIFTEEN decide rounds replayed via scripts/"
            "disc002_batch15_replay.py (r1 2026-10-28T00:45:00Z, r2 "
            "01:30:00Z, batch2 02:30:00Z, batch3 05:30:00Z, batch4 "
            "2026-10-30T13:05:00Z, batch5 15:30:00Z, batch6 16:30:00Z, "
            "batch7 2026-10-31T00:30:00Z, batch8 01:30:00Z, batch9 "
            "03:00:00Z, batch10 05:30:00Z, batch11 08:00:00Z, batch12 "
            "10:30:00Z, batch13 13:30:00Z, batch14 2026-11-01T03:30:00Z), "
            "then discovery-index — CONTENT-IDENTICAL to the committed "
            "index (60,154 records; 51,312/7,214/1,623/3/1/1; F-0019 "
            "content-comparison; the replay ran clean on the FIRST try; "
            "validate green; reports/discovery/disc002-s15-replay-*.json; "
            "post-batch14 chain state preserved as the CAND at scratch/"
            "disc002-s15-batch14.jsonl). DISK NOTE: each chain state is "
            "~259MB and the scratch volume could not hold sixteen "
            "simultaneous intermediates, so each was deleted as soon as "
            "its successor was written (only the final CAND preserved) — "
            "an environmental constraint, not a semantic change; chain "
            "states are deterministic replays of committed inputs."
        ),
        "no_new_defect": (
            "NO new tooling defect this session. The batch-15 probe "
            "copied the F-0021-FIXED fence_spans(struct, total_lines) "
            "verbatim from scripts/disc002_batch14_probe.py and ran "
            "clean end-to-end (267 terms, exit 0, results at scratch/"
            "disc002-batch15-probe.json) — the session-14 fix held. The "
            "session-14 '^#+' verify blind spot is closed STRUCTURALLY: "
            "scripts/disc002_batch15_verify.py enforces LEVEL-EXACT "
            "heading patterns (every require_heading check uses '^### '-"
            "style literals; a startup guard rejects any '^#+' pattern), "
            "so an exact-level citation slip now fails loudly."
        ),
        "batch15_tranche": (
            "60 highest-signal unreviewed provisional candidates selected "
            "(scripts/disc002_batch15_tranche.py; 4,334 matching the "
            "signal rule of 51,312 unreviewed — exactly the session-14 "
            "handoff prediction; CAND at scratch/disc002-s15-batch14."
            "jsonl). Method: individual evidence review of all 60 brief "
            "blocks + fence-aware definitional-treatment coverage probe "
            "(scripts/disc002_batch15_probe.py, 267 terms, scratch/"
            "disc002-batch15-probe.json, F-0021-fixed fence_spans) + "
            "168-check targeted citation verification (scripts/"
            "disc002_batch15_verify.py — LEVEL-EXACT heading discipline "
            "with the startup guard; all OK after four pattern fixes: "
            "the f-string quote tail, the '.to(device)' backtick, the "
            "'# Batch normalization after second conv' comment text, "
            "and the '# Update learning rate' comment text) + "
            "independent subagent cross-check of ALL 60 judgment calls: "
            "60/60 first-pass AGREE (THIRD consecutive fully-agreeing "
            "tranche). The subagent flagged TWELVE citation errata and "
            "FOUR strengthening citations; ALL TWELVE errata were "
            "INDEPENDENTLY RE-VERIFIED against the corpus and ACCEPTED "
            "(three heading-LEVEL markers on sibling phrasings the "
            "orchestrator's bulk fix had missed: '## Mistake 1: "
            "Forgetting optimizer.zero_grad()' Common Mistakes:10, "
            "'# 6. Advanced Pooling Mechanisms and Global Average "
            "Pooling' GAP note:1, '## Draft Model Choices' Speculative "
            "Decoding:61; the '[!warning] Wrong Normalization = Broken "
            "Pre-Trained Model' title at Data Augmentation:479 with "
            "body :480; the 'gradients are *added*' clause at Backprop "
            "CNNs:263 vs '**Why accumulation is the default**' :265; "
            "the 'a Python float, releasing the graph' comment belongs "
            "to PyTorch Implementation Basics:574-575, not the Backprop "
            "CNNs note and not :578; the N-gram note title '# 07 - "
            "N-gram Language Models' at :9 after frontmatter; the "
            "notation note title '# Mathematical Notation in Linear "
            "Regression: A Deep Dive' at :3; the ResNet transform "
            "block :594-597 — RandomResizedCrop :595, "
            "RandomHorizontalFlip :596, ToTensor :597); ALL FOUR "
            "strengthening citations verified real and incorporated "
            "(Mini Agent 'web_search: Search the web for current "
            "information.' :150 and 'def web_search(query: str, "
            "max_results: int = 5) -> str:' :59; A-Z Terms '**Chat "
            "template** — format for wrapping user/assistant messages' "
            ":48 and '**Memory** — persistent state for agents' :166; "
            "Acronyms Index '**VLM** — Vision-Language Model' :202). "
            "SEVENTH consecutive session where subagent-erratum "
            "re-verification was required and cut both ways in "
            "principle — all twelve were right this time, and the "
            "level-exact guard now prevents the heading-level erratum "
            "class structurally."
        ),
        "decisions_and_delta": (
            "Decisions emitted by scripts/disc002_batch15_decisions.py -> "
            "state/concept-candidates/002-disc002-decisions-batch15.jsonl "
            "(IDs D-DISC002-B15-0001..0060; candidate IDs asserted against "
            "the selection file). 12 covers + 48 rejects. Applied with "
            "'vu discovery-decide --decided-utc 2026-11-01T04:15:00Z' "
            "(reports/discovery/disc002-s15-decide-batch15.json; "
            "decisions_applied 2064 cumulative — consistent with the "
            "committed chain: batch-14 reported 2004, +60 batch15). "
            "Delta verification PASSED ON THE FIRST TRY (scripts/"
            "disc002_batch15_delta.py; expectation arithmetic pre-written: "
            "51,312-60 / 7,214+12 / 1,623+48): 60 status changes (12 "
            "provisional->already_covered, 48 provisional->rejected), "
            "60,094 unchanged, history cleanly appended for all 60, "
            "final counts 51,252/7,226/1,671/3/1/1 exactly as expected. "
            "Index regenerated (60,154 records; reports/discovery/"
            "disc002-s15-index-postbatch15.json) and 'vu "
            "discovery-validate' green (0 errors; reports/discovery/"
            "disc002-s15-validate-postbatch15.json)."
        ),
        "no_new_gap": (
            "NO NEW CONFIRMED GAP this tranche (gap-watch verdict: "
            "none). 'tulu' was adversarially probed by both the "
            "orchestrator and the subagent: exactly 4 corpus occurrences "
            "(master-ai DPO Derivation:182, Instruction Tuning and Chat "
            "Templates:159, DPO 2023:133/:175), all bare example-list "
            "mentions; NO in-situ gloss (both glossaries and the quiz "
            "banks checked — no entry); NOT in dependency position "
            "(every occurrence's load-bearing concepts — DPO, "
            "instruction tuning, synthetic data, open-weights alignment "
            "— have dedicated treatments); so the confirm_gap dependency "
            "test FAILS and the OpenHermes/Sora in-situ-gloss cover "
            "precedents do not apply — REJECT stands (the first "
            "bare-named-entity reject precedent). Gap-shaped covers: "
            "'web search' via operational treatments (ReAct fresh-"
            "information motivation :16/:426; Mini Agent tool set :12/"
            ":19 with the tool-registry gloss :150 and implementation "
            ":59; MCP tool category :118); 'chat template' via the "
            "dedicated instruction-tuning note (:9/:53/:149) plus the "
            "A-Z Terms glossary entry :48; 'memories' via FFN key-value "
            "memories (:97/:98) plus the memory-systems chapter (:12) "
            "and glossary :166. Corpus confirmed_gap total stays 3 "
            "(second moment, bradley-terry, async def)."
        ),
    },
    "tests_and_evidence": {
        "baseline_pytest": "reports/discovery/disc002-session15-baseline-pytest.json (663/663)",
        "manifest_checks": [
            "reports/discovery/disc002-session15-manifest-ai-course.json (0 diff)",
            "reports/discovery/disc002-session15-manifest-master-ai.json (0 diff)",
        ],
        "replay_reports": "reports/discovery/disc002-s15-replay-*.json (15 rounds + index + validate)",
        "probe_results": "scratch/disc002-batch15-probe.json (267 terms, F-0021-fixed fence_spans, exit 0)",
        "citation_verification": "scripts/disc002_batch15_verify.py (168/168 OK, level-exact heading guard)",
        "subagent_cross_check": "60/60 first-pass AGREE; 12 errata flagged, all 12 independently re-verified and accepted; 4 strengthening citations verified and incorporated",
        "decide_report": "reports/discovery/disc002-s15-decide-batch15.json",
        "delta_report": "scratch/disc002-batch15-delta.json (PASS first try)",
        "index_report": "reports/discovery/disc002-s15-index-postbatch15.json",
        "validate_report": "reports/discovery/disc002-s15-validate-postbatch15.json (0 errors)",
        "final_pytest": "reports/discovery/disc002-session15-final-pytest.json (to be run after the last mutation; recorded here once available)",
    },
    "git_state_at_write": "to be filled after commit; see the state commit message",
    "next_task": (
        "DISC-002 batch-16 review tranche: copy the batch-15 script "
        "pattern (scripts/disc002_batch15_{replay,tranche,probe,decisions,"
        "verify,delta}.py -> batch16; CAND at scratch/disc002-s16-batch15."
        "jsonl after a sixteen-round replay; decision IDs D-DISC002-"
        "B16-****). Keep the F-0021-FIXED fence_spans(struct, total_lines) "
        "and the LEVEL-EXACT heading guard in the verify script. Expected "
        "pool: 4,274 matching the signal rule of 51,252 unreviewed. "
        "DISK NOTE for future sessions: replay intermediates are ~259MB "
        "each — keep the delete-as-consumed replay pattern when the "
        "scratch volume is tight. After the tranches: dossier-extension "
        "classification (per domain, bounded batches), then disposition "
        "assignment before gated synthesis."
    ),
}
CHECKPOINT.write_text(json.dumps(checkpoint, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print("state updates written:")
print(" -", QUEUE, "(DISC-002 notes updated)")
print(" -", STATE, "(stage/notes/final_statuses/chain/batch15 utc)")
print(" -", CHECKPOINT)
