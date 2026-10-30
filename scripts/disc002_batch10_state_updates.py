#!/usr/bin/env python3
"""DISC-002 session 10: update the task-queue record and current-state.json."""
from __future__ import annotations

import json
from pathlib import Path

QUEUE = Path("state/task-queue.jsonl")
STATE = Path("state/current-state.json")

lines = [l for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
records = [json.loads(l) for l in lines]

disc = None
for r in records:
    if r.get("task_id") == "DISC-002":
        disc = r
assert disc is not None and disc["status"] == "in_progress"

# 1. update notes with session-10 evidence. Toolkit improvement this session:
#    the batch-10 probe is FENCE-AWARE (authoritative mdextract headings +
#    fence spans) — the recurring '# comment in code fence looks like a
#    heading' defect class (three sessions in a row) is now structurally
#    prevented in the probe; heading citations in the verify script are also
#    checked against the authoritative heading list.
disc["notes"] = (
    "DISC-002 IN PROGRESS - session 10 (2026-10-31). Baseline independently "
    "re-verified at session start: clean tree with HEAD == origin/main == "
    "f54204e; 663/663 tests (reports/discovery/disc002-session10-baseline-"
    "pytest.json); both vaults byte-identical to committed manifests at start "
    "AND end (reports/discovery/disc002-session10-manifest{,-end}-{ai-course,"
    "master-ai}.json; 0 added/removed/changed). Answered the user's status "
    "question with repository evidence: framework v0.9.0, 24 capabilities "
    "(23 implemented-and-tested + 1 planned CAP-014 'source-to-output coverage "
    "and frequency regression reports'), the entire requested quality toolkit "
    "implemented and tested (CAP-018 lint-artifacts, CAP-019 assess-quality/"
    "quality-drift/quality-gate, CAP-020 repair loop, CAP-021 check-prompt, "
    "CAP-017 discovery). ADR-0010 replay extended to TEN decide rounds via "
    "scripts/disc002_batch10_replay.py (r1+r2+batch2..batch9 replayed with "
    "recorded --decided-utc values, then discovery-index) — CONTENT-IDENTICAL "
    "to the committed index (60,154 records; status counts matched exactly: "
    "51,612/7,085/1,452/3/1/1; validate green; F-0019 heeded; replay ran "
    "clean on the first try; post-batch9 chain state preserved at scratch/"
    "disc002-s10-batch9.jsonl). NO NEW TOOLING DEFECTS. TOOLKIT IMPROVEMENT "
    "(session-9 handoff follow-up): scripts/disc002_batch10_probe.py is "
    "FENCE-AWARE — heading detection uses the authoritative mdextract "
    "extract_structure_text headings and code-fence spans instead of the naive "
    "line.startswith('#') scan, and in-fence definition-window hits are "
    "excluded from def_hits and reported separately; the verify script "
    "(scripts/disc002_batch10_verify.py) additionally asserts every heading "
    "citation against the authoritative heading list. The recurring "
    "fence-heading false-positive class (batches 7/8/9) is now structurally "
    "prevented. BATCH 10 REVIEW TRANCHE: 60 highest-signal unreviewed "
    "provisional candidates (4,634 matching the signal rule of 51,612 "
    "unreviewed — exactly the count the session-9 handoff predicted; scripts/"
    "disc002_batch10_tranche.py, repo-relative). Tranche character: mixed — "
    "generic English vocabulary (verb 'considers', adverb 'deliberately'/'"
    "physically', gerunds 'entering'/'letting'/'fixing'/'reaching', fragments "
    "'exactly one'/'target's'/'different model'/'full context'/'existing "
    "content'/'entire source'/'slides across'/'one bias'-adjacent prose, date "
    "stamps 'august'/'august 2026', number words 'billion'/'decimal', homonyms "
    "'children'/'0-1'/'triangle', MOC/folder fragments 'note 04'/'note 05'/"
    "'04 neural'/'04 neural networks', vault-management labels 'adr-006', "
    "artifact fragments \"cpu'\"-family value '3e-4', layer label 'conv3', "
    "model name 'paligemma') plus a strong technical minority (fpr, hybrid "
    "models, imagenet normalization, long-running agents, pure vector search, "
    "running mean, unembedding, unlabeled, 20-tokens-per-parameter, "
    "adaptiveavgpool2d, base/chat models, channel dimensions, non-verifiable, "
    "spatial features, 56-layer degradation family, best-validation early "
    "stopping, color channels, mini moe, snell test-time-compute family, "
    "alignment method, dpo 2023, classification head). Method: individual "
    "evidence review of all 60 brief blocks + FENCE-AWARE definitional-"
    "treatment coverage probe (scripts/disc002_batch10_probe.py, 62 terms) + "
    "targeted citation verification (scripts/disc002_batch10_verify.py, 91 "
    "locator checks, all OK after 9 pattern fixes — mostly **bold** markers "
    "plus two wrong-file pointers) + independent subagent cross-check of 40 "
    "judgment calls: 40/40 AGREE. Subagent errata INDEPENDENTLY RE-VERIFIED "
    "before incorporation (session-9 lesson applied AGAIN — one erratum was "
    "itself wrong): VERIFIED and incorporated — ColPali 'embeds it via a VLM "
    "(PaliGemma)' quote is at :132 (:12 carries the other in-situ mention); "
    "Transfer Learning ImageNet mean/std values are at :564; several cited "
    "headings are ###-level (Perplexity :87/:90, channel headings, Eval :50, "
    "ResNet :477, TF-IDF :210, Scaling Laws :45) and Agent-vs-Workflow :97 is "
    "##-level. REJECTED as wrong — the claim that '06. VGG16 Architecture "
    "Deep Dive.md' contains no ImageNet normalization: the note HAS 4 ImageNet "
    "mentions including the mean-RGB preprocessing description at :131 and "
    "code defaults :513/:620/:622. DECISIONS: 30 evidence-cited covers + 0 "
    "confirm_gap + 0 merge + 30 noise rejects (state/concept-candidates/002-"
    "disc002-decisions-batch10.jsonl; applied with --decided-utc "
    "2026-10-31T05:30:00Z — chain-consistent value after batch-9's 03:00:00Z; "
    "reports/discovery/disc002-decide-batch10.json, disc002-validate-batch10."
    "json 60,154 records 0 errors, disc002-index-batch10.json). POST-BATCH10: "
    "51,552 provisional / 7,115 already_covered / 1,482 rejected / 3 "
    "confirmed_gap (second moment, bradley-terry, async def) / 1 merged / 1 "
    "deferred; index delta-verified exactly (-60 provisional, +30 covered, "
    "+30 rejected; all 60 statuses correct; all 60 decision_history entries "
    "appended; all other 60,094 records unchanged). NO NEW CONFIRMED GAP: the "
    "one gap-shaped candidate, 'unembedding' (used in dependency position at "
    "Initialization Schemes :176/:238, Logit Lens :85, InstructGPT :52, with "
    "no 'unembedding' heading corpus-wide), RESOLVED as cover — the defining "
    "note spells it HYPHENATED: master-ai '07 - Transformers/Components/06 - "
    "Embedding Layer.md:60' 'The output layer (un-embedding) is also a "
    "R^{d x |V|} matrix' inside '## Tied vs Untied Embeddings' :58. NEW PROBE "
    "LESSON RECORDED (session-9 LaTeX/unicode lesson extended): search "
    "hyphenation/spelling variants (unembedding/un-embedding) before claiming "
    "absence. REMAINING: batch-11+ review tranches (~4,574 still match the "
    "signal rule); per-domain semantic classification of the 69,185 "
    "dossier-extension overlap pairs (no bulk absorption); disposition "
    "assignment (release-blocking) before gated synthesis. Review standard "
    "unchanged: individual evidence review with file:line citations, "
    "subagent cross-check with independent re-verification of subagent "
    "corrections, confirmed gaps RARE."
)

QUEUE.write_text(
    "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
    encoding="utf-8",
)
print("task-queue.jsonl updated (DISC-002 notes); records:", len(records))

# 2. current-state.json
st = json.loads(STATE.read_text(encoding="utf-8"))
st["stage"] = "disc002-review-batch10-done"
st["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-31-disc002-session10.json"
st["notes"] = (
    "DISC-002 in progress; session 10 re-verified the baseline (663/663 "
    "tests at start, both vaults byte-identical to manifests at start and "
    "end, HEAD == origin/main == f54204e), answered the user's toolkit-status "
    "question with evidence (framework 0.9.0; 23 implemented-and-tested "
    "capabilities + 1 planned CAP-014; the full quality toolkit — "
    "lint-artifacts, assess-quality, quality-drift, quality-gate, repair "
    "loop, check-prompt, discover-gaps — is implemented and tested), extended "
    "the ADR-0010 replay to TEN decide rounds (content-identical to the "
    "committed index; replay ran clean on the first try), made the batch-10 "
    "probe FENCE-AWARE (authoritative mdextract headings; the recurring "
    "fence-heading false-positive class is now structurally prevented), and "
    "completed the batch-10 review tranche: 60 highest-signal unreviewed "
    "candidates (mixed generic + technical tranche), 62-term fence-aware "
    "coverage probe + 91-check citation verification + independent subagent "
    "cross-check of 40 judgment calls (40/40 AGREE; errata independently "
    "re-verified — one was wrong and rejected). Decisions: 30 evidence-cited "
    "covers + 0 new gaps + 0 merges + 30 noise rejects applied (--decided-utc "
    "2026-10-31T05:30:00Z), validate green, index regenerated and "
    "delta-verified. The one gap-shaped candidate ('unembedding') resolved as "
    "cover via the hyphenated 'un-embedding' definition at Embedding "
    "Layer.md:60 — probe lesson: search hyphenation variants before claiming "
    "absence. CURRENT: 51,552 provisional / 7,115 already_covered / 1,482 "
    "rejected / 3 confirmed_gap (second moment, bradley-terry, async def) / 1 "
    "merged / 1 deferred. NEXT: batch-11+ review tranches (~4,574 still match "
    "the signal rule); per-domain semantic classification of the "
    "dossier-extension overlap pairs; then disposition assignment before "
    "gated synthesis."
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["final_statuses"] = {
    "already_covered": 7115,
    "confirmed_gap": 3,
    "deferred": 1,
    "merged": 1,
    "provisional_candidate": 51552,
    "rejected": 1482,
}
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["decisions_chain"].append(
    "state/concept-candidates/002-disc002-decisions-batch10.jsonl (60)"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["replay_decided_utc"]["batch10"] = (
    "2026-10-31T05:30:00Z"
)
st["phase_zero_rebaseline"]["disc002_full_corpus_discovery"]["sessions_merged"].append(
    "session 10: ten-round replay re-verification + fence-aware probe + "
    "batch-10 tranche (30 covers + 30 rejects, no new gap)"
)
STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("current-state.json updated")
