# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  TWO PARALLEL SESSIONS MERGED on main (2026-10-28). The discovery run
  itself is complete and verified by both sessions independently; the
  multi-batch semantic review of the candidate set has started and must
  continue. After DISC-002: dossier extension, then disposition assignment,
  then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002 session A
  (3d2ff8b..e2914e9) + session B (merged via the merge commit).
- Framework version 0.9.0; 24 capabilities (CAP-023 `vu discovery-index` new).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never mark
  a task completed before its commit exists; always re-run the suite after
  the last mutation).

## The two-session merge (what happened, evidence-backed)

Two sessions worked DISC-002 in parallel from the same REGEN-001 base
(4ae8125) and both pushed/pushed-at main:

- **Session A** (origin/main first): corpus-scale hardening (byte-identical,
  3.3x), full-corpus discovery (60,154 candidates, coverage COMPLETE,
  double-run byte-identical, peak RSS 1.95GB), discovery-validate scale fix
  (F-0015), background-reap finding (F-0016), ADR-0010 (candidates monolith
  git-ignored, replayable), deterministic triage, review rounds r1 (1,153
  class-based rejects, subagent-verified) + r2 (44 individual decisions:
  FIRST 2 CONFIRMED GAPS — second moment, bradley-terry; 4 defers; 7
  covers; 31 rejects).
- **Session B** (this merge): F-0017 performance fix (single reused
  validators + inverted relationship matching; ~291s per full run vs ~547s,
  byte-identical output, equivalence pinned by a kept-verbatim reference
  oracle + 48 template-family tests + a 110,799-pair corpus differential),
  CAP-023 `vu discovery-index`, independent 114-candidate review (63 noise
  rejects, 51 evidence-cited covers), dossier reconciliation gap report.

Merge resolution (recorded in the merge commit and checkpoint):
- Kept session B's discovery implementation (faster; same byte output —
  both sessions proved equivalence independently).
- Adopted session A's validate-scale fix, ADR-0010, triage tooling, and
  r1/r2 decision files.
- Extended the decision state machine: `cover` is now valid FROM
  `rejected`/`deferred` (EMERGENT_CONCEPT_DISCOVERY requires revisable
  decisions with audit trail; the history keeps BOTH entries).
- Reconciled the overlapping decisions: 28 agreements dropped as redundant;
  12 of session A's class-based rejects were reversed to `cover` with
  file:line evidence (their r2 had already found this false-positive class:
  "paraphrased-definition" covers); 3 defers superseded by evidence-cited
  covers; the 2 confirm_gap-vs-cover conflicts (second moment, bradley-terry)
  resolved as `revise` — the confirmed_gap STANDS (conservative) and session
  B's coverage evidence is recorded in the history for the synthesis
  planner (the residual gap is coherent DERIVATION treatment, not total
  absence).
- The merged decision chain was REPLAYED CLEAN on the merged tree: fresh
  regeneration (double-run byte-identical 291.7s/286.7s) -> r1 -> r2 ->
  batch2; 0 errors; discovery-validate green (60,154 records).

## Current candidate-set state (60,154 records, validated)

- 52,032 provisional_candidate (review continues in bounded tranches)
- 6,907 already_covered (6,856 tool sightings + 51 reviewed covers)
- 1,212 rejected (class-based noise + individual rejects)
- 2 confirmed_gap: **second moment** (moment-estimation prerequisite),
  **bradley-terry** (preference-model math fragmented) — both carry revise
  entries with the corpus coverage citations
- 1 deferred (ssd framework family)
- Replay recipe (ADR-0010): `vu discover-gaps` (all 70 batches, both
  manifests — exact args in reports/discovery/disc002-full-corpus-run.json
  report_meta.args) then `vu discovery-decide` r1 (--decided-utc
  2026-10-28T00:45:00Z), r2 (2026-10-28T01:30:00Z), batch2
  (2026-10-28T02:30:00Z), then `vu discovery-index`.

## Next task: DISC-002 continuation (review tranches + dossier extension)

1. **Continue the semantic review in bounded tranches.** 52,032 provisional
   remain. Use session A's tooling (scripts/disc002_review_brief.py,
   disc002_triage.json classes, family strategy) + session B's
   scripts/disc002_coverage_probe.py (word-boundary definitional-treatment
   probe) and the noise classes both sessions converged on (numeric
   literals, code/import/def fragments, citation fragments, generic prose).
   Learn from the merge: class-based rejection over-rejects real concepts —
   individual evidence review with file:line citations is the standard;
   confirmed gaps are RARE (2 in ~1,400 reviewed) — look for concepts used
   in dependency position with NO definitional treatment anywhere.
2. **Dossier extension** per reports/discovery/disc002-dossier-
   reconciliation-gap.json next_action (overlap-candidates + classification
   discipline; 27 decisions touch dossier domains).
3. **Then disposition assignment** (Unaccounted blocks release) and GATED
   synthesis: check-prompt -> generation -> lint-artifacts -> assess-quality
   -> quality-drift -> quality-gate -> repair loop per batch.

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification. When a push is
  rejected because a parallel session moved main: fetch, review their
  commits, MERGE (do not rebase away history), reconcile decisions through
  the audit trail, and re-verify the chain before pushing again.
- F-0016: background processes are reaped between tool calls — long runs
  must fit one tool call (< 10 min); corpus discovery now takes ~5 min.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
