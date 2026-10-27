# Next Agent Handoff

## Project state

- Current milestone: REGEN-001 full-corpus re-extraction COMPLETE
  (user-authorized Phase-0 restart executed through FRAME-001/FRAME-002 and
  now the full-corpus extraction); the project moves to DISC-002:
  corpus-wide emergent-concept discovery, then dossier reconciliation, then
  GATED synthesis with disposition assignment.
- Completed and verified so far: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001 (feat commit recorded
  in the queue record and checkpoint).
- Framework version 0.8.0; 604/604 tests green; capabilities --verify: 22
  implemented-and-tested + 1 planned (CAP-014).
- Extraction state: ALL 609 source files extracted into 70 committed batches
  (11 revalidated pre-restart + 59 REGEN batches 012-070); 27,536 KUs; every
  id globally unique; every batch double-run byte-identical and verified
  byte-faithful to sources via `vu ku-fidelity` (CAP-022). Registry rebuilt
  (state/registries/kuregistry.db, git-ignored; rebuild via
  scripts/regen001_registry.py) with the 7 classification overlays applied;
  kureg-validate green. All KUs `Unaccounted` by design.
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* (esp.
  PHASE_ZERO_REBASELINE_AND_FRAMEWORK_REFACTOR.md,
  EMERGENT_CONCEPT_DISCOVERY.md, TOOLING_FRAMEWORK.md) ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never mark
  a task completed before its commit exists; always re-run the suite after
  the last mutation).

## What the previous session actually did (evidence-backed)

1. Verified the FRAME-002 completion claims against real evidence BEFORE
   working: fresh full-suite run (576/576 — the handoff text said 563, a
   stale undercount; the recorded report itself said 576; corrected as
   F-0012), capabilities --verify (true), both vaults byte-unchanged vs
   manifests.
2. Added the reusable `vu ku-fidelity` command (CAP-022, 22 unit tests + 5
   CLI tests), replacing the per-task fidelity scripts of EXT-001..010
   (retrospective gap: task-local scripts duplicated framework
   functionality).
3. REGEN-001 step 1 — revalidated all 11 committed batches by replaying
   their exact recorded recipes (report_meta.args): double-runs byte-
   identical, every batch regenerates its committed bytes exactly,
   1728/1728 records excerpt-byte-exact
   (reports/regen/regen001-revalidation.json).
4. REGEN-001 step 2 — extracted the remaining 578 files in 59 bounded
   batches 012-070 (per-file runs concatenated sorted; folder scopes were
   rejected because mixed folders would re-extract committed files). Two
   real catches by the gates, both fixed with regression tests:
   (a) F-0013: the fidelity heading rule did not know the empty_section
   design contract (empty_section units sit ON their heading line; batches
   014/015 first flagged it); (b) the extraction driver derived batch
   numbering from directory contents, so a resumed run renumbered the plan
   and minted 14 duplicate batches — the id-collision gate caught them,
   they were verified byte-identical to their twins, deleted, and the
   numbering was pinned to the committed sequence.
5. REGEN-001 step 3 — rebuilt the registry from all 70 batches + 7 overlays
   (kureg-validate green) and produced full-corpus accounting: 276/276 +
   333/333 files covered exactly once, 0 missing/extra/multi-batch, 0
   source-hash mismatches, 27,536 KUs, 0 duplicate ids
   (reports/regen/regen001-registry.json + regen001-accounting.json).

## Next task: DISC-002 (queue record; dependencies satisfied)

1. **Run corpus-wide concept discovery and reconcile dossiers before
   synthesis.** The discovery coverage gate is NOW OPEN: the partial-corpus
   run (6,340 provisional candidates, gate closed at 31/609) must be re-run
   over the complete corpus (all 70 batches / 27,536 KUs). Expect a much
   larger candidate set: budget the run, use bounded output, and record the
   coverage denominator in every report.
2. Semantic review of candidates is YOUR job (`vu discovery-decide`): the
   tool collects evidence; you decide unsearched/provisional/confirmed/
   already-covered/accepted/merged/split/rejected/deferred with rationale.
   A gap can only be confirmed with complete corpus coverage — which now
   exists.
3. Reconcile the six existing dossiers (state/dossiers/) against the full
   corpus; regenerate/extend where the evidence changed; keep the byte-
   identical regeneration property where possible.
4. Then synthesis begins UNDER THE GATES: map KUs to destinations and
   dispositions first (Unaccounted blocks release), then every batch
   through check-prompt -> generation -> lint -> assess -> drift -> gate ->
   repair. Use bounded batches (10-20+ iterations expected), fresh sessions,
   and the two-commit pattern (feat, then state-with-hash).

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification.
- Note F-0014 (open): two ai-course files end with 'END OF FILE / File
  Name' marker headings — synthesis must not copy them as knowledge
  headings; their KUs are accounted as empty_section units.
